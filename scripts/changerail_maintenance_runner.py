#!/usr/bin/env python3
"""Run bounded ChangeRail repository maintenance jobs."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from changerail_repository_knowledge import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_MAINTENANCE_RUNTIME_ROOT,
    DEFAULT_POLICY_PATH,
    validate_lifecycle_report,
    validate_maintenance_run,
    validate_maintenance_triage,
)

SOURCE_ROOT = Path(__file__).resolve().parents[1]
MAINTENANCE_HELPER = SOURCE_ROOT / "bin" / "changerail-maintenance"
SECRET_LIKE_RE = re.compile(
    r"(?i)(secret|token|password|passwd|api[_-]?key|credential|private[_-]?key)\s*[:=]\s*\S+"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def sanitize_detail(value: str, *, limit: int = 240) -> str:
    cleaned = SECRET_LIKE_RE.sub(r"\1=<redacted>", " ".join(value.split()))
    return cleaned[:limit]


def repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def head_commit(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout.strip() or None if result.returncode == 0 else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="repository root, default: current directory")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    scan = subparsers.add_parser("scan", help="run deterministic maintenance scan/report")
    add_common(scan)
    scan.add_argument("--catalog", default=DEFAULT_CATALOG_PATH.as_posix(), help="repository-relative catalog path")
    scan.add_argument("--policy", default=DEFAULT_POLICY_PATH.as_posix(), help="repository-relative policy path")
    scan.add_argument("--fail-on", choices=("info", "minor", "major", "blocker"), help="override scan threshold")

    triage = subparsers.add_parser("triage", help="validate bounded maintenance triage output")
    add_common(triage)
    triage.add_argument("--annotations", help="repository-relative triage annotation JSON")
    triage.add_argument("--report", help="repository-relative lifecycle report used for card preview")
    triage.add_argument("--agent-budget-tokens", type=int, help="optional agent budget recorded in status")
    triage.add_argument(
        "--triage-command",
        nargs=argparse.REMAINDER,
        help="optional child command whose stdout must be changerail.maintenance-triage.v1 JSON",
    )
    return parser


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-id", help="stable run id; default is generated")
    parser.add_argument("--timeout", type=int, default=900, help="child command timeout in seconds")
    parser.add_argument("--json", action="store_true", help="print final run status JSON")


def generated_run_id(mode: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{os.getpid()}-{mode}"


def diagnostic(code: str, message: str, *, severity: str = "blocker", path: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": sanitize_detail(message), "severity": severity}
    if path:
        payload["path"] = path
    return payload


class RunContext:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.root = Path(args.workspace).resolve(strict=False)
        self.mode = args.mode
        self.started_at = utc_now()
        self.run_id = args.run_id or generated_run_id(args.mode)
        self.runtime_root = self.root / DEFAULT_MAINTENANCE_RUNTIME_ROOT
        self.run_dir = self.runtime_root / "runs" / self.run_id
        self.status_path = self.run_dir / "status.json"
        self.lock_path = self.runtime_root / "maintenance.lock"
        self.lock_fd: int | None = None
        self.status: dict[str, Any] = {
            "schema": "changerail.maintenance-run.v1",
            "run_id": self.run_id,
            "updated_at": self.started_at,
            "workspace": {"root": self.root.as_posix()},
            "mode": self.mode,
            "phase": "starting",
            "result": "RUNNING",
            "timestamps": {"started_at": self.started_at},
            "command": {"argv": [], "stdin": "closed", "json": True, "timeout_seconds": args.timeout},
            "usage": {"available": False, "reason": "not observed by maintenance runner"},
            "diagnostics": [],
        }
        commit = head_commit(self.root)
        if commit:
            self.status["workspace"]["head_commit"] = commit

    def write_status(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.status["updated_at"] = utc_now()
        errors = validate_maintenance_run(self.status)
        if errors:
            raise RuntimeError("maintenance run status is schema-invalid: " + "; ".join(errors))
        tmp = self.status_path.with_suffix(".json.tmp")
        tmp.write_text(json_text(self.status), encoding="utf-8")
        tmp.replace(self.status_path)

    def acquire_lock(self) -> bool:
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        try:
            self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            self.status["lock"] = {
                "path": repo_rel(self.root, self.lock_path),
                "acquired": False,
                "released": False,
                "diagnostics": [diagnostic("lock_exists", "maintenance run lock already exists")],
            }
            self.status["phase"] = "terminal"
            self.status["result"] = "BLOCKED"
            self.status["terminal_reason"] = "lock_exists"
            self.status["timestamps"]["ended_at"] = utc_now()
            self.status["diagnostics"].append(diagnostic("lock_exists", "maintenance run lock already exists"))
            self.write_status()
            return False
        os.write(self.lock_fd, json_text({"run_id": self.run_id, "created_at": utc_now()}).encode("utf-8"))
        self.status["lock"] = {
            "path": repo_rel(self.root, self.lock_path),
            "acquired": True,
            "released": False,
            "diagnostics": [],
        }
        self.write_status()
        return True

    def release_lock(self) -> None:
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None
        if self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except OSError as exc:
                self.status["diagnostics"].append(diagnostic("lock_release_failed", str(exc)))
        if "lock" in self.status:
            self.status["lock"]["released"] = True


def run_child(ctx: RunContext, argv: list[str]) -> tuple[int | None, str, bool]:
    ctx.status["command"]["argv"] = [str(part) for part in argv]
    try:
        result = subprocess.run(
            argv,
            cwd=ctx.root,
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=ctx.args.timeout,
        )
    except subprocess.TimeoutExpired:
        ctx.status["process"] = {"timed_out": True}
        ctx.status["diagnostics"].append(diagnostic("command_timeout", "child execution exceeded configured timeout"))
        return None, "", True
    ctx.status["process"] = {"exit_code": result.returncode, "timed_out": False}
    if result.stderr:
        ctx.status["diagnostics"].append(
            diagnostic("child_stderr", sanitize_detail(result.stderr), severity="info")
        )
    return result.returncode, result.stdout, False


def load_json_stdout(ctx: RunContext, output: str, *, kind: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        ctx.status["diagnostics"].append(diagnostic("invalid_child_output", f"{kind} output is not JSON: {exc}"))
        return None
    if not isinstance(payload, dict):
        ctx.status["diagnostics"].append(diagnostic("invalid_child_output", f"{kind} output must be one JSON object"))
        return None
    return payload


def finish(ctx: RunContext, *, result: str, reason: str | None = None, exit_code: int) -> int:
    ctx.release_lock()
    ctx.status["phase"] = "terminal"
    ctx.status["result"] = result
    if reason:
        ctx.status["terminal_reason"] = reason
    ctx.status["timestamps"]["ended_at"] = utc_now()
    ctx.write_status()
    if ctx.args.json:
        print(json_text(ctx.status), end="")
    else:
        print(f"MAINTENANCE_RUN_{result} {repo_rel(ctx.root, ctx.status_path)}")
    return exit_code


def command_scan(ctx: RunContext) -> int:
    if not MAINTENANCE_HELPER.is_file():
        ctx.status["diagnostics"].append(diagnostic("helper_missing", "bin/changerail-maintenance is missing"))
        return finish(ctx, result="BLOCKED", reason="helper_missing", exit_code=2)
    ctx.status["phase"] = "scan"
    ctx.write_status()
    argv = [
        str(MAINTENANCE_HELPER),
        "--workspace",
        str(ctx.root),
        "report",
        "--catalog",
        ctx.args.catalog,
        "--policy",
        ctx.args.policy,
        "--json",
    ]
    if ctx.args.fail_on:
        argv.extend(["--fail-on", ctx.args.fail_on])
    exit_code, stdout, timed_out = run_child(ctx, argv)
    if timed_out:
        return finish(ctx, result="BLOCKED", reason="timeout", exit_code=2)
    payload = load_json_stdout(ctx, stdout, kind="maintenance report")
    if payload is None:
        return finish(ctx, result="BLOCKED", reason="invalid_child_output", exit_code=2)
    errors = validate_lifecycle_report(payload)
    if errors:
        ctx.status["diagnostics"].append(diagnostic("maintenance_report_schema_error", "; ".join(errors)))
        return finish(ctx, result="BLOCKED", reason="invalid_child_output", exit_code=2)
    report_path = ctx.run_dir / "maintenance-report.json"
    report_path.write_text(json_text(payload), encoding="utf-8")
    ctx.status["artifacts"] = {"lifecycle_report": repo_rel(ctx.root, report_path)}
    if exit_code == 0:
        return finish(ctx, result="SUCCEEDED", exit_code=0)
    if exit_code == 1:
        ctx.status["diagnostics"].append(
            diagnostic("threshold_reached", "maintenance report reached configured fail threshold", severity="major")
        )
        return finish(ctx, result="FAILED", reason="threshold_reached", exit_code=1)
    return finish(ctx, result="BLOCKED", reason="maintenance_report_failed", exit_code=2)


def triage_argv(ctx: RunContext) -> list[str] | None:
    if ctx.args.triage_command:
        command = list(ctx.args.triage_command)
        if command and command[0] == "--":
            command = command[1:]
        return command or None
    if not ctx.args.annotations:
        return None
    return [
        str(MAINTENANCE_HELPER),
        "--workspace",
        str(ctx.root),
        "triage",
        "--annotations",
        ctx.args.annotations,
        "--json",
    ]


def write_card_preview(ctx: RunContext) -> bool:
    if not ctx.args.report:
        return True
    argv = [
        str(MAINTENANCE_HELPER),
        "--workspace",
        str(ctx.root),
        "cards",
        "--report",
        ctx.args.report,
        "--json",
    ]
    try:
        result = subprocess.run(
            argv,
            cwd=ctx.root,
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=ctx.args.timeout,
        )
    except subprocess.TimeoutExpired:
        ctx.status["diagnostics"].append(diagnostic("card_preview_timeout", "card preview exceeded configured timeout"))
        return False
    if result.stderr:
        ctx.status["diagnostics"].append(
            diagnostic("card_preview_stderr", sanitize_detail(result.stderr), severity="info")
        )
    payload = load_json_stdout(ctx, result.stdout, kind="card preview")
    if result.returncode != 0 or payload is None or payload.get("ok") is not True:
        ctx.status["diagnostics"].append(diagnostic("card_preview_invalid", "card preview did not complete successfully"))
        return False
    preview_path = ctx.run_dir / "card-preview.json"
    preview_path.write_text(json_text(payload), encoding="utf-8")
    ctx.status.setdefault("artifacts", {})["card_preview"] = repo_rel(ctx.root, preview_path)
    return True


def command_triage(ctx: RunContext) -> int:
    command = triage_argv(ctx)
    if command is None:
        ctx.status["diagnostics"].append(diagnostic("triage_input_missing", "triage requires --annotations or --triage-command"))
        return finish(ctx, result="BLOCKED", reason="triage_input_missing", exit_code=2)
    if ctx.args.agent_budget_tokens:
        ctx.status["budget"] = {"agent_tokens": ctx.args.agent_budget_tokens}
    ctx.status["phase"] = "triage"
    ctx.write_status()
    exit_code, stdout, timed_out = run_child(ctx, command)
    if timed_out:
        return finish(ctx, result="BLOCKED", reason="timeout", exit_code=2)
    payload = load_json_stdout(ctx, stdout, kind="triage")
    if payload is None:
        return finish(ctx, result="BLOCKED", reason="invalid_child_output", exit_code=2)
    errors = validate_maintenance_triage(payload)
    if errors:
        ctx.status["diagnostics"].append(diagnostic("maintenance_triage_schema_error", "; ".join(errors)))
        return finish(ctx, result="BLOCKED", reason="invalid_child_output", exit_code=2)
    annotations_path = ctx.run_dir / "annotations.json"
    annotations_path.write_text(json_text(payload), encoding="utf-8")
    ctx.status["artifacts"] = {"annotations": repo_rel(ctx.root, annotations_path)}
    if not write_card_preview(ctx):
        return finish(ctx, result="BLOCKED", reason="card_preview_invalid", exit_code=2)
    if exit_code == 0:
        return finish(ctx, result="SUCCEEDED", exit_code=0)
    return finish(ctx, result="BLOCKED", reason="triage_failed", exit_code=2)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout < 1:
        parser.error("--timeout must be at least 1")
    ctx = RunContext(args)
    if not ctx.acquire_lock():
        if args.json:
            print(json_text(ctx.status), end="")
        else:
            print(f"MAINTENANCE_RUN_BLOCKED {repo_rel(ctx.root, ctx.status_path)}")
        return 1
    if args.mode == "scan":
        return command_scan(ctx)
    if args.mode == "triage":
        return command_triage(ctx)
    parser.error(f"unknown mode: {args.mode}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
