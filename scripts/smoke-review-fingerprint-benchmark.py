#!/usr/bin/env python3
"""Synthetic public-safe benchmark smoke for review fingerprint diagnostics."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "bin" / "changerail-review-verdict"
MANIFEST_HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"
TRACKED_FILE_COUNT = 180


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=240)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    raise AssertionError(f"{label} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(repo: Path, *args: str) -> None:
    require_ok(run(["git", *args], repo), f"git {' '.join(args)}")


def create_repo(root: Path) -> Path:
    repo = root / "synthetic-review-fingerprint"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "bin" / "openspec", "#!/usr/bin/env sh\nexit 0\n")
    os.chmod(repo / "bin" / "openspec", 0o755)
    write(repo / "scripts" / "public-surface-scan.py", "#!/usr/bin/env python3\nprint('scan ok')\n")
    for index in range(TRACKED_FILE_COUNT):
        write(repo / "src" / "generated" / f"file-{index:04d}.py", f"VALUE = {index}\n")
    write(repo / "docs" / "base.md", "baseline\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo


def fingerprint(repo: Path) -> dict[str, Any]:
    result = run([str(HELPER), "fingerprint", "--workspace", str(repo), "--diagnostics"], ROOT)
    require_ok(result, "fingerprint diagnostics")
    return json.loads(result.stdout)


def preflight(repo: Path) -> dict[str, Any]:
    card = "openspec/board/3.inprogress/example-card.md"
    write(
        repo / card,
        """# Example card

## Status
3.inprogress

## Owner
agent

## OpenSpec Stage
archived

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Change Set
- `example-change`

## Result
implemented

## Change 1: `example-change`

### Acceptance
- behavior delivered
""",
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-19-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", card, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive manifest")
    manifest = Path(json.loads(derived.stdout)["manifest"])
    result = run(
        [
            str(HELPER),
            "preflight",
            card,
            "--workspace",
            str(repo),
            "--manifest",
            str(manifest),
            "--diagnostics",
            "--json",
        ],
        repo,
    )
    require_ok(result, "preflight diagnostics")
    return json.loads(result.stdout)


def require_phases(timings: list[dict[str, Any]], expected: set[str], label: str) -> None:
    phases = {item.get("phase") for item in timings}
    missing = expected - phases
    if missing:
        raise AssertionError(f"{label} missing timing phases: {sorted(missing)}")
    for item in timings:
        if item.get("duration_ms", -1) < 0:
            raise AssertionError(f"{label} has negative duration: {item}")


def phase_duration(timings: list[dict[str, Any]], phase: str) -> float:
    for item in timings:
        if item.get("phase") == phase:
            return float(item["duration_ms"])
    raise AssertionError(f"missing duration for phase: {phase}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-review-benchmark-") as tmp:
        repo = create_repo(Path(tmp))
        write(repo / "docs" / "base.md", "docs payload\n")
        docs_payload = fingerprint(repo)
        docs_builder = docs_payload["diagnostics"]["tree_builder"]
        if docs_builder["full_index_refresh"] or docs_builder["changed_path_count"] > 1:
            raise AssertionError(f"docs-only payload was not path-scoped: {docs_builder}")
        require_phases(
            docs_payload["diagnostics"]["timings"],
            {"changed-path-discovery", "reviewed-tree-construction", "untracked-content-hashing", "fingerprint-assembly"},
            "fingerprint diagnostics",
        )

        write(repo / "src" / "payload.py", "PAYLOAD = True\n")
        source_payload = fingerprint(repo)
        if source_payload["diagnostics"]["tree_builder"]["full_index_refresh"]:
            raise AssertionError("source payload unexpectedly used a full-index refresh")

        data = preflight(repo)
        require_phases(
            data["diagnostics"]["preflight_timings"],
            {"fingerprint", "openspec-validation", "scoped-whitespace-check", "public-surface-scan"},
            "preflight diagnostics",
        )
        require_phases(
            data["diagnostics"]["fingerprint"]["timings"],
            {"changed-path-discovery", "reviewed-tree-construction", "untracked-content-hashing", "fingerprint-assembly"},
            "preflight fingerprint diagnostics",
        )
        summary = {
            "fixture_tracked_files": TRACKED_FILE_COUNT,
            "docs_changed_paths": docs_builder["changed_path_count"],
            "docs_tree_ms": phase_duration(docs_payload["diagnostics"]["timings"], "reviewed-tree-construction"),
            "source_changed_paths": source_payload["diagnostics"]["tree_builder"]["changed_path_count"],
            "source_tree_ms": phase_duration(source_payload["diagnostics"]["timings"], "reviewed-tree-construction"),
            "threshold_rationale": "docs-only changed paths must stay bounded to the synthetic fixture payload, not total tracked files",
        }

    print("review fingerprint benchmark smoke: PASS " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
