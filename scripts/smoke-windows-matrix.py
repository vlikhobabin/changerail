#!/usr/bin/env python3
"""Aggregate Windows support smoke matrix checks."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "changerail.windows-smoke-matrix.v1"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_ROOT = Path(".runtime/changerail/windows-smoke")
DEFAULT_INVENTORY = Path("internal/windows-lab-inventory.json")
EXPECTED_HOST_IDS = ("windows-host-a", "windows-host-b")
SECRET_KEY_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential)")
WINDOWS_HOME_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+")
WINDOWS_ABS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"']+")
POSIX_HOME_RE = re.compile(r"(?:/home|/Users)/[A-Za-z0-9._-]+")
SSH_TARGET_RE = re.compile(r"(?P<user>[A-Za-z0-9._-]+)@(?P<host>[A-Za-z0-9._-]+(?:\.[A-Za-z0-9._-]+)+)")


@dataclass
class MatrixItem:
    name: str
    category: str
    status: str
    command: str
    exit_code: int | None
    message: str
    evidence: dict[str, object]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def compact(value: str, limit: int = 300) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def sanitize_detail(value: str) -> str:
    redacted = SECRET_KEY_RE.sub("credential", value)
    redacted = WINDOWS_HOME_RE.sub("<windows-home>", redacted)
    redacted = WINDOWS_ABS_PATH_RE.sub("<windows-path>", redacted)
    redacted = POSIX_HOME_RE.sub("<home>", redacted)
    redacted = SSH_TARGET_RE.sub("<host>", redacted)
    return compact(redacted)


def sanitize_object(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_detail(value)
    if isinstance(value, list):
        return [sanitize_object(item) for item in value]
    if isinstance(value, dict):
        return {str(key): sanitize_object(item) for key, item in value.items()}
    return value


def command_display(display_command: list[str]) -> str:
    return " ".join(display_command)


def python_command(script: str, *args: str | Path) -> tuple[list[str], list[str]]:
    display_args = ["python3", script, *(str(arg) for arg in args)]
    command_args = [sys.executable, str(ROOT / script), *(str(arg) for arg in args)]
    return command_args, display_args


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json_from_path(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_json_from_text(text: str) -> dict[str, object] | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def payload_status(payload: dict[str, object] | None) -> str | None:
    if not payload:
        return None
    summary = payload.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("status"), str):
        return summary["status"]
    status = payload.get("status")
    if isinstance(status, str):
        return status
    ok = payload.get("ok")
    if isinstance(ok, bool):
        return "pass" if ok else "fail"
    return None


def payload_message(payload: dict[str, object] | None, fallback: str) -> str:
    if not payload:
        return fallback
    summary = payload.get("summary")
    if isinstance(summary, dict):
        total = summary.get("total")
        passed = summary.get("passed")
        failed = summary.get("failed")
        passed_hosts = summary.get("passed_hosts")
        failed_hosts = summary.get("failed_hosts")
        if all(isinstance(value, int) for value in (total, passed, failed)):
            return f"summary {summary.get('status')} ({passed}/{total} passed, {failed} failed)"
        host_count = summary.get("host_count")
        if all(isinstance(value, int) for value in (host_count, passed, failed)):
            return f"summary {payload_status(payload)} ({passed}/{host_count} hosts passed, {failed} failed)"
        if all(isinstance(value, int) for value in (passed_hosts, failed_hosts)):
            return (
                f"summary {payload_status(payload)} "
                f"({passed_hosts} hosts passed, {failed_hosts} hosts failed)"
            )
        return sanitize_detail(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    diagnostic = payload.get("diagnostic")
    if isinstance(diagnostic, str):
        return sanitize_detail(diagnostic)
    return fallback


def summarize_payload(payload: dict[str, object] | None) -> dict[str, object]:
    if not payload:
        return {}
    summary = payload.get("summary")
    hosts = payload.get("hosts")
    result: dict[str, object] = {}
    if isinstance(summary, dict):
        result["summary"] = sanitize_object(summary)
    if isinstance(hosts, list):
        result["hosts"] = sanitize_object(hosts)
    if isinstance(payload.get("schema"), str):
        result["schema"] = payload["schema"]
    if isinstance(payload.get("report_path"), str):
        result["child_report_path"] = sanitize_detail(payload["report_path"])
    return result


def run_child(
    *,
    name: str,
    category: str,
    command: list[str],
    display_command: list[str],
    cwd: Path,
    raw_dir: Path,
    workspace: Path,
    report_path: Path | None = None,
    timeout: float = 900.0,
) -> MatrixItem:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", name.lower()).strip("-")
    stdout_path = raw_dir / f"{safe_name}.stdout.txt"
    stderr_path = raw_dir / f"{safe_name}.stderr.txt"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "OPENSPEC_TELEMETRY": "0"}
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
            timeout=timeout,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        write_text(stdout_path, stdout)
        write_text(stderr_path, stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        write_text(stdout_path, stdout)
        write_text(stderr_path, stderr)
        return MatrixItem(
            name=name,
            category=category,
            status="fail",
            command=command_display(display_command),
            exit_code=None,
            message=f"command timed out after {timeout:g} seconds",
            evidence={
                "stdout_path": relpath(stdout_path, workspace),
                "stderr_path": relpath(stderr_path, workspace),
            },
        )

    payload = load_json_from_path(report_path) if report_path else None
    if payload is None:
        payload = load_json_from_text(stdout)
    observed = payload_status(payload)
    success_statuses = {"pass", "passed", "ok"}
    failed_statuses = {"fail", "failed", "blocked"}
    if completed.returncode == 0 and (observed is None or observed in success_statuses):
        status = "pass"
    elif observed in failed_statuses:
        status = "fail"
    else:
        status = "fail"
    fallback = sanitize_detail(stderr or stdout or f"exit {completed.returncode}")
    evidence: dict[str, object] = {
        "stdout_path": relpath(stdout_path, workspace),
        "stderr_path": relpath(stderr_path, workspace),
    }
    if report_path is not None:
        evidence["report_path"] = relpath(report_path, workspace)
    evidence.update(summarize_payload(payload))
    return MatrixItem(
        name=name,
        category=category,
        status=status,
        command=command_display(display_command),
        exit_code=completed.returncode,
        message=payload_message(payload, fallback),
        evidence=evidence,
    )


def local_items(cycle_dir: Path, workspace: Path) -> list[MatrixItem]:
    raw_dir = cycle_dir / "raw"
    command_specs: list[tuple[str, str, list[str], list[str], Path | None]] = []

    command, display = python_command("scripts/smoke-windows-entrypoints.py", "--json")
    command_specs.append(("Windows entrypoint smoke", "local", command, display, None))

    command, display = python_command(
        "scripts/smoke-bootstrap-project.py",
        "--runtime-root",
        cycle_dir / "bootstrap-smoke",
        "--report",
        cycle_dir / "reports" / "bootstrap-smoke.json",
    )
    command_specs.append(("Windows generated bootstrap smoke", "local", command, display, cycle_dir / "reports" / "bootstrap-smoke.json"))

    command, display = python_command(
        "scripts/smoke-verify-project.py",
        "--runtime-root",
        cycle_dir / "verify-project-smoke",
        "--report",
        cycle_dir / "reports" / "verify-project-smoke.json",
    )
    command_specs.append(("Windows verifier and drift smoke", "local", command, display, cycle_dir / "reports" / "verify-project-smoke.json"))

    command, display = python_command(
        "scripts/smoke-windows-wiring-git-safety.py",
        "--runtime-root",
        cycle_dir / "windows-wiring-git-safety",
        "--report",
        cycle_dir / "reports" / "windows-wiring-git-safety.json",
    )
    command_specs.append(("Windows wiring Git safety smoke", "local", command, display, cycle_dir / "reports" / "windows-wiring-git-safety.json"))

    command, display = python_command("scripts/windows-lab-probe.py", "--workspace", workspace, "dry-run", "--sample", "--json")
    command_specs.append(("Windows lab sample dry-run", "local", command, display, None))

    command, display = python_command(
        "scripts/windows-runtime-wiring-probe.py",
        "--workspace",
        workspace,
        "dry-run",
        "--sample",
        "--json",
    )
    command_specs.append(("Windows runtime wiring sample dry-run", "local", command, display, None))

    return [
        run_child(
            name=name,
            category=category,
            command=command,
            display_command=display,
            cwd=workspace,
            raw_dir=raw_dir,
            workspace=workspace,
            report_path=report_path,
        )
        for name, category, command, display, report_path in command_specs
    ]


def live_items(cycle_dir: Path, workspace: Path, inventory: Path, timeout: float) -> list[MatrixItem]:
    raw_dir = cycle_dir / "raw"
    output_root = relpath(cycle_dir / "live", workspace)
    run_id = cycle_dir.name

    lab_command, lab_display = python_command(
        "scripts/windows-lab-probe.py",
        "--workspace",
        workspace,
        "run",
        "--inventory",
        inventory,
        "--output-root",
        Path(output_root) / "lab",
        "--run-id",
        run_id,
        "--timeout",
        f"{timeout:g}",
        "--json",
    )
    runtime_command, runtime_display = python_command(
        "scripts/windows-runtime-wiring-probe.py",
        "--workspace",
        workspace,
        "run",
        "--inventory",
        inventory,
        "--output-root",
        Path(output_root) / "runtime-wiring",
        "--run-id",
        run_id,
        "--timeout",
        f"{timeout:g}",
        "--json",
    )
    return [
        run_child(
            name="Windows lab live readiness",
            category="live",
            command=lab_command,
            display_command=lab_display,
            cwd=workspace,
            raw_dir=raw_dir,
            workspace=workspace,
            timeout=max(timeout + 30.0, 120.0),
        ),
        run_child(
            name="Windows runtime wiring live smoke",
            category="live",
            command=runtime_command,
            display_command=runtime_display,
            cwd=workspace,
            raw_dir=raw_dir,
            workspace=workspace,
            timeout=max(timeout + 60.0, 180.0),
        ),
    ]


def skipped_live_item() -> MatrixItem:
    return MatrixItem(
        name="Windows live two-host smoke",
        category="live",
        status="not-run",
        command="python3 scripts/smoke-windows-matrix.py --live --inventory internal/windows-lab-inventory.json",
        exit_code=None,
        message="live mode not requested; record an explicit caveat before claiming two-host coverage",
        evidence={"expected_hosts": list(EXPECTED_HOST_IDS)},
    )


def run_cycle(args: argparse.Namespace, run_dir: Path, cycle: str, workspace: Path) -> list[MatrixItem]:
    cycle_dir = run_dir / cycle
    items = local_items(cycle_dir, workspace)
    if args.live:
        items.extend(live_items(cycle_dir, workspace, args.inventory, args.timeout))
    else:
        items.append(skipped_live_item())
    return items


def repeat_mismatches(primary: list[MatrixItem], repeat: list[MatrixItem]) -> list[dict[str, str]]:
    primary_status = {item.name: item.status for item in primary}
    repeat_status = {item.name: item.status for item in repeat}
    mismatches: list[dict[str, str]] = []
    for name in sorted(set(primary_status) | set(repeat_status)):
        if primary_status.get(name) != repeat_status.get(name):
            mismatches.append(
                {
                    "name": name,
                    "primary": primary_status.get(name, "missing"),
                    "repeat": repeat_status.get(name, "missing"),
                }
            )
    return mismatches


def build_report(args: argparse.Namespace) -> dict[str, object]:
    workspace = args.workspace.resolve(strict=False)
    run_id = args.run_id or utc_run_id()
    run_dir = (workspace / args.runtime_root / run_id).resolve(strict=False)
    run_dir.mkdir(parents=True, exist_ok=True)
    primary = run_cycle(args, run_dir, "primary", workspace)
    repeat: list[MatrixItem] = []
    mismatches: list[dict[str, str]] = []
    if args.repeat:
        repeat = run_cycle(args, run_dir, "repeat", workspace)
        mismatches = repeat_mismatches(primary, repeat)
    all_items = primary + repeat
    failed = sum(1 for item in all_items if item.status == "fail")
    not_run = sum(1 for item in all_items if item.status == "not-run")
    status = "fail" if failed or mismatches else "pass"
    report: dict[str, object] = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": "live" if args.live else "local",
        "repeat": bool(args.repeat),
        "status": status,
        "run_id": run_id,
        "runtime": {"report_dir": relpath(run_dir, workspace)},
        "summary": {
            "status": status,
            "total": len(all_items),
            "passed": sum(1 for item in all_items if item.status == "pass"),
            "failed": failed,
            "not_run": not_run,
            "live_status": "requested" if args.live else "not-run",
            "expected_hosts": list(EXPECTED_HOST_IDS),
            "repeat_mismatches": len(mismatches),
        },
        "items": [asdict(item) for item in all_items],
        "repeat_mismatches": mismatches,
    }
    report_path = args.report or run_dir / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_path"] = relpath(report_path, workspace)
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the aggregate Windows support smoke matrix.")
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--run-id")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--live", action="store_true", help="Run live Windows host probes from ignored inventory.")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--repeat", action="store_true", help="Run the matrix twice and report status mismatches.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args)
    summary = report["summary"]
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"report: {report['report_path']}")
        print(
            "summary: "
            f"{summary['status']} "
            f"({summary['passed']}/{summary['total']} passed, "
            f"{summary['failed']} failed, {summary['not_run']} not-run)"
        )
        for item in report["items"]:
            if item["status"] != "pass":
                print(f"{item['status'].upper()} {item['name']}: {item['message']}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
