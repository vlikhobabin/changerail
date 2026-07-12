#!/usr/bin/env python3
"""Smoke-test ChangeRail delivery manifest derivation and finalization helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=240)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        sys.stderr.write(f"{label} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n")
        raise SystemExit(1)


def require_fails(result: subprocess.CompletedProcess[str], label: str, needle: str) -> None:
    if result.returncode == 0:
        sys.stderr.write(f"{label} unexpectedly passed\nSTDOUT:\n{result.stdout}\n")
        raise SystemExit(1)
    if needle not in result.stderr:
        sys.stderr.write(f"{label} did not report {needle!r}\nSTDERR:\n{result.stderr}\n")
        raise SystemExit(1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_non_utf8_path(workspace: Path, raw_relative_path: bytes, payload: bytes) -> str:
    raw_path = os.path.join(os.fsencode(workspace), raw_relative_path)
    with open(raw_path, "wb") as handle:
        handle.write(payload)
    return os.fsdecode(raw_relative_path)


def make_workspace(root: Path) -> Path:
    workspace = root / "repo"
    workspace.mkdir()
    require_ok(run(["git", "init", "-q"], cwd=workspace), "git init")
    require_ok(run(["git", "config", "user.email", "smoke@example.invalid"], cwd=workspace), "git config email")
    require_ok(run(["git", "config", "user.name", "ChangeRail Smoke"], cwd=workspace), "git config name")
    write(workspace / ".gitignore", ".runtime/\n")
    write(workspace / "docs" / "tracked.md", "before\n")
    write(workspace / "docs" / "tracked path.md", "before\n")
    write(workspace / "docs" / "delete-me.md", "delete me\n")
    write(workspace / "docs" / "rename-source.md", "rename me\n")
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
                "docs/tracked path.md",
                "docs/delete-me.md",
                "docs/rename-source.md",
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
    write(workspace / "docs" / "tracked path.md", "after\n")
    (workspace / "docs" / "delete-me.md").unlink()
    require_ok(run(["git", "mv", "docs/rename-source.md", "docs/renamed target.md"], cwd=workspace), "git mv")
    write(workspace / "docs" / "quoted \"path\".txt", "quoted\n")
    write(workspace / "docs" / "name -> literal.txt", "literal arrow\n")
    write(workspace / "docs" / "unicode-снег.txt", "unicode\n")
    bad_byte_path = write_non_utf8_path(workspace, b"docs/bad-\xff.txt", b"bad byte\n")
    write(workspace / "new files" / "one.txt", "one\n")
    write(workspace / "new files" / "two.txt", "two\n")
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
    return workspace, bad_byte_path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        workspace, bad_byte_path = make_workspace(Path(tmp))
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
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        invalid_dir = manifest_path.parent / "invalid-fixtures"
        invalid_dir.mkdir()
        extra = deepcopy(manifest)
        extra["workspace"]["unexpected"] = True
        extra_path = invalid_dir / "extra-field.json"
        write_json(extra_path, extra)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(extra_path), "--json"]),
            "manifest additionalProperties fixture",
            "Additional properties",
        )
        bad_time = deepcopy(manifest)
        bad_time["updated_at"] = "not-a-date-time"
        bad_time_path = invalid_dir / "bad-time.json"
        write_json(bad_time_path, bad_time)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_time_path), "--json"]),
            "manifest date-time fixture",
            "date-time",
        )
        bad_type = deepcopy(manifest)
        bad_type["card"]["status"] = 42
        bad_type_path = invalid_dir / "bad-nested-type.json"
        write_json(bad_type_path, bad_type)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_type_path), "--json"]),
            "manifest nested type fixture",
            "$.card.status",
        )
        bad_rename = deepcopy(manifest)
        bad_rename["committable_paths"].append(
            {
                "path": "docs/renamed.md",
                "kind": "docs",
                "phase": "do",
                "operation": "rename",
                "source_path": "docs/source.md",
            }
        )
        bad_rename_path = invalid_dir / "bad-rename.json"
        write_json(bad_rename_path, bad_rename)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_rename_path), "--json"]),
            "manifest conditional fixture",
            "target_path",
        )
        entries = {
            entry["path"]: entry
            for entry in manifest["committable_paths"]
            if isinstance(entry, dict) and "path" in entry
        }
        plan = run([sys.executable, str(HELPER), "staging-plan", str(manifest_path), "--json"])
        require_ok(plan, "staging-plan")
        paths = set(json.loads(plan.stdout)["paths"])
        expected = {
            "docs/tracked.md",
            "docs/tracked path.md",
            "docs/delete-me.md",
            "docs/rename-source.md",
            "docs/renamed target.md",
            "docs/quoted \"path\".txt",
            "docs/name -> literal.txt",
            "docs/unicode-снег.txt",
            bad_byte_path,
            "new files/one.txt",
            "new files/two.txt",
            "openspec/board/3.inprogress/example-card.md",
            "openspec/changes/archive/2026-07-12-example-change/tasks.md",
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
        if "new files" in paths:
            sys.stderr.write("staging plan included an untracked directory-wide path\n")
            return 1
        rename_entry = entries.get("docs/renamed target.md")
        if not rename_entry or rename_entry.get("operation") != "rename":
            sys.stderr.write("rename operation was not recorded\n")
            return 1
        if rename_entry.get("source_path") != "docs/rename-source.md":
            sys.stderr.write("rename source path was not preserved\n")
            return 1
        if rename_entry.get("target_path") != "docs/renamed target.md":
            sys.stderr.write("rename target path was not preserved\n")
            return 1
        delete_entry = entries.get("docs/delete-me.md")
        if not delete_entry or delete_entry.get("operation") != "delete":
            sys.stderr.write("delete operation was not recorded\n")
            return 1
        for exact in (
            "docs/tracked path.md",
            "docs/quoted \"path\".txt",
            "docs/name -> literal.txt",
            "docs/unicode-снег.txt",
            bad_byte_path,
        ):
            if exact not in entries:
                sys.stderr.write(f"exact path was not preserved in manifest: {exact}\n")
                return 1
        if os.fsencode(bad_byte_path) != b"docs/bad-\xff.txt":
            sys.stderr.write("non-UTF-8 path did not survive byte round-trip\n")
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
