#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA = "changerail.drift-gate.v1"
GREEN_CLASSES = {"changerail_source", "explicitly_excluded"}
CHANGERAIL_LIKE_PATHS = (
    "AGENTS.md",
    "openspec",
    ".claude",
    ".codex",
    "bin/openspec",
    "bin/changerail-review-verdict",
    "bin/opsx-review-verdict",
)
SYMLINK_PATHS = (
    ".claude/skills",
    ".claude/commands/changerail",
    ".claude/commands/opsx",
    "bin/openspec",
    "bin/changerail-review-verdict",
    "bin/opsx-review-verdict",
)


@dataclass
class ProjectResult:
    name: str
    path: str
    class_: str
    status: str
    message: str
    excluded: bool
    exclude_reason: str | None
    verify_summary: dict[str, object] | None
    indicators: dict[str, object]

    def as_report_entry(self) -> dict[str, object]:
        data = asdict(self)
        data["class"] = data.pop("class_")
        return data


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def resolved_key(path: Path) -> str:
    return str(path.expanduser().resolve(strict=False))


def normalize_path(value: str, base: Path | None = None) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute() and base is not None:
        path = base / path
    return path.resolve(strict=False)


def load_json_config(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read config {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid config JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config {path} must be a JSON object")
    return data


def entry_path(entry: object, key: str = "path") -> str:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict) and isinstance(entry.get(key), str):
        return entry[key]
    raise ValueError(f"inventory entry must be a string or object with {key!r}")


def entry_reason(entry: object) -> str | None:
    if isinstance(entry, dict) and isinstance(entry.get("reason"), str):
        return entry["reason"]
    return None


def list_from_config(data: dict[str, object], key: str) -> list[object]:
    value = data.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"config key {key!r} must be an array")
    return value


def safe_config_entries(data: dict[str, object], key: str, errors: list[str]) -> list[object]:
    try:
        return list_from_config(data, key)
    except ValueError as exc:
        errors.append(str(exc))
        return []


def parse_cli_exclude(value: str) -> tuple[str, str | None]:
    path, sep, reason = value.partition(":")
    return path, reason if sep and reason else None


def collect_inventory(args: argparse.Namespace) -> tuple[list[Path], dict[str, str | None], list[Path], str, list[str]]:
    errors: list[str] = []
    config_data: dict[str, object] = {}
    config_base: Path | None = None
    config_source = "cli"

    if args.config:
        config_path = args.config.resolve(strict=False)
        config_base = config_path.parent
        config_source = str(config_path)
        try:
            config_data = load_json_config(config_path)
        except ValueError as exc:
            errors.append(str(exc))

    projects_by_key: dict[str, Path] = {}
    excludes: dict[str, str | None] = {}
    legacy_roots: list[Path] = []

    def add_project(path: Path) -> None:
        projects_by_key.setdefault(resolved_key(path), path)

    for entry in safe_config_entries(config_data, "projects", errors) if config_data else []:
        try:
            add_project(normalize_path(entry_path(entry), config_base))
        except ValueError as exc:
            errors.append(str(exc))

    for entry in safe_config_entries(config_data, "workspace_roots", errors) if config_data else []:
        try:
            root = normalize_path(entry_path(entry), config_base)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not root.is_dir():
            errors.append(f"workspace root is not a directory: {root}")
            continue
        for child in sorted(root.iterdir(), key=lambda item: item.name):
            if child.is_dir():
                add_project(child.resolve(strict=False))

    for entry in safe_config_entries(config_data, "exclude", errors) if config_data else []:
        try:
            path = normalize_path(entry_path(entry), config_base)
            excludes[resolved_key(path)] = entry_reason(entry)
            add_project(path)
        except ValueError as exc:
            errors.append(str(exc))

    for entry in safe_config_entries(config_data, "legacy_roots", errors) if config_data else []:
        try:
            legacy_roots.append(normalize_path(entry_path(entry), config_base))
        except ValueError as exc:
            errors.append(str(exc))

    for value in args.workspace_root or []:
        root = normalize_path(value)
        if not root.is_dir():
            errors.append(f"workspace root is not a directory: {root}")
            continue
        for child in sorted(root.iterdir(), key=lambda item: item.name):
            if child.is_dir():
                add_project(child.resolve(strict=False))

    for value in args.project or []:
        add_project(normalize_path(value))

    for value in args.exclude or []:
        path_text, reason = parse_cli_exclude(value)
        path = normalize_path(path_text)
        excludes[resolved_key(path)] = reason
        add_project(path)

    for value in args.legacy_root or []:
        legacy_roots.append(normalize_path(value))

    projects = sorted(projects_by_key.values(), key=lambda item: str(item))
    if not projects and not errors:
        errors.append("no drift inventory provided; pass --config, --workspace-root or --project")
    return projects, excludes, legacy_roots, config_source, errors


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def existing_indicators(project: Path) -> list[str]:
    found: list[str] = []
    for rel in CHANGERAIL_LIKE_PATHS:
        path = project / rel
        if path.exists() or path.is_symlink():
            found.append(rel)
    return found


def symlink_targets(project: Path) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    candidates = [project / rel for rel in SYMLINK_PATHS]
    codex_skills = project / ".codex" / "skills"
    if codex_skills.is_dir():
        candidates.extend(sorted(codex_skills.iterdir(), key=lambda item: item.name))

    for path in candidates:
        if not path.is_symlink():
            continue
        rel = str(path.relative_to(project))
        try:
            target = path.resolve(strict=True)
            targets.append({"path": rel, "resolved_target": str(target), "status": "resolved"})
        except OSError as exc:
            targets.append({"path": rel, "resolved_target": "", "status": f"broken: {exc}"})
    return targets


def legacy_symlinks(project: Path, legacy_roots: Iterable[Path]) -> list[dict[str, str]]:
    roots = [root.resolve(strict=False) for root in legacy_roots]
    matches: list[dict[str, str]] = []
    for target in symlink_targets(project):
        if target["status"] != "resolved":
            continue
        resolved = Path(target["resolved_target"]).resolve(strict=False)
        if any(is_relative_to(resolved, root) for root in roots):
            matches.append(target)
    return matches


def run_verify(project: Path, changerail_root: Path) -> tuple[int, dict[str, object] | None, str]:
    try:
        result = subprocess.run(
            [
                str(changerail_root / "bin" / "verify-project"),
                str(project),
                "--changerail-root",
                str(changerail_root),
                "--json",
            ],
            cwd=changerail_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ, "OPENSPEC_TELEMETRY": "0"},
            timeout=240,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, None, f"verify-project timed out after {exc.timeout} seconds"
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = None
    return result.returncode, data, result.stdout.strip()


def summarize_verify(data: dict[str, object] | None, fallback: str) -> dict[str, object] | None:
    if data is None:
        return {"status": "error", "message": fallback}
    summary = data.get("summary")
    if isinstance(summary, dict):
        return summary
    return {"status": "error", "message": "verify-project did not emit a summary"}


def classify_project(
    *,
    project: Path,
    excludes: dict[str, str | None],
    legacy_roots: list[Path],
    changerail_root: Path,
) -> ProjectResult:
    key = resolved_key(project)
    indicators = existing_indicators(project)
    symlinks = symlink_targets(project)
    indicator_data: dict[str, object] = {
        "exists": project.exists(),
        "is_dir": project.is_dir(),
        "changerail_like_paths": indicators,
        "symlinks": symlinks,
    }

    if key in excludes:
        return ProjectResult(
            name=project.name,
            path=key,
            class_="explicitly_excluded",
            status="pass",
            message="project is explicitly excluded from drift enforcement",
            excluded=True,
            exclude_reason=excludes[key],
            verify_summary=None,
            indicators=indicator_data,
        )

    if not project.is_dir():
        return ProjectResult(
            name=project.name,
            path=key,
            class_="disconnected",
            status="fail",
            message="project path is not a directory",
            excluded=False,
            exclude_reason=None,
            verify_summary=None,
            indicators=indicator_data,
        )

    verify_code, verify_data, verify_output = run_verify(project, changerail_root)
    verify_summary = summarize_verify(verify_data, verify_output)
    if verify_code == 0:
        return ProjectResult(
            name=project.name,
            path=key,
            class_="changerail_source",
            status="pass",
            message="verify-project passed",
            excluded=False,
            exclude_reason=None,
            verify_summary=verify_summary,
            indicators=indicator_data,
        )

    legacy_matches = legacy_symlinks(project, legacy_roots)
    indicator_data["legacy_symlinks"] = legacy_matches
    if legacy_matches:
        return ProjectResult(
            name=project.name,
            path=key,
            class_="legacy_source",
            status="fail",
            message="project resolves agent/helper wiring under a configured legacy root",
            excluded=False,
            exclude_reason=None,
            verify_summary=verify_summary,
            indicators=indicator_data,
        )

    if indicators or symlinks:
        return ProjectResult(
            name=project.name,
            path=key,
            class_="broken_wiring",
            status="fail",
            message="ChangeRail-like files are present but verify-project failed",
            excluded=False,
            exclude_reason=None,
            verify_summary=verify_summary,
            indicators=indicator_data,
        )

    return ProjectResult(
        name=project.name,
        path=key,
        class_="disconnected",
        status="fail",
        message="no ChangeRail indicators were found",
        excluded=False,
        exclude_reason=None,
        verify_summary=verify_summary,
        indicators=indicator_data,
    )


def summarize(results: list[ProjectResult], errors: list[str]) -> dict[str, object]:
    classes: dict[str, int] = {}
    for result in results:
        classes[result.class_] = classes.get(result.class_, 0) + 1
    failed_projects = sum(1 for result in results if result.status != "pass")
    failed = failed_projects + len(errors)
    passed = len(results) - failed_projects
    return {
        "status": "fail" if failed else "pass",
        "total": len(results) + len(errors),
        "passed": passed,
        "failed": failed,
        "classes": classes,
        "errors": len(errors),
    }


def build_report(
    *,
    run_id: str,
    changerail_root: Path,
    config_source: str,
    projects: list[Path],
    excludes: dict[str, str | None],
    legacy_roots: list[Path],
    errors: list[str],
) -> dict[str, object]:
    results = [
        classify_project(project=project, excludes=excludes, legacy_roots=legacy_roots, changerail_root=changerail_root)
        for project in projects
    ]
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "changerail_root": str(changerail_root),
        "config_source": config_source,
        "summary": summarize(results, errors),
        "errors": errors,
        "projects": [result.as_report_entry() for result in results],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ChangeRail workspace drift smoke checks.")
    parser.add_argument("--config", type=Path, default=None, help="JSON inventory config, often under internal/.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script(), help="ChangeRail repository root.")
    parser.add_argument("--runtime-root", type=Path, default=None, help="Runtime output root.")
    parser.add_argument("--run-id", default=utc_run_id(), help="Run id used under runtime output root.")
    parser.add_argument("--report", type=Path, default=None, help="Explicit report path.")
    parser.add_argument("--workspace-root", action="append", help="Workspace root whose direct child directories are checked.")
    parser.add_argument("--project", action="append", help="Explicit project path to include.")
    parser.add_argument("--exclude", action="append", help="Explicitly excluded project path, optionally PATH:reason.")
    parser.add_argument("--legacy-root", action="append", help="Legacy source root used to classify legacy symlink targets.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve(strict=False)
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "drift-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"

    projects, excludes, legacy_roots, config_source, errors = collect_inventory(args)
    report = build_report(
        run_id=args.run_id,
        changerail_root=changerail_root,
        config_source=config_source,
        projects=projects,
        excludes=excludes,
        legacy_roots=legacy_roots,
        errors=errors,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"report: {report_path}")
    print(
        "summary: "
        f"{summary['status']} "
        f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
    )
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
