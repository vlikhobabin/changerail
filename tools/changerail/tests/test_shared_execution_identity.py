"""Frozen execution includes OpenSpec code read through actual source links."""

import hashlib

import pytest

from scripts.changerail import local_delivery as delivery
from scripts.changerail import source_install
from test_source_binding import consumer, source as source


@pytest.mark.parametrize("operation", ["edit", "remove"])
def test_linked_workflow_drift_blocks_both_consumers(
    source, tmp_path, monkeypatch, operation
):
    projects = [consumer(tmp_path, name) for name in ("first", "second")]
    relative = "tools/openspec/workflow-instructions.mjs"
    snapshots = {}
    for project in projects:
        source_install.attach(source, project)
        monkeypatch.setattr(delivery, "REPO_ROOT", project)
        monkeypatch.setattr(
            delivery, "PROFILE_PATH", project / ".changerail/profile.toml"
        )
        monkeypatch.setattr(delivery, "RUNTIME_ROOT", project / ".runtime/changerail")
        run = delivery.RUNTIME_ROOT / "runs" / "frozen"
        run.mkdir(parents=True)
        identity = delivery.execution_identity()
        assert (
            identity[relative]
            == hashlib.sha256((source / relative).read_bytes()).hexdigest()
        )
        delivery.write_json(
            run / "run.json",
            {
                "execution_contract": "changerail.native.v1",
                "mode": "delivery",
                "lifecycle_mode": "openspec-v1",
                "process_identity": identity,
            },
        )
        snapshots[project] = (run / "run.json").read_bytes()
        delivery.require_frozen_execution(run)

    linked = projects[0] / relative
    if operation == "edit":
        linked.write_text("changed workflow instructions\n")
    else:
        (source / relative).unlink()
    for project in projects:
        monkeypatch.setattr(delivery, "REPO_ROOT", project)
        monkeypatch.setattr(
            delivery, "PROFILE_PATH", project / ".changerail/profile.toml"
        )
        monkeypatch.setattr(delivery, "RUNTIME_ROOT", project / ".runtime/changerail")
        run = delivery.RUNTIME_ROOT / "runs" / "frozen"
        with pytest.raises((delivery.DeliveryError, FileNotFoundError)):
            delivery.require_frozen_execution(run)
        assert (run / "run.json").read_bytes() == snapshots[project]
