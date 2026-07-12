#!/usr/bin/env python3
"""Validate, derive and update ChangeRail delivery manifests."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from changerail_contract_schema import validate_with_schema

SCHEMA_ID = "changerail.delivery-manifest.v1"
SCHEMA_FILE = "changerail-delivery-manifest.schema.json"
OPERATIONS = {"add", "modify", "delete", "rename", "unknown"}
CHANGE_RE = re.compile(r"^## Change\s+[0-9]+:\s*`?([a-z0-9][a-z0-9-]*)`?", re.MULTILINE)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


class ManifestError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManifestError(f"manifest cannot be read: {exc}", 2) from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest JSON is invalid: {exc}", 2) from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def json_line(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    errors.append(f"{label} must be an object")
    return None


def require_string(data: dict[str, Any], field: str, label: str, errors: list[str]) -> str | None:
    value = data.get(field)
    if isinstance(value, str) and value.strip():
        return value
    errors.append(f"{label}.{field} must be a non-empty string")
    return None


def validate_manifest(data: Any) -> list[str]:
    errors = validate_with_schema(data, SCHEMA_FILE)
    if errors:
        return errors
    return validate_manifest_semantics(data)


def validate_manifest_semantics(data: Any) -> list[str]:
    errors: list[str] = []
    manifest = require_object(data, "manifest", errors)
    if manifest is None:
        return errors
    for index, entry in enumerate(manifest["committable_paths"]):
        operation = entry.get("operation")
        label = f"committable_paths[{index}]"
        if operation is not None and operation not in OPERATIONS:
            errors.append(f"{label}.operation must be one of: {', '.join(sorted(OPERATIONS))}")
    return errors


def staging_paths(data: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()

    def add(path: str | None) -> None:
        if path and path not in seen:
            seen.add(path)
            paths.append(path)

    for entry in data.get("committable_paths", []):
        if not isinstance(entry, dict):
            continue
        operation = entry.get("operation")
        if operation == "rename":
            add(entry.get("source_path"))
            add(entry.get("target_path"))
        elif operation == "delete":
            add(entry.get("source_path"))
        elif operation in {"add", "modify"}:
            add(entry.get("target_path"))
        else:
            add(entry.get("path"))
    return paths


def git_output(workspace: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ManifestError(f"git {' '.join(args)}: {detail}", 2)
    return result.stdout


def git_output_bytes(workspace: Path, args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (
            result.stderr.decode("utf-8", errors="replace").strip()
            or result.stdout.decode("utf-8", errors="replace").strip()
            or "git command failed"
        )
        raise ManifestError(f"git {' '.join(args)}: {detail}", 2)
    return result.stdout


def relpath(path: Path, workspace: Path) -> str:
    return path.resolve(strict=False).relative_to(workspace.resolve(strict=False)).as_posix()


def card_id(card_path: str) -> str:
    return Path(card_path).name.removesuffix(".md")


def read_card(card: Path, workspace: Path) -> tuple[str, dict[str, Any]]:
    path = card if card.is_absolute() else workspace / card
    if not path.is_file():
        raise ManifestError(f"card cannot be read: {path}", 2)
    text = path.read_text(encoding="utf-8")
    rel = relpath(path, workspace)
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    status = section_body(text, "Status").strip().splitlines()
    return text, {
        "id": card_id(rel),
        "path": rel,
        "title": title,
        "status": status[0].strip() if status else "",
    }


def section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1) if match else ""


def set_section_body(text: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\s*\n)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    if pattern.search(text):
        return pattern.sub(lambda match: f"{match.group(1)}{body.rstrip()}\n\n", text, count=1)
    suffix = "" if text.endswith("\n") else "\n"
    return f"{text}{suffix}\n## {heading}\n{body.rstrip()}\n"


def parse_change_slugs(card_text: str) -> list[str]:
    slugs: list[str] = []

    def add(slug: str) -> None:
        if slug and slug not in slugs:
            slugs.append(slug)

    for line in section_body(card_text, "Change Set").splitlines():
        match = re.search(r"`([a-z0-9][a-z0-9-]*)`", line)
        if match:
            add(match.group(1))
    for match in CHANGE_RE.finditer(card_text):
        add(match.group(1))
    return slugs


def find_archive_path(workspace: Path, slug: str) -> str | None:
    archive_root = workspace / "openspec" / "changes" / "archive"
    if not archive_root.is_dir():
        return None
    matches = sorted(path for path in archive_root.glob(f"*-{slug}") if path.is_dir())
    return relpath(matches[-1], workspace) if matches else None


def classify_changes(workspace: Path, slugs: list[str]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for index, slug in enumerate(slugs, start=1):
        active = workspace / "openspec" / "changes" / slug
        archive = find_archive_path(workspace, slug)
        entry: dict[str, Any] = {"slug": slug, "order": index}
        if archive:
            entry.update({"state": "archived", "archive_path": archive})
        elif active.is_dir():
            entry.update({"state": "active", "active_path": relpath(active, workspace)})
        else:
            entry.update({"state": "planned"})
        changes.append(entry)
    return changes


def path_kind(path: str) -> str:
    if path.startswith("openspec/board/"):
        return "board"
    if path.startswith("openspec/changes/archive/"):
        return "openspec_archive"
    if path.startswith("openspec/changes/"):
        return "openspec_change"
    if path.startswith("openspec/specs/"):
        return "openspec_spec"
    if path.startswith("skills/"):
        return "skill"
    if path.startswith("claude/commands/"):
        return "claude_command"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("bin/"):
        return "helper"
    if path.startswith("templates/"):
        return "template"
    if path.startswith("docs/"):
        return "docs"
    if path.startswith(".github/"):
        return "ci"
    return "other"


def path_phase(path: str) -> str:
    if path.startswith("openspec/changes/archive/"):
        return "archive"
    if path.startswith("openspec/changes/"):
        return "ff"
    if path.startswith("openspec/specs/"):
        return "sync-specs"
    if path.startswith("openspec/board/"):
        return "board"
    return "do"


def operation_entry(path: str, status: str, source_path: str | None = None) -> dict[str, Any]:
    status_code = status.strip()
    entry: dict[str, Any] = {
        "path": path,
        "kind": path_kind(path),
        "phase": path_phase(path),
    }
    if "R" in status:
        entry.update(
            {
                "operation": "rename",
                "source_path": source_path or path,
                "target_path": path,
            }
        )
    elif status_code == "??" or "A" in status:
        entry.update({"operation": "add", "target_path": path})
    elif "D" in status:
        entry.update({"operation": "delete", "source_path": source_path or path})
    elif "M" in status or status_code:
        entry.update({"operation": "modify", "target_path": path})
    else:
        entry.update({"operation": "unknown"})
    return entry


def decode_git_path(raw_path: bytes) -> str:
    return os.fsdecode(raw_path).rstrip("/")


def ensure_safe_untracked_path(workspace: Path, path: str) -> None:
    absolute = workspace / path
    if absolute.is_dir():
        raise ManifestError(f"untracked directory cannot be staged as a directory-wide path: {path}", 1)
    if absolute.exists() and not (absolute.is_file() or absolute.is_symlink()):
        raise ManifestError(f"untracked path is not a regular file: {path}", 1)


def git_status_entries(workspace: Path) -> list[dict[str, Any]]:
    output = git_output_bytes(workspace, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    records = [record for record in output.split(b"\x00") if record]
    entries: list[dict[str, Any]] = []
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4:
            raise ManifestError("git status produced an invalid porcelain record", 2)
        status = record[:2].decode("ascii", errors="replace")
        path = decode_git_path(record[3:])
        source_path: str | None = None
        if "R" in status or "C" in status:
            index += 1
            if index >= len(records):
                raise ManifestError(f"git status missing source path for rename/copy target: {path}", 2)
            source_path = decode_git_path(records[index])
        if status == "??":
            ensure_safe_untracked_path(workspace, path)
        entries.append(operation_entry(path, status, source_path))
        index += 1
    return entries


def add_unique_path(entries: list[dict[str, Any]], path: str, operation: str = "unknown") -> None:
    if any(entry.get("path") == path for entry in entries):
        return
    entry: dict[str, Any] = {
        "path": path,
        "kind": path_kind(path),
        "phase": path_phase(path),
        "operation": operation,
    }
    if operation == "add":
        entry["target_path"] = path
    entries.append(entry)


def add_unique_tree_paths(entries: list[dict[str, Any]], workspace: Path, path: str, operation: str = "unknown") -> None:
    absolute = workspace / path
    if not absolute.is_dir():
        add_unique_path(entries, path, operation)
        return
    files = sorted(
        candidate
        for candidate in absolute.rglob("*")
        if candidate.is_file() or candidate.is_symlink()
    )
    if not files:
        raise ManifestError(f"directory path contains no committable files: {path}", 1)
    for candidate in files:
        add_unique_path(entries, relpath(candidate, workspace), operation)


def default_manifest_path(workspace: Path, card: dict[str, Any]) -> Path:
    return workspace / ".runtime" / "changerail" / "delivery-manifests" / f"{card['id']}.json"


def derive_manifest(card_path: Path, workspace: Path) -> dict[str, Any]:
    workspace = workspace.resolve(strict=False)
    card_text, card = read_card(card_path, workspace)
    changes = classify_changes(workspace, parse_change_slugs(card_text))
    committable_paths = git_status_entries(workspace)
    add_unique_path(committable_paths, str(card["path"]), "unknown")
    for change in changes:
        archive_path = change.get("archive_path")
        active_path = change.get("active_path")
        if isinstance(archive_path, str):
            add_unique_tree_paths(committable_paths, workspace, archive_path, "add")
        elif isinstance(active_path, str):
            add_unique_tree_paths(committable_paths, workspace, active_path, "add")
    manifest_path = default_manifest_path(workspace, card)
    verdict_base = workspace / ".runtime" / "changerail" / "reviews" / f"{card['id']}.json"
    return {
        "schema": SCHEMA_ID,
        "updated_at": utc_now(),
        "workspace": {
            "root": str(workspace),
            "repository": repository_id(workspace),
        },
        "card": card,
        "changes": changes,
        "committable_paths": committable_paths,
        "excluded_runtime_paths": [
            {
                "path": relpath(manifest_path, workspace),
                "kind": "manifest",
                "phase": "do",
                "reason": "Ignored runtime delivery manifest.",
            },
            {
                "path": relpath(verdict_base, workspace),
                "kind": "review-verdict",
                "phase": "review",
                "reason": "Ignored runtime review verdict.",
            },
            {
                "path": relpath(verdict_base.with_name(verdict_base.stem + ".history.json"), workspace),
                "kind": "review-history",
                "phase": "review",
                "reason": "Ignored runtime review-cycle history.",
            },
        ],
        "preexisting_dirty": [],
        "publish": {"status": "pending"},
    }


def repository_id(workspace: Path) -> str:
    try:
        remote = git_output(workspace, ["config", "--get", "remote.origin.url"]).strip()
    except ManifestError:
        remote = ""
    return remote or workspace.name


def update_publish(manifest_path: Path, args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    errors = validate_manifest(manifest)
    if errors:
        raise ManifestError("; ".join(errors), 1)
    publish = {"status": args.status}
    for field in ("commit", "remote", "branch", "pushed_at", "committed_at", "reason", "mode"):
        value = getattr(args, field)
        if value:
            publish[field] = value
    manifest["publish"] = publish
    manifest["updated_at"] = utc_now()
    write_json(manifest_path, manifest)
    return manifest


def finalize_card(card_path: Path, workspace: Path, args: argparse.Namespace) -> dict[str, str]:
    source = card_path if card_path.is_absolute() else workspace / card_path
    if not source.is_file():
        raise ManifestError(f"card cannot be read: {source}", 2)
    target = source
    if source.parent.name == "3.inprogress":
        target = source.parents[1] / "4.done" / source.name
    if target != source and target.exists():
        raise ManifestError(f"target card already exists: {target}", 1)

    text = source.read_text(encoding="utf-8")
    text = set_section_body(text, "Status", "4.done")
    text = set_section_body(text, "Owner", "unassigned")
    text = set_section_body(text, "OpenSpec Stage", "archived")
    text = set_section_body(text, "Next", "- done")

    publish_sentence = (
        f"Published reviewed payload as `{args.commit}`; push status `{args.push_status}`"
        f" on `{args.branch}`/`{args.remote}`."
    )
    result_body = section_body(text, "Result").strip()
    if args.commit not in result_body:
        if result_body and result_body != "not started":
            result_body = f"{result_body}\n\n{publish_sentence}"
        else:
            result_body = publish_sentence
        text = set_section_body(text, "Result", result_body)

    log_body = section_body(text, "Log").rstrip()
    log_line = (
        f"- {args.timestamp} publish finalized card into `4.done` with commit "
        f"`{args.commit}` and push status `{args.push_status}`."
    )
    if log_line not in log_body:
        text = set_section_body(text, "Log", f"{log_body}\n{log_line}" if log_body else log_line)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    if target != source:
        source.unlink()
    return {"source_path": relpath(source, workspace), "target_path": relpath(target, workspace)}


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_json(args.manifest)
    errors = validate_manifest(data)
    if errors:
        raise ManifestError("; ".join(errors), 1)
    payload = {
        "ok": True,
        "command": "validate",
        "manifest": str(args.manifest),
        "schema": SCHEMA_ID,
    }
    print(json_line(payload) if args.json else f"ok: valid {SCHEMA_ID} manifest")
    return 0


def cmd_staging_plan(args: argparse.Namespace) -> int:
    data = load_json(args.manifest)
    errors = validate_manifest(data)
    if errors:
        raise ManifestError("; ".join(errors), 1)
    paths = staging_paths(data)
    payload = {
        "ok": True,
        "command": "staging-plan",
        "manifest": str(args.manifest),
        "paths": paths,
    }
    if args.json:
        print(json_line(payload))
    else:
        for path in paths:
            sys.stdout.buffer.write(os.fsencode(path) + b"\n")
    return 0


def cmd_derive(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    manifest = derive_manifest(args.card, workspace)
    manifest_path = args.manifest or default_manifest_path(workspace, manifest["card"])
    errors = validate_manifest(manifest)
    if errors:
        raise ManifestError("; ".join(errors), 1)
    if args.write:
        write_json(manifest_path, manifest)
    payload = {
        "ok": True,
        "command": "derive",
        "manifest": str(manifest_path),
        "written": args.write,
        "schema": SCHEMA_ID,
    }
    if args.json:
        payload["data"] = manifest
        print(json_line(payload))
    else:
        print(f"ok: derived {SCHEMA_ID} manifest at {manifest_path}")
    return 0


def cmd_publish_update(args: argparse.Namespace) -> int:
    manifest = update_publish(args.manifest, args)
    payload = {
        "ok": True,
        "command": "publish-update",
        "manifest": str(args.manifest),
        "publish": manifest["publish"],
    }
    print(json_line(payload) if args.json else f"ok: updated publish state at {args.manifest}")
    return 0


def cmd_finalize_card(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    paths = finalize_card(args.card, workspace, args)
    payload = {"ok": True, "command": "finalize-card", **paths}
    print(json_line(payload) if args.json else f"ok: finalized {paths['target_path']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a delivery manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_validate)

    staging = subparsers.add_parser("staging-plan", help="print manifest staging paths")
    staging.add_argument("manifest", type=Path)
    staging.add_argument("--json", action="store_true")
    staging.set_defaults(func=cmd_staging_plan)

    derive = subparsers.add_parser("derive", help="derive a manifest from a board card and git status")
    derive.add_argument("card", type=Path)
    derive.add_argument("--workspace", type=Path, default=Path("."))
    derive.add_argument("--manifest", type=Path)
    derive.add_argument("--write", action="store_true")
    derive.add_argument("--json", action="store_true")
    derive.set_defaults(func=cmd_derive)

    publish = subparsers.add_parser("publish-update", help="update ignored manifest publish metadata")
    publish.add_argument("manifest", type=Path)
    publish.add_argument("--status", default="pending", choices=["pending", "staged", "committed", "pushed", "skipped", "failed"])
    publish.add_argument("--commit")
    publish.add_argument("--remote")
    publish.add_argument("--branch")
    publish.add_argument("--pushed-at")
    publish.add_argument("--committed-at")
    publish.add_argument("--reason")
    publish.add_argument("--mode")
    publish.add_argument("--json", action="store_true")
    publish.set_defaults(func=cmd_publish_update)

    finalize = subparsers.add_parser("finalize-card", help="move a reviewed board card to done and update metadata")
    finalize.add_argument("card", type=Path)
    finalize.add_argument("--workspace", type=Path, default=Path("."))
    finalize.add_argument("--commit", required=True)
    finalize.add_argument("--remote", default="origin")
    finalize.add_argument("--branch", required=True)
    finalize.add_argument("--push-status", default="pending")
    finalize.add_argument("--timestamp", default=utc_now())
    finalize.add_argument("--json", action="store_true")
    finalize.set_defaults(func=cmd_finalize_card)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ManifestError as exc:
        if getattr(args, "json", False):
            print(
                json.dumps(
                    {
                        "schema": SCHEMA_ID,
                        "ok": False,
                        "command": getattr(args, "command", "unknown"),
                        "diagnostic": str(exc),
                    },
                    ensure_ascii=True,
                ),
                file=sys.stderr,
            )
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
