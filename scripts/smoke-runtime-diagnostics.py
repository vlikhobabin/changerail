#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import runpy
import secrets
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "changerail.runtime-diagnostics-smoke.v1"
BUDGET = 32768
WARNING_BYTES = (BUDGET * 85 + 99) // 100


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


def write_budget_fixture(project: Path, size: int, *, explicit: bool = True) -> None:
    (project / ".codex").mkdir(parents=True, exist_ok=True)
    budget_line = f"project_doc_max_bytes = {BUDGET}\n" if explicit else ""
    (project / ".codex" / "config.toml").write_text(budget_line, encoding="utf-8")
    (project / "AGENTS.md").write_text("a" * size, encoding="utf-8")


def budget_checks(changerail_root: Path, run_dir: Path) -> list[Check]:
    namespace = runpy.run_path(str(changerail_root / "bin" / "verify-project"))
    checker = namespace.get("check_instruction_budget")
    if not callable(checker):
        return [Check("instruction budget boundaries", "fail", "check_instruction_budget is missing")]

    fixtures = (
        ("below", WARNING_BYTES - 1, True, "pass", "blocking"),
        ("boundary", WARNING_BYTES, True, "fail", "non-blocking"),
        ("over", BUDGET + 1, True, "fail", "blocking"),
        ("legacy default", WARNING_BYTES - 1, False, "pass", "blocking"),
    )
    failures: list[str] = []
    for name, size, explicit, expected_status, expected_severity in fixtures:
        project = run_dir / f"budget-{name.replace(' ', '-')}"
        write_budget_fixture(project, size, explicit=explicit)
        result = checker(project)
        if result.status != expected_status or result.severity != expected_severity:
            failures.append(
                f"{name}: got {result.status}/{result.severity}, "
                f"expected {expected_status}/{expected_severity}"
            )
        if str(size) not in result.message or str(BUDGET) not in result.message:
            failures.append(f"{name}: measured/allowed bytes missing")
        if name == "legacy default" and "compatibility default" not in result.message:
            failures.append("legacy default: compatibility source missing")
    if failures:
        return [Check("instruction budget boundaries", "fail", "; ".join(failures))]
    return [
        Check(
            "instruction budget boundaries",
            "pass",
            "below, 85-percent, over-budget and legacy-default fixtures classified",
        )
    ]


def write_fake_codex(fake_bin: Path) -> Path:
    fake_bin.mkdir(parents=True, exist_ok=True)
    executable = fake_bin / "codex"
    executable.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

log = Path(os.environ["FAKE_CODEX_LOG"])
with log.open("a", encoding="utf-8") as handle:
    handle.write(" ".join(sys.argv[1:]) + "\\n")
version = os.environ.get("FAKE_CODEX_VERSION", "0.147.7")
mode = os.environ.get("FAKE_CODEX_MODE", "valid")
marker = "runtime-credential-" + "sentinel"
raw_path = "/" + "home" + "/example-private/codex-state"
if sys.argv[1:] == ["--version"]:
    print(f"codex-cli {version}")
    raise SystemExit(0)
if sys.argv[1:] == ["doctor", "--json"]:
    if mode == "invalid-doctor":
        print(json.dumps({"schemaVersion": 2, "codexVersion": version}))
        raise SystemExit(0)
    item = lambda name, category: {
        "id": name,
        "category": category,
        "status": "ok",
        "summary": "ok",
        "details": {"local_path": raw_path, "credential_marker": marker},
        "remediation": None,
        "durationMs": 1,
    }
    print(json.dumps({
        "schemaVersion": 1,
        "generatedAt": "2026-08-10T00:00:00Z",
        "overallStatus": "ok",
        "codexVersion": version,
        "checks": {
            "auth.credentials": item("auth.credentials", "auth"),
            "config.load": item("config.load", "config"),
            "mcp.config": item("mcp.config", "mcp"),
        },
    }))
    raise SystemExit(0)
if sys.argv[1:] == ["debug", "prompt-input"]:
    if mode == "unsupported-command":
        print("prompt-input unavailable", file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps([{
        "id": "message-id-redacted",
        "role": "developer",
        "type": "message",
        "content": [{
            "type": "input_text",
            "text": "# Repository Guidelines\\nAGENTS.md\\n" + raw_path + "\\n" + marker,
        }],
        "internal_chat_message_metadata_passthrough": {},
    }]))
    raise SystemExit(0)
print("unsupported fake invocation", file=sys.stderr)
raise SystemExit(2)
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable


def run_verify(
    changerail_root: Path,
    project: Path,
    env: dict[str, str],
    *,
    runtime: bool,
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    command = [str(changerail_root / "bin" / "verify-project"), str(project), "--json"]
    if runtime:
        command.append("--runtime-diagnostics")
    result = subprocess.run(
        command,
        cwd=changerail_root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
        check=False,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}
    return result, data


def runtime_checks(changerail_root: Path, run_dir: Path) -> list[Check]:
    project = run_dir / "runtime-project"
    write_budget_fixture(project, 1024)
    (project / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    fake_bin = run_dir / "fake-bin"
    write_fake_codex(fake_bin)
    invocation_log = run_dir / "codex-invocations.log"
    env = {
        **os.environ,
        "PATH": str(fake_bin) + os.pathsep + os.environ.get("PATH", ""),
        "CODEX_HOME": str(project / ".codex"),
        "FAKE_CODEX_LOG": str(invocation_log),
    }
    failures: list[str] = []

    default_result, default_data = run_verify(changerail_root, project, env, runtime=False)
    if not default_data or invocation_log.exists():
        failures.append("default verifier launched Codex runtime")
    if "static" not in json.dumps(default_data.get("summary", {}), sort_keys=True):
        failures.append("default summary omitted static verification classification")

    runtime_result, runtime_data = run_verify(changerail_root, project, env, runtime=True)
    runtime_summary = runtime_data.get("runtime_diagnostics", {})
    if not isinstance(runtime_summary, dict) or runtime_summary.get("status") != "pass":
        failures.append(f"supported runtime adapter did not pass: {runtime_result.stdout[:300]}")
    marker = "runtime-credential-" + "sentinel"
    raw_path = "/" + "home" + "/example-private/codex-state"
    if marker in runtime_result.stdout or raw_path in runtime_result.stdout:
        failures.append("runtime summary exposed raw path or credential marker")
    evidence_dir = runtime_summary.get("evidence_dir") if isinstance(runtime_summary, dict) else None
    evidence_path = project / str(evidence_dir or "")
    raw_text = ""
    if not evidence_dir or Path(str(evidence_dir)).is_absolute() or not evidence_path.is_dir():
        failures.append("runtime evidence directory is missing or not project-relative")
    else:
        raw_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in evidence_path.iterdir()
            if path.is_file()
        )
    if marker not in raw_text or raw_path not in raw_text:
        failures.append("raw runtime evidence did not retain diagnostic source data")

    wrong_home = run_dir / "wrong-codex-home"
    mismatch_env = {**env, "CODEX_HOME": str(wrong_home)}
    mismatch_result, mismatch_data = run_verify(changerail_root, project, mismatch_env, runtime=True)
    mismatch_summary = mismatch_data.get("runtime_diagnostics", {})
    if not isinstance(mismatch_summary, dict) or mismatch_summary.get("status") == "pass":
        failures.append("wrong CODEX_HOME produced runtime success")
    if str(wrong_home) in mismatch_result.stdout:
        failures.append("wrong CODEX_HOME leaked an absolute local path")

    unsupported_env = {**env, "FAKE_CODEX_VERSION": "0.146.9"}
    _, unsupported_data = run_verify(changerail_root, project, unsupported_env, runtime=True)
    unsupported = unsupported_data.get("runtime_diagnostics", {})
    if not isinstance(unsupported, dict) or unsupported.get("status") != "unsupported":
        failures.append("unsupported Codex version was not classified")

    invalid_env = {**env, "FAKE_CODEX_MODE": "invalid-doctor"}
    _, invalid_data = run_verify(changerail_root, project, invalid_env, runtime=True)
    invalid = invalid_data.get("runtime_diagnostics", {})
    if not isinstance(invalid, dict) or invalid.get("status") != "invalid":
        failures.append("invalid doctor schema was not classified")

    unsupported_command_env = {**env, "FAKE_CODEX_MODE": "unsupported-command"}
    _, unsupported_command_data = run_verify(
        changerail_root,
        project,
        unsupported_command_env,
        runtime=True,
    )
    unsupported_command = unsupported_command_data.get("runtime_diagnostics", {})
    if (
        not isinstance(unsupported_command, dict)
        or unsupported_command.get("status") != "unsupported"
        or unsupported_command.get("reason") != "prompt-input-command-unavailable"
    ):
        failures.append("unsupported runtime command was not classified")

    if failures:
        return [Check("runtime diagnostic adapter", "fail", "; ".join(failures))]
    return [
        Check(
            "runtime diagnostic adapter",
            "pass",
            "opt-in, version/schema gates, CODEX_HOME and raw-output redaction passed",
        )
    ]


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    run_dir.mkdir(parents=True, exist_ok=True)
    checks = budget_checks(changerail_root, run_dir)
    checks.extend(runtime_checks(changerail_root, run_dir))
    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "changerail_root": str(changerail_root),
        "run_dir": str(run_dir),
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test instruction budget and runtime diagnostics.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = repo_root_from_script()
    run_dir = root / ".runtime" / "changerail" / "runtime-diagnostics-smoke" / utc_run_id()
    report = run_smoke(root, run_dir)
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(f"report: {report_path}")
        print(
            f"summary: {summary['status']} "
            f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
        )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
