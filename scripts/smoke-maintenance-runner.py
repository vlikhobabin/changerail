#!/usr/bin/env python3
"""Smoke-test the bounded ChangeRail maintenance runner."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from changerail_repository_knowledge import validate_maintenance_run  # noqa: E402


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run(command: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_non_runtime(path: Path) -> dict[str, bytes]:
    return {
        candidate.relative_to(path).as_posix(): candidate.read_bytes()
        for candidate in sorted(path.rglob("*"))
        if candidate.is_file() and ".runtime" not in candidate.relative_to(path).parts
    }


def write_workspace(workspace: Path) -> None:
    (workspace / ".changerail").mkdir(parents=True, exist_ok=True)
    (workspace / "docs").mkdir(parents=True, exist_ok=True)
    (workspace / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (workspace / ".changerail" / "knowledge.yaml").write_text(
        "schema: changerail.repository-knowledge.v1\n"
        "records:\n"
        "  - path: docs/guide.md\n"
        "    status: active\n"
        "    type: reference\n"
        "    owner: ChangeRail core\n"
        "    source_globs: []\n"
        "    verify: []\n"
        "    review_after: null\n"
        "    supersedes: []\n",
        encoding="utf-8",
    )
    (workspace / ".changerail" / "maintenance.yaml").write_text(
        "schema: changerail.maintenance-policy.v1\n"
        "catalog_path: .changerail/knowledge.yaml\n"
        "generated_index_path: .changerail/KNOWLEDGE.md\n",
        encoding="utf-8",
    )


def status_path(workspace: Path, run_id: str) -> Path:
    return workspace / ".runtime" / "changerail" / "maintenance" / "runs" / run_id / "status.json"


def assert_status(failures: list[str], workspace: Path, run_id: str, expected: str) -> dict[str, object]:
    path = status_path(workspace, run_id)
    if not path.is_file():
        failures.append(f"{run_id}: status was not written")
        return {}
    payload = read_json(path)
    errors = validate_maintenance_run(payload)
    if errors:
        failures.append(f"{run_id}: status schema validation failed: {errors}")
    if payload.get("result") != expected:
        failures.append(f"{run_id}: expected result {expected}, got {payload.get('result')}")
    return payload


def main() -> int:
    failures: list[str] = []
    workspace = ROOT / ".runtime" / "changerail" / "maintenance-runner-smoke"
    shutil.rmtree(workspace, ignore_errors=True)
    write_workspace(workspace)

    before_scan = snapshot_non_runtime(workspace)
    scan = run(
        [
            "bin/changerail-maintenance-runner",
            "--workspace",
            rel(workspace),
            "scan",
            "--run-id",
            "scan-ok",
            "--timeout",
            "30",
            "--json",
        ]
    )
    after_scan = snapshot_non_runtime(workspace)
    if scan.returncode != 0:
        failures.append(f"scan runner failed: {scan.stderr or scan.stdout}")
    scan_status = assert_status(failures, workspace, "scan-ok", "SUCCEEDED")
    artifacts = scan_status.get("artifacts") if isinstance(scan_status.get("artifacts"), dict) else {}
    report_rel = artifacts.get("lifecycle_report") if isinstance(artifacts.get("lifecycle_report"), str) else ""
    if not report_rel or not (workspace / report_rel).is_file():
        failures.append("scan runner did not retain lifecycle report artifact")
    if before_scan != after_scan:
        failures.append("scan runner mutated non-runtime workspace files")

    lock_root = workspace / ".runtime" / "changerail" / "maintenance"
    lock_root.mkdir(parents=True, exist_ok=True)
    (lock_root / "maintenance.lock").write_text("stale smoke lock\n", encoding="utf-8")
    locked = run(
        [
            "bin/changerail-maintenance-runner",
            "--workspace",
            rel(workspace),
            "scan",
            "--run-id",
            "lock-blocked",
            "--json",
        ]
    )
    if locked.returncode == 0:
        failures.append("runner did not block on existing lock")
    locked_status = assert_status(failures, workspace, "lock-blocked", "BLOCKED")
    if locked_status.get("terminal_reason") != "lock_exists":
        failures.append("lock-blocked status did not preserve lock_exists reason")
    (lock_root / "maintenance.lock").unlink()

    timeout_run = run(
        [
            "bin/changerail-maintenance-runner",
            "--workspace",
            rel(workspace),
            "triage",
            "--run-id",
            "triage-timeout",
            "--timeout",
            "1",
            "--json",
            "--triage-command",
            "python3",
            "-c",
            "import time; time.sleep(5)",
        ],
        timeout=10,
    )
    if timeout_run.returncode == 0:
        failures.append("triage timeout unexpectedly succeeded")
    timeout_status = assert_status(failures, workspace, "triage-timeout", "BLOCKED")
    if timeout_status.get("terminal_reason") != "timeout":
        failures.append("triage timeout status did not preserve timeout reason")

    invalid_triage = run(
        [
            "bin/changerail-maintenance-runner",
            "--workspace",
            rel(workspace),
            "triage",
            "--run-id",
            "triage-invalid",
            "--timeout",
            "30",
            "--json",
            "--triage-command",
            "python3",
            "-c",
            "print('not json')",
        ]
    )
    if invalid_triage.returncode == 0:
        failures.append("invalid triage child output unexpectedly succeeded")
    invalid_status = assert_status(failures, workspace, "triage-invalid", "BLOCKED")
    if invalid_status.get("terminal_reason") != "invalid_child_output":
        failures.append("invalid triage status did not preserve invalid_child_output reason")

    annotations = workspace / ".runtime" / "changerail" / "maintenance" / "triage-input.json"
    annotations.parent.mkdir(parents=True, exist_ok=True)
    annotations.write_text(
        json.dumps(
            {
                "schema": "changerail.maintenance-triage.v1",
                "generated_at": "2026-08-09T00:00:00Z",
                "annotations": [],
            },
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    valid_triage = run(
        [
            "bin/changerail-maintenance-runner",
            "--workspace",
            rel(workspace),
            "triage",
            "--run-id",
            "triage-ok",
            "--timeout",
            "30",
            "--annotations",
            annotations.relative_to(workspace).as_posix(),
            "--report",
            report_rel,
            "--json",
        ]
    )
    if valid_triage.returncode != 0:
        failures.append(f"valid triage runner failed: {valid_triage.stderr or valid_triage.stdout}")
    triage_status = assert_status(failures, workspace, "triage-ok", "SUCCEEDED")
    triage_artifacts = triage_status.get("artifacts") if isinstance(triage_status.get("artifacts"), dict) else {}
    if not triage_artifacts.get("annotations") or not triage_artifacts.get("card_preview"):
        failures.append("valid triage runner did not retain annotations and card preview artifacts")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print("SMOKE_MAINTENANCE_RUNNER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
