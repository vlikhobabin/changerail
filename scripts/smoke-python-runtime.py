#!/usr/bin/env python3
"""Smoke checks for the shared ChangeRail Python runtime selector."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


SCHEMA = "changerail.python-runtime-smoke.v1"
ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "bin" / "changerail-python"
BOOTSTRAP = ROOT / "bin" / "bootstrap-project"
STATE = ROOT / ".runtime" / "changerail" / "python-runtime" / "last-check.json"


@dataclass
class Check:
    name: str
    status: str
    message: str


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **(env or {})},
        check=False,
        timeout=60,
    )


def executable(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def fake_python(path: Path, version: tuple[int, int, int], missing_modules: list[str]) -> Path:
    payload = ".".join(str(part) for part in version) + f"|{path}|" + ",".join(missing_modules)
    return executable(
        path,
        "\n".join(
            [
                "#!/bin/sh",
                "if [ \"$1\" = \"-c\" ]; then",
                f"  printf '%s\\n' {json.dumps(payload)}",
                "  exit 0",
                "fi",
                "printf 'fake python must not execute target\\n' >&2",
                "exit 99",
                "",
            ]
        ),
    )


def check_launcher_exists() -> Check:
    if not LAUNCHER.is_file():
        return Check("launcher exists", "fail", f"missing {LAUNCHER.relative_to(ROOT)}")
    if not os.access(LAUNCHER, os.X_OK):
        return Check("launcher executable", "fail", f"not executable {LAUNCHER.relative_to(ROOT)}")
    return Check("launcher executable", "pass", f"found {LAUNCHER.relative_to(ROOT)}")


def check_supported_runtime(tmp: Path) -> Check:
    result = run(
        [str(LAUNCHER), "--check", "--json"],
        {"CHANGERAIL_PYTHON": sys.executable},
    )
    if result.returncode != 0:
        return Check("supported runtime", "fail", result.stderr.strip() or result.stdout.strip())
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return Check("supported runtime", "fail", f"invalid JSON: {exc}: {result.stdout}")
    if not payload.get("ok"):
        return Check("supported runtime", "fail", result.stdout.strip())

    probe = tmp / "probe.py"
    probe.write_text(
        "import os\n"
        "print('resolved=' + os.environ.get('CHANGERAIL_PYTHON_RESOLVED', ''))\n",
        encoding="utf-8",
    )
    executed = run([str(LAUNCHER), str(probe)], {"CHANGERAIL_PYTHON": sys.executable})
    if executed.returncode != 0 or "resolved=" not in executed.stdout:
        return Check("supported runtime execution", "fail", executed.stderr.strip() or executed.stdout.strip())
    return Check("supported runtime execution", "pass", executed.stdout.strip())


def check_old_runtime(tmp: Path) -> Check:
    old = fake_python(tmp / "python-old", (3, 10, 13), [])
    result = run([str(LAUNCHER), "--check"], {"CHANGERAIL_PYTHON": str(old)})
    detail = result.stderr.strip() or result.stdout.strip()
    if result.returncode != 0 and "Python 3.11" in detail:
        return Check("old runtime diagnostic", "pass", detail)
    return Check("old runtime diagnostic", "fail", detail or f"exit {result.returncode}")


def check_missing_dependency(tmp: Path) -> Check:
    missing = fake_python(tmp / "python-missing-jsonschema", (3, 11, 0), ["jsonschema"])
    result = run([str(LAUNCHER), "--check"], {"CHANGERAIL_PYTHON": str(missing)})
    detail = result.stderr.strip() or result.stdout.strip()
    if result.returncode != 0 and "jsonschema" in detail and "requirements-runtime.txt" in detail:
        return Check("missing dependency diagnostic", "pass", detail)
    return Check("missing dependency diagnostic", "fail", detail or f"exit {result.returncode}")


def check_invalid_override() -> Check:
    result = run([str(LAUNCHER), "--check"], {"CHANGERAIL_PYTHON": "/opt/example-project/missing-python"})
    detail = result.stderr.strip() or result.stdout.strip()
    if result.returncode != 0 and "CHANGERAIL_PYTHON" in detail and "invalid" in detail:
        return Check("invalid override diagnostic", "pass", detail)
    return Check("invalid override diagnostic", "fail", detail or f"exit {result.returncode}")


def check_bootstrap_invalid_override() -> Check:
    result = run([str(BOOTSTRAP), "--help"], {"CHANGERAIL_PYTHON": "/opt/example-project/missing-python"})
    detail = result.stderr.strip() or result.stdout.strip()
    if result.returncode != 0 and "CHANGERAIL_PYTHON" in detail and "invalid" in detail:
        return Check("bootstrap-project invalid override", "pass", detail)
    return Check("bootstrap-project invalid override", "fail", detail or f"exit {result.returncode}")


def check_runtime_state_ignored() -> Check:
    if not STATE.is_file():
        return Check("runtime state record", "fail", f"missing {STATE.relative_to(ROOT)}")
    ignored = run(["git", "check-ignore", str(STATE.relative_to(ROOT))])
    if ignored.returncode != 0:
        return Check("runtime state ignored", "fail", f"not ignored: {STATE.relative_to(ROOT)}")
    return Check("runtime state ignored", "pass", str(STATE.relative_to(ROOT)))


def run_smoke() -> dict[str, object]:
    checks: list[Check] = [check_launcher_exists()]
    if checks[0].status != "pass":
        failed = 1
        return {
            "schema": SCHEMA,
            "summary": {"status": "fail", "total": len(checks), "passed": 0, "failed": failed},
            "checks": [asdict(check) for check in checks],
        }

    with tempfile.TemporaryDirectory(prefix="changerail-python-runtime-") as tmp_dir:
        tmp = Path(tmp_dir)
        checks.extend(
            [
                check_supported_runtime(tmp),
                check_old_runtime(tmp),
                check_missing_dependency(tmp),
                check_invalid_override(),
                check_bootstrap_invalid_override(),
                check_runtime_state_ignored(),
            ]
        )
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


def main() -> int:
    report = run_smoke()
    summary = report["summary"]
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
    raise SystemExit(main())
