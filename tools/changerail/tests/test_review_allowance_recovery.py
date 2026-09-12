"""Applied technical recovery remains eligible for a later operator review.

The accepted native plan, frozen identity, technical prepare/apply receipts,
successor publication, dispatch reservation, locks and allowance are real.
Only the model group and outer orchestration callbacks are replaced: they
append deterministic completed review receipts, without external workers.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import review_allowance as policy
from scripts.changerail import technical_recovery as recovery
from tools.changerail.tests.test_review_allowance import exhausted as exhausted
from tools.changerail.tests.test_review_allowance import _history
from tools.changerail.tests.test_native_openspec_integration import project as project


@pytest.fixture
def applied_recovery(exhausted, monkeypatch):
    root, card, origin = exhausted
    # Reuse real admission, but construct the pre-review capacity failure before
    # prepare freezes any predecessor bytes. Never edit it after publication.
    shutil.rmtree(origin / "reviews")
    shutil.rmtree(origin / "sessions")
    metadata = d._check_json(origin / "run.json")
    metadata.update(completed=False, terminal_reason="selected model is at capacity")
    d.write_json(origin / "run.json", metadata)
    (origin / "phase-events.jsonl").write_text("".join(
        json.dumps({"phase": "change-1", "stage": stage,
                    "at": "2026-09-12T00:01:00Z"}) + "\n"
        for stage in ("starting", "complete")
    ))
    session = origin / "sessions/failed-group-2"
    d.write_json(session / "session.json", {
        "role": "implementation", "session": "capacity-session",
        "native_change_number": 2, "finished_at": "2026-09-12T00:02:00Z",
        "exit_code": 1, "completed": False, "timed_out": False,
        "interrupted": False, "budget_violation": None,
        "stop_reason": "nonzero_exit", "streams_complete": True,
        "process_group_quiescent": True, "model": "failed-model",
    })
    event = {"type": "thread.started", "thread_id": "capacity-session"}
    (session / "stderr.log").write_text("Selected model is at capacity\n")
    (session / "stdout.jsonl").write_text(json.dumps(event) + "\n")
    (session / "events.jsonl").write_text(json.dumps({
        "observed_at": "2026-09-12T00:02:00Z", "observed_elapsed_seconds": 0.0,
        "event": event,
    }) + "\n")
    profile = d.profile()
    monkeypatch.setattr(d, "profile", lambda: {
        **profile, "models": {**profile["models"], "technical_recovery": {
            "model": "fallback-model", "reasoning_effort": "high",
        }},
    })
    launches = []

    def launch(_delivery, **kwargs):
        child = kwargs["run_dir"]
        assert kwargs["only_group"] == 2
        assert kwargs["model_route_name"] == "technical-recovery"
        launches.append(child.name)
        assert d._check_json(child / "technical-recovery-dispatch.json")["successor"] == child.name
        (child / "phase-events.jsonl").write_text("".join(
            json.dumps({"phase": "change-2", "stage": stage,
                        "at": "2026-09-12T00:03:00Z"}) + "\n"
            for stage in ("starting", "complete")
        ))

    def execute(**kwargs):
        child = kwargs["run_dir"]
        kwargs["before_orchestrate"]()
        assert d.review_budget_usage(child) == {"semantic_cycles": 0}
        # Legitimate implementation changes after technical dispatch must not
        # invalidate its retained predecessor starting fingerprint.
        (root / "source.py").write_text("result = 'recovered implementation'\n")
        manifest = d._check_json(child / "manifest.json")
        paths = d.changed_paths()
        manifest.update(paths=paths, fingerprint=d.payload_fingerprint(paths),
                        path_fingerprints=d.path_fingerprints(paths))
        d.write_json(child / "manifest.json", manifest)
        d.write_json(d.manifest_path(card.stem), manifest)
        for cycle in (1, 2):
            stem = child / "reviews" / f"cycle-{cycle:02d}"
            d.write_json(stem.with_suffix(".json"), {
                "result": "no-go", "workspace": manifest["fingerprint"],
                "findings": [{"repair_scope": ["source.py"], "observed": "remaining failure"}],
            })
            d.write_json(stem.with_name(stem.name + "-manifest.json"), manifest)
            d.write_json(stem.with_name(stem.name + "-context.json"), {"cycle": cycle})
            d.write_json(child / "sessions" / f"review-{cycle:02d}" / "session.json", {
                "role": "review", "finished_at": "2026-09-12T00:04:00Z",
                "completed": True, "exit_code": 0,
            })
        result = d._check_json(child / "run.json")
        result.update(finished_at="2026-09-12T00:05:00Z", exit_code=2,
                      terminal_reason="autonomous review budget exhausted")
        d.write_json(child / "run.json", result)
        return 2

    monkeypatch.setattr(flow, "launch_groups", launch)
    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    before = _history(origin)
    prepared = recovery.prepare(d, origin)
    applied = recovery.apply(d, origin, Path(prepared["proposal"]))
    child = Path(applied["successor"])
    assert applied["state"] == "dispatched" and applied["exit_code"] == 2
    assert _history(origin) == before
    assert d.review_budget_usage(origin) == {"semantic_cycles": 0}
    assert d.review_budget_usage(child) == {"semantic_cycles": 2}
    assert launches == [child.name]
    return origin, child, launches


def test_applied_supported_recovery_allows_exhausted_descendant_one_review(applied_recovery):
    origin, child, launches = applied_recovery
    authority = d.RUNTIME_ROOT / "technical-recoveries" / origin.name
    histories = {path: _history(path) for path in (origin, child, authority)}
    preview = policy.review_allow(d, child, reason="Repair after completed technical recovery")
    result = policy.review_allow(d, child, reason="Repair after completed technical recovery",
                                authorize=preview["proposal_sha256"])
    assert result["state"] == "authorized"
    assert result["proposal"]["review_number"] == 3
    assert result["proposal"]["spent_before"] == 2
    assert result["proposal"]["lineage"] == [child.name, origin.name]
    assert result["proposal"]["root_run"] == origin.name
    assert policy.allowance(d, child)["remaining"] == 1
    assert d.review_budget_usage(child) == {"semantic_cycles": 2}
    assert all(_history(path) == before for path, before in histories.items())
    assert launches == [child.name]
    assert set((d.RUNTIME_ROOT / "runs").iterdir()) == {origin, child}


@pytest.mark.parametrize("damage", ["unapplied", "undispatched", "foreign-intent", "foreign-dispatch"])
def test_unresolved_or_foreign_technical_recovery_cannot_authorize(applied_recovery, damage):
    origin, child, launches = applied_recovery
    authority = d.RUNTIME_ROOT / "technical-recoveries" / origin.name
    if damage == "unapplied":
        (authority / "applied.json").unlink()
    elif damage == "undispatched":
        (child / "technical-recovery-dispatch.json").unlink()
    else:
        path = (authority / "successor-intent.json" if damage == "foreign-intent"
                else child / "technical-recovery-dispatch.json")
        value = d._check_json(path)
        value["successor"] = "foreign-run"
        d.write_json(path, value)
    histories = {path: _history(path) for path in (origin, child, authority)}
    with pytest.raises(d.DeliveryError, match="technical recovery|recovery intent"):
        policy.review_allow(d, child, reason="Must retain unresolved transition refusal")
    assert not list((d.RUNTIME_ROOT / "review-authorizations").glob("*/*.json"))
    assert all(_history(path) == before for path, before in histories.items())
    assert launches == [child.name]
    assert set((d.RUNTIME_ROOT / "runs").iterdir()) == {origin, child}


def test_authorized_allowance_rechecks_retained_technical_receipt(applied_recovery):
    """Even a non-identity receipt change invalidates its authorized history."""
    origin, child, launches = applied_recovery
    reason = "Bind the completed technical transition to this decision"
    preview = policy.review_allow(d, child, reason=reason)
    result = policy.review_allow(d, child, reason=reason,
                                authorize=preview["proposal_sha256"])
    assert policy.allowance(d, child)["remaining"] == 1
    records = _history(d.RUNTIME_ROOT / "review-authorizations")
    receipt = d.RUNTIME_ROOT / "technical-recoveries" / origin.name / "applied.json"
    value = d._check_json(receipt)
    value["applied_at"] = "2026-09-12T00:06:00Z"
    d.write_json(receipt, value)
    histories = {path: _history(path) for path in (origin, child)}
    with pytest.raises(d.DeliveryError, match="stale|history|authorization"):
        policy.allowance(d, child)
    with pytest.raises(d.DeliveryError, match="stale|history|authorization"):
        policy.review_allow(d, child, reason=reason, authorize=result["proposal_sha256"])
    assert _history(d.RUNTIME_ROOT / "review-authorizations") == records
    assert all(_history(path) == before for path, before in histories.items())
    assert launches == [child.name]
