#!/usr/bin/env python3
"""Validate OPSX delivery manifests and derive staging proposals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_ID = "opsx.delivery-manifest.v1"
OPERATIONS = {"add", "modify", "delete", "rename", "unknown"}


class ManifestError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ManifestError(f"manifest cannot be read: {exc}", 2) from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest JSON is invalid: {exc}", 2) from exc


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
    errors: list[str] = []
    manifest = require_object(data, "manifest", errors)
    if manifest is None:
        return errors
    if manifest.get("schema") != SCHEMA_ID:
        errors.append(f"schema must be {SCHEMA_ID}")
    for field in (
        "workspace",
        "card",
        "changes",
        "committable_paths",
        "excluded_runtime_paths",
        "preexisting_dirty",
        "updated_at",
    ):
        if field not in manifest:
            errors.append(f"manifest.{field} is required")
    if isinstance(manifest.get("committable_paths"), list):
        for index, entry in enumerate(manifest["committable_paths"]):
            label = f"committable_paths[{index}]"
            item = require_object(entry, label, errors)
            if item is None:
                continue
            require_string(item, "path", label, errors)
            require_string(item, "kind", label, errors)
            require_string(item, "phase", label, errors)
            operation = item.get("operation")
            if operation is None:
                continue
            if operation not in OPERATIONS:
                errors.append(f"{label}.operation must be one of: {', '.join(sorted(OPERATIONS))}")
            if operation == "rename":
                require_string(item, "source_path", label, errors)
                require_string(item, "target_path", label, errors)
            elif operation == "delete":
                require_string(item, "source_path", label, errors)
            elif operation in {"add", "modify"}:
                require_string(item, "target_path", label, errors)
    elif "committable_paths" in manifest:
        errors.append("manifest.committable_paths must be an array")
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
    print(json.dumps(payload, ensure_ascii=False) if args.json else f"ok: valid {SCHEMA_ID} manifest")
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
    print(json.dumps(payload, ensure_ascii=False) if args.json else "\n".join(paths))
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
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
