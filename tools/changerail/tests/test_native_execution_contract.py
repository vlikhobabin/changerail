from __future__ import annotations
import hashlib
import subprocess
import pytest
from scripts.changerail import local_delivery as d
from tools.changerail.tests.test_native_openspec_integration import project as project


@pytest.fixture
def contract_run(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    for args in [
        ("init", "-b", "main"),
        ("config", "user.name", "Fixture"),
        ("config", "user.email", "fixture@example.invalid"),
    ]:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(".runtime/\n")
    (root / "tracked.txt").write_text("before\n")
    (root / ".changerail").mkdir()
    profile = root / ".changerail/profile.toml"
    profile.write_text(
        'schema="changerail.local-delivery.v1"\n[budgets]\nenforce_limits=false\n'
    )
    for key, value in [
        ("REPO_ROOT", root),
        ("BOARD_ROOT", root / "openspec/board"),
        ("RUNTIME_ROOT", root / ".runtime/changerail"),
        ("PROFILE_PATH", profile),
    ]:
        monkeypatch.setattr(d, key, value)
    card = root / "openspec" / "board" / "3.inprogress" / "change.md"
    card.parent.mkdir(parents=True)
    card.write_text("# Card\n\n## Lifecycle\nopenspec-v1\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "baseline"], cwd=root, check=True, capture_output=True
    )
    run = d.RUNTIME_ROOT / "runs" / "native"
    run.mkdir(parents=True)
    data = {
        "schema": "changerail.delivery-run.v2",
        "run_id": run.name,
        "card": d.repo_relative(card),
        "execution_contract": "changerail.native.v1",
        "mode": "delivery",
        "lifecycle_mode": "openspec-v1",
        "started_at": d.utc_now(),
        "process_identity": d.execution_identity(),
    }
    d.write_json(run / "run.json", data)
    return root, card, run, data


@pytest.mark.parametrize(
    "field,value",
    [
        ("execution_contract", None),
        ("mode", "recovery"),
        ("lifecycle_mode", "board-only"),
    ],
)
def test_historical_execution_rejected_without_receipt_writes(
    contract_run, monkeypatch, field, value
):
    root, card, run, data = contract_run
    data[field] = value
    d.write_json(run / "run.json", data)
    before = {p: p.read_bytes() for p in run.iterdir()}
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    with pytest.raises(d.DeliveryError, match="read-only"):
        d.current_run_dir()
    assert {p: p.read_bytes() for p in run.iterdir()} == before


def test_frozen_process_refuses_profile_drift(contract_run):
    root, card, run, data = contract_run
    assert d.require_frozen_execution(run) == data
    before = (run / "run.json").read_bytes()
    d.PROFILE_PATH.write_text(
        'schema="changerail.local-delivery.v1"\n[budgets]\nenforce_limits=true\n'
    )
    with pytest.raises(d.DeliveryError, match="process changed"):
        d.require_frozen_execution(run)
    assert (run / "run.json").read_bytes() == before


@pytest.mark.parametrize(
    "relative",
    [
        "scripts/__init__.py",
        "tools/openspec/workflow-instructions.mjs",
        "tools/openspec/check-install.mjs",
        "tools/openspec/package.json",
        "tools/openspec/package-lock.json",
        "tools/openspec/bootstrap.sh",
    ],
)
@pytest.mark.parametrize("change", ["edit", "remove", "add"])
def test_frozen_process_refuses_openspec_runtime_drift(contract_run, relative, change):
    root, _, run, data = contract_run
    runtime = root / relative
    runtime.parent.mkdir(parents=True, exist_ok=True)
    if change != "add":
        runtime.write_text("original runtime bytes\n")
    data["process_identity"] = d.execution_identity()
    d.write_json(run / "run.json", data)
    original = (run / "run.json").read_bytes()
    assert d.require_frozen_execution(run) == data
    if change == "remove":
        runtime.unlink()
    else:
        runtime.write_text("different runtime bytes\n")
    with pytest.raises(d.DeliveryError, match="process changed"):
        d.require_frozen_execution(run)
    assert (run / "run.json").read_bytes() == original


def test_history_metrics_never_overwrite_retained_bytes(contract_run):
    root, card, run, data = contract_run
    data["execution_contract"] = "old"
    d.write_json(run / "run.json", data)
    metrics = run / "metrics.json"
    metrics.write_text('{"historical": true}\n')
    before = {p: p.read_bytes() for p in run.iterdir()}
    d.build_metrics(run)
    assert {p: p.read_bytes() for p in run.iterdir()} == before


@pytest.mark.parametrize(
    "contour", ["runs", "delivery-runs", "ff-runs", "offline-finalizations"]
)
def test_historical_cli_readers_preserve_bytes_and_refuse_execution(
    contract_run, contour, capsys
):
    from scripts.changerail.native_workflow import retained_run

    root, card, run, data = contract_run
    history = d.RUNTIME_ROOT / contour / "history"
    history.mkdir(parents=True)
    d.write_json(
        history / "run.json",
        {
            "run_id": "history",
            "mode": "ff",
            "card": d.repo_relative(card),
            "started_at": d.utc_now(),
        },
    )
    (history / "metrics.json").write_text('{"retained":true}\n')
    before = {p: p.read_bytes() for p in history.rglob("*") if p.is_file()}
    assert d.main(["status", str(history)]) == 0
    assert d.main(["metrics", str(history)]) == 0
    assert {p: p.read_bytes() for p in history.rglob("*") if p.is_file()} == before
    if contour != "runs":
        with pytest.raises(d.DeliveryError, match="exact local retained run"):
            retained_run(d, history)
    assert d.main(["resume", str(history)]) == 2
    alias = history.parent / "alias"
    alias.symlink_to(history, target_is_directory=True)
    assert d.main(["status", str(alias)]) == 2
    assert d.main(["metrics", str(alias)]) == 2


def test_old_board_only_is_readable_but_not_deliverable(contract_run):
    root, card, run, data = contract_run
    card.write_text("# Historical\n\n## Lifecycle\nboard-only\n")
    assert d.native.lifecycle_mode(card) == "board-only"
    with pytest.raises(d.DeliveryError, match="only openspec-v1"):
        d.require_deliverable_card(card)


def test_failed_floor_cannot_repeat_through_recovery(contract_run, monkeypatch):
    root, card, run, data = contract_run
    fingerprint = d.payload_fingerprint()
    failed = {"ok": False, "fingerprint": fingerprint}
    d.write_json(run / "verification.json", failed)
    child = d.RUNTIME_ROOT / "runs" / "child"
    child.mkdir()
    d.write_json(
        child / "run.json", {**data, "run_id": "child", "recovery_of": run.name}
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(child))
    monkeypatch.setattr(d, "verification_commands", lambda lane: ["true"])
    monkeypatch.setattr(
        d,
        "run_shell_verification",
        lambda *a, **k: pytest.fail("unchanged failed floor executed"),
    )
    with pytest.raises(d.DeliveryError, match="unchanged failed final floor"):
        d._run_full_floor(
            card,
            commands=["true"],
            root_name="verification",
            result_name="verification.json",
            schema="changerail.final-verification.v1",
            event_stage="verification",
            proof_lane="final",
        )
    assert not (child / "verification").exists()


def test_push_resume_rejects_absent_committed_receipt(contract_run):
    root, card, run, data = contract_run
    d.write_json(
        run / "publication.json",
        {"schema": "changerail.publication.v1", "state": "prepared"},
    )
    before = (run / "publication.json").read_bytes()
    with pytest.raises(d.DeliveryError, match="proven committed receipt"):
        d.resume_publication(run)
    assert (run / "publication.json").read_bytes() == before


def test_installer_retained_history_cannot_execute_current_marker(contract_run):
    root, card, run, data = contract_run
    lock = root / ".changerail/distribution-lock.json"
    d.write_json(
        lock,
        {
            "schema": "changerail.installation.v1",
            "retained_read_only_runs": {
                d.repo_relative(run / "run.json"): hashlib.sha256(
                    (run / "run.json").read_bytes()
                ).hexdigest()
            },
        },
    )
    before = (run / "run.json").read_bytes()
    with pytest.raises(d.DeliveryError, match="adopted run is read-only"):
        d.require_current_execution(run)
    assert (run / "run.json").read_bytes() == before


def test_exact_publication_and_push_recovery_to_local_bare_remote(
    contract_run, monkeypatch, tmp_path
):
    import shlex
    import sys

    root, card, run, data = contract_run
    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", str(remote)], check=True, capture_output=True
    )
    d.git("remote", "add", "origin", str(remote))
    d.git("push", "-u", "origin", "main")
    (d.BOARD_ROOT / "4.done").mkdir()
    card.write_text(
        "# Card\n\n## Lifecycle\nopenspec-v1\n\n## Status\n3.inprogress\n\n## Result\nImplemented value\n\n## Next\n- finalize\n\n## Log\n- observed value\n"
    )
    (root / "tracked.txt").write_text("after\n")
    command = shlex.join(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; assert Path('tracked.txt').read_text() == 'after\\n'; print('verified actual value')",
        ]
    )
    configured = d.profile()
    monkeypatch.setattr(
        d,
        "profile",
        lambda: {**configured, "verification": {"final_commands": [command]}},
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    fingerprint = d.payload_fingerprint()
    result = d._run_full_floor(
        card,
        commands=[command],
        root_name="verification",
        result_name="verification.json",
        schema="changerail.final-verification.v1",
        event_stage="verification",
        proof_lane="final",
    )
    assert result["ok"]
    verification = d._verified_command_set(
        run / "verification.json", run, card, fingerprint, [command], "final"
    )
    assert (
        verification is not None
        and b"verified actual value" in verification.receipts[0][1]
    )
    verdict = {"result": "go", "reviewed_at": d.utc_now(), "workspace": fingerprint}
    d.write_json(d.verdict_path(card.stem), verdict)
    manifest = {
        "paths": d.changed_paths(),
        "card": {"id": card.stem, "path": d.repo_relative(card)},
    }
    actual_git = d.git

    def uncertain_push(*args, **kwargs):
        if args and args[0] == "push":
            return subprocess.CompletedProcess(
                args, 1, stdout="", stderr="fixture transport unavailable"
            )
        return actual_git(*args, **kwargs)

    monkeypatch.setattr(d, "git", uncertain_push)
    assert (
        d._publish_continuation(
            card,
            run,
            d.manifest_path(card.stem),
            manifest,
            verdict,
            verification,
            "Deliver fixture",
        )
        == 1
    )
    receipt = d._check_json(run / "publication.json")
    assert receipt["state"] == "committed"
    committed = d.git("rev-parse", "HEAD").stdout.strip()
    assert not card.exists() and (d.BOARD_ROOT / "4.done" / card.name).is_file()
    assert not d.changed_paths()
    monkeypatch.setattr(d, "git", actual_git)
    assert d.resume_publication(run) == 0
    assert d.git("rev-parse", "HEAD").stdout.strip() == committed
    assert (
        d.git("ls-remote", "origin", "refs/heads/main").stdout.split()[0] == committed
    )
    assert d._check_json(run / "publication.json")["state"] == "pushed"
    assert d.resume_publication(run) == 0


@pytest.mark.parametrize(
    "body",
    [
        'schema="legacy"',
        "max_review_cycles=3",
        "max_review_cycles=true",
        "max_terminal_semantic_repair_reviews=0",
        "max_post_verification_repair_reviews=1",
        "[offline_finalization]\nenabled=false",
        '[models.ff]\nmodel="example"',
        '[budgets]\nenforce_limits="false"',
    ],
)
def test_profile_rejects_retired_or_ambiguous_execution_policy(contract_run, body):
    prefix = (
        "" if body.startswith("schema=") else 'schema="changerail.local-delivery.v1"\n'
    )
    d.PROFILE_PATH.write_text(prefix + body + "\n")
    with pytest.raises(d.DeliveryError):
        d.profile()


def test_profile_allows_an_explicit_technical_recovery_route(contract_run):
    d.PROFILE_PATH.write_text(
        'schema="changerail.local-delivery.v1"\n'
        "[models.technical_recovery]\n"
        'model="fallback-model"\n'
        'reasoning_effort="high"\n'
    )
    assert d.profile()["models"]["technical_recovery"]["model"] == "fallback-model"


def test_unchanged_failed_floor_cannot_allocate_recovery_review(
    contract_run, monkeypatch
):
    root, card, run, data = contract_run
    d.write_json(
        run / "verification.json",
        {
            "ok": False,
            "fingerprint": d.payload_fingerprint(),
            "commands": [{"command": "assert actual result", "exit_code": 1}],
        },
    )
    child = d.RUNTIME_ROOT / "runs/child"
    child.mkdir()
    d.write_json(
        child / "run.json", {**data, "run_id": "child", "recovery_of": run.name}
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(child))
    monkeypatch.setattr(d, "resolve_deliverable_card", lambda _: card)
    monkeypatch.setattr(
        d, "launch_codex", lambda **_: pytest.fail("review allocated before repair")
    )
    monkeypatch.setattr(
        d,
        "require_current_successful_preverification",
        lambda *_, **__: pytest.fail("unchanged failure reached evidence setup"),
    )
    d.write_json(
        child / "recovery-context.json",
        {"inherited_review_budget": {"semantic_cycles": 0}},
    )
    before = d.review_budget_usage(child)
    with pytest.raises(d.DeliveryError, match="unchanged failed final floor"):
        d.run_review(str(card))
    assert d.review_budget_usage(child) == before
    failures = d.failed_final_floors(child)
    assert failures[0]["receipt"] == d.repo_relative(run / "verification.json")
    assert failures[0]["commands"][0]["exit_code"] == 1
    (root / "tracked.txt").write_text("repaired\n")
    d.require_repaired_final_payload(child)
    assert d.failed_final_floors(child)[0]["matches_current_payload"] is False


def test_targeted_commands_execute_and_new_scope_invalidates_preverification(
    contract_run, monkeypatch
):
    import shlex
    import sys

    root, card, run, data = contract_run

    def command(text):
        return shlex.join([sys.executable, "-c", text])

    baseline = command("print('mandatory floor')")
    targeted = command(
        "from pathlib import Path; assert Path('tracked.txt').read_text() == 'after\\n'; print('actual changed value verified')"
    )
    additional = command(
        "from pathlib import Path; assert Path('extra.txt').read_text() == 'new\\n'"
    )
    configured = d.profile()
    monkeypatch.setattr(
        d,
        "profile",
        lambda: {
            **configured,
            "verification": {
                "pre_review_commands": [baseline],
                "final_commands": [baseline],
            },
            "targeted": [
                {"paths": ["tracked.txt"], "commands": [baseline, targeted]},
                {"paths": ["extra.txt"], "commands": [additional]},
            ],
        },
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    (root / "tracked.txt").write_text("after\n")
    assert d.verification_commands("pre_review") == [baseline, targeted]
    assert d.verification_commands("final") == [baseline]
    result = d._run_full_floor(
        card,
        commands=d.verification_commands("pre_review"),
        root_name="preverification",
        result_name="preverification.json",
        schema="changerail.pre-review-verification.v1",
        event_stage="preverification",
        proof_lane="pre_review",
    )
    assert result["ok"]
    assert (
        "actual changed value verified"
        in (root / result["commands"][1]["log"]).read_text()
    )
    d.require_current_successful_preverification(card, run, stage="test")
    (root / "extra.txt").write_text("new\n")
    assert d.verification_commands("pre_review") == [baseline, targeted, additional]
    assert d.verification_commands("final") == [baseline]
    with pytest.raises(d.DeliveryError, match="current successful preverification"):
        d.require_current_successful_preverification(card, run, stage="test")


def test_native_capacity_session_retains_terminal_stream_and_group_proof(
    contract_run, monkeypatch
):
    import os
    import sys
    from scripts.changerail import technical_recovery

    _root, _card, run, _metadata = contract_run
    monkeypatch.setattr(
        d,
        "codex_session_command",
        lambda **_kwargs: [
            sys.executable,
            "-c",
            "import sys; print('Selected model is at capacity', file=sys.stderr); sys.exit(1)",
        ],
    )
    monkeypatch.setattr(
        d, "execution_env", lambda extra=None: {**os.environ, **(extra or {})}
    )
    assert (
        d.launch_codex(
            role="implementation",
            prompt="fixture",
            model="fixture-model",
            reasoning="high",
            run_dir=run,
            timeout_minutes=1,
            session_env={"CHRL_CHANGE_NUMBER": "2"},
        )
        == 1
    )
    session = run / "sessions/implementation"
    metadata = d._check_json(session / "session.json")
    assert metadata["native_change_number"] == 2
    assert metadata["streams_complete"] is True
    assert metadata["process_group_quiescent"] is True
    assert (
        technical_recovery.classify_session(d, session)["failure_class"]
        == "model_capacity"
    )


def test_technical_apply_cli_propagates_successor_failure(contract_run, monkeypatch):
    from scripts.changerail import technical_recovery

    _root, _card, run, _metadata = contract_run
    monkeypatch.setattr(
        technical_recovery,
        "apply",
        lambda *_args: {"state": "dispatched", "exit_code": 2},
    )
    assert (
        d.main(["technical-recovery-apply", str(run), "--proposal", "proposal.json"])
        == 2
    )


@pytest.mark.parametrize(
    ("failure", "message"),
    [
        ("unknown", "allowlist"),
        ("semantic", "unknown failure event"),
        ("live", "proven terminal"),
        ("writer", "writer-started"),
    ],
)
def test_technical_recovery_rejects_non_capacity_failures_before_dispatch(
    project, monkeypatch, failure, message
):
    """Session inputs are synthetic; the rejection policy and retained state are real."""
    import json

    from scripts.changerail import native_workflow as flow
    from scripts.changerail import technical_recovery as recovery
    from tools.changerail.tests.test_technical_recovery import _files, _origin

    _root, _card, origin = _origin(project, monkeypatch)
    session = origin / "sessions/failed-group-2"
    if failure == "unknown":
        (session / "stderr.log").write_text("product test failed")
    elif failure == "semantic":
        event = {"type": "turn.failed", "error": {"message": "worker failed"}}
        (session / "stdout.jsonl").write_text(json.dumps(event) + "\n")
        (session / "events.jsonl").write_text(json.dumps({"event": event}) + "\n")
    elif failure == "live":
        metadata = d._check_json(session / "session.json")
        metadata["process_group_quiescent"] = False
        d.write_json(session / "session.json", metadata)
    else:
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
    before = _files(origin)
    before_budget = d.review_budget_usage(origin)
    monkeypatch.setattr(flow, "launch_groups", lambda *_args, **_kwargs: pytest.fail("writer"))

    with pytest.raises(d.DeliveryError, match=message):
        recovery.prepare(d, origin)

    assert _files(origin) == before
    assert d.review_budget_usage(origin) == before_budget == {"semantic_cycles": 0}
    assert not (d.RUNTIME_ROOT / "technical-recoveries" / origin.name).exists()
    assert [path for path in (d.RUNTIME_ROOT / "runs").iterdir() if path.is_dir()] == [
        origin
    ]
