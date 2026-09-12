"""Controlled, offline acceptance of an operator-selected release into a Git checkout.

prepare writes only an external proposal. apply/reconcile hold executor then legacy
delivery locks; every incomplete mutation remains fenced by maintenance_path().
The proposal is a retained receipt, not a backup to overlay onto live histories.
Only unprotected release blobs are replaced. Protected worktree entries (including
absence) and index rows never change: no release board is installed even transiently.
An exact per-step journal commits source, preserved-overlay index and detached HEAD
in that order. Local source collisions still require operator resolution.

Dependency provisioning is separate: `provision-lease PROPOSAL` holds maintenance
ownership while the operator provisions .venv / tools/openspec/node_modules from
another shell, then types `done`. No installer/command is executed by this module.
Reconcile requires the exact recorded provisioned inventory. Interrupted provisioning
can be resumed by the same command. Never remove the maintenance marker manually.

Integration requirement: ordinary launchers (including legacy delivery) must reject
maintenance_path(root) BEFORE importing target code, and verify_release must reject
it when accepted=None. Trusted maintenance verification passes accepted explicitly.
Local tag/provenance agreement does NOT prove GitHub publication or authenticity;
the operator chooses the downloaded source of trust. No old-run compatibility is
created. There is intentionally no destructive rollback API.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import fnmatch
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any

import distribution as dist
from scripts.changerail import release_executor as engine

SCHEMA = "changerail.release-update.v1"
PROTECTED = (".changerail", ".codex", ".runtime", "bin/codex", "openspec")
DEPENDENCIES = engine.DEPENDENCY_DIRS
DECLARATIONS = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements*.txt",
    "constraints*.txt",
    "uv.lock",
    "poetry.lock",
    "Pipfile*",
    "tools/openspec/package.json",
    "tools/openspec/package-lock.json",
    "tools/openspec/bootstrap.sh",
)


class ReleaseUpdateError(ValueError):
    """The retained proposal cannot safely authorize this transition."""


class ProvisioningRequired(ReleaseUpdateError):
    """Checkout is maintained; explicitly provision dependencies, then reconcile."""


def maintenance_path(root: Path) -> Path:
    return root.parent / f".{root.name}.release-maintenance.json"


def _under(name: str, roots: tuple[str, ...]) -> bool:
    return any(name == p or name.startswith(p + "/") for p in roots)


def _matches_git_entry(
    actual: dict[str, Any] | None, committed: dict[str, Any] | None
) -> bool:
    """Git records executable semantics, not checkout read/write permission bits.

    Use this ONLY at the Git/archive boundary. Journal and receipt comparisons
    continue to use exact actual modes, so chmod after prepare is still drift.
    """
    if (
        actual is not None
        and committed is not None
        and "sha256" in actual
        and "sha256" in committed
    ):
        return {k: v for k, v in actual.items() if k != "mode"} == {
            k: v for k, v in committed.items() if k != "mode"
        } and bool(actual["mode"] & 0o111) == bool(committed["mode"] & 0o111)
    return actual == committed


def _updated_entry(
    previous: dict[str, Any] | None, committed: dict[str, Any]
) -> dict[str, Any]:
    """Preserve existing ordinary permissions for a replaced regular file.

    If the release changes executable semantics, remove execute bits or grant
    execution to the existing readers. Never transfer setuid/setgid/sticky bits
    onto replacement code. New files/type changes use committed normalized modes.
    Unchanged entries are never republished or chmod-ed.
    """
    result = dict(committed)
    if previous is not None and "sha256" in previous and "sha256" in committed:
        mode = previous["mode"] & 0o777
        executable = bool(committed["mode"] & 0o111)
        if executable != bool(mode & 0o111):
            mode = mode & ~0o111
            if executable:
                mode |= (mode & 0o444) >> 2
                if not mode & 0o111:
                    raise ReleaseUpdateError(
                        "cannot grant release execution to a file with no readers"
                    )
        result["mode"] = mode
    return result


def _git(
    root: Path, *args: str, input: bytes | None = None, index: Path | None = None
) -> bytes:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL="/dev/null",
        GIT_OPTIONAL_LOCKS="0",
        GIT_TERMINAL_PROMPT="0",
        GIT_NO_LAZY_FETCH="1",
    )
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    result = subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "submodule.recurse=false",
            "-c",
            "core.attributesFile=/dev/null",
            "-C",
            str(root),
            *args,
        ],
        env=env,
        capture_output=True,
        check=False,
        umask=0o022,
        input=input,
    )
    if result.returncode:
        raise ReleaseUpdateError(f"Git {args[0]} refused the transition")
    return result.stdout


def _revision(root: Path, ref: str) -> str:
    return _git(root, "rev-parse", "--verify", ref).decode().strip()


def _tree(root: Path, commit: str) -> dict[str, dict[str, Any]]:
    result = {}
    for row in _git(root, "ls-tree", "-rz", commit).split(b"\0"):
        if not row:
            continue
        header, raw_name = row.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = dist.safe_name(raw_name.decode())
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise ReleaseUpdateError(f"unsupported Git entry: {name}")
        data = _git(root, "cat-file", "blob", oid)
        result[name] = (
            {"link": data.decode(), "mode": 0o777}
            if mode == "120000"
            else {
                "sha256": engine.digest(data),
                "size": len(data),
                "mode": 0o755 if mode == "100755" else 0o644,
            }
        )
    return result


def _checkout(root: Path) -> None:
    engine.canonical_root(root)
    if (
        not (root / ".git").is_dir()
        or (root / ".git").is_symlink()
        or (Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()) != root)
    ):
        raise ReleaseUpdateError("existing standalone main Git checkout required")
    config = _git(root, "config", "--local", "--null", "--list").decode().lower()
    if any(
        row.split("\n", 1)[0] == "extensions.partialclone"
        or row.split("\n", 1)[0].endswith(".promisor")
        for row in config.split("\0")
    ):
        raise ReleaseUpdateError(
            "partial/promisor checkout refused; fetch objects separately"
        )
    if _git(root, "rev-parse", "--shared-index-path").strip():
        raise ReleaseUpdateError("split index requires separate operator resolution")
    for name in (
        "index.lock",
        "HEAD.lock",
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "info/sparse-checkout",
        "info/attributes",
    ):
        if os.path.lexists(root / ".git" / name):
            raise ReleaseUpdateError(f"unfinished/unsupported Git state: {name}")
    for row in _git(root, "ls-files", "-v", "-z").split(b"\0"):
        if row and row[:1] != b"H":
            raise ReleaseUpdateError(
                "unmerged, sparse or assume-unchanged index refused"
            )


def _inventory(root: Path) -> dict[str, Any]:
    """Every nondependency worktree entry, including directory modes.

    Dependency directories are separately pinned by engine.dependency_inventory.
    The legacy lock is coordination state; its inode is retained separately.
    """
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for leaf in sorted(dirs + files):
            path = Path(directory) / leaf
            name = path.relative_to(root).as_posix()
            if name == ".git" or _under(name, DEPENDENCIES):
                if leaf in dirs:
                    dirs.remove(leaf)
                continue
            if name == ".runtime/changerail/delivery.lock":
                continue
            info = path.lstat()
            mode = stat.S_IMODE(info.st_mode)
            if stat.S_ISLNK(info.st_mode):
                result[name] = {"link": os.readlink(path), "mode": mode}
            elif stat.S_ISREG(info.st_mode):
                data = engine.regular(path)
                result[name] = {
                    "sha256": engine.digest(data),
                    "size": len(data),
                    "mode": mode,
                }
            elif stat.S_ISDIR(info.st_mode):
                # Coordination parents may be created by the legacy lock owner.
                if name not in {
                    ".runtime",
                    ".runtime/changerail",
                }:
                    result[name] = {"directory": True, "mode": mode}
            else:
                raise ReleaseUpdateError(f"special worktree entry: {name}")
    return result


def _sync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write(path: Path, data: bytes, *, new: bool = False) -> None:
    """Durable owner-only atomic publication; never overwrite an immutable receipt."""
    fd, temporary = tempfile.mkstemp(prefix=".release-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if new:
            os.link(temporary, path, follow_symlinks=False)
            os.unlink(temporary)
        else:
            if path.is_symlink():
                raise ReleaseUpdateError("linked authority refused")
            os.replace(temporary, path)
        _sync_dir(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _json(path: Path) -> dict[str, Any]:
    value = engine.document(path)
    info = path.stat()
    if info.st_uid != os.geteuid() or info.st_mode & 0o022 or info.st_nlink != 1:
        raise ReleaseUpdateError("unsafe authority ownership/mode")
    return value


def _assets(root: Path, archive: Path, provenance: Path, tag: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", tag):
        raise ReleaseUpdateError("explicit release tag required")
    _git(root, "check-ref-format", f"refs/tags/{tag}")
    raw = engine.regular(archive)
    provenance_bytes = engine.regular(provenance)
    manifest, payload = dist.inspect_archive(archive)
    if engine.regular(archive) != raw:
        raise ReleaseUpdateError("archive changed during inspection")
    record = json.loads(provenance_bytes)
    commit = _revision(root, f"refs/tags/{tag}^{{commit}}")
    tree = _revision(root, f"{commit}^{{tree}}")
    expected = {
        "schema": "changerail.release-provenance.v1",
        "version": manifest["version"],
        "planned_tag": tag,
        "source_commit": commit,
        "source_tree": tree,
        "archive": archive.name,
        "archive_sha256": engine.digest(raw),
        "payload_sha256": manifest["payload_sha256"],
    }
    if not isinstance(record, dict) or any(
        record.get(k) != v for k, v in expected.items()
    ):
        raise ReleaseUpdateError(
            "provenance differs from artifact or explicit local tag"
        )
    committed = _tree(root, commit)
    config = json.loads(_git(root, "show", f"{commit}:distribution.json"))
    if config.get("schema") != "changerail.distribution-config.v1":
        raise ReleaseUpdateError("unsupported committed distribution configuration")
    # Materialize ONLY selected blob names into a private temporary fixture to use
    # distribution's exact pathlib glob semantics; never import selected code.
    with tempfile.TemporaryDirectory(prefix="changerail-release-inspect-") as temporary:
        selection = Path(temporary)
        for directory in config["trees"]:
            (selection / dist.safe_name(directory)).mkdir(parents=True, exist_ok=True)
        for name in committed:
            if any(name.startswith(directory + "/") for directory in config["trees"]):
                target = selection / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
        names = set(config["files"])
        for directory, pattern in config["trees"].items():
            names.update(
                p.relative_to(selection).as_posix()
                for p in (selection / directory).glob(pattern)
            )
    if names != set(payload):
        raise ReleaseUpdateError(
            "archive names differ from committed distribution selection"
        )
    for name, item in payload.items():
        if committed.get(name) != dist.entry(item):
            raise ReleaseUpdateError(f"archive bytes/mode differ from tag: {name}")
    if any(
        config.get(k) != manifest.get(k)
        for k in ("version", "execution_contract", "provenance")
    ):
        raise ReleaseUpdateError(
            "manifest metadata differs from committed configuration"
        )
    return {
        **expected,
        "payload_files": manifest["files"],
        "tag_object": _revision(root, f"refs/tags/{tag}"),
        "provenance_sha256": engine.digest(provenance_bytes),
    }


def _external(path: Path, root: Path) -> Path:
    path = Path(path)
    if not path.is_absolute() or path != path.resolve() or path.is_relative_to(root):
        raise ReleaseUpdateError(
            "proposal/assets must be canonical and outside target checkout"
        )
    return path


def prepare(
    root: Path,
    *,
    archive: Path,
    provenance: Path,
    tag: str,
    proposal: Path,
    node: Path,
    bootstrap: bool = False,
) -> dict[str, Any]:
    """Read-only target validation; write a durable proposal outside protected history.

    bootstrap explicitly authorizes initial acceptance of an already selected HEAD;
    it never waives committed runtime validation. Dependencies may be provisioned
    before bootstrap or later under provision-lease maintenance ownership.

    The proposal's parent must exist outside target on the SAME filesystem: staged
    source leaves/directories are atomically renamed from it into the checkout.
    A minimal preview location is a private directory adjacent to the executor,
    e.g. /srv/tools/.changerail-update-preview/proposal (not an assumed /tmp mount).
    Assets can live on another filesystem. Existing source read/write permissions
    survive replacement; exact actual modes are pinned for apply/reconcile.
    """
    root = engine.canonical_root(root)
    proposal = _external(proposal, root)
    archive, provenance = _external(archive, root), _external(provenance, root)
    if proposal.parent.stat().st_dev != root.stat().st_dev:
        raise ReleaseUpdateError(
            "proposal must share target filesystem for atomic source publication"
        )
    if proposal.exists() or maintenance_path(root).exists():
        raise ReleaseUpdateError(
            "proposal already exists or checkout is maintained; reconcile it"
        )
    _checkout(root)
    assets = _assets(root, archive, provenance, tag)
    if (
        bootstrap
        and not {
            "scripts/changerail/release_executor.py",
            "scripts/changerail/release_update.py",
        }
        <= assets["payload_files"].keys()
    ):
        raise ReleaseUpdateError(
            "bootstrap requires published implementation release; update old checkout separately first"
        )
    before_head = _revision(root, "HEAD")
    current_tree, target_tree = (
        _tree(root, before_head),
        _tree(root, assets["source_commit"]),
    )
    before = _inventory(root)
    release_changed = sorted(
        n
        for n in current_tree.keys() | target_tree.keys()
        if current_tree.get(n) != target_tree.get(n)
    )
    if any(_under(n, DEPENDENCIES) for n in release_changed):
        raise ReleaseUpdateError(
            "release overlaps installed dependency paths; provision separately"
        )
    # Whole protected working-tree and index overlays survive even if the selected
    # Git tree adds/deletes those names. In particular an absent local path stays
    # absent and an untracked local counterpart is never installed over.
    changed = [n for n in release_changed if not _under(n, PROTECTED)]
    if any(
        Path(n).name == ".gitattributes" for n in before.keys() | target_tree.keys()
    ):
        raise ReleaseUpdateError(
            "Git attributes/filters require separate operator resolution"
        )
    after = dict(before)
    directories = {}
    for name in changed:
        if not _matches_git_entry(before.get(name), current_tree.get(name)):
            raise ReleaseUpdateError(f"local/index/ignored overlap: {name}")
        if name not in current_tree and os.path.lexists(root / name):
            raise ReleaseUpdateError(f"untracked/ignored directory overlap: {name}")
        for other in before:
            if (
                other.startswith(name + "/") or name.startswith(other + "/")
            ) and not before[other].get("directory"):
                raise ReleaseUpdateError(f"file/directory collision: {name}")
        if name in target_tree:
            after[name] = _updated_entry(before.get(name), target_tree[name])
            for parent in (root / name).parents:
                if parent == root:
                    break
                relative = parent.relative_to(root).as_posix()
                if relative not in before:
                    directories[relative] = {"directory": True, "mode": 0o755}
        else:
            after.pop(name, None)
    after.update(directories)
    # A staged delta on any changed path is ambiguous even if worktree was reverted.
    staged = _git(root, "diff", "--cached", "--name-only", "-z", before_head).split(
        b"\0"
    )
    if set(changed) & {n.decode() for n in staged if n}:
        raise ReleaseUpdateError("staged change overlaps release")
    engine.runtime_inventory(
        root, before_head
    )  # dirty executable input is never an overlay
    if any(
        not _matches_git_entry(before.get(n), current_tree.get(n))
        for n in before.keys() | current_tree.keys()
        if any(fnmatch.fnmatchcase(n, p) for p in DECLARATIONS)
    ):
        raise ReleaseUpdateError("dirty dependency declaration refused")
    receipt = engine.receipt_path(root)
    prior = engine.regular(receipt) if receipt.exists() else None
    if bootstrap:
        if prior is not None or before_head != assets["source_commit"]:
            raise ReleaseUpdateError(
                "bootstrap needs unaccepted checkout already at chosen tag"
            )
        dependencies = None
    else:
        if prior is None:
            raise ReleaseUpdateError(
                "missing accepted receipt; explicit bootstrap required"
            )
        # This is trusted updater verification, not ordinary execution. Take an
        # actual exclusive lease even during this nonmutating prepare inspection.
        with engine.exclusive_use(root):
            accepted = engine.verify_release(root, accepted=_json(receipt))
        dependencies = accepted["dependencies"]
    declarations_changed = any(
        any(fnmatch.fnmatchcase(n, p) for p in DECLARATIONS) for n in changed
    )
    declarations_changed = declarations_changed or (
        dependencies is not None
        and str(node.resolve(strict=True)) != dependencies["node"]["path"]
    )
    value = {
        "schema": SCHEMA,
        "root": str(root),
        "archive": str(archive),
        "provenance": str(provenance),
        "tag": tag,
        "node": str(node.resolve(strict=True)),
        "assets": assets,
        "bootstrap": bootstrap,
        "before_head": before_head,
        "before_index": _git(root, "ls-files", "--stage", "-z").hex(),
        "before_head_bytes": engine.regular(root / ".git/HEAD").hex(),
        "before": before,
        "after": after,
        "changed": changed,
        "protected_release_delta": [n for n in release_changed if _under(n, PROTECTED)],
        "prior_receipt": prior.hex() if prior is not None else None,
        "before_dependencies": dependencies,
        "requires_provisioning": declarations_changed,
    }
    # Detect concurrent source/index writers before authorizing this proposal.
    if (
        before != _inventory(root)
        or before_head != _revision(root, "HEAD")
        or (value["before_index"] != _git(root, "ls-files", "--stage", "-z").hex())
    ):
        raise ReleaseUpdateError("checkout changed during prepare")
    proposal.mkdir(mode=0o700)
    _sync_dir(proposal.parent)
    # Retain exact bytes of index and prior receipt; no protected history copies.
    _write(proposal / "before-index", engine.regular(root / ".git/index"), new=True)
    if prior is not None:
        _write(proposal / "before-receipt.json", prior, new=True)
    _prepare_transaction(root, proposal, value, directories)
    if (
        before != _inventory(root)
        or value["before_index"] != _git(root, "ls-files", "--stage", "-z").hex()
    ):
        raise ReleaseUpdateError("checkout changed while retaining transaction")
    _write(proposal / "proposal.json", engine.encoded(value), new=True)
    return {
        "proposal": str(proposal),
        "proposal_sha256": engine.digest(engine.encoded(value)),
        "requires_provisioning": declarations_changed,
        "trust": "operator-selected assets; local tag does not prove publication",
    }


def _load(proposal: Path) -> tuple[Path, dict[str, Any], dict[str, str]]:
    proposal = Path(proposal)
    value = _json(proposal / "proposal.json")
    if value.get("schema") != SCHEMA or "transaction" not in value:
        raise ReleaseUpdateError("unsupported proposal")
    root = engine.canonical_root(Path(value["root"]))
    _external(proposal, root)
    if proposal.stat().st_uid != os.geteuid() or proposal.stat().st_mode & 0o077:
        raise ReleaseUpdateError("proposal directory must be owner-only")
    identity = {
        "schema": SCHEMA,
        "proposal": str(proposal),
        "proposal_sha256": engine.digest(engine.encoded(value)),
    }
    return root, value, identity


@contextmanager
def _ownership(root: Path):
    with engine.exclusive_use(root) as lease:
        directory = root / ".runtime/changerail"
        if directory.resolve() != directory:
            raise ReleaseUpdateError("linked legacy delivery directory")
        directory.mkdir(parents=True, exist_ok=True)
        fd = os.open(
            directory / "delivery.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
        )
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ReleaseUpdateError("unsafe legacy delivery lock")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ReleaseUpdateError("live legacy delivery owns checkout") from exc
            yield lease
        finally:
            os.close(fd)


def _state(proposal: Path, identity: dict[str, str], phase: str, **extra: Any) -> None:
    _write(
        proposal / "state.json", engine.encoded({**identity, "phase": phase, **extra})
    )


def _check_inputs(root: Path, value: dict[str, Any]) -> None:
    _checkout(root)
    if (
        _assets(root, Path(value["archive"]), Path(value["provenance"]), value["tag"])
        != value["assets"]
    ):
        raise ReleaseUpdateError("proposal inputs changed")


def _index_after(root: Path, value: dict[str, Any]) -> str:
    rows = {
        row.split(b"\t", 1)[1].decode(): row
        for row in bytes.fromhex(value["before_index"]).split(b"\0")
        if row
    }
    target = {}
    for row in _git(root, "ls-tree", "-rz", value["assets"]["source_commit"]).split(
        b"\0"
    ):
        if row:
            header, name = row.split(b"\t", 1)
            mode, _kind, oid = header.split()
            target[name.decode()] = mode + b" " + oid + b" 0\t" + name
    for name in value["changed"]:
        if name in target:
            rows[name] = target[name]
        else:
            rows.pop(name, None)
    return b"".join(rows[n] + b"\0" for n in sorted(rows)).hex()


def _prepare_transaction(
    root: Path, proposal: Path, value: dict[str, Any], directories: dict[str, Any]
) -> None:
    """Retain only public changed source blobs and an exact preserved-overlay index.

    GIT_INDEX_FILE points outside the checkout. update-index consumes committed blob
    IDs directly, so neither worktree filters nor protected payload bytes are read
    or installed by Git. No credentials/history backup is needed or created.
    """
    steps = [
        {"kind": "directory", "name": n, "after": directories[n]}
        for n in sorted(directories, key=lambda n: (n.count("/"), n))
    ]
    (proposal / "blobs").mkdir(mode=0o700)
    commit = value["assets"]["source_commit"]
    for name in value["changed"]:
        entry = value["after"].get(name)
        step = {"kind": "source", "name": name, "after": entry}
        if entry is not None:
            data = _git(root, "show", f"{commit}:{name}")
            sha = engine.digest(data)
            if "link" not in entry and sha != entry["sha256"]:
                raise ReleaseUpdateError("committed source changed during preparation")
            if "link" in entry and data != entry["link"].encode():
                raise ReleaseUpdateError(
                    "committed source link changed during preparation"
                )
            blob = proposal / "blobs" / sha
            if not blob.exists():
                _write(blob, data, new=True)
            step["blob"] = sha
        steps.append(step)
    before_bytes = engine.regular(proposal / "before-index")
    value["before_index_file"] = {
        "sha256": engine.digest(before_bytes),
        "mode": stat.S_IMODE((root / ".git/index").stat().st_mode),
    }
    after_index = proposal / "after-index"
    _write(after_index, before_bytes, new=True)
    rows = _index_after(root, value)
    desired = {
        row.split(b"\t", 1)[1].decode(): row
        for row in bytes.fromhex(rows).split(b"\0")
        if row
    }
    updates = b"".join(
        desired.get(n, b"0 " + b"0" * len(value["before_head"]) + b"\t" + n.encode())
        + b"\0"
        for n in value["changed"]
    )
    if updates:
        _git(
            root, "update-index", "-z", "--index-info", input=updates, index=after_index
        )
    if _git(root, "ls-files", "--stage", "-z", index=after_index).hex() != rows:
        raise ReleaseUpdateError("prepared index does not preserve exact overlay rows")
    # Git's index publication was into the proposal only; retain it durably.
    fd = os.open(after_index, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    _sync_dir(proposal)
    value["after_index"] = rows
    value["after_index_file"] = {
        **value["before_index_file"],
        "sha256": engine.digest(engine.regular(after_index)),
    }
    if value["before_index_file"] != value["after_index_file"]:
        steps.append({"kind": "index"})
    if bytes.fromhex(value["before_head_bytes"]) != (commit + "\n").encode():
        steps.append({"kind": "head"})
    value["transaction"] = steps


def _expected_step(
    value: dict[str, Any], count: int
) -> tuple[dict[str, Any], dict[str, Any], str]:
    inventory = dict(value["before"])
    index = value["before_index_file"]
    head = value["before_head_bytes"]
    for step in value["transaction"][:count]:
        if step["kind"] in {"source", "directory"}:
            if step["after"] is None:
                inventory.pop(step["name"], None)
            else:
                inventory[step["name"]] = step["after"]
        elif step["kind"] == "index":
            index = value["after_index_file"]
        elif step["kind"] == "head":
            head = (value["assets"]["source_commit"] + "\n").encode().hex()
    return inventory, index, head


def _matches_step(root: Path, value: dict[str, Any], count: int) -> bool:
    inventory, index, head = _expected_step(value, count)
    path = root / ".git/index"
    actual_index = {
        "sha256": engine.digest(engine.regular(path)),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }
    return (
        actual_index == index
        and engine.regular(root / ".git/HEAD").hex() == head
        and _inventory(root) == inventory
    )


def _publish_entry(
    proposal: Path, path: Path, data: bytes, mode: int, *, link: str | None = None
) -> None:
    """Stage on the same filesystem OUTSIDE target, then atomically replace one leaf.

    Interrupted staging leaves only disposable temporary files in the proposal.
    Target is always exactly before or after, never a partially written blob/mode.
    """
    fd, temporary = tempfile.mkstemp(prefix=".publish-", dir=proposal)
    staged = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            os.fchmod(stream.fileno(), mode)
            stream.flush()
            os.fsync(stream.fileno())
        if link is not None:
            staged.unlink()
            staged.symlink_to(link)
        os.replace(staged, path)
        _sync_dir(path.parent)
        _sync_dir(proposal)
    finally:
        if os.path.lexists(staged):
            staged.unlink()


def _transition_step(
    root: Path, proposal: Path, value: dict[str, Any], step: dict[str, Any]
) -> None:
    kind = step["kind"]
    if kind in {"source", "directory"}:
        name = step["name"]
        if _under(name, PROTECTED + DEPENDENCIES):
            raise ReleaseUpdateError(
                "transaction must never write a protected/dependency path"
            )
        path = root / dist.safe_name(name)
        entry = step["after"]
        if kind == "directory":
            staged = Path(tempfile.mkdtemp(prefix=".publish-directory-", dir=proposal))
            staged.chmod(entry["mode"])
            _sync_dir(staged)
            os.rename(staged, path)
            _sync_dir(path.parent)
            _sync_dir(proposal)
        elif entry is None:
            path.unlink()
            _sync_dir(path.parent)
        else:
            data = engine.regular(proposal / "blobs" / step["blob"])
            if engine.digest(data) != step["blob"]:
                raise ReleaseUpdateError("retained source blob changed")
            _publish_entry(proposal, path, data, entry["mode"], link=entry.get("link"))
    elif kind == "index":
        data = engine.regular(proposal / "after-index")
        expected = value["after_index_file"]
        if engine.digest(data) != expected["sha256"]:
            raise ReleaseUpdateError("retained overlay index changed")
        rows = {
            row.split(b"\t", 1)[1].decode(): row
            for row in bytes.fromhex(value["after_index"]).split(b"\0")
            if row
        }
        updates = b"".join(
            rows.get(n, b"0 " + b"0" * len(value["before_head"]) + b"\t" + n.encode())
            + b"\0"
            for n in value["changed"]
        )
        # Let Git own its normal index.lock; never replace an index behind an
        # active Git writer. Only unprotected rows are passed to update-index.
        _git(root, "update-index", "-z", "--index-info", input=updates)
        fd = os.open(root / ".git/index", os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        _sync_dir(root / ".git")
    elif kind == "head":
        # --no-deref detaches HEAD without moving the previous branch. CAS retains
        # its old commit; Git appends the ordinary HEAD reflog rather than rewriting it.
        _git(
            root,
            "update-ref",
            "--no-deref",
            "HEAD",
            value["assets"]["source_commit"],
            value["before_head"],
        )
        fd = os.open(root / ".git/HEAD", os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        _sync_dir(root / ".git")
    else:
        raise ReleaseUpdateError("unknown transaction step")


def _run_transition(
    root: Path, proposal: Path, value: dict[str, Any], identity: dict[str, str]
) -> None:
    path = proposal / "progress.json"
    progress = _json(path) if path.exists() else {**identity, "next": 0}
    count = progress.get("next")
    if (
        type(count) is not int
        or not 0 <= count <= len(value["transaction"])
        or progress != {**identity, "next": count}
    ):
        raise ReleaseUpdateError("invalid exact transaction progress")
    while count < len(value["transaction"]):
        if not _matches_step(root, value, count):
            # The only admitted lag is a crash after this single atomic operation
            # but before its progress receipt. Unknown mixtures never get repaired.
            if not _matches_step(root, value, count + 1):
                raise ReleaseUpdateError(
                    "checkout/index differs from exact retained before/after step; maintenance retained"
                )
        else:
            _transition_step(root, proposal, value, value["transaction"][count])
            if not _matches_step(root, value, count + 1):
                raise ReleaseUpdateError(
                    "transaction step did not reach exact after state"
                )
        count += 1
        _write(path, engine.encoded({**identity, "next": count}))
    if not _matches_step(root, value, count):
        raise ReleaseUpdateError("completed transaction differs from retained state")


def _position(root: Path, value: dict[str, Any]) -> str:
    if _matches_step(root, value, len(value["transaction"])):
        return "after"
    if _matches_step(root, value, 0):
        return "before"
    raise ReleaseUpdateError(
        "checkout/index differs from exact retained before/after; maintenance retained"
    )


def _prior_receipt(root: Path, value: dict[str, Any]) -> None:
    path = engine.receipt_path(root)
    actual = engine.regular(path).hex() if os.path.lexists(path) else None
    if actual != value["prior_receipt"]:
        raise ReleaseUpdateError("accepted receipt changed outside this proposal")


def _dependencies(
    root: Path,
    value: dict[str, Any],
    *,
    baseline: dict[str, Any] | None = None,
    provision: bool = False,
) -> dict[str, Any]:
    baseline = baseline if baseline is not None else value["before_dependencies"]
    if baseline is not None and not provision:
        interpreter = baseline["python"]
        target = (root / ".venv/bin/python").resolve(strict=True)
        if (
            str(target) != interpreter["target"]
            or engine._entry(target) != interpreter["file"]
        ):
            raise ReleaseUpdateError("Python changed before dependency verification")
    return engine.dependency_inventory(root, node=Path(value["node"]))


def _before_dependencies(root: Path, value: dict[str, Any]) -> dict[str, Any]:
    # A new explicitly selected Node path is provisioned separately. Validate the
    # retained environment with its OLD Node before publishing maintenance intent.
    old = {**value, "node": value["before_dependencies"]["node"]["path"]}
    return _dependencies(root, old)


def _advance(
    proposal: Path,
    root: Path,
    value: dict[str, Any],
    identity: dict[str, str],
    lease: int | None = None,
) -> dict[str, Any]:
    if lease is None:
        raise ReleaseUpdateError("exclusive lease required before mutation")
    actual, expected = os.fstat(lease), engine.lock_path(root).stat()
    if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino) or not any(
        re.search(r"^lock:.* FLOCK +ADVISORY +WRITE ", row)
        for row in Path(f"/proc/self/fdinfo/{lease}").read_text().splitlines()
    ):
        raise ReleaseUpdateError("exclusive lease required before mutation")
    marker = maintenance_path(root)
    _check_inputs(root, value)
    if (proposal / "intent.json").exists() and _json(proposal / "intent.json") != value:
        raise ReleaseUpdateError("frozen proposal changed")
    completed = proposal / "accepted-receipt.json"
    if completed.exists() and not marker.exists():
        accepted = _json(completed)
        if (
            _position(root, value) != "after"
            or _json(engine.receipt_path(root)) != accepted
        ):
            raise ReleaseUpdateError(
                "completed proposal no longer matches checkout/receipt"
            )
        engine.verify_release(root, accepted=accepted)
        return {
            **identity,
            "phase": "accepted",
            "receipt": str(engine.receipt_path(root)),
        }
    if marker.exists():
        if _json(marker) != identity:
            raise ReleaseUpdateError("different maintenance intent owns checkout")
        frozen = _json(proposal / "intent.json")
        if frozen != value:
            raise ReleaseUpdateError("frozen proposal changed")
    else:
        if (proposal / "intent.json").exists() and _json(
            proposal / "intent.json"
        ) != value:
            raise ReleaseUpdateError("changed proposal after intent")
        if _position(root, value) not in {"before", "after"}:
            raise ReleaseUpdateError("invalid initial position")
        # Even if HEAD already equals destination, only the exact prepared state
        # may create the first intent. External manual checkout is not adoption.
        if (
            _revision(root, "HEAD") != value["before_head"]
            or _inventory(root) != value["before"]
        ):
            raise ReleaseUpdateError("checkout moved after prepare")
        _prior_receipt(root, value)
        if value["prior_receipt"] is not None:
            engine.verify_release(root, accepted=_json(engine.receipt_path(root)))
        if (
            value["before_dependencies"] is not None
            and _before_dependencies(root, value) != value["before_dependencies"]
        ):
            raise ReleaseUpdateError("dependencies changed after prepare")
        if not (proposal / "intent.json").exists():
            _write(proposal / "intent.json", engine.encoded(value), new=True)
        _write(marker, engine.encoded(identity), new=True)
        _state(proposal, identity, "intent")
    if not _matches_step(root, value, len(value["transaction"])):
        _prior_receipt(root, value)
        if (
            value["before_dependencies"] is not None
            and _before_dependencies(root, value) != value["before_dependencies"]
        ):
            raise ReleaseUpdateError("dependencies changed before checkout")
    _run_transition(root, proposal, value, identity)
    _state(proposal, identity, "checkout-ready")
    provisioned = proposal / "provisioned.json"
    if provisioned.exists():
        provision = _json(provisioned)
        if provision.get("intent") != identity or provision.get(
            "dependencies"
        ) != _dependencies(root, value, baseline=provision.get("dependencies")):
            raise ReleaseUpdateError("provisioned dependency inventory changed")
    elif (
        value["requires_provisioning"] or (proposal / "provision-intent.json").exists()
    ):
        _state(proposal, identity, "awaiting-provisioning")
        raise ProvisioningRequired(
            "maintenance retained: use provision-lease, then reconcile"
        )
    elif (
        value["before_dependencies"] is not None
        and _dependencies(root, value) != value["before_dependencies"]
    ):
        raise ReleaseUpdateError(
            "dependency bytes changed without explicit provisioning"
        )
    accepted = engine.inspect_release(root, tag=value["tag"], node=Path(value["node"]))
    files = accepted["distribution"]["files"]
    archived = value["assets"]["payload_files"]
    if files.keys() != archived.keys() or any(
        not _matches_git_entry(files[name], archived[name]) for name in archived
    ):
        raise ReleaseUpdateError(
            "checkout payload names/bytes/executable semantics differ from downloaded archive"
        )
    # Existing accepted-receipt is immutable, including after a crash at publication.
    if completed.exists():
        if _json(completed) != accepted:
            raise ReleaseUpdateError(
                "candidate receipt changed after acceptance intent"
            )
    else:
        _prior_receipt(root, value)
        _write(completed, engine.encoded(accepted), new=True)
    current_path = engine.receipt_path(root)
    current = (
        engine.regular(current_path).hex() if os.path.lexists(current_path) else None
    )
    if current not in {value["prior_receipt"], engine.encoded(accepted).hex()}:
        raise ReleaseUpdateError("unexpected current receipt; maintenance retained")
    _write(current_path, engine.encoded(accepted))
    engine.verify_release(root, accepted=accepted)
    if _position(root, value) != "after":
        raise ReleaseUpdateError("checkout changed before final acceptance")
    _state(
        proposal,
        identity,
        "accepted",
        receipt_sha256=engine.digest(engine.encoded(accepted)),
    )
    marker.unlink()
    _sync_dir(marker.parent)
    return {**identity, "phase": "accepted", "receipt": str(current_path)}


def apply(proposal: Path) -> dict[str, Any]:
    """Accept the exact proposal; failures never remove receipt or maintenance fence."""
    root, value, identity = _load(proposal)
    with _ownership(root) as lease:
        return _advance(proposal, root, value, identity, lease)


def reconcile(proposal: Path) -> dict[str, Any]:
    """Resume the same intent; reject mixed/unknown Git states, never catch-and-succeed."""
    return apply(proposal)


@contextmanager
def provisioning(proposal: Path):
    """Explicit separate provisioning lease; caller may modify ONLY dependency dirs.

    The operator owns provisioning policy and commands. On normal return installed
    bytes are pinned durably. On failure intent and maintenance marker remain; resume
    this context to finish. apply/reconcile alone cannot accept a partial provision.
    """
    root, value, identity = _load(proposal)
    with _ownership(root):
        if (
            _json(maintenance_path(root)) != identity
            or _json(proposal / "intent.json") != value
        ):
            raise ReleaseUpdateError(
                "provisioning requires the same active maintenance intent"
            )
        _check_inputs(root, value)
        if (
            _position(root, value) != "after"
            or (proposal / "accepted-receipt.json").exists()
        ):
            raise ReleaseUpdateError("provision only after checkout, before acceptance")
        if (proposal / "provisioned.json").exists():
            raise ReleaseUpdateError(
                "provisioning already recorded; reconcile exact recorded inventory"
            )
        _prior_receipt(root, value)
        intent = proposal / "provision-intent.json"
        if intent.exists():
            if _json(intent) != identity:
                raise ReleaseUpdateError("different provision intent")
        else:
            _write(intent, engine.encoded(identity), new=True)
        _state(proposal, identity, "provisioning")
        yield {"root": str(root), "allowed_directories": list(DEPENDENCIES)}
        _check_inputs(root, value)
        if _position(root, value) != "after":
            raise ReleaseUpdateError("provisioning changed protected/source inventory")
        _prior_receipt(root, value)
        _write(
            proposal / "provisioned.json",
            engine.encoded(
                {
                    "intent": identity,
                    "dependencies": _dependencies(root, value, provision=True),
                }
            ),
            new=True,
        )
        _state(proposal, identity, "provisioned")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare")
    for field in ("root", "archive", "provenance", "proposal", "node"):
        preparation.add_argument("--" + field, type=Path, required=True)
    preparation.add_argument("--tag", required=True)
    preparation.add_argument("--bootstrap", action="store_true")
    for name in ("apply", "reconcile", "provision-lease"):
        commands.add_parser(name).add_argument("proposal", type=Path)
    args = vars(parser.parse_args(argv))
    command = args.pop("command")
    try:
        if command == "prepare":
            result = prepare(**args)
        elif command == "provision-lease":
            with provisioning(args["proposal"]) as lease:
                print(json.dumps(lease), flush=True)
                print(
                    "Maintenance lease held. Provision separately; type done when finished.",
                    flush=True,
                )
                if input().strip() != "done":
                    raise ReleaseUpdateError(
                        "provisioning not confirmed; maintenance retained"
                    )
            result = {"phase": "provisioned", "next": "reconcile"}
        else:
            result = apply(args["proposal"])
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, EOFError) as exc:
        print(f"ChangeRail release update: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
