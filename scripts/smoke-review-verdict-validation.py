#!/usr/bin/env python3
"""Smoke-test ChangeRail review verdict validation and independence attestation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_review_verdict.py"


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        sys.stderr.write(f"{label} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n")
        raise SystemExit(1)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(verdict: Path, workspace: Path, check_fresh: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(HELPER), "validate", str(verdict), "--workspace", str(workspace), "--json"]
    if check_fresh:
        command.append("--check-fresh")
    return run(command)


def base_verdict(workspace: Path) -> dict[str, object]:
    fingerprint = run([sys.executable, str(HELPER), "fingerprint", "--workspace", str(workspace)])
    require_ok(fingerprint, "fingerprint")
    data = json.loads(fingerprint.stdout)
    return {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": "2026-07-12T00:00:00Z",
        "card": {
            "id": "example-card",
            "path": "openspec/board/3.inprogress/example-card.md",
        },
        "workspace": {
            "root": data["workspace"],
            "head_commit": data["head_commit"],
            "diff_fingerprint": data["diff_fingerprint"],
        },
        "reviewer": {
            "kind": "codex-exec",
            "independence": {
                "fresh_context": True,
                "did_not_plan_or_implement": True,
                "basis": "fresh smoke-test reviewer context",
            },
        },
        "result": "go",
        "review_cycle": 1,
        "acceptance": [
            {
                "criterion": "example criterion",
                "verdict": "pass",
                "evidence": "smoke fixture evidence",
            }
        ],
        "findings": [],
        "evidence_audit": {
            "claims_checked": 1,
            "claims_unbacked": 0,
        },
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "repo"
        workspace.mkdir()
        require_ok(run(["git", "init", "-q"], cwd=workspace), "git init")
        require_ok(run(["git", "config", "user.email", "smoke@example.invalid"], cwd=workspace), "git config email")
        require_ok(run(["git", "config", "user.name", "ChangeRail Smoke"], cwd=workspace), "git config name")
        (workspace / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        (workspace / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
        require_ok(run(["git", "add", ".gitignore", "tracked.txt"], cwd=workspace), "git add")
        require_ok(run(["git", "commit", "-q", "-m", "initial"], cwd=workspace), "git commit")

        valid = base_verdict(workspace)
        verdict_dir = workspace / ".runtime" / "changerail" / "reviews"
        verdict_dir.mkdir(parents=True)
        verdict_path = verdict_dir / "valid.json"
        write_json(verdict_path, valid)
        require_ok(validate(verdict_path, workspace, check_fresh=True), "valid verdict")

        missing = deepcopy(valid)
        del missing["reviewer"]["independence"]  # type: ignore[index]
        missing_path = verdict_dir / "missing-independence.json"
        write_json(missing_path, missing)
        missing_result = validate(missing_path, workspace)
        if missing_result.returncode != 1 or "independence" not in missing_result.stderr:
            sys.stderr.write("missing independence verdict did not fail as expected\n")
            sys.stderr.write(missing_result.stderr)
            return 1

        false_fresh = deepcopy(valid)
        false_fresh["reviewer"]["independence"]["fresh_context"] = False  # type: ignore[index]
        false_fresh_path = verdict_dir / "false-fresh-context.json"
        write_json(false_fresh_path, false_fresh)
        false_fresh_result = validate(false_fresh_path, workspace)
        if false_fresh_result.returncode != 1 or "fresh_context" not in false_fresh_result.stderr:
            sys.stderr.write("false fresh_context verdict did not fail as expected\n")
            sys.stderr.write(false_fresh_result.stderr)
            return 1

        false_worker = deepcopy(valid)
        false_worker["reviewer"]["independence"]["did_not_plan_or_implement"] = False  # type: ignore[index]
        false_worker_path = verdict_dir / "false-worker-boundary.json"
        write_json(false_worker_path, false_worker)
        false_worker_result = validate(false_worker_path, workspace)
        if (
            false_worker_result.returncode != 1
            or "did_not_plan_or_implement" not in false_worker_result.stderr
        ):
            sys.stderr.write("false did_not_plan_or_implement verdict did not fail as expected\n")
            sys.stderr.write(false_worker_result.stderr)
            return 1

        extra_nested = deepcopy(valid)
        extra_nested["reviewer"]["independence"]["unexpected"] = True  # type: ignore[index]
        extra_nested_path = verdict_dir / "extra-nested-field.json"
        write_json(extra_nested_path, extra_nested)
        extra_nested_result = validate(extra_nested_path, workspace)
        if extra_nested_result.returncode != 1 or "Additional properties" not in extra_nested_result.stderr:
            sys.stderr.write("extra nested field verdict did not fail as expected\n")
            sys.stderr.write(extra_nested_result.stderr)
            return 1

        bad_time = deepcopy(valid)
        bad_time["reviewed_at"] = "not-a-date-time"
        bad_time_path = verdict_dir / "bad-reviewed-at.json"
        write_json(bad_time_path, bad_time)
        bad_time_result = validate(bad_time_path, workspace)
        if bad_time_result.returncode != 1 or "date-time" not in bad_time_result.stderr:
            sys.stderr.write("bad reviewed_at verdict did not fail as expected\n")
            sys.stderr.write(bad_time_result.stderr)
            return 1

        bad_type = deepcopy(valid)
        bad_type["evidence_audit"]["claims_checked"] = "1"  # type: ignore[index]
        bad_type_path = verdict_dir / "bad-nested-type.json"
        write_json(bad_type_path, bad_type)
        bad_type_result = validate(bad_type_path, workspace)
        if bad_type_result.returncode != 1 or "$.evidence_audit.claims_checked" not in bad_type_result.stderr:
            sys.stderr.write("bad nested type verdict did not fail as expected\n")
            sys.stderr.write(bad_type_result.stderr)
            return 1

        malformed_go = deepcopy(valid)
        malformed_go["findings"] = [
            {
                "id": "R1",
                "severity": "blocker",
                "area": "code",
                "summary": "blocker must make go invalid",
            }
        ]
        malformed_go_path = verdict_dir / "malformed-go.json"
        write_json(malformed_go_path, malformed_go)
        malformed_go_result = validate(malformed_go_path, workspace, check_fresh=True)
        if malformed_go_result.returncode != 1 or "result 'go' is inconsistent" not in malformed_go_result.stderr:
            sys.stderr.write("malformed go verdict did not fail freshness gate as expected\n")
            sys.stderr.write(malformed_go_result.stderr)
            return 1

    print("SMOKE_REVIEW_VERDICT_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
