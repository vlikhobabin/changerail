"""Verification coverage map contracts and canonical fingerprints."""

from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from changerail_contract_schema import validate_with_schema

DEFAULT_COVERAGE_MAP_PATH = ".changerail/verification-coverage.yaml"
COVERAGE_MAP_SCHEMA_FILE = "changerail-verification-coverage.schema.json"
COVERAGE_PLAN_SCHEMA_FILE = "changerail-verification-coverage-plan.schema.json"
COVERAGE_LEDGER_SCHEMA_FILE = "changerail-verification-coverage-ledger.schema.json"
EVIDENCE_INDEX_SCHEMA_FILE = "changerail-evidence-index.schema.json"

def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False

def _git_toplevel(workspace: Path) -> Path | None:
    result = subprocess.run(["git", "-C", str(workspace), "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
    return Path(result.stdout.strip()).resolve(strict=False) if result.returncode == 0 else None

def _git_tracked(workspace: Path, rel_path: str) -> bool:
    return subprocess.run(["git", "-C", str(workspace), "ls-files", "--error-unmatch", "--", rel_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0

def _safe_rel_path(value: str) -> str | None:
    raw = value.strip().rstrip("/")
    if not raw or raw in {".", ".."} or "\\" in raw or raw.startswith(("~", "/")):
        return None
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.as_posix() if path.as_posix() == raw else None

def _sorted_copy(value: Any) -> Any:
    if isinstance(value, list):
        copied_items = [_sorted_copy(item) for item in value]
        if all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in copied_items):
            return sorted(copied_items, key=lambda item: item["id"])
        return copied_items
    if isinstance(value, dict):
        copied = {key: _sorted_copy(item) for key, item in sorted(value.items())}
        applies_to = copied.get("applies_to")
        for key in ("operation_kinds", "path_globs", "surface_kinds"):
            if isinstance(applies_to, dict) and isinstance(applies_to.get(key), list):
                applies_to[key] = sorted(applies_to[key])
        evidence = copied.get("required_evidence")
        if isinstance(evidence, list):
            copied["required_evidence"] = sorted(
                evidence,
                key=lambda item: (item.get("kind") if isinstance(item, dict) else "", item.get("oracle_ref") if isinstance(item, dict) else ""),
            )
        return copied
    return copy.deepcopy(value)

def fingerprint_coverage_map(payload: dict[str, Any]) -> str:
    return fingerprint_payload(_sorted_copy(payload))

def fingerprint_payload(payload: Any) -> str:
    canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def validate_coverage_map(payload: Any) -> list[str]:
    errors = validate_with_schema(payload, COVERAGE_MAP_SCHEMA_FILE)
    if errors or not isinstance(payload, dict):
        return errors

    entries = payload.get("entries", [])
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries if isinstance(entries, list) else []):
        if not isinstance(entry, dict):
            continue
        coverage_id = entry.get("id")
        if isinstance(coverage_id, str):
            if coverage_id in seen_ids:
                errors.append(f"duplicate coverage id: {coverage_id}")
            seen_ids.add(coverage_id)
        oracle = entry.get("oracle")
        oracle_ref = oracle.get("ref") if isinstance(oracle, dict) else None
        evidence = entry.get("required_evidence", [])
        for evidence_index, evidence_entry in enumerate(evidence if isinstance(evidence, list) else []):
            if not isinstance(evidence_entry, dict):
                continue
            if evidence_entry.get("oracle_ref") != oracle_ref:
                errors.append(
                    f"entries[{index}].required_evidence[{evidence_index}].oracle_ref "
                    "must reference the entry oracle ref"
                )
    return errors

def _duplicate_field_errors(items: Any, field: str, label: str) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for item in items if isinstance(items, list) else []:
        value = item.get(field) if isinstance(item, dict) else None
        if not isinstance(value, str):
            continue
        if value in seen:
            errors.append(f"duplicate {label}: {value}")
        seen.add(value)
    return errors

def validate_coverage_plan(payload: Any) -> list[str]:
    errors = validate_with_schema(payload, COVERAGE_PLAN_SCHEMA_FILE)
    if errors or not isinstance(payload, dict):
        return errors
    card = payload.get("card") if isinstance(payload.get("card"), dict) else {}
    errors.extend(_duplicate_field_errors(payload.get("selected_coverage"), "id", "selected coverage id"))
    errors.extend(_duplicate_field_errors(card.get("acceptance_hashes"), "id", "acceptance hash id"))
    return errors

def validate_coverage_ledger(payload: Any) -> list[str]:
    errors = validate_with_schema(payload, COVERAGE_LEDGER_SCHEMA_FILE)
    if errors or not isinstance(payload, dict):
        return errors
    errors.extend(_duplicate_field_errors(payload.get("entries"), "coverage_id", "ledger coverage id"))
    return errors

def coverage_map_path_from_config(workspace: Path) -> str | None:
    config = workspace / "openspec" / "config.yaml"
    if not config.is_file():
        return None
    try:
        import yaml
        data = yaml.safe_load(config.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    verification = data.get("verification")
    if not isinstance(verification, dict):
        return None
    value = verification.get("coverage_map")
    if not isinstance(value, str) or value.lower() in {"", "null", "none", "~"}:
        return None
    return value

def card_acceptance_hashes(card_text: str) -> list[dict[str, str]]:
    in_acceptance = False
    criteria: list[str] = []
    current: list[str] = []
    for raw in card_text.splitlines():
        stripped = raw.strip().lower()
        if raw.startswith("## "):
            if in_acceptance:
                break
            in_acceptance = stripped in {"## acceptance", "### acceptance"}
            continue
        if raw.startswith("### "):
            if in_acceptance:
                break
            in_acceptance = stripped == "### acceptance"
            continue
        if not in_acceptance:
            continue
        if raw.startswith("- "):
            if current:
                criteria.append(" ".join(current).strip())
            current = [raw[2:].strip()]
        elif current and raw.startswith("  "):
            current.append(raw.strip())
    if current:
        criteria.append(" ".join(current).strip())
    return [{"id": f"a{index}", "hash": "sha256:" + hashlib.sha256(criterion.encode("utf-8")).hexdigest()} for index, criterion in enumerate(criteria, start=1) if criterion]

def manifest_fingerprint(manifest: dict[str, Any]) -> str:
    payload = copy.deepcopy(manifest)
    payload.pop("coverage_summary", None)
    payload.pop("updated_at", None)
    return fingerprint_payload(payload)

def _load_json_file(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except OSError as exc:
        return None, [f"{path} cannot be read: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{path} JSON is invalid: {exc}"]

def _change_plan_path(workspace: Path, slug: str) -> Path | None:
    active = workspace / "openspec" / "changes" / slug / "verification-coverage.json"
    if active.is_file():
        return active
    archive = workspace / "openspec" / "changes" / "archive"
    candidates = sorted(archive.glob(f"*-{slug}/verification-coverage.json")) if archive.is_dir() else []
    return candidates[-1] if candidates else None

def _entry_matches_scope(entry: dict[str, Any], actual: dict[str, dict[str, Any]], surfaces: set[str]) -> bool:
    applies_to = entry.get("applies_to") if isinstance(entry.get("applies_to"), dict) else {}
    globs = applies_to.get("path_globs") if isinstance(applies_to.get("path_globs"), list) else []
    operations = set(applies_to.get("operation_kinds") or []) if isinstance(applies_to.get("operation_kinds"), list) else set()
    surface_kinds = set(applies_to.get("surface_kinds") or []) if isinstance(applies_to.get("surface_kinds"), list) else set()
    if surface_kinds and surface_kinds & surfaces:
        return True
    return any(
        (not globs or any(fnmatch.fnmatchcase(path, pattern) for pattern in globs))
        and (not operations or scope.get("operation", "unknown") in operations)
        for path, scope in actual.items()
    )

def applicable_coverage_ids(
    coverage_map: dict[str, Any],
    actual: dict[str, dict[str, Any]],
    *,
    surfaces: set[str] | None = None,
) -> set[str]:
    active_surfaces = surfaces or set()
    entries = coverage_map.get("entries")
    items = entries if isinstance(entries, list) else []
    return {
        entry["id"]
        for entry in items
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
        and _entry_matches_scope(entry, actual, active_surfaces)
    }

def evidence_ref_status(workspace: Path, ref: dict[str, Any]) -> tuple[bool, str]:
    index_path = ref.get("index_path")
    evidence_id = ref.get("id")
    if not isinstance(index_path, str) or not isinstance(evidence_id, str):
        return False, "evidence ref must include id and index_path"
    if not isinstance(ref.get("kind"), str) or not isinstance(ref.get("oracle_ref"), str):
        return False, "evidence ref must include kind and oracle_ref"
    path = workspace / index_path
    data, errors = _load_json_file(path)
    if errors:
        return False, "; ".join(errors)
    if not isinstance(data, dict):
        return False, f"{index_path} must contain an evidence index object"
    schema_errors = validate_with_schema(data, EVIDENCE_INDEX_SCHEMA_FILE)
    if schema_errors:
        return False, f"{index_path}: " + "; ".join(schema_errors)
    entries = data.get("entries")
    if not isinstance(entries, list):
        return False, f"{index_path} has no evidence entries"
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("id") != evidence_id:
            continue
        if entry.get("status") != "passed":
            return False, f"evidence {evidence_id} status is {entry.get('status')!r}"
        if entry.get("kind") != ref["kind"]:
            return False, f"evidence {evidence_id} kind is {entry.get('kind')!r}, expected {ref['kind']!r}"
        return True, f"evidence {evidence_id} passed"
    return False, f"evidence {evidence_id} not found in {index_path}"

def coverage_preflight_check(
    *,
    workspace: Path,
    card_text: str,
    card: dict[str, Any],
    manifest: dict[str, Any] | None,
    actual: dict[str, dict[str, Any]],
    reviewed_tree: dict[str, str],
    surface_kinds: set[str] | None = None,
) -> tuple[dict[str, Any], bool, str]:
    configured_path = coverage_map_path_from_config(workspace)
    state: dict[str, Any] = {"configured": False}
    if configured_path is None:
        return state, True, "coverage map absent; existing verification floor applies"
    state.update({"configured": True, "map_path": configured_path})
    loaded = load_coverage_map(workspace, rel_path=configured_path, require_tracked=False)
    if loaded.get("errors"):
        return state, False, "; ".join(str(error) for error in loaded["errors"])
    if not loaded.get("present") or not isinstance(loaded.get("map"), dict):
        return state, False, f"configured coverage map is missing: {configured_path}"
    coverage_map = loaded["map"]
    map_fingerprint = loaded["fingerprint"]
    state["map_fingerprint"] = map_fingerprint
    map_entries = {entry["id"]: entry for entry in coverage_map.get("entries", []) if isinstance(entry, dict) and isinstance(entry.get("id"), str)}
    applicable = applicable_coverage_ids(coverage_map, actual, surfaces=surface_kinds)
    state["applicable"] = sorted(applicable)
    if manifest is None:
        return state, False, "coverage cannot be checked without a valid manifest"
    summary = manifest.get("coverage_summary")
    if not isinstance(summary, dict):
        return state, False, "delivery manifest is missing coverage_summary for configured map"
    state["summary"] = summary
    if summary.get("configured") is not True:
        return state, False, "coverage_summary.configured must be true when map is configured"

    acceptance_hashes = card_acceptance_hashes(card_text)
    manifest_fp = manifest_fingerprint(manifest)
    plans: dict[str, dict[str, Any]] = {}
    plan_fingerprints: dict[str, str] = {}
    for change in manifest.get("changes", []) if isinstance(manifest.get("changes"), list) else []:
        if not isinstance(change, dict) or not isinstance(change.get("slug"), str):
            continue
        slug = change["slug"]
        plan_path = _change_plan_path(workspace, slug)
        if plan_path is None:
            return state, False, f"missing verification coverage plan for {slug}"
        plan, errors = _load_json_file(plan_path)
        if errors:
            return state, False, "; ".join(errors)
        plan_errors = validate_coverage_plan(plan)
        if plan_errors:
            return state, False, f"{plan_path.relative_to(workspace).as_posix()}: " + "; ".join(plan_errors)
        if plan.get("map", {}).get("fingerprint") != map_fingerprint:
            return state, False, f"{slug} coverage plan map fingerprint is stale"
        if plan.get("card", {}).get("acceptance_hashes") != acceptance_hashes:
            return state, False, f"{slug} coverage plan card acceptance hashes are stale"
        selected = {item["id"] for item in plan.get("selected_coverage", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}
        missing_from_plan = sorted(applicable - selected)
        if missing_from_plan:
            return state, False, f"{slug} coverage plan omits applicable ids: {', '.join(missing_from_plan)}"
        plans[slug] = plan
        plan_fingerprints[slug] = fingerprint_payload(plan)

    ledgers = summary.get("ledgers")
    if not isinstance(ledgers, list):
        return state, False, "coverage_summary.ledgers must list per-change ledgers"
    ledger_by_change = {
        item.get("change"): item
        for item in ledgers
        if isinstance(item, dict) and isinstance(item.get("change"), str)
    }
    missing_ledgers = sorted(set(plans) - set(ledger_by_change))
    if missing_ledgers:
        return state, False, "coverage_summary missing ledgers for: " + ", ".join(missing_ledgers)

    counts = {"covered": 0, "missing": 0, "invalid": 0, "not_applicable": 0}
    for slug, plan in plans.items():
        ledger_ref = ledger_by_change[slug]
        ledger_path_value = ledger_ref.get("path")
        if not isinstance(ledger_path_value, str):
            return state, False, f"{slug} ledger reference missing path"
        ledger_path = workspace / ledger_path_value
        ledger, errors = _load_json_file(ledger_path)
        if errors:
            return state, False, "; ".join(errors)
        ledger_errors = validate_coverage_ledger(ledger)
        if ledger_errors:
            return state, False, f"{ledger_path_value}: " + "; ".join(ledger_errors)
        if ledger_ref.get("fingerprint") != fingerprint_payload(ledger):
            return state, False, f"{slug} ledger fingerprint does not match coverage_summary"
        if ledger.get("map", {}).get("fingerprint") != map_fingerprint:
            return state, False, f"{slug} ledger map fingerprint is stale"
        if ledger.get("plan", {}).get("fingerprint") != plan_fingerprints[slug]:
            return state, False, f"{slug} ledger plan fingerprint is stale"
        if ledger.get("manifest", {}).get("fingerprint") != manifest_fp:
            return state, False, f"{slug} ledger manifest fingerprint is stale"
        if ledger.get("reviewed_tree") != reviewed_tree:
            return state, False, f"{slug} ledger reviewed-tree fingerprint is stale"
        entries = ledger.get("entries", []) if isinstance(ledger.get("entries"), list) else []
        ledger_ids = {item.get("coverage_id") for item in entries if isinstance(item, dict)}
        missing_entries = sorted(applicable - {item for item in ledger_ids if isinstance(item, str)})
        if missing_entries:
            return state, False, f"{slug} ledger omits applicable ids: {', '.join(missing_entries)}"
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            coverage_id = entry.get("coverage_id")
            map_entry = map_entries.get(coverage_id)
            oracle_ref = map_entry.get("oracle", {}).get("ref") if isinstance(map_entry, dict) else None
            if entry.get("coverage_id") in applicable and entry.get("oracle_ref") != oracle_ref:
                return state, False, f"{slug} coverage {coverage_id} oracle_ref does not match map oracle"
            state_name = entry.get("state")
            if state_name in counts:
                counts[state_name] += 1
            if coverage_id in applicable and state_name != "covered":
                return state, False, f"{slug} applicable coverage {coverage_id} is {state_name}"
            if state_name == "covered":
                refs = entry.get("evidence_refs")
                if not isinstance(refs, list) or not refs:
                    return state, False, f"{slug} covered entry {coverage_id} has no evidence refs"
                matched: set[tuple[str, str]] = set()
                for ref in refs:
                    ok, detail = evidence_ref_status(workspace, ref) if isinstance(ref, dict) else (False, "malformed evidence ref")
                    if not ok:
                        return state, False, f"{slug} evidence check failed: {detail}"
                    matched.add((ref["kind"], ref["oracle_ref"]))
                required_items = map_entry.get("required_evidence", []) if isinstance(map_entry, dict) else []
                required = {(item["kind"], item["oracle_ref"]) for item in required_items if isinstance(item, dict)}
                if missing := sorted(required - matched):
                    return state, False, f"{slug} coverage {coverage_id} missing required evidence {missing}"
    for key, value in counts.items():
        if summary.get(key) != value:
            return state, False, f"coverage_summary.{key}={summary.get(key)!r} does not match ledger count {value}"
    if summary.get("applicable") != len(applicable):
        return state, False, "coverage_summary.applicable does not match current scope"
    return state, True, "coverage map, plans, ledgers and evidence refs are complete"

def load_coverage_map(
    workspace: Path,
    *,
    rel_path: str = DEFAULT_COVERAGE_MAP_PATH,
    require_tracked: bool = False,
) -> dict[str, Any]:
    root = workspace.resolve(strict=False)
    safe_rel = _safe_rel_path(rel_path)
    result: dict[str, Any] = {"present": False, "path": rel_path, "errors": []}
    if safe_rel is None:
        result["present"] = True
        result["errors"] = [f"coverage map path must be repository-relative POSIX path: {rel_path!r}"]
        return result

    path = root / safe_rel
    result["path"] = safe_rel
    if not path.exists() and not path.is_symlink():
        return result

    errors: list[str] = []
    if path.is_symlink():
        errors.append(f"{safe_rel} must be a regular file, not a symlink")
    resolved = path.resolve(strict=False)
    if not _is_relative_to(resolved, root):
        errors.append(f"{safe_rel} resolves outside the workspace")
    if path.exists() and not path.is_file():
        errors.append(f"{safe_rel} must be a regular file")
    if require_tracked and _git_toplevel(root) == root and not _git_tracked(root, safe_rel):
        errors.append(f"{safe_rel} must be tracked by git")

    data: Any = None
    if not errors:
        try:
            import yaml
        except Exception as exc:
            errors.append(f"PyYAML is required to read {safe_rel}: {type(exc).__name__}: {exc}")
        else:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError) as exc:
                errors.append(f"{safe_rel} cannot be parsed: {exc}")

    if data is not None:
        errors.extend(validate_coverage_map(data))

    result["present"] = True
    result["errors"] = errors
    if not errors and isinstance(data, dict):
        result["map"] = data
        result["fingerprint"] = fingerprint_coverage_map(data)
    return result
