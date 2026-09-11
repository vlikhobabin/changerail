"""Self-host recovery retains exact history and admits only complete finalization."""

from pathlib import Path
import json
import shutil
import pytest
from scripts.changerail import self_host_recovery as recovery
from scripts.changerail import local_delivery as d
from tools.changerail.tests.test_technical_recovery import _origin, _files
from tools.changerail.tests.test_native_openspec_integration import project as project


def origin(project, monkeypatch):
    root, card, run = _origin(project, monkeypatch)
    owner = d._check_json(run / "run.json")
    owner["terminal_reason"] = "implementation session exited without a handoff"
    d.write_json(run / "run.json", owner)
    events = run / "phase-events.jsonl"
    with events.open("a") as stream:
        for stage in ("starting", "complete"):
            stream.write(
                json.dumps(
                    {"phase": "change-2", "stage": stage, "at": "2026-09-10T00:02:00Z"}
                )
                + "\n"
            )
    session = run / "sessions/failed-group-2/session.json"
    metadata = d._check_json(session)
    metadata.update(
        exit_code=0, completed=False, stop_reason="incomplete_session_no_artifact"
    )
    d.write_json(session, metadata)
    manifest = d._check_json(run / "manifest.json")
    manifest["path_fingerprints"] = d.path_fingerprints(manifest["paths"])
    d.write_json(run / "manifest.json", manifest)
    snapshot = root.parent / "payload"
    snapshot.mkdir()
    for relative in manifest["paths"]:
        source = root / relative
        if source.is_file():
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    monkeypatch.setattr(recovery, "_engine", lambda _d: {"engine": "test-engine"})
    from scripts.changerail import engine_runtime

    profile_hash = d._check_json(run / "run.json")["process_identity"][
        d.repo_relative(d.PROFILE_PATH)
    ]
    monkeypatch.setattr(
        engine_runtime,
        "project_execution_identity",
        lambda _d: {d.repo_relative(d.PROFILE_PATH): profile_hash},
    )
    return root, card, run, snapshot


def test_recovery_requires_retained_payload_bytes(project, monkeypatch):
    root, _card, run, _snapshot = origin(project, monkeypatch)
    (root / "src/feature.py").parent.mkdir(exist_ok=True)
    # Change a path that belongs to the retained manifest.
    selected = next(
        p for p in d._check_json(run / "manifest.json")["paths"] if (root / p).is_file()
    )
    (root / selected).write_text("drift\n")
    with pytest.raises(d.DeliveryError, match="payload bytes"):
        recovery.prepare(d, run)


def test_successor_preserves_history_and_dispatches_once(project, monkeypatch):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    before = _files(run)
    calls = []

    def execute(**kwargs):
        calls.append(kwargs)
        child = kwargs["run_dir"]
        assert all(
            row["status"] == "complete"
            for row in d.change_checkpoint_statuses(
                d.declared_change_plan(child), d.combined_change_events(child)
            )
        )
        assert d.review_budget_usage(child) == {"semantic_cycles": 0}
        assert not (child / "native-sync.json").exists()
        return 0

    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    result = recovery.apply(d, run, Path(prepared["proposal"]))
    assert result["state"] == "dispatched"
    assert len(calls) == 1
    assert _files(run) == before
    repeated = recovery.apply(d, run, Path(prepared["proposal"]))
    assert repeated["successor"] == result["successor"]
    assert len(calls) == 1
    assert recovery.reconcile(d, run)["successor"] == result["successor"]


@pytest.mark.parametrize(
    "mutation", ["pending", "live_session", "archive", "interrupted_check"]
)
def test_boundary_rejects_unsafe_predecessor(project, monkeypatch, mutation):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    if mutation == "pending":
        (run / "phase-events.jsonl").write_text("")
    elif mutation == "live_session":
        session = run / "sessions/failed-group-2/session.json"
        value = d._check_json(session)
        value.pop("finished_at")
        d.write_json(session, value)
    elif mutation == "archive":
        d.write_json(run / "native-archive-intent.json", {})
    else:
        d.write_json(run / "verification-attempts/live.json", {"state": "started"})
    with pytest.raises(d.DeliveryError):
        recovery.prepare(d, run, payload_snapshot=snapshot)


@pytest.mark.parametrize("mutation", ["payload", "history", "engine", "proposal"])
def test_prepared_drift_cannot_dispatch(project, monkeypatch, mutation):
    root, _card, run, snapshot = origin(project, monkeypatch)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    proposal = Path(prepared["proposal"])
    if mutation == "payload":
        (root / "new-product.txt").write_text("drift")
    elif mutation == "history":
        (run / "metrics.json").write_text("{}")
    elif mutation == "engine":
        monkeypatch.setattr(recovery, "_engine", lambda _d: {"engine": "foreign"})
    else:
        value = d._check_json(proposal)
        value["corrective_diff"].append({"path": "forged"})
        d.write_json(proposal, value)
    with pytest.raises(d.DeliveryError):
        recovery.apply(d, run, proposal)
    assert not list(run.parent.glob("self-host-*/run.json"))


@pytest.mark.parametrize("boundary", ["before_publish", "after_publish", "dispatch"])
def test_crash_reconciles_same_successor_without_writer(project, monkeypatch, boundary):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    before = _files(run)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    original_rename = recovery.os.rename
    original_write = recovery._write
    calls = []
    monkeypatch.setattr(
        d,
        "execute_prepared_delivery",
        lambda **kwargs: calls.append(kwargs["run_dir"]) or 0,
    )

    def rename(source, target):
        if Path(target).parent == run.parent and Path(target).name.startswith(
            "self-host-"
        ):
            if boundary == "before_publish":
                raise OSError("crash")
            original_rename(source, target)
            raise OSError("crash")
        original_rename(source, target)

    def write(path, value):
        original_write(path, value)
        if path.name == "dispatch.json":
            raise OSError("crash")

    with monkeypatch.context() as patch:
        if boundary == "dispatch":
            patch.setattr(recovery, "_write", write)
        else:
            patch.setattr(recovery.os, "rename", rename)
        with pytest.raises(OSError, match="crash"):
            recovery.apply(d, run, Path(prepared["proposal"]))
    result = recovery.reconcile(d, run)
    assert calls == []
    assert _files(run) == before
    repeated = recovery.apply(d, run, Path(prepared["proposal"]))
    assert repeated["successor"] == result["successor"]
    assert len(calls) == (0 if boundary == "dispatch" else 1)
    assert len(list(run.parent.glob("self-host-*/run.json"))) == 1


def test_cross_checkout_copies_exact_history_and_reserves_origin(project, monkeypatch):
    root, _card, run, snapshot = origin(project, monkeypatch)
    remote = root.parent / "old-checkout"
    shutil.copytree(root, remote)
    source_run = remote / run.relative_to(root)
    shutil.rmtree(run)
    before = _files(source_run)
    prepared = recovery.prepare(d, source_run, payload_snapshot=snapshot)
    monkeypatch.setattr(d, "execute_prepared_delivery", lambda **_kwargs: 0)
    result = recovery.apply(d, source_run, Path(prepared["proposal"]))
    assert _files(source_run) == before
    assert _files(run) == before
    reservation = (
        remote / ".runtime/changerail/self-host-transitions" / (run.name + ".json")
    )
    value = recovery._json(d, reservation)
    assert value["project"] == str(root)
    assert value["successor"] == Path(result["successor"]).name
    with pytest.raises(d.DeliveryError, match="superseded"):
        recovery.require_not_superseded(d, run)
    recovery.require_not_superseded(d, Path(result["successor"]))
    with pytest.raises(d.DeliveryError, match="self-host transition"):
        d.require_frozen_execution(run)
    d.require_frozen_execution(Path(result["successor"]))
    value["project"] = str(remote)
    d.write_json(reservation, value)
    with pytest.raises(d.DeliveryError, match="another transition"):
        recovery.reconcile(d, source_run)


def test_live_process_and_held_origin_lock_block_apply(project, monkeypatch):
    import fcntl
    import os
    import subprocess

    root, _card, run, snapshot = origin(project, monkeypatch)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    process = subprocess.Popen(
        ["sleep", "30"], env={**os.environ, "CHRL_RUN_DIR": str(run)}
    )
    try:
        with pytest.raises(d.DeliveryError, match="live process"):
            recovery.apply(d, run, Path(prepared["proposal"]))
    finally:
        process.terminate()
        process.wait()
    with (root / ".runtime/changerail/delivery.lock").open("r+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(d.DeliveryError, match="holds a checkout"):
            recovery.apply(d, run, Path(prepared["proposal"]))


def test_concurrent_apply_reserves_single_writer(project, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    _root, _card, run, snapshot = origin(project, monkeypatch)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    entered, release = Event(), Event()

    def execute(**_kwargs):
        entered.set()
        assert release.wait(10)
        return 0

    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(recovery.apply, d, run, Path(prepared["proposal"]))
        assert entered.wait(10)
        try:
            with pytest.raises(d.DeliveryError, match="holds a checkout"):
                recovery.apply(d, run, Path(prepared["proposal"]))
        finally:
            release.set()
        result = first.result()
    assert len(list(run.parent.glob("self-host-*/run.json"))) == 1
    assert result["state"] == "dispatched"


def test_successor_runs_normal_finalize_review_archive_final_publication(
    project, monkeypatch
):
    from scripts.changerail import native_workflow as flow
    from scripts.changerail import openspec_board
    from scripts.changerail import openspec_context as native

    root, card, run, snapshot = origin(project, monkeypatch)
    before = _files(run)
    monkeypatch.setattr(openspec_board, "import_accepted", lambda *_args: None)
    monkeypatch.setattr(
        d, "planned_changes", lambda *_args: d.declared_change_plan(run)
    )
    calls = []

    def groups(_delivery, **kwargs):
        states = d.change_checkpoint_statuses(
            d.declared_change_plan(kwargs["run_dir"]),
            d.combined_change_events(kwargs["run_dir"]),
        )
        assert all(row["status"] == "complete" for row in states)

    def implementation(**kwargs):
        child = kwargs["run_dir"]
        assert d.current_run_dir() == child
        assert d._check_json(d.manifest_path(card.stem))["run_id"] == child.name
        calls.append("archive-refresh" if kwargs.get("repair_context") else "finalize")

    def review(_card):
        calls.append("review")
        return 0

    def archive(_delivery, _card, child):
        calls.append("archive")
        d.write_json(child / "native-archive.json", {"schema": "synthetic"})
        return {"schema": "synthetic"}

    def verify(_card):
        calls.append("final")
        return 0

    def publish(_card):
        calls.append("publish")
        done = root / "openspec/board/4.done" / card.name
        done.parent.mkdir(exist_ok=True)
        card.rename(done)
        d.git("add", "-A")
        d.git("commit", "-m", "synthetic delivery publication")
        return 0

    monkeypatch.setattr(flow, "launch_groups", groups)
    monkeypatch.setattr(d, "launch_implementation_stage", implementation)
    monkeypatch.setattr(d, "run_review", review)
    monkeypatch.setattr(native, "archive", archive)
    monkeypatch.setattr(d, "verify_as_outer_dispatch", verify)
    monkeypatch.setattr(d, "publish", publish)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    result = recovery.apply(d, run, Path(prepared["proposal"]))
    assert result["exit_code"] == 0
    assert calls == [
        "finalize",
        "review",
        "archive",
        "archive-refresh",
        "review",
        "final",
        "publish",
    ]
    assert _files(run) == before
    assert recovery.reconcile(d, run)["exit_code"] == 0


@pytest.mark.parametrize("count", [1, 2])
def test_review_boundary_is_rejected_even_after_no_go(project, monkeypatch, count):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    for number in range(1, count + 1):
        d.write_json(
            run / "reviews" / f"cycle-{number:02d}.json",
            {"result": "no-go", "workspace": {"old": True}},
        )
    with pytest.raises(d.DeliveryError, match="review"):
        recovery.prepare(d, run, payload_snapshot=snapshot)
    assert not (
        d.RUNTIME_ROOT / "self-host-transitions" / (run.name + ".json")
    ).exists()


def test_copy_corruption_after_dispatch_is_rejected(project, monkeypatch):
    root, _card, run, snapshot = origin(project, monkeypatch)
    remote = root.parent / "old-checkout"
    shutil.copytree(root, remote)
    source_run = remote / run.relative_to(root)
    shutil.rmtree(run)
    prepared = recovery.prepare(d, source_run, payload_snapshot=snapshot)
    monkeypatch.setattr(d, "execute_prepared_delivery", lambda **_kwargs: 0)
    recovery.apply(d, source_run, Path(prepared["proposal"]))
    (run / "phase-events.jsonl").write_text("")
    with pytest.raises(d.DeliveryError, match="local predecessor history drifted"):
        recovery.reconcile(d, source_run)


def test_receipt_retains_exact_corrective_bytes_and_modes(project, monkeypatch):
    import base64

    root, _card, run, snapshot = origin(project, monkeypatch)
    product = root / "correction.bin"
    product.write_bytes(b"\x00corrective\xff")
    product.chmod(0o755)
    prepared = recovery.prepare(d, run, payload_snapshot=snapshot)
    proposal = recovery._json(d, Path(prepared["proposal"]))
    delta = next(
        row for row in proposal["corrective_diff"] if row["path"] == "correction.bin"
    )
    assert delta["before"] is None
    assert delta["after"] == {
        "mode": 0o755,
        "bytes": base64.b64encode(product.read_bytes()).decode(),
    }
    assert proposal["old_payload"]


def test_project_execution_input_drift_is_not_engine_adoption(project, monkeypatch):
    root, _card, run, snapshot = origin(project, monkeypatch)
    profile = root / ".changerail/profile.toml"
    profile.write_text(profile.read_text() + "# changed\n")
    with pytest.raises(d.DeliveryError, match="execution inputs changed"):
        recovery.prepare(d, run, payload_snapshot=snapshot)


@pytest.mark.parametrize(
    "kind", ["review-session", "review-event", "operator-interrupt", "semantic-failure"]
)
def test_forbidden_terminal_boundary(project, monkeypatch, kind):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    if kind == "review-session":
        d.write_json(
            run / "sessions/review/session.json",
            {"role": "review", "finished_at": d.utc_now(), "exit_code": 0},
        )
    elif kind == "review-event":
        with (run / "phase-events.jsonl").open("a") as stream:
            stream.write(json.dumps({"phase": "review", "stage": "waiting"}) + "\n")
    elif kind == "operator-interrupt":
        path = run / "sessions/failed-group-2/session.json"
        value = d._check_json(path)
        value["interrupted"] = True
        d.write_json(path, value)
    else:
        value = d._check_json(run / "run.json")
        value["terminal_reason"] = "product test failure"
        d.write_json(run / "run.json", value)
    with pytest.raises(d.DeliveryError):
        recovery.prepare(d, run, payload_snapshot=snapshot)


@pytest.mark.parametrize("kind", ["missing", "role", "stop", "exit-type"])
def test_unknown_session_state_is_rejected(project, monkeypatch, kind):
    _root, _card, run, snapshot = origin(project, monkeypatch)
    if kind == "missing":
        (run / "sessions/unknown").mkdir()
    else:
        path = run / "sessions/failed-group-2/session.json"
        value = d._check_json(path)
        if kind == "role":
            value.pop("role")
        if kind == "stop":
            value["stop_reason"] = "unknown"
        if kind == "exit-type":
            value["exit_code"] = False
        d.write_json(path, value)
    with pytest.raises(d.DeliveryError, match="session"):
        recovery.prepare(d, run, payload_snapshot=snapshot)


@pytest.mark.parametrize("tamper", [False, True])
def test_completed_technical_successor_retains_classified_capacity_history(
    project, monkeypatch, tamper
):
    from scripts.changerail import technical_recovery as technical

    root, card, previous = _origin(project, monkeypatch)
    monkeypatch.setattr(d, "execute_prepared_delivery", lambda **kwargs: 0)
    prepared = technical.prepare(d, previous)
    result = technical.apply(d, previous, Path(prepared["proposal"]))
    run = Path(result["successor"])
    metadata = d._check_json(run / "run.json")
    metadata.update(
        finished_at=d.utc_now(),
        exit_code=2,
        terminal_reason="implementation session exited without a handoff",
    )
    d.write_json(run / "run.json", metadata)
    with (run / "phase-events.jsonl").open("a") as stream:
        for stage in ("starting", "complete"):
            stream.write(
                json.dumps({"phase": "change-2", "stage": stage, "at": d.utc_now()})
                + "\n"
            )
    manifest = d._check_json(run / "manifest.json")
    manifest.update(
        paths=d.changed_paths(),
        fingerprint=d.payload_fingerprint(),
        path_fingerprints=d.path_fingerprints(d.changed_paths()),
    )
    d.write_json(run / "manifest.json", manifest)
    monkeypatch.setattr(recovery, "_engine", lambda _d: {"engine": "fixture"})
    from scripts.changerail import engine_runtime

    monkeypatch.setattr(
        engine_runtime,
        "project_execution_identity",
        lambda _d: {
            d.repo_relative(d.PROFILE_PATH): metadata["process_identity"][
                d.repo_relative(d.PROFILE_PATH)
            ]
        },
    )
    if tamper:
        p = Path(prepared["proposal"])
        value = d._check_json(p)
        value["failure"]["session_sha256"] = "sha256:" + "0" * 64
        d.write_json(p, value)
        with pytest.raises(d.DeliveryError):
            recovery.prepare(d, run)
    else:
        assert recovery.prepare(d, run)["state"] == "prepared"
