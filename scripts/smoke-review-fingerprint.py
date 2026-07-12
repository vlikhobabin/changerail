#!/usr/bin/env python3
"""Smoke checks for ChangeRail review verdict freshness fingerprints."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_review_verdict.py"


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


def fingerprint(repo: Path) -> str:
    result = run([sys.executable, str(HELPER), "fingerprint", "--workspace", str(repo)], cwd=ROOT)
    require_ok(result, "fingerprint")
    payload: Any = json.loads(result.stdout)
    value = payload.get("diff_fingerprint")
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise AssertionError(f"unexpected fingerprint payload: {result.stdout.strip()}")
    return value


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
        repo = create_repo(Path(tmp))

        untracked = repo / "deliverable.txt"
        untracked.write_text("alpha\n", encoding="utf-8")
        before = fingerprint(repo)
        untracked.write_text("beta\n", encoding="utf-8")
        after = fingerprint(repo)
        if before == after:
            raise AssertionError("untracked non-ignored content change did not alter fingerprint")

        ignored = repo / ".runtime" / "changerail" / "reviews" / "card.json"
        ignored.parent.mkdir(parents=True)
        before_ignored = fingerprint(repo)
        ignored.write_text('{"schema":"changerail.review-verdict.v1"}\n', encoding="utf-8")
        after_ignored = fingerprint(repo)
        if before_ignored != after_ignored:
            raise AssertionError("ignored runtime content altered fingerprint")

    print("ok: review fingerprint smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
