#!/usr/bin/env python3
"""Smoke-test repository knowledge catalog and policy validation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from changerail_repository_knowledge import (  # noqa: E402
    Diagnostic,
    load_yaml,
    normalize_maintenance_report,
    validate_catalog_and_policy,
    validate_catalog_document,
    validate_lifecycle_report,
    validate_maintenance_baseline,
    validate_maintenance_state,
    validate_maintenance_triage,
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


def snapshot_non_runtime_tree(path: Path) -> dict[str, bytes]:
    return {
        candidate.relative_to(path).as_posix(): candidate.read_bytes()
        for candidate in sorted(path.rglob("*"))
        if candidate.is_file() and ".runtime" not in candidate.relative_to(path).parts
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

    feedback_fixture = fixture_root / "feedback"
    before_feedback = snapshot_tree(feedback_fixture)
    feedback_result = run(
        [
            "bin/changerail-maintenance",
            "feedback",
            "--adapter-id",
            "lifecycle",
            "--review-history",
            "fixtures/repository-knowledge/feedback/review-history.json",
            "--delivery-run",
            "fixtures/repository-knowledge/feedback/delivery-blocked.json",
            "--delivery-run",
            "fixtures/repository-knowledge/feedback/delivery-delivered.json",
            "--detector-result",
            "fixtures/repository-knowledge/feedback/external-valid.json",
            "--json",
        ]
    )
    after_feedback = snapshot_tree(feedback_fixture)
    try:
        feedback_payload = json.loads(feedback_result.stdout)
    except ValueError as exc:
        feedback_payload = {}
        failures.append(f"feedback output is not one JSON object: {exc}")
    feedback_findings = feedback_payload.get("findings") if isinstance(feedback_payload.get("findings"), list) else []
    feedback_codes = {finding.get("code") for finding in feedback_findings if isinstance(finding, dict)}
    feedback_text = json.dumps(feedback_payload, ensure_ascii=True)
    if (
        feedback_result.returncode != 0
        or feedback_payload.get("schema") != "changerail.maintenance-detector-result.v1"
        or feedback_payload.get("id") != "adapter-lifecycle"
        or feedback_payload.get("status") != "fail"
    ):
        failures.append(f"feedback valid fixture did not emit adapter result: {feedback_result.stderr or feedback_result.stdout}")
    expected_feedback_codes = {"review_cycle_finding", "blocked_delivery_run", "external_fixture_finding"}
    if not expected_feedback_codes.issubset(feedback_codes):
        failures.append(f"feedback fixture missing finding code(s): {sorted(expected_feedback_codes - feedback_codes)}")
    if len(feedback_findings) != 4:
        failures.append(f"feedback fixture expected 4 normalized findings, got {len(feedback_findings)}")
    if "Review prose must stay" in feedback_text or "Detailed review prose" in feedback_text:
        failures.append("feedback copied review summary/detail prose into normalized output")
    if before_feedback != after_feedback:
        failures.append("feedback command mutated fixture files")

    same_path_feedback = run(
        [
            "bin/changerail-maintenance",
            "feedback",
            "--adapter-id",
            "lifecycle",
            "--review-history",
            "fixtures/repository-knowledge/feedback/review-history-same-path.json",
            "--json",
        ]
    )
    try:
        same_path_feedback_payload = json.loads(same_path_feedback.stdout)
    except ValueError as exc:
        same_path_feedback_payload = {}
        failures.append(f"same-path review feedback output is not one JSON object: {exc}")
    same_path_findings = (
        same_path_feedback_payload.get("findings")
        if isinstance(same_path_feedback_payload.get("findings"), list)
        else []
    )
    same_path_scan = {
        "schema": "changerail.maintenance-scan-report.v1",
        "generated_at": "2026-08-09T00:10:00Z",
        "workspace": {"root": ROOT.as_posix()},
        "catalog_path": ".changerail/knowledge.yaml",
        "policy_path": ".changerail/maintenance.yaml",
        "complete": True,
        "fail_on": "major",
        "detectors": [same_path_feedback_payload] if isinstance(same_path_feedback_payload, dict) else [],
        "configuration_diagnostics": [],
        "summary": {
            "detectors": 1,
            "findings": len(same_path_findings),
            "errors": 0,
            "max_severity": "blocker",
            "threshold_reached": True,
        },
    }
    same_path_report, same_path_exit = normalize_maintenance_report(
        same_path_scan,
        root=ROOT,
        state_path=".runtime/changerail/maintenance/same-path-review-feedback-state.json",
    )
    same_path_lifecycle_findings = (
        same_path_report.get("findings") if isinstance(same_path_report.get("findings"), list) else []
    )
    same_path_fingerprints = {
        finding.get("fingerprint")
        for finding in same_path_lifecycle_findings
        if isinstance(finding, dict)
    }
    same_path_subject_ids = {
        finding.get("subject", {}).get("original_finding_id")
        for finding in same_path_lifecycle_findings
        if isinstance(finding, dict) and isinstance(finding.get("subject"), dict)
    }
    if same_path_feedback.returncode != 0 or len(same_path_findings) != 2:
        failures.append("same-path review feedback fixture did not emit two normalized findings")
    if (
        same_path_exit != 1
        or validate_lifecycle_report(same_path_report)
        or len(same_path_lifecycle_findings) != 2
        or len(same_path_fingerprints) != 2
        or same_path_subject_ids != {"R1", "R2"}
    ):
        failures.append("same-path review feedback findings collapsed to one lifecycle identity")

    feedback_error = run(
        [
            "bin/changerail-maintenance",
            "feedback",
            "--adapter-id",
            "lifecycle",
            "--review-history",
            "fixtures/repository-knowledge/feedback/review-history-unsafe-path.json",
            "--delivery-run",
            "fixtures/repository-knowledge/feedback/delivery-blocked-prose-only.json",
            "--detector-result",
            "fixtures/repository-knowledge/feedback/external-unsafe.json",
            "--json",
        ]
    )
    try:
        feedback_error_payload = json.loads(feedback_error.stdout)
    except ValueError as exc:
        feedback_error_payload = {}
        failures.append(f"feedback error output is not one JSON object: {exc}")
    feedback_error_codes = {
        error.get("code")
        for error in feedback_error_payload.get("errors", [])
        if isinstance(error, dict)
    }
    expected_feedback_errors = {
        "unsupported_review_history",
        "unsupported_delivery_run",
        "unsafe_feedback_path",
    }
    if (
        feedback_error.returncode != 0
        or feedback_error_payload.get("status") != "error"
        or not expected_feedback_errors.issubset(feedback_error_codes)
    ):
        failures.append(f"feedback invalid fixture did not fail closed: {feedback_error.stderr or feedback_error.stdout}")

    quality_fixture = fixture_root / "quality"
    before_quality = snapshot_tree(quality_fixture)
    quality_json = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--report",
            "fixtures/repository-knowledge/quality/report-latest.json",
            "--history",
            "fixtures/repository-knowledge/quality/report-earlier.json",
            "--triage",
            "fixtures/repository-knowledge/quality/triage.json",
            "--proposal",
            "fixtures/repository-knowledge/quality/proposal-accepted.json",
            "--proposal",
            "fixtures/repository-knowledge/quality/proposal-rejected.json",
            "--json",
        ]
    )
    after_quality = snapshot_tree(quality_fixture)
    try:
        quality_payload = json.loads(quality_json.stdout)
    except ValueError as exc:
        quality_payload = {}
        failures.append(f"quality --json output is not one JSON object: {exc}")
    quality_metrics = {
        metric.get("id"): metric
        for metric in quality_payload.get("metrics", [])
        if isinstance(metric, dict)
    }
    expected_quality_values = {
        "findings.open": 0,
        "findings.accepted": 1,
        "findings.waived": 1,
        "findings.resolved": 1,
        "proposals.accepted": 1,
        "proposals.rejected": 1,
        "triage.time_to_triage_seconds": 1800,
        "stale_generated.findings": 1,
        "board.dedup.missing": 2,
    }
    if quality_json.returncode != 0 or quality_payload.get("schema") != "changerail.maintenance-quality-rollup.v1":
        failures.append(f"quality --json did not emit schema-valid rollup: {quality_json.stderr or quality_json.stdout}")
    for metric_id, expected_value in expected_quality_values.items():
        metric = quality_metrics.get(metric_id, {})
        if metric.get("value") != expected_value or metric.get("status") != "known":
            failures.append(f"quality metric {metric_id} expected known {expected_value}, got {metric}")
    if quality_metrics.get("instruction.bytes", {}).get("status") != "unknown":
        failures.append("quality instruction bytes did not remain unknown without producer input")
    if quality_metrics.get("catalog.records.total", {}).get("status") != "known":
        failures.append("quality catalog records metric was not calculated from tracked catalog")
    if before_quality != after_quality:
        failures.append("quality command mutated fixture files")

    quality_csv = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--report",
            "fixtures/repository-knowledge/quality/report-latest.json",
            "--csv",
        ]
    )
    csv_lines = quality_csv.stdout.splitlines()
    if quality_csv.returncode != 0 or not csv_lines or csv_lines[0] != "metric,value,unit,status":
        failures.append(f"quality --csv did not emit stable header: {quality_csv.stderr or quality_csv.stdout}")
    if not any(line == "instruction.bytes,unknown,bytes,unknown" for line in csv_lines):
        failures.append("quality --csv did not render unknown instruction bytes")

    quality_text = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--report",
            "fixtures/repository-knowledge/quality/report-latest.json",
        ]
    )
    if quality_text.returncode != 0 or "findings.open" not in quality_text.stdout:
        failures.append(f"quality text output did not include metric ids: {quality_text.stderr or quality_text.stdout}")

    quality_incomplete = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--report",
            "fixtures/repository-knowledge/quality/report-latest.json",
            "--history",
            "fixtures/repository-knowledge/quality/report-incomplete.json",
            "--json",
        ]
    )
    try:
        quality_incomplete_payload = json.loads(quality_incomplete.stdout)
    except ValueError:
        quality_incomplete_payload = {}
    incomplete_metrics = {
        metric.get("id"): metric
        for metric in quality_incomplete_payload.get("metrics", [])
        if isinstance(metric, dict)
    }
    if incomplete_metrics.get("findings.resolved", {}).get("status") != "unknown":
        failures.append("quality incomplete history did not render resolved count as unknown")

    quality_invalid_proposal = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--report",
            "fixtures/repository-knowledge/quality/report-latest.json",
            "--proposal",
            "fixtures/repository-knowledge/quality/proposal-invalid.json",
            "--json",
        ]
    )
    try:
        quality_invalid_payload = json.loads(quality_invalid_proposal.stdout)
    except ValueError:
        quality_invalid_payload = {}
    quality_invalid_codes = {
        diagnostic.get("code")
        for diagnostic in quality_invalid_payload.get("diagnostics", [])
        if isinstance(diagnostic, dict)
    }
    if quality_invalid_proposal.returncode == 0 or "proposal_decision_invalid" not in quality_invalid_codes:
        failures.append("quality invalid proposal decision did not fail closed")

    contradiction_fixture = quality_fixture / "contradiction-annotation.json"
    try:
        contradiction_payload = json.loads(contradiction_fixture.read_text(encoding="utf-8"))
    except ValueError as exc:
        contradiction_payload = {}
        failures.append(f"contradiction annotation fixture is not JSON: {exc}")
    contradiction_evidence_refs = (
        contradiction_payload.get("evidence_refs")
        if isinstance(contradiction_payload.get("evidence_refs"), list)
        else []
    )
    if (
        contradiction_payload.get("schema") != "changerail.maintenance-proposal-decision.v1"
        or contradiction_payload.get("transformation_class") != "contradiction-annotation"
        or not any(
            isinstance(ref, dict)
            and ref.get("kind") == "model_annotation"
            and ref.get("value") == "evidence_only"
            for ref in contradiction_evidence_refs
        )
    ):
        failures.append("contradiction annotation fixture is not retained as schema-valid evidence")
    contradiction_quality = run(
        [
            "bin/changerail-maintenance",
            "quality",
            "--proposal",
            "fixtures/repository-knowledge/quality/contradiction-annotation.json",
            "--json",
        ]
    )
    try:
        contradiction_quality_payload = json.loads(contradiction_quality.stdout)
    except ValueError:
        contradiction_quality_payload = {}
    contradiction_metrics = {
        metric.get("id"): metric
        for metric in contradiction_quality_payload.get("metrics", [])
        if isinstance(metric, dict)
    }
    if (
        contradiction_quality.returncode != 0
        or contradiction_quality_payload.get("schema") != "changerail.maintenance-quality-rollup.v1"
        or contradiction_metrics.get("proposals.rejected", {}).get("value") != 1
    ):
        failures.append("quality rollup did not accept contradiction annotation evidence as proposal input")

    dogfood_status_before = run(["git", "status", "--short", "--untracked-files=all"])
    dogfood_scan = run(["bin/changerail-maintenance", "scan", "--json"])
    dogfood_status_after = run(["git", "status", "--short", "--untracked-files=all"])
    try:
        dogfood_scan_payload = json.loads(dogfood_scan.stdout)
    except ValueError as exc:
        dogfood_scan_payload = {}
        failures.append(f"dogfood scan --json output is not one JSON object: {exc}")
    dogfood_summary = dogfood_scan_payload.get("summary") if isinstance(dogfood_scan_payload.get("summary"), dict) else {}
    dogfood_detector_ids = {
        detector.get("id")
        for detector in dogfood_scan_payload.get("detectors", [])
        if isinstance(detector, dict) and isinstance(detector.get("id"), str)
    }
    expected_dogfood_detectors = {
        "catalog-coverage",
        "repository-orphans",
        "markdown-local-links",
        "generated-freshness",
        "forbidden-active-references",
    }
    if (
        dogfood_scan.returncode != 0
        or dogfood_scan_payload.get("schema") != "changerail.maintenance-scan-report.v1"
        or dogfood_scan_payload.get("complete") is not True
    ):
        failures.append(f"dogfood scan failed: {dogfood_scan.stderr or dogfood_scan.stdout}")
    if dogfood_summary.get("detectors", 0) <= 0:
        failures.append("dogfood scan did not exercise deterministic detector coverage")
    missing_dogfood_detectors = sorted(expected_dogfood_detectors - dogfood_detector_ids)
    if missing_dogfood_detectors:
        failures.append(f"dogfood scan missing detector(s): {', '.join(missing_dogfood_detectors)}")
    if "adapters" in dogfood_detector_ids or any(detector_id.startswith("adapter-") for detector_id in dogfood_detector_ids):
        failures.append("dogfood scan enabled runtime-dependent adapters by default")
    if dogfood_status_before.stdout != dogfood_status_after.stdout:
        failures.append("dogfood scan mutated git-visible repository files")
    if any("contradiction" in code for code in detector_codes(dogfood_scan_payload)):
        failures.append("dogfood scan treated model-only contradiction annotation as a deterministic finding")

    lifecycle_root = ROOT / ".runtime" / "changerail" / "repository-knowledge-lifecycle-smoke"
    shutil.rmtree(lifecycle_root, ignore_errors=True)
    (lifecycle_root / ".changerail").mkdir(parents=True, exist_ok=True)
    (lifecycle_root / "docs").mkdir(parents=True, exist_ok=True)
    (lifecycle_root / "openspec" / "board" / "1.backlog").mkdir(parents=True, exist_ok=True)
    for lane in ("2.todo", "3.inprogress", "4.done", "5.canceled"):
        (lifecycle_root / "openspec" / "board" / lane).mkdir(parents=True, exist_ok=True)
    (lifecycle_root / "docs" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
    (lifecycle_root / "knowledge.yaml").write_text(
        "schema: changerail.repository-knowledge.v1\nrecords: []\n",
        encoding="utf-8",
    )
    (lifecycle_root / "maintenance.yaml").write_text(
        "schema: changerail.maintenance-policy.v1\n"
        "catalog_path: knowledge.yaml\n"
        "generated_index_path: KNOWLEDGE.md\n"
        "scan:\n"
        "  include_globs:\n"
        "    - docs/*.md\n"
        "  enabled_detectors:\n"
        "    - catalog-coverage\n"
        "  fail_on: major\n",
        encoding="utf-8",
    )

    lifecycle_report = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--json",
            "--write-state",
        ]
    )
    try:
        lifecycle_payload = json.loads(lifecycle_report.stdout)
    except ValueError as exc:
        lifecycle_payload = {}
        failures.append(f"maintenance report output is not JSON: {exc}")
    if lifecycle_report.returncode != 1:
        failures.append(f"maintenance report expected threshold exit 1, got {lifecycle_report.returncode}")
    if validate_lifecycle_report(lifecycle_payload):
        failures.append("maintenance lifecycle report failed schema validation")
    findings = lifecycle_payload.get("findings") if isinstance(lifecycle_payload.get("findings"), list) else []
    if len(findings) != 1 or findings[0].get("status") != "open":
        failures.append("maintenance lifecycle report did not expose one open finding")
    first_seen = findings[0].get("first_seen") if findings and isinstance(findings[0], dict) else None
    state_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "state.json"
    try:
        state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        state_payload = {}
        failures.append(f"maintenance state was not written as JSON: {exc}")
    if validate_maintenance_state(state_payload):
        failures.append("maintenance state failed schema validation after --write-state")

    bad_state_report = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--state",
            ".changerail/bad-state.json",
            "--json",
            "--write-state",
        ]
    )
    if (
        bad_state_report.returncode != 2
        or "maintenance_state_path_invalid" not in bad_state_report.stdout
        or (lifecycle_root / ".changerail" / "bad-state.json").exists()
    ):
        failures.append("maintenance report allowed --write-state outside ignored runtime root")

    lifecycle_report_again = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--json",
            "--write-state",
        ]
    )
    try:
        lifecycle_again_payload = json.loads(lifecycle_report_again.stdout)
    except ValueError:
        lifecycle_again_payload = {}
    again_findings = lifecycle_again_payload.get("findings") if isinstance(lifecycle_again_payload.get("findings"), list) else []
    if (
        lifecycle_report_again.returncode != 1
        or not again_findings
        or again_findings[0].get("first_seen") != first_seen
        or lifecycle_again_payload.get("state", {}).get("restored") is not True
    ):
        failures.append("maintenance state continuity did not preserve first_seen")

    custom_scan = {
        "schema": "changerail.maintenance-scan-report.v1",
        "generated_at": "2026-08-09T00:00:00Z",
        "workspace": {"root": lifecycle_root.as_posix()},
        "catalog_path": "knowledge.yaml",
        "policy_path": "maintenance.yaml",
        "complete": True,
        "fail_on": "major",
        "detectors": [
            {
                "schema": "changerail.maintenance-detector-result.v1",
                "id": "catalog-coverage",
                "status": "fail",
                "findings": [
                    {
                        "id": "catalog-coverage:uncovered:docs-orphan",
                        "severity": "major",
                        "code": "uncovered_knowledge_file",
                        "message": "first message",
                        "path": "docs/orphan.md",
                        "evidence": {"line": 1},
                    }
                ],
                "errors": [],
            }
        ],
        "configuration_diagnostics": [],
        "summary": {"detectors": 1, "findings": 1, "errors": 0, "max_severity": "major", "threshold_reached": True},
    }
    identity_report_a, _ = normalize_maintenance_report(custom_scan, root=lifecycle_root, state_path=".runtime/changerail/maintenance/identity-a.json")
    custom_scan["detectors"][0]["findings"][0]["message"] = "second message"
    custom_scan["detectors"][0]["findings"][0]["evidence"] = {"line": 2}
    identity_report_b, _ = normalize_maintenance_report(custom_scan, root=lifecycle_root, state_path=".runtime/changerail/maintenance/identity-b.json")
    finding_a = identity_report_a["findings"][0]
    finding_b = identity_report_b["findings"][0]
    if finding_a["fingerprint"] != finding_b["fingerprint"]:
        failures.append("maintenance identity changed after message/evidence-only update")
    if finding_a["evidence_fingerprint"] == finding_b["evidence_fingerprint"]:
        failures.append("maintenance evidence fingerprint did not change after material evidence update")

    unsafe_scan = json.loads(json.dumps(custom_scan))
    sensitive_fixture = "token" + "=" + "example-secret-value"
    unsafe_scan["detectors"][0]["findings"][0]["evidence"] = {"raw": sensitive_fixture}
    unsafe_report, unsafe_exit = normalize_maintenance_report(
        unsafe_scan,
        root=lifecycle_root,
        state_path=".runtime/changerail/maintenance/unsafe.json",
    )
    unsafe_codes = {diagnostic.get("code") for diagnostic in unsafe_report.get("diagnostics", [])}
    if unsafe_exit != 2 or "secret_like_evidence" not in unsafe_codes:
        failures.append("maintenance lifecycle did not reject secret-like evidence")

    report_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(lifecycle_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    report_rel = report_path.relative_to(lifecycle_root).as_posix()

    state_before_corrupt = state_path.read_text(encoding="utf-8")
    state_path.write_text("{not json\n", encoding="utf-8")
    corrupt_report = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--catalog",
            "knowledge.yaml",
            "--policy",
            "maintenance.yaml",
            "--json",
            "--write-state",
        ]
    )
    if corrupt_report.returncode != 2 or state_path.read_text(encoding="utf-8") != "{not json\n":
        failures.append("corrupt maintenance state was not rejected without replacement")
    state_path.write_text(state_before_corrupt, encoding="utf-8")

    non_runtime_before = snapshot_non_runtime_tree(lifecycle_root)
    baseline_preview = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "accept-baseline",
            "--report",
            report_rel,
            "--json",
        ]
    )
    non_runtime_after_preview = snapshot_non_runtime_tree(lifecycle_root)
    if baseline_preview.returncode != 0 or non_runtime_before != non_runtime_after_preview:
        failures.append("accept-baseline preview mutated non-runtime files")

    baseline_write = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "accept-baseline",
            "--report",
            report_rel,
            "--write",
            "--json",
        ]
    )
    baseline_path = lifecycle_root / ".changerail" / "maintenance-baseline.yaml"
    baseline_data, baseline_load = load_yaml(baseline_path)
    if baseline_write.returncode != 0 or baseline_load or validate_maintenance_baseline(baseline_data):
        failures.append("accept-baseline --write did not create a valid baseline")

    expired_baseline = lifecycle_root / ".changerail" / "expired-baseline.yaml"
    fingerprint = findings[0]["fingerprint"] if findings else "sha256:" + ("0" * 64)
    expired_baseline.write_text(
        "schema: changerail.maintenance-baseline.v1\n"
        "accepted: []\n"
        "waivers:\n"
        f"  - fingerprint: {fingerprint}\n"
        "    owner: ChangeRail core\n"
        "    reason: expired smoke waiver\n"
        "    expires_at: 2000-01-01\n",
        encoding="utf-8",
    )
    expired_scan_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "scan.json"
    expired_scan_path.write_text(json.dumps(custom_scan, ensure_ascii=True), encoding="utf-8")
    expired_scan_rel = expired_scan_path.relative_to(lifecycle_root).as_posix()
    expired_report = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--scan-report",
            expired_scan_rel,
            "--baseline",
            expired_baseline.relative_to(lifecycle_root).as_posix(),
            "--json",
        ]
    )
    try:
        expired_payload = json.loads(expired_report.stdout)
    except ValueError:
        expired_payload = {}
    expired_findings = expired_payload.get("findings") if isinstance(expired_payload.get("findings"), list) else []
    expired_codes = {diagnostic.get("code") for diagnostic in expired_payload.get("diagnostics", []) if isinstance(diagnostic, dict)}
    if (
        expired_report.returncode != 1
        or not expired_findings
        or expired_findings[0].get("status") != "open"
        or "expired_maintenance_waiver" not in expired_codes
    ):
        failures.append("expired waiver did not fail open with an open finding")

    future_baseline = lifecycle_root / ".changerail" / "future-baseline.yaml"
    future_baseline.write_text(
        "schema: changerail.maintenance-baseline.v1\n"
        "accepted: []\n"
        "waivers:\n"
        f"  - fingerprint: {fingerprint}\n"
        "    owner: ChangeRail core\n"
        "    reason: active smoke waiver\n"
        "    expires_at: 2999-01-01\n",
        encoding="utf-8",
    )
    future_report = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "report",
            "--scan-report",
            expired_scan_rel,
            "--baseline",
            future_baseline.relative_to(lifecycle_root).as_posix(),
            "--json",
        ]
    )
    try:
        future_payload = json.loads(future_report.stdout)
    except ValueError:
        future_payload = {}
    future_findings = future_payload.get("findings") if isinstance(future_payload.get("findings"), list) else []
    suppressed_until = future_findings[0].get("suppressed_until") if future_findings and isinstance(future_findings[0], dict) else None
    if (
        future_report.returncode != 0
        or not future_findings
        or future_findings[0].get("status") != "waived"
        or suppressed_until != "2999-01-01T00:00:00Z"
        or validate_lifecycle_report(future_payload)
    ):
        failures.append("active date-only waiver did not produce a valid normalized lifecycle report")

    valid_annotations = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "triage.json"
    valid_annotations.write_text(
        json.dumps(
            {
                "schema": "changerail.maintenance-triage.v1",
                "generated_at": "2026-08-09T00:00:00Z",
                "annotations": [{"fingerprint": fingerprint, "status": "open"}],
            },
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    triage_result = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "triage",
            "--annotations",
            valid_annotations.relative_to(lifecycle_root).as_posix(),
            "--json",
        ]
    )
    try:
        triage_payload = json.loads(triage_result.stdout)
    except ValueError:
        triage_payload = {}
    if triage_result.returncode != 0 or validate_maintenance_triage(triage_payload):
        failures.append("valid triage annotations did not normalize")

    invalid_annotations = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "triage-invalid.json"
    invalid_annotations.write_text(
        json.dumps({"schema": "changerail.maintenance-triage.v1", "generated_at": "2026-08-09T00:00:00Z", "annotations": [{}]}),
        encoding="utf-8",
    )
    invalid_triage = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "triage",
            "--annotations",
            invalid_annotations.relative_to(lifecycle_root).as_posix(),
            "--json",
        ]
    )
    if invalid_triage.returncode == 0 or "maintenance_triage_invalid" not in invalid_triage.stdout:
        failures.append("invalid triage annotations did not fail closed")

    board_before_unsafe_cards = snapshot_non_runtime_tree(lifecycle_root / "openspec" / "board")
    unsafe_card_report = json.loads(json.dumps(lifecycle_payload))
    unsafe_card_report["findings"][0]["path"] = "/home/example/private.md"
    unsafe_card_report["findings"][0]["subject"] = {"path": "/home/example/private.md"}
    unsafe_card_report_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "unsafe-card-report.json"
    unsafe_card_report_path.write_text(json.dumps(unsafe_card_report, ensure_ascii=True), encoding="utf-8")
    unsafe_cards = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            unsafe_card_report_path.relative_to(lifecycle_root).as_posix(),
            "--write",
            "--json",
        ]
    )
    if (
        unsafe_cards.returncode == 0
        or "unsafe_card_path" not in unsafe_cards.stdout
        or board_before_unsafe_cards != snapshot_non_runtime_tree(lifecycle_root / "openspec" / "board")
    ):
        failures.append("cards --write did not reject absolute report-sourced card path")

    sensitive_card_report = json.loads(json.dumps(lifecycle_payload))
    sensitive_card_report["findings"][0]["detector"] = sensitive_fixture
    sensitive_card_report_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "sensitive-card-report.json"
    sensitive_card_report_path.write_text(json.dumps(sensitive_card_report, ensure_ascii=True), encoding="utf-8")
    sensitive_cards = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            sensitive_card_report_path.relative_to(lifecycle_root).as_posix(),
            "--write",
            "--json",
        ]
    )
    if (
        sensitive_cards.returncode == 0
        or "secret_like_card_value" not in sensitive_cards.stdout
        or board_before_unsafe_cards != snapshot_non_runtime_tree(lifecycle_root / "openspec" / "board")
    ):
        failures.append("cards --write did not reject secret-like report-sourced card material")

    sensitive_path_card_report = json.loads(json.dumps(lifecycle_payload))
    sensitive_path_card_report["findings"][0]["path"] = sensitive_fixture
    sensitive_path_card_report["findings"][0]["subject"] = {"id": "opaque-subject"}
    if validate_lifecycle_report(sensitive_path_card_report):
        failures.append("sensitive path card fixture was not a schema-valid lifecycle report")
    sensitive_path_card_report_path = lifecycle_root / ".runtime" / "changerail" / "maintenance" / "sensitive-path-card-report.json"
    sensitive_path_card_report_path.write_text(json.dumps(sensitive_path_card_report, ensure_ascii=True), encoding="utf-8")
    sensitive_path_cards = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            sensitive_path_card_report_path.relative_to(lifecycle_root).as_posix(),
            "--write",
            "--json",
        ]
    )
    if (
        sensitive_path_cards.returncode == 0
        or "secret_like_card_value" not in sensitive_path_cards.stdout
        or board_before_unsafe_cards != snapshot_non_runtime_tree(lifecycle_root / "openspec" / "board")
    ):
        failures.append("cards --write did not reject secret-like report-sourced finding path")

    cards_preview = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            report_rel,
            "--json",
        ]
    )
    try:
        cards_preview_payload = json.loads(cards_preview.stdout)
    except ValueError:
        cards_preview_payload = {}
    preview_cards = cards_preview_payload.get("cards") if isinstance(cards_preview_payload.get("cards"), list) else []
    if cards_preview.returncode != 0 or not preview_cards or not preview_cards[0].get("path", "").startswith(".runtime/changerail/maintenance/"):
        failures.append("cards preview did not retain preview under runtime state")

    cards_write = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            report_rel,
            "--write",
            "--json",
        ]
    )
    try:
        cards_write_payload = json.loads(cards_write.stdout)
    except ValueError:
        cards_write_payload = {}
    written_cards = cards_write_payload.get("cards") if isinstance(cards_write_payload.get("cards"), list) else []
    written_rel = written_cards[0].get("path") if written_cards and isinstance(written_cards[0], dict) else ""
    written_card = lifecycle_root / written_rel
    if (
        cards_write.returncode != 0
        or not written_card.exists()
        or written_card.read_text(encoding="utf-8").splitlines().count(f"Maintenance Origin: {fingerprint}") != 1
    ):
        failures.append("cards --write did not create one board card with exact origin marker")
    moved_card = lifecycle_root / "openspec" / "board" / "3.inprogress" / written_card.name
    moved_card.parent.mkdir(parents=True, exist_ok=True)
    if written_card.exists():
        written_card.rename(moved_card)
    cards_write_again = run(
        [
            "bin/changerail-maintenance",
            "--workspace",
            rel(lifecycle_root),
            "cards",
            "--report",
            report_rel,
            "--write",
            "--json",
        ]
    )
    backlog_cards = list((lifecycle_root / "openspec" / "board" / "1.backlog").glob("*.md"))
    inprogress_cards = list((lifecycle_root / "openspec" / "board" / "3.inprogress").glob("*.md"))
    if cards_write_again.returncode != 0 or backlog_cards or len(inprogress_cards) != 1:
        failures.append("cards --write did not deduplicate existing marker across board lanes")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print("SMOKE_REPOSITORY_KNOWLEDGE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
