#!/usr/bin/env python3
"""Smoke checks for ChangeRail review verdict freshness fingerprints."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_review_verdict.py"
sys.path.insert(0, str(ROOT / "scripts"))

from changerail_review_verdict import compute_fingerprint  # noqa: E402


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
    raise AssertionError(f"{label} failed: {detail}")


def git(repo: Path, *args: str) -> str:
    result = run(["git", *args], cwd=repo)
    require_ok(result, f"git {' '.join(args)}")
    return result.stdout


def fingerprint(repo: Path) -> dict[str, str]:
    result = run([sys.executable, str(HELPER), "fingerprint", "--workspace", str(repo)], cwd=ROOT)
    require_ok(result, "fingerprint")
    payload: Any = json.loads(result.stdout)
    value = payload.get("diff_fingerprint")
    tree = payload.get("tree_sha")
    if (
        not isinstance(value, str)
        or not value.startswith("sha256:")
        or not isinstance(tree, str)
        or len(tree) != 40
    ):
        raise AssertionError(f"unexpected fingerprint payload: {result.stdout.strip()}")
    return payload


def assert_reference_parity(repo: Path, label: str) -> None:
    optimized = compute_fingerprint(repo, diagnostics=True)
    reference = compute_fingerprint(repo, diagnostics=True, force_reference=True)
    for key in ("tree_sha", "diff_fingerprint"):
        if optimized[key] != reference[key]:
            raise AssertionError(f"{label}: optimized {key} differs from reference")
    tree_builder = optimized.get("diagnostics", {}).get("tree_builder", {})
    if tree_builder.get("mode") != "optimized":
        raise AssertionError(f"{label}: expected optimized builder, got {tree_builder}")


def parity_repo(root: Path, label: str) -> Path:
    repo = root / label
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "changerail@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    (repo / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    git(repo, "add", ".gitignore", "tracked.txt")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo


def create_repo(workspace: Path) -> Path:
    repo = workspace / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "changerail@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    (repo / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    git(repo, "add", ".gitignore", "tracked.txt")
    git(repo, "commit", "-m", "baseline")
    return repo


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-review-fingerprint-") as tmp:
        root = Path(tmp)
        repo = create_repo(root)
        clean = fingerprint(repo)
        head_tree = git(repo, "rev-parse", "HEAD^{tree}").strip()
        if clean["tree_sha"] != head_tree:
            raise AssertionError("clean reviewed tree does not match HEAD tree")

        untracked = repo / "deliverable.txt"
        untracked.write_text("alpha\n", encoding="utf-8")
        before = fingerprint(repo)
        untracked.write_text("beta\n", encoding="utf-8")
        after = fingerprint(repo)
        if before["diff_fingerprint"] == after["diff_fingerprint"]:
            raise AssertionError("untracked non-ignored content change did not alter fingerprint")
        if before["tree_sha"] == after["tree_sha"]:
            raise AssertionError("untracked non-ignored content change did not alter reviewed tree")

        ignored = repo / ".runtime" / "changerail" / "reviews" / "card.json"
        ignored.parent.mkdir(parents=True)
        before_ignored = fingerprint(repo)
        ignored.write_text('{"schema":"changerail.review-verdict.v1"}\n', encoding="utf-8")
        after_ignored = fingerprint(repo)
        if before_ignored != after_ignored:
            raise AssertionError("ignored runtime content altered fingerprint")

        unborn = Path(tmp) / "unborn"
        unborn.mkdir()
        git(unborn, "init", "-q")
        (unborn / "first.txt").write_text("first\n", encoding="utf-8")
        unborn_payload = fingerprint(unborn)
        if unborn_payload["head_commit"] != "unborn" or len(unborn_payload["tree_sha"]) != 40:
            raise AssertionError(f"unexpected unborn fingerprint payload: {unborn_payload}")

        repo = parity_repo(root, "modify")
        (repo / "tracked.txt").write_text("modified\n", encoding="utf-8")
        assert_reference_parity(repo, "modify")

        repo = parity_repo(root, "add")
        (repo / "added.txt").write_text("added\n", encoding="utf-8")
        assert_reference_parity(repo, "add")

        repo = parity_repo(root, "delete")
        (repo / "tracked.txt").unlink()
        assert_reference_parity(repo, "delete")

        repo = parity_repo(root, "rename")
        git(repo, "mv", "tracked.txt", "renamed.txt")
        assert_reference_parity(repo, "rename")

        repo = parity_repo(root, "spaces")
        (repo / "space name.txt").write_text("space\n", encoding="utf-8")
        assert_reference_parity(repo, "spaces")

        repo = parity_repo(root, "literal-arrow")
        (repo / "literal -> arrow.txt").write_text("arrow\n", encoding="utf-8")
        assert_reference_parity(repo, "literal arrow")

        repo = parity_repo(root, "unicode")
        (repo / "unicode-å.txt").write_text("unicode\n", encoding="utf-8")
        assert_reference_parity(repo, "unicode")

        repo = parity_repo(root, "symlink")
        try:
            (repo / "link.txt").symlink_to("tracked.txt")
        except OSError:
            pass
        else:
            assert_reference_parity(repo, "symlink")

        if os.name == "posix":
            repo = parity_repo(root, "non-utf8")
            raw_path = os.fsencode(repo) + b"/nonutf-\xff.txt"
            fd = os.open(raw_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as handle:
                handle.write(b"non-utf8\n")
            assert_reference_parity(repo, "non-utf8")

    print("ok: review fingerprint smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
