"""Shared-source attachment and separation from retained project evidence."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import distribution as dist
from scripts.changerail import local_delivery as delivery
from scripts.changerail import source_binding as binding
from scripts.changerail import source_install as install

SOURCE = Path(__file__).resolve().parents[3]


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    _config, payload = dist.source_payload(SOURCE)
    for name, (data, mode) in payload.items():
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(mode)
    shutil.copytree(
        SOURCE / "tools/changerail/tests",
        root / "tools/changerail/tests",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy2(SOURCE / "bin/test-changerail", root / "bin/test-changerail")
    shutil.copy2(
        SOURCE / "tools/openspec/test-wrapper.mjs",
        root / "tools/openspec/test-wrapper.mjs",
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def consumer(tmp_path, name="consumer"):
    root = tmp_path / name
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text(".runtime/\n")
    (root / ".changerail").mkdir()
    (root / ".changerail/profile.toml").write_text(
        (SOURCE / "tools/changerail/templates/profile.toml").read_text()
    )
    return root


def test_attach_two_projects_shared_edits_and_detach(source, tmp_path, monkeypatch):
    first, second = consumer(tmp_path, "one"), consumer(tmp_path, "two")
    install.attach(source, first, development=True)
    install.attach(source, second)
    for project in (first, second):
        assert not os.path.lexists(project / "tools/openspec/.gitignore")
        assert "tools/openspec/.gitignore" not in binding.binding(project)["mappings"]
    assert (first / "tools/changerail/tests").is_symlink()
    assert (first / "tools/openspec/test-wrapper.mjs").is_symlink()
    assert not (second / "tools/changerail/tests").exists()
    assert not (second / "tools/openspec/test-wrapper.mjs").exists()
    assert (
        binding.trusted_path(first, first / "scripts/changerail/contracts.py")
        == source / "scripts/changerail/contracts.py"
    )
    before = binding.source_info(first)["sha256"]
    (first / "scripts/changerail/contracts.py").write_text("changed shared source\n")
    assert (
        second / "scripts/changerail/contracts.py"
    ).read_text() == "changed shared source\n"
    assert binding.source_info(first)["sha256"] != before
    assert binding.source_info(first)["dirty"]
    monkeypatch.setenv("CHRL_PROJECT_ROOT", str(first))
    assert binding.project_root(source) == first
    monkeypatch.setenv("CHRL_PROJECT_ROOT", str(second))
    assert binding.project_root(source) == second
    install.detach(first)
    assert not (first / binding.BINDING).exists()
    assert not (first / "scripts/changerail").exists()
    assert (
        second / "scripts/changerail/contracts.py"
    ).read_text() == "changed shared source\n"


@pytest.mark.parametrize("dry_run", [False, True])
def test_attach_requires_ignored_runtime_before_creating_artifacts(
    source, tmp_path, dry_run
):
    target = consumer(tmp_path)
    (target / ".gitignore").unlink()
    before = sorted(path.relative_to(target) for path in target.rglob("*"))
    with pytest.raises(dist.DistributionError, match="must ignore .runtime/"):
        install.attach(source, target, dry_run=dry_run)
    assert sorted(path.relative_to(target) for path in target.rglob("*")) == before


@pytest.mark.parametrize("loss", ["moved", "deleted"])
@pytest.mark.parametrize("legacy", [False, True])
def test_detach_restores_without_shared_source(source, tmp_path, loss, legacy):
    target = consumer(tmp_path)
    (target / "bin").mkdir()
    original = target / "bin/chrl"
    original.write_bytes(b"original consumer executable\n")
    original.chmod(0o755)
    adoption = tmp_path / "adoption.json"
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    attached = install.attach(source, target, adoption=adoption)
    if legacy:
        # Existing v1 attachments predate the inventory digest field.
        attached.pop("inventory_sha256")
        (target / binding.BINDING).write_bytes(dist.encoded(attached))
        (target / attached["backup"] / "audit.json").write_bytes(
            dist.encoded({"state": "attached", **attached})
        )
    if loss == "moved":
        source.rename(tmp_path / "moved-source")
    else:
        shutil.rmtree(source)
    with pytest.raises(delivery.DeliveryError, match="shared-source root"):
        binding.binding(target)
    assert install.detach(target, dry_run=True)["dry_run"]
    assert original.is_symlink()
    install.detach(target)
    assert not original.is_symlink()
    assert original.read_bytes() == b"original consumer executable\n"
    assert original.stat().st_mode & 0o111
    assert not (target / binding.BINDING).exists()


@pytest.mark.parametrize(
    "tamper", ["link", "parent", "mappings", "inventory", "backup", "backup-parent"]
)
def test_detach_missing_source_rejects_tampering(source, tmp_path, tamper):
    target = consumer(tmp_path)
    (target / "bin").mkdir()
    (target / "bin/chrl").write_text("previous executable\n")
    adoption = tmp_path / "adoption.json"
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    attached = install.attach(source, target, adoption=adoption)
    source.rename(tmp_path / "moved-source")
    backup = target / attached["backup"]
    if tamper == "link":
        (target / "bin/chrl").unlink()
        (target / "bin/chrl").symlink_to(tmp_path / "replacement")
    elif tamper == "parent":
        (target / "bin").rename(target / "redirected-bin")
        (target / "bin").symlink_to(target / "redirected-bin")
    elif tamper == "mappings":
        attached["mappings"]["bin/chrl"] = "bin/chrl-run"
        (target / binding.BINDING).write_bytes(dist.encoded(attached))
    elif tamper == "inventory":
        document = json.loads((backup / "inventory.json").read_bytes())
        document["mappings"]["bin/chrl"] = "bin/chrl-run"
        (backup / "inventory.json").write_bytes(dist.encoded(document))
    elif tamper == "backup":
        (backup / "before/bin/chrl").write_text("tampered executable\n")
    else:
        (backup / "before").rename(backup / "redirected-before")
        (backup / "before").symlink_to(backup / "redirected-before")
    before = (target / binding.BINDING).read_bytes()
    with pytest.raises((delivery.DeliveryError, dist.DistributionError)):
        install.detach(target)
    assert (target / binding.BINDING).read_bytes() == before
    assert (target / "bin/chrl").is_symlink()


def test_source_directory_redirect_is_rejected(source, tmp_path):
    target = consumer(tmp_path)
    install.attach(source, target)
    directory = source / "scripts/changerail/adapters"
    outside = tmp_path / "outside-adapters"
    directory.rename(outside)
    directory.symlink_to(outside, target_is_directory=True)
    with pytest.raises(
        delivery.DeliveryError, match="linked path inside shared source"
    ):
        binding.source_info(target)


def test_profile_cannot_be_declared_as_shared_runtime(source, tmp_path):
    target = consumer(tmp_path)
    install.attach(source, target)
    document = target / binding.BINDING
    value = json.loads(document.read_text())
    value["mappings"][".changerail/profile.toml"] = (
        "tools/changerail/templates/profile.toml"
    )
    document.write_text(json.dumps(value))
    with pytest.raises(delivery.DeliveryError, match="tool ownership"):
        binding.binding(target)


@pytest.mark.parametrize("tamper", ["extra-file", "previous-lock"])
def test_detach_rejects_unexpected_restoration_bytes(source, tmp_path, tamper):
    target = consumer(tmp_path)
    archive = tmp_path / "runtime.tar.gz"
    dist.build(source, archive)
    dist.install(target, archive)
    adoption = tmp_path / "adoption.json"
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    attached = install.attach(source, target, adoption=adoption)
    backup = target / attached["backup"]
    if tamper == "extra-file":
        (backup / "before/scripts/changerail/unexpected.py").write_text(
            "unexpected = True\n"
        )
    else:
        (backup / "previous-lock.json").write_text("{}\n")
    before = (target / binding.BINDING).read_bytes()
    with pytest.raises(
        dist.DistributionError, match="backup inventory changed|previous lock changed"
    ):
        install.detach(target)
    assert (target / binding.BINDING).read_bytes() == before
    assert (target / "scripts/changerail").is_symlink()


def test_exact_predecessor_inventory_conflicts_and_rollback(
    source, tmp_path, monkeypatch
):
    target = consumer(tmp_path)
    (target / "bin").mkdir()
    (target / "bin/chrl").write_text("old executable\n")
    with pytest.raises(dist.DistributionError, match="requires exact"):
        install.attach(source, target)
    adoption = tmp_path / "adoption.json"
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    (target / "bin/chrl").write_text("user edit\n")
    with pytest.raises(dist.DistributionError, match="changed since"):
        install.attach(source, target, adoption=adoption)
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    original = Path.symlink_to

    def fail(self, *args, **kwargs):
        if self.name == "chrl-run":
            raise OSError("injected link failure")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "symlink_to", fail)
    with pytest.raises(OSError, match="injected"):
        install.attach(source, target, adoption=adoption)
    assert (target / "bin/chrl").read_text() == "user edit\n"
    assert not (target / "bin/chrl").is_symlink()
    assert not (target / binding.BINDING).exists()
    assert not (target / dist.LOCK).exists()


def test_bound_runtime_identity_does_not_relax_evidence_safety(
    source, tmp_path, monkeypatch
):
    target = consumer(tmp_path)
    install.attach(source, target)
    monkeypatch.setattr(delivery, "REPO_ROOT", target)
    monkeypatch.setattr(delivery, "PROFILE_PATH", target / ".changerail/profile.toml")
    identity = delivery.execution_identity()
    assert "scripts/changerail/contracts.py" in identity
    assert not any("tools/changerail/tests" in key for key in identity)
    assert delivery.external_changerail_symlinks() == []
    with pytest.raises((delivery.DeliveryError, OSError)):
        delivery._check_bytes(target / "scripts/changerail/contracts.py")
    external = target / "evidence.json"
    external.symlink_to(source / "distribution.json")
    assert binding.trusted_path(target, external) is None
    with pytest.raises((delivery.DeliveryError, OSError)):
        delivery._check_bytes(external)
    # A source-side redirect is not covered by consumer trust.
    module = source / "scripts/changerail/contracts.py"
    module.unlink()
    module.symlink_to(source / "distribution.json")
    with pytest.raises(delivery.DeliveryError, match="linked path inside"):
        delivery.execution_identity()


def test_copy_install_refuses_linked_consumer(source, tmp_path):
    target = consumer(tmp_path)
    install.attach(source, target)
    with pytest.raises(dist.DistributionError, match="must detach"):
        dist.install(target, tmp_path / "irrelevant.tar.gz")


def test_real_cli_uses_invocation_project_and_explicit_root(source, tmp_path):
    one, two = consumer(tmp_path, "first"), consumer(tmp_path, "second")
    install.attach(source, one)
    install.attach(source, two)
    env = {**os.environ, "CHRL_PROJECT_ROOT": str(one)}
    # Missing OpenSpec is reported against the consumer; no product operation runs.
    result = subprocess.run(
        [str(two / "bin/chrl"), "--project", str(two), "wiring"],
        cwd=one,
        env=env,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    assert report["source"]["project_root"] == str(two)
    assert report["source"]["source_root"] == str(source)
    assert (two / ".changerail/profile.toml").is_file()
    assert not (source / ".runtime").exists()


def test_linked_openspec_checks_and_executes_selected_consumer_package(
    source, tmp_path
):
    target = consumer(tmp_path)
    install.attach(source, target)
    package = target / "tools/openspec/node_modules/@fission-ai/openspec"
    (package / "bin").mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps({"name": "@fission-ai/openspec", "version": "1.3.1"})
    )
    (package / "bin/openspec.js").write_text(
        "console.log(JSON.stringify({cwd:process.cwd(),args:process.argv.slice(2)}))"
    )
    env = {
        key: value for key, value in os.environ.items() if key != "CHRL_PROJECT_ROOT"
    }
    result = subprocess.run(
        [str(target / "bin/openspec"), "--project", str(target), "selected-consumer"],
        cwd=source,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "cwd": str(target),
        "args": ["selected-consumer"],
    }


def test_attach_lock_history_and_detach_preserve_original_receipts(source, tmp_path):
    target = consumer(tmp_path)
    archive = tmp_path / "candidate.tar.gz"
    dist.build(source, archive)
    dist.install(target, archive)
    old_lock = (target / dist.LOCK).read_bytes()
    retained = target / ".runtime/changerail/runs/old/run.json"
    retained.parent.mkdir(parents=True)
    retained.write_text(
        json.dumps(
            {
                "mode": "delivery",
                "execution_contract": "changerail.native.v1",
                "lifecycle_mode": "openspec-v1",
            }
        )
    )
    receipt_bytes = retained.read_bytes()
    adoption = tmp_path / "adoption.json"
    adoption.write_bytes(dist.encoded(install.inventory(source, target, False)))
    install.attach(source, target, adoption=adoption)
    lock = json.loads((target / dist.LOCK).read_bytes())
    assert ".runtime/changerail/runs/old/run.json" in lock["retained_read_only_runs"]
    assert retained.read_bytes() == receipt_bytes
    install.detach(target)
    assert (target / dist.LOCK).read_bytes() == old_lock
    assert retained.read_bytes() == receipt_bytes
    assert not (target / "bin/chrl").is_symlink()
    assert (target / "bin/chrl").read_bytes() == (source / "bin/chrl").read_bytes()
