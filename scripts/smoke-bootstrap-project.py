#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import secrets
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "changerail.bootstrap-project-smoke.v1"


@dataclass
class Check:
    name: str
    status: str
    message: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=240,
    )


def contains_placeholder(project: Path) -> list[str]:
    offenders: list[str] = []
    for path in project.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "{{" in text or "}}" in text:
            offenders.append(str(path.relative_to(project)))
    return offenders


def missing_workflow_guidance(project: Path) -> list[str]:
    checks = {
        "AGENTS.md": [
            "explore -> ff -> do -> review -> pub",
            "## Supervised Roles",
            "Reviewer работает в fresh context",
            "3.inprogress",
            "4.done",
        ],
        "openspec/board/README.md": [
            "explore -> ff -> do -> review -> pub",
            "fresh independent `go` verdict",
            "`3.inprogress -> 4.done`",
            "`review` должен быть fresh context",
        ],
    }
    missing: list[str] = []
    for rel_path, needles in checks.items():
        path = project / rel_path
        if not path.is_file():
            missing.append(f"{rel_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel_path}: missing {needle!r}")
    return missing


def check_bootstrap_success(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "example-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "example-project",
            "--kind",
            "generic",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("bootstrap valid project", "fail", result.stdout.strip())
    placeholders = contains_placeholder(project)
    if placeholders:
        return Check("bootstrap valid project", "fail", "raw placeholders remain: " + ", ".join(placeholders))
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root)
    if verify.returncode != 0:
        return Check("bootstrap valid project", "fail", verify.stdout.strip())
    workflow_missing = missing_workflow_guidance(project)
    if workflow_missing:
        return Check("bootstrap workflow guidance", "fail", "; ".join(workflow_missing))
    return Check("bootstrap valid project", "pass", "project generated and verified")


def check_dry_run(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "dry-run-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "dry-run-project",
            "--kind",
            "generic",
            "--dry-run",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("dry-run no-write", "fail", result.stdout.strip())
    if project.exists():
        return Check("dry-run no-write", "fail", f"target was created: {project}")
    expected = (".claude/commands/chrl", ".codex/skills/chrl-do")
    missing = [needle for needle in expected if needle not in result.stdout]
    if missing:
        return Check("dry-run no-write", "fail", "dry-run omitted alias wiring: " + ", ".join(missing))
    return Check("dry-run no-write", "pass", "dry-run printed plan and left no target")


def check_refuse_existing(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "existing-project"
    project.mkdir(parents=True)
    marker = project / "existing.txt"
    marker.write_text("keep\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "existing-project",
            "--kind",
            "generic",
        ],
        changerail_root,
    )
    if result.returncode == 0:
        return Check("refuse existing target", "fail", "bootstrap unexpectedly succeeded")
    if marker.read_text(encoding="utf-8") != "keep\n":
        return Check("refuse existing target", "fail", "existing marker changed")
    return Check("refuse existing target", "pass", "non-empty target refused without changes")


def check_backup_existing(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "backup-project"
    project.mkdir(parents=True)
    marker = project / "existing.txt"
    marker.write_text("backup me\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "backup-project",
            "--kind",
            "generic",
            "--backup-existing",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("backup existing target", "fail", result.stdout.strip())
    backups = sorted(project.parent.glob("backup-project.backup-*"))
    if not backups:
        return Check("backup existing target", "fail", "backup directory was not created")
    if not (backups[-1] / "existing.txt").is_file():
        return Check("backup existing target", "fail", "backup marker missing")
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root)
    if verify.returncode != 0:
        return Check("backup existing target", "fail", verify.stdout.strip())
    return Check("backup existing target", "pass", "existing target backed up and new project verified")


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    checks = [
        check_bootstrap_success(changerail_root, run_dir),
        check_dry_run(changerail_root, run_dir),
        check_refuse_existing(changerail_root, run_dir),
        check_backup_existing(changerail_root, run_dir),
    ]
    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "run_dir": str(run_dir),
        "changerail_root": str(changerail_root),
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bootstrap-project smoke checks.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "bootstrap-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"

    report = run_smoke(changerail_root, run_dir)
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
