"""Offline transition regressions using independent full Git project fixtures."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import distribution as dist
from scripts.changerail import release_executor as engine
from scripts.changerail import release_update as update


def git(root, *args):
    return (
        subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.PIPE, umask=0o022
        )
        .decode()
        .strip()
    )


def put(root, name, text, mode=0o644):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(mode)
    return path


def commit(root, message):
    git(root, "add", ".")
    git(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def assets(root, directory, tag):
    directory.mkdir()
    version = json.loads((root / "distribution.json").read_text())["version"]
    archive = directory / f"changerail-{version}-runtime.tar.gz"
    built = dist.build(root, archive)
    provenance = directory / "release-provenance.json"
    provenance.write_bytes(
        engine.encoded(
            {
                "schema": "changerail.release-provenance.v1",
                "version": version,
                "planned_tag": tag,
                "source_commit": git(root, "rev-parse", "HEAD"),
                "source_tree": git(root, "rev-parse", "HEAD^{tree}"),
                "archive": archive.name,
                "archive_sha256": built["sha256"],
                "payload_sha256": built["payload_sha256"],
                "source_url": "https://example.invalid/operator-selected-release",
            }
        )
    )
    return archive, provenance


def group_source_modes(root):
    """Real working-tree permissions independent of Git's normalized modes."""
    for name, entry in update._inventory(root).items():
        if update._under(name, update.PROTECTED):
            continue
        if "sha256" in entry or entry.get("directory"):
            (root / name).chmod(0o775 if entry["mode"] & 0o111 else 0o664)


@pytest.fixture
def release(tmp_path, monkeypatch, request):
    options = getattr(request, "param", {})
    monkeypatch.delenv(engine.USE_FD, raising=False)
    root = tmp_path / "executor"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Release fixture")
    required = engine.REQUIRED | {
        "tools/openspec/package.json",
        "scripts/changerail/product.py",
        "scripts/changerail/release_update.py",
        # A release fixture includes every closed execution tree; H1's strict
        # inventory must not treat absent schema/skill directories as empty.
        "tools/changerail/schemas/fixture.json",
        "tools/changerail/skills/fixture/SKILL.md",
    }
    for name in required:
        put(
            root,
            name,
            "# runtime fixture\n",
            0o755 if name.startswith("bin/") else 0o644,
        )
    put(root, "tools/changerail/schemas/fixture.json", "{}\n")
    put(root, "tools/openspec/package-lock.json", '{"lockfileVersion": 3}\n')
    put(root, "tools/openspec/package.json", '{"name": "fixture"}\n')
    config = {
        "schema": "changerail.distribution-config.v1",
        "version": "1.0.0",
        "execution_contract": "changerail.native.v1",
        "provenance": {"owner": "fixture"},
        "files": sorted(required),
        "trees": {},
    }
    put(root, "distribution.json", json.dumps(config))
    # This is a full source checkout: project settings, docs, tests and historical
    # board exist outside archive ownership; they must never become install payload.
    put(root, "README.md", "source repository\n")
    put(root, "docs/guide.md", "guide\n")
    put(
        root,
        "tools/changerail/tests/test_product.py",
        "def test_product(): assert True\n",
    )
    put(root, "pyproject.toml", "[project]\nname = 'fixture'\nversion = '1'\n")
    put(root, "openspec/board/old.md", "immutable historical card\n")
    put(root, "openspec/changes/old/tasks.md", "old tasks\n")
    put(root, "openspec/specs/spec.md", "old specs\n")
    put(root, "openspec/config.yaml", "schema: openspec-v1\n")
    put(root, "bin/codex", "#!/bin/sh\necho old published launcher\n", 0o755)
    put(root, ".changerail/profile.toml", "old published profile\n")
    put(root, ".codex/config.toml", "old published defaults\n")
    put(root, ".gitignore", ".runtime/\n.venv/\n*.local\n")
    first = commit(root, "first source release")
    git(root, "tag", "v1.0.0")
    archive, provenance = assets(root, tmp_path / "assets-1", "v1.0.0")
    dep = put(root, ".venv/dependency", "installed dependency one\n")
    (root / ".venv/bin").mkdir()
    (root / ".venv/bin/python").symlink_to(Path(sys.executable).resolve())

    def dependencies(root, *, node, **_):
        target = Path(sys.executable).resolve()
        return {
            "node": {"path": str(node)},
            "python": {"target": str(target), "file": engine._entry(target)},
            "fixture_sha256": engine.digest((root / ".venv/dependency").read_bytes()),
        }

    monkeypatch.setattr(engine, "dependency_inventory", dependencies)
    if options.get("group_writable"):
        group_source_modes(root)
    bootstrap = tmp_path / "bootstrap"
    update.prepare(
        root,
        archive=archive,
        provenance=provenance,
        tag="v1.0.0",
        proposal=bootstrap,
        node=Path(sys.executable),
        bootstrap=True,
    )
    update.apply(bootstrap)
    old_receipt = engine.receipt_path(root).read_bytes()
    config["version"] = "2.0.0"
    put(root, "distribution.json", json.dumps(config))
    put(
        root,
        "scripts/changerail/product.py",
        "# next runtime\n",
        0o755 if options.get("exec_transition") == "enable" else 0o644,
    )
    put(
        root,
        "bin/chrl",
        "#!/bin/sh\n# next release launcher\n",
        0o644 if options.get("exec_transition") == "disable" else 0o755,
    )
    put(root, "docs/guide.md", "updated guide\n")
    (root / "openspec/board/old.md").unlink()
    put(root, "openspec/board/archive/old.md", "published archived card\n")
    put(root, "openspec/specs/spec.md", "published updated specs\n")
    (root / "openspec/changes/old/tasks.md").unlink()
    put(root, "openspec/changes/new/tasks.md", "published new tasks\n")
    put(root, "openspec/config.yaml", "published: new configuration\n")
    put(root, "bin/codex", "#!/bin/sh\necho new published launcher\n", 0o755)
    put(root, ".changerail/profile.toml", "new published profile\n")
    put(root, ".codex/config.toml", "new published defaults\n")
    second = commit(root, "second source release")
    git(root, "tag", "v2.0.0")
    archive, provenance = assets(root, tmp_path / "assets-2", "v2.0.0")
    git(root, "switch", "--detach", "v1.0.0")
    if options.get("group_writable"):
        group_source_modes(root)
    put(root, ".changerail/profile.toml", "local settings\n")
    put(root, ".codex/config.toml", "local model settings\n")
    put(root, "bin/codex", "#!/bin/sh\nexit 0\n", 0o755)
    put(root, ".runtime/changerail/runs/old/run.json", '{"reviews": 2}\n', 0o444)
    put(root, "openspec/board/old.md", "local historical card\n", 0o444)
    put(root, "README.md", "unrelated staged source change\n")
    git(root, "add", "README.md")
    put(root, "notes.local", "ignored operator content\n")
    (root / "unrelated-link").symlink_to("notes.local")
    if options.get("group_writable"):
        group_source_modes(root)
    proposal = tmp_path / "update"
    return {
        "root": root,
        "first": first,
        "second": second,
        "archive": archive,
        "provenance": provenance,
        "proposal": proposal,
        "node": Path(sys.executable),
        "tag": "v2.0.0",
        "old_receipt": old_receipt,
        "dep": dep,
    }


def prepare(release):
    return update.prepare(
        **{
            k: release[k]
            for k in ("root", "archive", "provenance", "tag", "proposal", "node")
        }
    )


def test_exact_transition_preserves_full_local_inventory_and_is_idempotent(release):
    r = release
    before = update._inventory(r["root"])
    prepare(r)
    assert update._inventory(r["root"]) == before  # prepare never changes target
    assert not update.maintenance_path(r["root"]).exists()
    inode = engine.lock_path(r["root"]).stat().st_ino
    result = update.apply(r["proposal"])
    assert result["phase"] == "accepted"
    assert git(r["root"], "rev-parse", "HEAD") == r["second"]
    value = json.loads((r["proposal"] / "proposal.json").read_text())
    assert update._inventory(r["root"]) == value["after"]
    for name in before.keys() - set(value["changed"]):
        assert update._inventory(r["root"])[name] == before[name]
    assert [
        n
        for n in git(r["root"], "diff", "--cached", "--name-only").splitlines()
        if not update._under(n, update.PROTECTED)
    ] == ["README.md"]
    assert (r["proposal"] / "before-receipt.json").read_bytes() == r["old_receipt"]
    current = engine.receipt_path(r["root"]).read_bytes()
    assert update.apply(r["proposal"]) == result
    assert update.reconcile(r["proposal"]) == result
    assert engine.receipt_path(r["root"]).read_bytes() == current
    assert engine.lock_path(r["root"]).stat().st_ino == inode
    assert not update.maintenance_path(r["root"]).exists()


@pytest.mark.parametrize(
    "boundary", ["intent", "checkout", "receipt-intent", "receipt", "final-state"]
)
def test_crash_boundaries_keep_fence_and_resume_same_intent(
    release, monkeypatch, boundary
):
    r = release
    prepare(r)
    original_write, original_git = update._write, update._git

    def interrupted_write(path, data, **kwargs):
        original_write(path, data, **kwargs)
        if (
            (boundary == "intent" and path == update.maintenance_path(r["root"]))
            or (boundary == "receipt-intent" and path.name == "accepted-receipt.json")
            or (boundary == "receipt" and path == engine.receipt_path(r["root"]))
            or (
                boundary == "final-state"
                and path.name == "state.json"
                and json.loads(data)["phase"] == "accepted"
            )
        ):
            raise RuntimeError("simulated process loss")

    def interrupted_git(root, *args, **kwargs):
        result = original_git(root, *args, **kwargs)
        if boundary == "checkout" and args[0] == "update-ref":
            raise RuntimeError("simulated process loss")
        return result

    monkeypatch.setattr(update, "_write", interrupted_write)
    monkeypatch.setattr(update, "_git", interrupted_git)
    with pytest.raises(RuntimeError, match="process loss"):
        update.apply(r["proposal"])
    assert update.maintenance_path(r["root"]).exists()
    assert engine.receipt_path(r["root"]).exists()  # never disable old authority
    assert (
        r["root"] / ".runtime/changerail/runs/old/run.json"
    ).read_text() == '{"reviews": 2}\n'
    monkeypatch.setattr(update, "_write", original_write)
    monkeypatch.setattr(update, "_git", original_git)
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    assert not update.maintenance_path(r["root"]).exists()


@contextmanager
def subprocess_lease(root, *, legacy=False):
    if legacy:
        code = "import fcntl,sys; f=open(sys.argv[1],'a+'); fcntl.flock(f,fcntl.LOCK_EX); print('ready',flush=True); sys.stdin.readline()"
        target = root / ".runtime/changerail/delivery.lock"
    else:
        code = "import sys; from pathlib import Path; from scripts.changerail import release_executor as e; e.ensure_use(Path(sys.argv[1])); print('ready',flush=True); sys.stdin.readline()"
        target = root
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", code, str(target)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout.readline().strip() == "ready"
        yield
    finally:
        child.communicate("done\n", timeout=10)
        assert child.returncode == 0


@pytest.mark.parametrize("legacy", [False, True])
def test_live_subprocess_lease_rejects_update_before_mutation(release, legacy):
    r = release
    prepare(r)
    before = update._inventory(r["root"])
    with subprocess_lease(r["root"], legacy=legacy):
        with pytest.raises(ValueError, match="in use|live legacy"):
            update.apply(r["proposal"])
        assert git(r["root"], "rev-parse", "HEAD") == r["first"]
        assert update._inventory(r["root"]) == before
        assert engine.receipt_path(r["root"]).read_bytes() == r["old_receipt"]
        assert not update.maintenance_path(r["root"]).exists()
    assert update.apply(r["proposal"])["phase"] == "accepted"


def test_unlocked_internal_apply_refused(release):
    prepare(release)
    root, value, identity = update._load(release["proposal"])
    with pytest.raises(update.ReleaseUpdateError, match="exclusive lease"):
        update._advance(release["proposal"], root, value, identity)
    assert not update.maintenance_path(root).exists()


@pytest.mark.parametrize(
    "tamper", ["archive", "provenance", "tag", "source", "index", "ignored", "proposal"]
)
def test_changed_inputs_fail_closed_before_mutation(release, tamper):
    r = release
    prepare(r)
    if tamper == "archive":
        with r["archive"].open("ab") as stream:
            stream.write(b"tampered")
    elif tamper == "provenance":
        data = json.loads(r["provenance"].read_text())
        data["source_tree"] = "0" * 40
        r["provenance"].write_text(json.dumps(data))
    elif tamper == "tag":
        git(r["root"], "tag", "-f", r["tag"], r["first"])
    elif tamper == "source":
        put(r["root"], "scripts/changerail/product.py", "injected\n")
    elif tamper == "index":
        git(r["root"], "add", "openspec/board/old.md")
    elif tamper == "ignored":
        put(r["root"], "notes.local", "concurrent local edit\n")
    else:
        # Freeze first, fail before Git, then edit original proposal.
        root, value, identity = update._load(r["proposal"])
        update._write(r["proposal"] / "intent.json", engine.encoded(value), new=True)
        update._write(update.maintenance_path(root), engine.encoded(identity), new=True)
        value["node"] = "/different/node"
        (r["proposal"] / "proposal.json").write_bytes(engine.encoded(value))
    with pytest.raises(ValueError):
        update.apply(r["proposal"])
    assert git(r["root"], "rev-parse", "HEAD") == r["first"]
    assert engine.receipt_path(r["root"]).read_bytes() == r["old_receipt"]


def test_dirty_executable_is_not_accepted_as_preserved_overlay(release):
    # This launcher is outside the release delta: rejection must come from the
    # runtime inventory, not the earlier changed-source overlap check.
    put(release["root"], "bin/openspec", "#!/bin/sh\necho injected\n", 0o755)
    with pytest.raises(ValueError, match="runtime differs"):
        prepare(release)
    assert not release["proposal"].exists()


def new_release(release, changes):
    r = release
    # Save local overlays through a separate disposable release-builder clone;
    # updater never stashes or invokes a package/dependency manager.
    builder = r["root"].parent / "builder"
    subprocess.run(["git", "clone", "-q", str(r["root"]), str(builder)], check=True)
    git(builder, "config", "user.email", "fixture@example.invalid")
    git(builder, "config", "user.name", "fixture")
    git(builder, "switch", "--detach", "v2.0.0")
    for name, data in changes.items():
        if data is None:
            (builder / name).unlink()
        else:
            put(builder, name, data)
        git(builder, "add", "-f", "--", name)
    commit(builder, "third release")
    git(builder, "tag", "v3.0.0")
    git(r["root"], "fetch", str(builder), "refs/tags/v3.0.0:refs/tags/v3.0.0")
    archive, provenance = assets(builder, r["root"].parent / "assets-3", "v3.0.0")
    r.update(archive=archive, provenance=provenance, tag="v3.0.0")


@pytest.mark.parametrize(
    "overlap",
    ["openspec/board/old.md", ".codex/config.toml", "bin/codex", "notes.local"],
)
def test_protected_release_delta_preserved_but_local_source_collision_refused(
    release, overlap
):
    new_release(release, {overlap: "incoming release file\n"})
    before = update._inventory(release["root"])
    if overlap == "notes.local":
        with pytest.raises(update.ReleaseUpdateError, match="overlap"):
            prepare(release)
        assert update._inventory(release["root"]) == before
    else:
        prepare(release)
        assert update.apply(release["proposal"])["phase"] == "accepted"
        after = update._inventory(release["root"])
        assert {
            n: e for n, e in after.items() if update._under(n, update.PROTECTED)
        } == {n: e for n, e in before.items() if update._under(n, update.PROTECTED)}


@pytest.mark.parametrize("release", [{}, {"group_writable": True}], indirect=True)
def test_dependency_update_requires_separate_exclusive_provisioning_and_reconcile(
    release,
):
    r = release
    new_release(
        r,
        {
            "pyproject.toml": "[project]\nname='fixture'\nversion='2'\ndependencies=['new-dep']\n"
        },
    )
    assert prepare(r)["requires_provisioning"]
    with pytest.raises(update.ProvisioningRequired):
        update.apply(r["proposal"])
    assert update.maintenance_path(r["root"]).exists()
    assert engine.receipt_path(r["root"]).read_bytes() == r["old_receipt"]
    before = update._inventory(r["root"])
    # The CLI/API executes no provisioning command. Operator work owns these bytes.
    with update.provisioning(r["proposal"]):
        r["dep"].write_text("explicitly provisioned dependency two\n")
        with pytest.raises(ValueError, match="updating|in use"):
            with engine.exclusive_use(r["root"]):
                pass
    assert update._inventory(r["root"]) == before
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    accepted = engine.document(engine.receipt_path(r["root"]))
    assert accepted["dependencies"]["fixture_sha256"] == engine.digest(
        r["dep"].read_bytes()
    )


def test_interrupted_provisioning_cannot_be_accepted_until_explicit_completion(release):
    r = release
    new_release(
        r, {"tools/openspec/package-lock.json": '{"lockfileVersion":3,"new":true}\n'}
    )
    prepare(r)
    with pytest.raises(update.ProvisioningRequired):
        update.apply(r["proposal"])
    with pytest.raises(RuntimeError):
        with update.provisioning(r["proposal"]):
            r["dep"].write_text("partial dependency\n")
            raise RuntimeError("operator provisioning failed")
    with pytest.raises(update.ProvisioningRequired):
        update.reconcile(r["proposal"])
    assert update.maintenance_path(r["root"]).exists()
    with update.provisioning(r["proposal"]):
        r["dep"].write_text("complete dependency\n")
    assert update.reconcile(r["proposal"])["phase"] == "accepted"


def test_mixed_checkout_after_crash_is_not_repaired_by_overwriting_history(
    release, monkeypatch
):
    prepare(release)
    original = update._transition_step

    def interrupted(root, *args):
        put(root, "scripts/changerail/product.py", "partial Git checkout\n")
        raise RuntimeError("checkout interrupted")

    monkeypatch.setattr(update, "_transition_step", interrupted)
    with pytest.raises(RuntimeError):
        update.apply(release["proposal"])
    monkeypatch.setattr(update, "_transition_step", original)
    before = update._inventory(release["root"])
    with pytest.raises(update.ReleaseUpdateError, match="exact retained before/after"):
        update.reconcile(release["proposal"])
    assert update._inventory(release["root"]) == before
    assert update.maintenance_path(release["root"]).exists()


def test_proposal_inside_target_is_refused(release):
    release["proposal"] = release["root"] / ".runtime/proposal"
    with pytest.raises(update.ReleaseUpdateError, match="outside target"):
        prepare(release)


@pytest.mark.parametrize("corruption", ["bytes", "mode", "names", "schema", "version"])
def test_self_consistent_artifact_cannot_substitute_committed_payload(
    release, corruption
):
    r = release
    builder = r["root"].parent / "counterfeit-builder"
    subprocess.run(
        ["git", "clone", "-q", str(r["root"]), str(builder)], check=True, umask=0o022
    )
    git(builder, "switch", "--detach", "v2.0.0")
    if corruption == "bytes":
        put(builder, "scripts/changerail/product.py", "# changed artifact body\n")
    elif corruption == "mode":
        (builder / "scripts/changerail/product.py").chmod(0o755)
    elif corruption == "names":
        config = json.loads((builder / "distribution.json").read_text())
        config["files"].remove("scripts/changerail/product.py")
        put(builder, "distribution.json", json.dumps(config))
    archive, provenance = assets(
        builder, r["root"].parent / "counterfeit-assets", "v2.0.0"
    )
    if corruption in {"schema", "version"}:
        record = json.loads(provenance.read_text())
        record[corruption] = "untrusted-value"
        provenance.write_text(json.dumps(record))
    r.update(archive=archive, provenance=provenance)
    with pytest.raises(ValueError, match="archive|provenance"):
        prepare(r)
    assert git(r["root"], "rev-parse", "HEAD") == r["first"]


def test_initial_unprovisioned_bootstrap_has_explicit_provisioning_path(release):
    r = release
    root = r["root"].parent / "unaccepted"
    subprocess.run(
        ["git", "clone", "-q", str(r["root"]), str(root)], check=True, umask=0o022
    )
    git(root, "switch", "--detach", "v2.0.0")
    proposal = r["root"].parent / "new-bootstrap"
    update.prepare(
        root,
        archive=r["archive"],
        provenance=r["provenance"],
        tag="v2.0.0",
        proposal=proposal,
        node=r["node"],
        bootstrap=True,
    )
    with pytest.raises(FileNotFoundError):
        update.apply(proposal)
    assert update.maintenance_path(root).exists()
    assert not engine.receipt_path(root).exists()
    with update.provisioning(proposal):
        put(root, ".venv/dependency", "operator provisioned bootstrap\n")
        (root / ".venv/bin").mkdir()
        (root / ".venv/bin/python").symlink_to(Path(sys.executable).resolve())
    with pytest.raises(update.ReleaseUpdateError, match="already recorded"):
        with update.provisioning(proposal):
            pytest.fail("completed provisioning must not be overwritten")
    assert update.reconcile(proposal)["phase"] == "accepted"


def test_empty_ignored_directory_collision_is_not_discarded(release):
    new_release(release, {"empty.local": "incoming file\n"})
    path = release["root"] / "empty.local"
    path.mkdir()
    with pytest.raises(update.ReleaseUpdateError, match="overlap"):
        prepare(release)
    assert path.is_dir()


def test_changed_interpreter_is_rejected_before_inventory_probe(release, monkeypatch):
    prepare(release)
    link = release["root"] / ".venv/bin/python"
    link.unlink()
    malicious = put(
        release["root"], ".venv/bin/fake-python", "#!/bin/sh\nexit 1\n", 0o755
    )
    link.symlink_to(malicious)

    def forbidden_probe(*args, **kwargs):
        pytest.fail("tampered interpreter must not be executed by dependency inventory")

    monkeypatch.setattr(engine, "dependency_inventory", forbidden_probe)
    with pytest.raises(ValueError, match="Python.*(changed|differs)"):
        update.apply(release["proposal"])
    assert not update.maintenance_path(release["root"]).exists()


def test_new_explicit_node_path_uses_separate_provisioning_acceptance(release):
    r = release
    r["node"] = put(
        r["root"].parent, "separately-provisioned-node", "fixture node\n", 0o755
    )
    assert prepare(r)["requires_provisioning"]
    with pytest.raises(update.ProvisioningRequired):
        update.apply(r["proposal"])
    with update.provisioning(r["proposal"]):
        pass  # Operator already provisioned the external Node before prepare.
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    assert engine.document(engine.receipt_path(r["root"]))["dependencies"]["node"][
        "path"
    ] == str(r["node"])


def test_partial_clone_requires_explicit_separate_object_retrieval(release):
    git(release["root"], "config", "remote.origin.promisor", "true")
    with pytest.raises(update.ReleaseUpdateError, match="fetch objects separately"):
        prepare(release)
    assert not release["proposal"].exists()


def test_completed_proposal_rejects_receipt_permission_tampering(release):
    prepare(release)
    update.apply(release["proposal"])
    path = engine.receipt_path(release["root"])
    path.chmod(0o666)
    with pytest.raises(update.ReleaseUpdateError, match="ownership/mode"):
        update.reconcile(release["proposal"])


def protected_snapshot(root):
    entries = {
        n: e
        for n, e in update._inventory(root).items()
        if update._under(n, update.PROTECTED)
    }
    return {
        n: {
            "entry": entry,
            "inode": (root / n).lstat().st_ino,
            "mtime_ns": (root / n).lstat().st_mtime_ns,
            "ctime_ns": (root / n).lstat().st_ctime_ns,
            "bytes": ((root / n).read_bytes().hex() if "sha256" in entry else None),
        }
        for n, entry in entries.items()
    }


def protected_index(root):
    return [
        row
        for row in update._git(root, "ls-files", "--stage", "-z").split(b"\0")
        if row and update._under(row.split(b"\t", 1)[1].decode(), update.PROTECTED)
    ]


def local_overlay(release):
    root = release["root"]
    # Unstaged absence of a tracked path and a staged deletion both survive.
    (root / "openspec/specs/spec.md").unlink()
    git(root, "rm", "--cached", "--", "openspec/changes/old/tasks.md")
    # A new release path has a local untracked counterpart with arbitrary bytes.
    raw = put(root, "openspec/changes/new/tasks.md", "placeholder")
    raw.write_bytes(b"\xff\x00local task history\r\n")
    raw.chmod(0o440)
    # Modified/staged protected row differs from both release commits.
    put(root, "openspec/config.yaml", "local: staged configuration\n")
    git(root, "add", "openspec/config.yaml")
    (root / "openspec/empty-local").mkdir(mode=0o750)
    # A legitimate local launcher link may escape checkout. It is not followed,
    # copied, replaced or normalized by the source transaction.
    external = put(root.parent, "operator-launcher", "#!/bin/sh\nexit 0\n", 0o700)
    (root / "bin/codex").unlink()
    (root / "bin/codex").symlink_to(external)
    (root / "openspec/history-link").symlink_to("changes/new/tasks.md")
    return protected_snapshot(root), protected_index(root)


@pytest.mark.parametrize(
    "boundary",
    [
        "source-before",
        "source-after",
        "index-before",
        "index-after",
        "head-before",
        "head-after",
    ],
)
def test_normal_release_overlay_is_untouched_across_every_transaction_boundary(
    release, monkeypatch, boundary
):
    r = release
    before, before_index = local_overlay(r)
    prepare(r)
    proposal = json.loads((r["proposal"] / "proposal.json").read_text())
    assert "openspec/board/archive/old.md" in proposal["protected_release_delta"]
    assert "bin/codex" in proposal["protected_release_delta"]
    assert all(
        not update._under(step.get("name", ""), update.PROTECTED)
        for step in proposal["transaction"]
    )
    original = update._transition_step
    kind, timing = boundary.split("-")

    def interrupt(root, proposal_path, value, step):
        assert protected_snapshot(root) == before
        assert protected_index(root) == before_index
        if step["kind"] == kind and timing == "before":
            raise RuntimeError("boundary crash")
        original(root, proposal_path, value, step)
        assert protected_snapshot(root) == before
        assert protected_index(root) == before_index
        if step["kind"] == kind and timing == "after":
            raise RuntimeError("boundary crash")

    monkeypatch.setattr(update, "_transition_step", interrupt)
    with pytest.raises(RuntimeError, match="boundary crash"):
        update.apply(r["proposal"])
    assert update.maintenance_path(r["root"]).exists()
    with pytest.raises(engine.ReleaseExecutorError, match="maintenance"):
        engine.verify_release(r["root"])
    assert engine.receipt_path(r["root"]).read_bytes() == r["old_receipt"]
    monkeypatch.setattr(update, "_transition_step", original)
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    assert git(r["root"], "rev-parse", "HEAD") == r["second"]
    assert (r["root"] / ".git/HEAD").read_text() == r["second"] + "\n"
    assert (
        r["root"] / "scripts/changerail/product.py"
    ).read_text() == "# next runtime\n"
    assert protected_snapshot(r["root"]) == before
    assert protected_index(r["root"]) == before_index
    assert not os.path.lexists(r["root"] / "openspec/specs/spec.md")
    assert not os.path.lexists(r["root"] / "openspec/board/archive")
    assert (r["proposal"] / "before-receipt.json").read_bytes() == r["old_receipt"]
    receipt = engine.receipt_path(r["root"]).read_bytes()
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    assert protected_snapshot(r["root"]) == before
    assert engine.receipt_path(r["root"]).read_bytes() == receipt


def test_source_directory_addition_and_deletion_resume_without_touching_protected_tree(
    release, monkeypatch
):
    r = release
    new_release(
        r, {"docs/new/nested/guide.md": "new release guide\n", "docs/guide.md": None}
    )
    before, before_index = local_overlay(r)
    prepare(r)
    original = update._transition_step

    def interrupt(root, proposal, value, step):
        original(root, proposal, value, step)
        if step["kind"] == "directory":
            raise RuntimeError("directory published before progress")

    monkeypatch.setattr(update, "_transition_step", interrupt)
    with pytest.raises(RuntimeError):
        update.apply(r["proposal"])
    monkeypatch.setattr(update, "_transition_step", original)
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    assert (r["root"] / "docs/new/nested/guide.md").read_text() == "new release guide\n"
    assert not (r["root"] / "docs/guide.md").exists()
    assert protected_snapshot(r["root"]) == before
    assert protected_index(r["root"]) == before_index


def test_unrelated_new_history_after_interruption_is_retained_and_blocks_reconcile(
    release, monkeypatch
):
    r = release
    prepare(r)
    original = update._transition_step

    def interrupt(root, proposal, value, step):
        original(root, proposal, value, step)
        raise RuntimeError("source step interrupted")

    monkeypatch.setattr(update, "_transition_step", interrupt)
    with pytest.raises(RuntimeError):
        update.apply(r["proposal"])
    new_history = put(
        r["root"], ".runtime/changerail/runs/new/receipt.json", "new retained receipt\n"
    )
    monkeypatch.setattr(update, "_transition_step", original)
    with pytest.raises(update.ReleaseUpdateError, match="exact retained before/after"):
        update.reconcile(r["proposal"])
    assert new_history.read_text() == "new retained receipt\n"
    assert update.maintenance_path(r["root"]).exists()


def test_bootstrap_refuses_pre_feature_release_even_with_valid_local_assets(release):
    r = release
    config = json.loads((r["root"] / "distribution.json").read_text())
    config["files"].remove("scripts/changerail/release_update.py")
    config["files"].remove("scripts/changerail/release_executor.py")
    new_release(
        r,
        {
            "distribution.json": json.dumps(config),
            "scripts/changerail/release_update.py": None,
            "scripts/changerail/release_executor.py": None,
        },
    )
    old = r["root"].parent / "pre-feature-checkout"
    subprocess.run(
        ["git", "clone", "-q", str(r["root"]), str(old)], check=True, umask=0o022
    )
    git(old, "switch", "--detach", r["tag"])
    with pytest.raises(
        update.ReleaseUpdateError, match="update old checkout separately first"
    ):
        update.prepare(
            old,
            archive=r["archive"],
            provenance=r["provenance"],
            tag=r["tag"],
            proposal=r["proposal"],
            node=r["node"],
            bootstrap=True,
        )
    assert not update.maintenance_path(old).exists()
    assert not engine.receipt_path(old).exists()


@pytest.mark.parametrize("release", [{"group_writable": True}], indirect=True)
@pytest.mark.parametrize("fault", ["chmod", "source", "index"])
def test_group_writable_checkout_preserves_permissions_and_recovers_exactly(
    release, monkeypatch, fault
):
    r = release
    local_overlay(r)
    (r["root"] / "openspec/changes/new/tasks.md").chmod(0o664)
    protected, index = protected_snapshot(r["root"]), protected_index(r["root"])
    before = update._inventory(r["root"])
    prepare(r)
    value = engine.document(r["proposal"] / "proposal.json")
    assert value["before"]["bin/chrl"]["mode"] == 0o775
    assert value["after"]["bin/chrl"]["mode"] == 0o775
    assert value["after"]["scripts/changerail/product.py"]["mode"] == 0o664
    assert value["after"]["distribution.json"]["mode"] == 0o664
    unchanged = {
        n: (entry, (r["root"] / n).lstat())
        for n, entry in before.items()
        if n not in value["changed"]
    }
    real_chmod, real_step = os.fchmod, update._transition_step

    def fail_chmod(fd, mode):
        real_chmod(fd, mode)
        if mode == 0o775:
            raise RuntimeError("fault after staging chmod")

    def fail_step(root, proposal, value, step):
        real_step(root, proposal, value, step)
        if step["kind"] == fault:
            raise RuntimeError("fault after atomic publication")

    with monkeypatch.context() as patch:
        if fault == "chmod":
            patch.setattr(update.os, "fchmod", fail_chmod)
        else:
            patch.setattr(update, "_transition_step", fail_step)
        with pytest.raises(RuntimeError, match="fault"):
            update.apply(r["proposal"])
    assert update.maintenance_path(r["root"]).exists()
    assert protected_snapshot(r["root"]) == protected
    assert protected_index(r["root"]) == index
    if fault == "chmod":
        assert (
            update._inventory(r["root"]) == before
        )  # staged chmod never reached target
    assert update.reconcile(r["proposal"])["phase"] == "accepted"
    after = update._inventory(r["root"])
    assert after == value["after"]
    assert git(r["root"], "rev-parse", "HEAD") == r["second"]
    assert protected_snapshot(r["root"]) == protected
    assert protected_index(r["root"]) == index
    for name, (entry, info) in unchanged.items():
        actual = (r["root"] / name).lstat()
        assert after[name] == entry
        assert (actual.st_ino, actual.st_mode) == (info.st_ino, info.st_mode)
        if entry.get("directory") and any(n.startswith(name + "/") for n in value["changed"]):
            # Replacing a child necessarily changes its parent's timestamps;
            # that directory's identity/mode remain intact. Protected directories
            # have no changed source children and retain all timestamps above.
            continue
        assert (
            actual.st_ino,
            actual.st_mode,
            actual.st_mtime_ns,
            actual.st_ctime_ns,
        ) == (info.st_ino, info.st_mode, info.st_mtime_ns, info.st_ctime_ns)
    accepted = engine.document(engine.receipt_path(r["root"]))
    assert accepted["distribution"]["files"]["bin/chrl"]["mode"] == 0o775
    assert accepted["distribution"]["files"]["distribution.json"]["mode"] == 0o664
    assert update.reconcile(r["proposal"])["phase"] == "accepted"


@pytest.mark.parametrize("release", [{"group_writable": True}], indirect=True)
@pytest.mark.parametrize("drift", ["added-execute", "removed-execute", "content"])
def test_group_write_does_not_waive_source_content_or_executable_drift(release, drift):
    root = release["root"]
    if drift == "added-execute":
        (root / "scripts/changerail/product.py").chmod(0o775)
    elif drift == "removed-execute":
        (root / "bin/chrl").chmod(0o664)
    else:
        with (root / "scripts/changerail/product.py").open("ab") as stream:
            stream.write(b"local content change\n")
    with pytest.raises(update.ReleaseUpdateError, match="overlap"):
        prepare(release)
    assert not update.maintenance_path(root).exists()


@pytest.mark.parametrize("release", [{"group_writable": True}], indirect=True)
def test_chmod_after_prepare_is_exact_journal_drift(release):
    prepare(release)
    path = release["root"] / "scripts/changerail/product.py"
    path.chmod(0o644)  # Same Git semantics, different retained actual permissions.
    with pytest.raises(update.ReleaseUpdateError, match="exact retained before/after"):
        update.apply(release["proposal"])
    assert path.stat().st_mode & 0o777 == 0o644
    assert not update.maintenance_path(release["root"]).exists()


@pytest.mark.parametrize(
    "release",
    [
        {"group_writable": True, "exec_transition": "enable"},
        {"group_writable": True, "exec_transition": "disable"},
    ],
    indirect=True,
)
def test_release_executable_change_preserves_checkout_read_write_permissions(
    release, request
):
    prepare(release)
    value = engine.document(release["proposal"] / "proposal.json")
    assert update.apply(release["proposal"])["phase"] == "accepted"
    root = release["root"]
    assert (root / "scripts/changerail/product.py").stat().st_mode & 0o777 == value[
        "after"
    ]["scripts/changerail/product.py"]["mode"]
    assert (root / "bin/chrl").stat().st_mode & 0o777 == value["after"]["bin/chrl"][
        "mode"
    ]
    assert value["after"]["scripts/changerail/product.py"]["mode"] == (
        0o775
        if request.node.callspec.params["release"]["exec_transition"] == "enable"
        else 0o664
    )
    assert value["after"]["bin/chrl"]["mode"] == (
        0o664
        if request.node.callspec.params["release"]["exec_transition"] == "disable"
        else 0o775
    )
