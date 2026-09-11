"""Regressions for retained stock archive intent and explicit Node resolution."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import openspec_context as native
from scripts.changerail import openspec_adapter as adapter
from tools.changerail.tests.test_native_openspec_integration import project as project
from tools.changerail.tests.test_plan_restoration import stopped as stopped


def interrupted_archive(project, monkeypatch):
    root, card, client = project
    active = root / "openspec/changes/example-change"
    tasks = active / "tasks.md"
    tasks.write_text(tasks.read_text().replace("[ ]", "[x]"))
    run = root / ".runtime/changerail/runs/interrupted"
    run.mkdir(parents=True)
    original_archive = client.archive

    class Yesterday:
        @staticmethod
        def now(tz):
            return datetime.now(tz) - timedelta(days=1)

    def interrupted(_identifier):
        raise RuntimeError("interrupted before stock move")

    monkeypatch.setattr(native, "adapter", lambda _delivery: client)
    monkeypatch.setattr(flow, "datetime", Yesterday)
    monkeypatch.setattr(client, "archive", interrupted)
    with pytest.raises(RuntimeError, match="interrupted before"):
        flow.archive_move(d, card, run)
    monkeypatch.setattr(flow, "datetime", datetime)
    monkeypatch.setattr(client, "archive", original_archive)
    return run, (run / "native-archive-intent.json").read_bytes()


@pytest.mark.parametrize("interrupt_successor", [False, True])
def test_archive_rollover_retains_intent_and_reconciles_stock_move(
    project, monkeypatch, interrupt_successor
):
    root, card, client = project
    run, original = interrupted_archive(project, monkeypatch)
    successor_before = None
    if interrupt_successor:
        original_archive = client.archive

        def interrupted(_identifier):
            raise RuntimeError("interrupted after successor intent")

        monkeypatch.setattr(client, "archive", interrupted)
        with pytest.raises(RuntimeError, match="after successor intent"):
            flow.archive_move(d, card, run)
        successor_before = (
            run / "native-archive-intent-successors/001.json"
        ).read_bytes()
        monkeypatch.setattr(client, "archive", original_archive)
    target = flow.archive_move(d, card, run)
    assert target.name == f"{datetime.now(timezone.utc).date()}-example-change"
    assert not (root / "openspec/changes/example-change").exists()
    assert (run / "native-archive-intent.json").read_bytes() == original
    successors = list((run / "native-archive-intent-successors").glob("*.json"))
    assert len(successors) == 1
    retained = successors[0].read_bytes()
    if interrupt_successor:
        assert retained == successor_before
    assert flow.archive_move(d, card, run) == target
    assert successors[0].read_bytes() == retained
    # Public resume calls this helper after carrying the initial intent.
    current = run.with_name("resumed")
    current.mkdir()
    (current / "native-archive-intent.json").write_bytes(original)
    report = run / "sync-report.md"
    report.write_text("retained semantic sync")
    preliminary = run / "preliminary.json"
    preliminary.write_text('{"verdict": "GO"}')
    d.write_json(
        run / "native-sync.json",
        {
            "report": d.repo_relative(report),
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        },
    )
    d.write_json(
        run / "native-review-continuation.json",
        {
            "preliminary": d.repo_relative(preliminary),
            "preliminary_sha256": hashlib.sha256(preliminary.read_bytes()).hexdigest(),
        },
    )
    flow.inherit_archived_context(d, run, current)
    inherited = current / successors[0].relative_to(run)
    assert inherited.read_bytes() == retained
    assert flow.archive_move(d, card, current) == target
    for mutation in ("raw_artifacts", "predecessor_sha256", "destination"):
        corrupted = json.loads(retained)
        corrupted[mutation] = None
        d.write_json(inherited, corrupted)
        with pytest.raises(d.DeliveryError, match="successor"):
            flow.archive_move(d, card, current)


@pytest.mark.parametrize("mutation", ["active", "outside", "old-target", "new-target"])
def test_archive_rollover_rejects_changed_or_colliding_payload(
    project, monkeypatch, mutation
):
    root, card, client = project
    run, original = interrupted_archive(project, monkeypatch)
    intent = json.loads(original)
    if mutation == "active":
        (root / intent["source"] / "tasks.md").write_text("- [x] replaced task\n")
    elif mutation == "outside":
        (root / "unrelated.txt").write_text("changed\n")
    else:
        destination = (
            root / intent["destination"]
            if mutation == "old-target"
            else root
            / "openspec/changes/archive"
            / f"{datetime.now(timezone.utc).date()}-example-change"
        )
        destination.mkdir(parents=True)
    monkeypatch.setattr(
        client, "archive", lambda _identifier: pytest.fail("unsafe stock move")
    )
    with pytest.raises(d.DeliveryError):
        flow.archive_move(d, card, run)
    assert (run / "native-archive-intent.json").read_bytes() == original
    assert not (run / "native-archive-intent-successors").exists()


def test_node_is_resolved_once_from_path_and_cli_stays_local(tmp_path, monkeypatch):
    dependency = tmp_path / "tools/openspec/node_modules/@fission-ai/openspec"
    (dependency / "bin").mkdir(parents=True)
    (dependency / "package.json").write_text(
        json.dumps({"name": "@fission-ai/openspec", "version": "1.3.1"})
    )
    (dependency / "bin/openspec.js").write_text("fixture\n")
    selected = tmp_path / "custom-bin/node"
    selected.parent.mkdir()
    selected.write_text("#!/bin/sh\nexit 0\n")
    selected.chmod(0o755)
    monkeypatch.setenv("PATH", str(selected.parent))
    calls = []

    def invoke(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, "1.3.1\n", "")

    monkeypatch.setattr(adapter.subprocess, "run", invoke)
    client = adapter.OpenSpecAdapter(tmp_path)
    assert client.node == selected.resolve()
    monkeypatch.setenv("PATH", "/unavailable")
    client._invoke("--version")
    assert all(
        call[0][:2] == [str(selected.resolve()), str(client.cli)] for call in calls
    )
    assert all(call[1]["env"]["XDG_DATA_HOME"] != str(tmp_path) for call in calls)


def test_missing_path_node_has_actionable_error(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(d.DeliveryError, match="Node.js.*PATH"):
        adapter.OpenSpecAdapter(tmp_path)


def test_plan_drift_and_manual_restore_form_two_distinct_recovery_failures(
    stopped,
):
    """Exercise real accepted-plan and exact-payload gates, then authorized repair."""
    from pathlib import Path
    from scripts.changerail import openspec_board as board
    from scripts.changerail import plan_restoration as restore

    _root, card, run, _accepted = stopped
    historical = restore._inventory(d, run)
    changed = card.read_bytes()
    assert d.recovery_source(card, d.changed_paths(), required_run_id=run.name)[0]
    with pytest.raises(d.DeliveryError, match="plan changed"):
        native.require_plan(d, card, run / "native-plan.json")
    child = run.with_name("failed-import")
    child.mkdir()
    with pytest.raises(d.DeliveryError, match="plan changed"):
        board.import_accepted(d, card, child)
    assert not (child / "native-plan.json").exists()

    card.write_bytes(changed.replace(b"- changed Next", b"- implement"))
    native.require_plan(d, card, run / "native-plan.json")
    assert not d.recovery_source(card, d.changed_paths(), required_run_id=run.name)[0]
    card.write_bytes(changed)
    with d.delivery_lock():
        with pytest.raises(d.DeliveryError, match="another delivery runner"):
            restore.prepare(d, run, reason="competing writer")
    assert not (d.RUNTIME_ROOT / "plan-restorations").exists()
    prepared = restore.prepare(d, run, reason="restore accepted Next")
    restore.apply(d, run, Path(prepared["proposal"]), prepared["proposal_sha256"])
    native.require_plan(d, card, run / "native-plan.json")
    assert d.recovery_source(card, d.changed_paths(), required_run_id=run.name)[0]
    assert restore._inventory(d, run) == historical


def test_technical_recovery_preserves_predecessor_history_and_review_budget(
    project, monkeypatch
):
    """The dispatch callback is isolated; recovery receipts and state remain real."""
    from scripts.changerail import technical_recovery as recovery
    from tools.changerail.tests.test_technical_recovery import _files, _origin

    _root, _card, origin = _origin(project, monkeypatch)
    before_files = _files(origin)
    before_payload = d.payload_fingerprint(d.changed_paths())
    before_events = d.combined_change_events(origin)
    before_checkpoints = d.change_checkpoint_statuses(
        d.declared_change_plan(origin) or [], before_events
    )
    before_budget = d.review_budget_usage(origin)
    launches: list[dict[str, object]] = []

    def launch(_delivery, **kwargs) -> None:
        launches.append(kwargs)

    def execute(**kwargs) -> int:
        kwargs["before_orchestrate"]()
        return 0

    monkeypatch.setattr(flow, "launch_groups", launch)
    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    prepared = recovery.prepare(d, origin)
    first = recovery.apply(d, origin, Path(prepared["proposal"]))
    successor = Path(first["successor"])
    repeated = recovery.apply(d, origin, Path(prepared["proposal"]))
    reconciled = recovery.reconcile(d, origin)

    assert _files(origin) == before_files
    assert d.payload_fingerprint(d.changed_paths()) == before_payload
    assert d.combined_change_events(origin) == before_events
    assert d.change_checkpoint_statuses(
        d.declared_change_plan(origin) or [], d.combined_change_events(origin)
    ) == before_checkpoints
    assert d.review_budget_usage(origin) == before_budget == {"semantic_cycles": 0}
    assert d.review_budget_usage(successor) == before_budget
    assert d._check_json(successor / "recovery-context.json")[
        "inherited_review_budget"
    ] == before_budget
    assert Path(repeated["successor"]) == successor
    assert Path(reconciled["successor"]) == successor
    assert len(launches) == 1 and launches[0]["only_group"] == 2
