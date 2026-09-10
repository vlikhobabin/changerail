"""Portable distribution acceptance, independent of product fixtures."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[3] / "distribution.py"
spec = importlib.util.spec_from_file_location("native_distribution", MODULE)
assert spec and spec.loader
dist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dist)


@pytest.fixture
def candidate(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    source.mkdir()
    (source / "bin").mkdir()
    (source / "bin/chrl").write_text("#!/bin/sh\necho native\n")
    (source / "bin/chrl").chmod(0o755)
    (source / "distribution.json").write_text(
        json.dumps(
            {
                "schema": "changerail.distribution-config.v1",
                "version": "2.0.0-candidate.1",
                "execution_contract": "changerail.native.v1",
                "provenance": {"owner": "ChangeRail"},
                "files": ["bin/chrl", "distribution.json"],
                "trees": {},
            }
        )
    )
    archive = tmp_path / "candidate.tar.gz"
    dist.build(source, archive)
    return source, archive


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    root = tmp_path / "arbitrary-consumer"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text(".runtime/\n")
    (root / ".changerail").mkdir()
    (root / ".changerail/profile.toml").write_text('project = "independent"\n')
    return root


def test_deterministic_archive_and_exact_install(candidate, consumer, tmp_path):
    source, archive = candidate
    repeated = tmp_path / "repeated.tar.gz"
    dist.build(source, repeated)
    assert archive.read_bytes() == repeated.read_bytes()
    result = dist.install(consumer, archive, dry_run=True)
    assert result["created"] == ["bin/chrl", "distribution.json"]
    assert not (consumer / "bin").exists()
    dist.install(consumer, archive)
    assert (consumer / "bin/chrl").read_bytes() == (source / "bin/chrl").read_bytes()
    assert (consumer / "bin/chrl").stat().st_mode & 0o111
    assert (
        consumer / ".changerail/profile.toml"
    ).read_text() == 'project = "independent"\n'
    lock_before = (consumer / dist.LOCK).read_bytes()
    repeated_result = dist.install(consumer, archive)
    assert not repeated_result["created"] and not repeated_result["replaced"]
    assert (consumer / dist.LOCK).read_bytes() == lock_before


def test_runtime_consumer_installs_no_changerail_development_suite(consumer, tmp_path):
    source = MODULE.parent
    assert (source / "tools/changerail/tests/test_distribution.py").is_file()
    archive = tmp_path / "runtime-only.tar.gz"
    dist.build(source, archive)
    dist.install(consumer, archive)
    assert (consumer / "scripts/changerail/local_delivery.py").is_file()
    assert (consumer / "tools/openspec/check-install.mjs").is_file()
    assert not (consumer / "tools/changerail/tests").exists()
    assert not (consumer / "tools/openspec/test-wrapper.mjs").exists()
    assert not (consumer / "bin/test-changerail").exists()
    assert not (consumer / ".changerail/tests").exists()


def test_tampered_installed_source_is_not_overwritten(candidate, consumer):
    _source, archive = candidate
    dist.install(consumer, archive)
    (consumer / "bin/chrl").write_text("local edit\n")
    with pytest.raises(dist.DistributionError, match="local drift"):
        dist.install(consumer, archive)
    assert (consumer / "bin/chrl").read_text() == "local edit\n"


def test_unowned_file_requires_exact_adoption(candidate, consumer, tmp_path):
    _source, archive = candidate
    (consumer / "bin").mkdir()
    (consumer / "bin/chrl").write_text("legacy\n")
    obsolete = consumer / "scripts/changerail/retired.py"
    obsolete.parent.mkdir(parents=True)
    obsolete.write_text("historical = True\n")
    with pytest.raises(dist.DistributionError, match="unowned file"):
        dist.install(consumer, archive)
    inventory = dist.adoption_inventory(
        consumer, archive, ["bin/chrl", "scripts/changerail/retired.py"]
    )
    allowance = tmp_path / "adoption.json"
    allowance.write_bytes(dist.encoded(inventory))
    result = dist.install(consumer, archive, adoption=allowance)
    assert result["removed"] == ["scripts/changerail/retired.py"]
    assert not obsolete.exists()
    backup = (
        consumer
        / ".runtime/changerail/distribution"
        / dist.digest(archive.read_bytes())
    )
    assert (
        backup / "before/scripts/changerail/retired.py"
    ).read_text() == "historical = True\n"
    assert json.loads((backup / "audit.json").read_text())["state"] == "installed"


def test_adoption_rejects_drift_or_wrong_candidate(candidate, consumer, tmp_path):
    source, archive = candidate
    (consumer / "bin").mkdir()
    (consumer / "bin/chrl").write_text("legacy\n")
    inventory = dist.adoption_inventory(consumer, archive, ["bin/chrl"])
    allowance = tmp_path / "adoption.json"
    allowance.write_bytes(dist.encoded(inventory))
    (consumer / "bin/chrl").write_text("changed since review\n")
    with pytest.raises(dist.DistributionError, match="predecessor has local drift"):
        dist.install(consumer, archive, adoption=allowance)
    (source / "bin/chrl").write_text("new candidate\n")
    second = tmp_path / "second.tar.gz"
    dist.build(source, second)
    with pytest.raises(dist.DistributionError, match="does not bind"):
        dist.install(consumer, second, adoption=allowance)


def test_active_run_refused_unless_explicit_exact_read_only_adoption(
    candidate, consumer, tmp_path
):
    _source, archive = candidate
    run = consumer / ".runtime/changerail/runs/unfinished/run.json"
    run.parent.mkdir(parents=True)
    run.write_text(json.dumps({"execution_contract": "legacy", "run_id": "unfinished"}))
    before = run.read_bytes()
    with pytest.raises(dist.DistributionError, match="frozen run blocks"):
        dist.install(consumer, archive)
    inventory = dist.adoption_inventory(consumer, archive, [], retain_history=True)
    allowance = tmp_path / "adoption.json"
    allowance.write_bytes(dist.encoded(inventory))
    dist.install(consumer, archive, adoption=allowance)
    assert run.read_bytes() == before
    lock = json.loads((consumer / dist.LOCK).read_text())
    assert list(lock["retained_read_only_runs"]) == [
        run.relative_to(consumer).as_posix()
    ]
    run.write_text("{}")
    with pytest.raises(dist.DistributionError, match="historical run changed"):
        dist.install(consumer, archive)


def test_ordinary_update_proves_old_hashes_and_refuses_active_run(
    candidate, consumer, tmp_path
):
    source, archive = candidate
    dist.install(consumer, archive)
    run = consumer / ".runtime/changerail/runs/current/run.json"
    run.parent.mkdir(parents=True)
    run.write_text(json.dumps({"execution_contract": "changerail.native.v1"}))
    dist.install(consumer, archive)  # Exact reinstall changes no frozen process.
    (source / "bin/chrl").write_text("updated\n")
    update = tmp_path / "update.tar.gz"
    dist.build(source, update)
    with pytest.raises(dist.DistributionError, match="frozen run blocks"):
        dist.install(consumer, update)
    run.unlink()
    result = dist.install(consumer, update)
    assert result["replaced"] == ["bin/chrl"]
    assert (consumer / "bin/chrl").read_text() == "updated\n"


def test_symlink_and_product_path_refused(candidate, consumer, tmp_path):
    _source, archive = candidate
    destination = tmp_path / "outside"
    destination.mkdir()
    (consumer / "bin").symlink_to(destination, target_is_directory=True)
    with pytest.raises(dist.DistributionError, match="symlink"):
        dist.install(consumer, archive)
    with pytest.raises(dist.DistributionError, match="not an eligible predecessor"):
        dist.adoption_inventory(consumer, archive, ["src/product.py"])
    assert not list(destination.iterdir())


def test_manifest_tamper_is_rejected(candidate, tmp_path):
    import gzip
    import io
    import tarfile

    _source, archive = candidate
    manifest, payload = dist.inspect_archive(archive)
    payload["bin/chrl"] = (b"tampered\n", 0o755)
    payload[dist.MANIFEST] = (dist.encoded(manifest), 0o644)
    tampered = tmp_path / "tampered.tar.gz"
    with gzip.open(tampered, "wb") as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as output:
            for name, (data, mode) in payload.items():
                member = tarfile.TarInfo(name)
                member.size, member.mode = len(data), mode
                output.addfile(member, io.BytesIO(data))
    with pytest.raises(dist.DistributionError, match="hashes or inventory"):
        dist.inspect_archive(tampered)


def test_live_delivery_lock_refuses_even_explicit_retirement(
    candidate, consumer, tmp_path
):
    import fcntl

    _source, archive = candidate
    inventory = dist.adoption_inventory(consumer, archive, [], retain_history=True)
    allowance = tmp_path / "adoption.json"
    allowance.write_bytes(dist.encoded(inventory))
    lock = consumer / ".runtime/changerail/delivery.lock"
    lock.parent.mkdir(parents=True)
    with lock.open("w") as writer:
        fcntl.flock(writer.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(dist.DistributionError, match="writer or another installer"):
            dist.install(consumer, archive, adoption=allowance)
        assert not (consumer / "bin").exists()
    dist.install(consumer, archive, adoption=allowance)


def test_upgrade_can_explicitly_retain_completed_run_without_overriding_drift(
    candidate, consumer, tmp_path
):
    source, archive = candidate
    dist.install(consumer, archive)
    run = consumer / ".runtime/changerail/runs/completed/run.json"
    run.parent.mkdir(parents=True)
    run.write_text(
        json.dumps(
            {"execution_contract": "changerail.native.v1", "status": "completed"}
        )
    )
    run_before = run.read_bytes()
    (source / "bin/chrl").write_text("updated\n")
    update = tmp_path / "update.tar.gz"
    dist.build(source, update)
    allowance = tmp_path / "history.json"
    allowance.write_bytes(dist.encoded(dist.history_inventory(consumer, update)))
    (consumer / "bin/chrl").write_text("local drift\n")
    with pytest.raises(dist.DistributionError, match="local drift"):
        dist.install(consumer, update, history=allowance)
    (consumer / "bin/chrl").write_text("#!/bin/sh\necho native\n")
    dist.install(consumer, update, history=allowance)
    assert run.read_bytes() == run_before
    lock = json.loads((consumer / dist.LOCK).read_text())
    assert run.relative_to(consumer).as_posix() in lock["retained_read_only_runs"]


def test_failed_replacement_restores_exact_sources_and_lock(
    candidate, consumer, tmp_path, monkeypatch
):
    source, archive = candidate
    dist.install(consumer, archive)
    original = {
        name: dist.read_file(consumer, name)
        for name in ["bin/chrl", "distribution.json", dist.LOCK]
    }
    (source / "bin/chrl").write_text("updated\n")
    config = json.loads((source / "distribution.json").read_text())
    config["version"] = "2.0.0-candidate.2"
    (source / "distribution.json").write_text(json.dumps(config))
    update = tmp_path / "update.tar.gz"
    dist.build(source, update)
    write = dist.write_atomic
    failed = False

    def fail_second_replacement(path, data, mode=0o644):
        nonlocal failed
        if path == consumer / "distribution.json" and not failed:
            failed = True
            raise OSError("injected replacement failure")
        return write(path, data, mode)

    monkeypatch.setattr(dist, "write_atomic", fail_second_replacement)
    with pytest.raises(dist.DistributionError, match="previous bytes were restored"):
        dist.install(consumer, update)
    assert failed
    assert {name: dist.read_file(consumer, name) for name in original} == original
    backup = (
        consumer / ".runtime/changerail/distribution" / dist.digest(update.read_bytes())
    )
    audit = json.loads((backup / "audit.json").read_text())
    assert audit["state"] == "rolled_back" and not audit["rollback_errors"]


def test_product_runtime_is_outside_run_inventory(candidate, consumer):
    _source, archive = candidate
    product = consumer / ".runtime/product/run.json"
    product.parent.mkdir(parents=True)
    product.write_text("not a changerail run, not even json")
    dist.install(consumer, archive)
    assert dist.run_inventory(consumer) == {}
    assert product.read_text() == "not a changerail run, not even json"


def test_failed_lock_commit_restores_removed_files_and_removes_created_files(
    candidate, consumer, tmp_path, monkeypatch
):
    source, archive = candidate
    dist.install(consumer, archive)
    before = dist.read_file(consumer, "bin/chrl")
    lock_before = (consumer / dist.LOCK).read_bytes()
    config = json.loads((source / "distribution.json").read_text())
    config["files"] = ["bin/chrl-run", "distribution.json"]
    (source / "distribution.json").write_text(json.dumps(config))
    (source / "bin/chrl-run").write_text("new runner\n")
    update = tmp_path / "replacement.tar.gz"
    dist.build(source, update)
    original_write = dist.write_atomic
    injected = False

    def fail_lock_once(path, data, mode=0o644):
        nonlocal injected
        if path == consumer / dist.LOCK and not injected:
            injected = True
            assert not (consumer / "bin/chrl").exists()
            assert (consumer / "bin/chrl-run").read_text() == "new runner\n"
            raise OSError("injected lock replacement failure")
        return original_write(path, data, mode)

    monkeypatch.setattr(dist, "write_atomic", fail_lock_once)
    with pytest.raises(dist.DistributionError, match="previous bytes were restored"):
        dist.install(consumer, update)
    assert injected
    assert dist.read_file(consumer, "bin/chrl") == before
    assert not (consumer / "bin/chrl-run").exists()
    assert (consumer / dist.LOCK).read_bytes() == lock_before
