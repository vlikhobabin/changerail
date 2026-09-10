"""Pending restoration excludes competing public mutation routes."""

from __future__ import annotations

import pytest

import distribution as dist
from scripts.changerail import local_delivery as d
from scripts.changerail import source_install


def test_pending_transition_blocks_all_cli_writers_before_dispatch(tmp_path, monkeypatch):
    root = tmp_path / "project"
    pending = root / ".runtime/changerail/plan-restorations/pending"
    pending.mkdir(parents=True)
    (pending / "apply-intent.json").write_text('{}\n')
    monkeypatch.setattr(d, "REPO_ROOT", root)
    monkeypatch.setattr(d, "RUNTIME_ROOT", root / ".runtime/changerail")
    called = []
    monkeypatch.setattr(d, "capture_manifest", lambda *a: called.append("manifest") or {})
    monkeypatch.setattr(d, "install_local_hooks", lambda: called.append("install") or {})
    for command in (["manifest", "card.md"], ["install"]):
        assert d.main(command) == 2
    assert called == []


def test_pending_transition_blocks_installer_and_source_under_lock(tmp_path, monkeypatch):
    root = tmp_path / "project"
    pending = root / ".runtime/changerail/plan-restorations/pending"
    pending.mkdir(parents=True)
    (pending / "apply-intent.json").write_text('{}\n')
    with pytest.raises(dist.DistributionError, match="pending.*restoration"):
        with dist.delivery_lock(root):
            pytest.fail("installer/source writer admitted")
    monkeypatch.setattr(dist, "git_root", lambda value: root)
    for operation in (
        lambda: dist.install(root, tmp_path / "missing.tar.gz"),
        lambda: source_install.detach(root),
    ):
        with pytest.raises(dist.DistributionError, match="pending.*restoration"):
            operation()
    assert not (pending / "applied.json").exists()


def test_pending_guard_runs_after_acquiring_project_lock(tmp_path, monkeypatch):
    root = tmp_path / "project"
    pending = root / ".runtime/changerail/plan-restorations/pending"
    pending.mkdir(parents=True)
    (pending / "apply-intent.json").write_text('{}\n')
    monkeypatch.setattr(d, "REPO_ROOT", root)
    monkeypatch.setattr(d, "RUNTIME_ROOT", root / ".runtime/changerail")
    with pytest.raises(d.DeliveryError, match="pending.*restoration"):
        with d.delivery_lock():
            pytest.fail("native-accept writer admitted")
    # Apply needs this explicit internal exception to reconcile the same intent.
    with d.delivery_lock(restoration_reconcile=True):
        pass
