"""A consumed restoration must always name a complete recoverable successor."""

from pathlib import Path

import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import plan_restoration as restore
from tools.changerail.tests.test_native_openspec_integration import project as project
from tools.changerail.tests.test_plan_restoration import stopped as stopped


def test_consumption_cannot_leave_partial_successor(stopped):
    _root, _card, previous, _ = stopped
    report = restore.prepare(d, previous, reason="restore")
    restore.apply(d, previous, Path(report["proposal"]), report["proposal_sha256"])
    child = previous.with_name("partial")
    child.mkdir()
    d.write_json(
        child / "run.json",
        {
            **d._check_json(previous / "run.json"),
            "run_id": child.name,
            "recovery_of": previous.name,
        },
    )
    with pytest.raises(d.DeliveryError, match="complete.*successor"):
        restore.consume(d, previous, child)
    assert not Path(report["proposal"]).with_name("consumed.json").exists()


@pytest.fixture
def restored(stopped, monkeypatch):
    root, card, previous, _ = stopped
    plan = d._check_json(previous / "native-plan.json")
    metadata = d._check_json(previous / "run.json")
    metadata["change_plan"] = [
        {"number": n, "slug": slug} for n, slug in plan["groups"]
    ]
    d.write_json(previous / "run.json", metadata)
    report = restore.prepare(d, previous, reason="restore")
    restore.apply(d, previous, Path(report["proposal"]), report["proposal_sha256"])
    monkeypatch.setattr(d, "PROFILE_PATH", root / ".changerail/profile.toml")
    monkeypatch.setattr(d, "profile", lambda: {})
    return (
        root,
        card,
        previous,
        Path(report["proposal"]).parent,
        [tuple(group) for group in plan["groups"]],
    )


@pytest.mark.parametrize(
    "boundary",
    [
        "observed-proof-selection.json",
        "run.json",
        "recovery-context.json",
        "native-plan.json",
        "successor-intent.json",
        "rename",
        "consumed.json",
    ],
)
def test_creation_interruptions_reconcile_without_orphan(
    restored, monkeypatch, boundary
):
    _root, card, previous, directory, changes = restored
    original_history = restore._inventory(d, previous)
    hit = False
    original_write = restore._write
    original_json = d.write_json
    original_rename = restore.os.rename

    def after_write(path, value):
        nonlocal hit
        original_write(path, value)
        if path.name == boundary and not hit:
            hit = True
            raise RuntimeError("creation interruption")

    def after_json(path, value):
        nonlocal hit
        original_json(path, value)
        if path.name == boundary and not hit:
            hit = True
            raise RuntimeError("creation interruption")

    def after_rename(source, target):
        nonlocal hit
        original_rename(source, target)
        if boundary == "rename" and not hit:
            hit = True
            raise RuntimeError("creation interruption")

    monkeypatch.setattr(restore, "_write", after_write)
    monkeypatch.setattr(d, "write_json", after_json)
    monkeypatch.setattr(restore.os, "rename", after_rename)
    with pytest.raises(RuntimeError, match="creation interruption"):
        restore.create_successor(d, previous, card, changes, "continue")
    assert hit
    if (directory / "consumed.json").exists():
        child = previous.with_name(
            d._check_json(directory / "consumed.json")["successor"]
        )
        assert (child / "manifest.json").is_file()
        assert (child / "native-plan.json").is_file()
        assert (child / "recovery-context.json").is_file()
    result = restore.create_successor(d, previous, card, changes, "continue")
    child = result["run_dir"]
    assert sorted(p.name for p in previous.parent.iterdir()) == sorted(
        [previous.name, child.name]
    )
    assert restore._inventory(d, previous) == original_history
    assert (
        restore.create_successor(d, previous, card, changes, "continue")["run_dir"]
        == child
    )
    assert d.recovery_source(card, d.changed_paths(), required_run_id=child.name)[0]
    assert d.review_budget_usage(child) == {"semantic_cycles": 0}


def test_started_successor_remains_recoverable_and_cannot_fork(restored):
    _root, card, previous, _directory, changes = restored
    result = restore.create_successor(d, previous, card, changes, "continue")
    child = result["run_dir"]
    (child / "phase-events.jsonl").write_text(
        '{"phase":"preflight","stage":"complete"}\n'
    )
    with pytest.raises(d.DeliveryError, match="already started.*resume"):
        restore.create_successor(d, previous, card, changes, "continue")
    assert d.recovery_source(card, d.changed_paths(), required_run_id=child.name)[0]


def test_published_creation_before_manifest_index_interrupt_is_reconciled(
    restored, monkeypatch
):
    _root, card, previous, _directory, _changes = restored
    monkeypatch.setattr(
        d, "doctor", lambda *a, **kw: {"ok": True, "recovery_of": previous.name}
    )
    # Historical observed-contract selection belongs to the original fixture;
    # current successor observed selection is checked by creation itself.
    actual_contract = d._run_observed_contract
    monkeypatch.setattr(
        d,
        "_run_observed_contract",
        lambda run: None if run == previous else actual_contract(run),
    )
    monkeypatch.setenv("CHRL_RECOVERY_OBJECTIVE", "continue")
    original = d.write_json
    hit = False

    def interrupt_index(path, value):
        nonlocal hit
        original(path, value)
        if path.parent.name == "delivery-manifests" and not hit:
            hit = True
            raise RuntimeError("index interruption")

    monkeypatch.setattr(d, "write_json", interrupt_index)
    with pytest.raises(RuntimeError, match="index interruption"):
        d._run_delivery(str(card), recovery=True, required_run_id=previous.name)
    children = [p for p in previous.parent.iterdir() if p != previous]
    assert len(children) == 1
    reached = []
    monkeypatch.setattr(
        d, "orchestrate_delivery", lambda **kw: reached.append(kw["run_dir"]) or 2
    )
    assert d._run_delivery(str(card), recovery=True, required_run_id=previous.name) == 2
    assert reached == children


def test_changed_staging_intent_cannot_be_published(restored, monkeypatch):
    _root, card, previous, directory, changes = restored
    original = restore._write

    def interrupt_intent(path, value):
        original(path, value)
        if path.name == "successor-intent.json":
            raise RuntimeError("before publish")

    monkeypatch.setattr(restore, "_write", interrupt_intent)
    with pytest.raises(RuntimeError, match="before publish"):
        restore.create_successor(d, previous, card, changes, "continue")
    intent = d._check_json(directory / "successor-intent.json")
    staged = directory / intent["staged"]
    (staged / "native-plan.json").write_text("{}")
    with pytest.raises(d.DeliveryError, match="staging changed"):
        restore.create_successor(d, previous, card, changes, "continue")
    assert list(previous.parent.iterdir()) == [previous]
    assert not (directory / "consumed.json").exists()


@pytest.mark.parametrize("published", [False, True])
def test_creation_record_publication_never_exposes_partial_json(
    tmp_path, monkeypatch, published
):
    path = tmp_path / "successor-intent.json"
    original = restore.os.link

    def interrupted_link(source, target, **kwargs):
        if published:
            original(source, target, **kwargs)
        raise RuntimeError("record publication interruption")

    monkeypatch.setattr(restore.os, "link", interrupted_link)
    with pytest.raises(RuntimeError, match="record publication interruption"):
        restore._write(
            path, {"schema": restore.SCHEMA, "inventory": {"run.json": "complete"}}
        )
    assert path.exists() is published
    if published:
        import json

        assert json.loads(path.read_bytes())["inventory"] == {"run.json": "complete"}
    assert list(tmp_path.iterdir()) == ([path] if published else [])
