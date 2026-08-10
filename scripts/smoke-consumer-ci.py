#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import yaml


SCHEMA = "changerail.consumer-ci-smoke.v1"
WORKFLOW_REL = Path(".github/workflows/changerail-consumer-verify.yml")
LOCK_REL = Path("openspec/changerail-consumer-lock.json")


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


def run(
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    effective_env = {**os.environ, "OPENSPEC_TELEMETRY": "0"}
    if env:
        effective_env.update(env)
    return subprocess.run(
        command,
        cwd=cwd,
        env=effective_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def require(command: list[str], cwd: Path) -> None:
    result = run(command, cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stdout.strip())


def create_clean_changerail_fixture(source_root: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    for rel_path in (
        "AGENTS.shared.md",
        "VERSION",
        "requirements-runtime.txt",
        "mcp-npm-lock.json",
        "templates",
        "skills",
        "claude",
        "bin",
        "schemas",
        "scripts",
    ):
        source = source_root / rel_path
        target = destination / rel_path
        if source.is_dir():
            shutil.copytree(source, target, symlinks=True)
        else:
            shutil.copy2(source, target)
    require(["git", "init", "--initial-branch=main"], destination)
    require(["git", "add", "."], destination)
    require(
        [
            "git",
            "-c",
            "user.name=ChangeRail Smoke",
            "-c",
            "user.email=smoke@example.invalid",
            "commit",
            "-m",
            "clean ChangeRail fixture",
        ],
        destination,
    )
    require(
        ["git", "remote", "add", "origin", "https://github.com/example/changerail.git"],
        destination,
    )
    return destination


def create_fake_npm(changerail_root: Path, fake_bin: Path) -> dict[str, str]:
    fake_bin.mkdir(parents=True)
    lock = json.loads((changerail_root / "mcp-npm-lock.json").read_text(encoding="utf-8"))
    mapping = {
        f"{package['name']}@{package['version']}": package["integrity"]
        for package in lock.get("packages", [])
        if isinstance(package, dict)
    }
    npm = fake_bin / "npm"
    npm.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"MAPPING = {mapping!r}\n"
        "if len(sys.argv) == 5 and sys.argv[1] == 'view' and sys.argv[3] == 'dist.integrity' and sys.argv[4] == '--json':\n"
        "    value = MAPPING.get(sys.argv[2])\n"
        "    if value:\n"
        "        print(json.dumps(value))\n"
        "        raise SystemExit(0)\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    npm.chmod(0o755)
    return {
        "PATH": str(fake_bin) + os.pathsep + os.environ.get("PATH", ""),
        "CODEX_HOME": "",
        "CODEX_AUTH_TOKEN": "",
        "OPENAI_API_KEY": "",
    }


def workflow_contract(workflow: Path) -> Check:
    try:
        text = workflow.read_text(encoding="utf-8")
        data = yaml.load(text, Loader=yaml.BaseLoader)
    except (OSError, yaml.YAMLError) as exc:
        return Check("consumer workflow contract", "fail", f"workflow is unreadable: {exc}")
    failures: list[str] = []
    triggers = data.get("on", {}) if isinstance(data, dict) else {}
    for trigger in ("push", "pull_request", "workflow_dispatch"):
        if trigger not in triggers:
            failures.append(f"missing trigger {trigger}")
    permissions = data.get("permissions", {}) if isinstance(data, dict) else {}
    if permissions != {"contents": "read"}:
        failures.append("permissions are not exactly contents: read")
    required = (
        "changerail.consumer-lock.v1",
        'lock.get("enforcement") != "strict"',
        "CHANGERAIL_REVISION",
        "fetch --depth=1 origin",
        "checkout --detach FETCH_HEAD",
        "--refresh-wiring --skip-verify",
        "/bin/verify-project",
        "validate --all --strict",
        "git -C \"$GITHUB_WORKSPACE\" diff --check",
        "persist-credentials: false",
    )
    for needle in required:
        if needle not in text:
            failures.append(f"missing workflow contract {needle!r}")
    forbidden = (
        "contents: write",
        "pull-requests: write",
        "git push",
        "changerail-delivery-runner",
        "CODEX_AUTH_TOKEN",
        "OPENAI_API_KEY",
    )
    for needle in forbidden:
        if needle in text:
            failures.append(f"forbidden workflow authority {needle!r}")
    return Check(
        "consumer workflow contract",
        "fail" if failures else "pass",
        "; ".join(failures) if failures else "workflow is read-only and exact-lock driven",
    )


def lock_preflight(lock_path: Path, changerail_root: Path, source_repo: Path) -> list[str]:
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        schema = json.loads(
            (changerail_root / "schemas" / "changerail-consumer-lock.schema.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        return [f"lock unreadable: {exc}"]
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(lock)]
    if errors:
        return ["lock schema invalid"]
    if lock.get("enforcement") != "strict":
        return ["consumer CI requires strict lock"]
    revision = str(lock["changerail"]["revision"])
    available = run(["git", "cat-file", "-e", f"{revision}^{{commit}}"], source_repo)
    if available.returncode != 0:
        return ["exact ChangeRail revision is unavailable"]
    return []


def init_consumer_repository(project: Path) -> None:
    require(["git", "init", "--initial-branch=main"], project)
    require(["git", "add", "."], project)
    require(
        [
            "git",
            "-c",
            "user.name=ChangeRail Smoke",
            "-c",
            "user.email=smoke@example.invalid",
            "commit",
            "-m",
            "strict consumer fixture",
        ],
        project,
    )


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    checks: list[Check] = []
    clean_root = create_clean_changerail_fixture(changerail_root, run_dir / "source")
    fake_env = create_fake_npm(clean_root, run_dir / "fake-bin")

    consumer = run_dir / "consumer"
    bootstrap = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(consumer),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "strict",
            "--with-ci",
            "--skip-verify",
        ],
        changerail_root,
    )
    checks.append(
        Check(
            "strict consumer CI bootstrap",
            "pass" if bootstrap.returncode == 0 and (consumer / WORKFLOW_REL).is_file() else "fail",
            bootstrap.stdout.strip(),
        )
    )
    if (consumer / WORKFLOW_REL).is_file():
        checks.append(workflow_contract(consumer / WORKFLOW_REL))
    else:
        checks.append(Check("consumer workflow contract", "fail", "generated workflow is missing"))

    init_consumer_repository(consumer)
    clone = run_dir / "non-sibling" / "consumer-clone"
    clone.parent.mkdir(parents=True)
    require(["git", "clone", str(consumer), str(clone)], run_dir)
    preflight_errors = lock_preflight(clone / LOCK_REL, clean_root, clean_root)
    install = run_dir / "disposable-install"
    require(["git", "clone", str(clean_root), str(install)], run_dir)
    revision = json.loads((clone / LOCK_REL).read_text(encoding="utf-8"))["changerail"]["revision"]
    checkout = run(["git", "checkout", "--detach", revision], install)
    repair = run(
        [
            str(install / "bin" / "bootstrap-project"),
            str(clone),
            "--changerail-root",
            str(install),
            "--refresh-wiring",
            "--skip-verify",
        ],
        clone,
    )
    verify = run(
        [
            str(install / "bin" / "verify-project"),
            str(clone),
            "--changerail-root",
            str(install),
        ],
        clone,
        fake_env,
    )
    baseline = run([str(clone / "bin" / "openspec"), "validate", "--all", "--strict"], clone)
    checks.append(
        Check(
            "strict lock clean-clone execution",
            "pass"
            if not preflight_errors
            and checkout.returncode == 0
            and repair.returncode == 0
            and verify.returncode == 0
            and baseline.returncode == 0
            else "fail",
            "\n".join(
                [
                    *preflight_errors,
                    checkout.stdout.strip(),
                    repair.stdout.strip(),
                    verify.stdout.strip(),
                    baseline.stdout.strip(),
                ]
            ).strip(),
        )
    )

    negative_failures: list[str] = []
    if not lock_preflight(run_dir / "missing-lock.json", clean_root, clean_root):
        negative_failures.append("absent lock passed")
    strict_lock = json.loads((clone / LOCK_REL).read_text(encoding="utf-8"))
    for name, mutation in (
        ("advisory", {"enforcement": "advisory"}),
        ("unavailable", {"changerail.revision": "0" * 40}),
    ):
        fixture = run_dir / f"{name}-lock.json"
        payload = json.loads(json.dumps(strict_lock))
        if "enforcement" in mutation:
            payload["enforcement"] = mutation["enforcement"]
        else:
            payload["changerail"]["revision"] = mutation["changerail.revision"]
        fixture.write_text(json.dumps(payload), encoding="utf-8")
        if not lock_preflight(fixture, clean_root, clean_root):
            negative_failures.append(f"{name} lock passed")
    malformed = run_dir / "malformed-lock.json"
    malformed.write_text("{not-json\n", encoding="utf-8")
    if not lock_preflight(malformed, clean_root, clean_root):
        negative_failures.append("malformed lock passed")

    conflict = clone / "bin" / "openspec"
    conflict.unlink()
    conflict.write_text("project-owned\n", encoding="utf-8")
    conflict_refresh = run(
        [
            str(install / "bin" / "bootstrap-project"),
            str(clone),
            "--changerail-root",
            str(install),
            "--refresh-wiring",
            "--skip-verify",
        ],
        clone,
    )
    if conflict_refresh.returncode == 0 or conflict.read_text(encoding="utf-8") != "project-owned\n":
        negative_failures.append("project-owned wiring conflict passed or was replaced")
    checks.append(
        Check(
            "consumer CI negative matrix",
            "fail" if negative_failures else "pass",
            "; ".join(negative_failures) if negative_failures else "all unsafe lock and wiring fixtures failed closed",
        )
    )

    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "run_dir": str(run_dir),
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run generated consumer CI contract smoke.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "consumer-ci-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"
    report = run_smoke(changerail_root, run_dir)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"report: {report_path}")
    print(
        f"summary: {summary['status']} "
        f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
