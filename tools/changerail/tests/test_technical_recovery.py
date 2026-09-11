"""Fail-closed technical model recovery, including its one-group successor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import openspec_context as native
from scripts.changerail import technical_recovery as recovery
from tools.changerail.tests.test_native_openspec_integration import project as project


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _origin(project, monkeypatch, *, stderr: str = "Selected model is at capacity"):
    root, card, _client = project
    active = root / "openspec/board/3.inprogress"
    active.mkdir()
    card.write_text(
        card.read_text().replace("## Status\n1.backlog", "## Status\n3.inprogress")
    )
    card = active / card.name
    (root / "openspec" / "board" / "1.backlog" / "example.md").rename(card)
    monkeypatch.setattr(native, "require_plan", lambda *_args: None)
    profile_path = root / ".changerail/profile.toml"
    profile_path.parent.mkdir(exist_ok=True)
    profile_path.write_text('schema = "changerail.local-delivery.v1"\n')
    monkeypatch.setattr(d, "PROFILE_PATH", profile_path)
    monkeypatch.setattr(
        d,
        "profile",
        lambda: {
            "models": {
                "technical_recovery": {
                    "model": "fallback-model",
                    "reasoning_effort": "high",
                }
            }
        },
    )
    run = d.RUNTIME_ROOT / "runs" / "capacity-origin"
    run.mkdir(parents=True)
    paths = d.changed_paths()
    d.write_json(
        run / "run.json",
        {
            "schema": "changerail.delivery-run.v2",
            "run_id": run.name,
            "card": d.repo_relative(card),
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": [
                {"number": 1, "slug": "implement-behavior"},
                {"number": 2, "slug": "verify-behavior"},
            ],
            "process_identity": d.execution_identity(),
            "finished_at": "2026-09-10T00:02:00Z",
            "exit_code": 2,
            "completed": False,
        },
    )
    d.write_json(
        run / "manifest.json",
        {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run.name,
            "paths": paths,
            "fingerprint": d.payload_fingerprint(paths),
            "baseline_head": d.git("rev-parse", "HEAD").stdout.strip(),
        },
    )
    d.write_json(
        run / "native-plan.json",
        {"groups": [[1, "implement-behavior"], [2, "verify-behavior"]]},
    )
    (run / "phase-events.jsonl").write_text(
        "\n".join(
            json.dumps(
                {"phase": "change-1", "stage": stage, "at": "2026-09-10T00:00:00Z"}
            )
            for stage in ("starting", "complete")
        )
        + "\n"
    )
    d.write_json(
        run / "focused-evidence" / "completed-group.json", {"proof": "retained"}
    )
    session = run / "sessions" / "failed-group-2"
    session.mkdir(parents=True)
    d.write_json(
        session / "session.json",
        {
            "role": "implementation",
            "session": "failed-session",
            "native_change_number": 2,
            "finished_at": "2026-09-10T00:01:00Z",
            "exit_code": 1,
            "completed": False,
            "timed_out": False,
            "interrupted": False,
            "budget_violation": None,
            "stop_reason": "nonzero_exit",
            "streams_complete": True,
            "process_group_quiescent": True,
            "model": "failed-model",
        },
    )
    (session / "stderr.log").write_text(stderr)
    (session / "stdout.jsonl").write_text(
        json.dumps({"type": "thread.started", "thread_id": "failed-session"}) + "\n"
    )
    (session / "events.jsonl").write_text(
        json.dumps(
            {
                "observed_at": "2026-09-10T00:01:00Z",
                "observed_elapsed_seconds": 0.0,
                "event": {"type": "thread.started", "thread_id": "failed-session"},
            }
        )
        + "\n"
    )
    return root, card, run


def test_capacity_recovery_creates_one_successor_and_preserves_predecessor(
    project, monkeypatch
):
    _root, card, origin = _origin(project, monkeypatch)
    before = _files(origin)
    calls = []

    def launch(delivery, **kwargs):
        calls.append(kwargs)
        successor = kwargs["run_dir"]
        (successor / "phase-events.jsonl").write_text(
            json.dumps(
                {
                    "phase": "change-2",
                    "stage": "starting",
                    "at": "2026-09-10T00:02:00Z",
                }
            )
            + "\n"
            + json.dumps(
                {
                    "phase": "change-2",
                    "stage": "complete",
                    "at": "2026-09-10T00:03:00Z",
                }
            )
            + "\n"
        )

    monkeypatch.setattr(flow, "launch_groups", launch)

    def prepared(**kwargs):
        kwargs["before_orchestrate"]()
        return 0

    monkeypatch.setattr(d, "execute_prepared_delivery", prepared)
    prepared = recovery.prepare(d, origin)
    result = recovery.apply(d, origin, Path(prepared["proposal"]))
    successor = Path(result["successor"])

    assert result["state"] == "dispatched"
    assert successor.is_dir()
    assert _files(origin) == before
    metadata = d._check_json(successor / "run.json")
    assert metadata["recovery_of"] == origin.name
    assert metadata["technical_recovery"]["next_group"] == 2
    assert metadata["technical_recovery"]["fallback"]["model"] == "fallback-model"
    assert d.combined_change_events(successor)[-2:]
    assert len(calls) == 1
    assert calls[0]["only_group"] == 2
    assert calls[0]["model_route_name"] == "technical-recovery"
    # Retrying the exact immutable receipt reconciles the same child; it never relaunches it.
    repeated = recovery.apply(d, origin, Path(prepared["proposal"]))
    assert Path(repeated["successor"]) == successor
    assert len([path for path in successor.parent.iterdir() if path.is_dir()]) == 2
    assert len(calls) == 1
    assert d.resolve_deliverable_card(d.repo_relative(card)) == card


@pytest.mark.parametrize(
    "mutation, message",
    [
        ("unknown", "allowlist"),
        ("writer", "writer-started"),
        ("live", "proven terminal"),
    ],
)
def test_technical_recovery_rejects_ambiguous_or_writer_started_runs(
    project, monkeypatch, mutation, message
):
    _root, _card, origin = _origin(project, monkeypatch)
    session = origin / "sessions" / "failed-group-2"
    if mutation == "unknown":
        (session / "stderr.log").write_text("product test failed")
    elif mutation == "writer":
        with (origin / "phase-events.jsonl").open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "phase": "change-2",
                        "stage": "starting",
                        "at": "2026-09-10T00:02:00Z",
                    }
                )
                + "\n"
            )
        assert d.read_phase_events(origin)[-1]["phase"] == "change-2"
        assert (
            d.change_checkpoint_statuses(
                d.declared_change_plan(origin) or [], d.combined_change_events(origin)
            )[1]["status"]
            == "started"
        )
    else:
        value = d._check_json(session / "session.json")
        value.pop("finished_at")
        d.write_json(session / "session.json", value)

    with pytest.raises(d.DeliveryError, match=message):
        recovery.prepare(d, origin)
    assert not (d.RUNTIME_ROOT / "technical-recoveries" / origin.name).exists()
    assert len(list((d.RUNTIME_ROOT / "runs").iterdir())) == 1


def test_technical_recovery_rejects_fallback_drift_and_foreign_run(
    project, monkeypatch
):
    root, _card, origin = _origin(project, monkeypatch)
    prepared = recovery.prepare(d, origin)
    monkeypatch.setattr(
        d,
        "profile",
        lambda: {
            "models": {
                "technical_recovery": {
                    "model": "changed-fallback",
                    "reasoning_effort": "high",
                }
            }
        },
    )
    with pytest.raises(d.DeliveryError, match="drifted"):
        recovery.apply(d, origin, Path(prepared["proposal"]))
    assert len(list((d.RUNTIME_ROOT / "runs").iterdir())) == 1
    outside = root / "outside-run"
    outside.mkdir()
    with pytest.raises(d.DeliveryError, match="exact local retained"):
        recovery.prepare(d, outside)


def test_successor_uses_normal_lifecycle_and_retains_resumable_payload(
    project, monkeypatch
):
    from scripts.changerail import openspec_board

    root, card, origin = _origin(project, monkeypatch)
    before = _files(origin)
    calls = []
    monkeypatch.setattr(openspec_board, "import_accepted", lambda *_args: None)
    monkeypatch.setattr(
        d, "planned_changes", lambda *_args: d.declared_change_plan(origin)
    )

    def group(delivery, **kwargs):
        successor = kwargs["run_dir"]
        assert d.current_run_dir() == successor
        assert d._check_json(d.manifest_path(card.stem))["run_id"] == successor.name
        assert kwargs["only_group"] == 2
        assert (
            kwargs["current_profile"]["models"]["technical-recovery"]["model"]
            == "fallback-model"
        )
        calls.append("fallback")
        (root / "source.py").write_text("result = 'recovered'\n")
        with (successor / "phase-events.jsonl").open("a") as stream:
            for stage in ("starting", "complete"):
                stream.write(
                    json.dumps({"phase": "change-2", "stage": stage, "at": d.utc_now()})
                    + "\n"
                )

    def orchestrate(**kwargs):
        calls.append("normal lifecycle")
        assert (root / "source.py").read_text() == "result = 'recovered'\n"
        assert d.review_budget_usage(kwargs["run_dir"]) == {"semantic_cycles": 0}
        raise d.DeliveryError("synthetic finalize stop")

    monkeypatch.setattr(flow, "launch_groups", group)
    monkeypatch.setattr(d, "orchestrate_delivery", orchestrate)
    prepared = recovery.prepare(d, origin)
    result = recovery.apply(d, origin, Path(prepared["proposal"]))
    successor = Path(result["successor"])
    assert result["exit_code"] == 2
    assert calls == ["fallback", "normal lifecycle"]
    assert (
        d._check_json(successor / "run.json")["terminal_reason"]
        == "synthetic finalize stop"
    )
    assert d.recovery_source(card, d.changed_paths(), required_run_id=successor.name)[0]
    assert d._check_json(d.manifest_path(card.stem))["run_id"] == successor.name
    assert _files(origin) == before
    assert recovery.apply(d, origin, Path(prepared["proposal"]))["successor"] == str(
        successor
    )
    assert recovery.reconcile(d, origin)["successor"] == str(successor)
    assert calls == ["fallback", "normal lifecycle"]
    assert _files(origin) == before


@pytest.mark.parametrize("surface", ["profile", "runtime", "launcher"])
def test_recovery_cannot_adopt_changed_execution_inputs(project, monkeypatch, surface):
    root, _card, origin = _origin(project, monkeypatch)
    prepared = recovery.prepare(d, origin)
    changed = {
        "profile": d.PROFILE_PATH,
        "runtime": root / "scripts/changerail/new_core.py",
        "launcher": root / "bin/codex",
    }[surface]
    changed.parent.mkdir(parents=True, exist_ok=True)
    changed.write_text("changed input\n")
    before = _files(origin)
    with pytest.raises(d.DeliveryError, match="frozen execution process changed"):
        recovery.apply(d, origin, Path(prepared["proposal"]))
    assert _files(origin) == before
    assert len(list((d.RUNTIME_ROOT / "runs").iterdir())) == 1


@pytest.mark.parametrize(
    "event",
    [
        {"type": "item.completed", "item": {"type": kind}}
        for kind in (
            "command_execution",
            "file_change",
            "mcp_tool_call",
            "tool_call",
            "future_tool",
        )
    ]
    + [
        None,
        {"type": "future_event"},
        {"type": "turn.failed", "error": {"message": "product failure"}},
    ],
)
def test_capacity_text_does_not_hide_execution_or_unknown_events(
    project, monkeypatch, event
):
    _root, _card, origin = _origin(project, monkeypatch)
    session = origin / "sessions/failed-group-2"
    (session / "stdout.jsonl").write_text(json.dumps(event) + "\n")
    (session / "events.jsonl").write_text(json.dumps({"event": event}) + "\n")
    before = _files(origin)
    with pytest.raises(d.DeliveryError, match="execution|unknown"):
        recovery.prepare(d, origin)
    assert _files(origin) == before


@pytest.mark.parametrize("field", ["streams_complete", "process_group_quiescent"])
def test_capacity_rejects_incomplete_capture_or_live_process_group(
    project, monkeypatch, field
):
    _root, _card, origin = _origin(project, monkeypatch)
    path = origin / "sessions/failed-group-2/session.json"
    metadata = d._check_json(path)
    metadata[field] = False
    d.write_json(path, metadata)
    with pytest.raises(d.DeliveryError, match="proven terminal"):
        recovery.prepare(d, origin)


def test_recovery_rejects_payload_change_before_dispatch(project, monkeypatch):
    root, _card, origin = _origin(project, monkeypatch)
    prepared = recovery.prepare(d, origin)
    monkeypatch.setattr(recovery, "_launch_successor_group", lambda *_args: 2)
    result = recovery.apply(d, origin, Path(prepared["proposal"]))
    (root / "new-product.py").write_text("unexpected\n")
    with pytest.raises(d.DeliveryError, match="payload differs|drifted"):
        recovery.apply(d, origin, Path(prepared["proposal"]))
    assert Path(result["successor"]).exists()
    assert len(list((d.RUNTIME_ROOT / "runs").iterdir())) == 2


def test_recovery_rejects_unresolved_verification(project, monkeypatch):
    _root, _card, origin = _origin(project, monkeypatch)
    d.write_json(origin / "verification-attempts/pending.json", {"state": "started"})
    with pytest.raises(d.DeliveryError, match="unresolved verification"):
        recovery.prepare(d, origin)


def test_concurrent_recovery_obeys_real_project_lock(project, monkeypatch):
    _root, _card, origin = _origin(project, monkeypatch)
    before = _files(origin)
    with d.delivery_lock():
        with pytest.raises(d.DeliveryError, match="another delivery runner"):
            recovery.prepare(d, origin)
    assert _files(origin) == before
    assert not (d.RUNTIME_ROOT / "technical-recoveries" / origin.name).exists()


def test_retry_after_successor_intent_reuses_the_staged_child(project, monkeypatch):
    _root, _card, origin = _origin(project, monkeypatch)
    before = _files(origin)
    prepared = recovery.prepare(d, origin)
    publish = recovery._publish_successor
    calls = []

    def crash(*_args):
        raise d.DeliveryError("synthetic crash before rename")

    monkeypatch.setattr(recovery, "_publish_successor", crash)
    with pytest.raises(d.DeliveryError, match="crash before rename"):
        recovery.apply(d, origin, Path(prepared["proposal"]))
    intent = d._check_json(
        Path(prepared["proposal"]).with_name("successor-intent.json")
    )
    monkeypatch.setattr(recovery, "_publish_successor", publish)

    def execute(**kwargs):
        calls.append(kwargs["run_dir"].name)
        return 2

    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    result = recovery.apply(d, origin, Path(prepared["proposal"]))
    assert Path(result["successor"]).name == intent["successor"]
    assert recovery.apply(d, origin, Path(prepared["proposal"]))["exit_code"] == 2
    assert calls == [intent["successor"]]
    assert len(list((d.RUNTIME_ROOT / "runs").iterdir())) == 2
    assert _files(origin) == before


def test_recovery_does_not_fork_an_existing_continuation(project, monkeypatch):
    _root, _card, origin = _origin(project, monkeypatch)
    child = origin.parent / "ordinary-child"
    d.write_json(
        child / "run.json",
        {
            **d._check_json(origin / "run.json"),
            "run_id": child.name,
            "recovery_of": origin.name,
        },
    )
    before = _files(origin.parent)
    with pytest.raises(d.DeliveryError, match="already has a continuation"):
        recovery.prepare(d, origin)
    assert _files(origin.parent) == before


def test_recovery_requires_clean_index(project, monkeypatch):
    _root, card, origin = _origin(project, monkeypatch)
    d.git("add", "--", d.repo_relative(card))
    with pytest.raises(d.DeliveryError, match="empty index"):
        recovery.prepare(d, origin)
