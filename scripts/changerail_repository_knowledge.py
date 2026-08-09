"""Repository knowledge catalog and maintenance policy validation."""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

from changerail_contract_schema import validate_with_schema

CATALOG_SCHEMA_ID = "changerail.repository-knowledge.v1"
POLICY_SCHEMA_ID = "changerail.maintenance-policy.v1"
CATALOG_SCHEMA_FILE = "changerail-repository-knowledge.schema.json"
POLICY_SCHEMA_FILE = "changerail-maintenance-policy.schema.json"
SCAN_REPORT_SCHEMA_ID = "changerail.maintenance-scan-report.v1"
DETECTOR_RESULT_SCHEMA_ID = "changerail.maintenance-detector-result.v1"
SCAN_REPORT_SCHEMA_FILE = "changerail-maintenance-scan-report.schema.json"
DETECTOR_RESULT_SCHEMA_FILE = "changerail-maintenance-detector-result.schema.json"
DEFAULT_CATALOG_PATH = Path(".changerail/knowledge.yaml")
DEFAULT_POLICY_PATH = Path(".changerail/maintenance.yaml")
DEFAULT_INDEX_PATH = Path(".changerail/KNOWLEDGE.md")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
SEVERITY_ORDER = {"none": -1, "info": 0, "minor": 1, "major": 2, "blocker": 3}
DEFAULT_FAIL_ON = "major"
CORE_DETECTORS = (
    "catalog-coverage",
    "repository-orphans",
    "markdown-local-links",
    "generated-freshness",
    "forbidden-active-references",
    "adapters",
)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    message: str


@dataclass
class ValidationResult:
    ok: bool
    catalog_path: str
    policy_path: str | None
    diagnostics: list[Diagnostic]
    catalog: dict[str, Any] | None = None
    policy: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": self.ok,
            "catalog_path": self.catalog_path,
            "policy_path": self.policy_path,
            "diagnostics": [asdict(diagnostic) for diagnostic in self.diagnostics],
        }
        if self.catalog is not None:
            payload["catalog_records"] = len(self.catalog.get("records", []))
        if self.policy is not None:
            payload["policy_configured"] = True
        return payload


class RepositoryKnowledgeError(Exception):
    """Raised for invalid caller input before catalog validation can run."""


def repo_root_from_path(path: Path | None = None) -> Path:
    return (path or Path.cwd()).resolve(strict=False)


def _format_yaml_error(exc: yaml.YAMLError) -> str:
    return " ".join(str(exc).split())


def load_yaml(path: Path, *, missing_ok: bool = False) -> tuple[Any | None, list[Diagnostic]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        if missing_ok:
            return None, [Diagnostic("not_configured", path.as_posix(), "file is not configured")]
        return None, [Diagnostic("file_missing", path.as_posix(), "file does not exist")]
    except OSError as exc:
        return None, [Diagnostic("file_read_error", path.as_posix(), str(exc))]
    try:
        return yaml.safe_load(text), []
    except yaml.YAMLError as exc:
        return None, [Diagnostic("yaml_parse_error", path.as_posix(), _format_yaml_error(exc))]


def schema_diagnostics(data: Any, schema_file: str, path: Path) -> list[Diagnostic]:
    return [
        Diagnostic("schema_error", path.as_posix(), error)
        for error in validate_with_schema(data, schema_file)
    ]


def _path_parts(value: str) -> tuple[str, ...]:
    return tuple(part for part in PurePosixPath(value).parts if part not in ("", "."))


def normalize_repo_path(value: str, *, field: str, root: Path) -> tuple[str | None, Diagnostic | None]:
    if not isinstance(value, str) or not value:
        return None, Diagnostic("path_invalid", field, "path must be a non-empty string")
    if "\\" in value or Path(value).is_absolute() or PurePosixPath(value).is_absolute() or WINDOWS_DRIVE_RE.match(value):
        return None, Diagnostic("path_not_relative", field, f"path must be repository-relative: {value}")
    parts = _path_parts(value)
    if not parts or any(part == ".." for part in parts):
        return None, Diagnostic("path_traversal", field, f"path must stay inside repository root: {value}")
    normalized = PurePosixPath(*parts).as_posix()
    candidate = (root / normalized).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError:
        return None, Diagnostic("path_traversal", field, f"path must stay inside repository root: {value}")
    return normalized, None


def _validate_path_list(values: Any, *, field: str, root: Path, diagnostics: list[Diagnostic]) -> list[str]:
    normalized: list[str] = []
    if not isinstance(values, list):
        return normalized
    for index, value in enumerate(values):
        if not isinstance(value, str):
            continue
        path, diagnostic = normalize_repo_path(value, field=f"{field}[{index}]", root=root)
        if diagnostic:
            diagnostics.append(diagnostic)
        elif path:
            normalized.append(path)
    return normalized


def semantic_catalog_diagnostics(catalog: Any, *, root: Path, path: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(catalog, dict):
        return diagnostics
    records = catalog.get("records")
    if not isinstance(records, list):
        return diagnostics
    seen_paths: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        field_prefix = f"{path.as_posix()}.records[{index}]"
        normalized, diagnostic = normalize_repo_path(str(record.get("path", "")), field=f"{field_prefix}.path", root=root)
        if diagnostic:
            diagnostics.append(diagnostic)
            continue
        if normalized in seen_paths:
            diagnostics.append(
                Diagnostic("duplicate_record_path", f"{field_prefix}.path", f"duplicate catalog path: {normalized}")
            )
        seen_paths.add(normalized)
        if record.get("status") == "active" and not (root / normalized).exists():
            diagnostics.append(
                Diagnostic("active_path_missing", f"{field_prefix}.path", f"active path does not exist: {normalized}")
            )
        _validate_path_list(record.get("source_globs"), field=f"{field_prefix}.source_globs", root=root, diagnostics=diagnostics)
        _validate_path_list(record.get("supersedes"), field=f"{field_prefix}.supersedes", root=root, diagnostics=diagnostics)
    return diagnostics


def semantic_policy_diagnostics(policy: Any, *, root: Path, path: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(policy, dict):
        return diagnostics
    for key in ("catalog_path", "generated_index_path"):
        value = policy.get(key)
        if isinstance(value, str):
            _, diagnostic = normalize_repo_path(value, field=f"{path.as_posix()}.{key}", root=root)
            if diagnostic:
                diagnostics.append(diagnostic)
    scan = policy.get("scan")
    if isinstance(scan, dict):
        for key in ("include_globs", "exclude_globs", "active_scope_globs"):
            _validate_path_list(scan.get(key), field=f"{path.as_posix()}.scan.{key}", root=root, diagnostics=diagnostics)
    return diagnostics


def validate_catalog_document(catalog: Any, *, root: Path, path: Path) -> list[Diagnostic]:
    diagnostics = schema_diagnostics(catalog, CATALOG_SCHEMA_FILE, path)
    if diagnostics:
        return diagnostics
    diagnostics.extend(semantic_catalog_diagnostics(catalog, root=root, path=path))
    return diagnostics


def validate_policy_document(policy: Any, *, root: Path, path: Path) -> list[Diagnostic]:
    diagnostics = schema_diagnostics(policy, POLICY_SCHEMA_FILE, path)
    if diagnostics:
        return diagnostics
    diagnostics.extend(semantic_policy_diagnostics(policy, root=root, path=path))
    return diagnostics


def resolve_input_path(root: Path, value: str | Path) -> Path:
    raw = str(value)
    if Path(raw).is_absolute() or PurePosixPath(raw).is_absolute() or WINDOWS_DRIVE_RE.match(raw):
        raise RepositoryKnowledgeError(f"path must be repository-relative: {raw}")
    normalized, diagnostic = normalize_repo_path(raw, field="input", root=root)
    if diagnostic or not normalized:
        raise RepositoryKnowledgeError(diagnostic.message if diagnostic else f"path is invalid: {raw}")
    return root / normalized


def validate_catalog_and_policy(
    *,
    root: Path | None = None,
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    policy_path: Path | str = DEFAULT_POLICY_PATH,
) -> ValidationResult:
    repo_root = repo_root_from_path(root)
    catalog_file = resolve_input_path(repo_root, catalog_path)
    policy_file = resolve_input_path(repo_root, policy_path)
    diagnostics: list[Diagnostic] = []

    catalog, catalog_load = load_yaml(catalog_file)
    diagnostics.extend(catalog_load)
    if not catalog_load:
        diagnostics.extend(validate_catalog_document(catalog, root=repo_root, path=catalog_file.relative_to(repo_root)))

    policy, policy_load = load_yaml(policy_file, missing_ok=True)
    policy_configured = not (len(policy_load) == 1 and policy_load[0].code == "not_configured")
    if policy_configured:
        diagnostics.extend(policy_load)
        if not policy_load:
            diagnostics.extend(validate_policy_document(policy, root=repo_root, path=policy_file.relative_to(repo_root)))
    else:
        diagnostics.extend(policy_load)

    blocking = [diagnostic for diagnostic in diagnostics if diagnostic.code != "not_configured"]
    return ValidationResult(
        ok=not blocking,
        catalog_path=catalog_file.relative_to(repo_root).as_posix(),
        policy_path=policy_file.relative_to(repo_root).as_posix(),
        diagnostics=diagnostics,
        catalog=catalog if isinstance(catalog, dict) else None,
        policy=policy if isinstance(policy, dict) else None,
    )


def require_valid_result(result: ValidationResult) -> None:
    if not result.ok:
        codes = ", ".join(diagnostic.code for diagnostic in result.diagnostics) or "unknown"
        raise RepositoryKnowledgeError(f"repository knowledge validation failed: {codes}")


def configured_index_path(root: Path, result: ValidationResult, override: str | Path | None = None) -> Path:
    repo_root = repo_root_from_path(root)
    if override is not None:
        return resolve_input_path(repo_root, override)
    if not result.policy:
        raise RepositoryKnowledgeError("maintenance policy is not configured and no --index override was supplied")
    raw = result.policy.get("generated_index_path")
    if not isinstance(raw, str) or not raw:
        raise RepositoryKnowledgeError("maintenance policy generated_index_path is missing")
    return resolve_input_path(repo_root, raw)


def _display(value: Any) -> str:
    if value is None or value == "":
        return "none"
    if isinstance(value, list):
        return ", ".join(_display(item) for item in value) if value else "none"
    return str(value)


def _escape_table(value: Any) -> str:
    return _display(value).replace("|", "\\|").replace("\n", " ")


def sorted_records(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    records = [record for record in catalog.get("records", []) if isinstance(record, dict)]
    return sorted(
        records,
        key=lambda record: (
            str(record.get("path", "")),
            str(record.get("type", "")),
            str(record.get("status", "")),
        ),
    )


def render_index_content(
    catalog: dict[str, Any],
    *,
    catalog_path: str,
    policy_path: str | None,
    index_path: str,
) -> str:
    lines = [
        "# Repository Knowledge Index",
        "",
        "Generated from the tracked ChangeRail repository knowledge catalog.",
        "",
        f"- Catalog: `{catalog_path}`",
        f"- Policy: `{policy_path or 'not configured'}`",
        f"- Index: `{index_path}`",
        "",
        "| Path | Status | Type | Owner | Review After | Verify |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in sorted_records(catalog):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_escape_table(record.get('path'))}`",
                    _escape_table(record.get("status")),
                    _escape_table(record.get("type")),
                    _escape_table(record.get("owner")),
                    _escape_table(record.get("review_after")),
                    _escape_table(record.get("verify")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _diagnostic_payload(diagnostic: Diagnostic, *, severity: str = "blocker") -> dict[str, Any]:
    payload = asdict(diagnostic)
    payload["severity"] = severity
    return payload


def _detector_error(code: str, message: str, *, path: str | None = None, severity: str = "blocker") -> dict[str, Any]:
    payload = {"code": code, "message": message, "severity": severity}
    if path:
        payload["path"] = path
    return payload


def _finding(
    detector_id: str,
    code: str,
    message: str,
    *,
    severity: str = "major",
    path: str | None = None,
    source_path: str | None = None,
    target_path: str | None = None,
    fragment: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_path = (path or source_path or target_path or "workspace").replace("/", ":").replace(".", "-").lower()
    safe_path = re.sub(r"[^a-z0-9._:-]+", "-", raw_path).strip("-") or "workspace"
    payload: dict[str, Any] = {
        "id": f"{detector_id}:{code}:{safe_path}",
        "severity": severity,
        "code": code,
        "message": message,
    }
    if path:
        payload["path"] = path
    if source_path:
        payload["source_path"] = source_path
    if target_path:
        payload["target_path"] = target_path
    if fragment:
        payload["fragment"] = fragment
    if evidence:
        payload["evidence"] = evidence
    return payload


def _detector_result(
    detector_id: str,
    findings: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    *,
    summary: str | None = None,
) -> dict[str, Any]:
    result_findings = findings or []
    result_errors = errors or []
    status = "error" if result_errors else "fail" if result_findings else "pass"
    payload: dict[str, Any] = {
        "schema": DETECTOR_RESULT_SCHEMA_ID,
        "id": detector_id,
        "status": status,
        "findings": result_findings,
        "errors": result_errors,
    }
    if summary:
        payload["summary"] = summary
    return payload


def _scan_config(policy: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(policy, dict):
        return {}
    scan = policy.get("scan")
    return scan if isinstance(scan, dict) else {}


def _detector_options(config: dict[str, Any], key: str) -> dict[str, Any]:
    detectors = config.get("detectors")
    if not isinstance(detectors, dict):
        return {}
    options = detectors.get(key)
    return options if isinstance(options, dict) else {}


def _configured_fail_on(config: dict[str, Any], override: str | None) -> str:
    if override:
        return override
    candidate = config.get("fail_on")
    return candidate if isinstance(candidate, str) and candidate in SEVERITY_ORDER else DEFAULT_FAIL_ON


def _configured_detectors(config: dict[str, Any], override: list[str] | None = None) -> list[str]:
    if override is not None:
        return override
    enabled = config.get("enabled_detectors")
    if not isinstance(enabled, list):
        return []
    return [detector for detector in enabled if isinstance(detector, str)]


def _is_excluded(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


def _discover_files(root: Path, include_globs: list[str], exclude_globs: list[str]) -> list[str]:
    discovered: set[str] = set()
    for pattern in include_globs:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            try:
                rel_path = path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
            except ValueError:
                continue
            if not _is_excluded(rel_path, exclude_globs):
                discovered.add(rel_path)
    return sorted(discovered)


def _active_catalog_paths(catalog: dict[str, Any], *, root: Path) -> set[str]:
    paths: set[str] = set()
    for record in catalog.get("records", []):
        if not isinstance(record, dict) or record.get("status") != "active":
            continue
        raw = record.get("path")
        if not isinstance(raw, str):
            continue
        normalized, diagnostic = normalize_repo_path(raw, field="catalog.records[].path", root=root)
        if diagnostic is None and normalized:
            paths.add(normalized)
    return paths


def _scan_scope(config: dict[str, Any], universe: list[str], *, root: Path) -> list[str]:
    active_scope_globs = [item for item in config.get("active_scope_globs", []) if isinstance(item, str)]
    if not active_scope_globs:
        return universe
    exclude_globs = [item for item in config.get("exclude_globs", []) if isinstance(item, str)]
    return _discover_files(root, active_scope_globs, exclude_globs)


def _detector_catalog_coverage(config: dict[str, Any], catalog: dict[str, Any], *, root: Path) -> dict[str, Any]:
    detector_id = "catalog-coverage"
    include_globs = [item for item in config.get("include_globs", []) if isinstance(item, str)]
    exclude_globs = [item for item in config.get("exclude_globs", []) if isinstance(item, str)]
    universe = _discover_files(root, include_globs, exclude_globs)
    errors: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    if not include_globs:
        errors.append(_detector_error("missing_include_globs", "scan include_globs must be configured before coverage can run"))
    elif not universe:
        errors.append(_detector_error("empty_documentation_universe", "configured documentation universe matched no files"))
    active_paths = _active_catalog_paths(catalog, root=root)
    for path in universe:
        if path not in active_paths:
            findings.append(
                _finding(
                    detector_id,
                    "uncovered_knowledge_file",
                    f"knowledge file is not covered by an active catalog record: {path}",
                    path=path,
                )
            )
    return _detector_result(detector_id, findings, errors, summary=f"{len(universe)} files inspected")


def _detector_repository_orphans(
    config: dict[str, Any],
    catalog: dict[str, Any],
    *,
    root: Path,
    active_missing: list[Diagnostic],
) -> dict[str, Any]:
    detector_id = "repository-orphans"
    include_globs = [item for item in config.get("include_globs", []) if isinstance(item, str)]
    exclude_globs = [item for item in config.get("exclude_globs", []) if isinstance(item, str)]
    universe = _discover_files(root, include_globs, exclude_globs)
    active_paths = _active_catalog_paths(catalog, root=root)
    findings = [
        _finding(
            detector_id,
            "missing_catalog_target",
            diagnostic.message,
            severity="blocker",
            path=diagnostic.path,
        )
        for diagnostic in active_missing
    ]
    for path in universe:
        if path not in active_paths:
            findings.append(
                _finding(
                    detector_id,
                    "orphan_discovered_file",
                    f"discovered knowledge file has no active catalog record: {path}",
                    path=path,
                )
            )
    return _detector_result(detector_id, findings, summary=f"{len(universe)} files inspected")


def _github_anchor(text: str, counts: dict[str, int]) -> str:
    normalized = unicodedata.normalize("NFKD", text.strip().lower())
    chars: list[str] = []
    previous_dash = False
    for char in normalized:
        category = unicodedata.category(char)
        if char.isspace() or char == "-":
            if not previous_dash:
                chars.append("-")
                previous_dash = True
            continue
        if category[0] in {"L", "N"} or char == "_":
            chars.append(char)
            previous_dash = False
    slug = "".join(chars).strip("-") or "section"
    count = counts.get(slug, 0)
    counts[slug] = count + 1
    return slug if count == 0 else f"{slug}-{count}"


def _normalize_fragment(fragment: str) -> str:
    return _github_anchor(fragment.lstrip("#"), {})


def _markdown_tokens(text: str) -> list[Any]:
    from markdown_it import MarkdownIt

    return MarkdownIt("commonmark").parse(text)


def _markdown_heading_anchors(path: Path) -> set[str]:
    md_stream = _markdown_tokens(path.read_text(encoding="utf-8"))
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for index, token in enumerate(md_stream[:-1]):
        if token.type == "heading_open" and md_stream[index + 1].type == "inline":
            anchors.add(_github_anchor(md_stream[index + 1].content, counts))
    return anchors


def _local_markdown_links(root: Path, rel_path: str) -> list[dict[str, Any]]:
    source = root / rel_path
    links: list[dict[str, Any]] = []
    md_stream = _markdown_tokens(source.read_text(encoding="utf-8"))
    for token in md_stream:
        if token.type != "inline" or not token.children:
            continue
        line = token.map[0] + 1 if token.map else None
        for child in token.children:
            if child.type != "link_open":
                continue
            href = child.attrs.get("href") if isinstance(child.attrs, dict) else None
            if not isinstance(href, str) or not href:
                continue
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            links.append({"href": href, "path": unquote(parsed.path), "fragment": unquote(parsed.fragment), "line": line})
    return links


def _resolve_link_target(root: Path, source_rel: str, target_path: str) -> tuple[str | None, Diagnostic | None]:
    if not target_path:
        return source_rel, None
    combined = PurePosixPath(source_rel).parent / target_path
    return normalize_repo_path(combined.as_posix(), field=f"{source_rel}.link", root=root)


def _detector_markdown_local_links(config: dict[str, Any], *, root: Path) -> dict[str, Any]:
    detector_id = "markdown-local-links"
    options = _detector_options(config, "markdown_local_links")
    extensions = options.get("extensions")
    suffixes = tuple(extensions if isinstance(extensions, list) else [".md", ".markdown"])
    universe = _scan_scope(config, _discover_files(
        root,
        [item for item in config.get("include_globs", []) if isinstance(item, str)],
        [item for item in config.get("exclude_globs", []) if isinstance(item, str)],
    ), root=root)
    markdown_files = [path for path in universe if Path(path).suffix in suffixes]
    findings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    anchor_cache: dict[str, set[str]] = {}
    try:
        for source_rel in markdown_files:
            for link in _local_markdown_links(root, source_rel):
                target_rel, diagnostic = _resolve_link_target(root, source_rel, link["path"])
                if diagnostic or not target_rel:
                    errors.append(_detector_error("unsafe_link_target", diagnostic.message if diagnostic else "link target is invalid", path=source_rel))
                    continue
                target = root / target_rel
                if not target.exists():
                    findings.append(
                        _finding(
                            detector_id,
                            "missing_link_target",
                            f"local Markdown link target is missing: {link['href']}",
                            source_path=source_rel,
                            target_path=target_rel,
                            evidence={"line": link["line"]},
                        )
                    )
                    continue
                fragment = link.get("fragment")
                if fragment and target.suffix in suffixes:
                    anchors = anchor_cache.get(target_rel)
                    if anchors is None:
                        anchors = _markdown_heading_anchors(target)
                        anchor_cache[target_rel] = anchors
                    if _normalize_fragment(fragment) not in anchors:
                        findings.append(
                            _finding(
                                detector_id,
                                "stale_anchor",
                                f"local Markdown anchor is missing: {link['href']}",
                                source_path=source_rel,
                                target_path=target_rel,
                                fragment=fragment,
                                evidence={"line": link["line"]},
                            )
                        )
    except ImportError as exc:
        errors.append(_detector_error("markdown_parser_unavailable", f"markdown-it-py is unavailable: {exc}"))
    except OSError as exc:
        errors.append(_detector_error("markdown_read_error", str(exc)))
    return _detector_result(detector_id, findings, errors, summary=f"{len(markdown_files)} Markdown files inspected")


def _detector_generated_freshness(result: ValidationResult, catalog: dict[str, Any], *, root: Path) -> dict[str, Any]:
    detector_id = "generated-freshness"
    findings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    try:
        index_path = configured_index_path(root, result)
        rel_index = index_path.relative_to(root.resolve(strict=False)).as_posix()
        expected = render_index_content(
            catalog,
            catalog_path=result.catalog_path,
            policy_path=result.policy_path,
            index_path=rel_index,
        )
        try:
            current = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            findings.append(
                _finding(
                    detector_id,
                    "generated_output_missing",
                    f"generated knowledge index is missing: {rel_index}",
                    severity="major",
                    path=rel_index,
                )
            )
        else:
            if current != expected:
                findings.append(
                    _finding(
                        detector_id,
                        "stale_generated_output",
                        f"generated knowledge index is stale: {rel_index}",
                        severity="major",
                        path=rel_index,
                    )
                )
    except RepositoryKnowledgeError as exc:
        errors.append(_detector_error("generated_freshness_config_error", str(exc)))
    return _detector_result(detector_id, findings, errors, summary="render-index freshness checked")


def _detector_forbidden_active_references(config: dict[str, Any], *, root: Path) -> dict[str, Any]:
    detector_id = "forbidden-active-references"
    options = _detector_options(config, "forbidden_active_references")
    patterns = options.get("patterns", [])
    universe = _scan_scope(config, _discover_files(
        root,
        [item for item in config.get("include_globs", []) if isinstance(item, str)],
        [item for item in config.get("exclude_globs", []) if isinstance(item, str)],
    ), root=root)
    findings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not isinstance(patterns, list):
        return _detector_result(detector_id, errors=[_detector_error("invalid_pattern_config", "forbidden patterns must be a list")])
    for rel_path in universe:
        try:
            text = (root / rel_path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            errors.append(_detector_error("active_reference_read_error", str(exc), path=rel_path))
            continue
        for pattern in patterns:
            if not isinstance(pattern, dict):
                continue
            raw_pattern = pattern.get("pattern")
            if not isinstance(raw_pattern, str) or raw_pattern not in text:
                continue
            pattern_id = str(pattern.get("id") or "unnamed")
            severity = str(pattern.get("severity") or "major")
            message = str(pattern.get("message") or f"forbidden active reference matched policy {pattern_id}")
            findings.append(
                _finding(
                    detector_id,
                    "forbidden_active_reference",
                    message,
                    severity=severity if severity in SEVERITY_ORDER else "major",
                    path=rel_path,
                    evidence={"policy_id": pattern_id},
                )
            )
    return _detector_result(detector_id, findings, errors, summary=f"{len(universe)} active-scope files inspected")


def _adapter_result_id(adapter_id: str) -> str:
    return f"adapter-{adapter_id}"


def _normalize_adapter_paths(payload: dict[str, Any], *, root: Path) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for finding in payload.get("findings", []) if isinstance(payload.get("findings"), list) else []:
        if not isinstance(finding, dict):
            continue
        for field in ("path", "source_path", "target_path"):
            value = finding.get(field)
            if not isinstance(value, str):
                continue
            normalized, diagnostic = normalize_repo_path(value, field=f"adapter.{field}", root=root)
            if diagnostic or not normalized:
                errors.append(
                    _detector_error(
                        "unsafe_adapter_path",
                        diagnostic.message if diagnostic else f"adapter path is invalid: {value}",
                        severity="blocker",
                    )
                )
            else:
                finding[field] = normalized
    return errors


def _adapter_timeout(config: dict[str, Any], adapter: dict[str, Any]) -> int:
    adapter_timeout = adapter.get("timeout_seconds")
    if isinstance(adapter_timeout, int) and adapter_timeout > 0:
        return adapter_timeout
    configured_timeout = config.get("timeout_seconds")
    if isinstance(configured_timeout, int) and configured_timeout > 0:
        return configured_timeout
    return 30


def _run_adapter(adapter: dict[str, Any], config: dict[str, Any], *, root: Path) -> dict[str, Any]:
    adapter_id = str(adapter.get("id") or "unnamed")
    result_id = _adapter_result_id(adapter_id)
    argv = adapter.get("argv")
    if not isinstance(argv, list) or not all(isinstance(item, str) and item for item in argv):
        return _detector_result(
            result_id,
            errors=[_detector_error("invalid_adapter_argv", f"adapter {adapter_id} must declare argv as a non-empty string array")],
        )
    timeout = _adapter_timeout(config, adapter)
    try:
        completed = subprocess.run(
            argv,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _detector_result(
            result_id,
            errors=[_detector_error("adapter_timeout", f"adapter {adapter_id} exceeded timeout {timeout}s")],
        )
    except OSError as exc:
        return _detector_result(
            result_id,
            errors=[_detector_error("adapter_execution_error", f"adapter {adapter_id} could not start: {exc}")],
        )
    if completed.returncode != 0:
        return _detector_result(
            result_id,
            errors=[
                _detector_error(
                    "adapter_nonzero_exit",
                    f"adapter {adapter_id} exited with status {completed.returncode}",
                )
            ],
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return _detector_result(
            result_id,
            errors=[_detector_error("invalid_adapter_json", f"adapter {adapter_id} output is not valid JSON: {exc.msg}")],
        )
    if not isinstance(payload, dict):
        return _detector_result(
            result_id,
            errors=[_detector_error("invalid_adapter_output", f"adapter {adapter_id} output must be a JSON object")],
        )
    payload = dict(payload)
    schema_errors = validate_detector_result(payload)
    if schema_errors:
        return _detector_result(
            result_id,
            errors=[_detector_error("invalid_adapter_output", "; ".join(schema_errors))],
        )
    if payload.get("id") != result_id:
        return _detector_result(
            result_id,
            errors=[
                _detector_error(
                    "invalid_adapter_output",
                    f"adapter {adapter_id} result id must be {result_id}",
                )
            ],
        )
    path_errors = _normalize_adapter_paths(payload, root=root)
    if path_errors:
        return _detector_result(result_id, errors=path_errors)
    return payload


def _detector_adapters(config: dict[str, Any], *, root: Path) -> list[dict[str, Any]]:
    adapters = config.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        return [
            _detector_result(
                "adapter-none",
                errors=[_detector_error("missing_adapter_config", "adapters detector is enabled but no adapters are configured")],
            )
        ]
    results: list[dict[str, Any]] = []
    for adapter in adapters:
        if isinstance(adapter, dict):
            results.append(_run_adapter(adapter, config, root=root))
    return results


def _max_report_severity(detectors: list[dict[str, Any]]) -> str:
    maximum = "none"
    for detector in detectors:
        for finding in detector.get("findings", []):
            severity = finding.get("severity", "major")
            if SEVERITY_ORDER.get(severity, 2) > SEVERITY_ORDER[maximum]:
                maximum = severity
        for error in detector.get("errors", []):
            severity = error.get("severity", "blocker")
            if SEVERITY_ORDER.get(severity, 3) > SEVERITY_ORDER[maximum]:
                maximum = severity
    return maximum


def _build_scan_report(
    *,
    root: Path,
    catalog_path: str,
    policy_path: str | None,
    complete: bool,
    fail_on: str,
    detectors: list[dict[str, Any]],
    configuration_diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    max_severity = _max_report_severity(detectors)
    threshold_reached = max_severity != "none" and SEVERITY_ORDER[max_severity] >= SEVERITY_ORDER[fail_on]
    return {
        "schema": SCAN_REPORT_SCHEMA_ID,
        "generated_at": _utc_now(),
        "workspace": {"root": root.as_posix()},
        "catalog_path": catalog_path,
        "policy_path": policy_path,
        "complete": complete,
        "fail_on": fail_on,
        "detectors": detectors,
        "configuration_diagnostics": configuration_diagnostics,
        "summary": {
            "detectors": len(detectors),
            "findings": sum(len(detector.get("findings", [])) for detector in detectors),
            "errors": sum(len(detector.get("errors", [])) for detector in detectors),
            "max_severity": max_severity,
            "threshold_reached": threshold_reached,
        },
    }


def validate_scan_report(report: Any) -> list[str]:
    return validate_with_schema(report, SCAN_REPORT_SCHEMA_FILE)


def validate_detector_result(result: Any) -> list[str]:
    return validate_with_schema(result, DETECTOR_RESULT_SCHEMA_FILE)


def scan_exit_code(report: dict[str, Any]) -> int:
    if not report.get("complete", False):
        return 2
    if report.get("summary", {}).get("threshold_reached") is True:
        return 1
    return 0


def scan_repository_knowledge(
    *,
    root: Path | None = None,
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    policy_path: Path | str = DEFAULT_POLICY_PATH,
    fail_on: str | None = None,
    enabled_detectors: list[str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root_from_path(root)
    try:
        validation = validate_catalog_and_policy(root=repo_root, catalog_path=catalog_path, policy_path=policy_path)
        catalog_display = validation.catalog_path
        policy_display = validation.policy_path
    except RepositoryKnowledgeError as exc:
        return _build_scan_report(
            root=repo_root,
            catalog_path=str(catalog_path),
            policy_path=str(policy_path),
            complete=False,
            fail_on=fail_on or DEFAULT_FAIL_ON,
            detectors=[],
            configuration_diagnostics=[
                {"code": "input_error", "path": "input", "message": str(exc), "severity": "blocker"}
            ],
        )

    config = _scan_config(validation.policy)
    threshold = _configured_fail_on(config, fail_on)
    active_missing = [diagnostic for diagnostic in validation.diagnostics if diagnostic.code == "active_path_missing"]
    configuration_diagnostics = [
        _diagnostic_payload(diagnostic)
        for diagnostic in validation.diagnostics
        if diagnostic.code not in {"not_configured", "active_path_missing"}
    ]
    if validation.catalog is None:
        configuration_diagnostics.append(
            {"code": "catalog_unavailable", "path": catalog_display, "message": "catalog did not load", "severity": "blocker"}
        )
    if configuration_diagnostics:
        return _build_scan_report(
            root=repo_root,
            catalog_path=catalog_display,
            policy_path=policy_display,
            complete=False,
            fail_on=threshold,
            detectors=[],
            configuration_diagnostics=configuration_diagnostics,
        )

    detectors: list[dict[str, Any]] = []
    requested = _configured_detectors(config, enabled_detectors)
    catalog = validation.catalog or {"records": []}
    for detector_id in requested:
        if detector_id not in CORE_DETECTORS:
            detectors.append(
                _detector_result(
                    detector_id,
                    errors=[_detector_error("unknown_detector", f"unknown maintenance detector: {detector_id}")],
                )
            )
            continue
        if detector_id == "catalog-coverage":
            detectors.append(_detector_catalog_coverage(config, catalog, root=repo_root))
        elif detector_id == "repository-orphans":
            detectors.append(_detector_repository_orphans(config, catalog, root=repo_root, active_missing=active_missing))
        elif detector_id == "markdown-local-links":
            detectors.append(_detector_markdown_local_links(config, root=repo_root))
        elif detector_id == "generated-freshness":
            detectors.append(_detector_generated_freshness(validation, catalog, root=repo_root))
        elif detector_id == "forbidden-active-references":
            detectors.append(_detector_forbidden_active_references(config, root=repo_root))
        elif detector_id == "adapters":
            detectors.extend(_detector_adapters(config, root=repo_root))

    return _build_scan_report(
        root=repo_root,
        catalog_path=catalog_display,
        policy_path=policy_display,
        complete=True,
        fail_on=threshold,
        detectors=detectors,
        configuration_diagnostics=[],
    )


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def dumps_result(result: ValidationResult) -> str:
    return json.dumps(result.to_json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
