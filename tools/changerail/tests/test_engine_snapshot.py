"""Immutable engine inventories and explicit project bindings."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import fcntl

import pytest

from scripts.changerail import engine_snapshot as engine


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "scripts/changerail").mkdir(parents=True)
    (root / "scripts/changerail/__init__.py").write_text("VALUE = 1\n")
    (root / "distribution.json").write_text(
        json.dumps(
            {
                "schema": "changerail.distribution-config.v1",
                "files": ["distribution.json"],
                "trees": {"scripts/changerail": "**/*.py"},
            }
        )
    )
    for args in (
        ["init", "-q"],
        ["add", "."],
        [
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "source",
        ],
    ):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    return root


def test_snapshot_complete_readonly_inventory_and_binding(source, tmp_path):
    snapshot = tmp_path / "engine"
    manifest = engine.create_snapshot(source, snapshot)
    assert engine.verify_snapshot(snapshot) == manifest
    assert manifest["source_commit"]
    assert manifest["files"]["scripts/changerail/__init__.py"]["mode"] == 0o444
    assert not (snapshot / ".git").exists()
    assert snapshot.stat().st_mode & 0o222 == 0
    assert engine.create_snapshot(source, snapshot) == manifest
    project = tmp_path / "project"
    project.mkdir()
    binding = engine.bind_engine(project, snapshot)
    assert engine.verify_binding(project, expected_engine=snapshot) == binding
    assert engine.bind_engine(project, snapshot) == binding
    (project / "product.py").write_text("changed product\n")
    assert engine.verify_binding(project) == binding


@pytest.mark.parametrize(
    "mutation",
    ["bytes", "mode", "extra", "directory", "symlink", "hardlink", "fifo", "manifest"],
)
def test_snapshot_rejects_drift_and_unsafe_entries(source, tmp_path, mutation):
    snapshot = tmp_path / "engine"
    engine.create_snapshot(source, snapshot)
    path = snapshot / "scripts/changerail/__init__.py"
    snapshot.chmod(0o755)
    path.parent.chmod(0o755)
    if mutation == "bytes":
        path.chmod(0o644)
        path.write_text("changed\n")
        path.chmod(0o444)
    elif mutation == "mode":
        path.chmod(0o644)
    elif mutation == "extra":
        (snapshot / "extra").write_text("unexpected")
    elif mutation == "directory":
        (snapshot / "empty").mkdir(mode=0o555)
    elif mutation == "symlink":
        path.unlink()
        path.symlink_to(source / "scripts/changerail/__init__.py")
    elif mutation == "hardlink":
        os.link(path, tmp_path / "alias")
    elif mutation == "fifo":
        path.unlink()
        os.mkfifo(path, 0o444)
    else:
        target = snapshot / engine.MANIFEST
        target.chmod(0o644)
        target.write_text("{}")
        target.chmod(0o444)
    snapshot.chmod(0o555)
    path.parent.chmod(0o555)
    with pytest.raises(engine.EngineSnapshotError):
        engine.verify_snapshot(snapshot)


@pytest.mark.parametrize("mutation", ["dirty", "untracked", "symlink", "hardlink"])
def test_source_must_be_clean_and_safe(source, tmp_path, mutation):
    path = source / "scripts/changerail/__init__.py"
    if mutation == "dirty":
        path.write_text("changed\n")
    elif mutation == "untracked":
        (source / "extra.py").write_text("uncommitted\n")
    elif mutation == "symlink":
        path.unlink()
        path.symlink_to("/etc/passwd")
    else:
        os.link(path, tmp_path / "alias")
    with pytest.raises(engine.EngineSnapshotError):
        engine.create_snapshot(source, tmp_path / "engine")
    assert not (tmp_path / "engine").exists()


def test_source_ignored_payload_is_not_accepted(source, tmp_path):
    (source / ".git/info/exclude").write_text("ignored.py\n")
    (source / "scripts/changerail/ignored.py").write_text("private\n")
    with pytest.raises(engine.EngineSnapshotError, match="committed"):
        engine.create_snapshot(source, tmp_path / "engine")


def test_snapshot_must_be_outside_project_and_source(source, tmp_path):
    with pytest.raises(engine.EngineSnapshotError):
        engine.create_snapshot(source, source / "engine")
    project = tmp_path / "project"
    project.mkdir()
    snapshot = project / "engine"
    engine.create_snapshot(source, snapshot)
    with pytest.raises(engine.EngineSnapshotError):
        engine.bind_engine(project, snapshot)


def test_concurrent_creation_publishes_one_verified_inventory(source, tmp_path):
    target = tmp_path / "engine"
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(
            pool.map(lambda _: engine.create_snapshot(source, target), range(4))
        )
    assert all(result == results[0] for result in results)
    assert engine.verify_snapshot(target) == results[0]
    assert not list(tmp_path.glob(".engine.staging-*"))


def test_binding_rejects_wrong_engine_and_copied_project(source, tmp_path):
    first, second = tmp_path / "one", tmp_path / "two"
    engine.create_snapshot(source, first)
    engine.create_snapshot(source, second)
    project = tmp_path / "project"
    project.mkdir()
    engine.bind_engine(project, first)
    with pytest.raises(engine.EngineSnapshotError):
        engine.verify_binding(project, expected_engine=second)
    copied = tmp_path / "copy"
    (copied / ".changerail").mkdir(parents=True)
    (copied / engine.BINDING).write_bytes((project / engine.BINDING).read_bytes())
    with pytest.raises(engine.EngineSnapshotError):
        engine.verify_binding(copied)


def test_publish_crash_leaves_no_partial_destination(source, tmp_path, monkeypatch):
    target = tmp_path / "engine"

    def crash(*_args):
        raise OSError("simulated crash before rename")

    with monkeypatch.context() as patch:
        patch.setattr(engine, "_publish_directory", crash)
        with pytest.raises(OSError, match="simulated crash"):
            engine.create_snapshot(source, target)
    assert not target.exists()
    assert not list(tmp_path.glob(".engine.staging-*"))
    assert engine.create_snapshot(source, target)


def test_publication_never_overwrites_noncooperating_destination(
    source, tmp_path, monkeypatch
):
    target = tmp_path / "engine"
    publish = engine._publish_directory

    def race(stage, destination):
        destination.mkdir()
        publish(stage, destination)

    monkeypatch.setattr(engine, "_publish_directory", race)
    with pytest.raises(FileExistsError):
        engine.create_snapshot(source, target)
    assert target.is_dir()
    assert not list(target.iterdir())


def test_mode_matches_commit_even_with_git_filemode_disabled(source, tmp_path):
    subprocess.run(
        ["git", "-C", str(source), "config", "core.filemode", "false"], check=True
    )
    (source / "scripts/changerail/__init__.py").chmod(0o755)
    with pytest.raises(engine.EngineSnapshotError, match="mode is not committed"):
        engine.create_snapshot(source, tmp_path / "engine")


@pytest.fixture
def rebind_pair(source, tmp_path):
    old, new, project = (tmp_path / name for name in ("old", "new", "project"))
    engine.create_snapshot(source, old)
    (source / "scripts/changerail/__init__.py").write_text("VALUE = 2\n")
    subprocess.run(["git", "-C", str(source), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(source),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "new",
        ],
        check=True,
    )
    engine.create_snapshot(source, new)
    project.mkdir()
    original = engine.bind_engine(project, old)
    return project, old, new, original


def test_rebind_has_append_only_before_after_receipts_and_preserves_runs(rebind_pair):
    project, old, new, original = rebind_pair
    run = project / ".runtime/changerail/runs/stopped/run.json"
    run.parent.mkdir(parents=True)
    run.write_text('{"process_identity":"frozen-old","review_count":2}')
    before = run.read_bytes()
    result = engine.rebind_engine(project, new, original["engine_identity"])
    assert result["binding"] == engine.verify_binding(project, expected_engine=new)
    receipt = Path(result["receipt"])
    intent = json.loads((receipt / "intent.json").read_text())
    assert intent["before"] == original
    assert intent["after"] == result["binding"]
    assert json.loads((receipt / "applied.json").read_text())[
        "intent_sha256"
    ] == engine._digest((receipt / "intent.json").read_bytes())
    files = {path.name: path.read_bytes() for path in receipt.iterdir()}
    assert engine.rebind_engine(project, new, original["engine_identity"]) == result
    assert {path.name: path.read_bytes() for path in receipt.iterdir()} == files
    assert run.read_bytes() == before
    assert engine.verify_snapshot(old)


@pytest.mark.parametrize("point", ["before-replace", "after-replace", "before-applied"])
def test_rebind_retry_reconciles_crash(rebind_pair, monkeypatch, point):
    project, _old, new, original = rebind_pair
    replace = engine._replace_binding
    receipt = engine._rebind_receipt

    def crash_replace(*args):
        if point == "after-replace":
            replace(*args)
        raise OSError("simulated rebind crash")

    def crash_receipt(path, value):
        if path.name == "applied.json":
            raise OSError("simulated rebind crash")
        return receipt(path, value)

    with monkeypatch.context() as patch:
        patch.setattr(
            engine,
            "_rebind_receipt" if point == "before-applied" else "_replace_binding",
            crash_receipt if point == "before-applied" else crash_replace,
        )
        with pytest.raises(OSError, match="simulated rebind crash"):
            engine.rebind_engine(project, new, original["engine_identity"])
    retained = list(
        (project / ".runtime/changerail/engine-rebind").glob("*/intent.json")
    )
    assert len(retained) == 1
    intent_bytes = retained[0].read_bytes()
    result = engine.rebind_engine(project, new, original["engine_identity"])
    assert result["binding"] == engine.verify_binding(project, expected_engine=new)
    assert retained[0].read_bytes() == intent_bytes


def test_rebind_rejects_wrong_expected_identity(rebind_pair):
    project, _old, new, original = rebind_pair
    with pytest.raises(engine.EngineSnapshotError, match="previous identity"):
        engine.rebind_engine(project, new, "0" * 64)
    assert engine.verify_binding(project) == original


@pytest.mark.parametrize("which", ["old", "new"])
def test_rebind_rejects_either_snapshot_drift(rebind_pair, which):
    project, old, new, original = rebind_pair
    snapshot = old if which == "old" else new
    snapshot.chmod(0o755)
    with pytest.raises(engine.EngineSnapshotError, match="drift"):
        engine.rebind_engine(project, new, original["engine_identity"])
    snapshot.chmod(0o555)
    assert engine.verify_binding(project) == original


def test_rebind_rejects_exact_binding_drift_after_intent(rebind_pair, monkeypatch):
    project, _old, new, original = rebind_pair

    def crash(*_args):
        raise OSError("before binding mutation")

    with monkeypatch.context() as patch:
        patch.setattr(engine, "_replace_binding", crash)
        with pytest.raises(OSError):
            engine.rebind_engine(project, new, original["engine_identity"])
    path = project / engine.BINDING
    path.write_text(path.read_text() + "\n")
    with pytest.raises(engine.EngineSnapshotError, match="binding.*drift"):
        engine.rebind_engine(project, new, original["engine_identity"])


def test_rebind_rejects_held_delivery_lock(rebind_pair):
    project, _old, new, original = rebind_pair
    path = project / ".runtime/changerail/delivery.lock"
    path.parent.mkdir(parents=True)
    with path.open("w") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(
            engine.EngineSnapshotError, match="delivery.*lock|delivery runner"
        ):
            engine.rebind_engine(project, new, original["engine_identity"])
    assert engine.verify_binding(project) == original


def test_rebind_rejects_live_run_owner(rebind_pair):
    project, _old, new, original = rebind_pair
    env = dict(os.environ, CHRL_RUN_DIR=str(project / ".runtime/changerail/runs/live"))
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"], env=env
    )
    try:
        with pytest.raises(engine.EngineSnapshotError, match="live process"):
            engine.rebind_engine(project, new, original["engine_identity"])
    finally:
        child.terminate()
        child.wait(timeout=5)
    assert engine.verify_binding(project) == original


def test_rebind_rejects_nested_delivery_operator(rebind_pair, monkeypatch):
    project, _old, new, original = rebind_pair
    monkeypatch.setenv("CHRL_SESSION_ROLE", "delivery")
    with pytest.raises(engine.EngineSnapshotError, match="outside delivery"):
        engine.rebind_engine(project, new, original["engine_identity"])
    assert engine.verify_binding(project) == original


def test_rebind_retry_still_verifies_old_snapshot(rebind_pair):
    project, old, new, original = rebind_pair
    engine.rebind_engine(project, new, original["engine_identity"])
    old.chmod(0o755)
    with pytest.raises(engine.EngineSnapshotError, match="drift"):
        engine.rebind_engine(project, new, original["engine_identity"])
    old.chmod(0o555)
    assert engine.verify_binding(project, expected_engine=new)


def test_rebind_rejects_corrupted_applied_receipt(rebind_pair):
    project, _old, new, original = rebind_pair
    result = engine.rebind_engine(project, new, original["engine_identity"])
    receipt = Path(result["receipt"]) / "applied.json"
    receipt.chmod(0o644)
    receipt.write_text("{}\n")
    receipt.chmod(0o444)
    with pytest.raises(engine.EngineSnapshotError, match="receipt"):
        engine.rebind_engine(project, new, original["engine_identity"])


def test_rebind_race_has_single_transition(rebind_pair):
    project, _old, new, original = rebind_pair

    def apply(_):
        try:
            return engine.rebind_engine(project, new, original["engine_identity"])
        except engine.EngineSnapshotError as exc:
            assert "lock" in str(exc) or "delivery runner" in str(exc)
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(apply, range(4)))
    assert any(results)
    final = engine.rebind_engine(project, new, original["engine_identity"])
    assert all(result is None or result == final for result in results)
    assert (
        len(list((project / ".runtime/changerail/engine-rebind").glob("*/intent.json")))
        == 1
    )


def test_rebind_cli_bootstraps_verified_new_snapshot_and_rejects_mutable_source(
    source, tmp_path
):
    repo = Path(__file__).resolve().parents[3]
    names = [
        "distribution.py",
        "scripts/__init__.py",
        "scripts/changerail/engine_snapshot.py",
        "scripts/changerail/engine_runtime.py",
        "scripts/changerail/contracts.py",
        "bin/chrl",
    ]
    for name in names:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((repo / name).read_bytes())
        path.chmod((repo / name).stat().st_mode & 0o777)
    config = json.loads((source / "distribution.json").read_text())
    config["files"] += ["distribution.py", "scripts/__init__.py", "bin/chrl"]
    (source / "distribution.json").write_text(json.dumps(config))
    runtime = source / "scripts/changerail/engine_runtime.py"
    new_runtime = runtime.read_bytes()
    runtime.write_text('raise RuntimeError("OLD_ENGINE_BOOTSTRAP")\n')

    def commit():
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "engine",
            ],
            check=True,
        )

    commit()
    old, new, project = (tmp_path / name for name in ("old", "new", "project"))
    engine.create_snapshot(source, old)
    runtime.write_bytes(new_runtime)
    commit()
    engine.create_snapshot(source, new)
    project.mkdir()
    original = engine.bind_engine(project, old)
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("CHRL_") and key != "PYTHONPATH"
    }
    arguments = [
        "--project",
        str(project),
        "engine-rebind",
        "--previous-identity",
        original["engine_identity"],
    ]
    mutable = subprocess.run(
        [str(source / "bin/chrl"), *arguments], env=env, capture_output=True, text=True
    )
    assert mutable.returncode != 0
    assert "snapshot" in mutable.stderr
    assert "OLD_ENGINE_BOOTSTRAP" not in mutable.stderr
    result = subprocess.run(
        [str(new / "bin/chrl"), *arguments], env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["binding"] == engine.verify_binding(
        project, expected_engine=new
    )
    retry = subprocess.run(
        [str(new / "bin/chrl"), *arguments], env=env, capture_output=True, text=True
    )
    assert retry.returncode == 0, retry.stderr
    assert json.loads(retry.stdout) == json.loads(result.stdout)


@pytest.mark.parametrize('field', ['schema', 'before', 'after_sha256'])
def test_rebind_pending_intent_rejects_internal_drift(rebind_pair, monkeypatch, field):
    project, _old, new, original = rebind_pair
    with monkeypatch.context() as patch:
        patch.setattr(engine, '_replace_binding', lambda *_: (_ for _ in ()).throw(OSError('crash')))
        with pytest.raises(OSError):
            engine.rebind_engine(project, new, original['engine_identity'])
    intent_path = next((project / '.runtime/changerail/engine-rebind').glob('*/intent.json'))
    intent = json.loads(intent_path.read_text())
    if field == 'before':
        intent[field]['project_root'] = '/foreign'
    else:
        intent[field] = 'corrupted'
    intent_path.chmod(0o644)
    intent_path.write_bytes(engine._encoded(intent))
    intent_path.chmod(0o444)
    before = (project / engine.BINDING).read_bytes()
    with pytest.raises(engine.EngineSnapshotError):
        engine.rebind_engine(project, new, original['engine_identity'])
    assert (project / engine.BINDING).read_bytes() == before


@pytest.mark.parametrize('target', ['old', 'new', 'binding'])
def test_rebind_rechecks_inputs_after_intent(rebind_pair, monkeypatch, target):
    project, old, new, original = rebind_pair
    receipt = engine._rebind_receipt
    before = (project / engine.BINDING).read_bytes()
    def drift(path, value):
        receipt(path, value)
        if path.name == 'intent.json':
            victim = project / engine.BINDING if target == 'binding' else (old if target == 'old' else new) / 'scripts/changerail/__init__.py'
            victim.chmod(0o644)
            victim.write_bytes(victim.read_bytes() + b'\n')
            if target != 'binding':
                victim.chmod(0o444)
    monkeypatch.setattr(engine, '_rebind_receipt', drift)
    with pytest.raises(engine.EngineSnapshotError):
        engine.rebind_engine(project, new, original['engine_identity'])
    assert (project / engine.BINDING).read_bytes() == before + (b'\n' if target == 'binding' else b'')
    assert not list((project / '.runtime/changerail/engine-rebind').glob('*/applied.json'))


def test_rebind_persists_new_runtime_directory_entries_before_binding(rebind_pair, monkeypatch):
    project, _old, new, original = rebind_pair
    synced = []
    sync, replace = engine._sync_directory, engine._replace_binding
    def record(path):
        synced.append(path)
        sync(path)
    def checked_replace(path, data):
        assert project in synced
        assert project / '.runtime' in synced
        assert project / '.runtime/changerail' in synced
        replace(path, data)
    monkeypatch.setattr(engine, '_sync_directory', record)
    monkeypatch.setattr(engine, '_replace_binding', checked_replace)
    engine.rebind_engine(project, new, original['engine_identity'])


def test_rebind_retry_completes_directory_sync_after_replace_crash(rebind_pair, monkeypatch):
    project, _old, new, original = rebind_pair
    sync = engine._sync_directory
    def crash(path):
        if path == project / '.changerail':
            raise OSError('directory sync crash')
        sync(path)
    with monkeypatch.context() as patch:
        patch.setattr(engine, '_sync_directory', crash)
        with pytest.raises(OSError, match='directory sync crash'):
            engine.rebind_engine(project, new, original['engine_identity'])
    synced = []
    def record(path):
        synced.append(path)
        sync(path)
    monkeypatch.setattr(engine, '_sync_directory', record)
    engine.rebind_engine(project, new, original['engine_identity'])
    assert project / '.changerail' in synced


@pytest.mark.parametrize('damage', [None, 'missing-applied', 'foreign-before', 'unknown-identity', 'binding-hash'])
def test_bound_predecessor_requires_completed_matching_rebind(rebind_pair, damage):
    project, _old, new, original = rebind_pair
    identity = {
        'engine/identity': original['engine_identity'],
        'engine/root': engine._digest(original['engine_root'].encode()),
        'project/.changerail/engine-binding.json': engine._digest((project / engine.BINDING).read_bytes()),
    }
    result = engine.rebind_engine(project, new, original['engine_identity'])
    directory = Path(result['receipt'])
    if damage == 'missing-applied':
        (directory / 'applied.json').unlink()
    elif damage == 'foreign-before':
        path = directory / 'intent.json'
        value = json.loads(path.read_text())
        value['before']['project_root'] = '/foreign'
        path.chmod(0o644)
        path.write_bytes(engine._encoded(value))
    elif damage == 'unknown-identity':
        identity['engine/identity'] = 'unknown'
    elif damage == 'binding-hash':
        identity['project/.changerail/engine-binding.json'] = 'unknown'
    if damage:
        with pytest.raises(engine.EngineSnapshotError):
            engine.verify_previous_binding(project, identity)
    else:
        engine.verify_previous_binding(project, identity)


def test_rebind_retry_persists_renamed_intent_before_binding(rebind_pair, monkeypatch):
    project, _old, new, original = rebind_pair
    sync, replace = engine._sync_directory, engine._replace_binding
    def crash(path):
        if (path / 'intent.json').exists():
            raise OSError('intent directory sync crash')
        sync(path)
    with monkeypatch.context() as patch:
        patch.setattr(engine, '_sync_directory', crash)
        with pytest.raises(OSError, match='intent directory sync crash'):
            engine.rebind_engine(project, new, original['engine_identity'])
    intent = next((project / '.runtime/changerail/engine-rebind').glob('*/intent.json'))
    synced = []
    def record(path):
        synced.append(path)
        sync(path)
    def checked_replace(path, data):
        assert intent.parent in synced, 'intent must be durable before binding'
        replace(path, data)
    monkeypatch.setattr(engine, '_sync_directory', record)
    monkeypatch.setattr(engine, '_replace_binding', checked_replace)
    engine.rebind_engine(project, new, original['engine_identity'])
