#!/usr/bin/env python3
"""Run the local ChangeRail release verification baseline."""

from __future__ import annotations

import os
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
        Step("python runtime smoke", ["python3", "scripts/smoke-python-runtime.py"]),
        Step("windows entrypoint smoke", ["python3", "scripts/smoke-windows-entrypoints.py"]),
        Step("windows wiring Git safety smoke", ["python3", "scripts/smoke-windows-wiring-git-safety.py"]),
        Step("windows smoke matrix", ["python3", "scripts/smoke-windows-matrix.py"]),
        Step("python lint", ["ruff", "check", "bin", "scripts"]),
        Step("ci workflow contract", ["python3", "scripts/smoke-release-ci.py"]),
        Step("public surface scan self-test", ["python3", "scripts/public-surface-scan.py", "--self-test"]),
        Step("public surface scan", ["python3", "scripts/public-surface-scan.py"]),
        Step("public surface scan history", ["python3", "scripts/public-surface-scan.py", "--history"]),
        Step("wiring discovery smoke", ["python3", "scripts/smoke-wiring-discovery.py"]),
        Step("verify-project smoke", ["python3", "scripts/smoke-verify-project.py"]),
        Step("runtime diagnostics smoke", ["python3", "scripts/smoke-runtime-diagnostics.py"]),
        Step("bootstrap smoke", ["python3", "scripts/smoke-bootstrap-project.py"]),
        Step("consumer CI smoke", ["python3", "scripts/smoke-consumer-ci.py"]),
        Step("review verdict validation smoke", ["python3", "scripts/smoke-review-verdict-validation.py"]),
        Step("review fingerprint smoke", ["python3", "scripts/smoke-review-fingerprint.py"]),
        Step("review fingerprint benchmark smoke", ["python3", "scripts/smoke-review-fingerprint-benchmark.py"]),
        Step("review fingerprint cache smoke", ["python3", "scripts/smoke-review-fingerprint-cache.py"]),
        Step("review preflight smoke", ["python3", "scripts/smoke-review-preflight.py"]),
        Step("retained evidence smoke", ["python3", "scripts/smoke-retained-evidence.py"]),
        Step("maintenance runner smoke", ["python3", "scripts/smoke-maintenance-runner.py"]),
        Step("delivery manifest smoke", ["python3", "scripts/smoke-delivery-manifest.py"]),
        Step("delivery manifest derive smoke", ["python3", "scripts/smoke-delivery-manifest-derive.py"]),
        Step("delivery runner one-command smoke", ["python3", "scripts/smoke-delivery-runner.py"]),
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
                "--lock-enforcement",
                "none",
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
    from changerail_release_profile import main as run_profile
    return run_profile(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
