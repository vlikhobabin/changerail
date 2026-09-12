"""Transaction-only byte budgets retain the ordinary authority checks."""

import os
import sys

import pytest

from scripts.changerail import release_executor as engine
from scripts.changerail import release_update as update
from test_release_update import prepare, put, release as release


def test_large_proposal_and_frozen_intent_keep_ordinary_and_transaction_bounds(release):
    r = release
    prepared = prepare(r)
    proposal = r["proposal"] / "proposal.json"
    original = proposal.read_bytes()
    # One real, valid JSON file above the default limit. Padding avoids millions
    # of synthetic inventory entries and is written in reusable 1 MiB chunks.
    with proposal.open("ab") as stream:
        remaining = engine.MAX_FILE_BYTES + 1 - len(original)
        padding = b" " * (1024 * 1024)
        while remaining:
            count = min(remaining, len(padding))
            stream.write(padding[:count])
            remaining -= count
    assert proposal.stat().st_size == 128 * 1024 * 1024 + 1
    for reader in (engine.document, update._json):
        with pytest.raises(engine.ReleaseExecutorError, match="bounded regular file"):
            reader(proposal)
    root, value, identity = update._load(r["proposal"])
    assert root == r["root"]
    assert identity["proposal_sha256"] == prepared["proposal_sha256"]
    assert engine.encoded(value) == original

    # Reuse the same padded inode as intent. Production apply must read this
    # frozen authority with the transaction budget and preserve canonical identity.
    intent = r["proposal"] / "intent.json"
    proposal.rename(intent)
    proposal.write_bytes(original)
    proposal.chmod(0o600)
    result = update.apply(r["proposal"])
    assert result["phase"] == "accepted"
    assert result["proposal_sha256"] == prepared["proposal_sha256"]
    intent.write_bytes(original)
    assert update.reconcile(r["proposal"]) == result

    # Sparse enlargement costs no GiB allocation; reject before reading/parsing.
    assert update.MAX_TRANSACTION_BYTES == 1024 * 1024 * 1024
    with intent.open("r+b") as stream:
        stream.truncate(update.MAX_TRANSACTION_BYTES + 1)
    with pytest.raises(engine.ReleaseExecutorError, match="bounded regular file"):
        update.reconcile(r["proposal"])
    proposal.unlink()
    intent.rename(proposal)
    with pytest.raises(engine.ReleaseExecutorError, match="bounded regular file"):
        update._load(r["proposal"])


def test_transaction_reader_preserves_link_type_and_ownership_checks(tmp_path):
    authority = tmp_path / "authority.json"
    authority.write_text("{}")
    linked = tmp_path / "linked.json"
    linked.symlink_to(authority)
    ancestor = tmp_path / "ancestor"
    ancestor.symlink_to(tmp_path, target_is_directory=True)
    for path in (linked, ancestor / authority.name):
        with pytest.raises(engine.ReleaseExecutorError, match="linked authority/source"):
            update._json(path, max_bytes=update.MAX_TRANSACTION_BYTES)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    with pytest.raises(engine.ReleaseExecutorError, match="bounded regular file"):
        update._json(fifo, max_bytes=update.MAX_TRANSACTION_BYTES)
    with pytest.raises((engine.ReleaseExecutorError, IsADirectoryError)):
        update._json(tmp_path, max_bytes=update.MAX_TRANSACTION_BYTES)
    authority.chmod(0o666)
    with pytest.raises(update.ReleaseUpdateError, match="unsafe authority ownership/mode"):
        update._json(authority, max_bytes=update.MAX_TRANSACTION_BYTES)
    authority.chmod(0o600)
    hardlink = tmp_path / "hardlink.json"
    os.link(authority, hardlink)
    with pytest.raises(update.ReleaseUpdateError, match="unsafe authority ownership/mode"):
        update._json(authority, max_bytes=update.MAX_TRANSACTION_BYTES)


@pytest.mark.parametrize("replacement", [b"[]", b"{} "])
def test_transaction_reader_detects_real_file_mutation(tmp_path, replacement):
    authority = tmp_path / "authority.json"
    authority.write_bytes(b"{}")
    mutated = False

    def mutate_after_stat(frame, event, function):
        nonlocal mutated
        # A C-return profile event puts a real disk mutation strictly after the
        # first fstat snapshot, without replacing reader/stat functions or races.
        if event == "c_return" and function is os.fstat and not mutated:
            mutated = True
            authority.write_bytes(replacement)
            os.utime(authority, ns=(1, 1))

    previous = sys.getprofile()
    try:
        sys.setprofile(mutate_after_stat)
        with pytest.raises(engine.ReleaseExecutorError, match="file changed during"):
            update._json(authority, max_bytes=update.MAX_TRANSACTION_BYTES)
    finally:
        sys.setprofile(previous)
    assert mutated


@pytest.mark.parametrize("bound", [0, -1, float("inf"), True])
def test_reader_requires_a_finite_positive_integer_bound(tmp_path, bound):
    with pytest.raises(engine.ReleaseExecutorError, match="positive integer"):
        engine.document(tmp_path / "unused", max_bytes=bound)


def test_prepare_apply_preserves_protected_historical_attributes(release):
    r = release
    root = r["root"]
    attributes = put(
        root,
        ".runtime/changerail/external/archived-project/.gitattributes",
        "* filter=historical-only text eol=crlf\n",
        0o444,
    )
    put(root, "openspec/.gitattributes", "*.md -text\n", 0o444)
    put(root, ".runtime/changerail/external/archived-project/history.txt", "old\n", 0o444)
    before = update._inventory(root)
    original = attributes.read_bytes()
    inode = attributes.stat().st_ino
    prepare(r)
    assert update._inventory(root) == before
    _, value, _ = update._load(r["proposal"])
    assert not any(update._under(name, update.PROTECTED) for name in value["changed"])
    assert update.apply(r["proposal"])["phase"] == "accepted"
    after = update._inventory(root)
    assert after == value["after"]
    assert {
        name: entry for name, entry in after.items() if update._under(name, update.PROTECTED)
    } == {
        name: entry for name, entry in before.items() if update._under(name, update.PROTECTED)
    }
    assert attributes.read_bytes() == original
    assert attributes.stat().st_ino == inode
    assert engine.regular(root / "scripts/changerail/product.py") == b"# next runtime\n"


@pytest.mark.parametrize("name", [".gitattributes", "scripts/.gitattributes", ".git/info/attributes"])
def test_prepare_rejects_source_and_repository_attributes(release, name):
    r = release
    put(r["root"], name, "* filter=unsupported\n")
    before = update._inventory(r["root"])
    message = "unsupported Git state: info/attributes" if name.startswith(".git/") else "Git attributes/filters"
    with pytest.raises(update.ReleaseUpdateError, match=message):
        prepare(r)
    assert not r["proposal"].exists()
    assert not update.maintenance_path(r["root"]).exists()
    assert update._inventory(r["root"]) == before
    assert engine.receipt_path(r["root"]).read_bytes() == r["old_receipt"]
