"""Self-host successor reaches real archive, verification and a local Git remote.

The model launcher and in-process engine import address are controlled test seams.
All plan, proof, accounting, archive, verification and publication gates are real.
Subprocess engine routing is covered separately by the engine entrypoint tests.
"""

import json
import os
import shutil
import sys
import subprocess
import time
from pathlib import Path

import pytest
import distribution as dist
from scripts.changerail import local_delivery as d
from scripts.changerail import openspec_board as board
from scripts.changerail import native_workflow as flow
from scripts.changerail import self_host_recovery as recovery
from scripts.changerail import engine_snapshot, engine_runtime
from tools.changerail.tests.test_native_openspec_integration import project as project
from tools.changerail.tests.test_plan_restore_e2e import (
    snapshot,
    observed_contract,
    inspect_behavior,
    retained_manifest,
)

SOURCE = Path(__file__).resolve().parents[3]


def wait_for_quiescence(roots, timeout=30):
    # Publication may return while a descendant with inherited CHRL_RUN_DIR
    # is still exiting. Keep the real guard and fail if it does not quiesce.
    deadline = time.monotonic() + timeout
    while True:
        try:
            recovery._live(roots)
            return
        except d.DeliveryError as exc:
            if str(exc) != "self-host recovery found a live process owner":
                raise
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.05)


def test_quiescence_wait_preserves_live_owner_guard(tmp_path):
    owner = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.buffer.read()"],
        stdin=subprocess.PIPE,
        env={**os.environ, "CHRL_RUN_DIR": str(tmp_path / ".runtime/changerail/runs/owned")},
    )
    try:
        with pytest.raises(d.DeliveryError, match="live process owner"):
            wait_for_quiescence([tmp_path], timeout=0)
        owner.stdin.close()
        wait_for_quiescence([tmp_path])
        owner.wait(timeout=5)
        assert owner.returncode == 0
    finally:
        if not owner.stdin.closed:
            owner.stdin.close()
        if owner.poll() is None:
            owner.terminate()
        owner.wait(timeout=5)


@pytest.mark.parametrize("resume_after_stop,empty_payload", [(False, False), (True, False), (True, True)])
def test_self_host_successor_reaches_real_local_publication(
    project, tmp_path, monkeypatch, capsys, resume_after_stop, empty_payload
):
    root, card, _client = project
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    (root / ".gitignore").write_text(
        ".runtime/\n__pycache__/\n.pytest_cache/\ntools/openspec/node_modules/\n"
    )
    for column in ("4.done", "5.canceled"):
        location = root / "openspec/board" / column
        location.mkdir(parents=True)
        (location / ".gitkeep").write_text("")
    archive = tmp_path / "runtime.tar.gz"
    dist.build(SOURCE, archive)
    dist.install(root, archive)
    profile = (SOURCE / "tools/changerail/templates/profile.toml").read_text()
    command = (
        f"{sys.executable} -m pytest -p no:cacheprovider -v tests/test_behavior.py"
    )
    profile = profile.replace(
        'final_commands = ["python3 -m pytest -v", "./bin/openspec validate --specs --strict --no-interactive"]',
        "final_commands = "
        + json.dumps(
            [command, "./bin/openspec validate --specs --strict --no-interactive"]
        ),
    )
    dist.write_atomic(root / ".changerail/profile.toml", profile.encode())
    dist.write_atomic(root / "bin/codex", b"#!/bin/sh\nexit 99\n", 0o755)
    monkeypatch.setattr(d, "PROFILE_PATH", root / ".changerail/profile.toml")
    # Public --project initializes these paths at import; this in-process CLI
    # fixture performs the same binding without replacing any validation gate.
    for name, value in list(vars(d).items()):
        if (
            name.endswith("SCHEMA_PATH")
            and isinstance(value, Path)
            and value.is_relative_to(SOURCE)
        ):
            monkeypatch.setattr(d, name, root / value.relative_to(SOURCE))
    if empty_payload:
        # Real sealed inventories and binding; only the in-process import address
        # is supplied by the fixture. Nested CLI commands load snapshot code.
        source = tmp_path / "engine-source"
        for name, (data, mode) in dist.source_payload(SOURCE)[1].items():
            dist.write_atomic(source / name, data, mode)
        def source_git(*args):
            subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
        source_git("init", "-q")
        source_git("config", "user.name", "Fixture")
        source_git("config", "user.email", "fixture@example.invalid")
        source_git("add", ".")
        source_git("commit", "-qm", "old engine")
        old_engine, new_engine = tmp_path / "old-engine", tmp_path / "new-engine"
        engine_snapshot.create_snapshot(source, old_engine)
        source_git("commit", "--allow-empty", "-qm", "new engine provenance")
        engine_snapshot.create_snapshot(source, new_engine)
        old_binding = engine_snapshot.bind_engine(root, old_engine)
        monkeypatch.setattr(d, "_SOURCE_REPO_ROOT", old_engine)
        monkeypatch.setattr(engine_runtime, "__file__", str(old_engine / "scripts/changerail/engine_runtime.py"))
        with (root / ".gitignore").open("a") as stream:
            stream.write(".changerail/engine-binding.json\n.changerail/.engine-binding.lock\n")
    (root / "source.py").write_text("def value():\n    return 1\n")
    dist.write_atomic(
        root / "tests/test_behavior.py",
        b"from source import value\n\ndef test_value():\n    assert value() == 2\n",
    )
    assert d.main(["native-accept", str(card)]) == 0
    card = card.parent.parent / "2.todo" / card.name
    d.git("add", ".")
    d.git("commit", "-m", "accepted installed fixture")
    baseline = d.git("rev-parse", "HEAD").stdout.strip()
    remote = tmp_path / "remote.git"
    d.git("init", "--bare", str(remote))
    d.git("remote", "add", "origin", str(remote))
    d.git("push", "-u", "origin", "main")
    plan = d._check_json(d.RUNTIME_ROOT / "native-plans/example/native-plan.json")
    origin = d.RUNTIME_ROOT / "runs/original"
    origin.mkdir(parents=True)
    board.import_accepted(d, card, origin)
    target = card.parent.parent / "3.inprogress" / card.name
    target.parent.mkdir()
    card.rename(target)
    card = target
    card.write_text(d.replace_section(card.read_text(), "Status", ["3.inprogress"]))
    metadata = {
        "schema": "changerail.delivery-run.v2",
        "run_id": origin.name,
        "card": d.repo_relative(card),
        "execution_contract": "changerail.native.v1",
        "mode": "delivery",
        "lifecycle_mode": "openspec-v1",
        "started_at": d.utc_now(),
        "baseline_head": baseline,
        "change_plan": [{"number": n, "slug": slug} for n, slug in plan["groups"]],
        "process_identity": d.execution_identity(),
        "observed_proof_contract": observed_contract(origin, card),
    }
    d.write_json(origin / "run.json", metadata)
    tasks = root / "openspec/changes/example-change/tasks.md"
    (root / "source.py").write_text("def value():\n    return 2\n")
    with monkeypatch.context() as env:
        env.setenv("CHRL_RUN_DIR", str(origin))
        env.setenv("CHRL_SESSION_ROLE", "implementation")
        env.setenv("CHRL_DELIVERY_STAGE", "change")
        for n, _slug in plan["groups"]:
            env.setenv("CHRL_CHANGE_NUMBER", str(n))
            d.emit_event(f"change-{n}", "starting")
            tasks.write_text(tasks.read_text().replace(f"[ ] {n}.1", f"[x] {n}.1"))
            assert (
                d.run_evidence(
                    f"group-{n}",
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-p",
                        "no:cacheprovider",
                        "-v",
                        "tests/test_behavior.py",
                    ],
                )
                == 0
            )
            inspect_behavior(root, card, origin)
            d.emit_event(f"change-{n}", "complete")
    metadata.update(
        finished_at=d.utc_now(),
        exit_code=2,
        terminal_reason="implementation session exited without a handoff",
    )
    d.write_json(origin / "run.json", metadata)
    retained_manifest(origin, card, baseline)
    old_payload = tmp_path / "retained-payload"
    old_payload.mkdir()
    for relative in d._check_json(origin / "manifest.json")["paths"]:
        source = root / relative
        if source.is_file():
            target = old_payload / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    # Model behavior is unchanged, but its corrective payload is newly reviewed.
    (root / "source.py").write_text("def value():\n    return 2  # corrected payload\n")
    if not empty_payload:
        monkeypatch.setattr(
            recovery, "_engine", lambda _d: {"engine": "controlled import address"}
        )
    if empty_payload:
        engine_snapshot.rebind_engine(root, new_engine, old_binding["engine_identity"])
        monkeypatch.setattr(d, "_SOURCE_REPO_ROOT", new_engine)
        monkeypatch.setattr(engine_runtime, "__file__", str(new_engine / "scripts/changerail/engine_runtime.py"))
        d.git("add", ".")
        d.git("commit", "-m", "committed finalization payload")
        baseline = d.git("rev-parse", "HEAD").stdout.strip()
        retained_manifest(origin, card, baseline)
        assert d._check_json(origin / "manifest.json")["paths"] == []
    history = snapshot(origin)
    prepared = recovery.prepare(d, origin, payload_snapshot=old_payload)
    # A relocated checkout has the retained native plan in its imported run,
    # but not necessarily the separate original admission directory.
    shutil.rmtree(d.RUNTIME_ROOT / "native-plans/example")
    capsys.readouterr()
    allocations = []
    stops = 0

    def controlled_session(**kwargs):
        nonlocal stops
        role, run = kwargs["role"], kwargs["run_dir"]
        stage = kwargs.get("session_env", {}).get("CHRL_DELIVERY_STAGE")
        assert stage != "change", "completed groups must never be replayed"
        if resume_after_stop and stops < (2 if empty_payload else 1) and stage == "finalize":
            stops += 1
            return 2
        allocations.append((role, stage))
        session = run / "sessions" / f"controlled-{len(allocations)}"
        session.mkdir(parents=True)
        d.write_json(
            session / "session.json",
            {
                "role": role,
                "started_at": d.utc_now(),
                "finished_at": d.utc_now(),
                "completed": True,
                "returncode": 0,
                "stop_reason": "completed",
            },
        )
        (session / "events.jsonl").write_text(
            json.dumps(
                {
                    "observed_at": d.utc_now(),
                    "event": {
                        "type": "thread.started",
                        "thread_id": "controlled-independent-review"
                        if role == "review"
                        else f"controlled-implementation-{len(allocations)}",
                    },
                }
            )
            + "\n"
        )
        if kwargs.get("on_session_started"):
            kwargs["on_session_started"](session)
        with monkeypatch.context() as env:
            env.setenv("CHRL_SESSION_ROLE", role)
            env.setenv("CHRL_RUN_DIR", str(run))
            for key, value in kwargs.get("session_env", {}).items():
                env.setenv(key, value)
            if role == "implementation":
                with pytest.raises(d.DeliveryError, match="handoff"):
                    d.require_current_implementation_handoff(card, run)
                if stage == "finalize":
                    canonical = root / "openspec/specs/example/spec.md"
                    delta = (
                        root / "openspec/changes/example-change/specs/example/spec.md"
                    )
                    canonical.write_text(
                        canonical.read_text()
                        + "\n"
                        + delta.read_text().split("\n", 1)[1]
                    )
                    report_path = run / "sync-report.md"
                    report_path.write_text(
                        "Added Added behavior; preserved Preserve old behavior.\n"
                    )
                    flow.record_sync(d, card, run, report_path)
                card.write_text(
                    d.replace_section(
                        card.read_text(),
                        "Result",
                        [
                            "Implemented and checked deterministic fixture behavior; current evidence retained."
                        ],
                    )
                )
                card.write_text(
                    d.replace_section(
                        card.read_text(),
                        "Log",
                        [
                            "- Completed both task groups; refreshed evidence for the current payload."
                        ],
                    )
                )
                assert (
                    d.run_evidence(
                        f"fresh-{len(allocations)}",
                        [
                            sys.executable,
                            "-m",
                            "pytest",
                            "-p",
                            "no:cacheprovider",
                            "-v",
                            "tests/test_behavior.py",
                        ],
                    )
                    == 0
                )
                inspect_behavior(root, card, run)
                assert d.implementation_handoff(str(card)) == 0
            else:
                proofs = d.require_current_stage_proofs(card, run, ["implementation"])
                template = d.verdict_template(str(card))["template"]
                for decision in template["decisions"]:
                    decision["assessment"] = (
                        "The inspected implementation and real pytest receipt prove fixture behavior; only the model launcher is simulated."
                    )
                    for ref in decision["condition_refs"]:
                        ref["observation_ids"] = [
                            p["observation_id"]
                            for p in proofs
                            if p["condition"] == ref["condition"]
                        ]
                    decision["observation_ids"] = [
                        p["observation_id"]
                        for p in proofs
                        if p["condition"] in decision["conditions"]
                    ]
                d.write_json(d.verdict_path(card.stem), template)
                assert d.validate_verdict(str(card))["result"] == "go"
        return 0

    monkeypatch.setattr(d, "launch_codex", controlled_session)
    result = d.main(
        ["self-host-recovery-apply", str(origin), "--proposal", prepared["proposal"]]
    )
    first_successor = next(
        p for p in (d.RUNTIME_ROOT / "runs").iterdir() if p != origin
    )
    resume_parent = first_successor
    if resume_after_stop:
        for attempt in range(2 if empty_payload else 1):
            assert result == 2
            assert d._check_json(resume_parent / "run.json")["finished_at"]
            before_resume = snapshot(resume_parent)
            result = d.main(["resume", str(resume_parent)])
            assert snapshot(resume_parent) == before_resume
            if empty_payload and attempt == 0:
                resume_parent = next(
                    p for p in (d.RUNTIME_ROOT / "runs").iterdir()
                    if d._check_json(p / "run.json").get("recovery_of") == resume_parent.name
                )
    captured = capsys.readouterr()
    assert result == 0, captured.out + captured.err
    assert allocations == [
        ("implementation", "finalize"),
        ("review", None),
        ("implementation", "archive-refresh"),
        ("review", None),
    ]
    assert snapshot(origin) == history
    assert not d.changed_paths()
    assert (root / "openspec/board/4.done/example.md").is_file()
    assert (
        d.git("--git-dir", str(remote), "rev-parse", "refs/heads/main").stdout
        == d.git("rev-parse", "HEAD").stdout
    )
    successor = next(
        p
        for p in (d.RUNTIME_ROOT / "runs").iterdir()
        if (p / "publication.json").is_file()
    )
    assert d.review_budget_usage(successor) == {"semantic_cycles": 1}
    assert d._check_json(successor / "publication.json")["state"] == "pushed"
    assert d._check_json(successor / "verification.json")["ok"] is True
    assert d._check_json(successor / "run.json")["recovery_of"] == (
        resume_parent.name if resume_after_stop else origin.name
    )
    count = len(allocations)
    wait_for_quiescence([root])
    assert (
        recovery.apply(d, origin, Path(prepared["proposal"]))["state"] == "dispatched"
    )
    assert len(allocations) == count
