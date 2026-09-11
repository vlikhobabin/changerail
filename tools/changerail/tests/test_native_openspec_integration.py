"""Real pinned CLI and Git boundaries; no model, live QA or external publication."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import openspec_context as native
from scripts.changerail import openspec_board as board

PROJECT = Path(__file__).resolve().parents[3]
FIXTURE_BOARD = "openspec/" + "board"


@pytest.fixture
def project(tmp_path, monkeypatch, request):
    root = tmp_path / "repo"
    root.mkdir()
    # Independent copies: writable hardlinks could corrupt the real installation.
    dependency = root / "tools/openspec"
    shutil.copytree(
        PROJECT / "tools/openspec",
        dependency,
        ignore=shutil.ignore_patterns("npm-logs"),
    )
    request.addfinalizer(lambda: shutil.rmtree(dependency / "node_modules"))
    for args in (
        ("init", "-b", "main"),
        ("config", "user.name", "Fixture"),
        ("config", "user.email", "fixture@example.invalid"),
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(".runtime/\ntools/openspec/node_modules/\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture baseline"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "openspec").mkdir()
    (root / "openspec/config.yaml").write_text("schema: spec-driven\n")
    canonical = root / "openspec/specs/example/spec.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text(
        "# Example\n\n## Purpose\nProvide deterministic fixture behavior for native delivery integration tests.\n\n## Requirements\n\n### Requirement: Preserve old behavior\nThe system SHALL preserve the old behavior.\n\n#### Scenario: Original use\n- **WHEN** old behavior is requested\n- **THEN** the original result is returned\n"
    )
    card = root / f"{FIXTURE_BOARD}/1.backlog/example.md"
    card.parent.mkdir(parents=True)
    (card.parent.parent / "2.todo").mkdir()
    for key, value in (
        ("REPO_ROOT", root),
        ("BOARD_ROOT", root / FIXTURE_BOARD),
        ("RUNTIME_ROOT", root / ".runtime/changerail"),
        ("EXCLUDED_PREFIXES", d.EXCLUDED_PREFIXES),
    ):
        monkeypatch.setattr(d, key, value)
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    monkeypatch.delenv("CHRL_RUN_DIR", raising=False)
    client = native.adapter(d)
    created = client._invoke("new", "change", "example-change")
    assert created.returncode == 0, created.stderr
    change = root / "openspec/changes/example-change"
    (change / "proposal.md").write_text(
        "## Why\nAdd fixture behavior.\n\n## What Changes\n- Add new behavior.\n\n## Capabilities\n### New Capabilities\n### Modified Capabilities\n- `example`: add behavior.\n\n## Impact\nFixture only.\n"
    )
    (change / "design.md").write_text(
        "## Context\nFixture behavior.\n\n## Goals / Non-Goals\nPreserve old behavior and add new behavior.\n\n## Decisions\nUse assertions.\n\n## Risks / Trade-offs\nNo live effects.\n"
    )
    (change / "tasks.md").write_text(
        "## 1. implement-behavior\n- [ ] 1.1 Add behavior.\n\n## 2. verify-behavior\n- [ ] 2.1 Check behavior.\n"
    )
    delta = change / "specs/example/spec.md"
    delta.parent.mkdir(parents=True)
    delta.write_text(
        "## ADDED Requirements\n\n### Requirement: Added behavior\nThe system SHALL return the new result.\n\n#### Scenario: New use\n- **WHEN** new behavior is requested\n- **THEN** the new result is returned\n"
    )
    evidence = {
        "schema": "changerail.card-evidence.v1",
        "conditions": [
            {
                "condition": "C1",
                "seam": "behavior",
                "precondition": "old result available",
                "action": "request new behavior",
                "expected": "new result and old compatibility",
                "method": {"kind": "inspection", "target": "source.py"},
                "stage": "implementation",
            }
        ],
        "risks": [
            {
                "kinds": [kind],
                "applies": False,
                "decision": "isolated fixture only",
                "conditions": [],
            }
            for kind in (
                "input_safety",
                "mutation",
                "restart",
                "concurrency",
                "publication",
                "external_effects",
            )
        ],
    }
    card.write_text(
        "# Example\n\n## Status\n1.backlog\n\n## Lifecycle\nopenspec-v1\n\n## Summary\nAdd fixture behavior.\n\n## Acceptance\n- [C1] New behavior preserves the original result.\n\n## Scope\n- source.py\n\n## Non-Goals\n- No live runtime.\n\n## Depends On\n- none\n\n## OpenSpec Changes\n1. `example-change`\n\n## Design\nAll risks are inapplicable to this isolated fixture.\n\n## Delivery Budget\n- primary_invariant: Compatibility\n- expected_wall_minutes: 30\n- production_owners: 1\n- runtime_contours: 0\n- estimated_product_files: 1\n- estimated_production_loc: 10\n\n## Verify\n```json\n"
        + json.dumps(evidence)
        + "\n```\n\n## Result\nnot started\n\n## Next\n- implement\n\n## Log\n- Fixture created\n"
    )
    return root, card, client


def test_public_admission_and_exact_stock_archive(project, monkeypatch):
    root, card, client = project
    follower = card.with_name("follower.md")
    follower.write_text(
        f"# Follower\n\n## Lifecycle\nboard-only\n\n## Depends On\n- `{FIXTURE_BOARD}/1.backlog/example.md`\n"
    )
    follower_before = follower.read_bytes()
    before = card.read_bytes()
    assert d.main(["native-accept", str(card), "--dry-run"]) == 0
    assert card.read_bytes() == before
    assert follower.read_bytes() == follower_before
    assert not (
        root / ".runtime/changerail/native-plans/example/native-plan.json"
    ).exists()
    assert d.main(["native-accept", str(card)]) == 0
    assert not card.exists()
    card = root / f"{FIXTURE_BOARD}/2.todo/example.md"
    assert d.repo_relative(card) in follower.read_text()
    d.require_live_board_references([])
    board.require_accepted(d, card)
    d.require_legacy_history()
    change = root / "openspec/changes/example-change"
    proposal = change / "proposal.md"
    original = proposal.read_bytes()
    proposal.write_bytes(original + b"\nChanged plan.\n")
    with pytest.raises(d.DeliveryError, match="plan changed"):
        board.require_accepted(d, card)
    proposal.write_bytes(original)
    run = root / ".runtime/changerail/runs/example"
    run.mkdir(parents=True)
    board.import_accepted(d, card, run)
    (run / "run.json").write_text(
        json.dumps(
            {
                "execution_contract": "changerail.native.v1",
                "mode": "delivery",
                "run_id": run.name,
                "card": d.repo_relative(card),
                "lifecycle_mode": "openspec-v1",
            }
        )
    )
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    (root / FIXTURE_BOARD / "3.inprogress").mkdir()
    card = d.start_delivery_card(card, {"paths": []})
    assert card.parent.name == "3.inprogress"
    d.write_json(
        run / "run.json",
        {**d._check_json(run / "run.json"), "card": d.repo_relative(card)},
    )
    # Accepted todo references are valid while that sole card is active;
    # publication owns their final rewrite to done.
    assert f"{FIXTURE_BOARD}/2.todo/example.md" in follower.read_text()
    d.require_live_board_references([])
    tasks = change / "tasks.md"
    tasks.write_text(tasks.read_text().replace("[ ]", "[x]"))
    native.require_plan(d, card, run / "native-plan.json")
    canonical = root / "openspec/specs/example/spec.md"
    canonical.write_text(
        canonical.read_text()
        + "\n"
        + (change / "specs/example/spec.md").read_text().split("\n", 1)[1]
    )
    report = run / "sync-report.md"
    report.write_text("Added Added behavior; preserved Preserve old behavior.\n")
    flow.record_sync(d, card, run, report)
    flow.require_sync(d, card, run)
    exact_specs = canonical.read_bytes()
    canonical.write_bytes(exact_specs + b"\nUnexpected edit.\n")
    with pytest.raises(d.DeliveryError, match="stale"):
        flow.require_sync(d, card, run)
    canonical.write_bytes(exact_specs)
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    receipt = native.archive(d, card, run)
    archived = root / receipt["destination"]
    assert archived.is_dir() and not change.exists()
    assert canonical.read_bytes() == exact_specs
    assert "Preserve old behavior" in canonical.read_text()
    assert "Added behavior" in canonical.read_text()
    flow.require_sync(d, card, run)
    native.require_complete(d, card)
    d.require_legacy_history()
    assert native.archive(d, card, run) == receipt
    shutil.copytree(archived, change)
    with pytest.raises(d.DeliveryError, match="also have an active"):
        native.require_complete(d, card)
    shutil.rmtree(change)
    archived_tasks = archived / "tasks.md"
    completed_tasks = archived_tasks.read_bytes()
    archived_tasks.write_bytes(completed_tasks.replace(b"[x]", b"[ ]"))
    with pytest.raises(d.DeliveryError, match="completion proof"):
        native.require_complete(d, card)
    archived_tasks.write_bytes(completed_tasks)
    # A crash after the stock move but before its receipt must reconcile exactly.
    (run / "native-archive.json").unlink()
    reconciled = native.archive(d, card, run)
    assert reconciled["destination"] == receipt["destination"]
    assert canonical.read_bytes() == exact_specs
    assert native.delivery_context(d, card)["state"] == "archived"
    assert client.workflow("sync")


@pytest.mark.parametrize(
    "archive_state", ["receipt", "intent", "changed-intent-target"]
)
def test_public_resume_initializes_archived_context(
    project, monkeypatch, archive_state
):
    """Real CLI/archive and public resume; model and measured admission are fixtures."""
    test_public_admission_and_exact_stock_archive(project, monkeypatch)
    root, _, _client = project
    card = root / f"{FIXTURE_BOARD}/3.inprogress/example.md"
    previous = root / ".runtime/changerail/runs/example"
    receipt = d._check_json(previous / "native-archive.json")
    plan = d._check_json(previous / "native-plan.json")
    d.write_json(
        previous / "run.json",
        {
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "run_id": previous.name,
            "card": d.repo_relative(card),
            "lifecycle_mode": "openspec-v1",
            "change_plan": [{"number": n, "slug": slug} for n, slug in plan["groups"]],
        },
    )
    d.write_json(
        previous / "manifest.json",
        {"run_id": previous.name, "paths": d.changed_paths()},
    )
    preliminary = previous / "preliminary.json"
    preliminary.write_text('{"verdict":"GO"}\n')
    d.write_json(
        previous / "native-review-continuation.json",
        {
            "preliminary": d.repo_relative(preliminary),
            "preliminary_sha256": hashlib.sha256(preliminary.read_bytes()).hexdigest(),
        },
    )
    if archive_state != "receipt":
        (previous / "native-archive.json").unlink()
    if archive_state == "changed-intent-target":
        tasks = root / receipt["destination"] / "tasks.md"
        tasks.write_text(tasks.read_text().replace("[x]", "[ ]"))
    source_bytes = {
        p.relative_to(previous): p.read_bytes()
        for p in previous.rglob("*")
        if p.is_file()
    }
    monkeypatch.delenv("CHRL_RUN_DIR")
    monkeypatch.setattr(d, "PROFILE_PATH", root / "profile.toml")
    monkeypatch.setattr(d, "profile", lambda: {})
    monkeypatch.setattr(
        d, "recovery_source", lambda *_a, **_kw: (True, "fixture", {"run_id": previous.name})
    )
    monkeypatch.setattr(
        d, "doctor", lambda *_a, **_k: {"ok": True, "recovery_of": previous.name}
    )
    monkeypatch.setattr(
        d,
        "_run_observed_contract",
        lambda *_a: {"schema": "changerail.observed-proof.v1"},
    )
    # This test owns archive receipt recovery; frozen source checks have separate real tests.
    monkeypatch.setattr(d, "require_frozen_execution", d.require_current_execution)

    def recovery_context(**kwargs):
        path = kwargs["run_dir"] / "recovery-context.json"
        d.write_json(path, {"inherited_change_events": []})
        return path

    monkeypatch.setattr(d, "build_recovery_context", recovery_context)
    monkeypatch.setattr(d, "build_metrics", lambda *_a, **_kw: {"usage": {}})
    monkeypatch.setattr(d, "retain_recovery_manifest", lambda **_k: None)
    reached = []

    def orchestrate(**kwargs):
        current = kwargs["run_dir"]
        assert native.change_root(d, card) == root / receipt["destination"]
        native.require_plan(d, card, current / "native-plan.json")
        flow.require_sync(d, card, current)
        assert d.declared_change_plan(current) == [
            tuple(group) for group in plan["groups"]
        ]
        reached.append(current)
        return 2  # Stop at the checked session boundary; no model or publication.

    monkeypatch.setattr(d, "orchestrate_delivery", orchestrate)
    assert d.main(["resume", str(previous)]) == 2
    assert bool(reached) is (archive_state != "changed-intent-target")
    assert "CHRL_RUN_DIR" not in os.environ
    assert source_bytes == {
        p.relative_to(previous): p.read_bytes()
        for p in previous.rglob("*")
        if p.is_file()
    }


def test_frozen_history_stays_exact_while_native_plan_can_be_added(
    project, monkeypatch
):
    root, card, _client = project
    legacy = root / "openspec/changes/legacy/tasks.md"
    legacy.parent.mkdir()
    legacy.write_text("- [ ] historical task\n")
    manifest = root / ".changerail/history.json"
    manifest.parent.mkdir()
    manifest.write_text(
        json.dumps(
            {
                "schema": "changerail.project-history.v1",
                "files": {
                    legacy.relative_to(root).as_posix(): hashlib.sha256(
                        legacy.read_bytes()
                    ).hexdigest()
                },
            }
        )
    )
    current = d.profile()
    monkeypatch.setattr(
        d,
        "profile",
        lambda: {**current, "history": {"manifest": ".changerail/history.json"}},
    )
    d.require_legacy_history()
    legacy.write_text("- [x] falsified completion\n")
    with pytest.raises(d.DeliveryError, match="frozen artifacts"):
        d.require_legacy_history()


def test_delivery_lock_rejects_a_competing_writer(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(d, "RUNTIME_ROOT", tmp_path / "runtime")
    with d.delivery_lock():
        with pytest.raises(d.DeliveryError, match="another delivery"):
            with d.delivery_lock():
                pytest.fail("competing writer entered")
    with d.delivery_lock():
        pass


def test_native_review_resumes_same_thread_and_counts_one_cycle(tmp_path, monkeypatch):
    """Exercise real review orchestration; only model and QA proof prerequisites are fixtures."""
    root = tmp_path / "repo"
    root.mkdir()
    for args in (
        ("init", "-b", "main"),
        ("config", "user.name", "Fixture"),
        ("config", "user.email", "fixture@example.invalid"),
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(".runtime/\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True
    )
    runtime = root / ".runtime/changerail"
    run = runtime / "runs/example"
    run.mkdir(parents=True)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/example.md"
    card.parent.mkdir(parents=True)
    card.write_text("# Example\n\n## Lifecycle\nopenspec-v1\n")
    (run / "run.json").write_text(
        json.dumps(
            {
                "schema": "changerail.delivery-run.v2",
                "run_id": run.name,
                "card": card.relative_to(root).as_posix(),
                "started_at": d.utc_now(),
                "execution_contract": "changerail.native.v1",
                "mode": "delivery",
                "lifecycle_mode": "openspec-v1",
            }
        )
    )
    for key, value in (
        ("REPO_ROOT", root),
        ("BOARD_ROOT", root / FIXTURE_BOARD),
        ("RUNTIME_ROOT", runtime),
        ("EXCLUDED_PREFIXES", d.EXCLUDED_PREFIXES),
    ):
        monkeypatch.setattr(d, key, value)
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    monkeypatch.setattr(
        d, "require_current_successful_preverification", lambda *a, **kw: None
    )
    monkeypatch.setattr(flow, "require_sync", lambda *a: None)
    monkeypatch.setattr(native, "delivery_context", lambda *a: {"state": "fixture"})
    monkeypatch.setattr(d, "_manifest_for_run", lambda *a: run / "manifest.json")
    monkeypatch.setattr(
        d, "validate_verdict", lambda _card: d._check_json(d.verdict_path(card.stem))
    )

    def context(**kwargs):
        path = run / "reviews" / f"cycle-{kwargs['cycle']:02d}-context.json"
        d.write_json(path, {"cycle": kwargs["cycle"]})
        return path

    monkeypatch.setattr(d, "build_review_context", context)
    calls = []

    def model(**kwargs):
        calls.append(kwargs)
        session = run / "sessions" / f"review-{len(calls):02d}"
        session.mkdir(parents=True)
        d.write_json(
            session / "session.json",
            {
                "role": "review",
                "started_at": d.utc_now(),
                "duration_seconds": 1,
                "exit_code": 0,
            },
        )
        (session / "events.jsonl").write_text(
            json.dumps(
                {
                    "observed_at": d.utc_now(),
                    "event": {
                        "type": "thread.started",
                        "thread_id": "independent-review-thread",
                    },
                }
            )
            + "\n"
        )
        kwargs["on_session_started"](session)
        d.write_json(
            kwargs["expected_artifact"],
            {"result": "go", "workspace": d.payload_fingerprint()},
        )
        return 0

    monkeypatch.setattr(d, "launch_codex", model)
    d.write_json(
        run / "manifest.json",
        {"paths": d.changed_paths(), "fingerprint": d.payload_fingerprint()},
    )
    assert d.run_review(str(card)) == 0
    assert d._completed_review_verdicts(run / "reviews") == []
    assert len(calls) == 1 and calls[0]["resume_thread_id"] is None
    # Unchanged preliminary result can continue to archive without another model.
    assert d.run_review(str(card)) == 0
    assert len(calls) == 1
    (run / "native-archive.json").write_text("{}")
    card.write_text(card.read_text() + "\n## Result\nrefreshed after fixture archive\n")
    d.write_json(
        run / "manifest.json",
        {"paths": d.changed_paths(), "fingerprint": d.payload_fingerprint()},
    )
    assert d.run_review(str(card)) == 0
    assert calls[1]["resume_thread_id"] == "independent-review-thread"
    assert calls[1]["session_env"]["CHRL_REVIEW_CYCLE"] == "1"
    assert calls[1]["session_env"]["CHRL_NATIVE_REVIEW_PHASE"] == "final"
    assert len(d._completed_review_verdicts(run / "reviews")) == 1
    state = d._check_json(run / "native-review-continuation.json")
    assert state["complete"] and state["final"] == d.payload_fingerprint()
    assert d.run_review(str(card)) == 0
    assert len(calls) == 2


def test_technical_recovery_reconcile_is_single_successor_and_rejects_drift(
    project, monkeypatch
):
    """Only the group worker is mocked; prepare/apply/reconcile use real locks and state."""
    from scripts.changerail import technical_recovery as recovery
    from tools.changerail.tests.test_technical_recovery import _files, _origin

    root, _card, origin = _origin(project, monkeypatch)
    launches: list[dict[str, object]] = []

    def launch(_delivery, **kwargs) -> None:
        launches.append(kwargs)

    def execute(**kwargs) -> int:
        kwargs["before_orchestrate"]()
        return 0

    monkeypatch.setattr(flow, "launch_groups", launch)
    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    original_profile = d.profile()
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
    monkeypatch.setattr(d, "profile", lambda: original_profile)

    payload_drift = root / "payload-drift.py"
    payload_drift.write_text("changed\n")
    with pytest.raises(d.DeliveryError, match="payload differs|predecessor was changed|drifted"):
        recovery.apply(d, origin, Path(prepared["proposal"]))
    payload_drift.unlink()

    first = recovery.apply(d, origin, Path(prepared["proposal"]))
    successor = Path(first["successor"])
    after_first = _files(origin.parent)
    review_usage = d.review_budget_usage(successor)
    repeated = recovery.apply(d, origin, Path(prepared["proposal"]))
    reconciled = recovery.reconcile(d, origin)
    assert Path(repeated["successor"]) == successor
    assert Path(reconciled["successor"]) == successor
    assert _files(origin.parent) == after_first
    assert len(launches) == 1
    assert d.review_budget_usage(successor) == review_usage == {"semantic_cycles": 0}

    before_locked = _files(origin.parent)
    with d.delivery_lock():
        with pytest.raises(d.DeliveryError, match="another delivery runner"):
            recovery.reconcile(d, origin)
    assert _files(origin.parent) == before_locked
    assert len([path for path in origin.parent.iterdir() if path.is_dir()]) == 2
    assert len(launches) == 1
