#!/usr/bin/env python3
"""Validate ChangeRail repository knowledge and render its generated index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from changerail_repository_knowledge import (
    DEFAULT_BASELINE_PATH,
    DEFAULT_CATALOG_PATH,
    DEFAULT_MAINTENANCE_RUNTIME_ROOT,
    DEFAULT_POLICY_PATH,
    RepositoryKnowledgeError,
    atomic_write_text,
    baseline_from_report,
    configured_index_path,
    dumps_result,
    load_maintenance_baseline,
    merge_baseline,
    normalize_maintenance_report,
    normalize_triage_annotations,
    read_lifecycle_report,
    render_index_content,
    require_valid_result,
    scan_exit_code,
    validate_catalog_and_policy,
    validate_maintenance_baseline,
    upsert_maintenance_card,
    write_maintenance_baseline,
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

    report_parser = subparsers.add_parser("report", help="emit normalized maintenance lifecycle report")
    add_common_paths(report_parser)
    report_parser.add_argument("--baseline", default=DEFAULT_BASELINE_PATH.as_posix(), help="repository-relative baseline path")
    report_parser.add_argument(
        "--state",
        help="repository-relative runtime state path below .runtime/changerail/maintenance/",
    )
    report_parser.add_argument("--scan-report", help="repository-relative scan report JSON to normalize instead of running scan")
    report_parser.add_argument("--write-state", action="store_true", help="atomically update ignored lifecycle state")
    report_parser.add_argument("--json", action="store_true", help="accepted for consistency; report always writes JSON")
    report_parser.add_argument(
        "--fail-on",
        choices=("info", "minor", "major", "blocker"),
        help="override the scan policy severity threshold",
    )

    baseline_parser = subparsers.add_parser("accept-baseline", help="preview or write maintenance baseline acceptance")
    add_common_paths(baseline_parser)
    baseline_parser.add_argument("--baseline", default=DEFAULT_BASELINE_PATH.as_posix(), help="repository-relative baseline path")
    baseline_parser.add_argument("--report", help="repository-relative lifecycle report JSON to use")
    baseline_parser.add_argument("--owner", default="ChangeRail core", help="owner stored on generated accepted entries")
    baseline_parser.add_argument("--reason", default="accepted by maintenance baseline command", help="reason stored on generated accepted entries")
    baseline_parser.add_argument("--write", action="store_true", help="write the tracked baseline file")
    baseline_parser.add_argument("--json", action="store_true", help="write structured JSON output")

    triage_parser = subparsers.add_parser("triage", help="validate and normalize maintenance triage annotations")
    triage_parser.add_argument("--annotations", required=True, help="repository-relative triage annotation JSON")
    triage_parser.add_argument("--json", action="store_true", help="write structured JSON output")

    cards_parser = subparsers.add_parser("cards", help="preview or upsert board cards for open maintenance findings")
    add_common_paths(cards_parser)
    cards_parser.add_argument("--baseline", default=DEFAULT_BASELINE_PATH.as_posix(), help="repository-relative baseline path")
    cards_parser.add_argument("--report", help="repository-relative lifecycle report JSON to use")
    cards_parser.add_argument("--write", action="store_true", help="write or update tracked board cards")
    cards_parser.add_argument("--json", action="store_true", help="write structured JSON output")
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


def _read_json_path(root: Path, raw_path: str) -> dict[str, Any]:
    from changerail_repository_knowledge import resolve_input_path

    path = resolve_input_path(root, raw_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RepositoryKnowledgeError(f"JSON file cannot be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RepositoryKnowledgeError(f"JSON file is invalid: {exc}") from exc
    if not isinstance(payload, dict):
        raise RepositoryKnowledgeError("JSON file must contain one object")
    return payload


def _lifecycle_report_for_args(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    from changerail_repository_knowledge import scan_repository_knowledge

    root = Path(args.workspace).resolve(strict=False)
    if getattr(args, "report", None):
        from changerail_repository_knowledge import resolve_input_path

        path = resolve_input_path(root, args.report)
        report = read_lifecycle_report(path)
        return report, 0 if report.get("complete") else 2
    if getattr(args, "scan_report", None):
        scan_report = _read_json_path(root, args.scan_report)
    else:
        scan_report = scan_repository_knowledge(
            root=root,
            catalog_path=args.catalog,
            policy_path=args.policy,
            fail_on=getattr(args, "fail_on", None),
        )
    return normalize_maintenance_report(
        scan_report,
        root=root,
        state_path=getattr(args, "state", None),
        baseline_path=getattr(args, "baseline", None),
        write_state=getattr(args, "write_state", False),
    )


def command_report(args: argparse.Namespace) -> int:
    report, exit_code = _lifecycle_report_for_args(args)
    print(json_line(report))
    return exit_code


def command_accept_baseline(args: argparse.Namespace) -> int:
    root = Path(args.workspace).resolve(strict=False)
    report, report_exit = _lifecycle_report_for_args(args)
    if report_exit == 2 or not report.get("complete"):
        print(json_line(report))
        return 2
    generated = baseline_from_report(report, owner=args.owner, reason=args.reason)
    existing, configured, diagnostics, baseline_rel_path = load_maintenance_baseline(root, args.baseline)
    if diagnostics:
        payload = {"ok": False, "diagnostics": diagnostics, "baseline_path": baseline_rel_path}
        print(json_line(payload))
        return 1
    merged = merge_baseline(existing if configured else {"schema": generated["schema"], "accepted": [], "waivers": []}, generated)
    errors = validate_maintenance_baseline(merged)
    if errors:
        payload = {"ok": False, "diagnostics": [{"code": "maintenance_baseline_schema_error", "path": baseline_rel_path, "message": "; ".join(errors), "severity": "blocker"}]}
        print(json_line(payload))
        return 1
    if args.write:
        written_path = write_maintenance_baseline(root, merged, args.baseline)
        payload = {"ok": True, "mode": "write", "baseline_path": written_path, "accepted": len(merged["accepted"])}
    else:
        preview_path = root / DEFAULT_MAINTENANCE_RUNTIME_ROOT / "previews" / "maintenance-baseline.yaml"
        atomic_write_text(preview_path, __import__("yaml").safe_dump(merged, sort_keys=False, allow_unicode=False))
        payload = {
            "ok": True,
            "mode": "preview",
            "baseline_path": baseline_rel_path,
            "preview_path": preview_path.relative_to(root).as_posix(),
            "accepted": len(merged["accepted"]),
        }
    print(json_line(payload) if args.json else json_line(payload))
    return 0


def command_triage(args: argparse.Namespace) -> int:
    from changerail_repository_knowledge import resolve_input_path

    root = Path(args.workspace).resolve(strict=False)
    try:
        normalized = normalize_triage_annotations(resolve_input_path(root, args.annotations))
    except RepositoryKnowledgeError as exc:
        payload = {"ok": False, "diagnostics": [{"code": "maintenance_triage_invalid", "path": args.annotations, "message": str(exc), "severity": "blocker"}]}
        print(json_line(payload))
        return 1
    print(json_line(normalized))
    return 0


def command_cards(args: argparse.Namespace) -> int:
    root = Path(args.workspace).resolve(strict=False)
    report, report_exit = _lifecycle_report_for_args(args)
    if report_exit == 2 or not report.get("complete"):
        print(json_line(report))
        return 2
    results = [
        upsert_maintenance_card(root, finding, write=args.write)
        for finding in report.get("findings", [])
        if isinstance(finding, dict) and finding.get("status") == "open"
    ]
    ok = all(result.get("ok") for result in results)
    payload = {
        "ok": ok,
        "mode": "write" if args.write else "preview",
        "cards": results,
        "card_count": len(results),
    }
    print(json_line(payload))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate-catalog":
        return command_validate(args)
    if args.command == "render-index":
        return command_render(args)
    if args.command == "scan":
        return command_scan(args)
    if args.command == "report":
        return command_report(args)
    if args.command == "accept-baseline":
        return command_accept_baseline(args)
    if args.command == "triage":
        return command_triage(args)
    if args.command == "cards":
        return command_cards(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
