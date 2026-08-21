from __future__ import annotations

import argparse, fnmatch, hashlib, json, os, subprocess, sys, tempfile  # noqa: E401
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
import yaml
from changerail_contract_schema import validate_with_schema
ROOT = Path(__file__).resolve().parents[1]
BUILTIN_PROFILE_DIR = ROOT / "profiles" / "source-classification"
CLASSIFICATION_REL = ".changerail/source-classification.yaml"
PROFILE_SCHEMA, CLASSIFICATION_SCHEMA, CHECK_SCHEMA = ("changerail-source-classification-profile.schema.json", "changerail-source-classification.schema.json", "changerail-source-classification-check.schema.json")
MAX_EXAMPLES = 5
class SourceClassificationError(RuntimeError): pass  # noqa: E701
def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def checksum_profile(profile: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(profile).encode("utf-8")).hexdigest()
def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SourceClassificationError(f"{path.name}: invalid YAML: {exc}") from exc
    except OSError as exc:
        raise SourceClassificationError(f"{path.name}: cannot read: {exc}") from exc
def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
def safe_rel(value: str, label: str) -> str:
    path = PurePosixPath(value.strip().rstrip("/"))
    raw = path.as_posix()
    if (
        not value
        or value != raw
        or raw in {"", "."}
        or "\\" in value
        or value.startswith(("~", "/"))
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise SourceClassificationError(f"{label} must be a normalized repository-relative POSIX path")
    return raw
def run_git(workspace: Path, args: list[str]) -> str:
    result = subprocess.run(["git", "-C", str(workspace), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise SourceClassificationError(detail)
    return result.stdout
def tree_paths(workspace: Path, snapshot: str) -> tuple[str, list[str]]:
    tree = run_git(workspace, ["rev-parse", "--verify", f"{snapshot}^{{tree}}"]).strip()
    paths = [safe_rel(line, "snapshot path") for line in run_git(workspace, ["ls-tree", "-r", "--name-only", tree]).splitlines() if line]
    return tree, sorted(paths)
def glob_match(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or (
        "**/" in pattern and fnmatch.fnmatchcase(path, pattern.replace("**/", ""))
    )
def validate_profile(profile: Any, source_label: str) -> dict[str, Any]:
    errors = validate_with_schema(profile, PROFILE_SCHEMA)
    if errors:
        raise SourceClassificationError(f"{source_label}: " + "; ".join(errors))
    if not isinstance(profile, dict):
        raise SourceClassificationError(f"{source_label}: profile must be an object")
    seen_sources: set[str] = set()
    for item in profile["classification"]["source_kinds"]:
        source_id = item["id"]
        if source_id in seen_sources:
            raise SourceClassificationError(f"{source_label}: duplicate source kind {source_id}")
        seen_sources.add(source_id)
        suffixes = {suffix.lower() for suffix in item["suffixes"]}
        if len(suffixes) != len(item["suffixes"]):
            raise SourceClassificationError(f"{source_label}: duplicate case-insensitive suffix in {source_id}")
        if item["measure"] == "xml-structure" and ".xml" not in suffixes:
            raise SourceClassificationError(f"{source_label}: xml-structure source kind {source_id} requires .xml")
    seen_signals: set[str] = set()
    for signal in profile["detection"]["signals"]:
        signal_id = signal["id"]
        if signal_id in seen_signals:
            raise SourceClassificationError(f"{source_label}: duplicate signal {signal_id}")
        seen_signals.add(signal_id)
    return profile
def load_profile(path: Path, source_kind: str) -> dict[str, Any]:
    profile = validate_profile(load_yaml(path), path.name)
    return {"profile": profile, "checksum": checksum_profile(profile), "source": {"kind": source_kind, "ref": path.name}}
def load_profiles(profile_files: list[str]) -> list[dict[str, Any]]:
    records = [load_profile(path, "built-in") for path in sorted(BUILTIN_PROFILE_DIR.glob("*.yaml"))]
    for raw in profile_files:
        records.append(load_profile(Path(raw), "local-integration"))
    by_key: dict[str, str] = {}
    for record in records:
        profile = record["profile"]
        key = f"{profile['id']}@{profile['version']}"
        checksum = record["checksum"]
        if key in by_key and by_key[key] != checksum:
            raise SourceClassificationError(f"profile {key} has conflicting checksums")
        by_key[key] = checksum
    return records
def normalize_kind(item: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": item["id"],
        "suffixes": sorted({suffix.lower() for suffix in item["suffixes"]}),
        "production_roots": sorted({safe_rel(root, f"{item['id']}.production_roots") for root in item["production_roots"]}),
        "measure": item["measure"],
    }
    if item.get("description"):
        result["description"] = item["description"]
    return result
def path_under(path: str, root: str) -> bool:
    parts = PurePosixPath(path).parts
    root_parts = PurePosixPath(root).parts
    return parts[: len(root_parts)] == root_parts
def roots_overlap(left: str, right: str) -> bool:
    return path_under(left, right) or path_under(right, left)
def select_records(records: list[dict[str, Any]], selectors: list[str]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    by_key = {f"{record['profile']['id']}@{record['profile']['version']}": record for record in records}
    for selector in dict.fromkeys(selectors):
        if selector not in by_key:
            raise SourceClassificationError(f"unknown profile selection {selector}")
        selected.append(by_key[selector])
    if not selected:
        raise SourceClassificationError("at least one --profile id@version selection is required")
    return selected
def merge_records(records: list[dict[str, Any]], override_paths: list[str] | None = None) -> dict[str, Any]:
    by_source: dict[str, dict[str, Any]] = {}
    non_production: set[str] = set()
    provenance: list[dict[str, Any]] = []
    for record in records:
        profile = record["profile"]
        provenance_item = {
            "id": profile["id"],
            "version": profile["version"],
            "checksum": record["checksum"],
            "source_kind": record["source"]["kind"],
        }
        if override_paths:
            provenance_item["declared_override_paths"] = sorted(set(override_paths))
        provenance.append(provenance_item)
        for root in profile["classification"].get("non_production_roots", []):
            non_production.add(safe_rel(root, "non_production_roots"))
        for source in profile["classification"]["source_kinds"]:
            normalized = normalize_kind(source)
            existing = by_source.get(normalized["id"])
            if existing == normalized:
                continue
            if existing is not None:
                raise SourceClassificationError(f"source kind {normalized['id']} has conflicting definitions")
            for other in by_source.values():
                if not (set(other["suffixes"]) & set(normalized["suffixes"])):
                    continue
                if other["measure"] == normalized["measure"]:
                    continue
                if any(roots_overlap(a, b) for a in other["production_roots"] for b in normalized["production_roots"]):
                    raise SourceClassificationError(f"measurement conflict between {other['id']} and {normalized['id']}")
            by_source[normalized["id"]] = normalized
    return {
        "schema": "changerail.source-classification.v1",
        "profile_provenance": provenance,
        "source_kinds": [by_source[key] for key in sorted(by_source)],
        "non_production_roots": sorted(non_production),
    }
def detect_candidates(records: list[dict[str, Any]], paths: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for record in records:
        profile = record["profile"]
        total = sum(signal["weight"] for signal in profile["detection"]["signals"])
        matched_weight = 0
        matched_signals = []
        required_missing = False
        for signal in profile["detection"]["signals"]:
            matches = [path for path in paths if glob_match(path, signal["path_glob"])]
            if matches:
                matched_weight += signal["weight"]
                matched_signals.append(
                    {
                        "id": signal["id"],
                        "path_glob": signal["path_glob"],
                        "weight": signal["weight"],
                        "matched_path_count": len(matches),
                        "example_paths": matches[:MAX_EXAMPLES],
                    }
                )
            elif signal.get("required"):
                required_missing = True
        if required_missing or matched_weight == 0:
            continue
        score = int(round((matched_weight / total) * 100))
        confidence = "high" if score >= 75 else "medium" if score >= 40 else "low"
        candidates.append(
            {
                "id": profile["id"],
                "version": profile["version"],
                "checksum": record["checksum"],
                "source": record["source"],
                "score": score,
                "confidence": confidence,
                "matched_signals": matched_signals,
            }
        )
    return sorted(candidates, key=lambda item: (-item["score"], item["id"], item["version"]))
def materialize_plan(workspace: Path, target_rel: str, classification: dict[str, Any]) -> dict[str, Any]:
    target = workspace / safe_rel(target_rel, "target")
    if not target.exists():
        return {"status": "preview", "target": target_rel, "action": "create", "classification": classification}
    current_text = target.read_text(encoding="utf-8")
    current = yaml.safe_load(current_text)
    if current == classification:
        return {"status": "unchanged", "target": target_rel, "action": "none", "classification": classification}
    return {
        "status": "migration-required",
        "target": target_rel,
        "action": "refuse-overwrite",
        "diff": diff_classification(classification, current if isinstance(current, dict) else {}),
    }
def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        tmp = Path(handle.name)
    os.replace(tmp, path)
def load_classification(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return None, [f"cannot parse {CLASSIFICATION_REL}: {exc}"]
    errors = validate_with_schema(data, CLASSIFICATION_SCHEMA)
    if errors:
        return None, [f"schema: {error}" for error in errors]
    return data, []
def diff_classification(expected: dict[str, Any], actual: dict[str, Any]) -> list[dict[str, str]]:
    diffs: list[dict[str, str]] = []
    expected_kinds = {item["id"]: item for item in expected.get("source_kinds", []) if isinstance(item, dict)}
    actual_kinds = {item["id"]: item for item in actual.get("source_kinds", []) if isinstance(item, dict)}
    for source_id in sorted(set(expected_kinds) | set(actual_kinds)):
        if source_id not in expected_kinds or source_id not in actual_kinds:
            diffs.append({"path": f"source_kinds.{source_id}.production_roots", "kind": "source-kind-mismatch"})
            continue
        for field in ("suffixes", "production_roots", "measure", "description"):
            if expected_kinds[source_id].get(field) != actual_kinds[source_id].get(field):
                diffs.append({"path": f"source_kinds.{source_id}.{field}", "kind": "value-mismatch"})
    if expected.get("non_production_roots", []) != actual.get("non_production_roots", []):
        diffs.append({"path": "non_production_roots", "kind": "value-mismatch"})
    return diffs
def check_report(workspace: Path, profile_files: list[str], target_rel: str, snapshot: str = "HEAD") -> dict[str, Any]:
    records = load_profiles(profile_files)
    diagnostics: list[dict[str, str]] = []
    try:
        tree, paths = tree_paths(workspace, snapshot)
    except SourceClassificationError as exc:
        tree, paths = "unavailable", []
        diagnostics = [{"severity": "advisory", "code": "snapshot-unavailable", "message": str(exc)}]
    target = workspace / safe_rel(target_rel, "target")
    classification, errors = load_classification(target)
    profiles: list[dict[str, str]] = []
    baseline_records: list[dict[str, Any]] = []
    if errors:
        diagnostics.extend({"severity": "blocking", "code": "invalid-classification", "message": error} for error in errors)
    by_key = {f"{record['profile']['id']}@{record['profile']['version']}": record for record in records}
    selected_keys: set[str] = set()
    declared_overrides: set[str] = set()
    if classification and classification.get("profile_provenance"):
        for item in classification["profile_provenance"]:
            key = f"{item['id']}@{item['version']}"
            selected_keys.add(key)
            declared_overrides.update(item.get("declared_override_paths", []))
            record = by_key.get(key)
            if record is None and item["source_kind"] == "local-integration":
                state = "unavailable"
                diagnostics.append({"severity": "advisory", "code": "local-profile-unavailable", "message": f"{key} baseline not supplied"})
            elif record is None:
                state = "missing"
                diagnostics.append({"severity": "blocking", "code": "profile-missing", "message": f"{key} built-in profile missing"})
            elif record["checksum"] != item["checksum"]:
                state = "checksum-conflict"
                diagnostics.append({"severity": "blocking", "code": "profile-checksum-conflict", "message": f"{key} checksum changed"})
            else:
                state = "matched"
                baseline_records.append(record)
            profiles.append(
                {
                    "id": item["id"],
                    "version": item["version"],
                    "checksum": item["checksum"],
                    "source_kind": item["source_kind"],
                    "state": state,
                }
            )
        if baseline_records:
            baseline = merge_records(baseline_records)
            for diff in diff_classification(baseline, classification):
                if diff["path"] not in declared_overrides:
                    diagnostics.append(
                        {"severity": "blocking", "code": "confirmed-profile-drift", "message": f"undeclared drift at {diff['path']}"}
                    )
    covered, excluded = coverage_counts(classification, paths) if classification else (0, 0)
    candidates = [
        {
            "id": item["id"],
            "version": item["version"],
            "confidence": item["confidence"],
            "score": item["score"],
            "matched_signal_count": len(item["matched_signals"]),
            "example_paths": sorted({path for signal in item["matched_signals"] for path in signal["example_paths"]})[:MAX_EXAMPLES],
        }
        for item in detect_candidates(records, paths)
        if f"{item['id']}@{item['version']}" not in selected_keys
    ]
    blocking = sum(1 for item in diagnostics if item["severity"] == "blocking")
    advisory = sum(1 for item in diagnostics if item["severity"] == "advisory") + len(candidates)
    report = {
        "schema": "changerail.source-classification-check.v1",
        "checked_at": utc_now(),
        "target": {"path": target_rel, "snapshot": tree},
        "classification": {
            "present": target.is_file(),
            "valid": bool(classification) and not errors,
            "provenance": "available" if classification and classification.get("profile_provenance") else "unavailable",
        },
        "profiles": profiles,
        "effective_rules": {
            "source_kind_count": len(classification.get("source_kinds", [])) if classification else 0,
            "non_production_root_count": len(classification.get("non_production_roots", [])) if classification else 0,
            "covered_path_count": covered,
            "excluded_path_count": excluded,
            "source_kinds": classification.get("source_kinds", []) if classification else [],
            "non_production_roots": classification.get("non_production_roots", []) if classification else [],
            "declared_override_paths": sorted(declared_overrides),
        },
        "uncovered_candidates": candidates,
        "diagnostics": diagnostics,
        "summary": {"status": "fail" if blocking else "pass", "blocking": blocking, "advisory": advisory},
    }
    schema_errors = validate_with_schema(report, CHECK_SCHEMA)
    if schema_errors:
        raise SourceClassificationError("invalid check report: " + "; ".join(schema_errors))
    return report
def coverage_counts(classification: dict[str, Any], paths: list[str]) -> tuple[int, int]:
    covered = excluded = 0
    non_production = tuple(classification.get("non_production_roots", []))
    for path in paths:
        is_excluded = any(path_under(path, root) for root in non_production)
        for rule in classification.get("source_kinds", []):
            if not path.endswith(tuple(rule["suffixes"])):
                continue
            if not any(path_under(path, root) for root in rule["production_roots"]):
                continue
            if is_excluded:
                excluded += 1
            else:
                covered += 1
    return covered, excluded
def output(payload: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if as_json else payload.get("summary") or payload.get("status") or payload.get("outcome") or "ok")
def cmd_detect(args: argparse.Namespace) -> int:
    records = load_profiles(args.profile_file)
    tree, paths = tree_paths(Path(args.workspace), args.snapshot)
    candidates = detect_candidates(records, paths)
    top_score = candidates[0]["score"] if candidates else 0
    ambiguities = [{"id": item["id"], "version": item["version"], "score": item["score"]} for item in candidates if item["score"] == top_score]
    payload = {
        "ok": True,
        "snapshot": {"input": args.snapshot, "tree": tree},
        "candidates": candidates,
        "ambiguities": ambiguities if len(ambiguities) > 1 else [],
        "recommended_action": "review-high-confidence-candidate" if candidates and candidates[0]["confidence"] == "high" else "review-candidates" if candidates else "none",
        "writes": [],
    }
    output(payload, args.json)
    return 0
def cmd_materialize(args: argparse.Namespace) -> int:
    records = load_profiles(args.profile_file)
    selected = select_records(records, args.profile)
    classification = merge_records(selected, args.override_path)
    if errors := validate_with_schema(classification, CLASSIFICATION_SCHEMA):
        raise SourceClassificationError("invalid materialized classification: " + "; ".join(errors))
    plan = materialize_plan(Path(args.workspace), args.target, classification)
    if args.write and plan["status"] == "preview":
        atomic_write(Path(args.workspace) / args.target, dump_yaml(classification))
        plan.update({"status": "created", "action": "write"})
    elif args.write and plan["status"] == "migration-required":
        output(plan, args.json)
        return 1
    output(plan, args.json)
    return 1 if plan["status"] == "migration-required" else 0
def cmd_check(args: argparse.Namespace) -> int:
    report = check_report(Path(args.workspace), args.profile_file, args.target, args.snapshot)
    output(report, args.json)
    return 1 if report["summary"]["blocking"] else 0
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect, materialize and check ChangeRail source classification profiles.")
    parser.add_argument("--workspace", default=".", help="Repository root, default current directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    sub = parser.add_subparsers(dest="command", required=True)
    detect = sub.add_parser("detect")
    detect.add_argument("--snapshot", default="HEAD")
    detect.set_defaults(func=cmd_detect)
    materialize = sub.add_parser("materialize")
    materialize.add_argument("--profile", action="append", default=[], help="Exact id@version selection.")
    materialize.add_argument("--target", default=CLASSIFICATION_REL)
    materialize.add_argument("--override-path", action="append", default=[])
    materialize.add_argument("--write", action="store_true")
    materialize.set_defaults(func=cmd_materialize)
    check = sub.add_parser("check")
    check.add_argument("--snapshot", default="HEAD")
    check.add_argument("--target", default=CLASSIFICATION_REL)
    check.set_defaults(func=cmd_check)
    for command in (detect, materialize, check):
        command.add_argument("--profile-file", action="append", default=[])
    return parser
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SourceClassificationError as exc:
        payload = {"ok": False, "error": {"message": str(exc)}}
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True) if getattr(args, "json", False) else str(exc), file=sys.stderr)
        return 2
if __name__ == "__main__":
    raise SystemExit(main())
