"""Immutable engine inventories and explicit project bindings."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
import subprocess

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
