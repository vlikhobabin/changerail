"""Deterministic review-history analysis across NO-GO verdicts."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(REPO_ROOT))
delivery = importlib.import_module("scripts.changerail.local_delivery")
diagnosis = importlib.import_module("scripts.changerail.exhaustion_diagnosis")
sys.path.pop(0)

CARD = "openspec/" + "board" + "/3.inprogress/example.md"
FINGERPRINT = "0" * 64


def _condition(short: str, disposition: str) -> dict:
    qualified = f"{CARD}@sha256:{FINGERPRINT}:{short}"
    return {
        "scenario": f"{CARD}@sha256:{FINGERPRINT} / Condition: {short}",
        "conditions": [qualified],
        "disposition": disposition,
        "observation_ids": [f"observed-{short.lower()}"],
        "condition_refs": [
            {
                "condition": qualified,
                "stage": "implementation",
                "disposition": disposition,
                "observation_ids": [f"observed-{short.lower()}"],
            }
        ],
        "assessment": f"{short} is {disposition}",
    }


def _finding(number: int, paths: list[str]) -> dict:
    return {
        "id": f"R{number}",
        "severity": "blocker",
        "summary": f"finding {number}",
        "preconditions": "a precondition",
        "expected": "expected behaviour",
        "observed": "observed behaviour",
        "repair_scope": "repair the affected path",
        "paths": paths,
    }


def _run(tmp_path: Path, monkeypatch, cycles: list[dict]) -> Path:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", tmp_path / ".runtime/changerail")
    run = tmp_path / ".runtime/changerail/runs/example-run"
    (run / "reviews").mkdir(parents=True)
    delivery.write_json(run / "run.json", {"run_id": "example-run"})
    for index, cycle in enumerate(cycles, start=1):
        delivery.write_json(run / "reviews" / f"cycle-{index:02d}.json", cycle)
    return run


def _verdict(result: str, decisions: list[dict], findings: list[dict]) -> dict:
    return {
        "schema": "changerail.review-verdict.v2",
        "card": CARD,
        "workspace": {"fingerprint": FINGERPRINT},
        "inventory_digest": FINGERPRINT,
        "reviewer": {
            "model": "fixture",
            "reasoning_effort": "high",
            "fresh_context": True,
            "did_not_implement": True,
        },
        "result": result,
        "decisions": decisions,
        "findings": findings,
        "reviewed_at": "2026-09-12T00:00:00Z",
    }


def test_real_two_no_go_case_marks_repeats_and_closures(tmp_path, monkeypatch):
    """Shape of run 20260912T091333Z-restore-accepted-task-wording."""
    first = _verdict(
        "no-go",
        [_condition("C1", "fail"), _condition("C2", "fail"), _condition("C3", "fail")],
        [_finding(1, ["tests/c1.py"]), _finding(2, ["tests/c2.py"])],
    )
    second = _verdict(
        "no-go",
        [_condition("C1", "fail"), _condition("C2", "fail"), _condition("C3", "pass")],
        [_finding(1, ["tests/c1.py"]), _finding(2, ["tests/c2.py"])],
    )
    run = _run(tmp_path, monkeypatch, [first, second])
    before = {
        path.name: path.read_bytes() for path in sorted((run / "reviews").glob("*.json"))
    }

    report = diagnosis.recurrence(delivery, run)

    assert report["schema"] == "changerail.review-recurrence.v1"
    assert report["cycle_count"] == 2
    assert report["recurring_conditions"] == ["C1", "C2"]
    assert report["closed_conditions"] == ["C3"]
    assert report["new_failures"] == []
    assert report["observed_class"] == "repeat_defect"
    assert [row["id"] for row in report["recurring_findings"]] == ["R1", "R2"]
    assert report["recurring_findings"][0]["shared_paths"] == ["tests/c1.py"]
    assert report["recurring_findings"][0]["earlier_ids"] == ["R1"]
    # Reporting must not touch the retained verdicts.
    assert {
        path.name: path.read_bytes() for path in sorted((run / "reviews").glob("*.json"))
    } == before


def test_new_condition_is_incomplete_work_not_a_repeat(tmp_path, monkeypatch):
    first = _verdict("no-go", [_condition("C1", "fail"), _condition("C2", "pass")], [])
    second = _verdict("no-go", [_condition("C1", "pass"), _condition("C2", "fail")], [])
    run = _run(tmp_path, monkeypatch, [first, second])

    report = diagnosis.recurrence(delivery, run)

    assert report["recurring_conditions"] == []
    assert report["closed_conditions"] == ["C1"]
    assert report["new_failures"] == ["C2"]
    assert report["observed_class"] == "incomplete_work"


def test_same_condition_twice_is_a_repeat_even_without_finding_overlap(
    tmp_path, monkeypatch
):
    first = _verdict("no-go", [_condition("C1", "fail")], [])
    second = _verdict("no-go", [_condition("C1", "fail")], [])
    run = _run(tmp_path, monkeypatch, [first, second])

    report = diagnosis.recurrence(delivery, run)

    assert report["recurring_conditions"] == ["C1"]
    assert report["observed_class"] == "repeat_defect"


def test_go_history_yields_no_observed_class(tmp_path, monkeypatch):
    first = _verdict("no-go", [_condition("C1", "fail")], [])
    second = _verdict("go", [_condition("C1", "pass")], [])
    run = _run(tmp_path, monkeypatch, [first, second])

    report = diagnosis.recurrence(delivery, run)

    assert report["latest_result"] == "go"
    assert report["observed_class"] is None
    assert report["closed_conditions"] == ["C1"]


def test_report_is_deterministic_and_content_bound(tmp_path, monkeypatch):
    cycles = [
        _verdict("no-go", [_condition("C1", "fail")], []),
        _verdict("no-go", [_condition("C1", "fail")], []),
    ]
    run = _run(tmp_path, monkeypatch, cycles)

    first = diagnosis.recurrence(delivery, run)
    second = diagnosis.recurrence(delivery, run)
    assert first["recurrence_sha256"] == second["recurrence_sha256"]

    changed = _verdict(
        "no-go", [_condition("C1", "fail"), _condition("C4", "fail")], []
    )
    delivery.write_json(run / "reviews" / "cycle-02.json", changed)
    third = diagnosis.recurrence(delivery, run)
    assert third["recurrence_sha256"] != first["recurrence_sha256"]


def test_without_verdicts_the_report_refuses(tmp_path, monkeypatch):
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", tmp_path / ".runtime/changerail")
    run = tmp_path / ".runtime/changerail/runs/empty-run"
    (run / "reviews").mkdir(parents=True)

    with pytest.raises(delivery.DeliveryError, match="at least one completed verdict"):
        diagnosis.recurrence(delivery, run)


def test_condition_name_reduces_qualified_reference():
    assert diagnosis.condition_name(f"{CARD}@sha256:{FINGERPRINT}:C1") == "C1"
    assert diagnosis.condition_name("C12") == "C12"
    assert diagnosis.condition_name("") is None
    assert diagnosis.condition_name(None) is None


def test_repair_context_carries_the_recurrence(tmp_path, monkeypatch):
    """The repair turn must see the history, not only the latest findings."""
    first = _verdict("no-go", [_condition("C1", "fail")], [_finding(1, ["src/a.py"])])
    second = _verdict("no-go", [_condition("C1", "fail")], [_finding(1, ["src/a.py"])])
    run = _run(tmp_path, monkeypatch, [first, second])
    card = tmp_path / CARD
    card.parent.mkdir(parents=True)
    card.write_text("# Example\n", encoding="utf-8")
    monkeypatch.setattr(delivery, "payload_fingerprint", lambda: FINGERPRINT)

    context = delivery.build_repair_context(card=card, run_dir=run, reason="semantic")

    payload = json.loads(context.read_text(encoding="utf-8"))
    assert payload["recurrence"]["observed_class"] == "repeat_defect"
    assert "Change the approach" in payload["instruction"]
