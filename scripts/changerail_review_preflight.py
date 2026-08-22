"""Deterministic gate before ChangeRail payload review."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from changerail_contract_schema import validate_with_schema
from changerail_execution_target import describe_execution_target, execution_targets_match, load_execution_target
from changerail_source_classification import SourceClassificationError, check_report as source_classification_check_report
from changerail_verification_coverage import coverage_preflight_check
import changerail_delivery_manifest as dm

SCHEMA_ID = "changerail.review-preflight-result.v1"
SCHEMA_FILE = "changerail-review-preflight-result.schema.json"
SOURCE_CLASSIFICATION_SCHEMA_FILE = "changerail-source-classification.schema.json"
SOURCE_CLASSIFICATION_PATH = ".changerail/source-classification.yaml"
PRODUCTION_SUFFIXES = {".c", ".cc", ".cpp", ".cs", ".go", ".h", ".hpp", ".java", ".js", ".jsx", ".kt", ".php", ".py", ".rb", ".rs", ".sh", ".ts", ".tsx"}
NON_PRODUCTION_PARTS = {"docs", "examples", "fixtures", "openspec", "schemas", "templates", "test", "tests"}
DEFAULT_PRODUCTION_LOC_LIMIT = 300
MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT = 500
MAX_BREAKDOWN_PATHS = 20
AUTHORIZATION_FIELD = "Published investigation authorization"
AUTHORIZATION_SOURCE_FIELD = "Investigation authorization"
CARD_ID_RE = r"[a-z0-9][a-z0-9-]*"
BOARD_CARD_REFERENCE_RE = re.compile(rf"^openspec/board/[1-5]\.(?:backlog|todo|inprogress|done|canceled)/({CARD_ID_RE})\.md$")
CARD_FILENAME_RE = re.compile(rf"^({CARD_ID_RE})\.md$")
BARE_CARD_ID_RE = re.compile(rf"^{CARD_ID_RE}$")


@dataclass(frozen=True)
class SourceKindRule:
    id: str
    suffixes: tuple[str, ...]
    production_roots: tuple[str, ...]
    measure: str


@dataclass(frozen=True)
class SourceClassification:
    present: bool
    rules: tuple[SourceKindRule, ...]
    non_production_roots: tuple[str, ...]
    errors: tuple[str, ...] = ()


def _classification(present: bool, rules: Any = (), non_production_roots: Any = (), errors: Any = ()) -> SourceClassification:
    return SourceClassification(present, tuple(rules), tuple(non_production_roots), tuple(errors))


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(name)}:\s*(.*?)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip().lower()


def _boolean(value: str | None, name: str) -> bool:
    if value in (None, "no", "false"):
        return False
    if value in ("yes", "true"):
        return True
    raise ValueError(f"{name} must be yes or no")


def _raw_field(text: str, name: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(name)}:\s*(.+?)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value


def _risk(text: str, override: str | None) -> dict[str, Any]:
    declared = _field(text, "Risk tier")
    declared = "deterministic" if declared == "process" else declared
    override = "deterministic" if override == "process" else override
    rank = {"deterministic": 0, "ordinary": 1, "critical": 2}
    tier = declared or "ordinary"
    if override and rank.get(override, -1) > rank.get(tier, -1):
        tier = override
    if tier not in rank:
        raise ValueError("Risk tier must be deterministic, ordinary or critical")
    source = "cli" if override == tier else ("card" if declared else "legacy-default")
    route = {"deterministic": ("machine-only", "none"), "ordinary": ("llm", "high"), "critical": ("llm", "xhigh")}[tier]
    return {"tier": tier, "source": source, "review_mode": route[0], "reasoning_effort": route[1]}


def _check(checks: list[dict[str, Any]], name: str, ok: bool, detail: str, command: list[str] | None = None) -> None:
    item: dict[str, Any] = {"id": name, "status": "pass" if ok else "fail", "detail": detail[:2000]}
    if command:
        item["command"] = command
    checks.append(item)


def _run(workspace: Path, command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, check=False, timeout=600)
    except subprocess.TimeoutExpired:
        return False, "command timed out after 600 seconds"
    detail = (result.stdout + "\n" + result.stderr).strip() or f"exit={result.returncode}"
    return result.returncode == 0, detail[-2000:]


def _timed(timings: list[dict[str, Any]], phase: str, func: Callable[[], Any]) -> Any:
    start = time.perf_counter()
    try:
        return func()
    finally:
        timings.append({"phase": phase, "duration_ms": round((time.perf_counter() - start) * 1000, 3)})


def _fingerprint(fingerprint_fn: Callable[..., dict[str, Any]], workspace: Path, diagnostics: bool) -> dict[str, Any]:
    try:
        return fingerprint_fn(workspace, use_cache=True, diagnostics=diagnostics)
    except TypeError:
        return fingerprint_fn(workspace)


def _safe_classification_path(value: Any, label: str) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, f"{label} must be a non-empty repository-relative path"
    raw = value.strip().rstrip("/")
    path = PurePosixPath(raw)
    if raw in {"", "."} or "\\" in raw or raw.startswith(("~", "/")) or path.is_absolute():
        return None, f"{label} must be a repository-relative POSIX path below the repository root"
    if any(part in {"", ".", ".."} for part in path.parts):
        return None, f"{label} must not contain traversal or empty path parts"
    normalized = path.as_posix()
    if normalized != raw:
        return None, f"{label} must be normalized as {normalized!r}"
    return normalized, None


def _load_source_classification(workspace: Path) -> SourceClassification:
    config_path = workspace / SOURCE_CLASSIFICATION_PATH
    if not config_path.is_file():
        return _classification(False)
    try:
        import yaml
    except Exception as exc:
        return _classification(True, errors=(f"PyYAML is required to read {SOURCE_CLASSIFICATION_PATH}: {type(exc).__name__}: {exc}",))
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return _classification(True, errors=(f"{SOURCE_CLASSIFICATION_PATH} cannot be parsed: {exc}",))
    schema_errors = validate_with_schema(data, SOURCE_CLASSIFICATION_SCHEMA_FILE)
    if schema_errors:
        return _classification(True, errors=tuple(f"schema: {error}" for error in schema_errors))
    if not isinstance(data, dict):
        return _classification(True, errors=(f"{SOURCE_CLASSIFICATION_PATH} must be a mapping",))

    errors: list[str] = []
    rules: list[SourceKindRule] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(data.get("source_kinds", [])):
        label = f"source_kinds[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        source_id = item.get("id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if source_id in seen_ids:
            errors.append(f"{label}.id duplicates {source_id!r}")
        seen_ids.add(source_id)
        suffixes = tuple(sorted({str(suffix).lower() for suffix in item.get("suffixes", [])}))
        if len(suffixes) != len(item.get("suffixes", [])):
            errors.append(f"{label}.suffixes contains case-insensitive duplicates")
        production_roots: list[str] = []
        for root_index, root in enumerate(item.get("production_roots", [])):
            normalized, error = _safe_classification_path(root, f"{label}.production_roots[{root_index}]")
            if error:
                errors.append(error)
            elif normalized:
                production_roots.append(normalized)
        if len(set(production_roots)) != len(production_roots):
            errors.append(f"{label}.production_roots contains duplicate roots")
        measure = item.get("measure")
        if measure == "xml-structure" and ".xml" not in suffixes:
            errors.append(f"{label}.measure xml-structure requires a .xml suffix")
        if not errors:
            rules.append(
                SourceKindRule(
                    id=source_id,
                    suffixes=suffixes,
                    production_roots=tuple(production_roots),
                    measure=str(measure),
                )
            )

    non_production_roots: list[str] = []
    for index, root in enumerate(data.get("non_production_roots", [])):
        normalized, error = _safe_classification_path(root, f"non_production_roots[{index}]")
        if error:
            errors.append(error)
        elif normalized:
            non_production_roots.append(normalized)
    if len(set(non_production_roots)) != len(non_production_roots):
        errors.append("non_production_roots contains duplicate roots")
    if errors:
        return _classification(True, errors=errors)
    return _classification(True, rules, non_production_roots)


def _path_under(path: str, root: str) -> bool:
    candidate_parts = PurePosixPath(path).parts
    root_parts = PurePosixPath(root).parts
    return candidate_parts[: len(root_parts)] == root_parts


def _non_production_path(path: str, extra_roots: tuple[str, ...] = ()) -> bool:
    candidate = PurePosixPath(path)
    lowered = {part.lower() for part in candidate.parts}
    if lowered & NON_PRODUCTION_PARTS:
        return True
    return any(_path_under(path, root) for root in extra_roots)


def _builtin_production_path(workspace: Path, path: str, extra_non_production_roots: tuple[str, ...] = ()) -> bool:
    candidate = PurePosixPath(path)
    name = candidate.name.lower()
    executable_path = workspace / path
    executable = candidate.parts[:1] == ("bin",) and not candidate.suffix and executable_path.is_file() and bool(executable_path.stat().st_mode & 0o111)
    if name.endswith("_test.go") or name.startswith(("test_", "smoke-", "smoke_")):
        return False
    return (candidate.suffix.lower() in PRODUCTION_SUFFIXES or executable) and not _non_production_path(path, extra_non_production_roots)


def _matches_source_rule(rule: SourceKindRule, path: str) -> bool:
    candidate = PurePosixPath(path)
    return candidate.suffix.lower() in rule.suffixes and any(_path_under(path, root) for root in rule.production_roots)


def _file_line_count(path: Path) -> int:
    payload = path.read_bytes()
    if b"\0" in payload:
        return 0
    return len(payload.splitlines())


def _raw_added_lines(workspace: Path, entries: dict[str, dict[str, Any]]) -> dict[str, int]:
    lines: dict[str, int] = {}
    paths = sorted(path for path, entry in entries.items() if entry.get("operation") != "delete")
    if paths:
        result = subprocess.run(
            ["git", "-C", str(workspace), "diff", "--numstat", "HEAD", "--", *paths],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git diff --numstat failed")
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0].isdigit():
                lines[parts[2]] = int(parts[0])
    for path, entry in entries.items():
        if entry.get("operation") != "add" or path in lines:
            continue
        target = entry.get("target_path") or entry.get("path") or path
        if not isinstance(target, str):
            continue
        absolute = workspace / target
        if absolute.is_file():
            lines[path] = _file_line_count(absolute)
    return lines


def _xml_structure_units(path: Path) -> tuple[int | None, str | None]:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return None, f"xml-structure fallback to raw lines: {exc}"
    units = 0
    for element in root.iter():
        units += 1
        if element.text and element.text.strip():
            units += 1
        if element.tail and element.tail.strip():
            units += 1
    return units, None


def _breakdown_bucket(
    buckets: dict[tuple[str, str], dict[str, Any]],
    source_kind: str,
    measure_strategy: str,
) -> dict[str, Any]:
    key = (source_kind, measure_strategy)
    if key not in buckets:
        buckets[key] = {"source_kind": source_kind, "measure_strategy": measure_strategy, "path_count": 0, "raw_added_lines": 0,
                        "effective_complexity": 0, "fallback": "none", "paths": [], "excluded_path_count": 0,
                        "excluded_raw_added_lines": 0, "notes": []}
    return buckets[key]


def _append_bounded(values: list[str], value: str) -> None:
    if value not in values and len(values) < MAX_BREAKDOWN_PATHS:
        values.append(value)


def _complexity_measure(
    workspace: Path,
    path: str,
    entry: dict[str, Any],
    raw_lines: int,
    rule: SourceKindRule,
) -> tuple[int, str, str | None]:
    if rule.measure != "xml-structure":
        return raw_lines, "none", None
    target = entry.get("target_path") or entry.get("path") or path
    if entry.get("operation") != "add":
        return raw_lines, "raw-lines", "modified classified XML uses raw added lines"
    if not isinstance(target, str):
        return raw_lines, "raw-lines", "classified XML target path is unavailable"
    effective, note = _xml_structure_units(workspace / target)
    if effective is None:
        return raw_lines, "raw-lines", note
    return effective, "none", None


def _finalize_breakdown(buckets: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    finalized: list[dict[str, Any]] = []
    for key in sorted(buckets):
        bucket = buckets[key]
        entry = {field: bucket[field] for field in ("source_kind", "measure_strategy", "path_count", "raw_added_lines", "effective_complexity", "fallback")}
        if bucket["paths"]:
            entry["paths"] = bucket["paths"]
        if bucket["excluded_path_count"]:
            entry["excluded_path_count"] = bucket["excluded_path_count"]
            entry["excluded_raw_added_lines"] = bucket["excluded_raw_added_lines"]
        if bucket["notes"]:
            entry["notes"] = bucket["notes"][:MAX_BREAKDOWN_PATHS]
        finalized.append(entry)
    return finalized


def _production_complexity(
    workspace: Path,
    entries: dict[str, dict[str, Any]],
    classification: SourceClassification,
) -> dict[str, Any]:
    raw_by_path = _raw_added_lines(workspace, entries)
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    total = 0
    for path in sorted(entries):
        entry = entries[path]
        if entry.get("operation") == "delete":
            continue
        raw_lines = raw_by_path.get(path, 0)
        matched_rules = [rule for rule in classification.rules if _matches_source_rule(rule, path)]
        excluded = _non_production_path(path, classification.non_production_roots)
        if excluded:
            for rule in matched_rules:
                bucket = _breakdown_bucket(buckets, rule.id, rule.measure)
                bucket["excluded_path_count"] += 1
                bucket["excluded_raw_added_lines"] += raw_lines
            continue
        rule = matched_rules[0] if matched_rules else None
        if rule is None:
            if not _builtin_production_path(workspace, path, classification.non_production_roots):
                continue
            rule = SourceKindRule("builtin", (PurePosixPath(path).suffix.lower(),), (), "lines")
        effective, fallback, note = _complexity_measure(workspace, path, entry, raw_lines, rule)
        bucket = _breakdown_bucket(buckets, rule.id, rule.measure)
        bucket["path_count"] += 1
        bucket["raw_added_lines"] += raw_lines
        bucket["effective_complexity"] += effective
        if fallback != "none":
            bucket["fallback"] = fallback
        if note:
            _append_bounded(bucket["notes"], f"{path}: {note}")
        _append_bounded(bucket["paths"], path)
        total += effective
    return {"added_production_loc": total, "source_breakdown": _finalize_breakdown(buckets)}


def _reference_matches(text: str, heading: str, expected: str) -> bool:
    references = re.findall(r"`([^`\n]+)`", dm.section_body(text, heading))
    normalized: set[str] = set()
    for reference in references:
        if BARE_CARD_ID_RE.fullmatch(reference):
            normalized.add(reference)
            continue
        filename = CARD_FILENAME_RE.fullmatch(reference)
        board_path = BOARD_CARD_REFERENCE_RE.fullmatch(reference)
        if filename:
            normalized.add(filename.group(1))
        elif board_path:
            normalized.add(board_path.group(1))
    return expected in normalized


def _tracked_at_head(workspace: Path, path: str) -> bool:
    for command in (("cat-file", "-e", f"HEAD:{path}"), ("diff", "--quiet", "HEAD", "--", path)):
        result = subprocess.run(["git", "-C", str(workspace), *command], capture_output=True, text=True, check=False)
        if result.returncode:
            return False
    return True


def _published_investigation_authorization(review_text: str, card_text: str, card: dict[str, Any], workspace: Path) -> dict[str, Any]:
    raw = _raw_field(review_text, AUTHORIZATION_FIELD)
    state: dict[str, Any] = {"status": "not-declared", "detail": "no published investigation authorization is declared"}
    if raw is None or raw.lower() == "none":
        return state
    try:
        reference = json.loads(raw)
        if not isinstance(reference, dict) or set(reference) != {"authorization_card", "authorization_id"}:
            raise ValueError("authorization reference must contain exactly authorization_card and authorization_id")
        if not all(isinstance(reference[field], str) and reference[field] for field in reference):
            raise ValueError("authorization reference values must be non-empty strings")
        source_path = (workspace / reference["authorization_card"]).resolve(strict=False)
        if not source_path.is_relative_to(workspace) or not source_path.is_file():
            raise ValueError("authorization source card cannot be read")
        source_text, source = dm.read_card(source_path, workspace)
        if not source["path"].startswith("openspec/board/4.done/") or source["status"] != "4.done":
            raise ValueError("authorization source card is not published in 4.done")
        if reference["authorization_card"] != source["path"] or reference["authorization_id"] != source["id"]:
            raise ValueError("authorization source path/id does not match the published card")
        if not _tracked_at_head(workspace, source["path"]):
            raise ValueError("authorization source card is not an unchanged tracked HEAD artifact")
        authorization_raw = _raw_field(source_text, AUTHORIZATION_SOURCE_FIELD)
        authorization = json.loads(authorization_raw or "")
        expected_fields = {"investigation_card", "investigation_id", "successor_card", "successor_id", "production_loc_ceiling", "allow_new_authority_or_wire_protocol"}
        if not isinstance(authorization, dict) or set(authorization) != expected_fields:
            raise ValueError("authorization source must contain exactly the required fields")
        string_fields = expected_fields - {"production_loc_ceiling", "allow_new_authority_or_wire_protocol"}
        if not all(isinstance(authorization[field], str) and authorization[field] for field in string_fields):
            raise ValueError("authorization source card paths and ids must be non-empty strings")
        ceiling = authorization["production_loc_ceiling"]
        if isinstance(ceiling, bool) or not isinstance(ceiling, int) or not DEFAULT_PRODUCTION_LOC_LIMIT < ceiling <= MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT:
            raise ValueError(f"production_loc_ceiling must be an integer from {DEFAULT_PRODUCTION_LOC_LIMIT + 1} through {MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT}")
        if not isinstance(authorization["allow_new_authority_or_wire_protocol"], bool):
            raise ValueError("allow_new_authority_or_wire_protocol must be a boolean")
        if authorization["successor_card"] != card["path"] or authorization["successor_id"] != card["id"]:
            raise ValueError("authorization source successor path/id does not match the target card")
        investigation_path = (workspace / authorization["investigation_card"]).resolve(strict=False)
        if not investigation_path.is_relative_to(workspace) or not investigation_path.is_file():
            raise ValueError("authorization source investigation card cannot be read")
        investigation_text, investigation = dm.read_card(investigation_path, workspace)
        if not investigation["path"].startswith("openspec/board/4.done/") or investigation["status"] != "4.done":
            raise ValueError("authorization source investigation card is not published in 4.done")
        if authorization["investigation_card"] != investigation["path"] or authorization["investigation_id"] != investigation["id"]:
            raise ValueError("authorization source investigation path/id does not match the published card")
        if not _tracked_at_head(workspace, investigation["path"]):
            raise ValueError("authorization investigation card is not an unchanged tracked HEAD artifact")
        if not _reference_matches(card_text, "Depends On", investigation["id"]):
            raise ValueError("successor Depends On does not reference the investigation id")
        if not _reference_matches(investigation_text, "Blocks", card["id"]):
            raise ValueError("published investigation Blocks does not reference the target card id")
        if not _reference_matches(source_text, "Depends On", investigation["id"]):
            raise ValueError("authorization source Depends On does not reference the investigation id")
        return {"status": "valid", "detail": "published authorization source binds the exact successor", "reference": reference, "authorization": authorization}
    except (json.JSONDecodeError, ValueError, dm.ManifestError) as exc:
        state.update({"status": "invalid", "detail": str(exc)})
        return state



def _normalize_manifest(manifest: dict[str, Any], card: dict[str, Any], card_text: str, workspace: Path) -> bool:
    excluded = dm.scope_excluded_paths(manifest)
    expected = dm.scope_expected_entries(manifest, excluded)
    actual = dm.scope_actual_entries(workspace, "working-tree", excluded)
    if set(expected) != set(actual):
        return False
    changed = manifest.get("card") != card
    manifest["card"] = card
    changes = dm.classify_changes(workspace, dm.parse_change_slugs(card_text))
    changed = changed or manifest.get("changes") != changes
    manifest["changes"] = changes
    for entry in manifest.get("committable_paths", []):
        normalized = dm.comparable_scope(entry)
        key = entry.get("target_path") or entry.get("source_path") or entry.get("path")
        if not isinstance(key, str) or key not in actual:
            continue
        current = dm.comparable_scope(actual[key])
        if normalized == current:
            continue
        changed = True
        for field in ("operation", "source_path", "target_path"):
            entry.pop(field, None)
        entry.update(current)
    if changed:
        manifest["updated_at"] = dm.utc_now()
    return changed


def _previous_verdict(path: Path, fingerprint: dict[str, str], validate_verdict: Callable[[Any], list[str]]) -> tuple[bool, str]:
    if not path.is_file():
        return False, "no previous verdict; route the current payload by risk"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"previous verdict is unreadable and will be replaced: {exc}"
    errors = validate_verdict(data)
    reviewed = data.get("workspace", {}) if isinstance(data, dict) else {}
    fresh = not errors and all(reviewed.get(key) == fingerprint[key] for key in ("head_commit", "tree_sha", "diff_fingerprint"))
    if fresh and data.get("result") == "go":
        return True, "existing GO verdict is fresh for the exact payload"
    return False, "previous verdict is absent, negative, invalid or stale; it is not a process blocker"


def _target_token(identity: dict[str, Any]) -> str:
    return json.dumps(
        {
            key: identity.get(key)
            for key in ("schema", "id", "fingerprint", "target_substitution_policy")
        },
        ensure_ascii=True,
        sort_keys=True,
    )


def _manifest_evidence_refs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    summary = manifest.get("verification_summary")
    if not isinstance(summary, dict):
        return refs
    refs.extend(ref for ref in summary.get("evidence_refs", []) if isinstance(ref, dict))
    for command in summary.get("commands", []):
        if isinstance(command, dict) and isinstance(command.get("evidence"), dict):
            refs.append(command["evidence"])
    return refs


def _evidence_target_identities(workspace: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    identities: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    active_raw = os.environ.get("CHANGERAIL_ACTIVE_RUN_DIR")
    active = Path(active_raw).resolve(strict=False) if active_raw else None
    for ref in _manifest_evidence_refs(manifest):
        raw_index = ref.get("index_path")
        if not isinstance(raw_index, str) or not raw_index:
            continue
        index_path = workspace / raw_index
        resolved = index_path.resolve(strict=False)
        if not resolved.is_relative_to(workspace):
            errors.append(f"evidence index path escapes workspace: {raw_index}")
            continue
        if active is not None and resolved.is_relative_to(active):
            errors.append(f"evidence index path is under active runner evidence: {raw_index}")
            continue
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(f"evidence index cannot be read: {raw_index}: {exc}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"evidence index JSON is invalid: {raw_index}: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"evidence index must be an object: {raw_index}")
            continue
        candidates = [payload.get("execution_target")]
        candidates.extend(
            entry.get("execution_target")
            for entry in payload.get("entries", [])
            if isinstance(entry, dict)
        )
        for candidate in candidates:
            if isinstance(candidate, dict):
                identities[_target_token(candidate)] = candidate
    return list(identities.values()), errors


def _execution_target_state(workspace: Path, manifest: dict[str, Any] | None) -> tuple[dict[str, Any], bool, str]:
    target = load_execution_target(workspace, require_tracked=True)
    identity = target.get("identity")
    state: dict[str, Any] = {
        "present": bool(target.get("present")),
        "path": str(target.get("path") or ".changerail/execution-target.json"),
        "evidence_identity_count": 0,
    }
    errors = list(target.get("errors") or [])
    if isinstance(identity, dict):
        state["identity"] = identity
    manifest_identity = manifest.get("execution_target") if isinstance(manifest, dict) else None
    if isinstance(manifest_identity, dict):
        state["manifest_identity"] = manifest_identity
    if errors:
        state["errors"] = errors
        return state, False, "; ".join(errors)
    if isinstance(identity, dict):
        if not isinstance(manifest_identity, dict):
            errors.append("delivery manifest is missing execution_target for declared project target")
        elif not execution_targets_match(identity, manifest_identity):
            errors.append(
                "delivery manifest execution_target differs from current declaration: "
                f"manifest {describe_execution_target(manifest_identity)} current {describe_execution_target(identity)}"
            )
        evidence_identities, evidence_errors = _evidence_target_identities(workspace, manifest or {})
        state["evidence_identity_count"] = len(evidence_identities)
        errors.extend(evidence_errors)
        if len(evidence_identities) == 0:
            errors.append("target-bound verification evidence is missing execution_target")
        elif len(evidence_identities) > 1:
            errors.append("target-bound verification evidence contains multiple execution targets")
        elif not execution_targets_match(identity, evidence_identities[0]):
            errors.append(
                "target-bound verification evidence differs from current declaration: "
                f"evidence {describe_execution_target(evidence_identities[0])} current {describe_execution_target(identity)}"
            )
    elif isinstance(manifest_identity, dict):
        errors.append("delivery manifest retains execution_target but current declaration is absent")
    if errors:
        state["errors"] = errors
        return state, False, "; ".join(errors)
    if isinstance(identity, dict):
        return state, True, f"execution target preserved: {describe_execution_target(identity)}"
    return state, True, "no execution target declaration; legacy-compatible flow"


def run_preflight(*, card_path: Path, workspace: Path, manifest_path: Path | None, normalize: bool,
                  risk_override: str | None, output: Path | None, fingerprint_fn: Callable[..., dict[str, Any]],
                  validate_verdict: Callable[[Any], list[str]], diagnostics: bool = False) -> tuple[int, dict[str, Any]]:
    workspace = workspace.resolve(strict=False)
    card_text, card = dm.read_card(card_path, workspace)
    review_text = dm.section_body(card_text, "Review")
    timings: list[dict[str, Any]] = []
    fingerprint = _timed(timings, "fingerprint", lambda: _fingerprint(fingerprint_fn, workspace, diagnostics))
    manifest_path = manifest_path or dm.default_manifest_path(workspace, card)
    if not manifest_path.is_absolute():
        manifest_path = workspace / manifest_path
    manifest_path = manifest_path.resolve(strict=False)
    if not manifest_path.is_relative_to(workspace):
        raise ValueError("manifest path must stay inside the workspace")
    checks: list[dict[str, Any]] = []
    risk = _risk(review_text, risk_override)
    classification = _load_source_classification(workspace)
    if classification.errors:
        _check(checks, "source-classification", False, "; ".join(classification.errors))
    elif classification.present:
        _check(checks, "source-classification", True, f"{SOURCE_CLASSIFICATION_PATH} declares {len(classification.rules)} source kinds")
    else:
        _check(checks, "source-classification", True, f"{SOURCE_CLASSIFICATION_PATH} absent; built-in classifier only")
    try:
        classification_report = source_classification_check_report(workspace, [], SOURCE_CLASSIFICATION_PATH)
        blocking = classification_report["summary"]["blocking"]
        advisory = classification_report["summary"]["advisory"]
        _check(
            checks,
            "source-classification-check",
            blocking == 0,
            f"blocking={blocking} advisory={advisory} candidates={len(classification_report.get('uncovered_candidates', []))}",
        )
    except SourceClassificationError as exc:
        _check(checks, "source-classification-check", False, str(exc))
    manifest_state = {"path": os.path.relpath(manifest_path, workspace), "valid": False, "normalized": False, "scope_ok": False}
    manifest: dict[str, Any] | None = None
    try:
        loaded = dm.load_json(manifest_path)
        errors = dm.validate_manifest(loaded)
        identity_ok = isinstance(loaded, dict) and loaded.get("card", {}).get("id") == card["id"]
        if errors or not identity_ok:
            _check(checks, "manifest", False, "; ".join(errors) or "manifest card id does not match target card")
        else:
            manifest = loaded
            manifest_state["valid"] = True
            _check(checks, "manifest", True, "delivery manifest is schema-valid")
    except dm.ManifestError as exc:
        _check(checks, "manifest", False, str(exc))

    board_ok = "/3.inprogress/" in f"/{card['path']}" and card["status"] == "3.inprogress"
    _check(checks, "board", board_ok, f"card path={card['path']} status={card['status'] or 'missing'}")
    actual: dict[str, dict[str, Any]] = {}
    if manifest is not None:
        if normalize:
            manifest_state["normalized"] = _normalize_manifest(manifest, card, card_text, workspace)
            if manifest_state["normalized"]:
                dm.write_json(manifest_path, manifest)
            normalized_errors = dm.validate_manifest(manifest)
            if normalized_errors:
                _check(checks, "manifest-normalization", False, "; ".join(normalized_errors))
        scope = dm.compare_scope(manifest, workspace, "working-tree")
        manifest_state["scope_ok"] = scope["ok"]
        _check(checks, "scope", scope["ok"], json.dumps(scope, ensure_ascii=True, sort_keys=True))
        archived = bool(manifest.get("changes")) and all(item.get("state") == "archived" for item in manifest["changes"])
        _check(checks, "archive", archived, "all card-owned changes are archived" if archived else "card-owned changes are missing or not archived")
        actual = dm.scope_actual_entries(workspace, "working-tree", dm.scope_excluded_paths(manifest))
    else:
        _check(checks, "scope", False, "scope cannot be checked without a valid manifest")
        _check(checks, "archive", False, "archive state cannot be checked without a valid manifest")
    execution_target, target_ok, target_detail = _execution_target_state(workspace, manifest)
    _check(checks, "execution-target", target_ok, target_detail)
    extension_surfaces = manifest.get("extension_surfaces", []) if isinstance(manifest, dict) else []
    coverage_state, coverage_ok, coverage_detail = coverage_preflight_check(
        workspace=workspace,
        card_text=card_text,
        card=card,
        manifest=manifest,
        actual=actual,
        reviewed_tree={key: fingerprint[key] for key in ("tree_sha", "diff_fingerprint")},
        surface_kinds={item["kind"] for item in extension_surfaces if isinstance(item, dict) and isinstance(item.get("kind"), str)},
    )
    coverage_payload = dict(coverage_state)
    coverage_payload["detail"] = coverage_detail
    _check(checks, "coverage", coverage_ok, json.dumps(coverage_payload, ensure_ascii=True, sort_keys=True))

    complexity = _production_complexity(workspace, actual, classification) if actual else {"added_production_loc": 0, "source_breakdown": []}
    added_loc = complexity["added_production_loc"]
    new_protocol = _boolean(_field(review_text, "New authority or wire protocol"), "New authority or wire protocol")
    repeated = _boolean(_field(review_text, "Repeated defect class"), "Repeated defect class")
    live = _boolean(_field(review_text, "Live admission"), "Live admission")
    final = _boolean(_field(review_text, "Final certification"), "Final certification")
    critical_boundary = _boolean(_field(review_text, "Credential or mutation authority"), "Credential or mutation authority")
    milestone = _boolean(_field(review_text, "Milestone audit"), "Milestone audit")
    risk.update({"milestone_audit": milestone, "critical_boundary": critical_boundary, "live_admission": live, "final_certification": final})
    authorization = _published_investigation_authorization(review_text, card_text, card, workspace)
    authorized = authorization["status"] == "valid"
    authorization_values = authorization.get("authorization", {})
    loc_limit = authorization_values.get("production_loc_ceiling", DEFAULT_PRODUCTION_LOC_LIMIT) if authorized else DEFAULT_PRODUCTION_LOC_LIMIT
    protocol_allowed = bool(authorization_values.get("allow_new_authority_or_wire_protocol")) if authorized else False
    complexity_reasons = []
    if authorization["status"] == "invalid":
        complexity_reasons.append(f"published investigation authorization is invalid: {authorization['detail']}")
    if added_loc > loc_limit:
        complexity_reasons.append(f"added production LOC {added_loc} exceeds {loc_limit}")
    if new_protocol and not protocol_allowed:
        complexity_reasons.append("new authority or wire protocol requires published investigation authorization")
    if repeated and not authorized:
        complexity_reasons.append("repeated defect class requires simplification")
    if risk["tier"] == "deterministic" and added_loc:
        _check(checks, "risk-tier", False, "deterministic risk cannot add production code")
    elif (critical_boundary or live or final) and risk["tier"] != "critical":
        _check(checks, "risk-tier", False, "credential/mutation, live admission and final certification require critical risk")
    else:
        _check(checks, "risk-tier", True, f"risk route={risk['tier']} effort={risk['reasoning_effort']}")

    openspec = workspace / "bin" / "openspec"
    if openspec.is_file() and os.access(openspec, os.X_OK):
        command = [str(openspec), "validate", "--all", "--strict"]
        ok, detail = _timed(timings, "openspec-validation", lambda: _run(workspace, command))
        _check(checks, "openspec", ok, detail, command)
    else:
        checks.append({"id": "openspec", "status": "skipped", "detail": "strict OpenSpec helper is not available"})
    scoped_paths = sorted(actual)
    base_tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" if fingerprint["head_commit"] == "unborn" else fingerprint["head_commit"]
    command = ["git", "diff-tree", "--check", "--no-commit-id", base_tree, fingerprint["tree_sha"], "--", *scoped_paths]
    ok, detail = _timed(timings, "scoped-whitespace-check", lambda: _run(workspace, command))
    _check(checks, "diff", ok, detail, command)
    scanner = workspace / "scripts" / "public-surface-scan.py"
    if scanner.is_file():
        command = [sys.executable, str(scanner)]
        ok, detail = _timed(timings, "public-surface-scan", lambda: _run(workspace, command))
        _check(checks, "public-surface", ok, detail, command)
    else:
        checks.append({"id": "public-surface", "status": "skipped", "detail": "public-surface scanner is not available"})

    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / f"{card['id']}.json"
    fresh_go, freshness_detail = _previous_verdict(verdict_path, fingerprint, validate_verdict)
    _check(checks, "freshness", True, freshness_detail)
    blocked = any(item["status"] == "fail" for item in checks)
    stop = bool(complexity_reasons)
    if blocked:
        outcome, llm_required, reason = "blocked", False, "deterministic process checks failed"
    elif stop:
        outcome, llm_required, reason = "investigation-required", False, "complexity guard requires investigation/simplification"
    elif fresh_go:
        outcome, llm_required, reason = "already-reviewed", False, "a fresh GO already binds this payload"
    elif risk["review_mode"] == "machine-only":
        outcome, llm_required, reason = "machine-reviewed", False, "deterministic preflight is the required payload review"
    else:
        outcome, llm_required, reason = "ready-for-llm-review", True, f"semantic {risk['tier']} payload review is required"
    result = {
        "schema": SCHEMA_ID, "checked_at": dm.utc_now(), "ok": not blocked and not stop, "outcome": outcome,
        "workspace": {"root": str(workspace), **{key: fingerprint[key] for key in ("head_commit", "tree_sha", "diff_fingerprint")}},
        "card": {"id": card["id"], "path": card["path"], "status": card["status"]},
        "manifest": manifest_state, "execution_target": execution_target, "risk": risk,
        "complexity_guard": {
            "added_production_loc": added_loc, "limit": loc_limit, "new_authority_or_wire_protocol": new_protocol,
            "repeated_defect_class": repeated, "published_investigation_authorization": authorization,
            "stop_required": stop, "reasons": complexity_reasons,
            "source_breakdown": complexity["source_breakdown"],
        },
        "checks": checks, "llm_review": {"required": llm_required, "reason": reason},
    }
    if diagnostics:
        result["diagnostics"] = {
            "fingerprint": fingerprint.get("diagnostics", {}),
            "preflight_timings": timings,
        }
    schema_errors = validate_with_schema(result, SCHEMA_FILE)
    if schema_errors:
        raise RuntimeError("invalid review preflight result: " + "; ".join(schema_errors))
    if output:
        target = output if output.is_absolute() else workspace / output
        dm.write_json(target, result)
    return (0 if result["ok"] else 1), result
