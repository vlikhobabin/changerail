"""Repository knowledge catalog and maintenance policy validation."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from changerail_contract_schema import validate_with_schema

CATALOG_SCHEMA_ID = "changerail.repository-knowledge.v1"
POLICY_SCHEMA_ID = "changerail.maintenance-policy.v1"
CATALOG_SCHEMA_FILE = "changerail-repository-knowledge.schema.json"
POLICY_SCHEMA_FILE = "changerail-maintenance-policy.schema.json"
DEFAULT_CATALOG_PATH = Path(".changerail/knowledge.yaml")
DEFAULT_POLICY_PATH = Path(".changerail/maintenance.yaml")
DEFAULT_INDEX_PATH = Path(".changerail/KNOWLEDGE.md")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


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


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def dumps_result(result: ValidationResult) -> str:
    return json.dumps(result.to_json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
