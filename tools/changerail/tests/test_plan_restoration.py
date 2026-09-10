"""Exact Git-backed Next restoration, append-only history and interruption safety."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import openspec_board as board
from scripts.changerail import plan_restoration as restore
from tools.changerail.tests.test_native_openspec_integration import project as project


@pytest.fixture
def stopped(project, monkeypatch):
    root, card, _client = project
    monkeypatch.setattr(d, "execution_identity", lambda: {"fixture": "frozen"})
    board.accept_card(d, card)
    card = card.parent.parent / "2.todo" / card.name
    d.git("add", ".")
    d.git("commit", "-m", "accepted plan")
    accepted = card.read_bytes()
    target = card.parent.parent / "3.inprogress" / card.name
    target.parent.mkdir()
    card.rename(target)
    card = target
    card.write_bytes(
        accepted.replace(b"2.todo", b"3.inprogress").replace(
            b"- implement", b"- changed Next"
        )
    )
    run = d.RUNTIME_ROOT / "runs/stopped"
    run.mkdir(parents=True)
    plan = d._check_json(d.RUNTIME_ROOT / "native-plans/example/native-plan.json")
    d.write_json(run / "native-plan.json", plan)
    d.write_json(
        run / "run.json",
        {
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "run_id": run.name,
            "card": d.repo_relative(card),
            "finished_at": d.utc_now(),
            "exit_code": 2,
            "terminal_reason": "accepted native OpenSpec plan changed; explicit replan required",
            "process_identity": d.execution_identity(),
        },
    )
    paths = d.changed_paths()
    d.write_json(
        run / "manifest.json",
        {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run.name,
            "card": {"id": d.card_id(card), "path": d.repo_relative(card)},
            "baseline_head": d.git("rev-parse", "HEAD").stdout.strip(),
            "paths": paths,
            "fingerprint": d.payload_fingerprint(paths),
            "path_fingerprints": d.path_fingerprints(paths),
            "path_states": {path: d._path_state(path) for path in paths},
        },
    )
    return root, card, run, accepted


def history(run):
    return {
        p.relative_to(run).as_posix(): p.read_bytes()
        for p in run.rglob("*")
        if p.is_file()
    }


def test_exact_restore_preserves_history_and_live_lookup(stopped):
    root, card, run, _ = stopped
    before = history(run)
    original = card.read_bytes()
    report = restore.prepare(d, run, reason="restore frozen Next")
    assert card.read_bytes() == original
    receipt = restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    assert card.read_bytes() == original.replace(b"- changed Next", b"- implement")
    assert history(run) == before
    manifest = restore.effective_manifest(d, run)
    assert manifest["fingerprint"] == d.payload_fingerprint()
    assert (
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
        == receipt
    )
    # Successor may move/archive the card. Proven transition lookup stays historical.
    card.unlink()
    assert restore.accepted_plan(d, run)["change_id"] == "example-change"
    assert restore.effective_identity(d, run, d._check_json(run / "run.json")) == {
        "fixture": "frozen"
    }


@pytest.mark.parametrize(
    "mutation",
    ["product", "scope", "next-duplicate", "runtime", "stage", "operator", "exhausted"],
)
def test_prepare_rejects_unsafe_states(stopped, monkeypatch, mutation):
    root, card, run, _ = stopped
    if mutation == "product":
        (root / "source.py").write_text("unretained change")
    elif mutation == "scope":
        card.write_bytes(card.read_bytes().replace(b"- source.py", b"- other.py"))
        manifest = d._check_json(run / "manifest.json")
        manifest.update(
            fingerprint=d.payload_fingerprint(),
            path_fingerprints=d.path_fingerprints(d.changed_paths()),
        )
        d.write_json(run / "manifest.json", manifest)
    elif mutation == "next-duplicate":
        card.write_bytes(card.read_bytes() + b"\n## Next\n- duplicate\n")
    elif mutation == "runtime":
        monkeypatch.setattr(d, "execution_identity", lambda: {"fixture": "changed"})
    elif mutation == "stage":
        (run / "native-archive-intent.json").write_text("{}")
    elif mutation == "operator":
        metadata = d._check_json(run / "run.json")
        metadata["terminal_reason"] = "operator_interrupt"
        d.write_json(run / "run.json", metadata)
    else:
        reviews = run / "reviews"
        reviews.mkdir()
        for number in (1, 2):
            (reviews / f"cycle-{number:02}.json").write_text(
                json.dumps({"result": "no-go"})
            )
    original = card.read_bytes()
    before = history(run)
    with pytest.raises(d.DeliveryError):
        restore.prepare(d, run, reason="restore")
    assert history(run) == before
    assert card.read_bytes() == original
    assert not (d.RUNTIME_ROOT / "plan-restorations").exists()


def test_dry_run_and_authority_and_concurrent_drift(stopped):
    root, card, run, _ = stopped
    restore.prepare(d, run, reason="inspect", dry_run=True)
    assert not (d.RUNTIME_ROOT / "plan-restorations").exists()
    report = restore.prepare(d, run, reason="restore")
    with pytest.raises(d.DeliveryError, match="authority"):
        restore.apply(d, run, Path(report["proposal"]), "0" * 64)
    card.write_bytes(card.read_bytes() + b"unretained mutation\n")
    with pytest.raises(d.DeliveryError):
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    assert not Path(report["proposal"]).with_name("apply-intent.json").exists()


@pytest.mark.parametrize("after_replace", [False, True])
def test_durable_intent_reconciles_exact_states(stopped, monkeypatch, after_replace):
    root, card, run, _ = stopped
    report = restore.prepare(d, run, reason="restore")
    original = restore._atomic_card

    def interrupt(*args):
        if after_replace:
            original(*args)
        raise RuntimeError("interruption")

    monkeypatch.setattr(restore, "_atomic_card", interrupt)
    with pytest.raises(RuntimeError, match="interruption"):
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    with pytest.raises(d.DeliveryError, match="pending"):
        restore.ensure_no_pending(d)
    monkeypatch.setattr(restore, "_atomic_card", original)
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    restore.ensure_no_pending(d)
    assert b"- implement" in card.read_bytes()


def test_git_source_commit_artifact_history_and_receipt_tampering(stopped):
    root, card, run, _ = stopped
    with pytest.raises(d.DeliveryError, match="accepted commit"):
        restore.prepare(d, run, reason="restore", accepted_commit="0" * 40)
    proposal = root / "openspec/changes/example-change/proposal.md"
    original = proposal.read_bytes()
    proposal.write_bytes(original + b"\nScope changed.\n")
    manifest = d._check_json(run / "manifest.json")
    paths = d.changed_paths()
    d.write_json(
        run / "manifest.json",
        {
            **manifest,
            "paths": paths,
            "fingerprint": d.payload_fingerprint(paths),
            "path_fingerprints": d.path_fingerprints(paths),
        },
    )
    with pytest.raises(d.DeliveryError, match="complete accepted plan"):
        restore.prepare(d, run, reason="restore")
    proposal.write_bytes(original)
    d.write_json(run / "manifest.json", manifest)
    report = restore.prepare(d, run, reason="restore")
    (run / "extra-history.json").write_text("{}")
    with pytest.raises(d.DeliveryError, match="history changed"):
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    (run / "extra-history.json").unlink()
    prepared = Path(report["proposal"])
    value = d._check_json(prepared)
    value["reason"] = "altered after authorization"
    d.write_json(prepared, value)
    with pytest.raises(d.DeliveryError, match="authority"):
        restore.apply(d, run, prepared, report["proposal_sha256"])


def test_single_successor_and_third_state_reconciliation(stopped, monkeypatch):
    _root, card, run, _ = stopped
    report = restore.prepare(d, run, reason="restore")
    before = card.read_bytes()
    original = restore._atomic_card
    monkeypatch.setattr(
        restore,
        "_atomic_card",
        lambda *args: (_ for _ in ()).throw(RuntimeError("interrupt")),
    )
    with pytest.raises(RuntimeError):
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    card.write_bytes(before + b"\nthird state\n")
    with pytest.raises(d.DeliveryError, match="neither exact"):
        restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    card.write_bytes(before)
    monkeypatch.setattr(restore, "_atomic_card", original)
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    monkeypatch.setattr(d, "profile", lambda: {})
    monkeypatch.setattr(d, "PROFILE_PATH", _root / ".changerail/profile.toml")
    plan = d._check_json(run / "native-plan.json")
    successor = restore.create_successor(
        d, run, card, [tuple(group) for group in plan["groups"]], "continue"
    )["run_dir"]
    first = restore.consume(d, run, successor)
    assert restore.consume(d, run, successor) == first
    fork = run.with_name("fork")
    fork.mkdir()
    d.write_json(
        fork / "run.json",
        {**d._check_json(successor / "run.json"), "run_id": fork.name},
    )
    with pytest.raises(d.DeliveryError, match="already consumed"):
        restore.consume(d, run, fork)


def test_newline_mode_and_retained_review_budget(stopped):
    root, card, run, _ = stopped
    card.write_bytes(card.read_bytes().replace(b"\n", b"\r\n"))
    card.chmod(0o750)
    reviews = run / "reviews"
    reviews.mkdir()
    (reviews / "cycle-01.json").write_text('{"result":"no-go"}')
    manifest = d._check_json(run / "manifest.json")
    paths = d.changed_paths()
    d.write_json(
        run / "manifest.json",
        {
            **manifest,
            "fingerprint": d.payload_fingerprint(paths),
            "path_fingerprints": d.path_fingerprints(paths),
        },
    )
    before = card.read_bytes()
    report = restore.prepare(d, run, reason="restore")
    proposal = d._check_json(Path(report["proposal"]))
    assert proposal["review_budget"] == {"semantic_cycles": 1}
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    a, b = restore._next(before)
    accepted = bytes.fromhex(proposal["accepted_hex"])
    c, e = restore._next(accepted)
    assert card.read_bytes() == before[:a] + accepted[c:e] + before[b:]
    assert card.stat().st_mode & 0o777 == 0o750
    assert d.review_budget_usage(run) == {"semantic_cycles": 1}


def test_installed_projection_authorizes_added_removed_and_lock_paths(
    stopped, tmp_path
):
    """Prediction uses archive bytes and Git baseline before any installer writes."""
    import distribution as dist

    root, card, run, _ = stopped
    retired = root / "scripts/changerail/retired.py"
    retired.parent.mkdir(parents=True)
    retired.write_bytes(b"old runtime\n")
    d.git("add", "scripts/changerail/retired.py")
    d.git("commit", "-m", "previous runtime baseline")
    paths = d.changed_paths()
    manifest = {
        **d._check_json(run / "manifest.json"),
        "baseline_head": d.git("rev-parse", "HEAD").stdout.strip(),
        "paths": paths,
        "fingerprint": d.payload_fingerprint(paths),
        "path_fingerprints": d.path_fingerprints(paths),
    }
    archive = tmp_path / "target.tar.gz"
    dist.build(Path(__file__).resolve().parents[3], archive)
    target, payload = dist.inspect_archive(archive)
    bridge = {
        "archive": str(archive),
        "archive_sha256": dist.digest(archive.read_bytes()),
        "before_lock": {
            "files": {
                "scripts/changerail/retired.py": dist.entry(
                    (retired.read_bytes(), 0o644)
                )
            }
        },
        "after_lock": {"files": target["files"]},
    }
    before_card = card.read_bytes()
    after = before_card.replace(b"- changed Next", b"- implement")
    projected = restore._projected_manifest(
        d, manifest, card, after, runtime_transition=bridge
    )
    assert retired.exists() and card.read_bytes() == before_card
    for name, (data, mode) in payload.items():
        dist.write_atomic(root / name, data, mode)
    retired.unlink()
    dist.write_atomic(root / dist.LOCK, dist.encoded(bridge["after_lock"]))
    card.write_bytes(after)
    assert projected["paths"] == d.changed_paths()
    assert projected["path_fingerprints"] == d.path_fingerprints(d.changed_paths())
    assert projected["fingerprint"] == d.payload_fingerprint()
    assert "scripts/changerail/retired.py" in projected["paths"]
    assert dist.LOCK in projected["paths"]
    assert "scripts/changerail/plan_restoration.py" in projected["paths"]


def test_installed_applied_manifest_cannot_be_rewritten(stopped, monkeypatch):
    """Runtime identity proof cannot authorize a different product manifest."""
    from scripts.changerail import installed_restoration as bridge

    _root, _card, run, _ = stopped
    report = restore.prepare(d, run, reason="restore")
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    path = Path(report["proposal"])
    value = d._check_json(path)
    # Isolate the product-manifest trust gate from the separately tested bridge.
    # Authority is valid for a bridge-bearing proposal; only applied data drifts.
    value["runtime_transition"] = {"schema": bridge.SCHEMA}
    d.write_json(path, value)
    digest = restore._digest(path.read_bytes())
    intent = d._check_json(path.with_name("apply-intent.json"))
    intent.update(proposal_sha256=digest, authorized=digest)
    d.write_json(path.with_name("apply-intent.json"), intent)
    receipt = d._check_json(path.with_name("applied.json"))
    receipt["proposal_sha256"] = digest
    d.write_json(path.with_name("applied.json"), receipt)
    monkeypatch.setattr(bridge, "effective_identity", lambda *_: receipt["identity"])
    assert restore.effective_manifest(d, run) == value["projected_manifest"]
    receipt["effective_manifest"]["fingerprint"]["payload_fingerprint"] = (
        "sha256:" + "0" * 64
    )
    d.write_json(path.with_name("applied.json"), receipt)
    with pytest.raises(d.DeliveryError, match="authorized projection"):
        restore.effective_manifest(d, run)


def test_accepted_snapshot_recovers_unavailable_git_blob(stopped, monkeypatch):
    import subprocess

    _root, card, run, _ = stopped
    original = subprocess.run

    def missing_blob(argv, **kwargs):
        if argv[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(argv, 1, b"", b"missing blob")
        return original(argv, **kwargs)

    monkeypatch.setattr(restore.subprocess, "run", missing_blob)
    report = restore.prepare(d, run, reason="use retained accepted snapshot")
    value = d._check_json(Path(report["proposal"]))
    assert value["accepted_path"].endswith("accepted-card.md")
    restore.apply(d, run, Path(report["proposal"]), report["proposal_sha256"])
    assert b"- implement" in card.read_bytes()


def test_interrupted_new_admission_completes_snapshot_before_receipt(
    project, monkeypatch
):
    root, card, _client = project
    original = board._exclusive_json

    def interrupt(path, value):
        if path.name == "accepted-card.json":
            raise RuntimeError("snapshot interruption")
        original(path, value)

    monkeypatch.setattr(board, "_exclusive_json", interrupt)
    with pytest.raises(RuntimeError, match="snapshot interruption"):
        board.accept_card(d, card)
    receipt_root = d.RUNTIME_ROOT / "native-plans/example"
    assert not (receipt_root / "native-plan.json").exists()
    before = (receipt_root / "accepted-card.md").read_bytes()
    monkeypatch.setattr(board, "_exclusive_json", original)
    board.accept_card(d, card)
    assert (receipt_root / "accepted-card.md").read_bytes() == before
    assert (receipt_root / "accepted-card.json").is_file()
    assert (receipt_root / "native-plan.json").is_file()


def test_snapshot_tampering_and_old_admission_are_not_backfilled(stopped, monkeypatch):
    import subprocess

    _root, card, run, _ = stopped
    root = d.RUNTIME_ROOT / "native-plans/example"
    original = subprocess.run

    def missing_blob(argv, **kwargs):
        if argv[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(argv, 1, b"", b"missing blob")
        return original(argv, **kwargs)

    monkeypatch.setattr(restore.subprocess, "run", missing_blob)
    snapshot = root / "accepted-card.md"
    snapshot.write_bytes(snapshot.read_bytes().replace(b"- implement", b"- forged"))
    with pytest.raises(d.DeliveryError, match="snapshot source or full contract"):
        restore.prepare(d, run, reason="restore")
    for name in ("accepted-card.md", "accepted-card.json", "accepted-card-intent.json"):
        (root / name).unlink()
    with pytest.raises(d.DeliveryError, match="no authenticated admission snapshot"):
        restore.prepare(d, run, reason="restore")
    board._retain_acceptance(d, card, root, d._check_json(run / "native-plan.json"))
    assert sorted(path.name for path in root.iterdir()) == ["native-plan.json"]
