"""Installed boundaries with real archives, frozen runs and explicit test policy.

Generic archives inject a hash-bound synthetic descriptor only in this test
process; production never accepts them. Separate tests verify actual published
manifests and (when the tag exists locally) install genuine published bytes.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import distribution as dist
from scripts.changerail import local_delivery as delivery
from scripts.changerail import installed_compatibility as compatibility


def admit_synthetic_payload(monkeypatch, root):
    """Test-only policy injection: never a production extension mechanism."""
    lock = json.loads((root / dist.LOCK).read_text())
    monkeypatch.setitem(
        compatibility.REVIEWED_PAYLOADS,
        lock["payload_sha256"],
        {
            "version": lock["version"],
            "archive_sha256": lock["archive_sha256"],
            "identity_shape": "installed-legacy",
            "provenance": "explicit synthetic test descriptor, not a reviewed upstream release",
            "critical_sha256": {
                name: lock["files"][name]["sha256"]
                for name in (
                    "scripts/changerail/local_delivery.py",
                    "scripts/changerail/native_workflow.py",
                    "scripts/changerail/openspec_context.py",
                    "scripts/changerail/openspec_adapter.py",
                )
            },
            "checkpoint_policy": compatibility.CHECKPOINT_POLICY,
        },
    )


@pytest.fixture
def installed(tmp_path, monkeypatch):
    source = tmp_path / "old-source"
    source.mkdir()
    config, files = dist.source_payload(Path(__file__).resolve().parents[3])
    config["version"] = "2.0.0-candidate.5"
    files["distribution.json"] = (dist.encoded(config), 0o644)
    for name, (data, mode) in files.items():
        dist.write_atomic(source / name, data, mode)
    old = tmp_path / "old.tar.gz"
    dist.build(source, old)
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text(".runtime/\n")
    dist.install(root, old)
    admit_synthetic_payload(monkeypatch, root)
    dist.write_atomic(
        root / ".changerail/profile.toml", b'schema="changerail.local-delivery.v1"\n'
    )
    dist.write_atomic(root / "bin/codex", b"#!/bin/sh\nexit 99\n", 0o755)
    for key, value in {
        "REPO_ROOT": root,
        "PROFILE_PATH": root / ".changerail/profile.toml",
        "RUNTIME_ROOT": root / ".runtime/changerail",
    }.items():
        monkeypatch.setattr(delivery, key, value)
    identity = delivery.execution_identity()
    # The historical shape did not freeze these individually; its frozen lock did.
    identity = {
        key: value
        for key, value in identity.items()
        if key != "scripts/__init__.py" and not key.startswith("tools/openspec/")
    }
    original = root / ".runtime/changerail/runs/original"
    child = original.with_name("failed-child")
    for run in (original, child):
        run.mkdir(parents=True)
        metadata = {
            "schema": "changerail.delivery-run.v2",
            "run_id": run.name,
            "execution_contract": "changerail.native.v1",
            "lifecycle_mode": "openspec-v1",
            "mode": "delivery",
            "finished_at": "2026-09-10T01:00:00Z",
            "process_identity": identity,
        }
        if run == child:
            metadata["recovery_of"] = original.name
        dist.write_atomic(run / "run.json", dist.encoded(metadata))
    dist.write_atomic(
        original / "focused-evidence/check.json", b'{"historical": true}\n'
    )
    target = tmp_path / "target.tar.gz"
    dist.build(Path(__file__).resolve().parents[3], target)
    return root, child, target


def authorize_transition(root, transition, proposal):
    parent = {
        "schema": "changerail.plan-restoration.v1",
        "project": str(root),
        "run_id": proposal["run_id"],
        "runtime_transition": proposal,
    }
    raw = dist.encoded(parent)
    dist.write_atomic(transition / "proposal.json", raw)
    dist.write_atomic(
        transition / "apply-intent.json",
        dist.encoded(
            {
                "schema": "changerail.plan-restoration.v1",
                "proposal_sha256": dist.digest(raw),
                "authorized": dist.digest(raw),
            }
        ),
    )


def test_installed_bridge_restores_execution_without_changing_runs(installed):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    before = {
        p: p.read_bytes()
        for p in (root / ".runtime/changerail/runs").rglob("*")
        if p.is_file()
    }
    with pytest.raises(dist.DistributionError, match="frozen run"):
        dist.install(root, archive)
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/fixture"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    result = bridge.apply_transition(delivery, proposal, transition)
    assert (
        bridge.effective_identity(delivery, proposal, transition)
        == delivery.execution_identity()
    )
    assert bridge.apply_transition(delivery, proposal, transition) == result
    assert {p: p.read_bytes() for p in before} == before
    assert not json.loads((root / dist.LOCK).read_text())["retained_read_only_runs"]


@pytest.mark.parametrize(
    "drift",
    [
        "profile",
        "launcher",
        "omitted-runtime",
        "unrelated-run",
        "read-only",
        "unknown-version",
    ],
)
def test_installed_bridge_rejects_incompatible_predecessor(installed, drift):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    if drift in {"profile", "launcher", "omitted-runtime"}:
        name = {
            "profile": ".changerail/profile.toml",
            "launcher": "bin/codex",
            "omitted-runtime": "tools/openspec/bootstrap.sh",
        }[drift]
        (root / name).write_text("drift\n")
    elif drift == "unrelated-run":
        dist.write_atomic(
            child.with_name("unrelated") / "run.json", (child / "run.json").read_bytes()
        )
    else:
        lock = json.loads((root / dist.LOCK).read_text())
        if drift == "read-only":
            lock["retained_read_only_runs"] = dist.run_inventory(root)
        else:
            lock["version"] = "99.0.0"
        dist.write_atomic(root / dist.LOCK, dist.encoded(lock))
    with pytest.raises((delivery.DeliveryError, dist.DistributionError)):
        bridge.prepare_transition(delivery, child, archive)


@pytest.mark.parametrize("interruption", ["runtime-file", "lock", "after-install"])
def test_installed_bridge_reconciles_only_proven_install_states(
    installed, monkeypatch, interruption
):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/interrupted"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    original = dist.write_atomic
    tripped = False

    def interrupt(path, data, mode=0o644):
        nonlocal tripped
        original(path, data, mode)
        if not tripped and (
            (interruption == "runtime-file" and path == root / "distribution.json")
            or (interruption == "lock" and path == root / dist.LOCK)
        ):
            tripped = True
            raise KeyboardInterrupt("fixture power loss")

    monkeypatch.setattr(dist, "write_atomic", interrupt)
    if interruption != "after-install":
        with pytest.raises(KeyboardInterrupt):
            bridge.apply_transition(delivery, proposal, transition)
    else:
        bridge.apply_transition(delivery, proposal, transition)
    monkeypatch.setattr(dist, "write_atomic", original)
    bridge.apply_transition(delivery, proposal, transition)
    assert (
        bridge.effective_identity(delivery, proposal, transition)
        == delivery.execution_identity()
    )


def test_installed_bridge_rejects_archive_or_payload_drift_after_prepare(installed):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/drift"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    (root / "bin/chrl").write_text("third state\n")
    with pytest.raises(
        (delivery.DeliveryError, dist.DistributionError),
        match="local drift|unexpected bytes",
    ):
        bridge.apply_transition(delivery, proposal, transition)
    assert not (transition / "runtime-intent.json").exists()


def test_installed_bridge_rejects_forged_receipt_and_history_addition(installed):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/history"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    (child / "foreign.json").write_text("{}\n")
    with pytest.raises(
        (delivery.DeliveryError, dist.DistributionError), match="history"
    ):
        bridge.apply_transition(delivery, proposal, transition)


def test_installed_bridge_needs_outer_plan_authority(installed):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/no-authority"
    transition.mkdir(parents=True)
    lock = (root / dist.LOCK).read_bytes()
    with pytest.raises((OSError, dist.DistributionError)):
        bridge.apply_transition(delivery, proposal, transition)
    assert (root / dist.LOCK).read_bytes() == lock
    assert not (transition / "runtime-intent.json").exists()


def test_installed_bridge_archive_substitution_is_rejected_before_writes(installed):
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    proposal = bridge.prepare_transition(delivery, child, archive)
    transition = root / ".runtime/changerail/plan-restorations/archive-drift"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    # A valid but different archive cannot inherit the original hash authority.
    source = archive.parent / "old-source"
    archive.unlink()
    dist.build(source, archive)
    with pytest.raises(
        (delivery.DeliveryError, dist.DistributionError),
        match="target archive changed|target archive differs",
    ):
        bridge.apply_transition(delivery, proposal, transition)
    assert not (transition / "runtime-intent.json").exists()


def test_coherent_unknown_fork_cannot_inherit_published_compatibility(installed):
    """A fork can rewrite its lock and runs consistently without becoming upstream."""
    from scripts.changerail import installed_restoration as bridge

    root, child, archive = installed
    path = root / "scripts/changerail/native_workflow.py"
    path.write_bytes(path.read_bytes() + b"\n# unknown checkpoint semantics fork\n")
    source = archive.parent / "old-source"
    (source / "scripts/changerail/native_workflow.py").write_bytes(path.read_bytes())
    fork_archive = archive.parent / "coherent-fork.tar.gz"
    fork = dist.build(source, fork_archive)
    lock = json.loads((root / dist.LOCK).read_text())
    lock.update(
        files=fork["files"],
        payload_sha256=fork["payload_sha256"],
        archive_sha256=fork["sha256"],
    )
    dist.write_atomic(root / dist.LOCK, dist.encoded(lock))
    identity = delivery.execution_identity()
    identity = {
        key: value
        for key, value in identity.items()
        if key != "scripts/__init__.py" and not key.startswith("tools/openspec/")
    }
    for run in (child, child.with_name("original")):
        metadata = json.loads((run / "run.json").read_text())
        metadata["process_identity"] = identity
        dist.write_atomic(run / "run.json", dist.encoded(metadata))
    with pytest.raises(delivery.DeliveryError, match="reviewed.*payload|compatibility"):
        bridge.prepare_transition(delivery, child, archive)


@pytest.mark.parametrize("version", ["2.0.0-candidate.5", "2.0.0-rc.1", "2.0.0-rc.2"])
def test_exact_upstream_manifest_and_checkpoint_descriptor(version):
    locks = json.loads(
        (Path(__file__).parent / "fixtures/reviewed-installed-locks.json").read_text()
    )
    lock = locks[version]
    descriptor = compatibility.require_reviewed_payload(lock)
    assert descriptor["version"] == version
    assert descriptor["checkpoint_semantics"]["inherited_evidence"].startswith(
        "historical only"
    )
    assert descriptor["checkpoint_semantics"]["review_allowance"].startswith(
        "at most two"
    )
    assert ("pre-release" in descriptor["provenance"]) == ("candidate" in version)
    # Even changing a non-critical tool file invalidates the complete payload pin.
    lock["files"]["tools/changerail/README.md"]["sha256"] = "0" * 64
    lock["payload_sha256"] = dist.digest(dist.encoded(lock["files"]))
    with pytest.raises(delivery.DeliveryError, match="exact reviewed source payload"):
        compatibility.require_reviewed_payload(lock)


def test_genuine_published_archive_installs_with_production_policy(
    tmp_path, monkeypatch
):
    import io
    import tarfile
    from scripts.changerail import installed_restoration as bridge

    source_root = Path(__file__).resolve().parents[3]
    exported = subprocess.run(
        ["git", "archive", "v2.0.0-rc.2"], cwd=source_root, capture_output=True
    )
    if exported.returncode:
        pytest.skip(
            "published tag absent in shallow checkout; exact manifest regression remains mandatory"
        )
    source = tmp_path / "published-source"
    source.mkdir()
    with tarfile.open(fileobj=io.BytesIO(exported.stdout)) as archive:
        # Trusted public Git tag; extract the regular files only, not symlinks.
        for member in archive:
            if member.isdir():
                continue
            assert member.isfile()
            data = archive.extractfile(member).read()
            dist.write_atomic(
                source / dist.safe_name(member.name),
                data,
                0o755 if member.mode & 0o111 else 0o644,
            )
    published = tmp_path / "published.tar.gz"
    result = dist.build(source, published)
    assert (
        result["sha256"]
        == "28aa0d639fa8581cc37c03e8a03b7034123504ac6649f237d8df41ef70a0968a"
    )
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text(".runtime/\n")
    dist.install(root, published)
    dist.write_atomic(
        root / ".changerail/profile.toml", b'schema="changerail.local-delivery.v1"\n'
    )
    dist.write_atomic(root / "bin/codex", b"#!/bin/sh\nexit 99\n", 0o755)
    for key, value in {
        "REPO_ROOT": root,
        "PROFILE_PATH": root / ".changerail/profile.toml",
        "RUNTIME_ROOT": root / ".runtime/changerail",
    }.items():
        monkeypatch.setattr(delivery, key, value)
    identity = delivery.execution_identity()
    original = root / ".runtime/changerail/runs/original"
    child = original.with_name("failed-child")
    for run in (original, child):
        metadata = {
            "schema": "changerail.delivery-run.v2",
            "run_id": run.name,
            "execution_contract": "changerail.native.v1",
            "lifecycle_mode": "openspec-v1",
            "mode": "delivery",
            "finished_at": "2026-09-10T01:00:00Z",
            "process_identity": identity,
        }
        if run == child:
            metadata["recovery_of"] = original.name
        dist.write_atomic(run / "run.json", dist.encoded(metadata))
    target = tmp_path / "target.tar.gz"
    dist.build(source_root, target)
    proposal = bridge.prepare_transition(delivery, child, target)
    assert proposal["compatibility"]["provenance"] == "GitHub release tag v2.0.0-rc.2"
    transition = root / ".runtime/changerail/plan-restorations/published"
    transition.mkdir(parents=True)
    authorize_transition(root, transition, proposal)
    bridge.apply_transition(delivery, proposal, transition)
    assert (
        bridge.effective_identity(delivery, proposal, transition)
        == delivery.execution_identity()
    )


def test_known_payload_cannot_use_unreviewed_checkpoint_semantics(
    installed, monkeypatch
):
    root, child, target = installed
    lock = json.loads((root / dist.LOCK).read_text())
    descriptor = dict(compatibility.REVIEWED_PAYLOADS[lock["payload_sha256"]])
    descriptor["checkpoint_policy"] = "unknown.reset-review-and-trust-checkboxes"
    monkeypatch.setitem(
        compatibility.REVIEWED_PAYLOADS, lock["payload_sha256"], descriptor
    )
    from scripts.changerail import installed_restoration as bridge

    with pytest.raises(delivery.DeliveryError, match="checkpoint policy"):
        bridge.prepare_transition(delivery, child, target)
