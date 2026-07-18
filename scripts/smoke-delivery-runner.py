#!/usr/bin/env python3
"""Smoke checks for the ChangeRail non-interactive delivery runner."""

from __future__ import annotations

import http.server
import hashlib
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
    (workspace / ".gitignore").write_text(".runtime/\n.codex/\n", encoding="utf-8")
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
                "import json, os, sys, time",
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
                "if mode == 'fix-budget-exhausted':",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-fix-budget', 'type': 'agent_message', 'text': 'Verification remains red.\\nterminal_outcome: BLOCKED\\nterminal_reason: fix_budget_exhausted'}}))",
                "if mode == 'external-blocker':",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-external', 'type': 'agent_message', 'text': 'Target unavailable.\\nterminal_outcome: BLOCKED\\nterminal_reason: external_blocker'}}))",
                "if mode == 'marker-like-prose':",
                "    print(json.dumps({'type': 'assistant-message', 'content': 'terminal_outcome: DELIVERED and terminal_reason: ignored are prose'}))",
                "if mode == 'performance':",
                "    print(json.dumps({'type': 'item.started', 'item': {'id': 'cmd-1', 'type': 'command_execution', 'command': '/bin/echo one', 'status': 'in_progress'}}), flush=True)",
                "    time.sleep(0.01)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'cmd-1', 'type': 'command_execution', 'command': '/bin/echo one', 'status': 'completed', 'exit_code': 0}}), flush=True)",
                "    print(json.dumps({'type': 'item.started', 'item': {'id': 'cmd-2', 'type': 'command_execution', 'command': '/bin/echo two', 'status': 'in_progress'}}), flush=True)",
                "    time.sleep(0.01)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'cmd-2', 'type': 'command_execution', 'command': '/bin/echo two', 'status': 'completed', 'exit_code': 0}}), flush=True)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-1', 'type': 'agent_message', 'text': 'done'}}), flush=True)",
                "if mode not in {'unstructured-success', 'safety-stop-no-go', 'fix-budget-exhausted', 'external-blocker', 'marker-like-prose', 'no-go', 'awaiting-review', 'ordered-conflict'}:",
                "    print(json.dumps({'terminal_outcome': 'DELIVERED'}))",
                "print(json.dumps({'usage': {'input_tokens': 3, 'cached_input_tokens': 1, 'uncached_input_tokens': 2, 'output_tokens': 5, 'reasoning_tokens': 1, 'total_tokens': 8}}))",
                "sys.exit(1 if mode == 'no-go' else (2 if mode == 'nonzero' else 0))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_queue_runner(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import argparse, json, os, sys",
                "from pathlib import Path",
                "parser = argparse.ArgumentParser()",
                "sub = parser.add_subparsers(dest='command', required=True)",
                "run = sub.add_parser('run')",
                "run.add_argument('card')",
                "run.add_argument('--workspace', required=True)",
                "run.add_argument('--runtime-root', required=True)",
                "run.add_argument('--run-id', required=True)",
                "run.add_argument('--model')",
                "run.add_argument('--reasoning-effort')",
                "run.add_argument('--deliver-arg', action='append', default=[])",
                "preflight = sub.add_parser('preflight')",
                "preflight.add_argument('card')",
                "preflight.add_argument('--workspace', required=True)",
                "preflight.add_argument('--runtime-root', required=True)",
                "preflight.add_argument('--run-id', required=True)",
                "preflight.add_argument('--json', action='store_true')",
                "preflight.add_argument('--write-status', action='store_true')",
                "args = parser.parse_args()",
                "call_log = os.environ.get('CHANGERAIL_FAKE_CALL_LOG')",
                "if call_log:",
                "    with open(call_log, 'a', encoding='utf-8') as handle:",
                "        handle.write(json.dumps({'argv': sys.argv, 'card': args.card}) + '\\n')",
                "if args.command == 'preflight':",
                "    status = {",
                "        'schema': 'changerail.delivery-run.v1',",
                "        'run_id': args.run_id,",
                "        'updated_at': '2026-07-15T00:00:00Z',",
                "        'workspace': {'root': args.workspace},",
                "        'card': {'id': Path(args.card).name.removesuffix('.md'), 'path': args.card},",
                "        'phase': 'preflight',",
                "        'result': 'DELIVERED',",
                "        'timestamps': {'started_at': '2026-07-15T00:00:00Z', 'ended_at': '2026-07-15T00:00:01Z'},",
                "        'command': {'argv': sys.argv, 'launcher': sys.argv[0], 'stdin': 'closed', 'json': True},",
                "        'usage': {'available': False, 'reason': 'fake queue preflight'},",
                "        'preflight': {'checks': [{'name': 'fake', 'status': 'pass', 'message': 'ready'}]},",
                "    }",
                "    path = Path(args.runtime_root) / args.run_id / 'status.json'",
                "    path.parent.mkdir(parents=True, exist_ok=True)",
                "    path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
                "    print(json.dumps(status))",
                "    sys.exit(0)",
                "mode = os.environ.get('CHANGERAIL_QUEUE_FAKE_MODE')",
                "if mode == 'missing-status' and 'service-a-card' in args.card:",
                "    sys.exit(0)",
                "result = 'DELIVERED'",
                "terminal_reason = None",
                "if mode == 'no-go' and 'service-a-card' in args.card:",
                "    result = 'NO-GO'",
                "if mode == 'blocked' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "if mode == 'fix-budget' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "    terminal_reason = 'fix_budget_exhausted'",
                "if mode == 'external-blocker' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "    terminal_reason = 'external_blocker'",
                "if mode == 'recovery-no-go' and 'service-a-recovery' in args.card:",
                "    result = 'NO-GO'",
                "status = {",
                "    'schema': 'changerail.delivery-run.v1',",
                "    'run_id': args.run_id,",
                "    'updated_at': '2026-07-15T00:00:00Z',",
                "    'workspace': {'root': args.workspace},",
                "    'card': {'id': Path(args.card).name.removesuffix('.md'), 'path': args.card},",
                "    'phase': 'terminal',",
                "    'result': result,",
                "    'terminal_outcome': result,",
                "    'timestamps': {'started_at': '2026-07-15T00:00:00Z', 'ended_at': '2026-07-15T00:00:01Z'},",
                "    'command': {'argv': sys.argv, 'launcher': sys.argv[0], 'stdin': 'closed', 'json': True},",
                "    'usage': {'available': False, 'reason': 'fake queue runner'},",
                "}",
                "if terminal_reason:",
                "    status['terminal_reason'] = terminal_reason",
                "path = Path(args.runtime_root) / args.run_id / 'status.json'",
                "path.parent.mkdir(parents=True, exist_ok=True)",
                "path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
                "print('terminal_outcome: ' + result)",
                "print('status: ' + str(path))",
                "sys.exit(0 if result == 'DELIVERED' else 1)",
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


def write_queue_plan(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def queue_plan_fixture() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-plan.v1",
        "id": "queue-smoke",
        "max_parallel": 2,
        "per_workspace_parallelism": 1,
        "push_mode": "push",
        "workspaces": [
            {"alias": "service-a", "path": "service-a"},
            {"alias": "service-b", "path": "service-b"},
        ],
        "waves": [{"id": 1}, {"id": 2, "depends_on": [1]}],
        "cards": [
            {
                "id": "service-a-card",
                "workspace": "service-a",
                "card": "service-a-card.md",
                "wave": 1,
                "model": "gpt-test",
                "reasoning_effort": "low",
            },
            {
                "id": "service-b-card",
                "workspace": "service-b",
                "card": "service-b-card.md",
                "depends_on": ["service-a-card"],
                "wave": 2,
            },
        ],
    }


def queue_plan_fingerprint(plan: dict[str, Any]) -> str:
    encoded = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def configure_upstream_baseline(workspace: Path) -> None:
    remote = workspace.parent / f"{workspace.name}.git"
    git(["init", "--bare", str(remote)], workspace.parent)
    git(["remote", "add", "origin", str(remote)], workspace)
    git(["push", "-u", "origin", "HEAD"], workspace)


def create_queue_consumer(tmp: Path, name: str, no_push_ready: bool = True) -> tuple[Path, Path, Path]:
    consumer = tmp / name
    consumer.mkdir()
    service_a = create_workspace(consumer, "service-a")
    service_b = create_workspace(consumer, "service-b")
    if no_push_ready:
        configure_upstream_baseline(service_a)
        configure_upstream_baseline(service_b)
    write_board_card(service_a, "openspec/board/3.inprogress/service-a-card.md")
    write_board_card(service_a, "openspec/board/2.todo/service-a-recovery.md")
    write_board_card(service_a, "openspec/board/2.todo/service-a-recovery-two.md")
    write_board_card(service_a, "openspec/board/3.inprogress/duplicate-card.md")
    write_board_card(service_a, "openspec/board/5.canceled/canceled-card.md")
    write_board_card(service_b, "openspec/board/2.todo/service-b-card.md")
    write_board_card(service_b, "openspec/board/2.todo/service-b-recovery.md")
    write_board_card(service_b, "openspec/board/2.todo/duplicate-card.md")
    git(["add", "openspec"], service_a)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "cards"],
        service_a,
    )
    git(["add", "openspec"], service_b)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "cards"],
        service_b,
    )
    return consumer, service_a, service_b


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


def check_performance_summary_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "performance-workspace")
    launcher = tmp / "fake-codex-performance"
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
            "performance",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("performance"),
    )
    require_ok(result, "runner performance")
    status = load_status(runtime, "performance")
    performance = status.get("performance")
    if not isinstance(performance, dict):
        raise AssertionError(f"performance summary missing from status: {status}")
    if performance.get("command_execution_count") != 2:
        raise AssertionError(f"command count was not captured: {performance}")
    commands = performance.get("commands")
    if not isinstance(commands, list) or len(commands) != 2:
        raise AssertionError(f"command summaries missing: {performance}")
    durations = [command.get("duration_seconds") for command in commands]
    if not all(isinstance(duration, (int, float)) and duration >= 0 for duration in durations):
        raise AssertionError(f"command durations were not measurable: {commands}")
    if max(durations) <= 0:
        raise AssertionError(f"expected at least one positive command duration: {commands}")
    if performance.get("agent_message_count") != 1:
        raise AssertionError(f"agent message count was not captured: {performance}")
    if performance.get("file_change_count", -1) < 0:
        raise AssertionError(f"file change count missing: {performance}")
    slowest = performance.get("slowest_commands")
    if not isinstance(slowest, list) or not slowest:
        raise AssertionError(f"slowest command summary missing: {performance}")
    timeline = performance.get("timeline")
    if not isinstance(timeline, list) or not any(event.get("terminal_outcome") == "DELIVERED" for event in timeline):
        raise AssertionError(f"terminal outcome timing missing from timeline: {timeline}")
    if status["usage"].get("cached_input_tokens") != 1 or status["usage"].get("reasoning_tokens") != 1:
        raise AssertionError(f"usage breakdown was not parsed: {status['usage']}")


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


def check_fix_budget_handoff_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "fix-budget-workspace")
    launcher = tmp / "fake-codex-fix-budget"
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
            "fix-budget",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("fix-budget-exhausted"),
    )
    if result.returncode == 0:
        raise AssertionError("fix-budget safety stop unexpectedly returned success")
    status = load_status(runtime, "fix-budget")
    if status.get("result") != "BLOCKED" or status.get("terminal_reason") != "fix_budget_exhausted":
        raise AssertionError(f"fix-budget terminal signal was not preserved: {status}")
    if "terminal_reason: fix_budget_exhausted" not in result.stdout:
        raise AssertionError(f"fix-budget reason was not printed: {result.stdout}")


def check_external_blocker_handoff_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "external-blocker-workspace")
    launcher = tmp / "fake-codex-external-blocker"
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
            "external-blocker",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("external-blocker"),
    )
    if result.returncode == 0:
        raise AssertionError("external blocker unexpectedly returned success")
    status = load_status(runtime, "external-blocker")
    if status.get("result") != "BLOCKED" or status.get("terminal_reason") != "external_blocker":
        raise AssertionError(f"external blocker reason was not preserved: {status}")


def check_unstructured_unpublished_success_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "unpublished-success-workspace")
    launcher = tmp / "fake-codex-unpublished-success"
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
            "unpublished-success",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("unstructured-success"),
    )
    if result.returncode == 0:
        raise AssertionError("unstructured unpublished exit 0 unexpectedly delivered")
    status = load_status(runtime, "unpublished-success")
    if status.get("result") != "BLOCKED" or status.get("terminal_reason") != "unpublished_card":
        raise AssertionError(f"unpublished exit 0 was not fail-closed: {status}")


def check_marker_like_prose_is_not_authoritative(tmp: Path) -> None:
    workspace = create_workspace(tmp, "marker-prose-workspace")
    launcher = tmp / "fake-codex-marker-prose"
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
            "marker-prose",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("marker-like-prose"),
    )
    if result.returncode == 0:
        raise AssertionError("marker-like arbitrary prose unexpectedly delivered")
    status = load_status(runtime, "marker-prose")
    if status.get("terminal_reason") != "unpublished_card":
        raise AssertionError(f"arbitrary prose was treated as authoritative: {status}")


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


def check_queue_plan_preflight(tmp: Path) -> None:
    consumer, service_a, _service_b = create_queue_consumer(tmp, "queue-consumer")
    plan = consumer / "delivery-plan.json"
    runtime = tmp / "queue-runtime"
    write_queue_plan(plan, queue_plan_fixture())

    dry_run = run(
        [
            str(RUNNER),
            "plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-dry-run",
            "--launcher",
            str(RUNNER),
            "--json",
            "--no-push",
        ]
    )
    require_ok(dry_run, "queue plan dry-run")
    payload = json.loads(dry_run.stdout)
    if payload["result"] != "DELIVERED":
        raise AssertionError(f"queue dry-run did not pass: {payload}")
    commands = [card.get("command", []) for card in payload["cards"]]
    if not any("--deliver-arg=--no-push" in command for command in commands):
        raise AssertionError(f"dry-run did not propagate no-push to child command: {commands}")
    if (service_a / ".runtime" / "changerail" / "delivery-runs").exists():
        raise AssertionError("dry-run unexpectedly launched a child delivery")

    preflight = run(
        [
            str(RUNNER),
            "preflight-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-preflight",
            "--launcher",
            str(RUNNER),
            "--json",
        ]
    )
    require_ok(preflight, "queue preflight")
    status = load_status(runtime, "queue-preflight")
    if status["schema"] != "changerail.delivery-plan-status.v1" or status["result"] != "DELIVERED":
        raise AssertionError(f"queue preflight status invalid: {status}")
    if len(status["cards"]) != 2 or not all(card["state"] == "ready" for card in status["cards"]):
        raise AssertionError(f"queue preflight did not resolve cards: {status['cards']}")

    status_result = run(
        [
            str(RUNNER),
            "status-plan",
            str(runtime / "queue-preflight" / "status.json"),
            "--json",
        ]
    )
    require_ok(status_result, "queue status-plan")
    status_payload = json.loads(status_result.stdout)
    if status_payload["plan"]["id"] != "queue-smoke" or status_payload["result"] != "DELIVERED":
        raise AssertionError(f"status-plan did not read aggregate status: {status_payload}")


def check_queue_preflight_failures(tmp: Path) -> None:
    cases: list[tuple[str, Any]] = [
        (
            "cycle",
            lambda plan: (
                plan["cards"][0].update({"depends_on": ["service-b-card"]}),
                plan["cards"][1].update({"depends_on": ["service-a-card"]}),
            ),
        ),
        ("duplicate-id", lambda plan: plan["cards"].append(dict(plan["cards"][0]))),
        (
            "duplicate-card",
            lambda plan: plan["cards"].append(
                {"id": "duplicate-card-copy", "workspace": "service-a", "card": "service-a-card.md", "wave": 1}
            ),
        ),
        (
            "duplicate-card-board-path",
            lambda plan: plan["cards"].append(
                {
                    "id": "duplicate-card-path-copy",
                    "workspace": "service-a",
                    "card": "openspec/board/3.inprogress/service-a-card.md",
                    "wave": 1,
                }
            ),
        ),
        ("missing-card", lambda plan: plan["cards"][0].update({"card": "missing-card.md"})),
        ("missing-workspace", lambda plan: plan["cards"][0].update({"workspace": "missing-service"})),
        ("missing-dependency", lambda plan: plan["cards"][1].update({"depends_on": ["missing-card"]})),
        ("canceled-card", lambda plan: plan["cards"][0].update({"card": "canceled-card.md"})),
        (
            "invalid-wave",
            lambda plan: (
                plan["cards"][0].update({"wave": 1, "depends_on": ["service-b-card"]}),
                plan["cards"][1].update({"wave": 2}),
            ),
        ),
        (
            "invalid-recovery-wave",
            lambda plan: plan["cards"].append(
                {
                    "id": "service-a-recovery",
                    "workspace": "service-a",
                    "card": "service-a-recovery.md",
                    "wave": 2,
                    "recovery_for": "service-a-card",
                }
            ),
        ),
        (
            "invalid-recovery-workspace",
            lambda plan: plan["cards"].append(
                {
                    "id": "service-b-recovery",
                    "workspace": "service-b",
                    "card": "service-b-recovery.md",
                    "wave": 1,
                    "recovery_for": "service-a-card",
                }
            ),
        ),
        (
            "duplicate-recovery-source",
            lambda plan: plan["cards"].extend(
                [
                    {
                        "id": "service-a-recovery",
                        "workspace": "service-a",
                        "card": "service-a-recovery.md",
                        "wave": 1,
                        "recovery_for": "service-a-card",
                    },
                    {
                        "id": "service-a-recovery-two",
                        "workspace": "service-a",
                        "card": "service-a-recovery-two.md",
                        "wave": 1,
                        "recovery_for": "service-a-card",
                    },
                ]
            ),
        ),
        ("invalid-concurrency", lambda plan: plan.update({"per_workspace_parallelism": 2})),
    ]
    for name, mutate in cases:
        consumer, _service_a, _service_b = create_queue_consumer(tmp, f"queue-fail-{name}")
        plan_payload = queue_plan_fixture()
        mutate(plan_payload)
        plan = consumer / "delivery-plan.json"
        runtime = tmp / f"queue-fail-runtime-{name}"
        write_queue_plan(plan, plan_payload)
        result = run(
            [
                str(RUNNER),
                "preflight-plan",
                str(plan),
                "--consumer-root",
                str(consumer),
                "--runtime-root",
                str(runtime),
                "--run-id",
                name,
                "--launcher",
                str(RUNNER),
                "--json",
            ]
        )
        if result.returncode == 0:
            raise AssertionError(f"{name} preflight unexpectedly passed: {result.stdout}")
        status = load_status(runtime, name)
        if status["schema"] != "changerail.delivery-plan-status.v1" or status["result"] != "BLOCKED":
            raise AssertionError(f"{name} did not write BLOCKED aggregate status: {status}")

    dirty_consumer, dirty_service_a, _dirty_service_b = create_queue_consumer(tmp, "queue-fail-dirty")
    (dirty_service_a / "DIRTY.txt").write_text("dirty\n", encoding="utf-8")
    dirty_plan = dirty_consumer / "delivery-plan.json"
    dirty_runtime = tmp / "queue-fail-runtime-dirty"
    write_queue_plan(dirty_plan, queue_plan_fixture())
    dirty_result = run(
        [
            str(RUNNER),
            "preflight-plan",
            str(dirty_plan),
            "--consumer-root",
            str(dirty_consumer),
            "--runtime-root",
            str(dirty_runtime),
            "--run-id",
            "dirty",
            "--launcher",
            str(RUNNER),
            "--json",
        ]
    )
    if dirty_result.returncode == 0:
        raise AssertionError(f"dirty workspace preflight unexpectedly passed: {dirty_result.stdout}")
    dirty_status = load_status(dirty_runtime, "dirty")
    if dirty_status["result"] != "BLOCKED" or not any(check["name"] == "workspace dirty state" for check in dirty_status["checks"]):
        raise AssertionError(f"dirty workspace did not produce structured BLOCKED status: {dirty_status}")


def queue_lock_path(runtime: Path, workspace: Path) -> Path:
    digest = hashlib.sha256(str(workspace.resolve(strict=False)).encode("utf-8")).hexdigest()[:16]
    return runtime / "locks" / f"{digest}.lock"


def queue_run_calls(call_log: Path) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for line in call_log.read_text(encoding="utf-8").splitlines():
        call = json.loads(line)
        argv = call.get("argv", [])
        if len(argv) > 1 and argv[1] == "run":
            calls.append(call)
    return calls


def check_queue_run_plan(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-run-consumer")
    runner = tmp / "fake-queue-runner"
    call_log = tmp / "queue-run-calls.jsonl"
    runtime = tmp / "queue-run-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    result = run(
        [
            str(RUNNER),
            "run-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-run",
            "--launcher",
            str(runner),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    require_ok(result, "queue run-plan")
    status = load_status(runtime, "queue-run")
    if status["result"] != "DELIVERED" or status["summary"]["delivered"] != 2:
        raise AssertionError(f"queue run did not deliver both cards: {status}")
    calls = queue_run_calls(call_log)
    if len(calls) != 2:
        raise AssertionError(f"queue run should invoke one child per card: {calls}")
    first_call = calls[0]["argv"]
    if "--model" not in first_call or "gpt-test" not in first_call:
        raise AssertionError(f"per-card model override missing from live child invocation: {first_call}")
    if "--reasoning-effort" not in first_call or "low" not in first_call:
        raise AssertionError(f"per-card reasoning override missing from live child invocation: {first_call}")
    if not all(Path(card["run_status_path"]).name == "status.json" for card in status["cards"]):
        raise AssertionError(f"child status references missing: {status['cards']}")


def check_queue_fail_fast_and_locks(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-fail-fast-consumer")
    runner = tmp / "fake-queue-runner-fail"
    call_log = tmp / "queue-fail-fast-calls.jsonl"
    runtime = tmp / "queue-fail-fast-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    env["CHANGERAIL_QUEUE_FAKE_MODE"] = "no-go"
    result = run(
        [
            str(RUNNER),
            "run-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-no-go",
            "--launcher",
            str(runner),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    if result.returncode == 0:
        raise AssertionError("queue no-go unexpectedly passed")
    status = load_status(runtime, "queue-no-go")
    if status["result"] != "NO-GO" or status["summary"]["no_go"] != 1:
        raise AssertionError(f"queue did not fail fast on NO-GO: {status}")
    calls = queue_run_calls(call_log)
    if len(calls) != 1:
        raise AssertionError(f"dependent card should not launch after NO-GO: {calls}")

    lock_consumer, lock_a, _lock_b = create_queue_consumer(tmp, "queue-lock-consumer")
    lock_plan = lock_consumer / "delivery-plan.json"
    lock_runtime = tmp / "queue-lock-runtime"
    write_queue_plan(lock_plan, queue_plan_fixture())
    lock_path = queue_lock_path(lock_runtime, lock_a)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("{}\n", encoding="utf-8")
    lock_result = run(
        [
            str(RUNNER),
            "run-plan",
            str(lock_plan),
            "--consumer-root",
            str(lock_consumer),
            "--runtime-root",
            str(lock_runtime),
            "--run-id",
            "queue-lock",
            "--launcher",
            str(runner),
            "--no-push",
            "--json",
        ],
        env=runner_env(),
    )
    if lock_result.returncode == 0:
        raise AssertionError("queue lock conflict unexpectedly passed")
    lock_status = load_status(lock_runtime, "queue-lock")
    if lock_status["result"] != "BLOCKED" or not lock_path.exists():
        raise AssertionError(f"queue lock was not fail-closed/preserved: {lock_status}")


def check_queue_terminal_reason_and_missing_status(tmp: Path) -> None:
    for mode, expected_reason in (
        ("fix-budget", "fix_budget_exhausted"),
        ("external-blocker", "external_blocker"),
        ("missing-status", "missing_or_invalid_child_status"),
    ):
        consumer, _service_a, _service_b = create_queue_consumer(tmp, f"queue-{mode}-consumer")
        runner = tmp / f"fake-queue-runner-{mode}"
        runtime = tmp / f"queue-{mode}-runtime"
        plan = consumer / "delivery-plan.json"
        write_fake_queue_runner(runner)
        write_queue_plan(plan, queue_plan_fixture())
        env = runner_env()
        env["CHANGERAIL_QUEUE_FAKE_MODE"] = mode
        result = run(
            [
                str(RUNNER),
                "run-plan",
                str(plan),
                "--consumer-root",
                str(consumer),
                "--runtime-root",
                str(runtime),
                "--run-id",
                f"queue-{mode}",
                "--launcher",
                str(runner),
                "--no-push",
                "--json",
            ],
            env=env,
        )
        if result.returncode == 0:
            raise AssertionError(f"queue {mode} unexpectedly passed")
        status = load_status(runtime, f"queue-{mode}")
        first = status["cards"][0]
        if first.get("state") != "blocked" or first.get("terminal_reason") != expected_reason:
            raise AssertionError(f"queue {mode} did not preserve fail-closed reason: {status}")


def recovery_plan_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    original = queue_plan_fixture()
    augmented = json.loads(json.dumps(original))
    augmented["cards"].append(
        {
            "id": "service-a-recovery",
            "workspace": "service-a",
            "card": "service-a-recovery.md",
            "wave": 1,
            "recovery_for": "service-a-card",
        }
    )
    return original, augmented


def recovery_previous_status(
    original: dict[str, Any],
    *,
    source_state: str = "no-go",
    source_result: str = "NO-GO",
    terminal_reason: str | None = None,
) -> dict[str, Any]:
    source: dict[str, Any] = {
        "id": "service-a-card",
        "workspace": "service-a",
        "card": "service-a-card.md",
        "resolved_path": "openspec/board/3.inprogress/service-a-card.md",
        "state": source_state,
        "result": source_result,
        "wave": 1,
        "reason": f"child returned {source_result}",
    }
    if terminal_reason:
        source["terminal_reason"] = terminal_reason
    return {
        "schema": "changerail.delivery-plan-status.v1",
        "run_id": "queue-recovery",
        "updated_at": "2026-07-15T00:00:00Z",
        "plan": {"id": "queue-smoke", "path": "delivery-plan.json", "fingerprint": queue_plan_fingerprint(original)},
        "phase": "terminal",
        "result": source_result,
        "terminal_outcome": source_result,
        "mode": "no-push",
        "timestamps": {"started_at": "2026-07-15T00:00:00Z", "ended_at": "2026-07-15T00:00:01Z"},
        "cards": [
            source,
            {
                "id": "service-b-card",
                "workspace": "service-b",
                "card": "service-b-card.md",
                "resolved_path": "openspec/board/2.todo/service-b-card.md",
                "state": "blocked",
                "wave": 2,
                "depends_on": ["service-a-card"],
            },
        ],
    }


def check_queue_recovery_resume(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-recovery-consumer")
    runner = tmp / "fake-queue-runner-recovery"
    call_log = tmp / "queue-recovery-calls.jsonl"
    runtime = tmp / "queue-recovery-runtime"
    plan = consumer / "delivery-plan.json"
    original, augmented = recovery_plan_fixture()
    previous_path = runtime / "previous" / "status.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, augmented)
    write_json(previous_path, recovery_previous_status(original))
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    result = run(
        [
            str(RUNNER),
            "resume-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-recovery",
            "--launcher",
            str(runner),
            "--status-path",
            str(previous_path),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    require_ok(result, "queue recovery resume")
    status = load_status(runtime, "queue-recovery")
    cards = {card["id"]: card for card in status["cards"]}
    if cards["service-a-card"].get("state") != "recovered":
        raise AssertionError(f"source was not marked recovered: {status}")
    if cards["service-a-card"].get("recovered_by") != "service-a-recovery":
        raise AssertionError(f"source recovery lineage missing: {status}")
    if status.get("summary", {}).get("recovered") != 1 or status.get("result") != "DELIVERED":
        raise AssertionError(f"recovery aggregate status is inconsistent: {status}")
    calls = queue_run_calls(call_log)
    launched = [call.get("card") for call in calls]
    if launched != [
        "openspec/board/2.todo/service-a-recovery.md",
        "openspec/board/2.todo/service-b-card.md",
    ]:
        raise AssertionError(f"recovery did not precede downstream or source was re-run: {launched}")


def check_queue_recovery_fail_closed(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-recovery-fail-consumer")
    runner = tmp / "fake-queue-runner-recovery-fail"
    call_log = tmp / "queue-recovery-fail-calls.jsonl"
    runtime = tmp / "queue-recovery-fail-runtime"
    plan = consumer / "delivery-plan.json"
    original, augmented = recovery_plan_fixture()
    previous_path = runtime / "previous" / "status.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, augmented)
    write_json(previous_path, recovery_previous_status(original))
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    env["CHANGERAIL_QUEUE_FAKE_MODE"] = "recovery-no-go"
    result = run(
        [
            str(RUNNER),
            "resume-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-recovery-fail",
            "--launcher",
            str(runner),
            "--status-path",
            str(previous_path),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    if result.returncode == 0:
        raise AssertionError("failed recovery unexpectedly resumed downstream")
    calls = queue_run_calls(call_log)
    if [call.get("card") for call in calls] != ["openspec/board/2.todo/service-a-recovery.md"]:
        raise AssertionError(f"downstream launched after failed recovery: {calls}")


def check_queue_recovery_rejects_external_and_unrelated_drift(tmp: Path) -> None:
    for name, previous, mutate in (
        (
            "external",
            lambda original: recovery_previous_status(
                original,
                source_state="blocked",
                source_result="BLOCKED",
                terminal_reason="external_blocker",
            ),
            lambda augmented: None,
        ),
        (
            "unrelated-drift",
            lambda original: recovery_previous_status(original),
            lambda augmented: augmented["cards"][1].update({"depends_on": []}),
        ),
    ):
        consumer, _service_a, _service_b = create_queue_consumer(tmp, f"queue-recovery-{name}-consumer")
        runner = tmp / f"fake-queue-runner-recovery-{name}"
        call_log = tmp / f"queue-recovery-{name}-calls.jsonl"
        runtime = tmp / f"queue-recovery-{name}-runtime"
        plan = consumer / "delivery-plan.json"
        original, augmented = recovery_plan_fixture()
        mutate(augmented)
        previous_path = runtime / "previous" / "status.json"
        write_fake_queue_runner(runner)
        write_queue_plan(plan, augmented)
        write_json(previous_path, previous(original))
        env = runner_env()
        env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
        result = run(
            [
                str(RUNNER),
                "resume-plan",
                str(plan),
                "--consumer-root",
                str(consumer),
                "--runtime-root",
                str(runtime),
                "--run-id",
                f"queue-recovery-{name}",
                "--launcher",
                str(runner),
                "--status-path",
                str(previous_path),
                "--no-push",
                "--json",
            ],
            env=env,
        )
        if result.returncode == 0:
            raise AssertionError(f"unsafe recovery plan {name} unexpectedly passed")
        calls = queue_run_calls(call_log)
        if calls:
            raise AssertionError(f"unsafe recovery plan {name} launched live child: {calls}")


def check_queue_resume_plan(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-resume-consumer")
    runner = tmp / "fake-queue-runner-resume"
    call_log = tmp / "queue-resume-calls.jsonl"
    runtime = tmp / "queue-resume-runtime"
    plan_payload = queue_plan_fixture()
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, plan_payload)
    previous = {
        "schema": "changerail.delivery-plan-status.v1",
        "run_id": "queue-resume",
        "updated_at": "2026-07-15T00:00:00Z",
        "plan": {"id": "queue-smoke", "path": "delivery-plan.json", "fingerprint": queue_plan_fingerprint(plan_payload)},
        "phase": "terminal",
        "result": "BLOCKED",
        "terminal_outcome": "BLOCKED",
        "mode": "no-push",
        "timestamps": {"started_at": "2026-07-15T00:00:00Z", "ended_at": "2026-07-15T00:00:01Z"},
        "cards": [
            {
                "id": "service-a-card",
                "workspace": "service-a",
                "card": "service-a-card.md",
                "resolved_path": "openspec/board/3.inprogress/service-a-card.md",
                "state": "delivered",
                "result": "DELIVERED",
                "wave": 1,
            },
            {
                "id": "service-b-card",
                "workspace": "service-b",
                "card": "service-b-card.md",
                "resolved_path": "openspec/board/2.todo/service-b-card.md",
                "state": "blocked",
                "wave": 2,
                "depends_on": ["service-a-card"],
            },
        ],
    }
    previous_path = runtime / "previous" / "status.json"
    write_json(previous_path, previous)
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    result = run(
        [
            str(RUNNER),
            "resume-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-resume",
            "--launcher",
            str(runner),
            "--status-path",
            str(previous_path),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    require_ok(result, "queue resume-plan")
    status = load_status(runtime, "queue-resume")
    if status["summary"]["skipped"] != 1 or status["summary"]["delivered"] != 1:
        raise AssertionError(f"resume did not skip prior delivered card and deliver remaining card: {status}")
    calls = queue_run_calls(call_log)
    if len(calls) != 1 or calls[0].get("card") != "openspec/board/2.todo/service-b-card.md":
        raise AssertionError(f"resume should launch only unfinished card: {calls}")


def check_queue_push_success_validation(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-push-validation-consumer")
    runner = tmp / "fake-queue-runner-push"
    runtime = tmp / "queue-push-validation-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    result = run(
        [
            str(RUNNER),
            "run-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-push-validation",
            "--launcher",
            str(runner),
            "--json",
        ],
        env=runner_env(),
    )
    if result.returncode == 0:
        raise AssertionError("push-enabled queue should block when fake child does not publish board card")
    status = load_status(runtime, "queue-push-validation")
    if status["result"] != "BLOCKED" or "done card location" not in status["cards"][0].get("reason", ""):
        raise AssertionError(f"push success validation did not block inconsistent child success: {status}")


def check_queue_no_push_requires_ahead(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-no-push-upstream-consumer", no_push_ready=False)
    runner = tmp / "fake-queue-runner-no-push"
    runtime = tmp / "queue-no-push-upstream-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    result = run(
        [
            str(RUNNER),
            "run-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-no-push-upstream",
            "--launcher",
            str(runner),
            "--no-push",
            "--json",
        ],
        env=runner_env(),
    )
    if result.returncode == 0:
        raise AssertionError("no-push queue without ahead-of-upstream state unexpectedly passed")
    status = load_status(runtime, "queue-no-push-upstream")
    first = status["cards"][0]
    if status["result"] != "BLOCKED" or first.get("upstream_state") != "unknown":
        raise AssertionError(f"no-push upstream enforcement did not block structurally: {status}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-delivery-runner-") as tmp:
        workspace = Path(tmp)
        check_success_run(workspace)
        check_default_workspace_run(workspace)
        check_performance_summary_run(workspace)
        check_no_go_run(workspace)
        check_review_no_go_fallback_run(workspace)
        check_supervisor_stops_after_fallback_no_go(workspace)
        check_fix_budget_handoff_run(workspace)
        check_external_blocker_handoff_run(workspace)
        check_unstructured_unpublished_success_run(workspace)
        check_marker_like_prose_is_not_authoritative(workspace)
        check_non_terminal_error_success_run(workspace)
        check_ordered_conflict_run(workspace)
        check_nonzero_without_outcome_run(workspace)
        check_awaiting_review_run(workspace)
        check_preflight(workspace)
        check_preflight_connectivity_failure_redaction(workspace)
        check_run_preflight_failure(workspace)
        check_stale_symlink_preflight(workspace)
        check_queue_plan_preflight(workspace)
        check_queue_preflight_failures(workspace)
        check_queue_run_plan(workspace)
        check_queue_fail_fast_and_locks(workspace)
        check_queue_terminal_reason_and_missing_status(workspace)
        check_queue_resume_plan(workspace)
        check_queue_recovery_resume(workspace)
        check_queue_recovery_fail_closed(workspace)
        check_queue_recovery_rejects_external_and_unrelated_drift(workspace)
        check_queue_push_success_validation(workspace)
        check_queue_no_push_requires_ahead(workspace)
    print("ok: delivery runner smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
