#!/usr/bin/env python3
"""Smoke-test ChangeRail delivery manifest derivation and finalization helpers."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=240)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        sys.stderr.write(f"{label} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n")
        raise SystemExit(1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_workspace(root: Path) -> Path:
    workspace = root / "repo"
    workspace.mkdir()
    require_ok(run(["git", "init", "-q"], cwd=workspace), "git init")
    require_ok(run(["git", "config", "user.email", "smoke@example.invalid"], cwd=workspace), "git config email")
    require_ok(run(["git", "config", "user.name", "ChangeRail Smoke"], cwd=workspace), "git config name")
    write(workspace / ".gitignore", ".runtime/\n")
    write(workspace / "docs" / "tracked.md", "before\n")
    write(workspace / "openspec" / "board" / "3.inprogress" / ".gitkeep", "")
    write(workspace / "openspec" / "board" / "4.done" / ".gitkeep", "")
    write(workspace / "openspec" / "changes" / "archive" / ".gitkeep", "")
    require_ok(
        run(
            [
                "git",
                "add",
                ".gitignore",
                "docs/tracked.md",
                "openspec/board/3.inprogress/.gitkeep",
                "openspec/board/4.done/.gitkeep",
                "openspec/changes/archive/.gitkeep",
            ],
            cwd=workspace,
        ),
        "git add baseline",
    )
    require_ok(run(["git", "commit", "-q", "-m", "baseline"], cwd=workspace), "git commit baseline")
    write(workspace / "docs" / "tracked.md", "after\n")
    write(
        workspace / "openspec" / "board" / "3.inprogress" / "example-card.md",
        """# Example Card

## Status
3.inprogress

## Owner
agent

## OpenSpec Stage
review-ready

## Change Set
- `example-change`

## Result
Implemented and archived.

## Next
- `$changerail-review openspec/board/3.inprogress/example-card.md`

## Change 1: `example-change`

### Related
- `openspec/changes/archive/2026-07-12-example-change/`

## Log
- 2026-07-12T00:00:00Z fixture created.
""",
    )
    write(
        workspace / "openspec" / "changes" / "archive" / "2026-07-12-example-change" / "tasks.md",
        "## 1. Tasks\n\n- [x] done\n",
    )
    return workspace


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = make_workspace(Path(tmp))
        card = workspace / "openspec" / "board" / "3.inprogress" / "example-card.md"
        derive = run(
            [
                sys.executable,
                str(HELPER),
                "derive",
                str(card.relative_to(workspace)),
                "--workspace",
                str(workspace),
                "--write",
                "--json",
            ]
        )
        require_ok(derive, "derive")
        payload = json.loads(derive.stdout)
        manifest_path = Path(payload["manifest"])
        require_ok(run([sys.executable, str(HELPER), "validate", str(manifest_path), "--json"]), "validate")
        plan = run([sys.executable, str(HELPER), "staging-plan", str(manifest_path), "--json"])
        require_ok(plan, "staging-plan")
        paths = set(json.loads(plan.stdout)["paths"])
        expected = {
            "docs/tracked.md",
            "openspec/board/3.inprogress/example-card.md",
            "openspec/changes/archive/2026-07-12-example-change",
        }
        normalized = {path if path.endswith("/") else path for path in paths}
        missing = [path for path in expected if path not in normalized]
        if missing:
            sys.stderr.write("staging plan missing expected paths: " + ", ".join(missing) + "\n")
            sys.stderr.write(plan.stdout)
            return 1
        if any(path.startswith(".runtime/") for path in paths):
            sys.stderr.write("staging plan included runtime path\n")
            return 1

        require_ok(
            run(
                [
                    sys.executable,
                    str(HELPER),
                    "publish-update",
                    str(manifest_path),
                    "--status",
                    "pushed",
                    "--commit",
                    "abc1234",
                    "--remote",
                    "origin",
                    "--branch",
                    "main",
                    "--pushed-at",
                    "2026-07-12T00:00:01Z",
                    "--mode",
                    "review-gated",
                    "--json",
                ]
            ),
            "publish-update",
        )
        updated = json.loads(manifest_path.read_text(encoding="utf-8"))
        if updated["publish"].get("commit") != "abc1234" or updated["publish"].get("status") != "pushed":
            sys.stderr.write("publish metadata was not updated\n")
            return 1

        finalize = run(
            [
                sys.executable,
                str(HELPER),
                "finalize-card",
                str(card.relative_to(workspace)),
                "--workspace",
                str(workspace),
                "--commit",
                "abc1234",
                "--remote",
                "origin",
                "--branch",
                "main",
                "--push-status",
                "pushed",
                "--timestamp",
                "2026-07-12T00:00:02Z",
                "--json",
            ]
        )
        require_ok(finalize, "finalize-card")
        done = workspace / "openspec" / "board" / "4.done" / "example-card.md"
        text = done.read_text(encoding="utf-8")
        for needle in ("## Status\n4.done", "## OpenSpec Stage\narchived", "## Next\n- done", "abc1234"):
            if needle not in text:
                sys.stderr.write(f"finalized card missing {needle!r}\n{text}\n")
                return 1
        if card.exists():
            sys.stderr.write("source inprogress card still exists after finalization\n")
            return 1

    print("SMOKE_DELIVERY_MANIFEST_DERIVE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
