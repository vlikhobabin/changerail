#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "changerail.verify-project-smoke.v1"
SPECIAL_OUTPUTS = {
    Path("gitignore.tpl"): Path(".gitignore"),
    Path("mcp.json.tpl"): Path(".mcp.json"),
    Path("codex-config.toml.tpl"): Path(".codex/config.toml"),
}


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


def skill_names(changerail_root: Path) -> list[str]:
    return sorted(
        path.name
        for path in (changerail_root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def render_text(text: str, project: Path, changerail_root: Path) -> str:
    replacements = {
        "{{PROJECT_PATH}}": str(project),
        "{{PROJECT_NAME}}": "example-project",
        "{{PROJECT_KIND}}": "generic",
        "{{CHANGERAIL_ROOT}}": str(changerail_root),
        "{{CHANGERAIL_SHARED_AGENTS}}": (changerail_root / "AGENTS.shared.md").read_text(encoding="utf-8"),
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def output_path_for(rel: Path) -> Path | None:
    if rel == Path("README.md"):
        return None
    if rel in SPECIAL_OUTPUTS:
        return SPECIAL_OUTPUTS[rel]
    if rel.name.endswith(".tpl"):
        return rel.with_name(rel.name[: -len(".tpl")])
    return rel


def symlink_force(target: Path, link_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.exists():
        if link_path.is_dir() and not link_path.is_symlink():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    os.symlink(target, link_path)


def create_fixture(project: Path, changerail_root: Path) -> None:
    template_root = changerail_root / "templates" / "project"
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)

    for source in template_root.rglob("*"):
        if source.is_dir():
            continue
        rel = source.relative_to(template_root)
        out_rel = output_path_for(rel)
        if out_rel is None:
            continue
        target = project / out_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.name.endswith(".tpl"):
            target.write_text(render_text(source.read_text(encoding="utf-8"), project, changerail_root), encoding="utf-8")
        else:
            shutil.copy2(source, target)

    symlink_force(changerail_root / "skills", project / ".claude" / "skills")
    symlink_force(changerail_root / "claude" / "commands" / "changerail", project / ".claude" / "commands" / "changerail")
    for skill in skill_names(changerail_root):
        symlink_force(changerail_root / "skills" / skill, project / ".codex" / "skills" / skill)
    symlink_force(changerail_root / "bin" / "openspec", project / "bin" / "openspec")
    symlink_force(changerail_root / "bin" / "changerail-review-verdict", project / "bin" / "changerail-review-verdict")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "OPENSPEC_TELEMETRY": "0"},
        timeout=180,
    )


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    checks: list[Check] = []
    good_project = run_dir / "example-project"
    create_fixture(good_project, changerail_root)

    verify = run([str(changerail_root / "bin" / "verify-project"), str(good_project)], changerail_root)
    checks.append(
        Check(
            "valid fixture passes",
            "pass" if verify.returncode == 0 else "fail",
            verify.stdout.strip(),
        )
    )

    bad_project = run_dir / "bad-missing-runtime-ignore"
    shutil.copytree(good_project, bad_project, symlinks=True)
    gitignore = bad_project / ".gitignore"
    gitignore.write_text(
        "\n".join(line for line in gitignore.read_text(encoding="utf-8").splitlines() if line.strip() != ".runtime/")
        + "\n",
        encoding="utf-8",
    )
    negative = run([str(changerail_root / "bin" / "verify-project"), str(bad_project)], changerail_root)
    checks.append(
        Check(
            "missing runtime ignore fails",
            "pass" if negative.returncode != 0 else "fail",
            negative.stdout.strip(),
        )
    )

    stale_project = run_dir / "bad-stale-opsx-wiring"
    shutil.copytree(good_project, stale_project, symlinks=True)
    symlink_force(changerail_root / "claude" / "commands" / "changerail", stale_project / ".claude" / "commands" / "opsx")
    symlink_force(changerail_root / "skills" / "changerail-do", stale_project / ".codex" / "skills" / "opsx-do")
    symlink_force(changerail_root / "bin" / "changerail-review-verdict", stale_project / "bin" / "opsx-review-verdict")
    stale = run([str(changerail_root / "bin" / "verify-project"), str(stale_project)], changerail_root)
    checks.append(
        Check(
            "stale OPSX wiring fails",
            "pass" if stale.returncode != 0 and "stale OPSX wiring" in stale.stdout else "fail",
            stale.stdout.strip(),
        )
    )

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
    parser = argparse.ArgumentParser(description="Run verify-project smoke checks.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "verify-project-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"
    run_dir.mkdir(parents=True, exist_ok=True)

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
