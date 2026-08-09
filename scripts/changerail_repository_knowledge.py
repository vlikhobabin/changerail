"""Repository knowledge catalog and maintenance policy validation."""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
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
LIFECYCLE_REPORT_SCHEMA_ID = "changerail.maintenance-report.v1"
MAINTENANCE_STATE_SCHEMA_ID = "changerail.maintenance-state.v1"
MAINTENANCE_BASELINE_SCHEMA_ID = "changerail.maintenance-baseline.v1"
MAINTENANCE_TRIAGE_SCHEMA_ID = "changerail.maintenance-triage.v1"
SCAN_REPORT_SCHEMA_FILE = "changerail-maintenance-scan-report.schema.json"
DETECTOR_RESULT_SCHEMA_FILE = "changerail-maintenance-detector-result.schema.json"
LIFECYCLE_REPORT_SCHEMA_FILE = "changerail-maintenance-report.schema.json"
MAINTENANCE_STATE_SCHEMA_FILE = "changerail-maintenance-state.schema.json"
MAINTENANCE_BASELINE_SCHEMA_FILE = "changerail-maintenance-baseline.schema.json"
MAINTENANCE_TRIAGE_SCHEMA_FILE = "changerail-maintenance-triage.schema.json"
DEFAULT_CATALOG_PATH = Path(".changerail/knowledge.yaml")
DEFAULT_POLICY_PATH = Path(".changerail/maintenance.yaml")
DEFAULT_INDEX_PATH = Path(".changerail/KNOWLEDGE.md")
DEFAULT_BASELINE_PATH = Path(".changerail/maintenance-baseline.yaml")
DEFAULT_MAINTENANCE_RUNTIME_ROOT = Path(".runtime/changerail/maintenance")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
SECRET_LIKE_RE = re.compile(
    r"(?i)(?:secret|token|password|passwd|api[_-]?key|credential|private[_-]?key)\s*[:=]\s*\S+|\bAKIA[0-9A-Z]{16}\b"
)
SEVERITY_ORDER = {"none": -1, "info": 0, "minor": 1, "major": 2, "blocker": 3}
DEFAULT_FAIL_ON = "major"
IDENTITY_VERSION = 1
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


def validate_lifecycle_report(report: Any) -> list[str]:
    return validate_with_schema(report, LIFECYCLE_REPORT_SCHEMA_FILE)


def validate_maintenance_state(state: Any) -> list[str]:
    return validate_with_schema(state, MAINTENANCE_STATE_SCHEMA_FILE)


def validate_maintenance_baseline(baseline: Any) -> list[str]:
    errors = validate_with_schema(baseline, MAINTENANCE_BASELINE_SCHEMA_FILE)
    if errors or not isinstance(baseline, dict):
        return errors
    seen_accepted: set[str] = set()
    for index, entry in enumerate(baseline.get("accepted", [])):
        if not isinstance(entry, dict):
            continue
        fingerprint = entry.get("fingerprint")
        if isinstance(fingerprint, str):
            if fingerprint in seen_accepted:
                errors.append(f"accepted[{index}].fingerprint duplicate: {fingerprint}")
            seen_accepted.add(fingerprint)
    seen_waivers: set[str] = set()
    for index, entry in enumerate(baseline.get("waivers", [])):
        if not isinstance(entry, dict):
            continue
        fingerprint = entry.get("fingerprint")
        if isinstance(fingerprint, str):
            if fingerprint in seen_waivers:
                errors.append(f"waivers[{index}].fingerprint duplicate: {fingerprint}")
            seen_waivers.add(fingerprint)
        for field in ("expires_at", "review_after"):
            value = entry.get(field)
            if isinstance(value, str) and _parse_iso_boundary(value) is None:
                errors.append(f"waivers[{index}].{field} must be an ISO-8601 date or date-time")
    return errors


def validate_maintenance_triage(triage: Any) -> list[str]:
    return validate_with_schema(triage, MAINTENANCE_TRIAGE_SCHEMA_FILE)


def _repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: Any) -> str:
    return "sha256:" + sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _maintenance_diagnostic(
    code: str,
    path: str,
    message: str,
    *,
    severity: str = "blocker",
) -> dict[str, Any]:
    return {"code": code, "path": path, "message": message, "severity": severity}


def _state_file(root: Path, state_path: str | Path | None = None) -> Path:
    repo_root = repo_root_from_path(root)
    if state_path is None:
        return repo_root / DEFAULT_MAINTENANCE_RUNTIME_ROOT / "state.json"
    path = resolve_input_path(repo_root, state_path)
    rel_path = _repo_relative(path, repo_root)
    runtime_root = DEFAULT_MAINTENANCE_RUNTIME_ROOT.as_posix().rstrip("/")
    if not rel_path.startswith(f"{runtime_root}/"):
        raise RepositoryKnowledgeError(f"maintenance state path must be below {runtime_root}/: {rel_path}")
    return path


def _baseline_file(root: Path, baseline_path: str | Path | None = None) -> Path:
    return resolve_input_path(root, baseline_path or DEFAULT_BASELINE_PATH)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n")


def load_maintenance_state(root: Path, state_path: str | Path | None = None) -> tuple[dict[str, Any], bool, list[dict[str, Any]], str]:
    try:
        path = _state_file(root, state_path)
    except RepositoryKnowledgeError as exc:
        rel_path = str(state_path or DEFAULT_MAINTENANCE_RUNTIME_ROOT / "state.json")
        return {}, False, [_maintenance_diagnostic("maintenance_state_path_invalid", rel_path, str(exc))], rel_path
    rel_path = _repo_relative(path, root)
    if not path.exists():
        return {
            "schema": MAINTENANCE_STATE_SCHEMA_ID,
            "updated_at": _utc_now(),
            "identity_version": IDENTITY_VERSION,
            "findings": {},
        }, False, [], rel_path
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, False, [_maintenance_diagnostic("maintenance_state_invalid", rel_path, str(exc))], rel_path
    errors = validate_maintenance_state(state)
    if errors:
        return {}, False, [_maintenance_diagnostic("maintenance_state_schema_error", rel_path, "; ".join(errors))], rel_path
    if state.get("identity_version") != IDENTITY_VERSION:
        return {}, False, [
            _maintenance_diagnostic(
                "unsupported_maintenance_state_version",
                rel_path,
                f"unsupported identity_version: {state.get('identity_version')}",
            )
        ], rel_path
    return state, True, [], rel_path


def write_maintenance_state(root: Path, findings: list[dict[str, Any]], state_path: str | Path | None = None) -> str:
    path = _state_file(root, state_path)
    payload = {
        "schema": MAINTENANCE_STATE_SCHEMA_ID,
        "updated_at": _utc_now(),
        "identity_version": IDENTITY_VERSION,
        "findings": {
            finding["fingerprint"]: {
                "first_seen": finding["first_seen"],
                "last_seen": finding["last_seen"],
                "evidence_fingerprint": finding["evidence_fingerprint"],
                "status": finding["status"],
            }
            for finding in sorted(findings, key=lambda item: item["fingerprint"])
        },
    }
    errors = validate_maintenance_state(payload)
    if errors:
        raise RepositoryKnowledgeError("; ".join(errors))
    atomic_write_json(path, payload)
    return _repo_relative(path, root)


def _is_path_like_evidence(key: str, value: str) -> bool:
    lowered = key.lower()
    if "path" in lowered or lowered in {"href", "target", "source"}:
        return True
    if "\\" in value or value.startswith("/") or value.startswith("./") or value.startswith("../"):
        return True
    if WINDOWS_DRIVE_RE.match(value):
        return True
    return "/" in value and "://" not in value


def _sanitize_scalar_evidence(key: str, value: Any, *, root: Path, path: str) -> tuple[Any | None, list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    if isinstance(value, str):
        if SECRET_LIKE_RE.search(value):
            return None, [_maintenance_diagnostic("secret_like_evidence", path, f"secret-like evidence rejected for {key}")]
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            return None, [_maintenance_diagnostic("unsupported_evidence_reference", path, f"external evidence reference rejected for {key}")]
        if _is_path_like_evidence(key, value):
            normalized, diagnostic = normalize_repo_path(value, field=path, root=root)
            if diagnostic or not normalized:
                message = diagnostic.message if diagnostic else f"evidence path is invalid: {value}"
                return None, [_maintenance_diagnostic("unsafe_evidence_path", path, message)]
            return normalized, diagnostics
        return value, diagnostics
    if isinstance(value, (int, float, bool)) or value is None:
        return value, diagnostics
    return None, [_maintenance_diagnostic("unsupported_evidence_value", path, f"unsupported evidence value for {key}")]


def _normalized_subject(finding: dict[str, Any], *, root: Path, base_path: str) -> tuple[dict[str, str], list[dict[str, Any]]]:
    subject: dict[str, str] = {}
    diagnostics: list[dict[str, Any]] = []
    for field in ("path", "source_path", "target_path"):
        value = finding.get(field)
        if not isinstance(value, str):
            continue
        normalized, diagnostic = normalize_repo_path(value, field=f"{base_path}.{field}", root=root)
        if diagnostic or not normalized:
            message = diagnostic.message if diagnostic else f"finding {field} is invalid: {value}"
            diagnostics.append(_maintenance_diagnostic("unsafe_finding_subject", f"{base_path}.{field}", message))
        else:
            subject[field] = normalized
    fragment = finding.get("fragment")
    if isinstance(fragment, str):
        subject["fragment"] = fragment.lstrip("#")
    if not subject:
        subject["id"] = str(finding.get("id", "finding"))
    return subject, diagnostics


def _sanitize_evidence(
    finding: dict[str, Any],
    *,
    root: Path,
    base_path: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    evidence = finding.get("evidence")
    if evidence is None:
        return {}, [], []
    if not isinstance(evidence, dict):
        return {}, [], [_maintenance_diagnostic("unsupported_evidence_value", f"{base_path}.evidence", "evidence must be an object")]
    material: dict[str, Any] = {}
    refs: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for key in sorted(evidence):
        value, value_diagnostics = _sanitize_scalar_evidence(
            str(key),
            evidence[key],
            root=root,
            path=f"{base_path}.evidence.{key}",
        )
        diagnostics.extend(value_diagnostics)
        if value_diagnostics:
            continue
        material[str(key)] = value
        refs.append({"kind": "detector-evidence", "key": str(key), "value": value})
    return material, refs, diagnostics


def _normalize_lifecycle_finding(
    detector: dict[str, Any],
    finding: dict[str, Any],
    *,
    root: Path,
    state_findings: dict[str, Any],
    observed_at: str,
    base_path: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    subject, subject_diagnostics = _normalized_subject(finding, root=root, base_path=base_path)
    evidence_material, evidence_refs, evidence_diagnostics = _sanitize_evidence(finding, root=root, base_path=base_path)
    diagnostics = subject_diagnostics + evidence_diagnostics
    if diagnostics:
        return None, diagnostics
    detector_id = str(detector.get("id", "unknown"))
    rule = str(finding.get("code", "unknown"))
    identity_material = {
        "identity_version": IDENTITY_VERSION,
        "detector": detector_id,
        "rule": rule,
        "subject": subject,
    }
    fingerprint = _fingerprint(identity_material)
    evidence_fingerprint = _fingerprint({"finding": fingerprint, "evidence": evidence_material})
    previous = state_findings.get(fingerprint) if isinstance(state_findings, dict) else None
    first_seen = previous.get("first_seen") if isinstance(previous, dict) and isinstance(previous.get("first_seen"), str) else observed_at
    primary_path = subject.get("path") or subject.get("source_path") or subject.get("target_path")
    return {
        "fingerprint": fingerprint,
        "evidence_fingerprint": evidence_fingerprint,
        "detector": detector_id,
        "rule": rule,
        "severity": finding.get("severity", "major"),
        "confidence": 1.0,
        "path": primary_path,
        "subject": subject,
        "evidence_refs": evidence_refs,
        "remediation": None,
        "first_seen": first_seen,
        "last_seen": observed_at,
        "owner": None,
        "risk_class": "maintenance",
        "status": "open",
    }, []


def _detector_summaries(scan_report: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for detector in scan_report.get("detectors", []):
        if not isinstance(detector, dict):
            continue
        summaries.append(
            {
                "id": str(detector.get("id", "unknown")),
                "status": str(detector.get("status", "error")),
                "findings": len(detector.get("findings", [])) if isinstance(detector.get("findings"), list) else 0,
                "errors": len(detector.get("errors", [])) if isinstance(detector.get("errors"), list) else 0,
            }
        )
    return summaries


def _severity_threshold_reached(max_severity: str, fail_on: str) -> bool:
    return max_severity != "none" and SEVERITY_ORDER[max_severity] >= SEVERITY_ORDER[fail_on]


def _recalculate_lifecycle_summary(report: dict[str, Any]) -> None:
    max_severity = "none"
    for finding in report.get("findings", []):
        if not isinstance(finding, dict) or finding.get("status") != "open":
            continue
        severity = str(finding.get("severity", "major"))
        if SEVERITY_ORDER.get(severity, 2) > SEVERITY_ORDER[max_severity]:
            max_severity = severity
    for diagnostic in report.get("diagnostics", []):
        if not isinstance(diagnostic, dict):
            continue
        severity = str(diagnostic.get("severity", "blocker"))
        if SEVERITY_ORDER.get(severity, 3) > SEVERITY_ORDER[max_severity]:
            max_severity = severity
    findings = [finding for finding in report.get("findings", []) if isinstance(finding, dict)]
    report["summary"] = {
        "detectors": len(report.get("detectors", [])) if isinstance(report.get("detectors"), list) else 0,
        "findings": len(findings),
        "open": sum(1 for finding in findings if finding.get("status") == "open"),
        "accepted": sum(1 for finding in findings if finding.get("status") == "accepted"),
        "waived": sum(1 for finding in findings if finding.get("status") == "waived"),
        "diagnostics": len(report.get("diagnostics", [])) if isinstance(report.get("diagnostics"), list) else 0,
        "max_severity": max_severity,
        "threshold_reached": _severity_threshold_reached(max_severity, str(report.get("fail_on", DEFAULT_FAIL_ON))),
    }


def _source_scan_summary(scan_report: dict[str, Any], observed_at: str) -> dict[str, Any]:
    return {
        "schema": SCAN_REPORT_SCHEMA_ID,
        "generated_at": str(scan_report.get("generated_at") or observed_at),
        "catalog_path": str(scan_report.get("catalog_path") or DEFAULT_CATALOG_PATH.as_posix()),
        "policy_path": scan_report.get("policy_path") if isinstance(scan_report.get("policy_path"), str) else None,
        "complete": bool(scan_report.get("complete", False)),
    }


def _empty_lifecycle_report(
    *,
    root: Path,
    scan_report: dict[str, Any],
    observed_at: str,
    state_path: str,
    restored: bool,
    written: bool,
    diagnostics: list[dict[str, Any]],
    fail_on: str,
) -> dict[str, Any]:
    report = {
        "schema": LIFECYCLE_REPORT_SCHEMA_ID,
        "generated_at": observed_at,
        "workspace": {"root": root.as_posix()},
        "source_scan": _source_scan_summary(scan_report, observed_at),
        "state": {
            "path": state_path,
            "restored": restored,
            "written": written,
            "continuity": "restored" if restored else "not_restored",
        },
        "complete": False,
        "fail_on": fail_on,
        "summary": {
            "detectors": 0,
            "findings": 0,
            "open": 0,
            "accepted": 0,
            "waived": 0,
            "diagnostics": len(diagnostics),
            "max_severity": "blocker" if diagnostics else "none",
            "threshold_reached": bool(diagnostics) and SEVERITY_ORDER["blocker"] >= SEVERITY_ORDER[fail_on],
        },
        "detectors": [],
        "findings": [],
        "diagnostics": diagnostics,
    }
    return report


def _parse_iso_boundary(value: str) -> datetime | None:
    candidate = value.strip()
    if not candidate:
        return None
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate):
            return datetime.fromisoformat(candidate + "T00:00:00+00:00")
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_maintenance_baseline(
    root: Path,
    baseline_path: str | Path | None = None,
) -> tuple[dict[str, Any], bool, list[dict[str, Any]], str]:
    path = _baseline_file(root, baseline_path)
    rel_path = _repo_relative(path, root)
    if not path.exists():
        return {"schema": MAINTENANCE_BASELINE_SCHEMA_ID, "accepted": [], "waivers": []}, False, [], rel_path
    data, load_errors = load_yaml(path)
    if load_errors:
        return {}, True, [
            _maintenance_diagnostic(diagnostic.code, diagnostic.path, diagnostic.message)
            for diagnostic in load_errors
        ], rel_path
    data = _json_compatible_dates(data)
    errors = validate_maintenance_baseline(data)
    if errors:
        return {}, True, [_maintenance_diagnostic("maintenance_baseline_schema_error", rel_path, "; ".join(errors))], rel_path
    return data if isinstance(data, dict) else {}, True, [], rel_path


def _json_compatible_dates(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_compatible_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_compatible_dates(item) for item in value]
    return value


def apply_maintenance_baseline(
    report: dict[str, Any],
    baseline: dict[str, Any],
    *,
    observed_at: str,
    baseline_path: str,
) -> None:
    now = _parse_iso_boundary(observed_at) or datetime.now(timezone.utc)
    accepted = {
        entry.get("fingerprint"): entry
        for entry in baseline.get("accepted", [])
        if isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str)
    }
    waivers = [
        entry
        for entry in baseline.get("waivers", [])
        if isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str)
    ]
    diagnostics = report.setdefault("diagnostics", [])
    for finding in report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        fingerprint = finding.get("fingerprint")
        accepted_entry = accepted.get(fingerprint)
        if isinstance(accepted_entry, dict):
            finding["status"] = "accepted"
            finding["status_reason"] = str(accepted_entry.get("reason") or "accepted by maintenance baseline")
            owner = accepted_entry.get("owner")
            if isinstance(owner, str) and owner:
                finding["owner"] = owner
            continue
        matching_waivers = [entry for entry in waivers if entry.get("fingerprint") == fingerprint]
        for waiver in matching_waivers:
            boundary_value = waiver.get("expires_at") or waiver.get("review_after")
            boundary = _parse_iso_boundary(str(boundary_value)) if isinstance(boundary_value, str) else None
            if boundary is not None and boundary < now:
                diagnostics.append(
                    _maintenance_diagnostic(
                        "expired_maintenance_waiver",
                        baseline_path,
                        f"expired waiver does not suppress {fingerprint}",
                        severity="major",
                    )
                )
                continue
            finding["status"] = "waived"
            finding["status_reason"] = str(waiver.get("reason") or "waived by maintenance baseline")
            finding["owner"] = str(waiver.get("owner") or finding.get("owner") or "unassigned")
            finding["suppressed_until"] = boundary.isoformat().replace("+00:00", "Z") if boundary else None
            break
    _recalculate_lifecycle_summary(report)


def normalize_maintenance_report(
    scan_report: dict[str, Any],
    *,
    root: Path | None = None,
    state_path: str | Path | None = None,
    baseline_path: str | Path | None = None,
    write_state: bool = False,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root_from_path(root)
    observed_at = _utc_now()
    state, restored, state_diagnostics, state_rel_path = load_maintenance_state(repo_root, state_path)
    fail_on = str(scan_report.get("fail_on") or DEFAULT_FAIL_ON)
    if fail_on not in SEVERITY_ORDER:
        fail_on = DEFAULT_FAIL_ON
    if state_diagnostics:
        report = _empty_lifecycle_report(
            root=repo_root,
            scan_report=scan_report,
            observed_at=observed_at,
            state_path=state_rel_path,
            restored=False,
            written=False,
            diagnostics=state_diagnostics,
            fail_on=fail_on,
        )
        return report, 2

    scan_errors = validate_scan_report(scan_report)
    if scan_errors or scan_report.get("complete") is not True:
        diagnostics = [
            _maintenance_diagnostic("source_scan_schema_error", "scan", "; ".join(scan_errors))
        ] if scan_errors else []
        if scan_report.get("complete") is not True:
            diagnostics.append(_maintenance_diagnostic("source_scan_incomplete", "scan", "source scan report is incomplete"))
        for diagnostic in scan_report.get("configuration_diagnostics", []):
            if isinstance(diagnostic, dict):
                diagnostics.append(
                    _maintenance_diagnostic(
                        str(diagnostic.get("code", "configuration_diagnostic")),
                        str(diagnostic.get("path", "configuration")),
                        str(diagnostic.get("message", "configuration diagnostic")),
                        severity=str(diagnostic.get("severity", "blocker")),
                    )
                )
        report = _empty_lifecycle_report(
            root=repo_root,
            scan_report=scan_report,
            observed_at=observed_at,
            state_path=state_rel_path,
            restored=restored,
            written=False,
            diagnostics=diagnostics,
            fail_on=fail_on,
        )
        return report, 2

    findings: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    state_findings = state.get("findings", {}) if isinstance(state, dict) else {}
    for detector_index, detector in enumerate(scan_report.get("detectors", [])):
        if not isinstance(detector, dict):
            continue
        detector_id = str(detector.get("id", f"detector-{detector_index}"))
        for error in detector.get("errors", []) if isinstance(detector.get("errors"), list) else []:
            if isinstance(error, dict):
                diagnostics.append(
                    _maintenance_diagnostic(
                        str(error.get("code", "detector_error")),
                        str(error.get("path") or f"detectors.{detector_id}"),
                        str(error.get("message", "detector error")),
                        severity=str(error.get("severity", "blocker")),
                    )
                )
        for finding_index, finding in enumerate(detector.get("findings", [])):
            if not isinstance(finding, dict):
                continue
            normalized, finding_diagnostics = _normalize_lifecycle_finding(
                detector,
                finding,
                root=repo_root,
                state_findings=state_findings,
                observed_at=observed_at,
                base_path=f"detectors[{detector_index}].findings[{finding_index}]",
            )
            diagnostics.extend(finding_diagnostics)
            if normalized is not None:
                findings.append(normalized)

    report = {
        "schema": LIFECYCLE_REPORT_SCHEMA_ID,
        "generated_at": observed_at,
        "workspace": {"root": repo_root.as_posix()},
        "source_scan": _source_scan_summary(scan_report, observed_at),
        "state": {
            "path": state_rel_path,
            "restored": restored,
            "written": False,
            "continuity": "restored" if restored else "not_restored",
        },
        "complete": not diagnostics,
        "fail_on": fail_on,
        "summary": {
            "detectors": 0,
            "findings": 0,
            "open": 0,
            "accepted": 0,
            "waived": 0,
            "diagnostics": 0,
            "max_severity": "none",
            "threshold_reached": False,
        },
        "detectors": _detector_summaries(scan_report),
        "findings": sorted(findings, key=lambda item: item["fingerprint"]),
        "diagnostics": diagnostics,
    }

    baseline, baseline_configured, baseline_diagnostics, baseline_rel_path = load_maintenance_baseline(repo_root, baseline_path)
    if baseline_diagnostics:
        report["complete"] = False
        report["diagnostics"].extend(baseline_diagnostics)
    elif baseline_configured:
        apply_maintenance_baseline(report, baseline, observed_at=observed_at, baseline_path=baseline_rel_path)
    else:
        _recalculate_lifecycle_summary(report)

    if write_state and report["complete"]:
        try:
            write_maintenance_state(repo_root, report["findings"], state_path)
        except RepositoryKnowledgeError as exc:
            report["complete"] = False
            report["diagnostics"].append(_maintenance_diagnostic("maintenance_state_write_failed", state_rel_path, str(exc)))
        else:
            report["state"]["written"] = True
    _recalculate_lifecycle_summary(report)

    errors = validate_lifecycle_report(report)
    if errors:
        report["complete"] = False
        report["diagnostics"].append(_maintenance_diagnostic("maintenance_report_schema_error", "report", "; ".join(errors)))
        _recalculate_lifecycle_summary(report)
        return report, 2
    if not report["complete"]:
        return report, 2
    return report, 1 if report["summary"]["threshold_reached"] else 0


def baseline_from_report(
    report: dict[str, Any],
    *,
    owner: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for finding in report.get("findings", []):
        if not isinstance(finding, dict) or finding.get("status") != "open":
            continue
        entry: dict[str, Any] = {"fingerprint": finding["fingerprint"]}
        if owner:
            entry["owner"] = owner
        if reason:
            entry["reason"] = reason
        entry["accepted_at"] = report.get("generated_at")
        entries.append(entry)
    return {
        "schema": MAINTENANCE_BASELINE_SCHEMA_ID,
        "accepted": sorted(entries, key=lambda item: item["fingerprint"]),
        "waivers": [],
    }


def merge_baseline(existing: dict[str, Any], new_entries: dict[str, Any]) -> dict[str, Any]:
    accepted_by_fingerprint = {
        entry.get("fingerprint"): dict(entry)
        for entry in existing.get("accepted", [])
        if isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str)
    }
    for entry in new_entries.get("accepted", []):
        if isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str):
            accepted_by_fingerprint.setdefault(entry["fingerprint"], dict(entry))
    return {
        "schema": MAINTENANCE_BASELINE_SCHEMA_ID,
        "accepted": [accepted_by_fingerprint[key] for key in sorted(accepted_by_fingerprint)],
        "waivers": existing.get("waivers", []) if isinstance(existing.get("waivers"), list) else [],
    }


def write_maintenance_baseline(root: Path, baseline: dict[str, Any], baseline_path: str | Path | None = None) -> str:
    path = _baseline_file(root, baseline_path)
    errors = validate_maintenance_baseline(baseline)
    if errors:
        raise RepositoryKnowledgeError("; ".join(errors))
    text = yaml.safe_dump(baseline, sort_keys=False, allow_unicode=False)
    atomic_write_text(path, text)
    return _repo_relative(path, root)


def read_lifecycle_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RepositoryKnowledgeError(f"report cannot be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RepositoryKnowledgeError(f"report JSON is invalid: {exc}") from exc
    errors = validate_lifecycle_report(payload)
    if errors:
        raise RepositoryKnowledgeError("; ".join(errors))
    if not isinstance(payload, dict):
        raise RepositoryKnowledgeError("report must be a JSON object")
    return payload


def normalize_triage_annotations(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RepositoryKnowledgeError(f"annotations cannot be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RepositoryKnowledgeError(f"annotations JSON is invalid: {exc}") from exc
    errors = validate_maintenance_triage(payload)
    if errors:
        raise RepositoryKnowledgeError("; ".join(errors))
    annotations = payload.get("annotations", []) if isinstance(payload, dict) else []
    return {
        "schema": MAINTENANCE_TRIAGE_SCHEMA_ID,
        "generated_at": payload.get("generated_at"),
        "annotations": sorted(annotations, key=lambda item: item.get("fingerprint", "") if isinstance(item, dict) else ""),
    }


def _safe_slug(value: str, *, default: str = "finding") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def _safe_card_token(value: Any, *, field: str, diagnostics: list[dict[str, Any]]) -> str:
    raw = str(value or "unknown")
    if SECRET_LIKE_RE.search(raw):
        diagnostics.append(_maintenance_diagnostic("secret_like_card_value", field, f"secret-like card value rejected for {field}"))
        return "redacted"
    if "\\" in raw or raw.startswith("/") or WINDOWS_DRIVE_RE.match(raw) or urlsplit(raw).scheme or urlsplit(raw).netloc:
        diagnostics.append(_maintenance_diagnostic("unsafe_card_value", field, f"unsafe card value rejected for {field}"))
        return "redacted"
    return _safe_slug(raw, default="unknown")


def _validate_report_sourced_string(value: Any, *, field: str, root: Path, diagnostics: list[dict[str, Any]]) -> None:
    if not isinstance(value, str):
        return
    if SECRET_LIKE_RE.search(value):
        diagnostics.append(_maintenance_diagnostic("secret_like_card_value", field, f"secret-like report value rejected for {field}"))
        return
    if _is_path_like_evidence(field, value):
        _, diagnostic = normalize_repo_path(value, field=field, root=root)
        if diagnostic:
            diagnostics.append(_maintenance_diagnostic("unsafe_card_path", field, diagnostic.message))


def _finding_for_card(root: Path, finding: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    sanitized = dict(finding)
    path_value = finding.get("path")
    if isinstance(path_value, str):
        if SECRET_LIKE_RE.search(path_value):
            diagnostics.append(
                _maintenance_diagnostic(
                    "secret_like_card_value",
                    "finding.path",
                    "secret-like report value rejected for finding.path",
                )
            )
        else:
            normalized, diagnostic = normalize_repo_path(path_value, field="finding.path", root=root)
            if diagnostic or not normalized:
                diagnostics.append(
                    _maintenance_diagnostic(
                        "unsafe_card_path",
                        "finding.path",
                        diagnostic.message if diagnostic else f"invalid finding path: {path_value}",
                    )
                )
            else:
                sanitized["path"] = normalized
    elif path_value is not None:
        diagnostics.append(_maintenance_diagnostic("unsafe_card_path", "finding.path", "finding path must be a string or null"))

    subject = finding.get("subject")
    if isinstance(subject, dict):
        for key, value in subject.items():
            _validate_report_sourced_string(value, field=f"finding.subject.{key}", root=root, diagnostics=diagnostics)
    for index, reference in enumerate(finding.get("evidence_refs", []) if isinstance(finding.get("evidence_refs"), list) else []):
        if not isinstance(reference, dict):
            continue
        _validate_report_sourced_string(
            reference.get("value"),
            field=f"finding.evidence_refs[{index}].value",
            root=root,
            diagnostics=diagnostics,
        )

    sanitized["detector"] = _safe_card_token(finding.get("detector"), field="finding.detector", diagnostics=diagnostics)
    sanitized["rule"] = _safe_card_token(finding.get("rule"), field="finding.rule", diagnostics=diagnostics)
    sanitized["risk_class"] = _safe_card_token(finding.get("risk_class"), field="finding.risk_class", diagnostics=diagnostics)
    if diagnostics:
        return None, diagnostics
    return sanitized, []


def _card_origin_line(fingerprint: str) -> str:
    return f"Maintenance Origin: {fingerprint}"


def _card_body_for_finding(finding: dict[str, Any]) -> str:
    fingerprint = str(finding["fingerprint"])
    rule = _safe_slug(str(finding.get("rule", "finding")))
    path = finding.get("path") or "workspace"
    title = f"Maintenance finding {rule}"
    summary = f"Maintenance detector `{finding.get('detector')}` reported `{finding.get('rule')}` for `{path}`."
    return (
        f"# {title}\n\n"
        "## Status\n"
        "1.backlog\n\n"
        "## Owner\n"
        "unassigned\n\n"
        "## OpenSpec Stage\n"
        "story\n\n"
        "## Series\n"
        "- none\n\n"
        "## Series Index\n"
        "- none\n\n"
        "## Source\n"
        "- `bin/changerail-maintenance cards`\n\n"
        f"{_card_origin_line(fingerprint)}\n\n"
        "## Summary\n"
        f"{summary}\n\n"
        "## Acceptance\n"
        "- Finding is triaged, accepted with reviewed baseline, waived with an active owner/reason/boundary, or resolved by updating the affected knowledge artifact.\n\n"
        "## Change Set\n"
        "- none yet\n\n"
        "## Verify\n"
        "- `bin/changerail-maintenance report --json`\n\n"
        "## Archive\n"
        "- not started\n\n"
        "## Related\n"
        f"- `{path}`\n\n"
        "## Maintenance Evidence\n"
        f"- Fingerprint: `{fingerprint}`\n"
        f"- Detector: `{finding.get('detector')}`\n"
        f"- Rule: `{finding.get('rule')}`\n"
        f"- Severity: `{finding.get('severity')}`\n"
        f"- Risk class: `{finding.get('risk_class')}`\n\n"
        "## Result\n"
        "not started\n\n"
        "## Next\n"
        "- triage\n\n"
        "## Log\n"
        f"- `{_utc_now()}` card generated from maintenance lifecycle finding preview/write bridge\n"
    )


def _set_markdown_section_body(text: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\s*\n)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    replacement = f"## {heading}\n{body.rstrip()}\n\n"
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1).rstrip() + "\n"
    return text.rstrip() + f"\n\n{replacement}"


def find_board_card_by_origin(root: Path, fingerprint: str) -> tuple[Path | None, list[dict[str, Any]]]:
    board_root = root / "openspec" / "board"
    marker = _card_origin_line(fingerprint)
    matches: list[Path] = []
    diagnostics: list[dict[str, Any]] = []
    for lane in ("1.backlog", "2.todo", "3.inprogress", "4.done", "5.canceled"):
        lane_root = board_root / lane
        if not lane_root.is_dir():
            continue
        for candidate in sorted(lane_root.glob("*.md")):
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError as exc:
                diagnostics.append(_maintenance_diagnostic("board_card_read_error", _repo_relative(candidate, root), str(exc)))
                continue
            count = sum(1 for line in text.splitlines() if line == marker)
            if count > 1:
                diagnostics.append(
                    _maintenance_diagnostic(
                        "duplicate_origin_marker_in_card",
                        _repo_relative(candidate, root),
                        f"card contains {count} maintenance origin markers for {fingerprint}",
                    )
                )
            if count == 1:
                matches.append(candidate)
    if len(matches) > 1:
        diagnostics.append(
            _maintenance_diagnostic(
                "duplicate_maintenance_cards",
                "openspec/board",
                f"multiple cards contain maintenance origin {fingerprint}",
            )
        )
    return (matches[0] if len(matches) == 1 else None), diagnostics


def upsert_maintenance_card(root: Path, finding: dict[str, Any], *, write: bool) -> dict[str, Any]:
    card_finding, finding_diagnostics = _finding_for_card(root, finding)
    fingerprint = str(finding.get("fingerprint", "unknown"))
    if finding_diagnostics or card_finding is None:
        return {"ok": False, "fingerprint": fingerprint, "diagnostics": finding_diagnostics}
    finding = card_finding
    fingerprint = str(finding["fingerprint"])
    card_text = _card_body_for_finding(finding)
    digest = fingerprint.split(":", 1)[1][:12]
    filename = f"maintenance-{digest}-{_safe_slug(str(finding.get('rule', 'finding')))}.md"
    diagnostics: list[dict[str, Any]] = []
    existing, marker_diagnostics = find_board_card_by_origin(root, fingerprint)
    diagnostics.extend(marker_diagnostics)
    if diagnostics:
        return {"ok": False, "fingerprint": fingerprint, "diagnostics": diagnostics}
    if write:
        target = existing or (root / "openspec" / "board" / "1.backlog" / filename)
        if existing:
            current = target.read_text(encoding="utf-8")
            evidence = (
                f"- Fingerprint: `{fingerprint}`\n"
                f"- Detector: `{finding.get('detector')}`\n"
                f"- Rule: `{finding.get('rule')}`\n"
                f"- Severity: `{finding.get('severity')}`\n"
                f"- Risk class: `{finding.get('risk_class')}`\n"
                f"- Last seen: `{finding.get('last_seen')}`\n"
            )
            card_text = _set_markdown_section_body(current, "Maintenance Evidence", evidence)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(card_text, encoding="utf-8")
        return {"ok": True, "mode": "write", "fingerprint": fingerprint, "path": _repo_relative(target, root), "updated": existing is not None}
    target = root / DEFAULT_MAINTENANCE_RUNTIME_ROOT / "previews" / "cards" / filename
    atomic_write_text(target, card_text)
    return {"ok": True, "mode": "preview", "fingerprint": fingerprint, "path": _repo_relative(target, root), "updated": existing is not None}


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
