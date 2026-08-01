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


def git_stdout(command: list[str], cwd: Path, label: str) -> str:
    result = run(command, cwd=cwd)
    require_ok(result, label)
    return result.stdout.strip()


def derive_manifest(workspace: Path) -> Path:
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
    require_ok(derive, "derive scope manifest")
    return Path(json.loads(derive.stdout)["manifest"])


def scope_check(manifest_path: Path, workspace: Path, target: str) -> subprocess.CompletedProcess[str]:
    return run(
        [
            sys.executable,
            str(HELPER),
            "scope-check",
            str(manifest_path),
            "--workspace",
            str(workspace),
            "--target",
            target,
            "--json",
        ]
    )


def require_scope_ok(manifest_path: Path, workspace: Path, target: str, label: str) -> None:
    result = scope_check(manifest_path, workspace, target)
    require_ok(result, label)
    payload = json.loads(result.stdout)
    targets = payload.get("targets", {})
    names = ("working-tree", "staged") if target == "both" else (target,)
    for name in names:
        if not targets.get(name, {}).get("ok"):
            sys.stderr.write(f"{label} returned non-ok payload: {payload!r}\n")
            raise SystemExit(1)


def require_scope_fails(
    manifest_path: Path,
    workspace: Path,
    target: str,
    bucket: str,
    needle: str,
    label: str,
) -> None:
    result = scope_check(manifest_path, workspace, target)
    if result.returncode == 0:
        sys.stderr.write(f"{label} unexpectedly passed\nSTDOUT:\n{result.stdout}\n")
        raise SystemExit(1)
    payload = json.loads(result.stdout)
    entries = payload.get("targets", {}).get(target, {}).get(bucket, [])
    if needle not in json.dumps(entries, ensure_ascii=False):
        sys.stderr.write(f"{label} did not report {needle!r} in {bucket}: {payload!r}\n")
        raise SystemExit(1)


def staged_scope_paths(workspace: Path) -> set[str]:
    result = run(["git", "diff", "--cached", "--name-status", "-z", "--find-renames", "--"], cwd=workspace)
    require_ok(result, "git diff cached scope paths")
    records = [record for record in result.stdout.split("\0") if record]
    paths: set[str] = set()
    index = 0
    while index < len(records):
        status = records[index]
        index += 1
        if status.startswith(("R", "C")):
            paths.add(records[index])
            paths.add(records[index + 1])
            index += 2
        else:
            paths.add(records[index])
            index += 1
    return paths


def stage_manifest_paths(manifest_path: Path, workspace: Path, skip: set[str] | None = None) -> None:
    skip = skip or set()
    plan = run([sys.executable, str(HELPER), "staging-plan", str(manifest_path), "--json"])
    require_ok(plan, "scope staging-plan")
    paths = [path for path in json.loads(plan.stdout)["paths"] if path not in skip]
    for path in paths:
        absolute = workspace / path
        if absolute.exists() or absolute.is_symlink():
            require_ok(run(["git", "add", "--", path], cwd=workspace), f"git add scope path {path}")
        else:
            if path in staged_scope_paths(workspace):
                continue
            require_ok(run(["git", "add", "-u", "--", path], cwd=workspace), f"git add scope missing path {path}")


def write_non_utf8_path(workspace: Path, raw_relative_path: bytes, payload: bytes) -> str:
    raw_path = os.path.join(os.fsencode(workspace), raw_relative_path)
    with open(raw_path, "wb") as handle:
        handle.write(payload)
    return os.fsdecode(raw_relative_path)


def make_workspace(root: Path) -> Path:
    workspace = root / "repo"
    workspace.mkdir(parents=True)
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


def check_scope_reconciliation(root: Path) -> None:
    workspace, _ = make_workspace(root / "scope-positive")
    manifest_path = derive_manifest(workspace)
    require_scope_ok(manifest_path, workspace, "working-tree", "scope-check working tree")
    stage_manifest_paths(manifest_path, workspace)
    require_scope_ok(manifest_path, workspace, "staged", "scope-check staged")
    require_scope_ok(manifest_path, workspace, "both", "scope-check both")

    workspace, _ = make_workspace(root / "scope-extra")
    manifest_path = derive_manifest(workspace)
    stage_manifest_paths(manifest_path, workspace)
    write(workspace / "docs" / "extra-staged.md", "extra\n")
    require_ok(run(["git", "add", "--", "docs/extra-staged.md"], cwd=workspace), "git add extra staged")
    require_scope_fails(
        manifest_path,
        workspace,
        "staged",
        "extra",
        "docs/extra-staged.md",
        "scope-check staged extra",
    )

    workspace, _ = make_workspace(root / "scope-missing")
    manifest_path = derive_manifest(workspace)
    stage_manifest_paths(manifest_path, workspace, skip={"docs/tracked.md"})
    require_scope_fails(
        manifest_path,
        workspace,
        "staged",
        "missing",
        "docs/tracked.md",
        "scope-check staged missing",
    )

    workspace, _ = make_workspace(root / "scope-mismatched")
    manifest_path = derive_manifest(workspace)
    stage_manifest_paths(manifest_path, workspace)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["committable_paths"]:
        if entry.get("path") == "docs/tracked.md":
            entry["operation"] = "delete"
            entry["source_path"] = "docs/tracked.md"
            entry.pop("target_path", None)
            break
    else:
        sys.stderr.write("scope mismatch fixture could not find docs/tracked.md\n")
        raise SystemExit(1)
    write_json(manifest_path, manifest)
    require_scope_fails(
        manifest_path,
        workspace,
        "staged",
        "mismatched",
        "docs/tracked.md",
        "scope-check staged mismatched",
    )


def check_bare_remote_publish_finalization(root: Path) -> None:
    remote = root / "remote.git"
    workspace = root / "publish-repo"
    require_ok(run(["git", "init", "--bare", "-q", str(remote)]), "git init bare remote")
    workspace.mkdir()
    require_ok(run(["git", "init", "-q"], cwd=workspace), "git init publish workspace")
    require_ok(run(["git", "checkout", "-q", "-b", "main"], cwd=workspace), "git checkout main")
    require_ok(run(["git", "config", "user.email", "smoke@example.invalid"], cwd=workspace), "git config email")
    require_ok(run(["git", "config", "user.name", "ChangeRail Smoke"], cwd=workspace), "git config name")
    require_ok(run(["git", "remote", "add", "origin", str(remote)], cwd=workspace), "git remote add")
    write(workspace / ".gitignore", ".runtime/\n")
    write(workspace / "docs" / "payload.md", "before\n")
    write(workspace / "openspec" / "board" / "4.done" / ".gitkeep", "")
    write(
        workspace / "openspec" / "board" / "3.inprogress" / "publish-card.md",
        """# Publish Card

## Status
3.inprogress

## Owner
agent

## OpenSpec Stage
review-ready

## Change Set
- `publish-change`

## Result
Implemented and reviewed.

## Next
- `$changerail-pub openspec/board/3.inprogress/publish-card.md`

## Change 1: `publish-change`

### Related
- `openspec/changes/archive/2026-07-12-publish-change/`

## Log
- 2026-07-12T00:00:00Z fixture created.
""",
    )
    require_ok(
        run(
            [
                "git",
                "add",
                ".gitignore",
                "docs/payload.md",
                "openspec/board/3.inprogress/publish-card.md",
                "openspec/board/4.done/.gitkeep",
            ],
            cwd=workspace,
        ),
        "git add publish baseline",
    )
    require_ok(run(["git", "commit", "-q", "-m", "baseline"], cwd=workspace), "git commit publish baseline")
    require_ok(run(["git", "push", "-q", "-u", "origin", "main"], cwd=workspace), "git push publish baseline")

    card = workspace / "openspec" / "board" / "3.inprogress" / "publish-card.md"
    write(workspace / "docs" / "payload.md", "after\n")
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
    require_ok(derive, "derive publish manifest")
    manifest_path = Path(json.loads(derive.stdout)["manifest"])

    require_ok(run(["git", "add", "docs/payload.md", str(card.relative_to(workspace))], cwd=workspace), "git add payload")
    require_ok(run(["git", "commit", "-q", "-m", "payload"], cwd=workspace), "git commit payload")
    payload_commit = git_stdout(["git", "rev-parse", "HEAD"], workspace, "rev-parse payload")

    finalize = run(
        [
            sys.executable,
            str(HELPER),
            "finalize-card",
            str(card.relative_to(workspace)),
            "--workspace",
            str(workspace),
            "--manifest",
            str(manifest_path.relative_to(workspace)),
            "--commit",
            payload_commit,
            "--remote",
            "origin",
            "--branch",
            "main",
            "--push-status",
            "pending",
            "--timestamp",
            "2026-07-12T00:00:02Z",
            "--json",
        ]
    )
    require_ok(finalize, "finalize publish card")
    done = workspace / "openspec" / "board" / "4.done" / "publish-card.md"
    require_ok(
        run(
            [
                "git",
                "add",
                "openspec/board/3.inprogress/publish-card.md",
                "openspec/board/4.done/publish-card.md",
            ],
            cwd=workspace,
        ),
        "git add finalized card",
    )
    require_ok(run(["git", "commit", "--amend", "-q", "--no-edit"], cwd=workspace), "git amend finalized card")
    final_commit = git_stdout(["git", "rev-parse", "HEAD"], workspace, "rev-parse final")
    if final_commit == payload_commit:
        sys.stderr.write("finalized commit did not change after card-only amend\n")
        raise SystemExit(1)
    require_ok(run(["git", "show", "--check", "--oneline", "HEAD"], cwd=workspace), "git show check finalized")
    require_ok(run(["git", "push", "-q", "origin", "HEAD:main"], cwd=workspace), "git push final")
    require_ok(
        run(
            [
                sys.executable,
                str(HELPER),
                "publish-update",
                str(manifest_path),
                "--status",
                "pushed",
                "--payload-commit",
                payload_commit,
                "--published-commit",
                final_commit,
                "--remote",
                "origin",
                "--branch",
                "main",
                "--pushed-at",
                "2026-07-12T00:00:03Z",
                "--mode",
                "review-gated",
                "--json",
            ]
        ),
        "publish-update final",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    publish = manifest["publish"]
    if publish.get("payload_commit") != payload_commit or publish.get("published_commit") != final_commit:
        sys.stderr.write(f"manifest did not distinguish payload/final commits: {publish!r}\n")
        raise SystemExit(1)
    if publish.get("status") != "pushed" or publish.get("remote") != "origin" or publish.get("branch") != "main":
        sys.stderr.write(f"manifest missing final push metadata: {publish!r}\n")
        raise SystemExit(1)
    if manifest["card"].get("path") != "openspec/board/4.done/publish-card.md":
        sys.stderr.write(f"manifest card path was not finalized: {manifest['card']!r}\n")
        raise SystemExit(1)
    if manifest["card"].get("status") != "4.done":
        sys.stderr.write(f"manifest card status was not finalized: {manifest['card']!r}\n")
        raise SystemExit(1)
    text = done.read_text(encoding="utf-8")
    forbidden = (payload_commit, final_commit, "push status", "pending")
    for needle in forbidden:
        if needle in text:
            sys.stderr.write(f"tracked finalized card retained forbidden metadata {needle!r}\n{text}\n")
            raise SystemExit(1)


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
        bad_publish = deepcopy(manifest)
        bad_publish["publish"]["pushed_at"] = "not-a-date-time"
        bad_publish_path = invalid_dir / "bad-publish-time.json"
        write_json(bad_publish_path, bad_publish)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_publish_path), "--json"]),
            "manifest publish date-time fixture",
            "date-time",
        )
        bad_publish_extra = deepcopy(manifest)
        bad_publish_extra["publish"]["unexpected"] = True
        bad_publish_extra_path = invalid_dir / "bad-publish-extra.json"
        write_json(bad_publish_extra_path, bad_publish_extra)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_publish_extra_path), "--json"]),
            "manifest publish additionalProperties fixture",
            "Additional properties",
        )
        bad_pushed_status_only = deepcopy(manifest)
        bad_pushed_status_only["publish"] = {"status": "pushed"}
        bad_pushed_status_only_path = invalid_dir / "bad-pushed-status-only.json"
        write_json(bad_pushed_status_only_path, bad_pushed_status_only)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_pushed_status_only_path), "--json"]),
            "manifest pushed status-only fixture",
            "payload_commit",
        )
        bad_pushed_missing_pushed_at = deepcopy(manifest)
        bad_pushed_missing_pushed_at["publish"] = {
            "status": "pushed",
            "payload_commit": "payload1234",
            "published_commit": "published1234",
            "remote": "origin",
            "branch": "main",
        }
        bad_pushed_missing_pushed_at_path = invalid_dir / "bad-pushed-missing-pushed-at.json"
        write_json(bad_pushed_missing_pushed_at_path, bad_pushed_missing_pushed_at)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_pushed_missing_pushed_at_path), "--json"]),
            "manifest pushed missing pushed_at fixture",
            "pushed_at",
        )
        bad_skipped = deepcopy(manifest)
        bad_skipped["publish"] = {"status": "skipped"}
        bad_skipped_path = invalid_dir / "bad-skipped.json"
        write_json(bad_skipped_path, bad_skipped)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_skipped_path), "--json"]),
            "manifest skipped missing evidence fixture",
            "payload_commit",
        )
        bad_skipped_mode = deepcopy(manifest)
        bad_skipped_mode["publish"] = {
            "status": "skipped",
            "payload_commit": "payload1234",
            "published_commit": "published1234",
            "reason": "push skipped by --no-push",
            "mode": "review-gated",
        }
        bad_skipped_mode_path = invalid_dir / "bad-skipped-mode.json"
        write_json(bad_skipped_mode_path, bad_skipped_mode)
        require_fails(
            run([sys.executable, str(HELPER), "validate", str(bad_skipped_mode_path), "--json"]),
            "manifest skipped mode fixture",
            "local-only",
        )
        skipped_path = invalid_dir / "skipped-positive.json"
        write_json(skipped_path, manifest)
        require_ok(
            run(
                [
                    sys.executable,
                    str(HELPER),
                    "publish-update",
                    str(skipped_path),
                    "--status",
                    "skipped",
                    "--payload-commit",
                    "payload1234",
                    "--published-commit",
                    "published1234",
                    "--reason",
                    "push skipped by --no-push",
                    "--mode",
                    "local-only",
                    "--json",
                ]
            ),
            "publish-update skipped",
        )
        skipped = json.loads(skipped_path.read_text(encoding="utf-8"))["publish"]
        if (
            skipped.get("status") != "skipped"
            or skipped.get("mode") != "local-only"
            or skipped.get("reason") != "push skipped by --no-push"
        ):
            sys.stderr.write(f"skipped publish metadata was not updated: {skipped!r}\n")
            return 1
        bad_pushed_update_path = invalid_dir / "bad-pushed-update.json"
        write_json(bad_pushed_update_path, manifest)
        require_fails(
            run(
                [
                    sys.executable,
                    str(HELPER),
                    "publish-update",
                    str(bad_pushed_update_path),
                    "--status",
                    "pushed",
                    "--json",
                ]
            ),
            "publish-update pushed missing evidence fixture",
            "payload_commit",
        )
        bad_pushed_update_missing_pushed_at_path = invalid_dir / "bad-pushed-update-missing-pushed-at.json"
        write_json(bad_pushed_update_missing_pushed_at_path, manifest)
        require_fails(
            run(
                [
                    sys.executable,
                    str(HELPER),
                    "publish-update",
                    str(bad_pushed_update_missing_pushed_at_path),
                    "--status",
                    "pushed",
                    "--payload-commit",
                    "payload1234",
                    "--published-commit",
                    "published1234",
                    "--remote",
                    "origin",
                    "--branch",
                    "main",
                    "--json",
                ]
            ),
            "publish-update pushed missing pushed_at fixture",
            "pushed_at",
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
                    "--payload-commit",
                    "payload1234",
                    "--published-commit",
                    "published1234",
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
        if (
            updated["publish"].get("payload_commit") != "payload1234"
            or updated["publish"].get("published_commit") != "published1234"
            or updated["publish"].get("status") != "pushed"
        ):
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
                "--manifest",
                str(manifest_path),
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
        for needle in ("## Status\n4.done", "## OpenSpec Stage\narchived", "## Next\n- done"):
            if needle not in text:
                sys.stderr.write(f"finalized card missing {needle!r}\n{text}\n")
                return 1
        for forbidden in ("abc1234", "push status"):
            if forbidden in text:
                sys.stderr.write(f"finalized card retained {forbidden!r}\n{text}\n")
                return 1
        if text.endswith("\n\n"):
            sys.stderr.write("finalized card ended with a blank line\n")
            return 1
        finalized_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if finalized_manifest["card"].get("path") != "openspec/board/4.done/example-card.md":
            sys.stderr.write(f"manifest card path was not finalized: {finalized_manifest['card']!r}\n")
            return 1
        if finalized_manifest["card"].get("status") != "4.done":
            sys.stderr.write(f"manifest card status was not finalized: {finalized_manifest['card']!r}\n")
            return 1
        if finalized_manifest["publish"].get("payload_commit") != "abc1234":
            sys.stderr.write(f"manifest payload commit was not recorded: {finalized_manifest['publish']!r}\n")
            return 1
        if card.exists():
            sys.stderr.write("source inprogress card still exists after finalization\n")
            return 1

        check_scope_reconciliation(Path(tmp))
        check_bare_remote_publish_finalization(Path(tmp))

    print("SMOKE_DELIVERY_MANIFEST_DERIVE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
