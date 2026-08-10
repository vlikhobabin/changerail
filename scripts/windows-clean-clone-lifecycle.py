#!/usr/bin/env python3
"""Run sanitized native Windows clean-clone lifecycle probes."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "changerail.windows-clean-clone-lifecycle.v1"
HOST_SCHEMA = "changerail.windows-clean-clone-lifecycle-host-result.v1"
EXPECTED_HOST_IDS = ("windows-host-a", "windows-host-b")
DEFAULT_INVENTORY = Path("internal/windows-lab-inventory.json")
DEFAULT_RUNTIME_ROOT = Path(".runtime/changerail/windows-clean-clone-lifecycle")
DEFAULT_REPO_URL = "https://github.com/vlikhobabin/changerail.git"
DEFAULT_BRANCH = "main"
SECRET_KEY_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential)")
WINDOWS_HOME_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+")
WINDOWS_ABS_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"']+")
POSIX_HOME_RE = re.compile(r"(?:/home|/Users)/[A-Za-z0-9._-]+")
SSH_TARGET_RE = re.compile(r"(?P<user>[A-Za-z0-9._-]+)@(?P<host>[A-Za-z0-9._-]+(?:\.[A-Za-z0-9._-]+)+)")
CHECK_NAMES = (
    "clean_clone",
    "cmd_entrypoint_discovery",
    "generated_copy_bootstrap",
    "verify_project",
    "agent_surface_discovery",
    "refresh_stale_generated_wiring",
    "scoped_no_push_staging",
    "cleanup",
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
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compact(value: str, limit: int = 260) -> str:
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


def git_output(command: list[str], workspace: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), *command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProbeError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return result.stdout


def build_worktree_bundle(workspace: Path, bundle_dir: Path) -> str:
    source_dir = bundle_dir / "source"
    bundle_path = bundle_dir / "changerail-current-worktree.bundle"
    if source_dir.exists():
        shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    paths_output = git_output(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], workspace)
    rel_paths = [value for value in paths_output.split("\0") if value]
    for rel in rel_paths:
        source = workspace / rel
        target = source_dir / rel
        if not source.exists() and not source.is_symlink():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            os.symlink(os.readlink(source), target)
        elif source.is_file():
            shutil.copy2(source, target)
    subprocess.run(["git", "init"], cwd=source_dir, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
    subprocess.run(["git", "config", "user.email", "changerail@example.invalid"], cwd=source_dir, check=True)
    subprocess.run(["git", "config", "user.name", "ChangeRail Proof"], cwd=source_dir, check=True)
    subprocess.run(["git", "add", "-A"], cwd=source_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "clean clone lifecycle proof source"],
        cwd=source_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    subprocess.run(["git", "bundle", "create", str(bundle_path), "HEAD"], cwd=source_dir, check=True)
    return base64.b64encode(bundle_path.read_bytes()).decode("ascii")


def remote_python_script(
    host: HostConfig,
    probe_id: str,
    repo_url: str,
    branch: str,
    ref: str | None,
    bundle_b64: str | None,
) -> str:
    template = r'''
import hashlib
import json
import os
from pathlib import Path
import base64
import shutil
import subprocess
import sys

ROOT = __ROOT_JSON__
PROBE_ID = __PROBE_ID_JSON__
HOST_SCHEMA = __HOST_SCHEMA_JSON__
REPO_URL = __REPO_URL_JSON__
BRANCH = __BRANCH_JSON__
REF = __REF_JSON__
BUNDLE_B64 = __BUNDLE_B64_JSON__
CHECK_NAMES = __CHECK_NAMES_JSON__

probe_root = Path(ROOT) / ("changerail-clean-clone-" + PROBE_ID)
source_root = probe_root / "changerail"
consumer_root = probe_root / "consumer project with spaces"
source_bin = source_root / "bin"
checks = []
env = os.environ.copy()
env["OPENSPEC_TELEMETRY"] = "0"


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


def first_line(text):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[0] if lines else ""


def snippet(result, limit=12000):
    text = (result.get("stderr") or "") + "\n" + (result.get("stdout") or "")
    if result.get("error"):
        text = result["error"] + "\n" + text
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    compact = " | ".join(lines)
    return compact[:limit]


def run_cmd(argv, timeout=120, cwd=None):
    try:
        completed = subprocess.run(
            [str(arg) for arg in argv],
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        return {
            "ok": False,
            "exit_code": -1,
            "stdout": stdout,
            "stderr": stderr,
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


def resolve_command(command):
    candidates = [command]
    if not Path(command).suffix:
        candidates.extend([command + ".cmd", command + ".bat", command + ".exe"])
    for candidate in candidates:
        resolved = shutil.which(candidate, path=env.get("PATH"))
        if resolved:
            return resolved
    return None


def command_help(path, *args, timeout=180):
    return run_cmd(["cmd", "/c", str(path), *args], timeout=timeout, cwd=source_root)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version(command, *args):
    executable = resolve_command(command)
    if not executable:
        return {"status": "unavailable", "command": command, "value": "unavailable"}
    result = run_cmd([executable, *args], timeout=20)
    if result["ok"]:
        value = first_line(result["stdout"] or result["stderr"])
        return {"status": "available", "command": command, "value": value or "available"}
    return {"status": "unavailable", "command": command, "value": "unavailable"}


def cleanup_probe_root():
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


def existing_check(name):
    return next((check for check in checks if check["name"] == name), None)


status = "passed"
cleanup = "not_started"
error = None
environment = {}

try:
    cleanup_probe_root()
except Exception:
    pass

try:
    environment = {
        "git": version("git", "--version"),
        "python": version("python", "--version"),
        "node": version("node", "--version"),
        "npm": version("npm", "--version"),
    }

    probe_root.mkdir(parents=True, exist_ok=True)
    if BUNDLE_B64:
        bundle_path = probe_root / "changerail-current-worktree.bundle"
        bundle_path.write_bytes(base64.b64decode(BUNDLE_B64.encode("ascii")))
        clone = run_cmd(["git", "clone", str(bundle_path), source_root], timeout=420)
    else:
        clone = run_cmd(
            ["git", "clone", "--no-tags", "--depth", "1", "--branch", BRANCH, REPO_URL, source_root],
            timeout=420,
        )
    checkout_ok = False
    if clone["ok"] and REF and not BUNDLE_B64:
        checkout = run_cmd(["git", "-C", source_root, "checkout", "--detach", REF], timeout=180)
        checkout_ok = checkout["ok"]
    elif clone["ok"]:
        checkout = {"ok": True, "stdout": "", "stderr": "", "exit_code": 0}
        checkout_ok = True
    else:
        checkout = {"ok": False, "stdout": "", "stderr": "", "exit_code": -1, "error": "clone failed"}
    porcelain = run_cmd(["git", "-C", source_root, "status", "--porcelain=v1", "--untracked-files=all"], timeout=60)
    clean_clone_ok = clone["ok"] and checkout_ok and porcelain["ok"] and not porcelain["stdout"].strip()
    add_check(
        "clean_clone",
        "source",
        "passed" if clean_clone_ok else "failed",
        "clean clone checked out requested ref with no manual source edits"
        if clean_clone_ok
        else first_line(clone.get("stderr") or clone.get("stdout") or checkout.get("stderr") or porcelain.get("stdout"))
        or clone.get("error")
        or checkout.get("error")
        or "clean clone failed",
        {
            "branch": BRANCH,
            "source_kind": "bundle" if bool(BUNDLE_B64) else "remote",
            "ref_checked": bool(REF) or bool(BUNDLE_B64),
            "working_tree_clean": porcelain["ok"] and not porcelain["stdout"].strip(),
        },
    )

    helper_names = [
        "bootstrap-project",
        "openspec",
        "changerail-python",
        "verify-project",
        "changerail-review-verdict",
        "changerail-evidence",
        "changerail-delivery-runner",
        "changerail-delivery-metrics",
    ]
    entrypoint_results = {}
    if clean_clone_ok:
        for helper in helper_names:
            wrapper = source_bin / f"{helper}.cmd"
            if not wrapper.is_file():
                entrypoint_results[helper] = {"status": "missing"}
                continue
            if helper == "changerail-python":
                result = command_help(wrapper, "--check", "--json", timeout=120)
            else:
                result = command_help(wrapper, "--help", timeout=240 if helper == "openspec" else 120)
            entrypoint_results[helper] = {
                "status": "passed" if result["ok"] else "failed",
                "exit_code": result["exit_code"],
                **({} if result["ok"] else {"diagnostic": snippet(result)}),
            }
    entrypoints_ok = bool(entrypoint_results) and all(
        value.get("status") == "passed" for value in entrypoint_results.values()
    )
    add_check(
        "cmd_entrypoint_discovery",
        "entrypoints",
        "passed" if entrypoints_ok else "failed",
        "required native .cmd helper entrypoints launched"
        if entrypoints_ok
        else "one or more required native .cmd helper entrypoints failed",
        {"helpers": entrypoint_results},
    )

    bootstrap_ok = False
    if entrypoints_ok:
        bootstrap = command_help(
            source_bin / "bootstrap-project.cmd",
            str(consumer_root),
            "--name",
            "windows-clean-clone-consumer",
            "--kind",
            "generic",
            "--lock-enforcement",
            "none",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "generated-copy",
            timeout=720,
        )
        bootstrap_ok = bootstrap["ok"]
        add_check(
            "generated_copy_bootstrap",
            "consumer",
            "passed" if bootstrap_ok else "failed",
            "generated-copy consumer bootstrap passed through native .cmd helper"
            if bootstrap_ok
            else first_line(bootstrap.get("stderr") or bootstrap.get("stdout")) or bootstrap.get("error") or "bootstrap failed",
            {"backend": "generated-copy", "exit_code": bootstrap["exit_code"], **({} if bootstrap_ok else {"diagnostic": snippet(bootstrap)})},
        )
    else:
        add_check("generated_copy_bootstrap", "consumer", "blocked", "entrypoint discovery failed", {"backend": "generated-copy"})

    verify_ok = False
    if bootstrap_ok:
        verify = command_help(source_bin / "verify-project.cmd", str(consumer_root), "--json", timeout=420)
        verify_ok = verify["ok"]
        add_check(
            "verify_project",
            "consumer",
            "passed" if verify_ok else "failed",
            "verify-project passed against generated consumer"
            if verify_ok
            else first_line(verify.get("stderr") or verify.get("stdout")) or verify.get("error") or "verify-project failed",
            {"command": "verify-project.cmd --json"},
        )
    else:
        add_check("verify_project", "consumer", "blocked", "bootstrap failed", {"command": "verify-project.cmd --json"})

    discovery_ok = False
    if bootstrap_ok:
        required_paths = [
            ".codex/skills/changerail-deliver/SKILL.md",
            ".codex/skills/chrl-deliver/SKILL.md",
            ".codex/skills/openspec-apply-change/SKILL.md",
            ".claude/commands/changerail/deliver.md",
            ".claude/commands/chrl/deliver.md",
            "bin/openspec.cmd",
            "bin/bootstrap-project.cmd",
            "bin/verify-project.cmd",
            "bin/changerail-delivery-runner.cmd",
        ]
        missing = [rel for rel in required_paths if not (consumer_root / rel).is_file()]
        link_like = [
            rel
            for rel in required_paths
            if (consumer_root / rel).is_symlink()
        ]
        discovery_ok = not missing and not link_like
        add_check(
            "agent_surface_discovery",
            "consumer",
            "passed" if discovery_ok else "failed",
            "required generated skills, commands and helpers are discoverable"
            if discovery_ok
            else "required generated surface missing or link-backed",
            {"missing_count": len(missing), "link_like_count": len(link_like)},
        )
    else:
        add_check("agent_surface_discovery", "consumer", "blocked", "bootstrap failed", {})

    refresh_ok = False
    if verify_ok:
        project_owned = consumer_root / "src" / "project-owned.txt"
        project_owned.parent.mkdir(parents=True, exist_ok=True)
        project_owned.write_text("project-owned content\n", encoding="utf-8")
        generated_wrapper = consumer_root / "bin" / "verify-project.cmd"
        source_wrapper = source_bin / "verify-project.cmd"
        source_wrapper.write_text(
            source_wrapper.read_text(encoding="utf-8") + "\r\nrem clean-clone refresh probe\r\n",
            encoding="utf-8",
        )
        stale = command_help(source_bin / "verify-project.cmd", str(consumer_root), "--json", timeout=240)
        refresh = command_help(source_bin / "bootstrap-project.cmd", str(consumer_root), "--refresh-wiring", "--skip-verify", timeout=420)
        refreshed_hash = file_hash(generated_wrapper) if generated_wrapper.exists() else ""
        source_hash = file_hash(source_wrapper)
        post_verify = command_help(source_bin / "verify-project.cmd", str(consumer_root), "--json", timeout=420)
        refresh_ok = (
            stale["exit_code"] != 0
            and refresh["ok"]
            and post_verify["ok"]
            and refreshed_hash == source_hash
            and project_owned.read_text(encoding="utf-8") == "project-owned content\n"
        )
        add_check(
            "refresh_stale_generated_wiring",
            "consumer",
            "passed" if refresh_ok else "failed",
            "stale generated helper failed verification, refresh restored it and project-owned file stayed unchanged"
            if refresh_ok
            else "generated wiring refresh did not restore expected state",
            {
                "stale_detected": stale["exit_code"] != 0,
                "refresh_exit_code": refresh["exit_code"],
                "post_verify_exit_code": post_verify["exit_code"],
                "refreshed_matches_source": refreshed_hash == source_hash,
                "project_owned_preserved": project_owned.read_text(encoding="utf-8") == "project-owned content\n",
            },
        )
    else:
        add_check("refresh_stale_generated_wiring", "consumer", "blocked", "verify-project failed", {})

    staging_ok = False
    if refresh_ok:
        git_init = run_cmd(["git", "-C", consumer_root, "init"], timeout=60)
        run_cmd(["git", "-C", consumer_root, "config", "core.autocrlf", "false"], timeout=30)
        run_cmd(["git", "-C", consumer_root, "config", "user.email", "changerail@example.invalid"], timeout=30)
        run_cmd(["git", "-C", consumer_root, "config", "user.name", "ChangeRail Windows Proof"], timeout=30)
        docs_file = consumer_root / "docs" / "scoped-delivery-smoke.md"
        runtime_file = consumer_root / ".runtime" / "changerail" / "smoke" / "raw.log"
        docs_file.parent.mkdir(parents=True, exist_ok=True)
        runtime_file.parent.mkdir(parents=True, exist_ok=True)
        docs_file.write_text("scoped no-push delivery smoke\n", encoding="utf-8", newline="\n")
        runtime_file.write_text("ignored runtime output\n", encoding="utf-8", newline="\n")
        add = run_cmd(["git", "-C", consumer_root, "add", "--", "docs/scoped-delivery-smoke.md"], timeout=60)
        cached = run_cmd(["git", "-C", consumer_root, "diff", "--cached", "--name-only"], timeout=60)
        cached_check = run_cmd(["git", "-C", consumer_root, "diff", "--cached", "--check"], timeout=60)
        ignored = run_cmd(["git", "-C", consumer_root, "check-ignore", "-q", ".runtime/changerail/smoke/raw.log"], timeout=60)
        cached_paths = [line.strip() for line in cached["stdout"].splitlines() if line.strip()]
        cached_paths_match = cached_paths == ["docs/scoped-delivery-smoke.md"]
        staging_ok = (
            git_init["ok"]
            and add["ok"]
            and cached["ok"]
            and cached_check["ok"]
            and ignored["exit_code"] == 0
            and cached_paths_match
        )
        add_check(
            "scoped_no_push_staging",
            "git",
            "passed" if staging_ok else "failed",
            "explicit no-push staging scope excluded ignored runtime files"
            if staging_ok
            else "explicit staging scope did not match expected file set",
            {
                "git_init_exit_code": git_init["exit_code"],
                "git_add_exit_code": add["exit_code"],
                "cached_exit_code": cached["exit_code"],
                "cached_check_exit_code": cached_check["exit_code"],
                "ignored_exit_code": ignored["exit_code"],
                "cached_paths": cached_paths,
                "cached_paths_match": cached_paths_match,
                "runtime_ignored": ignored["exit_code"] == 0,
            },
        )
    else:
        add_check("scoped_no_push_staging", "git", "blocked", "refresh verification failed", {})

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
    if check_name == "cleanup":
        continue
    if check_name not in seen:
        add_check(check_name, "unknown", "failed", "remote result did not include this check", {})
add_check("cleanup", "cleanup", "passed" if cleanup == "passed" else "failed", f"cleanup {cleanup}", {})

if any(check["status"] != "passed" for check in checks):
    status = "failed"

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
    def py_literal(value: str | None) -> str:
        return "None" if value is None else json.dumps(value)

    replacements = {
        "__ROOT_JSON__": json.dumps(host.disposable_root),
        "__PROBE_ID_JSON__": json.dumps(probe_id),
        "__HOST_SCHEMA_JSON__": json.dumps(HOST_SCHEMA),
        "__REPO_URL_JSON__": json.dumps(repo_url),
        "__BRANCH_JSON__": json.dumps(branch),
        "__REF_JSON__": py_literal(ref),
        "__BUNDLE_B64_JSON__": py_literal(bundle_b64),
        "__CHECK_NAMES_JSON__": json.dumps(list(CHECK_NAMES)),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def summarize_host_result(host_id: str, result: dict[str, Any]) -> dict[str, Any]:
    checks = result.get("checks") if isinstance(result.get("checks"), list) else []
    materialized: list[dict[str, Any]] = []
    for check in checks:
        if isinstance(check, dict):
            materialized.append(
                {
                    "name": check.get("name", "unknown"),
                    "category": check.get("category", "unknown"),
                    "status": check.get("status", "failed"),
                    "message": check.get("message", ""),
                    "details": check.get("details", {}),
                }
            )
    seen = {check["name"] for check in materialized}
    for name in CHECK_NAMES:
        if name not in seen:
            materialized.append(
                {
                    "name": name,
                    "category": "unknown",
                    "status": "failed",
                    "message": "remote result did not include this check",
                    "details": {},
                }
            )
    counts: dict[str, int] = {}
    for check in materialized:
        status = str(check.get("status", "failed"))
        counts[status] = counts.get(status, 0) + 1
    return {
        "id": host_id,
        "status": result.get("status", "failed"),
        "cleanup": result.get("cleanup", "unknown"),
        "environment": result.get("environment", {}),
        "summary": {
            "check_count": len(materialized),
            "status_counts": counts,
        },
        "checks": sorted(materialized, key=lambda check: str(check.get("name", ""))),
        **({"diagnostic": result["error"]} if isinstance(result.get("error"), str) else {}),
    }


def run_host(
    host: HostConfig,
    probe_id: str,
    output_dir: Path,
    timeout: float,
    repo_url: str,
    branch: str,
    ref: str | None,
    bundle_b64: str | None,
) -> dict[str, Any]:
    ssh_argv = shlex.split(host.ssh_command)
    script = remote_python_script(host, probe_id, repo_url, branch, ref, bundle_b64)
    command = ssh_argv + ["python -"]
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
                "summary": {"check_count": len(CHECK_NAMES), "status_counts": {"failed": len(CHECK_NAMES)}},
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
            "summary": {"check_count": len(CHECK_NAMES), "status_counts": {"failed": len(CHECK_NAMES)}},
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
            "git": {"status": "sample", "value": "sample"},
            "python": {"status": "sample", "value": "sample"},
            "node": {"status": "sample", "value": "sample"},
            "npm": {"status": "sample", "value": "sample"},
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
    repo_url: str,
    branch: str,
    ref: str | None,
    source: str,
) -> dict[str, Any]:
    status = "passed" if all(result.get("status") == "passed" for result in host_results) else "failed"
    all_checks = [check for result in host_results for check in result.get("checks", []) if isinstance(check, dict)]
    counts: dict[str, int] = {}
    for check in all_checks:
        status_key = str(check.get("status", "failed"))
        counts[status_key] = counts.get(status_key, 0) + 1
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": mode,
        "status": status,
        "source": {
            "repo": "current working tree bundle"
            if source == "bundle"
            else ("public ChangeRail repository" if repo_url == DEFAULT_REPO_URL else "operator-supplied repository"),
            "branch": branch,
            "ref": "worktree-bundle" if source == "bundle" else (ref or "branch-head"),
        },
        "summary": {
            "host_count": len(hosts),
            "passed_hosts": sum(1 for result in host_results if result.get("status") == "passed"),
            "failed_hosts": sum(1 for result in host_results if result.get("status") != "passed"),
            "inventory_ignored": inventory_ignored,
            "host_ids": [host.id for host in hosts],
            "check_status_counts": counts,
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
        repo_url=args.repo_url,
        branch=args.branch,
        ref=args.ref,
        source=args.source,
    )
    print(json.dumps(report if args.json else report["summary"], ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def run_live(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    data = load_json(args.inventory)
    hosts = parse_inventory(data)
    if not ensure_ignored(args.inventory, workspace):
        raise ProbeError("inventory must be ignored by Git")
    probe_id = args.run_id or run_id()
    runtime_dir = (workspace / args.output_root / probe_id).resolve(strict=False)
    raw_dir = runtime_dir / "raw"
    bundle_b64 = None
    if args.source == "bundle":
        bundle_b64 = build_worktree_bundle(workspace, runtime_dir / "source-bundle")
    host_results = [
        run_host(host, probe_id, raw_dir, args.timeout, args.repo_url, args.branch, args.ref, bundle_b64)
        for host in hosts
    ]
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
        repo_url=args.repo_url,
        branch=args.branch,
        ref=args.ref,
        source=args.source,
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
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)

    dry = subparsers.add_parser("dry-run", help="validate inventory/report shape without SSH")
    dry.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    dry.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    dry.add_argument("--branch", default=DEFAULT_BRANCH)
    dry.add_argument("--ref")
    dry.add_argument("--source", choices=("remote", "bundle"), default="remote")
    dry.add_argument("--sample", action="store_true")
    dry.add_argument("--json", action="store_true")
    dry.set_defaults(func=dry_run)

    live = subparsers.add_parser("run", help="run live disposable clean-clone probes over SSH")
    live.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    live.add_argument("--output-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    live.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    live.add_argument("--branch", default=DEFAULT_BRANCH)
    live.add_argument("--ref")
    live.add_argument("--source", choices=("remote", "bundle"), default="remote")
    live.add_argument("--run-id")
    live.add_argument("--timeout", type=float, default=900.0)
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
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        else:
            print(f"error: {payload['diagnostic']}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
