"""Public restore/resume integration retains failed ancestry and completed work."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import openspec_board as board
from scripts.changerail import openspec_context as native
from tools.changerail.tests.test_plan_restoration import stopped as stopped
from tools.changerail.tests.test_native_openspec_integration import project as project


def snapshot(path):
    return {
        p.relative_to(path).as_posix(): p.read_bytes()
        for p in path.rglob("*")
        if p.is_file()
    }


def test_public_restore_then_resume_retains_failed_child(stopped, monkeypatch, capsys):
    root, card, origin, _ = stopped
    plan = d._check_json(origin / "native-plan.json")
    metadata = d._check_json(origin / "run.json")
    metadata["change_plan"] = [
        {"number": n, "slug": slug} for n, slug in plan["groups"]
    ]
    metadata["baseline_head"] = d.git("rev-parse", "HEAD").stdout.strip()
    d.write_json(origin / "run.json", metadata)
    tasks = root / "openspec/changes/example-change/tasks.md"
    tasks.write_text(tasks.read_text().replace("[ ]", "[x]"))
    events = [
        {
            "schema": "changerail.delivery-phase-event.v1",
            "at": d.utc_now(),
            "phase": f"change-{n}",
            "stage": stage,
        }
        for n, _ in plan["groups"]
        for stage in ("starting", "complete")
    ]
    (origin / "phase-events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events)
    )
    child = origin.with_name("stopped-child")
    child.mkdir()
    d.write_json(
        child / "run.json",
        {
            **metadata,
            "run_id": child.name,
            "recovery_of": origin.name,
            "inherited_change_events": events,
        },
    )
    with pytest.raises(d.DeliveryError, match="plan changed"):
        board.import_accepted(d, card, child)
    assert not (child / "native-plan.json").exists()
    manifest = {**d._check_json(origin / "manifest.json"), "run_id": child.name}
    d.retain_recovery_manifest(card_name=card.name, run_dir=child, manifest=manifest)
    d.write_json(
        child / "recovery-context.json",
        {"inherited_review_budget": {"semantic_cycles": 0}},
    )
    before = {origin.name: snapshot(origin), child.name: snapshot(child)}
    capsys.readouterr()
    assert (
        d.main(
            ["plan-restore-prepare", str(child), "--reason", "restore accepted Next"]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert (
        d.main(
            [
                "plan-restore-apply",
                str(child),
                "--proposal",
                report["proposal"],
                "--authorize",
                report["proposal_sha256"],
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert d.recovery_source(card, d.changed_paths(), required_run_id=child.name)[0]
    d.require_frozen_execution(child)
    reached = []
    # Admission environment and observed-proof origin are outside this narrow
    # predecessor-transfer test. Recovery, plan, accounting and gates stay real.
    monkeypatch.setattr(
        d, "doctor", lambda *a, **kw: {"ok": True, "recovery_of": child.name}
    )
    monkeypatch.setattr(d, "_run_observed_contract", lambda *a: None)
    monkeypatch.setattr(d, "profile", lambda: {})
    monkeypatch.setattr(d, "PROFILE_PATH", root / ".changerail/profile.toml")

    def boundary(**kwargs):
        run = kwargs["run_dir"]
        reached.append(run)
        meta = d._check_json(run / "run.json")
        assert meta["recovery_of"] == child.name
        assert meta["plan_restoration"]
        assert d.recovery_ancestors(run) == [child, origin]
        native.require_plan(d, card, run / "native-plan.json")
        d.require_completed_change_plan(card, run)
        assert d.review_budget_usage(run)["semantic_cycles"] == 0
        context = d._check_json(run / "recovery-context.json")
        assert context["next_change_event"] is None
        assert "re-execute" in context["instruction"]
        # Real launcher skips all complete groups; no implementation/model call.
        monkeypatch.setattr(
            d, "launch_codex", lambda **k: pytest.fail("repeated completed group")
        )
        flow.launch_groups(
            d,
            card=card,
            run_dir=run,
            current_profile={},
            recovery_context=run / "recovery-context.json",
        )
        # No stale/synthetic handoff may advance the outer runner.
        with pytest.raises(d.DeliveryError, match="handoff"):
            d.require_current_implementation_handoff(card, run)
        return 2

    monkeypatch.setattr(d, "orchestrate_delivery", boundary)
    assert d.main(["resume", str(child)]) == 2
    assert len(reached) == 1
    assert before == {origin.name: snapshot(origin), child.name: snapshot(child)}
    assert not (child / "native-plan.json").exists()


def test_resume_exact_predecessor_is_passed_inside_writer_lock(stopped, monkeypatch):
    _root, card, run, _ = stopped
    selected = []
    monkeypatch.setattr(d, "require_frozen_execution", lambda run: {})
    monkeypatch.setattr(
        d, "recovery_source", lambda *a, **kw: (True, "exact", {"run_id": run.name})
    )

    def start(value, **kwargs):
        selected.append(kwargs)
        return 2

    monkeypatch.setattr(d, "run_delivery", start)
    assert d.main(["resume", str(run)]) == 2
    assert selected == [{"recovery": True, "required_run_id": run.name}]


def test_restoration_invalidates_old_evidence_and_records_fresh(stopped, monkeypatch):
    import sys
    from scripts.changerail import plan_restoration as restore

    root, card, run, _ = stopped
    # Real focused evidence does not need plan validity; it records the current
    # product payload. The completed task state is retained independently.
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    monkeypatch.setattr(d, "_run_observed_contract", lambda *a: None)
    assert (
        d.run_evidence(
            "before-restoration", [sys.executable, "-c", "assert 2 + 2 == 4"]
        )
        == 0
    )
    old = next((run / "focused-evidence").glob("*.json"))
    assert d.read_check_result(old, run, "focused")[2]
    d.retain_recovery_manifest(
        card_name=card.name, run_dir=run, manifest=d._check_json(run / "manifest.json")
    )
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    report = restore.prepare(d, run, reason="restore exact Next")
    before = snapshot(run)
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    assert not d.read_check_result(old, run, "focused")[2]
    fresh = run.with_name("fresh-evidence")
    fresh.mkdir()
    metadata = d._check_json(run / "run.json")
    metadata.update(run_id=fresh.name, recovery_of=run.name)
    d.write_json(fresh / "run.json", metadata)
    d.write_json(
        fresh / "recovery-context.json",
        {"inherited_review_budget": {"semantic_cycles": 0}},
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(fresh))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    assert (
        d.run_evidence("after-restoration", [sys.executable, "-c", "assert 2 + 2 == 4"])
        == 0
    )
    new = next((fresh / "focused-evidence").glob("*.json"))
    assert d.read_check_result(new, fresh, "focused")[2]
    assert snapshot(run) == before


def test_restoration_never_restarts_late_or_interrupted_work(stopped):
    from scripts.changerail import plan_restoration as restore

    _root, card, run, _ = stopped
    before = card.read_bytes()
    for name in (
        "native-review-continuation.json",
        "native-archive-intent.json",
        "native-archive.json",
        "verification.json",
        "publication.json",
        "publication-journal.json",
        "verification-attempts/interrupted.json",
    ):
        path = run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{}\n')
        history = snapshot(run)
        with pytest.raises(d.DeliveryError, match="pending|interrupted"):
            restore.prepare(d, run, reason="restore")
        assert card.read_bytes() == before
        assert snapshot(run) == history
        assert not (d.RUNTIME_ROOT / "plan-restorations").exists()
        path.unlink()
    metadata = d._check_json(run / "run.json")
    d.write_json(run / "run.json", {**metadata, "stop_reason": "operator_interrupt"})
    with pytest.raises(d.DeliveryError, match="operator-stopped"):
        restore.prepare(d, run, reason="restore")
    assert card.read_bytes() == before


def test_restoration_rejects_missing_cyclic_and_foreign_ancestors(stopped):
    from scripts.changerail import plan_restoration as restore

    _root, card, run, _ = stopped
    metadata = d._check_json(run / "run.json")
    for previous in ("missing", run.name, "foreign"):
        d.write_json(run / "run.json", {**metadata, "recovery_of": previous})
        if previous == "foreign":
            other = run.with_name(previous)
            other.mkdir()
            d.write_json(
                other / "run.json",
                {**metadata, "run_id": previous, "card": "openspec/board/3.inprogress/other.md"},
            )
        history = snapshot(run.parent)
        with pytest.raises((d.DeliveryError, OSError)):
            restore.prepare(d, run, reason="restore")
        assert snapshot(run.parent) == history
        assert not (d.RUNTIME_ROOT / "plan-restorations").exists()


def test_restoration_does_not_bypass_an_unrelated_board_gate(stopped):
    from scripts.changerail import plan_restoration as restore

    root, card, run, _ = stopped
    follower = card.with_name("follower.md")
    follower.write_text(
        "# Follower\n\n## Lifecycle\nboard-only\n\n## Depends On\n"
        "- `openspec/board/2.todo/missing.md`\n"
    )
    d.retain_recovery_manifest(
        card_name=card.name, run_dir=run, manifest=d._check_json(run / "manifest.json")
    )
    with pytest.raises(d.DeliveryError, match="dangling live board"):
        d.require_live_board_references()
    report = restore.prepare(d, run, reason="restore exact Next")
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    native.require_plan(d, card, run / "native-plan.json")
    with pytest.raises(d.DeliveryError, match="dangling live board"):
        d.require_live_board_references()
    assert (root / d.repo_relative(follower)).exists()
