#!/usr/bin/env python3
"""Run sanitized native Windows lab readiness probes."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "changerail.windows-lab-report.v1"
EXPECTED_HOST_IDS = ("windows-host-a", "windows-host-b")
DEFAULT_INVENTORY = Path("internal/windows-lab-inventory.json")
DEFAULT_RUNTIME_ROOT = Path(".runtime/changerail/windows-lab")
FIXTURE_TEXT = "ChangeRail Windows lab fixture\n"
SECRET_KEY_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential)")
WINDOWS_HOME_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+")
POSIX_HOME_RE = re.compile(r"(?:/home|/Users)/[A-Za-z0-9._-]+")
SSH_TARGET_RE = re.compile(r"(?:(?P<user>[A-Za-z0-9._-]+)@)?(?P<host>[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+)")


class ProbeError(Exception):
    pass


@dataclass
class HostConfig:
    id: str
    ssh_command: str
    disposable_root: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def compact(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def sanitize_detail(value: str) -> str:
    redacted = SECRET_KEY_RE.sub("credential", value)
    redacted = WINDOWS_HOME_RE.sub("<windows-home>", redacted)
    redacted = POSIX_HOME_RE.sub("<home>", redacted)
    redacted = SSH_TARGET_RE.sub("<host>", redacted)
    return compact(redacted)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProbeError(f"inventory not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ProbeError(f"inventory JSON is invalid: {exc}") from exc


def sample_inventory() -> dict[str, Any]:
    return {
        "schema": "changerail.windows-lab-inventory.v1",
        "notes": "public sample inventory; do not use for live probes",
        "hosts": [
            {
                "id": "windows-host-a",
                "ssh_command": "ssh windows-host-a",
                "disposable_root": "C:/Temp/changerail-lab-a",
            },
            {
                "id": "windows-host-b",
                "ssh_command": "ssh windows-host-b",
                "disposable_root": "C:/Temp/changerail-lab-b",
            },
        ],
    }


def parse_inventory(data: Any) -> list[HostConfig]:
    if not isinstance(data, dict):
        raise ProbeError("inventory must be a JSON object")
    hosts = data.get("hosts")
    if not isinstance(hosts, list):
        raise ProbeError("inventory.hosts must be an array")
    parsed: list[HostConfig] = []
    errors: list[str] = []
    for index, host in enumerate(hosts):
        label = f"hosts[{index}]"
        if not isinstance(host, dict):
            errors.append(f"{label} must be an object")
            continue
        host_id = host.get("id")
        ssh_command = host.get("ssh_command")
        disposable_root = host.get("disposable_root")
        if not isinstance(host_id, str) or not host_id:
            errors.append(f"{label}.id must be a non-empty string")
        if not isinstance(ssh_command, str) or not ssh_command:
            errors.append(f"{label}.ssh_command must be a non-empty string")
        if not isinstance(disposable_root, str) or not disposable_root:
            errors.append(f"{label}.disposable_root must be a non-empty string")
        if all(isinstance(value, str) and value for value in (host_id, ssh_command, disposable_root)):
            parsed.append(HostConfig(host_id, ssh_command, disposable_root))
    ids = [host.id for host in parsed]
    if sorted(ids) != sorted(EXPECTED_HOST_IDS):
        errors.append(f"inventory hosts must be exactly {', '.join(EXPECTED_HOST_IDS)}")
    if len(ids) != len(set(ids)):
        errors.append("inventory host ids must be unique")
    for host in parsed:
        try:
            shlex.split(host.ssh_command)
        except ValueError as exc:
            errors.append(f"{host.id}.ssh_command cannot be parsed: {exc}")
    if errors:
        raise ProbeError("; ".join(errors))
    return sorted(parsed, key=lambda host: host.id)


def ensure_ignored(path: Path, workspace: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(workspace), "check-ignore", "-q", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def remote_script(host: HostConfig, probe_id: str) -> str:
    root = json.dumps(host.disposable_root)
    run = json.dumps(probe_id)
    fixture = json.dumps(FIXTURE_TEXT)
    return rf"""
$ErrorActionPreference = "Stop"
try {{
  [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
  $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
}} catch {{
}}
$root = {root}
$probeId = {run}
$fixtureInput = {fixture}
$probeRoot = Join-Path -Path $root -ChildPath ("changerail-" + $probeId)
$fixturePath = Join-Path -Path $probeRoot -ChildPath "fixture.txt"
$status = "passed"
$errorMessage = $null
$cleanup = "not_started"
$result = [ordered]@{{}}
try {{
  New-Item -ItemType Directory -Path $probeRoot -Force | Out-Null
  if ([string]::IsNullOrEmpty($fixtureInput)) {{
    throw "fixture input was empty"
  }}
  $utf8 = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($fixturePath, $fixtureInput, $utf8)
  $fixtureHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $fixturePath).Hash.ToLowerInvariant()

  $os = Get-CimInstance Win32_OperatingSystem | Select-Object -First 1 Caption, Version, BuildNumber, OSArchitecture
  $drive = (Get-Item -LiteralPath $probeRoot).PSDrive.Name
  $filesystem = "unknown"
  try {{
    $volume = Get-Volume -DriveLetter $drive -ErrorAction Stop
    if ($volume.FileSystem) {{
      $filesystem = [string]$volume.FileSystem
    }}
  }} catch {{
    $filesystem = "unknown"
  }}

  function Read-Version($command, [string[]]$arguments) {{
    try {{
      $cmd = Get-Command $command -ErrorAction Stop
      $output = & $cmd.Source @arguments 2>&1 | Select-Object -First 1
      return [ordered]@{{ status = "available"; value = ([string]$output).Trim() }}
    }} catch {{
      return [ordered]@{{ status = "unavailable"; value = "unavailable" }}
    }}
  }}

  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  $developerMode = "unknown"
  try {{
    $dev = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -ErrorAction Stop
    if ($dev.AllowDevelopmentWithoutDevLicense -eq 1) {{ $developerMode = "enabled" }} else {{ $developerMode = "disabled" }}
  }} catch {{
    $developerMode = "unknown"
  }}

  $result["capabilities"] = [ordered]@{{
    os = [ordered]@{{
      caption = [string]$os.Caption
      version = [string]$os.Version
      build = [string]$os.BuildNumber
      architecture = [string]$os.OSArchitecture
    }}
    filesystem = [ordered]@{{ disposable_root_drive = "present"; type = $filesystem }}
    git = Read-Version "git" @("--version")
    python = [ordered]@{{
      python = Read-Version "python" @("--version")
      py_launcher = Read-Version "py" @("-3", "--version")
    }}
    shell = [ordered]@{{
      powershell = $PSVersionTable.PSVersion.ToString()
      edition = [string]$PSVersionTable.PSEdition
    }}
    privilege = [ordered]@{{
      elevated = $isAdmin
      developer_mode = $developerMode
    }}
  }}
  $result["checks"] = [ordered]@{{
    ssh = "passed"
    non_interactive = "passed"
    disposable_root = "passed"
    fixture_transfer = "passed"
    fixture_sha256 = $fixtureHash
  }}
}} catch {{
  $status = "failed"
  $errorMessage = $_.Exception.Message
}} finally {{
  try {{
    if (Test-Path -LiteralPath $probeRoot) {{
      Remove-Item -LiteralPath $probeRoot -Recurse -Force
    }}
    $cleanup = "passed"
  }} catch {{
    $cleanup = "failed"
    if ($status -eq "passed") {{
      $status = "failed"
      $errorMessage = $_.Exception.Message
    }}
  }}
}}
$result["schema"] = "changerail.windows-lab-host-result.v1"
$result["status"] = $status
$result["cleanup"] = $cleanup
if ($errorMessage) {{
  $result["error"] = $errorMessage
}}
$result | ConvertTo-Json -Depth 10 -Compress
if ($status -ne "passed") {{ exit 1 }}
"""


def summarize_host_result(host_id: str, result: dict[str, Any]) -> dict[str, Any]:
    capabilities = result.get("capabilities") if isinstance(result.get("capabilities"), dict) else {}
    checks = result.get("checks") if isinstance(result.get("checks"), dict) else {}
    return {
        "id": host_id,
        "status": result.get("status", "failed"),
        "checks": {
            "ssh": checks.get("ssh", "failed"),
            "non_interactive": checks.get("non_interactive", "failed"),
            "disposable_root": checks.get("disposable_root", "failed"),
            "fixture_transfer": checks.get("fixture_transfer", "failed"),
            "cleanup": result.get("cleanup", "unknown"),
        },
        "capabilities": {
            "os": capabilities.get("os", {}),
            "filesystem": capabilities.get("filesystem", {}),
            "git": capabilities.get("git", {"status": "unknown", "value": "unknown"}),
            "python": capabilities.get("python", {}),
            "shell": capabilities.get("shell", {}),
            "privilege": capabilities.get("privilege", {}),
        },
    }


def run_host(host: HostConfig, probe_id: str, output_dir: Path, timeout: float) -> dict[str, Any]:
    ssh_argv = shlex.split(host.ssh_command)
    script = remote_script(host, probe_id)
    wrapper = (
        "$s=[Console]::In.ReadToEnd(); "
        "$p=[IO.Path]::GetTempFileName()+'.ps1'; "
        "[IO.File]::WriteAllText($p,$s,[Text.UTF8Encoding]::new($false)); "
        "try { & powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $p; "
        "exit $LASTEXITCODE } finally { "
        "Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue }"
    )
    quoted_wrapper = wrapper.replace('"', '`"')
    remote_command = (
        'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass '
        f'-Command "{quoted_wrapper}"'
    )
    command = ssh_argv + [remote_command]
    started = utc_now()
    started_clock = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / f"{host.id}.txt"
    try:
        completed = subprocess.run(
            command,
            input=script.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        duration = round(time.monotonic() - started_clock, 3)
        stdout = completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raw_path.write_text(
            "[stdout]\n"
            + stdout
            + "\n[stderr]\n"
            + stderr
            + f"\n[exit_code] {completed.returncode}\n",
            encoding="utf-8",
        )
        try:
            payload = json.loads(stdout.strip().splitlines()[-1])
            if not isinstance(payload, dict):
                raise ValueError("host payload is not an object")
            summary = summarize_host_result(host.id, payload)
        except (IndexError, json.JSONDecodeError, ValueError):
            summary = {
                "id": host.id,
                "status": "failed",
                "checks": {
                    "ssh": "failed",
                    "non_interactive": "failed",
                    "disposable_root": "unknown",
                    "fixture_transfer": "unknown",
                    "cleanup": "unknown",
                },
                "capabilities": {},
                "diagnostic": "remote command did not return sanitized JSON; see ignored raw output",
            }
        if completed.returncode != 0 and summary.get("status") == "passed":
            summary["status"] = "failed"
        if completed.returncode != 0 and "diagnostic" not in summary:
            summary["diagnostic"] = "remote command failed; see ignored raw output"
        summary["evidence"] = {
            "raw_output_path": raw_path.as_posix(),
            "started_at": started,
            "duration_seconds": duration,
        }
        return summary
    except subprocess.TimeoutExpired as exc:
        duration = round(time.monotonic() - started_clock, 3)
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        raw_path.write_text("[stdout]\n" + stdout + "\n[stderr]\n" + stderr + "\n[timeout]\n", encoding="utf-8")
        return {
            "id": host.id,
            "status": "failed",
            "checks": {
                "ssh": "unknown",
                "non_interactive": "timeout",
                "disposable_root": "unknown",
                "fixture_transfer": "unknown",
                "cleanup": "unknown",
            },
            "capabilities": {},
            "diagnostic": f"remote command timed out after {timeout:g} seconds",
            "evidence": {
                "raw_output_path": raw_path.as_posix(),
                "started_at": started,
                "duration_seconds": duration,
            },
        }


def build_report(
    *,
    mode: str,
    hosts: list[HostConfig],
    host_results: list[dict[str, Any]],
    runtime_dir: Path | None,
    workspace: Path,
    inventory_ignored: bool | str,
) -> dict[str, Any]:
    status = "passed" if all(result.get("status") == "passed" for result in host_results) else "failed"
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": mode,
        "status": status,
        "summary": {
            "host_count": len(hosts),
            "passed": sum(1 for result in host_results if result.get("status") == "passed"),
            "failed": sum(1 for result in host_results if result.get("status") != "passed"),
            "inventory_ignored": inventory_ignored,
            "host_ids": [host.id for host in hosts],
        },
        "hosts": host_results,
    }
    if runtime_dir is not None:
        report["runtime"] = {"report_dir": relpath(runtime_dir, workspace)}
    return report


def dry_run(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    data = sample_inventory() if args.sample else load_json(args.inventory)
    hosts = parse_inventory(data)
    inventory_ignored: bool | str = "sample"
    if not args.sample:
        inventory_ignored = ensure_ignored(args.inventory, workspace)
        if not inventory_ignored:
            raise ProbeError("inventory must be ignored by Git")
    host_results = [
        {
            "id": host.id,
            "status": "passed",
            "checks": {
                "inventory_schema": "passed",
                "ssh_command_present": "passed",
                "disposable_root_present": "passed",
            },
            "capabilities": {},
        }
        for host in hosts
    ]
    report = build_report(
        mode="dry-run",
        hosts=hosts,
        host_results=host_results,
        runtime_dir=None,
        workspace=workspace,
        inventory_ignored=inventory_ignored,
    )
    print(json.dumps(report if args.json else report["summary"], ensure_ascii=False, indent=2))
    return 0


def run_live(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    inventory = args.inventory
    data = load_json(inventory)
    hosts = parse_inventory(data)
    if not ensure_ignored(inventory, workspace):
        raise ProbeError("inventory must be ignored by Git")
    probe_id = args.run_id or run_id()
    runtime_dir = (workspace / args.output_root / probe_id).resolve(strict=False)
    raw_dir = runtime_dir / "raw"
    host_results = [run_host(host, probe_id, raw_dir, args.timeout) for host in hosts]
    for result in host_results:
        evidence = result.get("evidence")
        if isinstance(evidence, dict) and isinstance(evidence.get("raw_output_path"), str):
            evidence["raw_output_path"] = relpath(Path(evidence["raw_output_path"]), workspace)
        if isinstance(result.get("diagnostic"), str):
            result["diagnostic"] = sanitize_detail(result["diagnostic"])
    report = build_report(
        mode="live",
        hosts=hosts,
        host_results=host_results,
        runtime_dir=runtime_dir,
        workspace=workspace,
        inventory_ignored=True,
    )
    write_json(runtime_dir / "report.json", report)
    payload = {
        "ok": report["status"] == "passed",
        "schema": SCHEMA,
        "status": report["status"],
        "report_path": relpath(runtime_dir / "report.json", workspace),
        "summary": report["summary"],
        "hosts": [
            {
                "id": result["id"],
                "status": result["status"],
                "checks": result.get("checks", {}),
                "capabilities": result.get("capabilities", {}),
                **({"diagnostic": result["diagnostic"]} if "diagnostic" in result else {}),
            }
            for result in host_results
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)

    dry = subparsers.add_parser("dry-run", help="validate inventory/report shape without SSH")
    dry.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    dry.add_argument("--sample", action="store_true")
    dry.add_argument("--json", action="store_true")
    dry.set_defaults(func=dry_run)

    live = subparsers.add_parser("run", help="run live non-destructive probes over SSH")
    live.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    live.add_argument("--output-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    live.add_argument("--run-id")
    live.add_argument("--timeout", type=float, default=60.0)
    live.add_argument("--json", action="store_true")
    live.set_defaults(func=run_live)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ProbeError as exc:
        payload = {
            "ok": False,
            "schema": SCHEMA,
            "status": "failed",
            "diagnostic": sanitize_detail(str(exc)),
        }
        if getattr(args, "json", False):
            print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        else:
            print(f"error: {payload['diagnostic']}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
