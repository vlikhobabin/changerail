#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCHEMA = "changerail.release-ci-smoke.v1"
ROOT = Path(__file__).resolve().parents[1]
CORE = (
    '["./bin/openspec", "validate", "--all", "--strict"]',
    '["python3", "-m", "json.tool", ".mcp.json"]',
    '["python3", "-c", "import tomllib; tomllib.load(open(\'.codex/config.toml\', \'rb\')); print(\'TOML_OK\')"]',
    '["python3", "scripts/smoke-contract-schemas.py"]',
    '["python3", "scripts/compile-python-inventory.py"]',
    '["python3", "scripts/smoke-python-runtime.py"]',
    '["ruff", "check", "bin", "scripts"]',
    '["python3", "scripts/smoke-source-distribution.py"]',
    '["python3", "scripts/smoke-release-ci.py"]',
    '["python3", "scripts/public-surface-scan.py", "--self-test"]',
    '["python3", "scripts/smoke-public-surface-history.py"]',
    '["python3", "scripts/public-surface-scan.py"]',
    '["python3", "scripts/public-surface-scan.py", "--history"]',
    '["python3", "scripts/smoke-wiring-discovery.py"]',
    '["python3", "scripts/smoke-verify-project.py"]',
    '["python3", "scripts/smoke-runtime-diagnostics.py"]',
    '["python3", "scripts/smoke-bootstrap-project.py"]',
    '["python3", "scripts/smoke-consumer-ci.py"]',
    '["rm", "-rf", ".runtime/changerail/ci-drift"]',
    '["./bin/bootstrap-project", ".runtime/changerail/ci-drift/example-project", "--name", "example-project", "--kind", "generic", "--lock-enforcement", "none"]',
    '["python3", "scripts/smoke-drift.py", "--project", ".runtime/changerail/ci-drift/example-project"]',
    '["git", "diff", "--check"]',
    '["git", "status", "--short", "--ignored"]',
)
EXTENDED = (
    '["python3", "scripts/smoke-review-verdict-validation.py"]',
    '["python3", "scripts/smoke-review-fingerprint.py"]',
    '["python3", "scripts/smoke-review-fingerprint-benchmark.py"]',
    '["python3", "scripts/smoke-review-fingerprint-cache.py"]',
    '["python3", "scripts/smoke-review-preflight.py"]',
    '["python3", "scripts/smoke-retained-evidence.py"]',
    '["python3", "scripts/smoke-maintenance-runner.py"]',
    '["python3", "scripts/smoke-delivery-manifest.py"]',
    '["python3", "scripts/smoke-delivery-manifest-derive.py"]',
    '["python3", "scripts/smoke-delivery-runner.py"]',
    '["python3", "scripts/smoke-delivery-metrics.py"]',
    '["python3", "scripts/smoke-openspec-archive-diagnostics.py"]',
)
DELIVERY = '["python3", "scripts/smoke-delivery-runner.py"]'
CHECKOUT = "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
SETUP_NODE = "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020"


def add(checks: list[dict[str, str]], name: str, ok: bool, message: str) -> None:
    checks.append({"name": name, "status": "pass" if ok else "fail", "message": message})


def inventory(*args: str) -> tuple[str, ...]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run-release-baseline.py"), *args, "--list"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    return tuple(result.stdout.splitlines())


def valid_inventories(core: tuple[str, ...], extended: tuple[str, ...]) -> bool:
    return core == CORE and extended == EXTENDED and len(set(core)) == len(core) and len(set(extended)) == len(extended) and not set(core) & set(extended) and DELIVERY not in core and extended.count(DELIVERY) == 1


def workflow_checks(checks: list[dict[str, str]], path: Path, *, extended: bool) -> None:
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = [line.strip() for line in text.splitlines()]
    route = "python3 scripts/run-release-baseline.py --suite extended" if extended else "python3 scripts/run-release-baseline.py"
    required = {
        "workflow exists": path.is_file(),
        "pinned checkout": CHECKOUT in text,
        "pinned setup node": SETUP_NODE in text,
        "full history checkout": "fetch-depth: 0" in lines,
        "exact suite route": lines.count("run: " + route) == 1,
        "manual trigger" if extended else "push trigger": ("workflow_dispatch:" if extended else "push:") in lines,
        "schedule trigger" if extended else "pull request trigger": ("schedule:" if extended else "pull_request:") in lines,
        "route isolation": (
            "run: python3 scripts/run-release-baseline.py" not in lines
            if extended else "run: python3 scripts/run-release-baseline.py --suite extended" not in lines
        ),
        "windows diagnostics excluded": not any("smoke-windows-" in line for line in lines),
        "one-command smoke not direct": not any("smoke-delivery-runner.py" in line for line in lines),
    }
    for name, ok in required.items():
        add(checks, ("extended " if extended else "core ") + name, ok, str(path))


def run_smoke(workflow: Path) -> dict[str, object]:
    checks: list[dict[str, str]] = []
    core, explicit_core, extended = inventory(), inventory("--suite", "core"), inventory("--suite", "extended")
    add(checks, "default core inventory", core == CORE, "exact ordered 23-item inventory")
    add(checks, "explicit core inventory", explicit_core == CORE, "default and explicit core match")
    add(checks, "extended inventory", extended == EXTENDED, "exact ordered 12-item inventory")
    add(checks, "inventory uniqueness", len(set(core)) == len(core) and len(set(extended)) == len(extended), "no duplicates")
    add(checks, "inventory disjointness", not set(core) & set(extended), "no overlap")
    add(checks, "one-command ownership", DELIVERY not in core and extended.count(DELIVERY) == 1, "extended only")
    mutations = ((CORE[:-1], EXTENDED), (CORE + ('["extra"]',), EXTENDED), (CORE + (CORE[0],), EXTENDED), (CORE, EXTENDED + (CORE[0],)), (CORE + (DELIVERY,), tuple(item for item in EXTENDED if item != DELIVERY)))
    add(checks, "negative inventory oracle", all(not valid_inventories(*item) for item in mutations), "missing/extra/duplicate/overlap/core-ownership rejected")
    workflow_checks(checks, workflow, extended=False)
    workflow_checks(checks, ROOT / ".github/workflows/changerail-extended.yml", extended=True)
    failed = sum(check["status"] != "pass" for check in checks)
    return {"schema": SCHEMA, "workflow": str(workflow), "summary": {"status": "fail" if failed else "pass", "total": len(checks), "passed": len(checks) - failed, "failed": failed}, "checks": checks}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate ChangeRail release suite contracts.")
    parser.add_argument("--workflow", type=Path, default=ROOT / ".github/workflows/changerail-ci.yml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = run_smoke(args.workflow)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(f"summary: {summary['status']} ({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)")
        for check in report["checks"]:
            if check["status"] != "pass":
                print(f"FAIL {check['name']}: {check['message']}")
    return 0 if report["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
