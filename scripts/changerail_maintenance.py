#!/usr/bin/env python3
"""Validate ChangeRail repository knowledge and render its generated index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from changerail_repository_knowledge import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_POLICY_PATH,
    RepositoryKnowledgeError,
    atomic_write_text,
    configured_index_path,
    dumps_result,
    render_index_content,
    require_valid_result,
    validate_catalog_and_policy,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="repository root, default: current directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-catalog", help="validate catalog and maintenance policy")
    add_common_paths(validate_parser)
    validate_parser.add_argument("--json", action="store_true", help="write structured JSON output")

    render_parser = subparsers.add_parser("render-index", help="render or check the generated knowledge index")
    add_common_paths(render_parser)
    render_parser.add_argument("--index", help="repository-relative generated index override")
    mode = render_parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check existing generated index without writing")
    mode.add_argument("--write", action="store_true", help="write the generated index")
    render_parser.add_argument("--json", action="store_true", help="write structured JSON output")

    scan_parser = subparsers.add_parser("scan", help="run read-only repository knowledge integrity detectors")
    add_common_paths(scan_parser)
    scan_parser.add_argument("--json", action="store_true", help="accepted for consistency; scan always writes JSON")
    scan_parser.add_argument(
        "--fail-on",
        choices=("info", "minor", "major", "blocker"),
        help="override the scan policy severity threshold",
    )
    return parser


def add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH.as_posix(), help="repository-relative catalog path")
    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH.as_posix(), help="repository-relative policy path")


def json_line(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def validation_failure(result_payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json_line(result_payload))
    else:
        print(f"repository knowledge validation failed: {result_payload['diagnostics']}", file=sys.stderr)
    return 1


def command_validate(args: argparse.Namespace) -> int:
    root = Path(args.workspace).resolve(strict=False)
    try:
        result = validate_catalog_and_policy(root=root, catalog_path=args.catalog, policy_path=args.policy)
    except RepositoryKnowledgeError as exc:
        payload = {"ok": False, "diagnostics": [{"code": "input_error", "message": str(exc), "path": "input"}]}
        return validation_failure(payload, json_output=args.json)
    payload = result.to_json()
    if args.json:
        print(dumps_result(result), end="")
        return 0 if result.ok else 1
    elif result.ok:
        print(f"VALIDATE_CATALOG_OK ({payload.get('catalog_records', 0)} records)")
    if not result.ok:
        return validation_failure(payload, json_output=args.json)
    return 0


def command_render(args: argparse.Namespace) -> int:
    root = Path(args.workspace).resolve(strict=False)
    try:
        result = validate_catalog_and_policy(root=root, catalog_path=args.catalog, policy_path=args.policy)
        require_valid_result(result)
        index_path = configured_index_path(root, result, args.index)
    except RepositoryKnowledgeError as exc:
        payload = {"ok": False, "diagnostics": [{"code": "input_error", "message": str(exc), "path": "input"}]}
        return validation_failure(payload, json_output=args.json)
    if result.catalog is None:
        payload = {"ok": False, "diagnostics": [{"code": "catalog_missing", "message": "catalog did not load", "path": args.catalog}]}
        return validation_failure(payload, json_output=args.json)

    rel_index = index_path.relative_to(root).as_posix()
    expected = render_index_content(
        result.catalog,
        catalog_path=result.catalog_path,
        policy_path=result.policy_path,
        index_path=rel_index,
    )

    payload: dict[str, Any] = {
        "ok": True,
        "mode": "write" if args.write else "check" if args.check else "render",
        "catalog_path": result.catalog_path,
        "policy_path": result.policy_path,
        "index_path": rel_index,
        "catalog_records": len(result.catalog.get("records", [])),
        "changed": False,
    }

    if args.write:
        previous = index_path.read_text(encoding="utf-8") if index_path.exists() else None
        atomic_write_text(index_path, expected)
        payload["changed"] = previous != expected
    elif args.check:
        try:
            current = index_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            payload.update({"ok": False, "diagnostics": [{"code": "index_missing", "path": rel_index, "message": "generated index is missing"}]})
        else:
            if current != expected:
                payload.update({"ok": False, "diagnostics": [{"code": "index_drift", "path": rel_index, "message": "generated index is stale"}]})
    else:
        payload["content"] = expected

    if args.json:
        print(json_line(payload))
    elif payload["ok"] and args.write:
        print(f"RENDER_INDEX_WRITE_OK {rel_index}")
    elif payload["ok"] and args.check:
        print(f"RENDER_INDEX_CHECK_OK {rel_index}")
    elif payload["ok"]:
        print(expected, end="")
    else:
        print(f"repository knowledge index check failed: {payload['diagnostics']}", file=sys.stderr)
    return 0 if payload["ok"] else 1


def command_scan(args: argparse.Namespace) -> int:
    from changerail_repository_knowledge import (
        scan_exit_code,
        scan_repository_knowledge,
        validate_scan_report,
    )

    root = Path(args.workspace).resolve(strict=False)
    report = scan_repository_knowledge(
        root=root,
        catalog_path=args.catalog,
        policy_path=args.policy,
        fail_on=args.fail_on,
    )
    errors = validate_scan_report(report)
    if errors:
        report = {
            "schema": "changerail.maintenance-scan-report.v1",
            "generated_at": report.get("generated_at", "1970-01-01T00:00:00Z"),
            "workspace": {"root": root.as_posix()},
            "catalog_path": args.catalog,
            "policy_path": args.policy,
            "complete": False,
            "fail_on": args.fail_on or "major",
            "detectors": [],
            "configuration_diagnostics": [
                {
                    "code": "scan_report_schema_error",
                    "path": "scan",
                    "message": "; ".join(errors),
                    "severity": "blocker",
                }
            ],
            "summary": {
                "detectors": 0,
                "findings": 0,
                "errors": 0,
                "max_severity": "none",
                "threshold_reached": False,
            },
        }
    print(json_line(report))
    return scan_exit_code(report)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate-catalog":
        return command_validate(args)
    if args.command == "render-index":
        return command_render(args)
    if args.command == "scan":
        return command_scan(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
