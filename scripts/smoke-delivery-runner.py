#!/usr/bin/env python3
"""Smoke checks for the ChangeRail non-interactive delivery runner."""

from __future__ import annotations

import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "bin" / "changerail-delivery-runner"
VERDICT_HELPER = ROOT / "scripts" / "changerail_review_verdict.py"
CARD = "openspec/board/3.inprogress/harden-delivery-operations.md"


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def run(
    command: list[str],
    env: dict[str, str] | None = None,
    cwd: Path = ROOT,
) -> subprocess.CompletedProcess[str]:
    if env is None:
        env = runner_env()
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, env=env)


def runner_env(mode: str | None = None) -> dict[str, str]:
    env = os.environ.copy()
    for name in ("CODEX_HOME", "CODEX_WORKDIR", "CODEX_AUTH_TOKEN", "OPENAI_API_KEY", "CHANGERAIL_FAKE_MODE"):
        env.pop(name, None)
    if mode:
        env["CHANGERAIL_FAKE_MODE"] = mode
    return env


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
    raise AssertionError(f"{label} failed: {detail}")


def git(command: list[str], cwd: Path) -> str:
    result = subprocess.run(["git", *command], cwd=cwd, capture_output=True, text=True, check=False)
    require_ok(result, "git " + " ".join(command))
    return result.stdout.strip()


def create_workspace(root: Path, name: str) -> Path:
    workspace = root / name
    workspace.mkdir()
    (workspace / ".codex").mkdir()
    (workspace / ".codex" / "config.toml").write_text("# smoke config\n", encoding="utf-8")
    (workspace / ".codex" / "auth.json").write_text("{}\n", encoding="utf-8")
    (workspace / "README.md").write_text("smoke workspace\n", encoding="utf-8")
    (workspace / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    git(["init"], workspace)
    git(["add", ".gitignore", "README.md"], workspace)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "init"],
        workspace,
    )
    return workspace


def head_commit(workspace: Path) -> str:
    return git(["rev-parse", "HEAD"], workspace)


def write_fake_launcher(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "call_log = os.environ.get('CHANGERAIL_FAKE_CALL_LOG')",
                "if call_log:",
                "    with open(call_log, 'a', encoding='utf-8') as handle:",
                "        handle.write(json.dumps({'argv': sys.argv}) + '\\n')",
                "stdin = sys.stdin.read()",
                "print(json.dumps({'argv': sys.argv, 'stdin_len': len(stdin), 'cwd': os.getcwd(), 'CODEX_WORKDIR': os.environ.get('CODEX_WORKDIR'), 'CODEX_HOME': os.environ.get('CODEX_HOME')}))",
                "mode = os.environ.get('CHANGERAIL_FAKE_MODE')",
                "if mode == 'non-terminal-error':",
                "    print(json.dumps({'type': 'tool/result', 'data': {'status': 'failed', 'message': 'error'}}))",
                "if mode == 'no-go':",
                "    print(json.dumps({'type': 'external-review/no-go', 'data': {'result': 'no-go'}}))",
                "if mode == 'awaiting-review':",
                "    print(json.dumps({'type': 'awaiting-review', 'data': {'result': 'awaiting-review'}}))",
                "if mode == 'ordered-conflict':",
                "    print(json.dumps({'type': 'external-review/no-go'}))",
                "    print(json.dumps({'terminal_outcome': 'delivered'}))",
                "if mode == 'safety-stop-no-go':",
                "    print(json.dumps({'type': 'assistant-message', 'content': 'safety stop after repeated no-go'}))",
                "print(json.dumps({'usage': {'input_tokens': 3, 'output_tokens': 5, 'total_tokens': 8}}))",
                "sys.exit(1 if mode == 'no-go' else (2 if mode == 'nonzero' else 0))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def load_status(runtime_root: Path, run_id: str) -> dict[str, Any]:
    return json.loads((runtime_root / run_id / "status.json").read_text(encoding="utf-8"))


def write_board_card(workspace: Path, card: str) -> None:
    path = workspace / card
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Smoke card",
                "",
                "## Status",
                "3.inprogress",
                "",
                "## Result",
                "awaiting review fix",
                "",
            ]
        ),
        encoding="utf-8",
    )


def review_fingerprint(workspace: Path) -> dict[str, str]:
    result = run([sys.executable, str(VERDICT_HELPER), "fingerprint", "--workspace", str(workspace)])
    require_ok(result, "review fingerprint")
    return json.loads(result.stdout)


def write_no_go_verdict(workspace: Path, card: str) -> Path:
    data = review_fingerprint(workspace)
    card_name = Path(card).name.removesuffix(".md")
    verdict = {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": "2026-07-12T00:00:00Z",
        "card": {
            "id": card_name,
            "path": card,
        },
        "workspace": {
            "root": data["workspace"],
            "head_commit": data["head_commit"],
            "diff_fingerprint": data["diff_fingerprint"],
        },
        "reviewer": {
            "kind": "codex-exec",
            "independence": {
                "fresh_context": True,
                "did_not_plan_or_implement": True,
                "basis": "fresh smoke-test reviewer context",
            },
        },
        "result": "no-go",
        "review_cycle": 3,
        "acceptance": [
            {
                "criterion": "published payload",
                "verdict": "fail",
                "evidence": "smoke fixture: card remains unpublished under 3.inprogress",
            }
        ],
        "findings": [
            {
                "id": "R1",
                "severity": "blocker",
                "area": "process",
                "summary": "publish is blocked by repeated no-go",
            }
        ],
        "evidence_audit": {
            "claims_checked": 1,
            "claims_unbacked": 0,
        },
    }
    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / f"{card_name}.json"
    verdict_path.parent.mkdir(parents=True, exist_ok=True)
    verdict_path.write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate = run(
        [
            sys.executable,
            str(VERDICT_HELPER),
            "validate",
            str(verdict_path),
            "--check-fresh",
            "--workspace",
            str(workspace),
            "--json",
        ]
    )
    require_ok(validate, "review verdict validate")
    return verdict_path


def check_success_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "success-workspace")
    launcher = tmp / "fake-codex"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "success",
            "--launcher",
            str(launcher),
            "--model",
            "gpt-test",
            "--reasoning-effort",
            "low",
        ]
    )
    require_ok(result, "runner success")
    status = load_status(runtime, "success")
    argv = status["command"]["argv"]
    if status["result"] != "DELIVERED":
        raise AssertionError(f"unexpected result: {status['result']}")
    if status.get("commit") != head_commit(workspace):
        raise AssertionError(f"commit was not recorded from workspace HEAD: {status}")
    if status["command"].get("stdin") != "closed":
        raise AssertionError("stdin was not recorded as closed")
    if "-m" not in argv or "gpt-test" not in argv:
        raise AssertionError(f"model override missing from argv: {argv}")
    if 'model_reasoning_effort="low"' not in argv:
        raise AssertionError(f"reasoning override missing from argv: {argv}")
    if status["usage"].get("total_tokens") != 8:
        raise AssertionError(f"usage was not parsed: {status['usage']}")
    stdout = Path(status["logs"]["stdout"]).read_text(encoding="utf-8")
    first = json.loads(stdout.splitlines()[0])
    if first.get("stdin_len") != 0:
        raise AssertionError(f"child stdin was not closed: {first}")
    if first.get("cwd") != str(workspace):
        raise AssertionError(f"child cwd did not honor --workspace: {first}")
    if first.get("CODEX_WORKDIR") != str(workspace):
        raise AssertionError(f"CODEX_WORKDIR did not honor --workspace: {first}")
    if first.get("CODEX_HOME") != str(workspace / ".codex"):
        raise AssertionError(f"CODEX_HOME did not default to workspace .codex: {first}")
    if "terminal_outcome: DELIVERED" not in result.stdout:
        raise AssertionError(f"terminal outcome was not printed: {result.stdout}")


def check_default_workspace_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "default-workspace")
    launcher = tmp / "fake-codex-default"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--run-id",
            "default-workspace",
            "--launcher",
            str(launcher),
        ],
        cwd=workspace,
    )
    require_ok(result, "runner default workspace")
    runtime = workspace / ".runtime" / "changerail" / "delivery-runs"
    status = load_status(runtime, "default-workspace")
    if status["workspace"]["root"] != str(workspace):
        raise AssertionError(f"default workspace did not use invocation repo: {status['workspace']}")
    if status.get("commit") != head_commit(workspace):
        raise AssertionError(f"default workspace commit was not recorded: {status}")
    stdout = Path(status["logs"]["stdout"]).read_text(encoding="utf-8")
    first = json.loads(stdout.splitlines()[0])
    if first.get("cwd") != str(workspace):
        raise AssertionError(f"default child cwd did not use invocation repo: {first}")
    if first.get("CODEX_WORKDIR") != str(workspace):
        raise AssertionError(f"default CODEX_WORKDIR did not use invocation repo: {first}")
    if first.get("CODEX_HOME") != str(workspace / ".codex"):
        raise AssertionError(f"default CODEX_HOME did not follow workspace: {first}")
    if "status: " + str(runtime / "default-workspace" / "status.json") not in result.stdout:
        raise AssertionError(f"default runtime root did not follow workspace: {result.stdout}")


def check_no_go_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "no-go-workspace")
    launcher = tmp / "fake-codex-no-go"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "no-go",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("no-go"),
    )
    if result.returncode == 0:
        raise AssertionError("no-go run unexpectedly returned success")
    status = load_status(runtime, "no-go")
    if status["result"] != "NO-GO":
        raise AssertionError(f"structured external-review/no-go should be NO-GO: {status['result']}")
    if "terminal_outcome: NO-GO" not in result.stdout:
        raise AssertionError(f"NO-GO terminal outcome was not printed: {result.stdout}")


def check_review_no_go_fallback_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "review-no-go-fallback-workspace")
    launcher = tmp / "fake-codex-review-no-go-fallback"
    runtime = tmp / "runtime"
    card = "openspec/board/3.inprogress/review-no-go-fallback.md"
    write_fake_launcher(launcher)
    write_board_card(workspace, card)
    write_no_go_verdict(workspace, card)
    result = run(
        [
            str(RUNNER),
            "run",
            card,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "review-no-go-fallback",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("safety-stop-no-go"),
    )
    if result.returncode == 0:
        raise AssertionError("review no-go fallback unexpectedly returned success")
    status = load_status(runtime, "review-no-go-fallback")
    if status["result"] != "NO-GO" or status.get("terminal_outcome") != "NO-GO":
        raise AssertionError(f"fresh no-go verdict fallback should be NO-GO: {status}")
    if status.get("process", {}).get("exit_code") != 0:
        raise AssertionError(f"fixture child should exit 0: {status}")
    if "terminal_outcome: NO-GO" not in result.stdout:
        raise AssertionError(f"NO-GO fallback terminal outcome was not printed: {result.stdout}")


def check_supervisor_stops_after_fallback_no_go(tmp: Path) -> None:
    workspace = create_workspace(tmp, "supervisor-stop-workspace")
    launcher = tmp / "fake-codex-supervisor-stop"
    runtime = tmp / "runtime"
    call_log = tmp / "supervisor-calls.jsonl"
    first_card = "openspec/board/3.inprogress/supervisor-first.md"
    second_card = "openspec/board/3.inprogress/supervisor-second.md"
    write_fake_launcher(launcher)
    write_board_card(workspace, first_card)
    write_board_card(workspace, second_card)
    write_no_go_verdict(workspace, first_card)

    started: list[str] = []
    for index, card in enumerate((first_card, second_card), start=1):
        env = runner_env("safety-stop-no-go" if index == 1 else None)
        env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
        result = run(
            [
                str(RUNNER),
                "run",
                card,
                "--workspace",
                str(workspace),
                "--runtime-root",
                str(runtime),
                "--run-id",
                f"supervisor-{index}",
                "--launcher",
                str(launcher),
            ],
            env=env,
        )
        started.append(card)
        if result.returncode != 0:
            break

    if started != [first_card]:
        raise AssertionError(f"supervisor should stop after first non-delivered card: {started}")
    calls = call_log.read_text(encoding="utf-8").splitlines()
    if len(calls) != 1:
        raise AssertionError(f"second runner child should not start after fallback NO-GO: {calls}")
    status = load_status(runtime, "supervisor-1")
    if status["result"] != "NO-GO":
        raise AssertionError(f"first card should stop batch with NO-GO: {status}")


def check_non_terminal_error_success_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "non-terminal-error-workspace")
    launcher = tmp / "fake-codex-non-terminal-error"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "non-terminal-error",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("non-terminal-error"),
    )
    require_ok(result, "runner non-terminal error success")
    status = load_status(runtime, "non-terminal-error")
    if status["result"] != "DELIVERED":
        raise AssertionError(f"non-terminal error string should not block delivery: {status['result']}")
    if "terminal_outcome: DELIVERED" not in result.stdout:
        raise AssertionError(f"DELIVERED terminal outcome was not printed: {result.stdout}")


def check_ordered_conflict_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "ordered-conflict-workspace")
    launcher = tmp / "fake-codex-ordered-conflict"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "ordered-conflict",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("ordered-conflict"),
    )
    require_ok(result, "runner ordered conflict")
    status = load_status(runtime, "ordered-conflict")
    if status["result"] != "DELIVERED":
        raise AssertionError(f"last authoritative terminal event should win: {status['result']}")


def check_nonzero_without_outcome_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "nonzero-workspace")
    launcher = tmp / "fake-codex-nonzero"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "nonzero",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("nonzero"),
    )
    if result.returncode == 0:
        raise AssertionError("non-zero child exit unexpectedly returned success")
    status = load_status(runtime, "nonzero")
    if status["result"] != "BLOCKED":
        raise AssertionError(f"non-zero exit without authoritative outcome should be BLOCKED: {status['result']}")
    if "terminal_outcome: BLOCKED" not in result.stdout:
        raise AssertionError(f"BLOCKED terminal outcome was not printed: {result.stdout}")


def check_awaiting_review_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "awaiting-workspace")
    launcher = tmp / "fake-codex-awaiting"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "awaiting",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("awaiting-review"),
    )
    if result.returncode == 0:
        raise AssertionError("awaiting-review run unexpectedly returned success")
    status = load_status(runtime, "awaiting")
    if status["result"] != "BLOCKED":
        raise AssertionError(f"awaiting-review should be BLOCKED: {status['result']}")
    if "terminal_outcome: BLOCKED" not in result.stdout:
        raise AssertionError(f"BLOCKED terminal outcome was not printed: {result.stdout}")


def check_preflight(tmp: Path) -> None:
    workspace = create_workspace(tmp, "preflight-workspace")
    launcher = tmp / "fake-codex-preflight"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://user:secret@127.0.0.1:{server.server_port}/health?access_token=raw-token"
        result = run(
            [
                str(RUNNER),
                "preflight",
                CARD,
                "--workspace",
                str(workspace),
                "--runtime-root",
                str(runtime),
                "--run-id",
                "preflight",
                "--launcher",
                str(launcher),
                "--connectivity-url",
                url,
                "--json",
                "--write-status",
            ]
        )
        require_ok(result, "preflight")
        payload = json.loads(result.stdout)
        checks = {check["name"]: check for check in payload["preflight"]["checks"]}
        if checks["connectivity"]["status"] != "pass":
            raise AssertionError(f"connectivity did not pass: {checks['connectivity']}")
        message = checks["connectivity"]["message"]
        for forbidden in ("user:secret", "access_token", "raw-token", "/health"):
            if forbidden in message:
                raise AssertionError(f"connectivity success leaked raw URL data: {message}")
        if checks["CODEX auth"]["status"] != "pass":
            raise AssertionError(f"auth state did not pass: {checks['CODEX auth']}")
        if checks["CODEX_HOME symlinks"]["status"] != "pass":
            raise AssertionError(f"symlink diagnostics did not pass: {checks['CODEX_HOME symlinks']}")
        if not (runtime / "preflight" / "status.json").is_file():
            raise AssertionError("preflight status was not written")
    finally:
        server.shutdown()


def check_preflight_connectivity_failure_redaction(tmp: Path) -> None:
    workspace = create_workspace(tmp, "preflight-failure-workspace")
    launcher = tmp / "fake-codex-preflight-failure"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    url = "http://user:secret@127.0.0.1:1/health?token=raw-token"
    result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "preflight-failure",
            "--launcher",
            str(launcher),
            "--connectivity-url",
            url,
            "--connectivity-timeout",
            "0.2",
            "--json",
            "--write-status",
        ]
    )
    if result.returncode == 0:
        raise AssertionError("connectivity failure preflight unexpectedly passed")
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["preflight"]["checks"]}
    if checks["connectivity"]["status"] != "fail":
        raise AssertionError(f"connectivity did not fail: {checks['connectivity']}")
    message = checks["connectivity"]["message"]
    for forbidden in ("user:secret", "token", "raw-token", "/health"):
        if forbidden in message:
            raise AssertionError(f"connectivity failure leaked raw URL data: {message}")


def check_run_preflight_failure(tmp: Path) -> None:
    workspace = create_workspace(tmp, "run-preflight-failure-workspace")
    launcher = tmp / "fake-codex-run-preflight-failure"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    (workspace / ".codex" / "auth.json").unlink()
    result = run(
        [
            str(RUNNER),
            "run",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "run-preflight-failure",
            "--launcher",
            str(launcher),
        ]
    )
    if result.returncode == 0:
        raise AssertionError("run preflight failure unexpectedly passed")
    status = load_status(runtime, "run-preflight-failure")
    if status["result"] != "BLOCKED" or status.get("terminal_outcome") != "BLOCKED":
        raise AssertionError(f"run preflight failure did not record BLOCKED: {status}")
    lines = result.stdout.splitlines()
    if lines[:2] != [
        "terminal_outcome: BLOCKED",
        f"status: {runtime / 'run-preflight-failure' / 'status.json'}",
    ]:
        raise AssertionError(f"run preflight failure did not print BLOCKED before status: {result.stdout}")


def check_stale_symlink_preflight(tmp: Path) -> None:
    workspace = create_workspace(tmp, "stale-workspace")
    launcher = tmp / "fake-codex-stale"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    skills = workspace / ".codex" / "skills"
    skills.mkdir()
    (skills / "missing").symlink_to(workspace / "missing-skill")
    result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "stale",
            "--launcher",
            str(launcher),
            "--json",
            "--write-status",
        ]
    )
    if result.returncode == 0:
        raise AssertionError("stale symlink preflight unexpectedly passed")
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["preflight"]["checks"]}
    if checks["CODEX_HOME symlinks"]["status"] != "fail":
        raise AssertionError(f"stale symlink was not reported: {checks['CODEX_HOME symlinks']}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-delivery-runner-") as tmp:
        workspace = Path(tmp)
        check_success_run(workspace)
        check_default_workspace_run(workspace)
        check_no_go_run(workspace)
        check_review_no_go_fallback_run(workspace)
        check_supervisor_stops_after_fallback_no_go(workspace)
        check_non_terminal_error_success_run(workspace)
        check_ordered_conflict_run(workspace)
        check_nonzero_without_outcome_run(workspace)
        check_awaiting_review_run(workspace)
        check_preflight(workspace)
        check_preflight_connectivity_failure_redaction(workspace)
        check_run_preflight_failure(workspace)
        check_stale_symlink_preflight(workspace)
    print("ok: delivery runner smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
