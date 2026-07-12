#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SCHEMA = "changerail.release-ci-smoke.v1"

REQUIRED_SNIPPETS = {
    "trigger push": "push:",
    "trigger pull request": "pull_request:",
    "trigger manual dispatch": "workflow_dispatch:",
    "checkout action pin": "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
    "checkout action version comment": "actions/checkout v4",
    "node setup action pin": "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",
    "node setup action version comment": "actions/setup-node v4",
    "toml config check": "import tomllib",
    "drift fixture bootstrap": "./bin/bootstrap-project .runtime/changerail/ci-drift/example-project",
    "drift uses generated project": "--project .runtime/changerail/ci-drift/example-project",
}

REQUIRED_COMMANDS = {
    "python release venv": "python3 -m venv .runtime/changerail/ci-venv",
    "python release dependencies": ".runtime/changerail/ci-venv/bin/python -m pip install --disable-pip-version-check -r requirements-dev.txt",
    "openspec validation": "./bin/openspec validate --all --strict",
    "json config check": "python3 -m json.tool .mcp.json",
    "whitespace check": "git diff --check",
    "contract schema validation": "python3 scripts/smoke-contract-schemas.py",
    "python syntax inventory": "python3 scripts/compile-python-inventory.py",
    "python lint": "ruff check bin scripts",
    "release ci smoke": "python3 scripts/smoke-release-ci.py",
    "public surface scan self-test": "python3 scripts/public-surface-scan.py --self-test",
    "public surface scan": "python3 scripts/public-surface-scan.py",
    "public surface scan history": "python3 scripts/public-surface-scan.py --history",
    "wiring smoke": "python3 scripts/smoke-wiring-discovery.py",
    "verify smoke": "python3 scripts/smoke-verify-project.py",
    "bootstrap smoke": "python3 scripts/smoke-bootstrap-project.py",
    "review verdict validation smoke": "python3 scripts/smoke-review-verdict-validation.py",
    "review fingerprint smoke": "python3 scripts/smoke-review-fingerprint.py",
    "delivery manifest smoke": "python3 scripts/smoke-delivery-manifest.py",
    "delivery manifest derive smoke": "python3 scripts/smoke-delivery-manifest-derive.py",
    "delivery runner smoke": "python3 scripts/smoke-delivery-runner.py",
    "delivery metrics smoke": "python3 scripts/smoke-delivery-metrics.py",
    "openspec archive diagnostics smoke": "python3 scripts/smoke-openspec-archive-diagnostics.py",
    "drift smoke": "python3 scripts/smoke-drift.py",
}

FORBIDDEN_SNIPPETS = {
    "private absolute project path": "/opt" + "/",
    "private drift inventory": "internal/changerail-drift.json",
    "ci drift config inventory": "smoke-drift.py --config",
    "mutable checkout action tag": "actions/checkout@v4",
    "mutable setup-node action tag": "actions/setup-node@v4",
}


@dataclass
class Check:
    name: str
    status: str
    message: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def check_required(text: str) -> list[Check]:
    checks: list[Check] = []
    for name, snippet in REQUIRED_SNIPPETS.items():
        if snippet in text:
            checks.append(Check(name, "pass", "required snippet present"))
        else:
            checks.append(Check(name, "fail", f"missing required snippet: {snippet}"))
    return checks


def command_inventory(text: str) -> set[str]:
    commands: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "|":
            continue
        if line.startswith("run: "):
            value = line.removeprefix("run: ").strip()
            if value and value != "|":
                commands.add(value)
            continue
        if line.startswith(("python3 ", "./bin/", ".runtime/", "ruff ", "git ", "rm ")):
            commands.add(line.removesuffix("\\").rstrip())
    return commands


def check_required_commands(text: str) -> list[Check]:
    checks: list[Check] = []
    commands = command_inventory(text)
    for name, command in REQUIRED_COMMANDS.items():
        if command in commands:
            checks.append(Check(name, "pass", "required command present"))
        else:
            checks.append(Check(name, "fail", f"missing required command: {command}"))
    return checks


def check_forbidden(text: str) -> list[Check]:
    checks: list[Check] = []
    for name, snippet in FORBIDDEN_SNIPPETS.items():
        if snippet in text:
            checks.append(Check(name, "fail", f"forbidden snippet present: {snippet}"))
        else:
            checks.append(Check(name, "pass", "forbidden snippet absent"))
    return checks


def run_smoke(workflow: Path) -> dict[str, object]:
    checks: list[Check] = []
    if not workflow.is_file():
        checks.append(Check("workflow exists", "fail", f"missing workflow: {workflow}"))
        text = ""
    else:
        checks.append(Check("workflow exists", "pass", f"found workflow: {workflow}"))
        text = workflow.read_text(encoding="utf-8")

    checks.extend(check_required(text))
    checks.extend(check_required_commands(text))
    checks.extend(check_forbidden(text))
    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "workflow": str(workflow),
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description="Validate ChangeRail CI workflow contract.")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=root / ".github" / "workflows" / "changerail-ci.yml",
        help="Path to the ChangeRail CI workflow.",
    )
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = run_smoke(args.workflow)
    summary = report["summary"]
    if args.json:
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
