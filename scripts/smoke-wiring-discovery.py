#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA = "opsx.wiring-discovery-smoke.v1"
SKILLS = (
    "opsx-explore",
    "opsx-ff",
    "opsx-do",
    "opsx-review",
    "opsx-pub",
    "opsx-deliver",
    "openspec-apply-change",
    "openspec-archive-change",
    "openspec-bulk-archive-change",
    "openspec-continue-change",
    "openspec-explore",
    "openspec-ff-change",
    "openspec-new-change",
    "openspec-onboard",
    "openspec-propose",
    "openspec-sync-specs",
    "openspec-verify-change",
)
COMMANDS = {
    "explore": "opsx-explore",
    "ff": "opsx-ff",
    "do": "opsx-do",
    "review": "opsx-review",
    "pub": "opsx-pub",
    "deliver": "opsx-deliver",
}
FORBIDDEN_CONSUMER_ROOT_SKILLS = re.compile(r"(^|[\s`'\"])(\./)?skills/")


@dataclass
class Check:
    name: str
    path: str
    expected_target: str
    resolved_target: str
    status: str
    message: str
    mode: str
    surface: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def expand_selected(values: list[str] | None, allowed: tuple[str, ...]) -> list[str]:
    if not values or "all" in values:
        return list(allowed)
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def safe_resolve(path: Path) -> tuple[Path | None, str | None]:
    try:
        return path.resolve(strict=True), None
    except OSError as exc:
        try:
            return path.resolve(strict=False), str(exc)
        except OSError:
            return None, str(exc)


def check_symlink(
    *,
    name: str,
    path: Path,
    expected_target: Path,
    opsx_root: Path,
    mode: str,
    surface: str,
    require_relative_link: bool,
) -> Check:
    expected_resolved, expected_error = safe_resolve(expected_target)
    resolved, resolved_error = safe_resolve(path)

    failures: list[str] = []
    if expected_error:
        failures.append(f"expected target is not resolvable: {expected_error}")
    if not path.is_symlink():
        failures.append("path is not a symlink")
    if resolved_error:
        failures.append(f"path is not resolvable: {resolved_error}")
    if expected_resolved and resolved and resolved != expected_resolved:
        failures.append("resolved target differs from expected target")
    if resolved and not is_relative_to(resolved, opsx_root):
        failures.append("resolved target is outside opsx_root")
    if require_relative_link and path.is_symlink():
        raw_target = os.readlink(path)
        if Path(raw_target).is_absolute():
            failures.append("repo-local symlink target is absolute")

    status = "fail" if failures else "pass"
    message = "; ".join(failures) if failures else "symlink resolves to expected OPSX source"
    return Check(
        name=name,
        path=str(path),
        expected_target=str(expected_resolved or expected_target),
        resolved_target=str(resolved or ""),
        status=status,
        message=message,
        mode=mode,
        surface=surface,
    )


def frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "name":
            return value.strip().strip("\"'")
    return None


def check_skill_contract(
    *,
    skill_path: Path,
    expected_name: str,
    expected_source: Path,
    mode: str,
    surface: str,
) -> Check:
    skill_md = skill_path / "SKILL.md"
    expected_skill_md = expected_source / "SKILL.md"
    resolved, resolved_error = safe_resolve(skill_md)

    failures: list[str] = []
    actual_name = None
    if resolved_error:
        failures.append(f"SKILL.md is not resolvable: {resolved_error}")
    else:
        try:
            actual_name = frontmatter_name(skill_md)
        except OSError as exc:
            failures.append(f"SKILL.md cannot be read: {exc}")
    if actual_name != expected_name:
        failures.append(f"frontmatter name is {actual_name!r}, expected {expected_name!r}")

    status = "fail" if failures else "pass"
    message = "; ".join(failures) if failures else "SKILL.md frontmatter name matches"
    return Check(
        name=f"{surface} {mode} {expected_name} skill contract",
        path=str(skill_md),
        expected_target=str(expected_skill_md),
        resolved_target=str(resolved or ""),
        status=status,
        message=message,
        mode=mode,
        surface=surface,
    )


def check_command_wrapper(
    *,
    command_file: Path,
    command_name: str,
    expected_skill: str,
    expected_source: Path,
    mode: str,
    surface: str,
) -> Check:
    resolved, resolved_error = safe_resolve(command_file)
    failures: list[str] = []
    text = ""
    if resolved_error:
        failures.append(f"command wrapper is not resolvable: {resolved_error}")
    else:
        try:
            text = command_file.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append(f"command wrapper cannot be read: {exc}")

    if text:
        slash = f"/opsx:{command_name}"
        if expected_skill not in text:
            failures.append(f"wrapper does not mention {expected_skill}")
        if slash not in text:
            failures.append(f"wrapper does not mention {slash}")
        if FORBIDDEN_CONSUMER_ROOT_SKILLS.search(text):
            failures.append("wrapper references a consumer-root skills/ path")

    status = "fail" if failures else "pass"
    message = "; ".join(failures) if failures else "wrapper references expected skill without root skills/ path"
    return Check(
        name=f"claude {mode} /opsx:{command_name} wrapper contract",
        path=str(command_file),
        expected_target=str(expected_source),
        resolved_target=str(resolved or ""),
        status=status,
        message=message,
        mode=mode,
        surface=surface,
    )


def symlink_force(target: Path, link_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.exists():
        if link_path.is_dir() and not link_path.is_symlink():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    os.symlink(target, link_path)


def create_consumer_example(run_dir: Path, opsx_root: Path) -> Path:
    project = run_dir / "example-project"
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)

    symlink_force(opsx_root / "skills", project / ".claude" / "skills")
    symlink_force(opsx_root / "claude" / "commands" / "opsx", project / ".claude" / "commands" / "opsx")
    for skill in SKILLS:
        symlink_force(opsx_root / "skills" / skill, project / ".codex" / "skills" / skill)
    return project


def base_for_mode(mode: str, run_dir: Path, opsx_root: Path) -> Path:
    if mode == "repo-local":
        return opsx_root
    if mode == "consumer-example":
        return create_consumer_example(run_dir, opsx_root)
    raise ValueError(f"unsupported mode: {mode}")


def claude_checks(mode: str, base: Path, opsx_root: Path) -> list[Check]:
    checks: list[Check] = []
    require_relative = mode == "repo-local"
    skills_dir = base / ".claude" / "skills"
    commands_dir = base / ".claude" / "commands" / "opsx"
    checks.append(
        check_symlink(
            name=f"claude {mode} skills directory",
            path=skills_dir,
            expected_target=opsx_root / "skills",
            opsx_root=opsx_root,
            mode=mode,
            surface="claude",
            require_relative_link=require_relative,
        )
    )
    checks.append(
        check_symlink(
            name=f"claude {mode} commands directory",
            path=commands_dir,
            expected_target=opsx_root / "claude" / "commands" / "opsx",
            opsx_root=opsx_root,
            mode=mode,
            surface="claude",
            require_relative_link=require_relative,
        )
    )
    for skill in SKILLS:
        checks.append(
            check_skill_contract(
                skill_path=skills_dir / skill,
                expected_name=skill,
                expected_source=opsx_root / "skills" / skill,
                mode=mode,
                surface="claude",
            )
        )
    for command_name, skill in COMMANDS.items():
        checks.append(
            check_command_wrapper(
                command_file=commands_dir / f"{command_name}.md",
                command_name=command_name,
                expected_skill=skill,
                expected_source=opsx_root / "claude" / "commands" / "opsx" / f"{command_name}.md",
                mode=mode,
                surface="claude",
            )
        )
    return checks


def codex_checks(mode: str, base: Path, opsx_root: Path) -> list[Check]:
    checks: list[Check] = []
    require_relative = mode == "repo-local"
    for skill in SKILLS:
        skill_path = base / ".codex" / "skills" / skill
        source_path = opsx_root / "skills" / skill
        checks.append(
            check_symlink(
                name=f"codex {mode} {skill} skill directory",
                path=skill_path,
                expected_target=source_path,
                opsx_root=opsx_root,
                mode=mode,
                surface="codex",
                require_relative_link=require_relative,
            )
        )
        checks.append(
            check_skill_contract(
                skill_path=skill_path,
                expected_name=skill,
                expected_source=source_path,
                mode=mode,
                surface="codex",
            )
        )
    return checks


def summarize(checks: Iterable[Check]) -> dict[str, int | str]:
    materialized = list(checks)
    failed = sum(1 for check in materialized if check.status != "pass")
    passed = len(materialized) - failed
    return {
        "status": "fail" if failed else "pass",
        "total": len(materialized),
        "passed": passed,
        "failed": failed,
    }


def build_report(run_id: str, opsx_root: Path, run_dir: Path, modes: list[str], surfaces: list[str]) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    all_checks: list[Check] = []

    consumer_base: Path | None = None
    for mode in modes:
        if mode == "consumer-example":
            consumer_base = create_consumer_example(run_dir, opsx_root)
            break

    for mode in modes:
        base = opsx_root if mode == "repo-local" else consumer_base
        if base is None:
            base = base_for_mode(mode, run_dir, opsx_root)
        for surface in surfaces:
            if surface == "claude":
                checks = claude_checks(mode, base, opsx_root)
            elif surface == "codex":
                checks = codex_checks(mode, base, opsx_root)
            else:
                raise ValueError(f"unsupported surface: {surface}")
            all_checks.extend(checks)
            runs.append(
                {
                    "mode": mode,
                    "surface": surface,
                    "summary": summarize(checks),
                    "checks": [asdict(check) for check in checks],
                }
            )

    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "opsx_root": str(opsx_root),
        "report_kind": "aggregate",
        "modes": modes,
        "surfaces": surfaces,
        "summary": summarize(all_checks),
        "runs": runs,
        "checks": [asdict(check) for check in all_checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OPSX wiring discovery smoke checks.")
    parser.add_argument("--opsx-root", type=Path, default=repo_root_from_script(), help="OPSX repository root.")
    parser.add_argument("--runtime-root", type=Path, default=None, help="Runtime output root.")
    parser.add_argument("--run-id", default=utc_run_id(), help="Run id used under runtime output root.")
    parser.add_argument("--report", type=Path, default=None, help="Explicit report path.")
    parser.add_argument(
        "--mode",
        action="append",
        choices=("all", "repo-local", "consumer-example"),
        help="Mode to run. May be repeated. Defaults to all.",
    )
    parser.add_argument(
        "--surface",
        action="append",
        choices=("all", "claude", "codex"),
        help="Surface to run. May be repeated. Defaults to all.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    opsx_root = args.opsx_root.resolve()
    runtime_root = args.runtime_root or opsx_root / ".runtime" / "opsx" / "wiring-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"
    modes = expand_selected(args.mode, ("repo-local", "consumer-example"))
    surfaces = expand_selected(args.surface, ("claude", "codex"))

    run_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args.run_id, opsx_root, run_dir, modes, surfaces)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"report: {report_path}")
    print(
        "summary: "
        f"{summary['status']} "
        f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
