#!/usr/bin/env python3
"""Run the local ChangeRail release verification baseline."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_BIN = ROOT / ".runtime" / "changerail" / "ci-venv" / "bin"
DRIFT_PROJECT = ROOT / ".runtime" / "changerail" / "ci-drift" / "example-project"


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]


def command_text(command: list[str]) -> str:
    return " ".join(command)


def baseline_env() -> dict[str, str]:
    env = os.environ.copy()
    if VENV_BIN.is_dir():
        env["PATH"] = f"{VENV_BIN}{os.pathsep}{env.get('PATH', '')}"
    return env


def steps() -> list[Step]:
    return [
        Step("openspec validation", ["./bin/openspec", "validate", "--all", "--strict"]),
        Step("json config parse", ["python3", "-m", "json.tool", ".mcp.json"]),
        Step(
            "toml config parse",
            [
                "python3",
                "-c",
                "import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')",
            ],
        ),
        Step("contract schema validation", ["python3", "scripts/smoke-contract-schemas.py"]),
        Step("python syntax inventory", ["python3", "scripts/compile-python-inventory.py"]),
        Step("python lint", ["ruff", "check", "bin", "scripts"]),
        Step("ci workflow contract", ["python3", "scripts/smoke-release-ci.py"]),
        Step("public surface scan self-test", ["python3", "scripts/public-surface-scan.py", "--self-test"]),
        Step("public surface scan", ["python3", "scripts/public-surface-scan.py"]),
        Step("public surface scan history", ["python3", "scripts/public-surface-scan.py", "--history"]),
        Step("wiring discovery smoke", ["python3", "scripts/smoke-wiring-discovery.py"]),
        Step("verify-project smoke", ["python3", "scripts/smoke-verify-project.py"]),
        Step("bootstrap smoke", ["python3", "scripts/smoke-bootstrap-project.py"]),
        Step("review verdict validation smoke", ["python3", "scripts/smoke-review-verdict-validation.py"]),
        Step("review fingerprint smoke", ["python3", "scripts/smoke-review-fingerprint.py"]),
        Step("delivery manifest smoke", ["python3", "scripts/smoke-delivery-manifest.py"]),
        Step("delivery manifest derive smoke", ["python3", "scripts/smoke-delivery-manifest-derive.py"]),
        Step("delivery runner smoke", ["python3", "scripts/smoke-delivery-runner.py"]),
        Step("delivery metrics smoke", ["python3", "scripts/smoke-delivery-metrics.py"]),
        Step("openspec archive diagnostics smoke", ["python3", "scripts/smoke-openspec-archive-diagnostics.py"]),
        Step("generated drift fixture reset", ["rm", "-rf", ".runtime/changerail/ci-drift"]),
        Step(
            "generated drift fixture bootstrap",
            [
                "./bin/bootstrap-project",
                ".runtime/changerail/ci-drift/example-project",
                "--name",
                "example-project",
                "--kind",
                "generic",
            ],
        ),
        Step("generated drift smoke", ["python3", "scripts/smoke-drift.py", "--project", str(DRIFT_PROJECT)]),
        Step("whitespace check", ["git", "diff", "--check"]),
        Step("ignored status check", ["git", "status", "--short", "--ignored"]),
    ]


def print_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")


def main() -> int:
    env = baseline_env()
    for index, step in enumerate(steps(), start=1):
        print(f"[{index}/{len(steps())}] {step.name}: {command_text(step.command)}")
        executable = shutil.which(step.command[0], path=env.get("PATH"))
        if executable is None:
            print(f"FAIL {step.name}: executable not found: {step.command[0]}", file=sys.stderr)
            if step.command[0] == "ruff":
                print(
                    "Install release dependencies first: "
                    "python3 -m venv .runtime/changerail/ci-venv && "
                    ".runtime/changerail/ci-venv/bin/python -m pip install "
                    "--disable-pip-version-check -r requirements-dev.txt",
                    file=sys.stderr,
                )
            return 1
        result = subprocess.run(step.command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        print_output(result)
        if result.returncode != 0:
            print(
                json.dumps(
                    {
                        "status": "fail",
                        "step": step.name,
                        "command": step.command,
                        "returncode": result.returncode,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return result.returncode
        print(f"PASS {step.name}")
    print(json.dumps({"status": "pass", "steps": len(steps())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
