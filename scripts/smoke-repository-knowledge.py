#!/usr/bin/env python3
"""Smoke-test repository knowledge catalog and policy validation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from changerail_repository_knowledge import (  # noqa: E402
    Diagnostic,
    load_yaml,
    validate_catalog_and_policy,
    validate_catalog_document,
    validate_policy_document,
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )


def has_code(diagnostics: list[Diagnostic], code: str) -> bool:
    return any(diagnostic.code == code for diagnostic in diagnostics)


def snapshot_tree(path: Path) -> dict[str, bytes]:
    return {
        candidate.relative_to(path).as_posix(): candidate.read_bytes()
        for candidate in sorted(path.rglob("*"))
        if candidate.is_file()
    }


def detector_codes(payload: dict[str, object]) -> set[str]:
    codes: set[str] = set()
    detectors = payload.get("detectors")
    if not isinstance(detectors, list):
        return codes
    for detector in detectors:
        if not isinstance(detector, dict):
            continue
        for field in ("findings", "errors"):
            entries = detector.get(field)
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("code"), str):
                    codes.add(entry["code"])
    return codes


def main() -> int:
    failures: list[str] = []
    fixture_root = ROOT / "fixtures" / "repository-knowledge"

    valid = validate_catalog_and_policy(
        root=ROOT,
        catalog_path=Path("fixtures/repository-knowledge/valid/knowledge.yaml"),
        policy_path=Path("fixtures/repository-knowledge/valid/maintenance.yaml"),
    )
    if not valid.ok:
        failures.append(f"valid fixture failed: {[d.code for d in valid.diagnostics]}")

    dogfood = validate_catalog_and_policy(root=ROOT)
    if not dogfood.ok:
        failures.append(f"dogfood catalog failed: {[d.code for d in dogfood.diagnostics]}")

    missing_policy = validate_catalog_and_policy(
        root=ROOT,
        catalog_path=Path("fixtures/repository-knowledge/valid/knowledge.yaml"),
        policy_path=Path("fixtures/repository-knowledge/valid/missing-maintenance.yaml"),
    )
    if not missing_policy.ok or not has_code(missing_policy.diagnostics, "not_configured"):
        failures.append("missing policy did not validate as explicit no-op")

    invalid_catalog_cases = {
        "catalog unknown field": ("catalog-unknown-field.yaml", "schema_error"),
        "catalog traversal": ("catalog-traversal.yaml", "path_traversal"),
        "catalog active missing": ("catalog-active-missing.yaml", "active_path_missing"),
    }
    for label, (filename, expected_code) in invalid_catalog_cases.items():
        data, load_errors = load_yaml(fixture_root / "invalid" / filename)
        diagnostics = load_errors or validate_catalog_document(
            data,
            root=ROOT,
            path=Path("fixtures/repository-knowledge/invalid") / filename,
        )
        if not has_code(diagnostics, expected_code):
            failures.append(f"{label}: expected {expected_code}, got {[d.code for d in diagnostics]}")

    invalid_policy_cases = {
        "policy unknown field": ("policy-unknown-field.yaml", "schema_error"),
        "policy traversal": ("policy-traversal.yaml", "path_traversal"),
        "policy scan traversal": ("policy-scan-traversal.yaml", "path_traversal"),
    }
    for label, (filename, expected_code) in invalid_policy_cases.items():
        data, load_errors = load_yaml(fixture_root / "invalid" / filename)
        diagnostics = load_errors or validate_policy_document(
            data,
            root=ROOT,
            path=Path("fixtures/repository-knowledge/invalid") / filename,
        )
        if not has_code(diagnostics, expected_code):
            failures.append(f"{label}: expected {expected_code}, got {[d.code for d in diagnostics]}")

    runtime = ROOT / ".runtime" / "changerail" / "repository-knowledge-smoke"
    runtime.mkdir(parents=True, exist_ok=True)
    policy = runtime / "maintenance.yaml"
    index = runtime / "KNOWLEDGE.md"
    catalog_rel = "fixtures/repository-knowledge/valid/knowledge.yaml"
    policy.write_text(
        "schema: changerail.maintenance-policy.v1\n"
        f"catalog_path: {catalog_rel}\n"
        f"generated_index_path: {rel(index)}\n",
        encoding="utf-8",
    )

    validate_cli = run(
        [
            "bin/changerail-maintenance",
            "validate-catalog",
            "--catalog",
            catalog_rel,
            "--policy",
            rel(policy),
            "--json",
        ]
    )
    if validate_cli.returncode != 0:
        failures.append(f"validate-catalog CLI failed: {validate_cli.stderr or validate_cli.stdout}")

    invalid_override = run(["bin/changerail-maintenance", "validate-catalog", "--catalog", "/tmp/outside.yaml"])
    if invalid_override.returncode == 0:
        failures.append("validate-catalog accepted absolute path override")

    invalid_json = run(
        [
            "bin/changerail-maintenance",
            "validate-catalog",
            "--catalog",
            "fixtures/repository-knowledge/invalid/catalog-traversal.yaml",
            "--policy",
            "fixtures/repository-knowledge/valid/maintenance.yaml",
            "--json",
        ]
    )
    try:
        invalid_json_payload = json.loads(invalid_json.stdout)
    except ValueError as exc:
        invalid_json_payload = {}
        failures.append(f"invalid validate-catalog --json output is not one JSON object: {exc}")
    if (
        invalid_json.returncode == 0
        or invalid_json_payload.get("ok") is not False
        or not invalid_json_payload.get("diagnostics")
    ):
        failures.append("invalid validate-catalog --json did not return one structured failure payload")

    index.write_text("stale index\n", encoding="utf-8")
    before_check = index.read_text(encoding="utf-8")
    stale_check = run(
        [
            "bin/changerail-maintenance",
            "render-index",
            "--catalog",
            catalog_rel,
            "--policy",
            rel(policy),
            "--check",
            "--json",
        ]
    )
    after_check = index.read_text(encoding="utf-8")
    if stale_check.returncode == 0 or before_check != after_check or "index_drift" not in stale_check.stdout:
        failures.append("render-index --check did not report stale index without mutation")

    write_index = run(
        [
            "bin/changerail-maintenance",
            "render-index",
            "--catalog",
            catalog_rel,
            "--policy",
            rel(policy),
            "--write",
            "--json",
        ]
    )
    if write_index.returncode != 0:
        failures.append(f"render-index --write failed: {write_index.stderr or write_index.stdout}")
    first_render = index.read_text(encoding="utf-8")
    write_again = run(
        [
            "bin/changerail-maintenance",
            "render-index",
            "--catalog",
            catalog_rel,
            "--policy",
            rel(policy),
            "--write",
            "--json",
        ]
    )
    second_render = index.read_text(encoding="utf-8")
    if write_again.returncode != 0 or first_render != second_render:
        failures.append("render-index --write is not idempotent")

    current_check = run(
        [
            "bin/changerail-maintenance",
            "render-index",
            "--catalog",
            catalog_rel,
            "--policy",
            rel(policy),
            "--check",
        ]
    )
    if current_check.returncode != 0:
        failures.append(f"render-index --check failed after write: {current_check.stderr or current_check.stdout}")

    scan_fixture = fixture_root / "scan"
    before_scan = snapshot_tree(scan_fixture)
    scan_result = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(scan_fixture),
            "scan",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--json",
        ]
    )
    after_scan = snapshot_tree(scan_fixture)
    try:
        scan_payload = json.loads(scan_result.stdout)
    except ValueError as exc:
        scan_payload = {}
        failures.append(f"scan --json output is not one JSON object: {exc}")
    expected_scan_codes = {
        "uncovered_knowledge_file",
        "missing_catalog_target",
        "orphan_discovered_file",
        "missing_link_target",
        "stale_anchor",
        "stale_generated_output",
        "forbidden_active_reference",
    }
    observed_scan_codes = detector_codes(scan_payload)
    if scan_result.returncode != 1:
        failures.append(f"scan fixture expected exit 1, got {scan_result.returncode}: {scan_result.stderr or scan_result.stdout}")
    if scan_payload.get("schema") != "changerail.maintenance-scan-report.v1" or scan_payload.get("complete") is not True:
        failures.append("scan fixture did not produce a complete maintenance scan report")
    missing_scan_codes = sorted(expected_scan_codes - observed_scan_codes)
    if missing_scan_codes:
        failures.append(f"scan fixture missing detector code(s): {', '.join(missing_scan_codes)}")
    if before_scan != after_scan:
        failures.append("scan fixture mutated repository files")

    adapter_fixture = fixture_root / "adapters"
    before_adapter_scan = snapshot_tree(adapter_fixture)
    adapter_result = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(adapter_fixture),
            "scan",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--json",
        ]
    )
    after_adapter_scan = snapshot_tree(adapter_fixture)
    try:
        adapter_payload = json.loads(adapter_result.stdout)
    except ValueError as exc:
        adapter_payload = {}
        failures.append(f"adapter scan --json output is not one JSON object: {exc}")
    expected_adapter_codes = {
        "adapter_fixture_finding",
        "invalid_adapter_json",
        "invalid_adapter_output",
        "unsafe_adapter_path",
        "adapter_nonzero_exit",
        "adapter_timeout",
    }
    observed_adapter_codes = detector_codes(adapter_payload)
    if adapter_result.returncode != 1:
        failures.append(
            f"adapter scan fixture expected exit 1, got {adapter_result.returncode}: "
            f"{adapter_result.stderr or adapter_result.stdout}"
        )
    if adapter_payload.get("schema") != "changerail.maintenance-scan-report.v1" or adapter_payload.get("complete") is not True:
        failures.append("adapter scan fixture did not produce a complete maintenance scan report")
    missing_adapter_codes = sorted(expected_adapter_codes - observed_adapter_codes)
    if missing_adapter_codes:
        failures.append(f"adapter scan fixture missing detector code(s): {', '.join(missing_adapter_codes)}")
    if before_adapter_scan != after_adapter_scan:
        failures.append("adapter scan fixture mutated repository files")

    dogfood_scan = run(["bin/changerail-maintenance", "scan", "--json"])
    try:
        dogfood_scan_payload = json.loads(dogfood_scan.stdout)
    except ValueError as exc:
        dogfood_scan_payload = {}
        failures.append(f"dogfood scan --json output is not one JSON object: {exc}")
    if (
        dogfood_scan.returncode != 0
        or dogfood_scan_payload.get("schema") != "changerail.maintenance-scan-report.v1"
        or dogfood_scan_payload.get("complete") is not True
    ):
        failures.append(f"dogfood scan failed: {dogfood_scan.stderr or dogfood_scan.stdout}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print("SMOKE_REPOSITORY_KNOWLEDGE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
