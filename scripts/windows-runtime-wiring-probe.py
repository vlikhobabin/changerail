#!/usr/bin/env python3
"""Run sanitized native Windows runtime, wiring and Git behavior probes."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "changerail.windows-runtime-wiring-report.v1"
HOST_SCHEMA = "changerail.windows-runtime-wiring-host-result.v1"
EXPECTED_HOST_IDS = ("windows-host-a", "windows-host-b")
DEFAULT_INVENTORY = Path("internal/windows-lab-inventory.json")
DEFAULT_RUNTIME_ROOT = Path(".runtime/changerail/windows-runtime-wiring")
SECRET_KEY_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential)")
WINDOWS_HOME_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+")
WINDOWS_ABS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"']+")
POSIX_HOME_RE = re.compile(r"(?:/home|/Users)/[A-Za-z0-9._-]+")
SSH_TARGET_RE = re.compile(r"(?P<user>[A-Za-z0-9._-]+)@(?P<host>[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+)")
CHECK_NAMES = (
    "direct_os_symlink_directory",
    "direct_os_symlink_file",
    "direct_os_symlink_without_elevation",
    "junction_directory",
    "generated_copy_drift_detection",
    "generated_copy_source_update_behavior",
    "extensionless_direct_launch",
    "cmd_wrapper_launch",
    "powershell_wrapper_launch",
    "python_wrapper_launch",
    "explicit_bash_launch",
    "git_status_porcelain",
    "git_add_dry_run",
    "git_index_inspection",
)


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


def compact(value: str, limit: int = 220) -> str:
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
    host_schema = json.dumps(HOST_SCHEMA)
    return rf"""
$ErrorActionPreference = "Stop"
try {{
  [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
  $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
}} catch {{
}}

$root = {root}
$probeId = {run}
$hostSchema = {host_schema}
$probeRoot = Join-Path -Path $root -ChildPath ("changerail-runtime-wiring-" + $probeId)
$sourceRoot = Join-Path -Path $probeRoot -ChildPath "source"
$consumerRoot = Join-Path -Path $probeRoot -ChildPath "consumer"
$sourceSkill = Join-Path -Path $sourceRoot -ChildPath "skills\changerail-ff"
$sourceSkillFile = Join-Path -Path $sourceSkill -ChildPath "SKILL.md"
$sourceBin = Join-Path -Path $sourceRoot -ChildPath "bin"
$consumerSkills = Join-Path -Path $consumerRoot -ChildPath ".codex\skills"
$consumerBin = Join-Path -Path $consumerRoot -ChildPath "bin"
  $status = "passed"
  $setupError = $null
  $cleanup = "not_started"
  $checks = New-Object System.Collections.ArrayList
  Write-Output "progress: fixture-start"

function Add-Check([string]$Name, [string]$Category, [string]$Status, [string]$Message, [hashtable]$Details) {{
  $payload = [ordered]@{{
    name = $Name
    category = $Category
    status = $Status
    message = $Message
    details = [ordered]@{{}}
  }}
  if ($Details) {{
    foreach ($key in $Details.Keys) {{
      $payload.details[$key] = $Details[$key]
    }}
  }}
  [void]$script:checks.Add($payload)
}}

function First-Line([object[]]$Lines) {{
  if ($null -eq $Lines -or $Lines.Count -eq 0) {{ return "" }}
  return ([string]$Lines[0]).Trim()
}}

function Command-Version([string]$Command, [string[]]$Arguments) {{
  try {{
    $cmd = Get-Command $Command -ErrorAction Stop
    $output = & $cmd.Source @Arguments 2>&1 | Select-Object -First 1
    return [ordered]@{{ status = "available"; command = $Command; value = ([string]$output).Trim(); source = [string]$cmd.Source }}
  }} catch {{
    return [ordered]@{{ status = "unavailable"; command = $Command; value = "unavailable" }}
  }}
}}

function Invoke-Native([string[]]$Argv) {{
  try {{
    $output = & $Argv[0] @($Argv[1..($Argv.Count - 1)]) 2>&1
    return [ordered]@{{
      ok = ($LASTEXITCODE -eq 0)
      exit_code = $LASTEXITCODE
      output = ($output -join "`n")
    }}
  }} catch {{
    return [ordered]@{{
      ok = $false
      exit_code = -1
      output = $_.Exception.Message
    }}
  }}
}}

function Invoke-PythonJson([string]$PythonExe, [string[]]$Arguments) {{
  $output = & $PythonExe @Arguments 2>&1
  $exit = $LASTEXITCODE
  try {{
    $payload = ($output | Select-Object -Last 1) | ConvertFrom-Json
  }} catch {{
    $payload = [ordered]@{{ ok = $false; error = "invalid JSON from helper"; stdout = ($output -join "`n") }}
  }}
  return [ordered]@{{ exit_code = $exit; payload = $payload }}
}}

function Hash-File([string]$Path) {{
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}}

try {{
  New-Item -ItemType Directory -Path $sourceSkill -Force | Out-Null
  New-Item -ItemType Directory -Path $sourceBin -Force | Out-Null
  New-Item -ItemType Directory -Path $consumerSkills -Force | Out-Null
  New-Item -ItemType Directory -Path $consumerBin -Force | Out-Null

  [IO.File]::WriteAllText($sourceSkillFile, "name: changerail-ff`nversion: source-v1`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $sourceBin "openspec"), "#!/usr/bin/env bash`necho wrapper-extensionless`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $sourceBin "openspec.cmd"), "@echo off`r`necho wrapper-cmd`r`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $sourceBin "openspec.ps1"), "Write-Output 'wrapper-powershell'`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $sourceBin "openspec.py"), "print('wrapper-python')`n", [Text.UTF8Encoding]::new($false))

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

  $pythonVersion = Command-Version "python" @("--version")
  if ($pythonVersion.status -ne "available") {{
    throw "python is unavailable on PATH"
  }}
  $pythonExe = [string](Get-Command "python" -ErrorAction Stop).Source
  $gitVersion = Command-Version "git" @("--version")
  $bashVersion = Command-Version "bash" @("--version")

  $symlinkHelper = Join-Path $probeRoot "make_symlink.py"
  [IO.File]::WriteAllText($symlinkHelper, @'
import json
import os
import sys

target, link, kind = sys.argv[1:4]
try:
    os.symlink(target, link, target_is_directory=(kind == "dir"))
    print(json.dumps({{"ok": True}}))
except Exception as exc:
    print(json.dumps({{"ok": False, "error": f"{{exc.__class__.__name__}}: {{exc}}"}}))
    sys.exit(1)
'@, [Text.UTF8Encoding]::new($false))

  $launcherHelper = Join-Path $probeRoot "launch_wrapper.py"
  [IO.File]::WriteAllText($launcherHelper, @'
import json
import subprocess
import sys

cmd = sys.argv[1:]
try:
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15, check=False)
    print(json.dumps({{
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }}))
    sys.exit(0 if completed.returncode == 0 else 1)
except Exception as exc:
    print(json.dumps({{"ok": False, "error": f"{{exc.__class__.__name__}}: {{exc}}"}}))
    sys.exit(1)
'@, [Text.UTF8Encoding]::new($false))

  $directorySymlink = Join-Path $consumerSkills "changerail-ff-link"
  $dirLink = Invoke-PythonJson $pythonExe @($symlinkHelper, $sourceSkill, $directorySymlink, "dir")
  if ($dirLink.payload.ok -eq $true) {{
    Add-Check "direct_os_symlink_directory" "filesystem" "passed" "direct Python os.symlink created a directory link" @{{ link_type = "directory"; token_elevated = $isAdmin; developer_mode = $developerMode }}
  }} else {{
    Add-Check "direct_os_symlink_directory" "filesystem" "failed" ([string]$dirLink.payload.error) @{{ link_type = "directory"; token_elevated = $isAdmin; developer_mode = $developerMode }}
  }}

  $fileSymlink = Join-Path $consumerBin "openspec-link"
  $fileLink = Invoke-PythonJson $pythonExe @($symlinkHelper, (Join-Path $sourceBin "openspec"), $fileSymlink, "file")
  if ($fileLink.payload.ok -eq $true) {{
    Add-Check "direct_os_symlink_file" "filesystem" "passed" "direct Python os.symlink created a file link" @{{ link_type = "file"; token_elevated = $isAdmin; developer_mode = $developerMode }}
  }} else {{
    Add-Check "direct_os_symlink_file" "filesystem" "failed" ([string]$fileLink.payload.error) @{{ link_type = "file"; token_elevated = $isAdmin; developer_mode = $developerMode }}
  }}

  if ($isAdmin) {{
    Add-Check "direct_os_symlink_without_elevation" "filesystem" "not-applicable" "current SSH token reports elevated=true; harness did not request elevation, but this run cannot prove non-elevated Developer Mode symlink behavior" @{{ token_elevated = $true; developer_mode = $developerMode }}
  }} elseif ($developerMode -eq "enabled" -and $dirLink.payload.ok -eq $true -and $fileLink.payload.ok -eq $true) {{
    Add-Check "direct_os_symlink_without_elevation" "filesystem" "passed" "non-elevated token with Developer Mode created direct symlinks" @{{ token_elevated = $false; developer_mode = $developerMode }}
  }} else {{
    Add-Check "direct_os_symlink_without_elevation" "filesystem" "failed" "non-elevated direct symlink was unavailable" @{{ token_elevated = $false; developer_mode = $developerMode }}
  }}

  $junction = Join-Path $consumerSkills "changerail-ff-junction"
  try {{
    New-Item -ItemType Junction -Path $junction -Target $sourceSkill -Force | Out-Null
    Add-Check "junction_directory" "filesystem" "passed" "PowerShell created a directory junction" @{{ link_type = "junction" }}
  }} catch {{
    Add-Check "junction_directory" "filesystem" "failed" $_.Exception.Message @{{ link_type = "junction" }}
  }}

  $copy = Join-Path $consumerSkills "changerail-ff-copy"
  Copy-Item -LiteralPath $sourceSkill -Destination $copy -Recurse -Force
  $copyFile = Join-Path $copy "SKILL.md"
  $copyHashV1 = Hash-File $copyFile
  [IO.File]::WriteAllText($sourceSkillFile, "name: changerail-ff`nversion: source-v2`n", [Text.UTF8Encoding]::new($false))
  $sourceHashV2 = Hash-File $sourceSkillFile
  $copyHashAfterSourceUpdate = Hash-File $copyFile
  if ($copyHashAfterSourceUpdate -ne $sourceHashV2) {{
    Add-Check "generated_copy_drift_detection" "generated-copy" "passed" "generated copy stayed stale after source update, so drift is detectable by hash comparison" @{{ initial_copy_hash = $copyHashV1; copy_stale_after_source_update = $true }}
  }} else {{
    Add-Check "generated_copy_drift_detection" "generated-copy" "failed" "generated copy changed without explicit refresh" @{{ copy_stale_after_source_update = $false }}
  }}
  Remove-Item -LiteralPath $copy -Recurse -Force
  Copy-Item -LiteralPath $sourceSkill -Destination $copy -Recurse -Force
  $copyHashAfterRefresh = Hash-File $copyFile
  if ($copyHashAfterRefresh -eq $sourceHashV2) {{
    Add-Check "generated_copy_source_update_behavior" "generated-copy" "passed" "generated copy required an explicit refresh to pick up source updates" @{{ update_model = "manual-refresh-required" }}
  }} else {{
    Add-Check "generated_copy_source_update_behavior" "generated-copy" "failed" "generated copy refresh did not match source" @{{ update_model = "refresh-failed" }}
  }}

  function Add-LaunchCheck([string]$Name, [string[]]$Argv, [string]$Expected) {{
    $launch = Invoke-PythonJson $pythonExe @(@($launcherHelper) + $Argv)
    if ($launch.payload.ok -eq $true -and ([string]$launch.payload.stdout).Contains($Expected)) {{
      Add-Check $Name "runtime" "passed" "wrapper invocation returned expected marker" @{{ exit_code = $launch.payload.exit_code; marker = $Expected }}
    }} else {{
      $reason = [string]$launch.payload.error
      if ([string]::IsNullOrEmpty($reason)) {{ $reason = ([string]$launch.payload.stderr + " " + [string]$launch.payload.stdout).Trim() }}
      Add-Check $Name "runtime" "failed" $reason @{{ exit_code = $launch.payload.exit_code; marker = $Expected }}
    }}
  }}

  Add-LaunchCheck "extensionless_direct_launch" @((Join-Path $sourceBin "openspec")) "wrapper-extensionless"
  Add-LaunchCheck "cmd_wrapper_launch" @((Join-Path $sourceBin "openspec.cmd")) "wrapper-cmd"
  Add-LaunchCheck "powershell_wrapper_launch" @("powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $sourceBin "openspec.ps1")) "wrapper-powershell"
  Add-LaunchCheck "python_wrapper_launch" @($pythonExe, (Join-Path $sourceBin "openspec.py")) "wrapper-python"
  if ($bashVersion.status -eq "available") {{
    Add-LaunchCheck "explicit_bash_launch" @("bash", (Join-Path $sourceBin "openspec")) "wrapper-extensionless"
  }} else {{
    Add-Check "explicit_bash_launch" "runtime" "unsupported" "bash is unavailable on PATH" @{{ prerequisite = "bash" }}
  }}

  if ($gitVersion.status -eq "available") {{
    [void](Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "init")))
    [void](Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "config", "core.autocrlf", "false")))
    [void](Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "config", "user.email", "changerail@example.invalid")))
    [void](Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "config", "user.name", "ChangeRail Probe")))
    $porcelainResult = Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "status", "--porcelain=v1", "--untracked-files=all"))
    $porcelainExit = [int]$porcelainResult.payload.exit_code
    $porcelainText = (([string]$porcelainResult.payload.stdout) + "`n" + ([string]$porcelainResult.payload.stderr)).Trim()
    $porcelain = @()
    if (-not [string]::IsNullOrEmpty($porcelainText)) {{ $porcelain = $porcelainText -split "`n" }}
    $gitStatusDetails = @{{
      exit_code = $porcelainExit
      safe = ($porcelainExit -eq 0)
      unsafe_paths = @()
      entry_count = @($porcelain).Count
      mentions_directory_symlink = $porcelainText.Contains(".codex/skills/changerail-ff-link")
      mentions_file_symlink = $porcelainText.Contains("bin/openspec-link")
      mentions_junction = $porcelainText.Contains(".codex/skills/changerail-ff-junction")
      mentions_generated_copy = $porcelainText.Contains(".codex/skills/changerail-ff-copy")
    }}
    if ($porcelainExit -eq 0) {{
      Add-Check "git_status_porcelain" "git" "passed" "git status --porcelain completed" $gitStatusDetails
    }} else {{
      Add-Check "git_status_porcelain" "git" "failed" (First-Line $porcelain) $gitStatusDetails
    }}

    $dryRunResult = Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "add", "--dry-run", "."))
    $dryRunExit = [int]$dryRunResult.payload.exit_code
    $dryRunText = (([string]$dryRunResult.payload.stdout) + "`n" + ([string]$dryRunResult.payload.stderr)).Trim()
    $dryRun = @()
    if (-not [string]::IsNullOrEmpty($dryRunText)) {{ $dryRun = $dryRunText -split "`n" }}
    $dryRunDetails = @{{
      exit_code = $dryRunExit
      safe = ($dryRunExit -eq 0)
      unsafe_paths = @()
      entry_count = @($dryRun).Count
      mentions_directory_symlink = $dryRunText.Contains(".codex/skills/changerail-ff-link")
      mentions_file_symlink = $dryRunText.Contains("bin/openspec-link")
      mentions_junction = $dryRunText.Contains(".codex/skills/changerail-ff-junction")
      mentions_generated_copy = $dryRunText.Contains(".codex/skills/changerail-ff-copy")
    }}
    if ($dryRunExit -eq 0) {{
      Add-Check "git_add_dry_run" "git" "passed" "git add --dry-run completed" $dryRunDetails
    }} else {{
      Add-Check "git_add_dry_run" "git" "failed" (First-Line $dryRun) $dryRunDetails
    }}

    $addResult = Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "add", "."))
    $addExit = [int]$addResult.payload.exit_code
    $addOutputText = (([string]$addResult.payload.stdout) + "`n" + ([string]$addResult.payload.stderr)).Trim()
    $addOutput = @()
    if (-not [string]::IsNullOrEmpty($addOutputText)) {{ $addOutput = $addOutputText -split "`n" }}
    $indexResult = Invoke-PythonJson $pythonExe @(@($launcherHelper) + @("git", "-C", $consumerRoot, "ls-files", "--stage"))
    $indexExit = [int]$indexResult.payload.exit_code
    $indexText = (([string]$indexResult.payload.stdout) + "`n" + ([string]$indexResult.payload.stderr)).Trim()
    $index = @()
    if (-not [string]::IsNullOrEmpty($indexText)) {{ $index = $indexText -split "`n" }}
    $indexDetails = @{{
      git_add_exit_code = $addExit
      ls_files_exit_code = $indexExit
      safe = ($addExit -eq 0 -and $indexExit -eq 0)
      unsafe_paths = @()
      index_entry_count = @($index).Count
      has_directory_symlink_entry = $indexText.Contains(".codex/skills/changerail-ff-link")
      has_file_symlink_entry = $indexText.Contains("bin/openspec-link")
      has_junction_entry = $indexText.Contains(".codex/skills/changerail-ff-junction")
      has_generated_copy_entry = $indexText.Contains(".codex/skills/changerail-ff-copy")
      has_symlink_mode = $indexText.Contains("120000")
    }}
    if ($addExit -eq 0 -and $indexExit -eq 0) {{
      Add-Check "git_index_inspection" "git" "passed" "git add and git ls-files --stage completed" $indexDetails
    }} else {{
      $message = (First-Line $addOutput)
      if ([string]::IsNullOrEmpty($message)) {{ $message = First-Line $index }}
      Add-Check "git_index_inspection" "git" "failed" $message $indexDetails
    }}
  }} else {{
    Add-Check "git_status_porcelain" "git" "unsupported" "git is unavailable on PATH" @{{ prerequisite = "git" }}
    Add-Check "git_add_dry_run" "git" "unsupported" "git is unavailable on PATH" @{{ prerequisite = "git" }}
    Add-Check "git_index_inspection" "git" "unsupported" "git is unavailable on PATH" @{{ prerequisite = "git" }}
  }}
}} catch {{
  $status = "failed"
  $setupError = $_.Exception.Message
}} finally {{
  try {{
    foreach ($linkPath in @($directorySymlink, $junction)) {{
      if ($linkPath -and (Test-Path -LiteralPath $linkPath)) {{
        cmd /c rmdir "$linkPath" 2>$null | Out-Null
      }}
    }}
    if ($fileSymlink -and (Test-Path -LiteralPath $fileSymlink)) {{
      Remove-Item -LiteralPath $fileSymlink -Force -ErrorAction SilentlyContinue
    }}
    if (Test-Path -LiteralPath $probeRoot) {{
      Remove-Item -LiteralPath $probeRoot -Recurse -Force
    }}
    $cleanup = "passed"
  }} catch {{
    $cleanup = "failed"
    if ($status -eq "passed") {{
      $status = "failed"
      $setupError = $_.Exception.Message
    }}
  }}
}}

$result = [ordered]@{{
  schema = $hostSchema
  status = $status
  cleanup = $cleanup
  environment = [ordered]@{{
    privilege = [ordered]@{{ elevated = $isAdmin; developer_mode = $developerMode }}
    git = $gitVersion
    python = $pythonVersion
    bash = $bashVersion
    shell = [ordered]@{{ powershell = $PSVersionTable.PSVersion.ToString(); edition = [string]$PSVersionTable.PSEdition }}
  }}
  checks = $checks
}}
if ($setupError) {{
  $result["error"] = $setupError
}}
$result | ConvertTo-Json -Depth 20 -Compress
if ($status -ne "passed") {{ exit 1 }}
"""


def summarize_host_result(host_id: str, result: dict[str, Any]) -> dict[str, Any]:
    checks = result.get("checks") if isinstance(result.get("checks"), list) else []
    materialized_checks: list[dict[str, Any]] = []
    for check in checks:
        if isinstance(check, dict):
            materialized_checks.append(
                {
                    "name": check.get("name", "unknown"),
                    "category": check.get("category", "unknown"),
                    "status": check.get("status", "failed"),
                    "message": check.get("message", ""),
                    "details": check.get("details", {}),
                }
            )
    seen = {check["name"] for check in materialized_checks}
    for name in CHECK_NAMES:
        if name not in seen:
            materialized_checks.append(
                {
                    "name": name,
                    "category": "unknown",
                    "status": "failed",
                    "message": "remote result did not include this check",
                    "details": {},
                }
            )
    status_counts: dict[str, int] = {}
    for check in materialized_checks:
        status = str(check.get("status", "failed"))
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "id": host_id,
        "status": result.get("status", "failed"),
        "cleanup": result.get("cleanup", "unknown"),
        "environment": result.get("environment", {}),
        "summary": {
            "check_count": len(materialized_checks),
            "status_counts": status_counts,
        },
        "checks": sorted(materialized_checks, key=lambda check: str(check.get("name", ""))),
        **({"diagnostic": result["error"]} if isinstance(result.get("error"), str) else {}),
    }


def remote_python_script(host: HostConfig, probe_id: str) -> str:
    template = r'''
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import winreg

ROOT = __ROOT_JSON__
PROBE_ID = __PROBE_ID_JSON__
HOST_SCHEMA = __HOST_SCHEMA_JSON__
CHECK_NAMES = __CHECK_NAMES_JSON__

probe_root = Path(ROOT) / ("changerail-runtime-wiring-" + PROBE_ID)
source_root = probe_root / "source"
consumer_root = probe_root / "consumer"
source_skill = source_root / "skills" / "changerail-ff"
source_skill_file = source_skill / "SKILL.md"
source_bin = source_root / "bin"
consumer_skills = consumer_root / ".codex" / "skills"
consumer_bin = consumer_root / "bin"
directory_symlink = consumer_skills / "changerail-ff-link"
file_symlink = consumer_bin / "openspec-link"
junction = consumer_skills / "changerail-ff-junction"
checks = []


def add_check(name, category, status, message, details=None):
    checks.append(
        {
            "name": name,
            "category": category,
            "status": status,
            "message": message,
            "details": details or {},
        }
    )


def run_cmd(argv, timeout=15, cwd=None):
    try:
        completed = subprocess.run(
            [str(arg) for arg in argv],
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        return {
            "ok": False,
            "exit_code": -1,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "error": f"timeout after {timeout:g} seconds",
        }
    except Exception as exc:
        return {
            "ok": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def version(command, *args):
    result = run_cmd([command, *args], timeout=10)
    if result["ok"]:
        value = (result["stdout"] or result["stderr"]).splitlines()
        return {"status": "available", "command": command, "value": value[0] if value else "available"}
    return {"status": "unavailable", "command": command, "value": "unavailable"}


def first_line(text):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[0] if lines else ""


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_rmdir_link(path):
    try:
        if path.exists() or path.is_symlink():
            run_cmd(["cmd", "/c", "rmdir", str(path)], timeout=5)
    except Exception:
        pass


def cleanup_probe_root():
    safe_rmdir_link(directory_symlink)
    safe_rmdir_link(junction)
    try:
        if file_symlink.exists() or file_symlink.is_symlink():
            file_symlink.unlink()
    except Exception:
        pass
    if probe_root.exists():
        def clear_readonly(function, path, exc_info):
            try:
                os.chmod(path, 0o700)
                function(path)
            except Exception:
                pass

        try:
            shutil.rmtree(probe_root, onexc=lambda function, path, exc: clear_readonly(function, path, exc))
        except TypeError:
            shutil.rmtree(probe_root, onerror=clear_readonly)


def launch_check(name, argv, expected):
    result = run_cmd(argv, timeout=15)
    output = (result.get("stdout", "") + "\n" + result.get("stderr", "")).strip()
    if result["ok"] and expected in output:
        add_check(
            name,
            "runtime",
            "passed",
            "wrapper invocation returned expected marker",
            {"exit_code": result["exit_code"], "marker": expected},
        )
    else:
        add_check(
            name,
            "runtime",
            "failed",
            result.get("error") or first_line(output) or "wrapper invocation failed",
            {"exit_code": result["exit_code"], "marker": expected},
        )


def git_mentions(text, needle):
    return needle.replace("\\", "/") in text.replace("\\", "/")


status = "passed"
cleanup = "not_started"
error = None
environment = {}

try:
    cleanup_probe_root()
except Exception:
    pass

try:
    source_skill.mkdir(parents=True, exist_ok=True)
    source_bin.mkdir(parents=True, exist_ok=True)
    consumer_skills.mkdir(parents=True, exist_ok=True)
    consumer_bin.mkdir(parents=True, exist_ok=True)
    source_skill_file.write_text("name: changerail-ff\nversion: source-v1\n", encoding="utf-8")
    (source_bin / "openspec").write_text("#!/usr/bin/env bash\necho wrapper-extensionless\n", encoding="utf-8")
    (source_bin / "openspec.cmd").write_text("@echo off\r\necho wrapper-cmd\r\n", encoding="utf-8")
    (source_bin / "openspec.ps1").write_text("Write-Output 'wrapper-powershell'\n", encoding="utf-8")
    (source_bin / "openspec.py").write_text("print('wrapper-python')\n", encoding="utf-8")

    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        is_admin = False
    developer_mode = "unknown"
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AllowDevelopmentWithoutDevLicense")
            developer_mode = "enabled" if int(value) == 1 else "disabled"
    except Exception:
        developer_mode = "unknown"

    git_version = version("git", "--version")
    python_version = version("python", "--version")
    bash_version = version("bash", "--version")
    powershell = run_cmd(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$PSVersionTable.PSVersion.ToString() + '|' + $PSVersionTable.PSEdition",
        ],
        timeout=10,
    )
    shell_value = first_line(powershell.get("stdout") or powershell.get("stderr"))
    environment = {
        "privilege": {"elevated": is_admin, "developer_mode": developer_mode},
        "git": git_version,
        "python": python_version,
        "bash": bash_version,
        "shell": {"powershell": shell_value or "unknown"},
    }

    try:
        os.symlink(source_skill, directory_symlink, target_is_directory=True)
        add_check(
            "direct_os_symlink_directory",
            "filesystem",
            "passed",
            "direct Python os.symlink created a directory link",
            {"link_type": "directory", "token_elevated": is_admin, "developer_mode": developer_mode},
        )
    except Exception as exc:
        add_check(
            "direct_os_symlink_directory",
            "filesystem",
            "failed",
            f"{exc.__class__.__name__}: {exc}",
            {"link_type": "directory", "token_elevated": is_admin, "developer_mode": developer_mode},
        )

    try:
        os.symlink(source_bin / "openspec", file_symlink, target_is_directory=False)
        add_check(
            "direct_os_symlink_file",
            "filesystem",
            "passed",
            "direct Python os.symlink created a file link",
            {"link_type": "file", "token_elevated": is_admin, "developer_mode": developer_mode},
        )
    except Exception as exc:
        add_check(
            "direct_os_symlink_file",
            "filesystem",
            "failed",
            f"{exc.__class__.__name__}: {exc}",
            {"link_type": "file", "token_elevated": is_admin, "developer_mode": developer_mode},
        )

    symlink_dir_ok = any(check["name"] == "direct_os_symlink_directory" and check["status"] == "passed" for check in checks)
    symlink_file_ok = any(check["name"] == "direct_os_symlink_file" and check["status"] == "passed" for check in checks)
    if is_admin:
        add_check(
            "direct_os_symlink_without_elevation",
            "filesystem",
            "not-applicable",
            "current SSH token reports elevated=true; harness did not request elevation, but this run cannot prove non-elevated Developer Mode symlink behavior",
            {"token_elevated": True, "developer_mode": developer_mode},
        )
    elif developer_mode == "enabled" and symlink_dir_ok and symlink_file_ok:
        add_check(
            "direct_os_symlink_without_elevation",
            "filesystem",
            "passed",
            "non-elevated token with Developer Mode created direct symlinks",
            {"token_elevated": False, "developer_mode": developer_mode},
        )
    else:
        add_check(
            "direct_os_symlink_without_elevation",
            "filesystem",
            "failed",
            "non-elevated direct symlink was unavailable",
            {"token_elevated": False, "developer_mode": developer_mode},
        )

    junction_result = run_cmd(["cmd", "/c", "mklink", "/J", str(junction), str(source_skill)], timeout=10)
    if junction_result["ok"]:
        add_check("junction_directory", "filesystem", "passed", "cmd mklink created a directory junction", {"link_type": "junction"})
    else:
        add_check(
            "junction_directory",
            "filesystem",
            "failed",
            junction_result.get("error") or first_line(junction_result["stderr"] or junction_result["stdout"]),
            {"link_type": "junction", "exit_code": junction_result["exit_code"]},
        )

    copy = consumer_skills / "changerail-ff-copy"
    shutil.copytree(source_skill, copy, dirs_exist_ok=True)
    copy_file = copy / "SKILL.md"
    copy_hash_v1 = file_hash(copy_file)
    source_skill_file.write_text("name: changerail-ff\nversion: source-v2\n", encoding="utf-8")
    source_hash_v2 = file_hash(source_skill_file)
    copy_hash_after_source_update = file_hash(copy_file)
    if copy_hash_after_source_update != source_hash_v2:
        add_check(
            "generated_copy_drift_detection",
            "generated-copy",
            "passed",
            "generated copy stayed stale after source update, so drift is detectable by hash comparison",
            {"initial_copy_hash": copy_hash_v1, "copy_stale_after_source_update": True},
        )
    else:
        add_check(
            "generated_copy_drift_detection",
            "generated-copy",
            "failed",
            "generated copy changed without explicit refresh",
            {"copy_stale_after_source_update": False},
        )
    shutil.rmtree(copy)
    shutil.copytree(source_skill, copy)
    if file_hash(copy_file) == source_hash_v2:
        add_check(
            "generated_copy_source_update_behavior",
            "generated-copy",
            "passed",
            "generated copy required an explicit refresh to pick up source updates",
            {"update_model": "manual-refresh-required"},
        )
    else:
        add_check(
            "generated_copy_source_update_behavior",
            "generated-copy",
            "failed",
            "generated copy refresh did not match source",
            {"update_model": "refresh-failed"},
        )

    launch_check("extensionless_direct_launch", [source_bin / "openspec"], "wrapper-extensionless")
    launch_check("cmd_wrapper_launch", [source_bin / "openspec.cmd"], "wrapper-cmd")
    launch_check(
        "powershell_wrapper_launch",
        ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", source_bin / "openspec.ps1"],
        "wrapper-powershell",
    )
    launch_check("python_wrapper_launch", [sys.executable, source_bin / "openspec.py"], "wrapper-python")
    if bash_version["status"] == "available":
        launch_check("explicit_bash_launch", ["bash", source_bin / "openspec"], "wrapper-extensionless")
    else:
        add_check("explicit_bash_launch", "runtime", "unsupported", "bash is unavailable on PATH", {"prerequisite": "bash"})

    if git_version["status"] == "available":
        run_cmd(["git", "-C", consumer_root, "init"], timeout=10)
        run_cmd(["git", "-C", consumer_root, "config", "core.autocrlf", "false"], timeout=10)
        run_cmd(["git", "-C", consumer_root, "config", "user.email", "changerail@example.invalid"], timeout=10)
        run_cmd(["git", "-C", consumer_root, "config", "user.name", "ChangeRail Probe"], timeout=10)
        porcelain = run_cmd(["git", "-C", consumer_root, "status", "--porcelain=v1", "--untracked-files=all"], timeout=15)
        porcelain_text = (porcelain["stdout"] + "\n" + porcelain["stderr"]).strip()
        porcelain_details = {
            "exit_code": porcelain["exit_code"],
            "safe": porcelain["ok"],
            "unsafe_paths": [],
            "entry_count": len([line for line in porcelain_text.splitlines() if line.strip()]),
            "mentions_directory_symlink": git_mentions(porcelain_text, ".codex/skills/changerail-ff-link"),
            "mentions_file_symlink": git_mentions(porcelain_text, "bin/openspec-link"),
            "mentions_junction": git_mentions(porcelain_text, ".codex/skills/changerail-ff-junction"),
            "mentions_generated_copy": git_mentions(porcelain_text, ".codex/skills/changerail-ff-copy"),
        }
        if porcelain["ok"]:
            add_check("git_status_porcelain", "git", "passed", "git status --porcelain completed", porcelain_details)
        else:
            add_check(
                "git_status_porcelain",
                "git",
                "failed",
                porcelain.get("error") or first_line(porcelain_text),
                porcelain_details,
            )

        dry_run = run_cmd(["git", "-C", consumer_root, "add", "--dry-run", "."], timeout=15)
        dry_text = (dry_run["stdout"] + "\n" + dry_run["stderr"]).strip()
        dry_details = {
            "exit_code": dry_run["exit_code"],
            "safe": dry_run["ok"],
            "unsafe_paths": [],
            "entry_count": len([line for line in dry_text.splitlines() if line.strip()]),
            "mentions_directory_symlink": git_mentions(dry_text, ".codex/skills/changerail-ff-link"),
            "mentions_file_symlink": git_mentions(dry_text, "bin/openspec-link"),
            "mentions_junction": git_mentions(dry_text, ".codex/skills/changerail-ff-junction"),
            "mentions_generated_copy": git_mentions(dry_text, ".codex/skills/changerail-ff-copy"),
        }
        if dry_run["ok"]:
            add_check("git_add_dry_run", "git", "passed", "git add --dry-run completed", dry_details)
        else:
            add_check("git_add_dry_run", "git", "failed", dry_run.get("error") or first_line(dry_text), dry_details)

        git_add = run_cmd(["git", "-C", consumer_root, "add", "."], timeout=15)
        index = run_cmd(["git", "-C", consumer_root, "ls-files", "--stage"], timeout=15)
        index_text = (index["stdout"] + "\n" + index["stderr"]).strip()
        index_details = {
            "git_add_exit_code": git_add["exit_code"],
            "ls_files_exit_code": index["exit_code"],
            "safe": git_add["ok"] and index["ok"],
            "unsafe_paths": [],
            "index_entry_count": len([line for line in index_text.splitlines() if line.strip()]),
            "has_directory_symlink_entry": git_mentions(index_text, ".codex/skills/changerail-ff-link"),
            "has_file_symlink_entry": git_mentions(index_text, "bin/openspec-link"),
            "has_junction_entry": git_mentions(index_text, ".codex/skills/changerail-ff-junction"),
            "has_generated_copy_entry": git_mentions(index_text, ".codex/skills/changerail-ff-copy"),
            "has_symlink_mode": "120000" in index_text,
        }
        if git_add["ok"] and index["ok"]:
            add_check("git_index_inspection", "git", "passed", "git add and git ls-files --stage completed", index_details)
        else:
            add_check(
                "git_index_inspection",
                "git",
                "failed",
                git_add.get("error") or index.get("error") or first_line((git_add["stderr"] + "\n" + index_text).strip()),
                index_details,
            )
    else:
        add_check("git_status_porcelain", "git", "unsupported", "git is unavailable on PATH", {"prerequisite": "git"})
        add_check("git_add_dry_run", "git", "unsupported", "git is unavailable on PATH", {"prerequisite": "git"})
        add_check("git_index_inspection", "git", "unsupported", "git is unavailable on PATH", {"prerequisite": "git"})
except Exception as exc:
    status = "failed"
    error = f"{exc.__class__.__name__}: {exc}"
finally:
    try:
        cleanup_probe_root()
        cleanup = "passed"
    except Exception as exc:
        cleanup = "failed"
        if status == "passed":
            status = "failed"
            error = f"{exc.__class__.__name__}: {exc}"

seen = {check["name"] for check in checks}
for check_name in CHECK_NAMES:
    if check_name not in seen:
        add_check(check_name, "unknown", "failed", "remote result did not include this check", {})

result = {
    "schema": HOST_SCHEMA,
    "status": status,
    "cleanup": cleanup,
    "environment": environment,
    "checks": checks,
}
if error:
    result["error"] = error
print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
sys.exit(0 if status == "passed" else 1)
'''
    replacements = {
        "__ROOT_JSON__": json.dumps(host.disposable_root),
        "__PROBE_ID_JSON__": json.dumps(probe_id),
        "__HOST_SCHEMA_JSON__": json.dumps(HOST_SCHEMA),
        "__CHECK_NAMES_JSON__": json.dumps(list(CHECK_NAMES)),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def run_host(host: HostConfig, probe_id: str, output_dir: Path, timeout: float) -> dict[str, Any]:
    ssh_argv = shlex.split(host.ssh_command)
    script = remote_python_script(host, probe_id)
    remote_command = "python -"
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
            summary = summarize_host_result(host.id, sanitize_object(payload))
        except (IndexError, json.JSONDecodeError, ValueError):
            summary = {
                "id": host.id,
                "status": "failed",
                "cleanup": "unknown",
                "environment": {},
                "summary": {"check_count": 0, "status_counts": {"failed": len(CHECK_NAMES)}},
                "checks": [
                    {
                        "name": name,
                        "category": "unknown",
                        "status": "failed",
                        "message": "remote command did not return sanitized JSON; see ignored raw output",
                        "details": {},
                    }
                    for name in CHECK_NAMES
                ],
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
            "cleanup": "unknown",
            "environment": {},
            "summary": {"check_count": 0, "status_counts": {"failed": len(CHECK_NAMES)}},
            "checks": [
                {
                    "name": name,
                    "category": "unknown",
                    "status": "failed",
                    "message": f"remote command timed out after {timeout:g} seconds",
                    "details": {},
                }
                for name in CHECK_NAMES
            ],
            "diagnostic": f"remote command timed out after {timeout:g} seconds",
            "evidence": {
                "raw_output_path": raw_path.as_posix(),
                "started_at": started,
                "duration_seconds": duration,
            },
        }


def sample_host_result(host_id: str) -> dict[str, Any]:
    checks = [
        {
            "name": name,
            "category": "sample",
            "status": "passed",
            "message": "sample dry-run check validates report shape only",
            "details": {},
        }
        for name in CHECK_NAMES
    ]
    return {
        "id": host_id,
        "status": "passed",
        "cleanup": "sample",
        "environment": {
            "privilege": {"elevated": False, "developer_mode": "sample"},
            "git": {"status": "sample", "value": "sample"},
            "python": {"status": "sample", "value": "sample"},
            "bash": {"status": "sample", "value": "sample"},
        },
        "summary": {"check_count": len(checks), "status_counts": {"passed": len(checks)}},
        "checks": checks,
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
    all_checks = [check for result in host_results for check in result.get("checks", []) if isinstance(check, dict)]
    status_counts: dict[str, int] = {}
    for check in all_checks:
        status_key = str(check.get("status", "failed"))
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": mode,
        "status": status,
        "summary": {
            "host_count": len(hosts),
            "passed_hosts": sum(1 for result in host_results if result.get("status") == "passed"),
            "failed_hosts": sum(1 for result in host_results if result.get("status") != "passed"),
            "inventory_ignored": inventory_ignored,
            "host_ids": [host.id for host in hosts],
            "check_status_counts": status_counts,
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
    host_results = [sample_host_result(host.id) for host in hosts]
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
                "cleanup": result.get("cleanup", "unknown"),
                "environment": result.get("environment", {}),
                "summary": result.get("summary", {}),
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

    live = subparsers.add_parser("run", help="run live disposable probes over SSH")
    live.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    live.add_argument("--output-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    live.add_argument("--run-id")
    live.add_argument("--timeout", type=float, default=120.0)
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
