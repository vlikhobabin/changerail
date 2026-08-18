#!/usr/bin/env python3
"""Deterministic smoke checks for native Windows helper entrypoint contracts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


SCHEMA = "changerail.windows-entrypoint-smoke.v1"
ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
WINDOWS_SELECTOR = ROOT / "scripts" / "changerail_python_windows.py"
SUPPORTED = (
    "bootstrap-project",
    "openspec",
    "changerail-python",
    "verify-project",
    "changerail-review-verdict",
    "changerail-evidence",
    "changerail-delivery-runner",
    "changerail-delivery-metrics",
    "changerail-maintenance",
    "changerail-maintenance-runner",
)
PYTHON_BACKED = (
    "bootstrap-project",
    "verify-project",
    "changerail-review-verdict",
    "changerail-evidence",
    "changerail-delivery-runner",
    "changerail-delivery-metrics",
    "changerail-maintenance",
    "changerail-maintenance-runner",
)
FORBIDDEN_CMD_SNIPPETS = ("bash", "powershell", "pwsh", "cmd /c")


@dataclass
class Check:
    name: str
    status: str
    message: str


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def cmd_text(name: str) -> str:
    return (BIN / f"{name}.cmd").read_text(encoding="utf-8")


def add(checks: list[Check], name: str, ok: bool, message: str) -> None:
    checks.append(Check(name, "pass" if ok else "fail", message))


def check_inventory(checks: list[Check]) -> None:
    for name in SUPPORTED:
        add(
            checks,
            f"{name} POSIX entrypoint exists",
            (BIN / name).is_file(),
            f"found {rel(BIN / name)}",
        )
        add(
            checks,
            f"{name}.cmd entrypoint exists",
            (BIN / f"{name}.cmd").is_file(),
            f"found {rel(BIN / f'{name}.cmd')}",
        )


def check_python_backed_wrappers(checks: list[Check]) -> None:
    for name in PYTHON_BACKED:
        text = cmd_text(name)
        expected = f'call "%~dp0changerail-python.cmd" "%~dp0{name}" %*'
        add(
            checks,
            f"{name}.cmd routes through selector",
            expected in text,
            f"expected selector invocation in {name}.cmd",
        )
        add(
            checks,
            f"{name}.cmd propagates exit code",
            "exit /b %ERRORLEVEL%" in text,
            f"expected exit-code propagation in {name}.cmd",
        )


def check_selector_wrapper(checks: list[Check]) -> None:
    text = cmd_text("changerail-python")
    requirements = {
        "uses Windows selector backend": "scripts\\changerail_python_windows.py",
        "supports explicit override": "CHANGERAIL_PYTHON",
        "probes python command": "where python",
        "probes py launcher": "where py",
        "forwards argv": "%*",
        "propagates exit code": "exit /b %ERRORLEVEL%",
    }
    for label, snippet in requirements.items():
        add(
            checks,
            f"changerail-python.cmd {label}",
            snippet in text,
            f"required snippet present: {snippet}",
        )


def check_openspec_wrapper(checks: list[Check]) -> None:
    text = cmd_text("openspec")
    requirements = {
        "pins default version": "openspec_version=1.3.1",
        "uses npx pinned package": 'npx -y "@fission-ai/openspec@%openspec_version%" %*',
        "supports OPENSPEC_WORKDIR": "OPENSPEC_WORKDIR",
        "sets telemetry default": "OPENSPEC_TELEMETRY=0",
        "prefers cached package metadata": "npm_config_prefer_offline=true",
        "propagates helper exit code": "exit /b %status%",
    }
    for label, snippet in requirements.items():
        add(
            checks,
            f"openspec.cmd {label}",
            snippet in text,
            f"required snippet present: {snippet}",
        )
    add(
        checks,
        "openspec.cmd avoids extensionless POSIX launch",
        "%~dp0openspec" not in text,
        "does not invoke sibling extensionless wrapper",
    )


def check_no_shell_fallbacks(checks: list[Check]) -> None:
    for name in SUPPORTED:
        text = cmd_text(name).lower()
        found = [snippet for snippet in FORBIDDEN_CMD_SNIPPETS if snippet in text]
        add(
            checks,
            f"{name}.cmd avoids implicit shell fallback",
            not found,
            "no Bash, PowerShell or cmd /c fallback found"
            if not found
            else f"forbidden snippet(s): {', '.join(found)}",
        )


def check_bootstrap_verify_handoff(checks: list[Check]) -> None:
    text = (BIN / "bootstrap-project").read_text(encoding="utf-8")
    add(
        checks,
        "bootstrap-project uses native verify wrapper on Windows",
        'verify_name = "verify-project.cmd" if os.name == "nt" else "verify-project"' in text,
        "bootstrap verification handoff selects verify-project.cmd on native Windows",
    )


def check_verify_openspec_handoff(checks: list[Check]) -> None:
    text = (BIN / "verify-project").read_text(encoding="utf-8")
    add(
        checks,
        "verify-project uses native OpenSpec wrapper on Windows",
        'openspec_name = "openspec.cmd" if os.name == "nt" else "openspec"' in text,
        "OpenSpec validation handoff selects openspec.cmd on native Windows",
    )


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **(env or {})},
        check=False,
        timeout=60,
    )


def check_windows_selector_backend(checks: list[Check]) -> None:
    result = run(
        [
            sys.executable,
            str(WINDOWS_SELECTOR),
            "--source",
            "smoke",
            "--root",
            str(ROOT),
            "--check",
            "--json",
        ],
        ROOT,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    add(
        checks,
        "Windows selector check JSON",
        result.returncode == 0 and payload.get("ok") is True,
        result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}",
    )

    with tempfile.TemporaryDirectory(prefix="changerail windows entrypoints Пример ") as tmp:
        tmp_root = Path(tmp)
        cwd = tmp_root / "cwd with spaces Пример"
        target_dir = tmp_root / "target dir Пример"
        cwd.mkdir()
        target_dir.mkdir()
        target = target_dir / "probe target.py"
        target.write_text(
            "import json, os, sys\n"
            "payload = {\n"
            "    'argv': sys.argv[1:],\n"
            "    'cwd': os.getcwd(),\n"
            "    'env': os.environ.get('CHANGERAIL_ENTRYPOINT_SMOKE_ENV'),\n"
            "    'resolved': os.environ.get('CHANGERAIL_PYTHON_RESOLVED'),\n"
            "    'pythonpath': os.environ.get('PYTHONPATH', ''),\n"
            "}\n"
            "print(json.dumps(payload, ensure_ascii=False, sort_keys=True))\n"
            "raise SystemExit(37)\n",
            encoding="utf-8",
        )
        expected_args = ["plain", "value with spaces", "значение"]
        result = run(
            [
                sys.executable,
                str(WINDOWS_SELECTOR),
                "--source",
                "smoke",
                "--root",
                str(ROOT),
                str(target),
                *expected_args,
            ],
            cwd,
            {"CHANGERAIL_ENTRYPOINT_SMOKE_ENV": "present"},
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
        add(
            checks,
            "Windows selector preserves argv",
            result.returncode == 37 and payload.get("argv") == expected_args,
            result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}",
        )
        add(
            checks,
            "Windows selector preserves cwd",
            payload.get("cwd") == str(cwd),
            f"observed cwd: {payload.get('cwd')}",
        )
        add(
            checks,
            "Windows selector preserves environment",
            payload.get("env") == "present",
            f"observed env: {payload.get('env')}",
        )
        add(
            checks,
            "Windows selector records resolved runtime",
            bool(payload.get("resolved")),
            f"resolved runtime: {payload.get('resolved')}",
        )
        add(
            checks,
            "Windows selector injects scripts path",
            str(ROOT / "scripts") in payload.get("pythonpath", ""),
            f"PYTHONPATH: {payload.get('pythonpath')}",
        )


def run_smoke() -> dict[str, object]:
    checks: list[Check] = []
    check_inventory(checks)
    check_python_backed_wrappers(checks)
    check_selector_wrapper(checks)
    check_openspec_wrapper(checks)
    check_no_shell_fallbacks(checks)
    check_bootstrap_verify_handoff(checks)
    check_verify_openspec_handoff(checks)
    check_windows_selector_backend(checks)
    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


def main(argv: list[str]) -> int:
    json_output = "--json" in argv
    report = run_smoke()
    summary = report["summary"]
    if json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            "summary: "
            f"{summary['status']} "
            f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
        )
        for check in report["checks"]:
            if check["status"] != "pass":
                print(f"FAIL {check['name']}: {check['message']}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
