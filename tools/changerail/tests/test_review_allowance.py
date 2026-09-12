"""Operator authorizations use real native admission, history and project locks.

Only host /proc owner discovery is replaced: these tests own synthetic tmp
projects, and inject the unknown-live failure independently. No model is run.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.changerail import engine_snapshot
from scripts.changerail import local_delivery as d
from scripts.changerail import openspec_board as board
from scripts.changerail import native_workflow as flow
from scripts.changerail import review_allowance as policy
from tools.changerail.tests.test_native_openspec_integration import project as project
from tools.changerail.tests.test_release_executor_integration import full_release as full_release


def _history(run: Path) -> dict[str, bytes]:
    return {p.relative_to(run).as_posix(): p.read_bytes()
            for p in sorted(run.rglob("*")) if p.is_file()}


def _records() -> list[Path]:
    return sorted((d.RUNTIME_ROOT / "review-authorizations").glob("*/*.json"))


@pytest.fixture
def exhausted(project, monkeypatch):
    root, card, _client = project
    monkeypatch.setattr(engine_snapshot, "_no_live_delivery", lambda _root: None)
    profile = root / ".changerail/profile.toml"
    profile.parent.mkdir(exist_ok=True)
    profile.write_bytes(d.PROFILE_PATH.read_bytes())
    monkeypatch.setattr(d, "PROFILE_PATH", profile)
    board.accept_card(d, card)
    card = card.parent.parent / "2.todo" / card.name
    d.git("add", ".")
    d.git("commit", "-m", "accepted fixture plan")
    run = d.RUNTIME_ROOT / "runs/exhausted"
    run.mkdir(parents=True)
    board.import_accepted(d, card, run)
    active = card.parent.parent / "3.inprogress" / card.name
    active.parent.mkdir()
    card.rename(active)
    card = active
    card.write_text(card.read_text().replace("## Status\n2.todo", "## Status\n3.inprogress"))
    (root / "source.py").write_text("result = 'retained implementation'\n")
    selection = run / "observed-proof-selection.json"
    stages = ["implementation", "review", "final"]
    d.write_json(selection, {
        "schema": "changerail.observed-proof-selection.v1",
        "root": d.repo_relative(run),
        "owner": {"run_id": run.name, "card": d.repo_relative(card)},
        "required_stages": stages,
    })
    metadata = {
        "schema": "changerail.delivery-run.v2", "run_id": run.name,
        "card": d.repo_relative(card), "execution_contract": "changerail.native.v1",
        "mode": "delivery", "lifecycle_mode": "openspec-v1",
        "change_plan": [{"number": number, "slug": slug}
                        for number, slug in d._check_json(run / "native-plan.json")["groups"]],
        "process_identity": d.execution_identity(), "started_at": "2026-09-12T00:00:00Z",
        "finished_at": "2026-09-12T00:05:00Z", "exit_code": 3,
        "terminal_reason": "shared two-review budget exhausted",
        "observed_proof_contract": {
            "schema": "changerail.observed-proof.v1", "required_stages": stages,
            "selection": {"path": d.repo_relative(selection),
                          "sha256": hashlib.sha256(selection.read_bytes()).hexdigest()},
        },
    }
    d.write_json(run / "run.json", metadata)
    (run / "phase-events.jsonl").write_text("".join(
        json.dumps({"phase": f"change-{group['number']}", "stage": stage,
                    "at": "2026-09-12T00:01:00Z"}) + "\n"
        for group in metadata["change_plan"] for stage in ("starting", "complete")
    ))
    paths = d.changed_paths()
    manifest = {
        "schema": "changerail.delivery-manifest.v1", "run_id": run.name,
        "card": {"id": card.stem, "path": d.repo_relative(card)},
        "baseline_head": d.git("rev-parse", "HEAD").stdout.strip(),
        "paths": paths, "fingerprint": d.payload_fingerprint(paths),
        "path_fingerprints": d.path_fingerprints(paths),
    }
    d.write_json(run / "manifest.json", manifest)
    for cycle in (1, 2):
        stem = run / "reviews" / f"cycle-{cycle:02d}"
        d.write_json(stem.with_suffix(".json"), {
            "result": "no-go", "workspace": manifest["fingerprint"],
            "findings": [{"repair_scope": ["source.py"], "observed": "fixture finding"}],
        })
        d.write_json(stem.with_name(stem.name + "-manifest.json"), manifest)
        d.write_json(stem.with_name(stem.name + "-context.json"), {"cycle": cycle})
        d.write_json(run / "sessions" / f"review-{cycle:02d}" / "session.json", {
            "role": "review", "finished_at": "2026-09-12T00:04:00Z",
            "completed": True, "exit_code": 0,
        })
    return root, card, run


def _authorize(run: Path) -> dict:
    preview = policy.review_allow(d, run, reason="Repair the retained finding")
    return policy.review_allow(d, run, reason="Repair the retained finding",
                               authorize=preview["proposal_sha256"])


def test_real_release_launcher_accepts_operator_lease_and_refuses_workers(full_release, exhausted):
    from scripts.changerail import engine_runtime, executor_binding, release_executor
    from tools.changerail.tests.test_release_executor import copy_runtime_dependencies

    _unused, engine, old = full_release
    root, _card, run = exhausted
    # Complete the isolated published fixture with the real pinned CLI/deps.
    shutil.rmtree(engine / "tools/openspec/node_modules")
    shutil.copytree(root / "tools/openspec/node_modules", engine / "tools/openspec/node_modules")
    copy_runtime_dependencies(Path(old["dependencies"]["python"]["site_packages"]))
    receipt = release_executor.inspect_release(engine, tag="fixture-v1", node=Path(shutil.which("node")))
    release_executor.receipt_path(engine).write_bytes(release_executor.encoded(receipt))
    launcher = root / "bin/codex"
    launcher.parent.mkdir(exist_ok=True)
    launcher.write_text("#!/bin/sh\nexit 99\n")
    launcher.chmod(0o755)
    (root / ".git/info/exclude").write_text(".changerail/\nbin/codex\n")
    manifest = d._check_json(run / "manifest.json")
    paths = d.changed_paths()
    manifest.update(paths=paths, fingerprint=d.payload_fingerprint(paths),
                    path_fingerprints=d.path_fingerprints(paths))
    # Binding is fixture setup, before frozen history is retained.
    prepared = executor_binding.prepare(root, engine)
    executor_binding.apply(Path(prepared["proposal"]))
    value = {**release_executor.binding_document(root, engine),
             "engine_identity": release_executor.digest(release_executor.encoded(receipt)),
             "release_receipt": receipt}
    metadata = d._check_json(run / "run.json")
    metadata["process_identity"] = engine_runtime.release_identity(d, value)
    d.write_json(run / "run.json", metadata)
    d.write_json(run / "manifest.json", manifest)
    for path in (run / "reviews").glob("cycle-*-manifest.json"):
        d.write_json(path, manifest)
        verdict_path = path.with_name(path.name.replace("-manifest", ""))
        verdict = d._check_json(verdict_path)
        verdict["workspace"] = manifest["fingerprint"]
        d.write_json(verdict_path, verdict)
    before = _history(run)
    env = {key: value for key, value in os.environ.items() if not key.startswith("CHRL_")}
    command = [str(root / ".changerail/chrl"), "review-allow", str(run),
               "--reason", "Repair the retained finding through the release operator CLI"]

    def invoke(*args, worker=None):
        return subprocess.run([*command, *args], cwd=root, env={**env, **(worker or {})},
                              capture_output=True, text=True)

    preview = invoke()
    assert preview.returncode == 0, preview.stderr
    proposal = json.loads(preview.stdout)
    assert proposal["state"] == "preview" and not _records()
    digest = proposal["proposal_sha256"]
    for worker in ({"CHRL_SESSION_ROLE": "implementation"}, {"CHRL_RUN_DIR": str(run)},
                   {"CHRL_NATIVE_CONTEXT": "fixture-worker"}, {"CHRL_RECOVERY_CONTEXT": "fixture-worker"}):
        denied = invoke("--authorize", digest, worker=worker)
        assert denied.returncode == 2 and "outside worker context" in denied.stderr
        assert not _records() and _history(run) == before
    granted = invoke("--authorize", digest)
    assert granted.returncode == 0, granted.stderr
    result = json.loads(granted.stdout)
    assert result["state"] == "authorized" and result["authorization"]["review_number"] == 3
    assert len(_records()) == 1 and _history(run) == before
    repeated = invoke("--authorize", digest)
    assert repeated.returncode == 0, repeated.stderr
    assert json.loads(repeated.stdout)["reused"] is True and len(_records()) == 1
    assert _history(run) == before


def test_preview_authorize_repeat_preserve_exact_history(exhausted):
    _root, _card, run = exhausted
    before = _history(run)
    default = policy.allowance(d, run)
    assert (default["autonomous_allowance"], default["spent_reviews"], default["remaining"]) == (2, 2, 0)
    first = policy.review_allow(d, run, reason="Repair the retained finding")
    second = policy.review_allow(d, run, reason="Repair the retained finding")
    assert first == second and first["state"] == "preview"
    assert not _records() and _history(run) == before
    granted = _authorize(run)
    record = d.REPO_ROOT / granted["authorization"]["path"]
    recorded_bytes = record.read_bytes()
    assert record.parent == d.RUNTIME_ROOT / "review-authorizations" / run.name
    assert granted["authorization"]["review_number"] == 3
    assert policy.allowance(d, run)["remaining"] == 1
    repeated = _authorize(run)
    assert repeated["reused"] is True
    assert repeated["authorization"] == granted["authorization"]
    assert _records() == [record] and record.read_bytes() == recorded_bytes
    with pytest.raises(d.DeliveryError, match="not exhausted"):
        policy.review_allow(d, run, reason="Another reason cannot accumulate slots")
    assert policy.allowance(d, run)["operator_granted_slots"] == 1
    assert _history(run) == before


def test_early_request_does_not_allocate(exhausted):
    _root, _card, run = exhausted
    for path in (run / "reviews").glob("cycle-02*"):
        path.unlink()
    before = _history(run)
    with pytest.raises(d.DeliveryError, match="not exhausted"):
        policy.review_allow(d, run, reason="too early")
    assert not _records() and _history(run) == before


@pytest.mark.parametrize("mutation", ["payload", "index", "head", "scope"])
def test_stale_start_refuses_authorize_before_record(exhausted, mutation):
    root, card, run = exhausted
    preview = policy.review_allow(d, run, reason="specific repair")
    before = _history(run)
    if mutation == "payload":
        (root / "source.py").write_text("unretained payload\n")
    elif mutation == "index":
        d.git("add", "source.py")
    elif mutation == "head":
        d.git("commit", "--allow-empty", "-m", "different head")
    else:
        card.write_text(card.read_text().replace("- source.py", "- different.py"))
    with pytest.raises(d.DeliveryError, match="starting payload|empty index|plan changed"):
        policy.review_allow(d, run, reason="specific repair", authorize=preview["proposal_sha256"])
    assert not _records() and _history(run) == before


def test_stale_payload_before_claim_keeps_authorization_and_history(exhausted):
    root, _card, run = exhausted
    granted = _authorize(run)
    before = _history(run)
    record = root / granted["authorization"]["path"]
    saved = record.read_bytes()
    (root / "source.py").write_text("edit before claim\n")
    with d.delivery_lock(), pytest.raises(d.DeliveryError, match="starting payload"):
        policy.recovery_authorization(d, run)
    assert _history(run) == before and record.read_bytes() == saved
    assert list((d.RUNTIME_ROOT / "runs").iterdir()) == [run]


@pytest.mark.parametrize("key", ["CHRL_SESSION_ROLE", "CHRL_RUN_DIR", "CHRL_NATIVE_CONTEXT",
                                  "CHRL_RECOVERY_CONTEXT", "CHRL_REPAIR_CONTEXT"])
def test_worker_api_and_cli_are_denied(exhausted, monkeypatch, capsys, key):
    _root, _card, run = exhausted
    before = _history(run)
    monkeypatch.setenv(key, "synthetic-worker")
    with pytest.raises(d.DeliveryError, match="separate operator"):
        policy.review_allow(d, run, reason="worker cannot grant")
    assert d.main(["review-allow", str(run), "--reason", "worker cannot grant"]) == 2
    assert "separate operator" in capsys.readouterr().err
    assert not _records() and _history(run) == before


def test_real_lock_and_unknown_live_owner_refuse_writes(exhausted, monkeypatch):
    _root, _card, run = exhausted
    before = _history(run)
    preview = policy.review_allow(d, run, reason="competing operator")
    with d.delivery_lock(), pytest.raises(d.DeliveryError, match="another delivery runner"):
        policy.review_allow(d, run, reason="competing operator", authorize=preview["proposal_sha256"])
    def unknown(_root):
        raise engine_snapshot.EngineSnapshotError("unknown live delivery owner")
    monkeypatch.setattr(engine_snapshot, "_no_live_delivery", unknown)
    with pytest.raises(d.DeliveryError, match="unknown live delivery owner"):
        policy.review_allow(d, run, reason="owner unresolved")
    assert not _records() and _history(run) == before


@pytest.mark.parametrize("mutation, message", [
    ("operator", "operator stop"), ("unfinished", "terminal failed"),
    ("verification", "unresolved verification"), ("pending-review", "pending native review"),
    ("review-session", "unresolved review session"), ("allocation", "unresolved review allocation"),
    ("publication", "publication boundary"), ("frozen", "process changed"),
    ("history", "read-only"), ("restoration", "conflicting recovery intent"),
    ("child", "current terminal leaf"),
])
def test_existing_eligibility_gates_remain_closed(exhausted, mutation, message):
    _root, _card, run = exhausted
    metadata = d._check_json(run / "run.json")
    if mutation in {"operator", "unfinished", "frozen", "history"}:
        if mutation == "operator":
            metadata["exit_code"] = 130
        elif mutation == "unfinished":
            metadata.pop("finished_at")
        elif mutation == "frozen":
            metadata["process_identity"] = {"unsupported": "frozen engine"}
        else:
            metadata["execution_contract"] = "historical"
        d.write_json(run / "run.json", metadata)
    elif mutation == "verification":
        d.write_json(run / "verification-attempts/pending.json", {"state": "started"})
    elif mutation == "pending-review":
        d.write_json(run / "native-review-continuation.json", {"complete": False})
    elif mutation == "review-session":
        d.write_json(run / "sessions/review-02/session.json", {
            "role": "review", "finished_at": "2026-09-12T00:04:00Z", "completed": False})
    elif mutation == "allocation":
        d.write_json(run / "reviews/cycle-03-context.json", {"cycle": 3})
    elif mutation == "publication":
        d.write_json(run / "publication.json", {})
    elif mutation == "restoration":
        (d.RUNTIME_ROOT / "plan-restorations" / run.name).mkdir(parents=True)
    else:
        d.write_json(run.parent / "child/run.json", {**metadata, "run_id": "child", "recovery_of": run.name})
    before = _history(run)
    with pytest.raises(d.DeliveryError, match=message):
        policy.review_allow(d, run, reason="cannot weaken stage gate")
    assert not _records() and _history(run) == before


@pytest.mark.parametrize("mutation", ["unknown", "bool", "float", "negative", "duplicate",
    "foreign", "ordinal", "replay", "nested", "digest", "symlink", "history"])
def test_malformed_or_foreign_authority_never_becomes_a_slot(exhausted, mutation):
    root, _card, run = exhausted
    granted = _authorize(run)
    path = root / granted["authorization"]["path"]
    record = d._check_json(path)
    if mutation == "unknown":
        record["unlimited"] = True
    elif mutation in {"bool", "float", "negative"}:
        record["spent_before"] = {"bool": True, "float": 2.0, "negative": -1}[mutation]
    elif mutation == "foreign":
        record["project"]["root"] = str(root.parent / "foreign")
    elif mutation == "ordinal":
        record["review_number"] = 4
    elif mutation == "replay":
        record["previous_authorization"] = "0" * 64
    elif mutation == "nested":
        record["starting"]["unexpected"] = True
    elif mutation == "digest":
        record["proposal_sha256"] = "0" * 64
    if mutation == "duplicate":
        path.write_text(path.read_text().replace('"schema":', '"schema":"duplicate", "schema":', 1))
    elif mutation == "symlink":
        external = root.parent / "record.json"
        external.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(external)
    elif mutation == "history":
        (run / "reviews/cycle-01-context.json").write_text('{"cycle":1,"forged":true}')
    else:
        d.write_json(path, record)
    before = _history(run)
    record_before = path.read_bytes()
    with pytest.raises(d.DeliveryError, match="authorization|duplicate|history|symlink|counter"):
        policy.allowance(d, run)
    assert _history(run) == before and path.read_bytes() == record_before
    assert len(_records()) == 1


def test_wrong_digest_and_invalid_reasons_have_no_side_effect(exhausted):
    _root, _card, run = exhausted
    before = _history(run)
    for reason in ("", " ", "x" * 1001):
        with pytest.raises(d.DeliveryError, match="reason"):
            policy.review_allow(d, run, reason=reason)
    for digest in ("bad", "0" * 64):
        with pytest.raises(d.DeliveryError, match="SHA256|stale"):
            policy.review_allow(d, run, reason="specific repair", authorize=digest)
    assert not _records() and _history(run) == before


def test_independent_same_card_owner_cannot_receive_grant(exhausted):
    _root, _card, run = exhausted
    owner = d._check_json(run / "run.json")
    independent = run.parent / "independent"
    d.write_json(independent / "run.json", {**owner, "run_id": independent.name})
    before = {path: _history(path) for path in (run, independent)}
    with pytest.raises(d.DeliveryError, match="another run owns this card"):
        policy.review_allow(d, run, reason="no competing ownership")
    assert not _records()
    assert {path: _history(path) for path in before} == before


def test_missing_or_changed_checkpoint_plan_cannot_receive_grant(exhausted):
    _root, _card, run = exhausted
    original = d._check_json(run / "run.json")
    for plan in (None, [{"number": 1, "slug": "foreign-group"}]):
        metadata = dict(original)
        if plan is None:
            metadata.pop("change_plan")
        else:
            metadata["change_plan"] = plan
        d.write_json(run / "run.json", metadata)
        before = _history(run)
        with pytest.raises(d.DeliveryError, match="checkpoint plan differs"):
            policy.review_allow(d, run, reason="must retain accepted checkpoint plan")
        assert not _records() and _history(run) == before
    d.write_json(run / "run.json", original)


@pytest.mark.parametrize("damage", ["missing-record", "context-digest"])
def test_claim_requires_its_exact_immutable_authorization(exhausted, damage):
    root, _card, run = exhausted
    granted = _authorize(run)
    with d.delivery_lock():
        child_name, reference = policy.recovery_authorization(d, run)
    child = run.parent / child_name
    d.write_json(child / "run.json", {
        **d._check_json(run / "run.json"), "run_id": child_name, "recovery_of": run.name,
    })
    context = {
        "run_id": child_name, "recovery_of": run.name,
        "inherited_review_budget": {"semantic_cycles": 2},
        "current_fingerprint": granted["proposal"]["starting"]["fingerprint"],
        "review_authorization": reference,
    }
    d.write_json(child / "recovery-context.json", context)
    assert policy.allowance(d, child)["remaining"] == 1
    if damage == "missing-record":
        (root / reference["path"]).unlink()
    else:
        context["review_authorization"] = {**reference, "sha256": "0" * 64}
        d.write_json(child / "recovery-context.json", context)
    before = {path: _history(path) for path in (run, child)}
    with pytest.raises(d.DeliveryError, match="claim"):
        policy.allowance(d, child)
    assert {path: _history(path) for path in before} == before


def test_archived_failed_final_grant_preserves_real_plan_and_failed_floor(exhausted, monkeypatch):
    """Use stock archive and real archived plan lookup; no archive/plan gate mocks."""
    root, card, run = exhausted
    change = root / "openspec/changes/example-change"
    tasks = change / "tasks.md"
    tasks.write_text(tasks.read_text().replace("[ ]", "[x]"))
    canonical = root / "openspec/specs/example/spec.md"
    canonical.write_text(canonical.read_text() + "\n" +
                         (change / "specs/example/spec.md").read_text().split("\n", 1)[1])
    report = run / "sync-report.md"
    report.write_text("Added Added behavior; preserved Preserve old behavior.\n")
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    flow.record_sync(d, card, run, report)
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    archive = d.native.archive(d, card, run)
    monkeypatch.delenv("CHRL_RUN_DIR")
    assert not change.exists() and (root / archive["destination"]).is_dir()
    paths = d.changed_paths()
    manifest = {
        **d._check_json(run / "manifest.json"), "paths": paths,
        "fingerprint": d.payload_fingerprint(paths),
        "path_fingerprints": d.path_fingerprints(paths),
    }
    d.write_json(run / "manifest.json", manifest)
    d.write_json(run / "reviews/cycle-02-manifest.json", manifest)
    d.write_json(run / "reviews/cycle-02.json", {
        "result": "go", "workspace": manifest["fingerprint"], "findings": [],
    })
    d.write_json(run / "verification.json", {
        "ok": False, "fingerprint": manifest["fingerprint"],
        "commands": [{"command": "fixture final assertion", "exit_code": 1}],
    })
    before = _history(run)
    granted = _authorize(run)
    assert granted["authorization"]["review_number"] == 3
    assert "CHRL_RUN_DIR" not in os.environ
    with d.delivery_lock():
        assert policy.recovery_authorization(d, run)[1] == granted["authorization"]
    assert "CHRL_RUN_DIR" not in os.environ
    with pytest.raises(d.DeliveryError, match="unchanged failed final floor"):
        d.require_repaired_final_payload(run)
    assert _history(run) == before
