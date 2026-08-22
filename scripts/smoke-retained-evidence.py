#!/usr/bin/env python3
"""Smoke-test retained ChangeRail evidence capture and validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "bin" / "changerail-evidence"
TARGET = {
    "schema": "changerail.execution-target.v1",
    "id": "database-primary",
    "fingerprint": "sha256:" + ("1" * 64),
    "target_substitution_policy": "forbid",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def require_json(result: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{label} did not emit JSON\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}") from exc


def require_returncode(result: subprocess.CompletedProcess[str], expected: int, label: str) -> None:
    if result.returncode == expected:
        return
    raise AssertionError(
        f"{label} returned {result.returncode}, expected {expected}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def capture(workspace: Path, evidence_id: str, *argv: str, timeout: str = "5") -> subprocess.CompletedProcess[str]:
    return run(
        [
            str(HELPER),
            "capture",
            "--workspace",
            str(workspace),
            "--card-id",
            "example-card",
            "--change",
            "example-change",
            "--id",
            evidence_id,
            "--timeout",
            timeout,
            "--json",
            "--",
            *argv,
        ]
    )


def git(workspace: Path, *args: str) -> None:
    result = subprocess.run(["git", "-C", str(workspace), *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-evidence-smoke-") as tmp:
        workspace = Path(tmp)

        success = capture(workspace, "success", sys.executable, "-c", "print('success output')")
        require_returncode(success, 0, "success capture")
        success_payload = require_json(success, "success capture")
        index_path = workspace / success_payload["index_path"]
        raw_success_path = workspace / success_payload["raw_output_path"]
        if not raw_success_path.is_file():
            raise AssertionError(f"success raw output missing: {raw_success_path}")

        failure = capture(workspace, "failure", sys.executable, "-c", "import sys; print('bad'); sys.exit(7)")
        require_returncode(failure, 1, "failure capture")
        failure_payload = require_json(failure, "failure capture")
        if failure_payload["status"] != "failed" or failure_payload["exit_code"] != 7:
            raise AssertionError(f"failure capture did not retain exit code: {failure_payload!r}")

        timeout = capture(
            workspace,
            "timeout",
            sys.executable,
            "-c",
            "import time; print('before timeout'); time.sleep(1)",
            timeout="0.1",
        )
        require_returncode(timeout, 1, "timeout capture")
        timeout_payload = require_json(timeout, "timeout capture")
        if timeout_payload["status"] != "timeout":
            raise AssertionError(f"timeout capture did not retain timeout status: {timeout_payload!r}")

        redaction_script = workspace / "emit_redaction.py"
        redaction_script.write_text("print('to' + 'ken=' + 'redacted-value')\n", encoding="utf-8")
        redaction = capture(workspace, "redaction", sys.executable, str(redaction_script))
        require_returncode(redaction, 0, "redaction capture")
        redaction_payload = require_json(redaction, "redaction capture")
        redacted_path = workspace / redaction_payload["raw_output_path"]
        redacted_text = redacted_path.read_text(encoding="utf-8")
        if "redacted-value" in redacted_text or "<REDACTED>" not in redacted_text:
            raise AssertionError(f"secret-like output was not redacted: {redacted_text!r}")

        auth_script = workspace / "emit_auth_redaction.py"
        auth_script.write_text("print('Author' + 'ization: Bearer ' + 'tail-value')\n", encoding="utf-8")
        auth_redaction = capture(workspace, "auth-redaction", sys.executable, str(auth_script))
        require_returncode(auth_redaction, 0, "authorization redaction capture")
        auth_payload = require_json(auth_redaction, "authorization redaction capture")
        auth_text = (workspace / auth_payload["raw_output_path"]).read_text(encoding="utf-8")
        if "tail-value" in auth_text or "<REDACTED>" not in auth_text:
            raise AssertionError(f"authorization-style output was not fully redacted: {auth_text!r}")

        blocked_arg = "--" + "to" + "ken=blocked-value"
        blocked = capture(workspace, "blocked", sys.executable, "-c", "print('should not run')", blocked_arg)
        require_returncode(blocked, 2, "secret argv block")
        if blocked_arg in blocked.stderr:
            raise AssertionError(f"secret-like argv leaked into diagnostic: {blocked.stderr!r}")

        outside_index = run(
            [
                str(HELPER),
                "capture",
                "--workspace",
                str(workspace),
                "--index",
                "tracked-evidence/index.json",
                "--id",
                "outside-runtime",
                "--json",
                "--",
                sys.executable,
                "-c",
                "print('outside')",
            ]
        )
        require_returncode(outside_index, 2, "outside-runtime index block")
        if (workspace / "tracked-evidence" / "index.json").exists():
            raise AssertionError("outside-runtime index path was written")

        target_workspace = workspace / "target-evidence"
        target_workspace.mkdir()
        git(target_workspace, "init", "-q")
        target_path = target_workspace / ".changerail" / "execution-target.json"
        target_path.parent.mkdir()
        target_path.write_text(json.dumps(TARGET, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        git(target_workspace, "add", ".changerail/execution-target.json")
        target_capture = capture(target_workspace, "target-success", sys.executable, "-c", "print('target success')")
        require_returncode(target_capture, 0, "target-bound capture")
        target_payload = require_json(target_capture, "target-bound capture")
        target_index = json.loads((target_workspace / target_payload["index_path"]).read_text(encoding="utf-8"))
        if target_index.get("execution_target") != TARGET or target_index["entries"][0].get("execution_target") != TARGET:
            raise AssertionError(f"target-bound evidence did not retain identity: {target_index!r}")

        note_workspace = workspace / "note-first"
        note_workspace.mkdir()
        note = run(
            [
                str(HELPER),
                "note",
                "--workspace",
                str(note_workspace),
                "--card-id",
                "example-card",
                "--id",
                "red-not-applicable",
                "--reason",
                "RED evidence is not applicable for this smoke note",
                "--json",
            ]
        )
        require_returncode(note, 0, "not-applicable note")
        note_payload = require_json(note, "not-applicable note")
        note_index_path = note_workspace / note_payload["index_path"]
        if not note_index_path.is_file():
            raise AssertionError(f"standalone not-applicable note index missing: {note_index_path}")

        validate = run([str(HELPER), "validate", str(index_path), "--workspace", str(workspace), "--json"])
        require_returncode(validate, 0, "evidence validate")

        raw_success_path.unlink()
        missing = run([str(HELPER), "validate", str(index_path), "--workspace", str(workspace), "--json"])
        require_returncode(missing, 1, "missing evidence validate")
        if "missing runtime evidence path" not in missing.stderr:
            raise AssertionError(f"missing evidence diagnostic was not specific: {missing.stderr!r}")

    print("SMOKE_RETAINED_EVIDENCE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
