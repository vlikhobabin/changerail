#!/usr/bin/env python3
"""Validate ChangeRail review verdicts and compute working-tree freshness fingerprints.

The review verdict (`changerail.review-verdict.v1`) is the machine gate between
`$changerail-do` and `$changerail-pub`: a card publish that is part of the review-gated
flow requires a verdict that is valid, `result: go`, and fresh against the
current working tree. This helper provides:

- `validate <verdict.json>`: schema-shape plus consistency validation
  (blocker findings force `no-go`; `no-go` requires a blocker or a failed
  acceptance criterion; reviewer independence attestation is required), with
  optional `--check-fresh` freshness comparison;
- `fingerprint --workspace <root>`: deterministic sha256 fingerprint over
  `git status --porcelain`, `git diff HEAD` and untracked non-ignored file
  content, shared by the reviewer that embeds it and every consumer that
  re-checks it.

Exit codes follow the shared ChangeRail helper convention: 0 valid, 1 validation
failed, 2 input error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_ID = "changerail.review-verdict.v1"
ACCEPTED_SCHEMA_IDS = (SCHEMA_ID,)
REVIEWER_KINDS = ("codex-exec", "claude-subagent", "external-session", "operator")
RESULTS = ("go", "no-go")
ACCEPTANCE_VERDICTS = ("pass", "fail", "unverifiable", "not-applicable")
SEVERITIES = ("blocker", "major", "minor")
AREAS = ("evidence", "code", "tests", "scope", "docs", "process")
FINDING_ID_RE = re.compile(r"^R[0-9]+$")
FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TOP_LEVEL_KEYS = {
    "schema",
    "reviewed_at",
    "card",
    "workspace",
    "reviewer",
    "result",
    "review_cycle",
    "acceptance",
    "findings",
    "evidence_audit",
    "notes",
}
READ_CHUNK_SIZE = 1024 * 1024


class VerdictError(Exception):
    """Validation or input failure with an explicit exit code."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _require_str(errors: list[str], data: dict[str, Any], field: str, label: str) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{field} must be a non-empty string")
        return None
    return value


def _validate_verdict(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["verdict must be a JSON object"]
    if data.get("schema") not in ACCEPTED_SCHEMA_IDS:
        accepted = "', '".join(ACCEPTED_SCHEMA_IDS)
        errors.append(f"schema must be one of: '{accepted}'")
    unknown = sorted(set(data) - TOP_LEVEL_KEYS)
    if unknown:
        errors.append(f"unknown top-level field(s): {', '.join(unknown)}")
    _require_str(errors, data, "reviewed_at", "verdict")

    card = data.get("card")
    if not isinstance(card, dict):
        errors.append("card must be an object with id and path")
    else:
        _require_str(errors, card, "id", "card")
        _require_str(errors, card, "path", "card")

    workspace = data.get("workspace")
    if not isinstance(workspace, dict):
        errors.append("workspace must be an object with root, head_commit and diff_fingerprint")
    else:
        _require_str(errors, workspace, "root", "workspace")
        _require_str(errors, workspace, "head_commit", "workspace")
        fingerprint = _require_str(errors, workspace, "diff_fingerprint", "workspace")
        if fingerprint is not None and not FINGERPRINT_RE.match(fingerprint):
            errors.append("workspace.diff_fingerprint must match 'sha256:<64 hex digits>'")

    reviewer = data.get("reviewer")
    if not isinstance(reviewer, dict):
        errors.append("reviewer must be an object with kind and independence")
    else:
        if reviewer.get("kind") not in REVIEWER_KINDS:
            errors.append(f"reviewer.kind must be one of: {', '.join(REVIEWER_KINDS)}")
        independence = reviewer.get("independence")
        if not isinstance(independence, dict):
            errors.append("reviewer.independence must be an object")
        else:
            if independence.get("fresh_context") is not True:
                errors.append("reviewer.independence.fresh_context must be true")
            if independence.get("did_not_plan_or_implement") is not True:
                errors.append("reviewer.independence.did_not_plan_or_implement must be true")
            basis = independence.get("basis")
            if not isinstance(basis, str) or not basis.strip():
                errors.append("reviewer.independence.basis must be a non-empty string")

    result = data.get("result")
    if result not in RESULTS:
        errors.append(f"result must be one of: {', '.join(RESULTS)}")

    review_cycle = data.get("review_cycle")
    if not isinstance(review_cycle, int) or isinstance(review_cycle, bool) or review_cycle < 1:
        errors.append("review_cycle must be an integer >= 1")

    has_failed_acceptance = False
    acceptance = data.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        errors.append("acceptance must be a non-empty array of criterion verdicts")
    else:
        for index, entry in enumerate(acceptance):
            label = f"acceptance[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{label} must be an object")
                continue
            _require_str(errors, entry, "criterion", label)
            _require_str(errors, entry, "evidence", label)
            verdict = entry.get("verdict")
            if verdict not in ACCEPTANCE_VERDICTS:
                errors.append(f"{label}.verdict must be one of: {', '.join(ACCEPTANCE_VERDICTS)}")
            elif verdict == "fail":
                has_failed_acceptance = True

    has_blocker = False
    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array (empty when there are none)")
    else:
        seen_ids: set[str] = set()
        for index, entry in enumerate(findings):
            label = f"findings[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{label} must be an object")
                continue
            finding_id = entry.get("id")
            if not isinstance(finding_id, str) or not FINDING_ID_RE.match(finding_id):
                errors.append(f"{label}.id must match 'R<number>'")
            elif finding_id in seen_ids:
                errors.append(f"{label}.id duplicates {finding_id}")
            else:
                seen_ids.add(finding_id)
            severity = entry.get("severity")
            if severity not in SEVERITIES:
                errors.append(f"{label}.severity must be one of: {', '.join(SEVERITIES)}")
            elif severity == "blocker":
                has_blocker = True
            if entry.get("area") not in AREAS:
                errors.append(f"{label}.area must be one of: {', '.join(AREAS)}")
            _require_str(errors, entry, "summary", label)

    audit = data.get("evidence_audit")
    if audit is not None:
        if not isinstance(audit, dict):
            errors.append("evidence_audit must be an object")
        else:
            for field in ("claims_checked", "claims_unbacked"):
                value = audit.get(field)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append(f"evidence_audit.{field} must be an integer >= 0")

    if result == "go" and (has_blocker or has_failed_acceptance):
        errors.append("result 'go' is inconsistent with blocker findings or failed acceptance criteria")
    if result == "no-go" and not (has_blocker or has_failed_acceptance):
        errors.append("result 'no-go' requires at least one blocker finding or one failed acceptance criterion")
    return errors


def _git_output(workspace: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise VerdictError(f"git {' '.join(args)}: {detail}", exit_code=2)
    return result.stdout


def _git_output_bytes(workspace: Path, args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (
            result.stderr.decode("utf-8", errors="replace").strip()
            or result.stdout.decode("utf-8", errors="replace").strip()
            or "git command failed"
        )
        raise VerdictError(f"git {' '.join(args)}: {detail}", exit_code=2)
    return result.stdout


def _hash_untracked_files(digest: Any, workspace: Path) -> None:
    output = _git_output_bytes(workspace, ["ls-files", "--others", "--exclude-standard", "-z"])
    paths = sorted(path for path in output.split(b"\x00") if path)
    for raw_path in paths:
        path = workspace / os.fsdecode(raw_path)
        digest.update(b"untracked:path\x00")
        digest.update(raw_path)
        digest.update(b"\x00")
        try:
            if path.is_symlink():
                digest.update(b"untracked:symlink\x00")
                digest.update(os.fsencode(os.readlink(path)))
                digest.update(b"\x00")
                continue
            if not path.is_file():
                digest.update(b"untracked:missing-or-non-regular\x00")
                continue
            digest.update(b"untracked:file\x00")
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    digest.update(chunk)
            digest.update(b"\x00")
        except FileNotFoundError:
            digest.update(b"untracked:missing\x00")
        except OSError as exc:
            raise VerdictError(f"untracked file cannot be read: {path}: {exc}", exit_code=2) from exc


def compute_fingerprint(workspace: Path) -> dict[str, str]:
    if not workspace.is_dir():
        raise VerdictError(f"workspace directory cannot be read: {workspace}", exit_code=2)
    head_commit = _git_output(workspace, ["rev-parse", "HEAD"]).strip()
    status = _git_output(workspace, ["status", "--porcelain"])
    diff = _git_output(workspace, ["diff", "HEAD", "--no-color"])
    digest = hashlib.sha256()
    digest.update(status.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(diff.encode("utf-8"))
    digest.update(b"\x00")
    _hash_untracked_files(digest, workspace)
    return {
        "workspace": str(workspace),
        "head_commit": head_commit,
        "diff_fingerprint": f"sha256:{digest.hexdigest()}",
    }


def _load_verdict(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerdictError(f"verdict cannot be read: {exc}", exit_code=2) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise VerdictError(f"verdict JSON is invalid: {exc}", exit_code=2) from exc


def _cmd_validate(args: argparse.Namespace) -> int:
    data = _load_verdict(args.verdict)
    errors = _validate_verdict(data)
    freshness: dict[str, Any] | None = None
    if not errors and args.check_fresh:
        current = compute_fingerprint(Path(args.workspace))
        recorded = data["workspace"]
        fresh = (
            recorded.get("diff_fingerprint") == current["diff_fingerprint"]
            and recorded.get("head_commit") == current["head_commit"]
        )
        freshness = {
            "fresh": fresh,
            "recorded": {
                "head_commit": recorded.get("head_commit"),
                "diff_fingerprint": recorded.get("diff_fingerprint"),
            },
            "current": {
                "head_commit": current["head_commit"],
                "diff_fingerprint": current["diff_fingerprint"],
            },
        }
        if not fresh:
            errors.append(
                "verdict is stale: recorded fingerprint does not match the current working tree; re-review required"
            )
    if errors:
        raise VerdictError("; ".join(errors), exit_code=1)
    payload: dict[str, Any] = {
        "ok": True,
        "command": "validate",
        "verdict": str(args.verdict),
        "schema": SCHEMA_ID,
        "accepted_schema": data["schema"],
        "result": data["result"],
    }
    if freshness is not None:
        payload["freshness"] = freshness
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"ok: valid {SCHEMA_ID} verdict ({data['result']}) at {args.verdict}")
    return 0


def _cmd_fingerprint(args: argparse.Namespace) -> int:
    payload = {
        "ok": True,
        "command": "fingerprint",
        **compute_fingerprint(Path(args.workspace)),
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _print_json_diagnostic(message: str, command: str, code: str) -> None:
    diagnostic = {
        "kind": "changerail_review_verdict",
        "code": code,
        "message": message,
    }
    payload = {
        "schema": SCHEMA_ID,
        "ok": False,
        "command": command,
        "diagnostic": diagnostic,
        "diagnostics": [diagnostic],
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a v1 review verdict")
    validate.add_argument("verdict", type=Path)
    validate.add_argument(
        "--check-fresh",
        action="store_true",
        help="also compare the recorded fingerprint against the current working tree",
    )
    validate.add_argument(
        "--workspace",
        default=".",
        help="workspace root for --check-fresh (default: current directory)",
    )
    validate.add_argument("--json", action="store_true", help="emit structured JSON result or diagnostic")
    validate.set_defaults(func=_cmd_validate)

    fingerprint = subparsers.add_parser(
        "fingerprint", help="compute the working-tree freshness fingerprint"
    )
    fingerprint.add_argument(
        "--workspace",
        default=".",
        help="workspace root to fingerprint (default: current directory)",
    )
    fingerprint.set_defaults(func=_cmd_fingerprint)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except VerdictError as exc:
        if getattr(args, "json", False) or args.command == "fingerprint":
            _print_json_diagnostic(
                str(exc),
                getattr(args, "command", "unknown"),
                "input_error" if exc.exit_code == 2 else "validation_failed",
            )
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        if getattr(args, "json", False):
            _print_json_diagnostic(str(exc), getattr(args, "command", "unknown"), "input_error")
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
