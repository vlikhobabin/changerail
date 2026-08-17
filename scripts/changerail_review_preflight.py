"""Deterministic gate before ChangeRail payload review."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from changerail_contract_schema import validate_with_schema
import changerail_delivery_manifest as dm

SCHEMA_ID = "changerail.review-preflight-result.v1"
SCHEMA_FILE = "changerail-review-preflight-result.schema.json"
PRODUCTION_SUFFIXES = {".c", ".cc", ".cpp", ".cs", ".go", ".h", ".hpp", ".java", ".js", ".jsx", ".kt", ".php", ".py", ".rb", ".rs", ".sh", ".ts", ".tsx"}
NON_PRODUCTION_PARTS = {"docs", "examples", "fixtures", "openspec", "schemas", "templates", "test", "tests"}
DEFAULT_PRODUCTION_LOC_LIMIT = 300
MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT = 500
AUTHORIZATION_FIELD = "Published investigation authorization"
AUTHORIZATION_SOURCE_FIELD = "Investigation authorization"
CARD_ID_RE = r"[a-z0-9][a-z0-9-]*"
BOARD_CARD_REFERENCE_RE = re.compile(rf"^openspec/board/[1-5]\.(?:backlog|todo|inprogress|done|canceled)/({CARD_ID_RE})\.md$")
CARD_FILENAME_RE = re.compile(rf"^({CARD_ID_RE})\.md$")
BARE_CARD_ID_RE = re.compile(rf"^{CARD_ID_RE}$")


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(name)}:\s*`?([^`\n]+)`?\s*$", text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip().lower() if match else None


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


def _production_path(workspace: Path, path: str) -> bool:
    candidate = Path(path)
    lowered = {part.lower() for part in candidate.parts}
    name = candidate.name.lower()
    executable = candidate.parts[:1] == ("bin",) and not candidate.suffix and (workspace / candidate).is_file() and bool((workspace / candidate).stat().st_mode & 0o111)
    return ((candidate.suffix.lower() in PRODUCTION_SUFFIXES or executable) and not name.endswith("_test.go") and not (lowered & NON_PRODUCTION_PARTS)
            and not name.startswith(("test_", "smoke-", "smoke_")))


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


def _added_loc(workspace: Path, entries: dict[str, dict[str, Any]]) -> int:
    total = 0
    tracked = [path for path in entries if _production_path(workspace, path)]
    if tracked:
        result = subprocess.run(
            ["git", "-C", str(workspace), "diff", "--numstat", "HEAD", "--", *tracked],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git diff --numstat failed")
        for line in result.stdout.splitlines():
            added = line.split("\t", 1)[0]
            if added.isdigit():
                total += int(added)
    for path, entry in entries.items():
        if not _production_path(workspace, path) or entry.get("operation") != "add":
            continue
        absolute = workspace / path
        if absolute.is_file():
            payload = absolute.read_bytes()
            if b"\0" not in payload:
                total += len(payload.splitlines())
    return total


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


def run_preflight(*, card_path: Path, workspace: Path, manifest_path: Path | None, normalize: bool,
                  risk_override: str | None, output: Path | None, fingerprint_fn: Callable[[Path], dict[str, str]],
                  validate_verdict: Callable[[Any], list[str]]) -> tuple[int, dict[str, Any]]:
    workspace = workspace.resolve(strict=False)
    card_text, card = dm.read_card(card_path, workspace)
    review_text = dm.section_body(card_text, "Review")
    fingerprint = fingerprint_fn(workspace)
    manifest_path = manifest_path or dm.default_manifest_path(workspace, card)
    if not manifest_path.is_absolute():
        manifest_path = workspace / manifest_path
    manifest_path = manifest_path.resolve(strict=False)
    if not manifest_path.is_relative_to(workspace):
        raise ValueError("manifest path must stay inside the workspace")
    checks: list[dict[str, Any]] = []
    risk = _risk(review_text, risk_override)
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

    added_loc = _added_loc(workspace, actual) if actual else 0
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
    if repeated:
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
        ok, detail = _run(workspace, command)
        _check(checks, "openspec", ok, detail, command)
    else:
        checks.append({"id": "openspec", "status": "skipped", "detail": "strict OpenSpec helper is not available"})
    scoped_paths = sorted(actual)
    base_tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" if fingerprint["head_commit"] == "unborn" else fingerprint["head_commit"]
    command = ["git", "diff-tree", "--check", "--no-commit-id", base_tree, fingerprint["tree_sha"], "--", *scoped_paths]
    ok, detail = _run(workspace, command)
    _check(checks, "diff", ok, detail, command)
    scanner = workspace / "scripts" / "public-surface-scan.py"
    if scanner.is_file():
        command = [sys.executable, str(scanner)]
        ok, detail = _run(workspace, command)
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
        "manifest": manifest_state, "risk": risk,
        "complexity_guard": {
            "added_production_loc": added_loc, "limit": loc_limit, "new_authority_or_wire_protocol": new_protocol,
            "repeated_defect_class": repeated, "published_investigation_authorization": authorization,
            "stop_required": stop, "reasons": complexity_reasons,
        },
        "checks": checks, "llm_review": {"required": llm_required, "reason": reason},
    }
    schema_errors = validate_with_schema(result, SCHEMA_FILE)
    if schema_errors:
        raise RuntimeError("invalid review preflight result: " + "; ".join(schema_errors))
    if output:
        target = output if output.is_absolute() else workspace / output
        dm.write_json(target, result)
    return (0 if result["ok"] else 1), result
