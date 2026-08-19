#!/usr/bin/env python3
"""Smoke-test validated review fingerprint cache reuse and invalidation."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "bin" / "changerail-review-verdict"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=120)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    raise AssertionError(f"{label} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def git(repo: Path, *args: str) -> None:
    require_ok(run(["git", *args], repo), f"git {' '.join(args)}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_repo(root: Path, label: str) -> Path:
    repo = root / label
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "tracked.txt", "baseline\n")
    write(repo / "rename-me.txt", "rename\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo


def fingerprint(repo: Path) -> dict[str, Any]:
    result = run([str(HELPER), "fingerprint", "--workspace", str(repo), "--cache", "--diagnostics"], ROOT)
    require_ok(result, "cached fingerprint")
    return json.loads(result.stdout)


def cache_status(payload: dict[str, Any]) -> str:
    return payload["diagnostics"]["cache"]["status"]


def assert_hit_after_warm(repo: Path, label: str) -> dict[str, Any]:
    first = fingerprint(repo)
    if cache_status(first) not in {"miss", "stale"}:
        raise AssertionError(f"{label}: first run should compute cache, got {cache_status(first)}")
    second = fingerprint(repo)
    if cache_status(second) != "hit":
        raise AssertionError(f"{label}: second run should hit cache, got {cache_status(second)}")
    return second


def assert_invalidates(root: Path, label: str, mutate: Any) -> None:
    repo = create_repo(root, label)
    warm = assert_hit_after_warm(repo, label)
    mutate(repo)
    changed = fingerprint(repo)
    if cache_status(changed) == "hit":
        raise AssertionError(f"{label}: cache reused stale payload")
    if (
        changed["tree_sha"] == warm["tree_sha"]
        and changed["diff_fingerprint"] == warm["diff_fingerprint"]
    ):
        raise AssertionError(f"{label}: mutation did not change payload identity")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-review-cache-") as tmp:
        root = Path(tmp)
        assert_invalidates(root, "tracked-modify", lambda repo: write(repo / "tracked.txt", "modified\n"))
        assert_invalidates(root, "tracked-delete", lambda repo: (repo / "tracked.txt").unlink())
        assert_invalidates(root, "tracked-rename", lambda repo: git(repo, "mv", "rename-me.txt", "renamed.txt"))
        assert_invalidates(root, "untracked-content", lambda repo: write(repo / "deliverable.txt", "alpha\n"))
        assert_invalidates(root, "permission", lambda repo: (repo / "tracked.txt").chmod(0o755))
        assert_invalidates(root, "exclude-state", lambda repo: write(repo / ".gitignore", ".runtime/\nignored.txt\n"))

        repo = create_repo(root, "ignored-runtime")
        warm = assert_hit_after_warm(repo, "ignored-runtime")
        write(repo / ".runtime" / "changerail" / "reviews" / "card.json", "{}\n")
        ignored = fingerprint(repo)
        if cache_status(ignored) != "hit" or ignored["diff_fingerprint"] != warm["diff_fingerprint"]:
            raise AssertionError("ignored runtime content invalidated cache")

    print("review fingerprint cache smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
