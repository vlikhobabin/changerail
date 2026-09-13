"""Deterministic review-history analysis across NO-GO verdicts."""

from __future__ import annotations

import importlib
import json
import os
import shutil
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


def _run(tmp_path: Path, monkeypatch, cycles: list[dict], name: str = "example-run") -> Path:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", tmp_path / ".runtime/changerail")
    run = tmp_path / ".runtime/changerail/runs" / name
    (run / "reviews").mkdir(parents=True, exist_ok=True)
    delivery.write_json(run / "run.json", {"run_id": name})
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


def _repeat_run(tmp_path, monkeypatch, name: str = "example-run"):
    first = _verdict("no-go", [_condition("C1", "fail")], [_finding(1, ["src/a.py"])])
    second = _verdict("no-go", [_condition("C1", "fail")], [_finding(1, ["src/a.py"])])
    return _run(tmp_path, monkeypatch, [first, second], name=name)


def _undetermined_run(tmp_path, monkeypatch, name: str = "example-run"):
    first = _verdict("no-go", [_condition("C1", "fail")], [])
    second = _verdict("no-go", [], [_finding(1, ["src/x.py"])])
    return _run(tmp_path, monkeypatch, [first, second], name=name)


def test_diagnosis_for_repeat_offers_repair_and_replan(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)

    value = diagnosis.diagnosis(delivery, run)

    assert value["schema"] == "changerail.exhausted-review-diagnosis.v1"
    assert value["primary_class"] == "repeat_defect"
    assert value["status"] == "operator_required"
    assert value["recommendation"] == "systemic-repair"
    assert [item["id"] for item in value["options"]] == [
        "systemic-repair",
        "revise-plan",
    ]
    assert "already failed earlier: C1" in value["rationale"]
    # A diagnosis must not spend or grant review allowance.
    assert all(item["reviews"] in (0, 1) for item in value["options"])


def test_infrastructure_class_never_routes_automatically(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    original = diagnosis.recurrence
    monkeypatch.setattr(
        diagnosis,
        "recurrence",
        lambda d, r: {**original(d, r), "observed_class": "infrastructure"},
    )
    value = diagnosis.diagnosis(delivery, run)
    assert value["status"] == "operator_required"


def test_diagnosis_is_reused_and_refreshed(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)

    first = diagnosis.write_diagnosis(delivery, run)
    second = diagnosis.write_diagnosis(delivery, run)
    assert first["diagnosis_sha256"] == second["diagnosis_sha256"]

    changed = _verdict("go", [_condition("C1", "pass")], [])
    delivery.write_json(run / "reviews" / "cycle-02.json", changed)
    with pytest.raises(delivery.DeliveryError, match="stale"):
        diagnosis.load_diagnosis(delivery, run)
    third = diagnosis.write_diagnosis(delivery, run)
    assert third["diagnosis_sha256"] != first["diagnosis_sha256"]


def test_choice_preview_then_authorize_appends_one_record(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    preview = diagnosis.choose(
        delivery, run, option_id="systemic-repair", reason="same approach failed twice"
    )
    assert preview["state"] == "preview"
    digest = preview["proposal"]["choice_sha256"]
    assert preview["proposal"]["transition"] == "repair"

    with pytest.raises(delivery.DeliveryError, match="stale choice digest"):
        diagnosis.choose(
            delivery,
            run,
            option_id="systemic-repair",
            reason="same approach failed twice",
            authorize="0" * 64,
        )

    chosen = diagnosis.choose(
        delivery,
        run,
        option_id="systemic-repair",
        reason="same approach failed twice",
        authorize=digest,
    )
    assert chosen["state"] == "chosen"
    records = sorted((run.parent.parent / "rethink" / run.name / "choices").glob("*.json"))
    assert len(records) == 1
    assert json.loads(records[0].read_text())["option"] == "systemic-repair"


def test_choice_rejects_an_option_outside_the_diagnosis(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    with pytest.raises(delivery.DeliveryError, match="not available"):
        diagnosis.choose(
            delivery, run, option_id="amend-criterion", reason="not offered here"
        )


def test_choice_and_amendment_require_an_operator_context(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))

    with pytest.raises(delivery.DeliveryError, match="outside worker context"):
        diagnosis.choose(delivery, run, option_id="systemic-repair", reason="worker")
    with pytest.raises(delivery.DeliveryError, match="outside worker context"):
        diagnosis.amend_criterion(
            delivery,
            run,
            condition="C1",
            before="before",
            after="after",
            reason="worker",
        )


def test_criterion_amendment_preserves_the_previous_wording(tmp_path, monkeypatch):
    run = _undetermined_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    preview = diagnosis.amend_criterion(
        delivery,
        run,
        condition="C1",
        before="the old, unachievable wording",
        after="the restated wording",
        reason="the criterion cannot be evidenced as written",
    )
    assert preview["state"] == "preview"
    amended = diagnosis.amend_criterion(
        delivery,
        run,
        condition="C1",
        before="the old, unachievable wording",
        after="the restated wording",
        reason="the criterion cannot be evidenced as written",
        authorize=preview["proposal"]["amendment_sha256"],
    )
    assert amended["state"] == "amended"
    record = json.loads((tmp_path / amended["path"]).read_text())
    assert record["before"] == "the old, unachievable wording"
    assert record["after"] == "the restated wording"
    assert record["condition"] == "C1"


def test_criterion_amendment_is_refused_for_a_repeated_defect(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    with pytest.raises(delivery.DeliveryError, match="criterion amendment requires"):
        diagnosis.amend_criterion(
            delivery,
            run,
            condition="C1",
            before="a",
            after="b",
            reason="not a criterion problem",
        )


PROFILE_ROUTE = {
    "models": {
        "implementation": {"model": "m", "reasoning_effort": "high"},
        "diagnosis": {"model": "d", "reasoning_effort": "high"},
    }
}


def _model_claim(primary: str, rationale: str = "model view") -> dict:
    return {
        "schema": diagnosis.MODEL_SCHEMA,
        "primary_class": primary,
        "rationale": rationale,
        "model": {"model": "d", "reasoning_effort": "high"},
    }


def test_model_claim_refines_a_consistent_class(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    assert diagnosis.diagnosis(delivery, run)["primary_class"] == "repeat_defect"

    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("plan_conflict"))

    refined = diagnosis.diagnosis(delivery, run)
    assert refined["primary_class"] == "plan_conflict"
    assert refined["rationale"] == "model view"
    assert refined["options"][0]["id"] == "revise-plan"
    # The model cannot make a stop automatic on its own.
    assert refined["status"] == "operator_required"


def test_model_claim_denying_an_observed_repeat_is_ignored(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    delivery.write_json(
        run / diagnosis.MODEL_ARTIFACT, _model_claim("incomplete_work")
    )

    value = diagnosis.diagnosis(delivery, run)

    assert value["primary_class"] == "repeat_defect"
    assert "model" not in value


def test_model_claim_denying_a_new_failure_is_ignored(tmp_path, monkeypatch):
    first = _verdict("no-go", [_condition("C1", "fail")], [])
    second = _verdict("no-go", [_condition("C2", "fail")], [])
    run = _run(tmp_path, monkeypatch, [first, second])
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("repeat_defect"))

    assert diagnosis.diagnosis(delivery, run)["primary_class"] == "incomplete_work"


def test_unknown_model_class_is_ignored(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("made-up"))

    assert diagnosis.diagnosis(delivery, run)["primary_class"] == "repeat_defect"


def test_route_is_optional_and_validated(tmp_path, monkeypatch):
    assert diagnosis.route(delivery, {"models": {}}) is None
    configured = diagnosis.route(
        delivery, {"models": {"diagnosis": {"model": "d", "reasoning_effort": "high"}}}
    )
    assert configured == ("d", "high")
    with pytest.raises(delivery.DeliveryError, match="invalid reasoning effort"):
        diagnosis.route(
            delivery, {"models": {"diagnosis": {"model": "d", "reasoning_effort": ""}}}
        )


def test_announce_launches_the_model_only_for_an_undetermined_class(
    tmp_path, monkeypatch
):
    run = _repeat_run(tmp_path, monkeypatch)
    calls = []
    detail = diagnosis.announce(
        delivery,
        run,
        PROFILE_ROUTE,
        reason="exhausted",
        launch=lambda *, context: calls.append(context),
    )
    assert calls == []
    assert "diagnosis repeat_defect" in detail
    assert "systemic-repair" in detail

    undetermined = _undetermined_run(tmp_path, monkeypatch)
    launched = []
    diagnosis.announce(
        delivery,
        undetermined,
        PROFILE_ROUTE,
        reason="exhausted",
        launch=lambda *, context: launched.append(context),
    )
    assert len(launched) == 1
    assert launched[0].name == diagnosis.CONTEXT_NAME


def test_announce_without_a_route_never_launches(tmp_path, monkeypatch):
    run = _undetermined_run(tmp_path, monkeypatch)
    calls = []
    diagnosis.announce(
        delivery, run, {"models": {}}, reason="exhausted",
        launch=lambda *, context: calls.append(context),
    )
    assert calls == []


def test_recorded_choice_is_latest_and_refuses_a_stale_record(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)
    assert diagnosis.recorded_choice(delivery, run) is None

    diagnosis.choose(
        delivery, run, option_id="revise-plan", reason="replan instead"
    )
    preview = diagnosis.choose(
        delivery, run, option_id="revise-plan", reason="replan instead"
    )
    diagnosis.choose(
        delivery,
        run,
        option_id="revise-plan",
        reason="replan instead",
        authorize=preview["proposal"]["choice_sha256"],
    )
    record = diagnosis.recorded_choice(delivery, run)
    assert record["option"] == "revise-plan"
    assert record["transition"] == "close-and-replan"

    changed = _verdict("go", [_condition("C1", "pass")], [])
    delivery.write_json(run / "reviews" / "cycle-02.json", changed)
    with pytest.raises(delivery.DeliveryError, match="stale"):
        diagnosis.recorded_choice(delivery, run)


def test_announce_reports_the_recorded_choice_and_its_followup(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)
    preview = diagnosis.choose(
        delivery, run, option_id="revise-plan", reason="replan instead"
    )
    diagnosis.choose(
        delivery,
        run,
        option_id="revise-plan",
        reason="replan instead",
        authorize=preview["proposal"]["choice_sha256"],
    )

    detail = diagnosis.announce(delivery, run, PROFILE_ROUTE, reason="exhausted")

    assert "operator chose revise-plan (close-and-replan)" in detail
    assert "separate new plan" in detail


def test_announce_without_a_choice_still_offers_the_menu(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)

    detail = diagnosis.announce(delivery, run, {"models": {}}, reason="exhausted")

    assert "diagnosis repeat_defect" in detail
    assert "available: systemic-repair, revise-plan" in detail


def test_decision_state_carries_class_and_options(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    state = diagnosis.decision_state(delivery, run)

    assert state["schema"] == "changerail.awaiting-operator-decision.v1"
    assert state["primary_class"] == "repeat_defect"
    assert state["options"] == ["systemic-repair", "revise-plan"]
    assert state["recommendation"] == "systemic-repair"
    assert state["diagnosis"].endswith("diagnosis.json")


def test_awaiting_decision_is_a_delivery_error_carrying_state():
    error = delivery.AwaitingDecision("stop", state={"primary_class": "repeat_defect"})
    # Existing failure handlers must still catch it as a delivery error.
    assert isinstance(error, delivery.DeliveryError)
    assert error.state["primary_class"] == "repeat_defect"


def test_no_class_routes_automatically(tmp_path, monkeypatch):
    """The environment route cannot operate on a reviewed lineage, so nothing is
    prepared without an operator - and a model claim never makes a route auto."""
    run = _repeat_run(tmp_path, monkeypatch)
    original = diagnosis.recurrence
    monkeypatch.setattr(
        diagnosis,
        "recurrence",
        lambda d, r: {**original(d, r), "observed_class": "infrastructure"},
    )
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("infrastructure"))

    value = diagnosis.diagnosis(delivery, run)

    assert value["primary_class"] == "infrastructure"
    assert value["status"] == "operator_required"
    # The only environment route that exists refuses a run that already went
    # through review, so the operator keeps the routes that can actually run,
    # and the class still names a recommendation.
    assert [item["id"] for item in value["options"]] == [
        "systemic-repair",
        "revise-plan",
        "amend-criterion",
        "close-attempt",
    ]
    assert value["recommendation"] == "close-attempt"


def test_environment_claim_is_not_rejected_by_a_repeat(tmp_path, monkeypatch):
    """An environment stop can look like a repeat; the class carries that signal."""
    run = _repeat_run(tmp_path, monkeypatch)
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("infrastructure"))

    value = diagnosis.diagnosis(delivery, run)

    assert value["primary_class"] == "infrastructure"
    assert value["status"] == "operator_required"


def test_options_carry_effect_price_and_preconditions(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)

    value = diagnosis.diagnosis(delivery, run)

    for item in value["options"]:
        assert item["preconditions"].strip()
        assert item["effect"].strip()
    # C4 requires the price to be readable, not implicit in the option name.
    assert {item["id"]: (item["reviews"], item["scope"], item["architecture"]) for item in value["options"]} == {
        "systemic-repair": (1, "in-scope", False),
        "revise-plan": (0, "new-plan", True),
    }
    assert value["recommendation"] == "systemic-repair"


def test_recurrence_spans_the_recovery_lineage(tmp_path, monkeypatch):
    """A successor's diagnosis must see the reviews that rejected the lineage."""
    first = _verdict("no-go", [_condition("C1", "fail")], [_finding(1, ["src/a.py"])])
    predecessor = _run(tmp_path, monkeypatch, [first], name="run-1")
    second = _verdict("no-go", [_condition("C1", "fail")], [_finding(2, ["src/a.py"])])
    successor = _run(tmp_path, monkeypatch, [second], name="run-2")

    monkeypatch.setattr(
        delivery, "recovery_ancestors", lambda run: [predecessor] if run == successor else []
    )
    report = diagnosis.recurrence(delivery, successor)

    assert report["recurring_conditions"] == ["C1"]
    assert [item["cycle"] for item in report["conditions"]["C1"]] == [1, 2]
    assert [item["id"] for item in report["recurring_findings"]] == ["R2"]


def test_inherited_verdict_copies_are_not_counted_twice(tmp_path, monkeypatch):
    first = _verdict("no-go", [_condition("C1", "fail")], [])
    predecessor = _run(tmp_path, monkeypatch, [first], name="run-3")
    successor = _run(tmp_path, monkeypatch, [], name="run-4")
    shutil.copy2(predecessor / "reviews" / "cycle-01.json", successor / "reviews" / "cycle-01.json")
    monkeypatch.setattr(
        delivery, "recovery_ancestors", lambda run: [predecessor] if run == successor else []
    )

    report = diagnosis.recurrence(delivery, successor)

    assert report["cycle_count"] == 1


def test_unsupported_class_on_an_unverified_base_is_rejected(tmp_path, monkeypatch):
    """Nothing comparable in the history cannot support a claim about the plan."""
    run = _undetermined_run(tmp_path, monkeypatch)
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("unsatisfiable"))

    value = diagnosis.diagnosis(delivery, run)

    assert value["primary_class"] is None
    assert "model" not in value


def test_observation_classes_survive_an_unverified_base(tmp_path, monkeypatch):
    run = _undetermined_run(tmp_path, monkeypatch)
    delivery.write_json(run / diagnosis.MODEL_ARTIFACT, _model_claim("unreproducible"))

    value = diagnosis.diagnosis(delivery, run)

    assert value["primary_class"] == "unreproducible"
    # A model claim never makes a route automatic.
    assert value["status"] == "operator_required"


def test_operator_can_reconsider_a_recorded_decision(tmp_path, monkeypatch):
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    first = diagnosis.choose(delivery, run, option_id="systemic-repair", reason="repair it")
    chosen = diagnosis.choose(
        delivery, run, option_id="systemic-repair", reason="repair it",
        authorize=first["proposal"]["choice_sha256"],
    )
    assert chosen["state"] == "chosen" and "reused" not in chosen

    # The same decision recorded again is the same decision, not a second record.
    again = diagnosis.choose(delivery, run, option_id="systemic-repair", reason="repair it")
    assert again["state"] == "chosen" and again["reused"] is True
    assert again["choice"]["option"] == "systemic-repair"
    records = list((diagnosis._rethink_root(delivery, run) / "choices").glob("*.json"))
    assert len(records) == 1

    # The same reason cannot silently carry a different transition...
    with pytest.raises(delivery.DeliveryError, match="needs its own reason"):
        diagnosis.choose(delivery, run, option_id="revise-plan", reason="repair it")
    assert list((diagnosis._rethink_root(delivery, run) / "choices").glob("*.json")) == records

    # ...but a genuinely reconsidered decision has its own reason and becomes
    # the latest record, so a refused route can never trap the operator.
    other = diagnosis.choose(delivery, run, option_id="revise-plan", reason="replan instead")
    replanned = diagnosis.choose(
        delivery, run, option_id="revise-plan", reason="replan instead",
        authorize=other["proposal"]["choice_sha256"],
    )
    assert replanned["state"] == "chosen"
    assert diagnosis.recorded_choice(delivery, run)["option"] == "revise-plan"
    assert len(list((diagnosis._rethink_root(delivery, run) / "choices").glob("*.json"))) == 2


def test_amendment_records_its_author(tmp_path, monkeypatch):
    run = _undetermined_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)

    preview = diagnosis.amend_criterion(
        delivery, run, condition="C1", before="old wording", after="new wording",
        reason="the old wording is not expressible",
    )
    result = diagnosis.amend_criterion(
        delivery, run, condition="C1", before="old wording", after="new wording",
        reason="the old wording is not expressible",
        authorize=preview["proposal"]["amendment_sha256"],
    )

    amendment = result["amendment"]
    assert amendment["author"]["uid"] == os.getuid()
    assert amendment["observed_at"]
    assert amendment["before"] == "old wording"
    assert amendment["after"] == "new wording"


def test_preview_digest_survives_a_second_boundary(tmp_path, monkeypatch):
    """The documented flow authorizes a digest copied at an earlier second."""
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)
    real = delivery.utc_now
    ticks = iter(["2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z"] * 4)
    monkeypatch.setattr(delivery, "utc_now", lambda: next(ticks))

    preview = diagnosis.choose(delivery, run, option_id="systemic-repair", reason="repair it")
    # A human copies the digest and authorizes it one second later.
    chosen = diagnosis.choose(
        delivery, run, option_id="systemic-repair", reason="repair it",
        authorize=preview["proposal"]["choice_sha256"],
    )

    assert chosen["state"] == "chosen"
    assert chosen["choice"]["observed_at"] != preview["proposal"]["observed_at"]
    assert chosen["choice"]["choice_sha256"] == preview["proposal"]["choice_sha256"]
    monkeypatch.setattr(delivery, "utc_now", real)

    # The same rule holds for an amendment preview: authorizing it one second
    # later must still match the digest the operator copied.
    other = _undetermined_run(tmp_path, monkeypatch, name="run-amend")
    diagnosis.write_diagnosis(delivery, other)
    ticks = iter(["2026-01-01T00:00:10Z", "2026-01-01T00:00:11Z"] * 2)
    monkeypatch.setattr(delivery, "utc_now", lambda: next(ticks))
    amendment_preview = diagnosis.amend_criterion(
        delivery, other, condition="C1", before="old wording",
        after="new wording", reason="not expressible",
    )
    amended = diagnosis.amend_criterion(
        delivery, other, condition="C1", before="old wording",
        after="new wording", reason="not expressible",
        authorize=amendment_preview["proposal"]["amendment_sha256"],
    )
    assert amended["state"] == "amended"
    assert amended["amendment"]["amendment_sha256"] == (
        amendment_preview["proposal"]["amendment_sha256"]
    )
    assert amended["amendment"]["observed_at"] != (
        amendment_preview["proposal"]["observed_at"]
    )


def test_recorded_choice_must_match_a_supported_transition(tmp_path, monkeypatch):
    """A hand-edited transition cannot smuggle a separate route into a repair."""
    run = _repeat_run(tmp_path, monkeypatch)
    diagnosis.write_diagnosis(delivery, run)
    preview = diagnosis.choose(delivery, run, option_id="revise-plan", reason="replan")
    diagnosis.choose(
        delivery, run, option_id="revise-plan", reason="replan",
        authorize=preview["proposal"]["choice_sha256"],
    )
    path = next((diagnosis._rethink_root(delivery, run) / "choices").glob("*.json"))
    record = delivery.load_json(path)
    record["transition"] = "repair"
    delivery.write_json(path, record)

    with pytest.raises(delivery.DeliveryError, match="supported transition"):
        diagnosis.recorded_choice(delivery, run)


def test_separate_route_decision_survives_down_the_lineage(tmp_path, monkeypatch):
    """A route nothing executes automatically keeps blocking its descendants.

    A repair or review decision is spent by the successor it authorized, so a
    deeper one is history. A separate-route decision is not spent by anything, so
    it must keep governing a later continuation instead of being dropped.
    """
    base = _repeat_run(tmp_path, monkeypatch, name="lineage-a")
    middle = _run(tmp_path, monkeypatch, [], name="lineage-b")
    leaf = _run(tmp_path, monkeypatch, [], name="lineage-c")
    monkeypatch.setattr(
        delivery,
        "recovery_ancestors",
        lambda run: {middle: [base], leaf: [middle, base]}.get(run, []),
    )
    diagnosis.write_diagnosis(delivery, base)
    preview = diagnosis.choose(delivery, base, option_id="revise-plan", reason="replan")
    diagnosis.choose(
        delivery, base, option_id="revise-plan", reason="replan",
        authorize=preview["proposal"]["choice_sha256"],
    )

    found = delivery._lineage_decision(leaf)

    assert found is not None
    assert found[1] == base
    assert found[0]["option"] == "revise-plan"


def test_spent_repair_decision_does_not_govern_a_deeper_run(tmp_path, monkeypatch):
    base = _repeat_run(tmp_path, monkeypatch, name="lineage-d")
    middle = _run(tmp_path, monkeypatch, [], name="lineage-e")
    leaf = _run(tmp_path, monkeypatch, [], name="lineage-f")
    monkeypatch.setattr(
        delivery,
        "recovery_ancestors",
        lambda run: {middle: [base], leaf: [middle, base]}.get(run, []),
    )
    diagnosis.write_diagnosis(delivery, base)
    preview = diagnosis.choose(delivery, base, option_id="systemic-repair", reason="repair")
    diagnosis.choose(
        delivery, base, option_id="systemic-repair", reason="repair",
        authorize=preview["proposal"]["choice_sha256"],
    )

    # The immediate successor honours it; a deeper run treats it as spent.
    assert delivery._lineage_decision(middle) is not None
    assert delivery._lineage_decision(leaf) is None
