#!/usr/bin/env python3
"""Smoke checks for the ChangeRail non-interactive delivery runner."""

from __future__ import annotations

import http.server
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "bin" / "changerail-delivery-runner"
VERDICT_HELPER = ROOT / "scripts" / "changerail_review_verdict.py"
MANIFEST_HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"
EVIDENCE_HELPER = ROOT / "bin" / "changerail-evidence"
CARD = "openspec/board/3.inprogress/harden-delivery-operations.md"
ONE_COMMAND_CARD = "openspec/board/2.todo/one-command-delivery-smoke.md"
ONE_COMMAND_DONE_CARD = "openspec/board/4.done/one-command-delivery-smoke.md"
ONE_COMMAND_CHANGE = "one-command-delivery-smoke"


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
    for name in (
        "CODEX_HOME",
        "CODEX_WORKDIR",
        "CODEX_AUTH_TOKEN",
        "OPENAI_API_KEY",
        "CHANGERAIL_FAKE_MODE",
        "CHANGERAIL_DISCOVERY_POLICY",
        "CHANGERAIL_COMMAND_OUTPUT_THRESHOLD_BYTES",
    ):
        env.pop(name, None)
    if mode:
        env["CHANGERAIL_FAKE_MODE"] = mode
    return env


def no_codex_path_env(tmp: Path) -> dict[str, str]:
    bin_dir = tmp / "no-codex-path"
    bin_dir.mkdir(exist_ok=True)
    tools = {
        "python": sys.executable,
        "python3": sys.executable,
    }
    for name in ("git", "readlink", "dirname", "sed", "mkdir"):
        found = shutil.which(name)
        if not found:
            raise AssertionError(f"required tool not found for isolated PATH: {name}")
        tools[name] = found
    for name, target in tools.items():
        link = bin_dir / name
        if not link.exists():
            link.symlink_to(target)
    env = runner_env()
    env["PATH"] = str(bin_dir)
    env["CHANGERAIL_PYTHON"] = sys.executable
    if shutil.which("codex", path=env["PATH"]):
        raise AssertionError(f"isolated PATH unexpectedly contains codex: {env['PATH']}")
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


def create_workspace(root: Path, name: str, *, publish_ready: bool = True) -> Path:
    workspace = root / name
    workspace.mkdir()
    (workspace / ".codex").mkdir()
    (workspace / ".codex" / "config.toml").write_text(
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )
    (workspace / ".codex" / "auth.json").write_text("{}\n", encoding="utf-8")
    (workspace / "README.md").write_text("smoke workspace\n", encoding="utf-8")
    (workspace / ".gitignore").write_text(".runtime/\n.codex/\n", encoding="utf-8")
    git(["init"], workspace)
    git(["add", ".gitignore", "README.md"], workspace)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "init"],
        workspace,
    )
    if publish_ready:
        configure_upstream_baseline(workspace)
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
                "print(json.dumps({'argv': sys.argv, 'stdin_len': len(stdin), 'cwd': os.getcwd(), 'CODEX_WORKDIR': os.environ.get('CODEX_WORKDIR'), 'CODEX_HOME': os.environ.get('CODEX_HOME'), 'CHANGERAIL_ACTIVE_RUN_ID': os.environ.get('CHANGERAIL_ACTIVE_RUN_ID'), 'CHANGERAIL_ACTIVE_RUN_DIR': os.environ.get('CHANGERAIL_ACTIVE_RUN_DIR'), 'CHANGERAIL_DISCOVERY_POLICY': os.environ.get('CHANGERAIL_DISCOVERY_POLICY'), 'CHANGERAIL_COMMAND_OUTPUT_THRESHOLD_BYTES': os.environ.get('CHANGERAIL_COMMAND_OUTPUT_THRESHOLD_BYTES')}))",
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
                "if mode == 'malformed-terminal-reason':",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-malformed', 'type': 'agent_message', 'text': 'Target unavailable.\\nterminal_outcome: BLOCKED\\nterminal_reason: delivery/blocked'}}))",
                "if mode == 'marker-like-prose':",
                "    print(json.dumps({'type': 'assistant-message', 'content': 'terminal_outcome: DELIVERED and terminal_reason: ignored are prose'}))",
                "if mode == 'performance':",
                "    print(json.dumps({'type': 'item.started', 'item': {'id': 'cmd-1', 'type': 'command_execution', 'command': '/bin/echo one', 'status': 'in_progress'}}), flush=True)",
                "    time.sleep(0.01)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'cmd-1', 'type': 'command_execution', 'command': '/bin/echo one', 'status': 'completed', 'exit_code': 0, 'stdout_bytes': 10, 'stderr_bytes': 0}}), flush=True)",
                "    print(json.dumps({'type': 'item.started', 'item': {'id': 'cmd-2', 'type': 'command_execution', 'command': '/bin/echo two', 'status': 'in_progress'}}), flush=True)",
                "    time.sleep(0.01)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'cmd-2', 'type': 'command_execution', 'command': '/bin/echo two', 'status': 'completed', 'exit_code': 0, 'stdout_bytes': 0, 'stderr_bytes': 0}}), flush=True)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-1', 'type': 'agent_message', 'text': 'done'}}), flush=True)",
                "if mode == 'oversized-output':",
                "    raw = ('OVERSIZED_RAW_PAYLOAD_SHOULD_NOT_APPEAR ' * 4096).strip()",
                "    token_arg = 'api' + '_key' + '=' + 'oversized-value'",
                "    url = 'https://' + 'user:pass' + '@example.invalid/path'",
                "    runtime_path = os.path.join(os.environ.get('CHANGERAIL_ACTIVE_RUN_DIR', '.runtime/changerail/delivery-runs/oversized-output'), 'stdout.jsonl')",
                "    command = '/usr/bin/rg ' + token_arg + ' ' + url + ' ' + runtime_path",
                "    print(json.dumps({'type': 'item.started', 'item': {'id': 'cmd-big', 'type': 'command_execution', 'command': command, 'status': 'in_progress'}}), flush=True)",
                "    time.sleep(0.01)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'cmd-big', 'type': 'command_execution', 'command': command, 'status': 'completed', 'exit_code': 0, 'stdout': raw, 'stdout_bytes': len(raw.encode('utf-8')), 'stderr_bytes': 0, 'stdout_truncated': True}}), flush=True)",
                "    print(json.dumps({'type': 'item.completed', 'item': {'id': 'msg-oversized', 'type': 'agent_message', 'text': 'done'}}), flush=True)",
                "if mode not in {'unstructured-success', 'safety-stop-no-go', 'fix-budget-exhausted', 'external-blocker', 'malformed-terminal-reason', 'marker-like-prose', 'no-go', 'awaiting-review', 'ordered-conflict'}:",
                "    print(json.dumps({'terminal_outcome': 'DELIVERED'}))",
                "print(json.dumps({'usage': {'input_tokens': 3, 'cached_input_tokens': 1, 'uncached_input_tokens': 2, 'output_tokens': 5, 'reasoning_tokens': 1, 'total_tokens': 8}}))",
                "sys.exit(1 if mode == 'no-go' else (2 if mode == 'nonzero' else 0))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_one_command_launcher(path: Path) -> None:
    path.write_text(
        r'''#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path.cwd()
REVIEW_HELPER = Path(%r)
DEFAULT_CARD = %r
DONE_CARD = %r
CHANGE = %r
NOW = "2026-08-01T00:00:00Z"


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def fail(message, code=1):
    emit({"type": "tool/result", "data": {"status": "failed", "message": message}})
    sys.exit(code)


def git(*args):
    result = subprocess.run(["git", *args], cwd=WORKSPACE, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or "git command failed", result.returncode)
    return result.stdout.strip()


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def card_from_prompt():
    prompt = sys.argv[-1] if sys.argv else ""
    parts = prompt.split()
    for index, value in enumerate(parts):
        if value in {"$changerail-deliver", "$chrl-deliver"} and index + 1 < len(parts):
            return parts[index + 1]
    return os.environ.get("CHANGERAIL_ONE_COMMAND_CARD", DEFAULT_CARD)


def rel(path):
    return path.relative_to(WORKSPACE).as_posix()


def card_id(card_path):
    return Path(card_path).name.removesuffix(".md")


def final_card_text(card_path):
    return "\n".join(
        [
            "# One-command delivery smoke",
            "",
            "## Status",
            "4.done",
            "",
            "## Owner",
            "ChangeRail smoke",
            "",
            "## OpenSpec Stage",
            "published",
            "",
            "## Acceptance",
            "- One-command delivery fixture reached reviewed publish.",
            "",
            "## Change Set",
            f"- `{CHANGE}` (archived)",
            "",
            "## Archive",
            f"- `openspec/changes/archive/2026-08-01-{CHANGE}/`",
            "",
            "## Result",
            "Reviewed payload finalized through ChangeRail scoped publish; exact ledger retained in ignored manifest.",
            "",
            "## Next",
            "- done",
            "",
            "## Log",
            "- 2026-08-01T00:00:00Z one-command delivery smoke finalized the card into `4.done`.",
            "",
        ]
    )


def write_evidence(card_path):
    cid = card_id(card_path)
    evidence_dir = WORKSPACE / ".runtime" / "changerail" / "evidence" / cid
    raw_path = evidence_dir / "outputs" / "one-command-success.txt"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text("one-command delivery smoke produced reviewed publish state\n", encoding="utf-8")
    index_path = evidence_dir / "index.json"
    raw_rel = rel(raw_path)
    payload = {
        "schema": "changerail.evidence-index.v1",
        "updated_at": NOW,
        "workspace": {"root": str(WORKSPACE), "repository": WORKSPACE.name},
        "scope": {"card_id": cid, "card_path": card_path, "changes": [CHANGE]},
        "entries": [
            {
                "id": "one-command-success",
                "path": raw_rel,
                "role": "raw_output",
                "storage": "runtime",
                "phase": "do",
                "classification": "mandatory",
                "change": CHANGE,
                "kind": "smoke-output",
                "command": {
                    "argv": ["python3", "scripts/smoke-delivery-runner.py"],
                    "display": "python3 scripts/smoke-delivery-runner.py",
                },
                "status": "passed",
                "exit_code": 0,
                "started_at": NOW,
                "ended_at": NOW,
                "duration_seconds": 0,
                "summary": "one-command delivery fake child produced final repository state",
                "raw_output_path": raw_rel,
                "redacted": False,
            }
        ],
    }
    write_json(index_path, payload)
    return rel(index_path), raw_rel


def fingerprint():
    result = subprocess.run(
        [sys.executable, str(REVIEW_HELPER), "fingerprint", "--workspace", str(WORKSPACE)],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or "fingerprint failed", result.returncode)
    return json.loads(result.stdout)


def write_verdict(card_path, result, reviewed_path, evidence_index=None, raw_output=None):
    cid = card_id(card_path)
    data = fingerprint()
    if result == "go":
        acceptance = [
            {
                "criterion": "one-command delivery reached reviewed publish",
                "verdict": "pass",
                "evidence": "local smoke fixture final card, manifest, evidence and Git history align",
                "evidence_refs": [
                    {
                        "id": "one-command-success",
                        "index_path": evidence_index,
                        "raw_output_path": raw_output,
                        "classification": "mandatory",
                    }
                ],
            }
        ]
        findings = []
        audit = {"claims_checked": 1, "claims_unbacked": 0}
    else:
        acceptance = [
            {
                "criterion": "review budget permits same-card rescue",
                "verdict": "fail",
                "evidence": "smoke fixture exhausted review rescue budget",
            }
        ]
        findings = [
            {
                "id": "R1",
                "severity": "blocker",
                "area": "process",
                "summary": "same-card review rescue budget is exhausted",
            }
        ]
        audit = {"claims_checked": 1, "claims_unbacked": 0}
    payload = {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": NOW,
        "card": {"id": cid, "path": reviewed_path},
        "workspace": {
            "root": data["workspace"],
            "head_commit": data["head_commit"],
            "tree_sha": data["tree_sha"],
            "diff_fingerprint": data["diff_fingerprint"],
        },
        "reviewer": {
            "kind": "codex-exec",
            "independence": {
                "fresh_context": True,
                "did_not_plan_or_implement": True,
                "basis": "fresh fake reviewer context in deterministic smoke fixture",
            },
        },
        "result": result,
        "review_cycle": 1 if result == "go" else 6,
        "acceptance": acceptance,
        "findings": findings,
        "evidence_audit": audit,
    }
    verdict_path = WORKSPACE / ".runtime" / "changerail" / "reviews" / f"{cid}.json"
    write_json(verdict_path, payload)
    return rel(verdict_path), data["tree_sha"]


def write_history(card_path, result, verdict_path, exhausted):
    cid = card_id(card_path)
    cycle = {
        "review_cycle": 1 if result == "go" else 3,
        "same_card_rescue_attempt": 0 if result == "go" else 2,
        "result": result,
        "reviewed_at": NOW,
        "verdict_path": verdict_path,
        "findings": {"blocker": 0 if result == "go" else 1, "major": 0, "minor": 0},
        "acceptance": {
            "pass": 1 if result == "go" else 0,
            "fail": 0 if result == "go" else 1,
            "unverifiable": 0,
            "not_applicable": 0,
        },
        "finding_details": []
        if result == "go"
        else [{"id": "R1", "severity": "blocker", "summary": "same-card review rescue budget is exhausted"}],
    }
    payload = {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": NOW,
        "card": {"id": cid, "path": card_path},
        "workspace": {"root": str(WORKSPACE), "head_commit": git("rev-parse", "HEAD")},
        "cycles": [cycle],
        "rescue_budget": {
            "limit": 2,
            "used": 0 if result == "go" else 2,
            "remaining": 2 if result == "go" else 0,
            "exhausted": exhausted,
        },
    }
    write_json(WORKSPACE / ".runtime" / "changerail" / "reviews" / f"{cid}.history.json", payload)


def manifest_payload(card_path, done_path, archive_dir, spec_path, verdict_path, evidence_index, raw_output):
    cid = card_id(card_path)
    manifest_path = WORKSPACE / ".runtime" / "changerail" / "delivery-manifests" / f"{cid}.json"
    history_path = WORKSPACE / ".runtime" / "changerail" / "reviews" / f"{cid}.history.json"
    evidence_root = WORKSPACE / ".runtime" / "changerail" / "evidence" / cid
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": NOW,
        "workspace": {"root": str(WORKSPACE), "repository": WORKSPACE.name},
        "card": {"id": cid, "path": card_path, "status": "4.done"},
        "changes": [
            {
                "slug": CHANGE,
                "state": "archived",
                "order": 1,
                "archive_path": rel(archive_dir),
            }
        ],
        "committable_paths": [
            {
                "path": rel(done_path),
                "kind": "board",
                "phase": "pub",
                "operation": "rename",
                "source_path": card_path,
                "target_path": rel(done_path),
            },
            {
                "path": rel(archive_dir / "proposal.md"),
                "kind": "openspec_archive",
                "phase": "archive",
                "operation": "add",
                "target_path": rel(archive_dir / "proposal.md"),
            },
            {
                "path": rel(archive_dir / "tasks.md"),
                "kind": "openspec_archive",
                "phase": "archive",
                "operation": "add",
                "target_path": rel(archive_dir / "tasks.md"),
            },
            {
                "path": rel(spec_path),
                "kind": "openspec_spec",
                "phase": "do",
                "operation": "add",
                "target_path": rel(spec_path),
            },
        ],
        "excluded_runtime_paths": [
            {"path": rel(manifest_path), "kind": "manifest", "phase": "do", "reason": "ignored runtime manifest"},
            {"path": verdict_path, "kind": "review-verdict", "phase": "review", "reason": "ignored runtime verdict"},
            {"path": rel(history_path), "kind": "review-history", "phase": "review", "reason": "ignored runtime history"},
            {"path": rel(evidence_root), "kind": "evidence", "phase": "do", "reason": "ignored retained evidence"},
        ],
        "preexisting_dirty": [],
        "verification_summary": {
            "result": "passed",
            "summary": "one-command delivery smoke produced final observable state",
            "commands": [
                {
                    "command": "python3 scripts/smoke-delivery-runner.py",
                    "outcome": "one-command fixture passed",
                    "evidence": {
                        "id": "one-command-success",
                        "index_path": evidence_index,
                        "raw_output_path": raw_output,
                        "classification": "mandatory",
                    },
                }
            ],
        },
        "review_summary": {
            "result": "go",
            "summary": "fake independent review passed for one-command smoke",
            "review_cycle": 1,
            "verdict_path": verdict_path,
            "findings": {"blocker": 0, "major": 0, "minor": 0},
        },
        "final_card_state": {
            "path": rel(done_path),
            "status": "4.done",
            "result_summary": "reviewed payload finalized through scoped publish",
        },
        "publish": {"status": "pending"},
    }


def run_success(card_path):
    source = WORKSPACE / card_path
    if not source.is_file():
        fail(f"card not found: {card_path}")
    done = WORKSPACE / "openspec" / "board" / "4.done" / source.name
    done.parent.mkdir(parents=True, exist_ok=True)
    done.write_text(final_card_text(card_path), encoding="utf-8")
    source.unlink()

    archive_dir = WORKSPACE / "openspec" / "changes" / "archive" / f"2026-08-01-{CHANGE}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "proposal.md").write_text("## Why\n\nOne-command smoke archive.\n", encoding="utf-8")
    (archive_dir / "tasks.md").write_text("## 1. Smoke\n\n- [x] 1.1 Delivered by fake child.\n", encoding="utf-8")
    spec_path = WORKSPACE / "openspec" / "specs" / "changerail-delivery-runner" / "spec.md"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(
        "### Requirement: One-command smoke fixture\n"
        "Temporary fixture spec written by the fake delivery child.\n",
        encoding="utf-8",
    )

    evidence_index, raw_output = write_evidence(card_path)
    verdict_path, reviewed_tree = write_verdict(card_path, "go", rel(done), evidence_index, raw_output)
    write_history(card_path, "go", verdict_path, False)
    manifest_path = WORKSPACE / ".runtime" / "changerail" / "delivery-manifests" / f"{card_id(card_path)}.json"
    write_json(manifest_path, manifest_payload(card_path, done, archive_dir, spec_path, verdict_path, evidence_index, raw_output))

    git("add", "-A", "--", card_path, rel(done), rel(archive_dir), rel(spec_path))
    git("-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "deliver one-command smoke")
    published = git("rev-parse", "HEAD")
    git("push", "origin", "HEAD")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["updated_at"] = NOW
    manifest["publish"] = {
        "status": "pushed",
        "payload_commit": published,
        "published_commit": published,
        "remote": "origin",
        "branch": git("branch", "--show-current"),
        "pushed_at": NOW,
    }
    manifest["notes"] = [f"reviewed_tree={reviewed_tree}"]
    write_json(manifest_path, manifest)
    emit({"type": "item.completed", "item": {"id": "msg-one-command", "type": "agent_message", "text": "delivered"}})


def run_review_budget_exhausted(card_path):
    verdict_path, _tree = write_verdict(card_path, "no-go", card_path)
    write_history(card_path, "no-go", verdict_path, True)
    emit({"type": "external-review/no-go", "data": {"result": "no-go", "rescue_budget": {"exhausted": True}}})


stdin = sys.stdin.read()
emit(
    {
        "argv": sys.argv,
        "stdin_len": len(stdin),
        "cwd": os.getcwd(),
        "CODEX_WORKDIR": os.environ.get("CODEX_WORKDIR"),
        "CODEX_HOME": os.environ.get("CODEX_HOME"),
    }
)
mode = os.environ.get("CHANGERAIL_ONE_COMMAND_MODE", "success")
card = card_from_prompt()
if mode == "success":
    run_success(card)
elif mode == "review-budget-exhausted":
    run_review_budget_exhausted(card)
elif mode == "noop":
    pass
else:
    fail(f"unknown one-command mode: {mode}", 2)
emit({"usage": {"input_tokens": 3, "cached_input_tokens": 1, "uncached_input_tokens": 2, "output_tokens": 5, "reasoning_tokens": 1, "total_tokens": 8}})
sys.exit(1 if mode == "review-budget-exhausted" else 0)
'''
        % (str(VERDICT_HELPER), ONE_COMMAND_CARD, ONE_COMMAND_DONE_CARD, ONE_COMMAND_CHANGE),
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_git(path: Path) -> None:
    real_git = shutil.which("git")
    if not real_git:
        raise AssertionError("git binary not found for fake git wrapper")
    path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os, subprocess, sys, time",
                f"REAL_GIT = {real_git!r}",
                "if 'ls-remote' not in sys.argv:",
                "    os.execv(REAL_GIT, [REAL_GIT, *sys.argv[1:]])",
                "mode = os.environ.get('CHANGERAIL_FAKE_GIT_MODE', 'success')",
                "log = os.environ.get('CHANGERAIL_FAKE_GIT_LOG')",
                "if log:",
                "    with open(log, 'a', encoding='utf-8') as handle:",
                "        handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "if mode == 'success':",
                "    sys.exit(0)",
                "if mode == 'ssh_config':",
                "    sys.stderr.write('Bad configuration option: Include\\n')",
                "    sys.exit(128)",
                "if mode == 'dns':",
                "    sys.stderr.write('ssh: Could not resolve hostname example.invalid: Name or service not known\\n')",
                "    sys.exit(128)",
                "if mode == 'auth':",
                "    sys.stderr.write('git@example.invalid: Permission denied (publickey).\\n')",
                "    sys.exit(128)",
                "if mode == 'missing_branch':",
                "    sys.exit(2)",
                "if mode == 'timeout':",
                "    time.sleep(2.0)",
                "    sys.exit(128)",
                "if mode == 'unknown_remote_failure':",
                "    sys.stderr.write('fatal: remote end hung up unexpectedly\\n')",
                "    sys.exit(128)",
                "sys.stderr.write('fatal: unexpected fake git mode\\n')",
                "sys.exit(128)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def fake_git_env(tmp: Path, mode: str, *, timeout: float | None = None, log: Path | None = None) -> dict[str, str]:
    bin_dir = tmp / f"fake-git-{mode}"
    bin_dir.mkdir(exist_ok=True)
    write_fake_git(bin_dir / "git")
    env = runner_env()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["CHANGERAIL_FAKE_GIT_MODE"] = mode
    if timeout is not None:
        env["CHANGERAIL_REMOTE_REACHABILITY_TIMEOUT_SECONDS"] = str(timeout)
    if log is not None:
        env["CHANGERAIL_FAKE_GIT_LOG"] = str(log)
    return env


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
                "preflight.add_argument('--deliver-arg', action='append', default=[])",
                "preflight.add_argument('--json', action='store_true')",
                "preflight.add_argument('--write-status', action='store_true')",
                "resume = sub.add_parser('resume')",
                "resume.add_argument('card')",
                "resume.add_argument('--status-path', required=True)",
                "resume.add_argument('--workspace', required=True)",
                "resume.add_argument('--runtime-root', required=True)",
                "resume.add_argument('--run-id', required=True)",
                "resume.add_argument('--model')",
                "resume.add_argument('--reasoning-effort')",
                "resume.add_argument('--deliver-arg', action='append', default=[])",
                "args = parser.parse_args()",
                "mode = os.environ.get('CHANGERAIL_QUEUE_FAKE_MODE')",
                "preflight_mode = os.environ.get('CHANGERAIL_QUEUE_PREFLIGHT_MODE')",
                "call_log = os.environ.get('CHANGERAIL_FAKE_CALL_LOG')",
                "if call_log:",
                "    with open(call_log, 'a', encoding='utf-8') as handle:",
                "        handle.write(json.dumps({'argv': sys.argv, 'card': args.card}) + '\\n')",
                "if args.command == 'preflight':",
                "    result = 'DELIVERED'",
                "    checks = [{'name': 'fake', 'status': 'pass', 'message': 'ready'}]",
                "    if preflight_mode == 'auth-fail' and 'service-a-card' in args.card:",
                "        result = 'BLOCKED'",
                "        checks = [{'name': 'CODEX auth', 'status': 'fail', 'message': 'no auth marker or supported auth environment variable found; see docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner'}]",
                "    if preflight_mode == 'remote-fail' and 'service-a-card' in args.card:",
                "        result = 'BLOCKED'",
                "        checks = [{'name': 'publish target', 'status': 'fail', 'message': 'mode=remote-push remote=origin branch=main remote_url_class=ssh reachable=false failure_class=dns detail=ssh: Could not resolve hostname example.invalid', 'result': 'failed', 'remote': 'origin', 'branch': 'main', 'remote_url_class': 'ssh', 'failure_class': 'dns', 'retryable': True, 'attempts': 2, 'detail': 'ssh: Could not resolve hostname example.invalid', 'evidence': {'command': 'git ls-remote --exit-code <remote> refs/heads/<branch>', 'result': 'failed', 'detail': 'ssh: Could not resolve hostname example.invalid'}}]",
                "    status = {",
                "        'schema': 'changerail.delivery-run.v1',",
                "        'run_id': args.run_id,",
                "        'updated_at': '2026-07-15T00:00:00Z',",
                "        'workspace': {'root': args.workspace},",
                "        'card': {'id': Path(args.card).name.removesuffix('.md'), 'path': args.card},",
                "        'phase': 'preflight',",
                "        'result': result,",
                "        'timestamps': {'started_at': '2026-07-15T00:00:00Z', 'ended_at': '2026-07-15T00:00:01Z'},",
                "        'command': {'argv': sys.argv, 'launcher': sys.argv[0], 'stdin': 'closed', 'json': True},",
                "        'usage': {'available': False, 'reason': 'fake queue preflight'},",
                "        'preflight': {'checks': checks},",
                "    }",
                "    path = Path(args.runtime_root) / args.run_id / 'status.json'",
                "    path.parent.mkdir(parents=True, exist_ok=True)",
                "    path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
                "    if result != 'DELIVERED':",
                "        print('RAW_CHILD_STDOUT_SHOULD_NOT_APPEAR')",
                "    print(json.dumps(status))",
                "    sys.exit(0 if result == 'DELIVERED' else 1)",
                "if mode == 'missing-status' and 'service-a-card' in args.card:",
                "    sys.exit(0)",
                "if args.command == 'resume':",
                "    dirty = Path(args.workspace) / 'DIRTY.txt'",
                "    if dirty.exists():",
                "        dirty.unlink()",
                "result = 'DELIVERED'",
                "terminal_reason = None",
                "if mode == 'no-go' and 'service-a-card' in args.card:",
                "    result = 'NO-GO'",
                "if mode == 'blocked' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "if mode == 'fix-budget' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "    terminal_reason = 'fix_budget_exhausted'",
                "if mode == 'investigation-required' and 'service-a-card' in args.card and args.command == 'run':",
                "    result = 'BLOCKED'",
                "    terminal_reason = 'investigation_required'",
                "if mode == 'external-blocker' and 'service-a-card' in args.card:",
                "    result = 'BLOCKED'",
                "    terminal_reason = 'external_blocker'",
                "if mode == 'recovery-no-go' and 'service-a-recovery' in args.card:",
                "    result = 'NO-GO'",
                "if args.command == 'resume' and 'service-a-card' in args.card:",
                "    resume_reasons = {",
                "        'resume-stale-auth': 'authorization_stale',",
                "        'resume-wrong-card': 'card_mismatch',",
                "        'resume-wrong-workspace': 'workspace_mismatch',",
                "        'resume-fingerprint-drift': 'payload_drift',",
                "    }",
                "    if mode in resume_reasons:",
                "        result = 'BLOCKED'",
                "        terminal_reason = resume_reasons[mode]",
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
                "if terminal_reason == 'investigation_required':",
                "    status['retained_payload'] = {",
                "        'schema': 'changerail.retained-payload-identity.v1',",
                "        'source_run_id': args.run_id,",
                "        'source_status_path': str(Path('.runtime/changerail/delivery-runs') / args.run_id / 'status.json'),",
                "        'captured_at': '2026-07-15T00:00:00Z',",
                "        'card': {'id': Path(args.card).name.removesuffix('.md'), 'path': args.card},",
                "        'workspace': {'root': args.workspace},",
                "        'head_commit': '1' * 40,",
                "        'tree_sha': '2' * 40,",
                "        'diff_fingerprint': 'sha256:' + '3' * 64,",
                "        'review_target': {'kind': 'working-tree'},",
                "    }",
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


def require_private_mode(path: Path, expected: int) -> None:
    actual = stat.S_IMODE(path.stat().st_mode)
    if actual != expected:
        raise AssertionError(f"private runtime mode mismatch for {path.name}: expected {expected:o}, got {actual:o}")


def single_card_status_payload(
    workspace: Path,
    run_id: str,
    *,
    card: str = CARD,
    result: str = "BLOCKED",
    phase: str = "terminal",
    terminal_reason: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "changerail.delivery-run.v1",
        "run_id": run_id,
        "updated_at": "2026-07-15T00:00:00Z",
        "workspace": {
            "root": str(workspace),
            "repository": workspace.name,
        },
        "card": {
            "id": Path(card).name.removesuffix(".md"),
            "path": card,
        },
        "phase": phase,
        "result": result,
        "timestamps": {
            "started_at": "2026-07-15T00:00:00Z",
        },
        "command": {
            "argv": [],
            "launcher": str(RUNNER),
            "stdin": "closed",
            "json": True,
        },
        "usage": {
            "available": False,
            "reason": "smoke fixture",
        },
    }
    if phase == "terminal":
        payload["timestamps"]["ended_at"] = "2026-07-15T00:00:01Z"
        payload["terminal_outcome"] = result
    if terminal_reason:
        payload["terminal_reason"] = terminal_reason
    return payload


def single_card_manifest_payload(workspace: Path, card: str = CARD) -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": "2026-07-15T00:00:00Z",
        "workspace": {
            "root": str(workspace),
            "repository": workspace.name,
        },
        "card": {
            "id": Path(card).name.removesuffix(".md"),
            "path": card,
        },
        "changes": [
            {
                "slug": "harden-delivery-operations",
                "state": "archived",
                "order": 1,
            }
        ],
        "committable_paths": [],
        "excluded_runtime_paths": [],
        "preexisting_dirty": [],
        "runtime_pause_reasons": [
            {
                "id": "pause-1",
                "category": "safety_pause",
                "summary": "smoke pause summary",
                "next_action": "$changerail-deliver openspec/board/3.inprogress/harden-delivery-operations.md",
            }
        ],
    }


def single_card_verdict_payload(workspace: Path, card: str = CARD) -> dict[str, Any]:
    return {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": "2026-07-15T00:00:00Z",
        "card": {
            "id": Path(card).name.removesuffix(".md"),
            "path": card,
        },
        "workspace": {
            "root": str(workspace),
            "head_commit": "1" * 40,
            "tree_sha": "2" * 40,
            "diff_fingerprint": "sha256:" + "3" * 64,
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
        "review_cycle": 1,
        "acceptance": [
            {
                "criterion": "status reader smoke",
                "verdict": "fail",
                "evidence": "smoke fixture",
            }
        ],
        "findings": [
            {
                "id": "R1",
                "severity": "blocker",
                "area": "process",
                "summary": "smoke no-go diagnostic",
            }
        ],
    }


def single_card_history_payload(workspace: Path, card: str = CARD) -> dict[str, Any]:
    card_id = Path(card).name.removesuffix(".md")
    return {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": "2026-07-15T00:00:00Z",
        "card": {
            "id": card_id,
            "path": card,
        },
        "workspace": {
            "root": str(workspace),
            "head_commit": "1" * 40,
        },
        "cycles": [
            {
                "review_cycle": 1,
                "same_card_rescue_attempt": 0,
                "result": "no-go",
                "reviewed_at": "2026-07-15T00:00:00Z",
                "verdict_path": f".runtime/changerail/reviews/{card_id}.json",
                "findings": {
                    "blocker": 1,
                    "major": 0,
                    "minor": 0,
                },
                "finding_details": [
                    {
                        "id": "R1",
                        "severity": "blocker",
                        "summary": "smoke no-go diagnostic",
                    }
                ],
                "acceptance": {
                    "pass": 0,
                    "fail": 1,
                    "unverifiable": 0,
                    "not_applicable": 0,
                },
            }
        ],
    }


def single_card_evidence_payload(workspace: Path, card: str = CARD) -> dict[str, Any]:
    return {
        "schema": "changerail.evidence-index.v1",
        "updated_at": "2026-07-15T00:00:00Z",
        "workspace": {
            "root": str(workspace),
            "repository": workspace.name,
        },
        "scope": {
            "card_id": Path(card).name.removesuffix(".md"),
            "card_path": card,
        },
        "entries": [],
    }


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def commit_paths(workspace: Path, message: str, *paths: str) -> None:
    git(["add", *paths], workspace)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", message],
        workspace,
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
    service_a = create_workspace(consumer, "service-a", publish_ready=False)
    service_b = create_workspace(consumer, "service-b", publish_ready=False)
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
            "tree_sha": data["tree_sha"],
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


def write_one_command_card(workspace: Path) -> None:
    path = workspace / ONE_COMMAND_CARD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# One-command delivery smoke",
                "",
                "## Status",
                "2.todo",
                "",
                "## Owner",
                "ChangeRail smoke",
                "",
                "## OpenSpec Stage",
                "story",
                "",
                "## Acceptance",
                "- One-command delivery reaches reviewed publish.",
                "- Runtime manifest, verdict, evidence and runner status align.",
                "",
                "## Change Set",
                f"- `{ONE_COMMAND_CHANGE}` (planned)",
                "",
                f"## Change 1: `{ONE_COMMAND_CHANGE}`",
                "",
                "### Why",
                "Prove the one-command runner handoff with a local smoke fixture.",
                "",
                "### Goal",
                "Reach reviewed publish through one runner invocation.",
                "",
                "### Acceptance",
                "- Final state is observable in Git, card and runtime evidence.",
                "",
                "### Depends On",
                "- none",
                "",
                "### Related",
                f"- `openspec/changes/{ONE_COMMAND_CHANGE}/`",
                "",
                "## Result",
                "not started",
                "",
                "## Next",
                f"- `$chrl-deliver {ONE_COMMAND_CARD}`",
                "",
                "## Log",
                "- 2026-08-01T00:00:00Z smoke card created.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def create_one_command_workspace(tmp: Path, name: str) -> Path:
    workspace = create_workspace(tmp, name, publish_ready=False)
    write_one_command_card(workspace)
    git(["add", ONE_COMMAND_CARD], workspace)
    git(
        [
            "-c",
            "user.name=ChangeRail Smoke",
            "-c",
            "user.email=changerail-smoke@example.invalid",
            "commit",
            "-m",
            "add one-command smoke card",
        ],
        workspace,
    )
    configure_upstream_baseline(workspace)
    return workspace


def remote_head(workspace: Path) -> str:
    branch = git(["branch", "--show-current"], workspace)
    output = git(["ls-remote", "origin", f"refs/heads/{branch}"], workspace)
    return output.split()[0]


def manifest_scope_paths(manifest: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for entry in manifest.get("committable_paths", []):
        if not isinstance(entry, dict):
            continue
        for key in ("path", "source_path", "target_path"):
            value = entry.get(key)
            if isinstance(value, str):
                paths.add(value)
    return paths


def changed_paths_in_head(workspace: Path) -> set[str]:
    output = git(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], workspace)
    return {line for line in output.splitlines() if line}


def assert_one_command_success(workspace: Path, runtime: Path, run_id: str, baseline: str) -> None:
    status = load_status(runtime, run_id)
    if status["result"] != "DELIVERED" or status.get("terminal_outcome") != "DELIVERED":
        raise AssertionError(f"one-command run did not deliver: {status}")
    published = head_commit(workspace)
    if not published or published == baseline:
        raise AssertionError(f"one-command run did not create a payload commit: {published}")
    if status.get("commit") != published:
        raise AssertionError(f"runner status commit does not match workspace HEAD: {status}")
    if remote_head(workspace) != published:
        raise AssertionError("one-command run did not push the final commit to the local bare remote")
    if (workspace / ONE_COMMAND_CARD).exists() or not (workspace / ONE_COMMAND_DONE_CARD).is_file():
        raise AssertionError("final card was not uniquely moved to 4.done")

    manifest_path = workspace / ".runtime" / "changerail" / "delivery-manifests" / "one-command-delivery-smoke.json"
    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / "one-command-delivery-smoke.json"
    history_path = workspace / ".runtime" / "changerail" / "reviews" / "one-command-delivery-smoke.history.json"
    evidence_index = workspace / ".runtime" / "changerail" / "evidence" / "one-command-delivery-smoke" / "index.json"
    for path in (manifest_path, verdict_path, history_path, evidence_index):
        if not path.is_file():
            raise AssertionError(f"expected runtime artifact missing: {path}")

    require_ok(
        run([sys.executable, str(MANIFEST_HELPER), "validate", str(manifest_path), "--json"]),
        "one-command manifest validate",
    )
    require_ok(
        run([str(EVIDENCE_HELPER), "validate", str(evidence_index), "--workspace", str(workspace), "--json"]),
        "one-command evidence validate",
    )
    require_ok(run([sys.executable, str(VERDICT_HELPER), "validate", str(verdict_path), "--json"]), "verdict validate")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))
    if manifest["publish"]["published_commit"] != published or manifest["publish"]["status"] != "pushed":
        raise AssertionError(f"manifest publish metadata does not match final commit: {manifest['publish']}")
    if manifest["review_summary"]["verdict_path"] != ".runtime/changerail/reviews/one-command-delivery-smoke.json":
        raise AssertionError(f"manifest does not reference canonical verdict: {manifest['review_summary']}")
    if history.get("rescue_budget", {}).get("exhausted") is not False:
        raise AssertionError(f"success history should record non-exhausted rescue budget: {history}")
    if verdict["workspace"]["tree_sha"] != git(["rev-parse", "HEAD^{tree}"], workspace):
        raise AssertionError("reviewed tree does not match the final committed tree")

    changed = changed_paths_in_head(workspace)
    scope = manifest_scope_paths(manifest)
    if not changed <= scope:
        raise AssertionError(f"commit changed paths outside manifest scope: changed={changed} scope={scope}")
    if any(path.startswith(".runtime/") for path in changed):
        raise AssertionError(f"runtime evidence leaked into the commit: {changed}")
    if git(["status", "--short"], workspace):
        raise AssertionError("one-command workspace is dirty after publish")
    card_text = (workspace / ONE_COMMAND_DONE_CARD).read_text(encoding="utf-8")
    for forbidden in (published, "push status"):
        if forbidden in card_text:
            raise AssertionError(f"final card contains mutable publish metadata: {forbidden}")
    if status.get("performance", {}).get("publish", {}).get("pushed_at") != "2026-08-01T00:00:00Z":
        raise AssertionError(f"runner status did not summarize publish timing: {status.get('performance')}")


def check_single_card_status_reader(tmp: Path) -> None:
    workspace = create_workspace(tmp, "single-card-status-workspace")
    runtime = tmp / "single-card-status-runtime"
    card_id = Path(CARD).name.removesuffix(".md")
    status_path = runtime / "status-blocked" / "status.json"
    no_go_path = runtime / "status-no-go" / "status.json"
    older_path = runtime / "status-old" / "status.json"
    corrupt_path = runtime / "status-corrupt" / "status.json"
    unsupported_path = runtime / "status-unsupported" / "status.json"

    status_payload = single_card_status_payload(
        workspace,
        "status-blocked",
        terminal_reason="fix_budget_exhausted",
    )
    write_json(status_path, status_payload)
    write_json(no_go_path, single_card_status_payload(workspace, "status-no-go", result="NO-GO"))
    write_json(older_path, single_card_status_payload(workspace, "status-old", result="DELIVERED"))
    corrupt_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt_path.write_text("{not json\n", encoding="utf-8")
    unsupported = single_card_status_payload(workspace, "status-unsupported")
    unsupported["schema"] = "changerail.unsupported.v1"
    write_json(unsupported_path, unsupported)

    manifest_path = workspace / ".runtime" / "changerail" / "delivery-manifests" / f"{card_id}.json"
    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / f"{card_id}.json"
    history_path = workspace / ".runtime" / "changerail" / "reviews" / f"{card_id}.history.json"
    evidence_path = workspace / ".runtime" / "changerail" / "evidence" / card_id / "index.json"
    write_json(manifest_path, single_card_manifest_payload(workspace))
    write_json(verdict_path, single_card_verdict_payload(workspace))
    write_json(history_path, single_card_history_payload(workspace))
    write_json(evidence_path, single_card_evidence_payload(workspace))

    before = {path: file_digest(path) for path in (status_path, manifest_path, verdict_path, history_path, evidence_path)}
    explicit = run([str(RUNNER), "status", str(status_path), "--workspace", str(workspace)])
    require_ok(explicit, "single-card status explicit path")
    for expected in (
        f"card: {CARD}",
        "run_id: status-blocked",
        "phase: terminal",
        "result: BLOCKED",
        "terminal_reason: fix_budget_exhausted",
        f"manifest: .runtime/changerail/delivery-manifests/{card_id}.json",
        f"review_verdict: .runtime/changerail/reviews/{card_id}.json",
        f"review_history: .runtime/changerail/reviews/{card_id}.history.json",
        f"evidence: .runtime/changerail/evidence/{card_id}/index.json",
        "pause_reason[1].summary: smoke pause summary",
        f"pause_reason[1].next_action: $changerail-deliver {CARD}",
    ):
        if expected not in explicit.stdout:
            raise AssertionError(f"single-card status output missing {expected!r}: {explicit.stdout}")
    after = {path: file_digest(path) for path in before}
    if before != after:
        raise AssertionError("single-card status reader modified source or linked runtime artifacts")

    by_run_id = run(
        [
            str(RUNNER),
            "status",
            "--run-id",
            "status-blocked",
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--json",
        ]
    )
    require_ok(by_run_id, "single-card status by run id")
    if json.loads(by_run_id.stdout) != status_payload:
        raise AssertionError(f"--json did not return the source delivery-run record: {by_run_id.stdout}")

    os.utime(older_path, (1_000, 1_000))
    os.utime(no_go_path, (2_000, 2_000))
    os.utime(status_path, (3_000, 3_000))
    os.utime(corrupt_path, (500, 500))
    os.utime(unsupported_path, (500, 500))
    latest = run([str(RUNNER), "status", "--workspace", str(workspace), "--runtime-root", str(runtime)])
    require_ok(latest, "single-card status latest")
    if "run_id: status-blocked" not in latest.stdout:
        raise AssertionError(f"latest status did not pick the newest status record: {latest.stdout}")

    no_go = run([str(RUNNER), "status", str(no_go_path), "--workspace", str(workspace)])
    require_ok(no_go, "single-card status no-go")
    if "result: NO-GO" not in no_go.stdout:
        raise AssertionError(f"NO-GO status diagnostic missing: {no_go.stdout}")

    conflict = run(
        [
            str(RUNNER),
            "status",
            str(status_path),
            "--run-id",
            "status-blocked",
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
        ]
    )
    if conflict.returncode == 0 or "conflicting status selectors" not in conflict.stderr:
        raise AssertionError(f"conflicting status selectors did not fail closed: {conflict.stdout} {conflict.stderr}")

    corrupt = run([str(RUNNER), "status", str(corrupt_path), "--workspace", str(workspace)])
    if corrupt.returncode == 0 or "delivery-run status is invalid" not in corrupt.stderr:
        raise AssertionError(f"corrupt explicit status did not fail closed: {corrupt.stdout} {corrupt.stderr}")

    unsupported_result = run([str(RUNNER), "status", str(unsupported_path), "--workspace", str(workspace)])
    if unsupported_result.returncode == 0 or "delivery-run status is invalid" not in unsupported_result.stderr:
        raise AssertionError(
            f"unsupported explicit status did not fail closed: {unsupported_result.stdout} {unsupported_result.stderr}"
        )

    invalid_manifest = single_card_manifest_payload(workspace)
    invalid_manifest["schema"] = "changerail.invalid-manifest.v1"
    write_json(manifest_path, invalid_manifest)
    linked = run([str(RUNNER), "status", str(status_path), "--workspace", str(workspace)])
    if linked.returncode == 0 or f"manifest: .runtime/changerail/delivery-manifests/{card_id}.json (invalid:" not in linked.stdout:
        raise AssertionError(f"invalid linked manifest was trusted: {linked.stdout} {linked.stderr}")


def check_one_command_delivery_success(tmp: Path) -> None:
    workspace = create_one_command_workspace(tmp, "one-command-success")
    launcher = tmp / "fake-one-command-success"
    runtime = tmp / "runtime"
    baseline = head_commit(workspace)
    if not baseline:
        raise AssertionError("one-command baseline commit missing")
    write_fake_one_command_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            ONE_COMMAND_CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "one-command-success",
            "--launcher",
            str(launcher),
        ],
        env={**runner_env(), "CHANGERAIL_ONE_COMMAND_MODE": "success"},
    )
    require_ok(result, "one-command delivery success")
    assert_one_command_success(workspace, runtime, "one-command-success", baseline)


def check_one_command_delivery_resume_after_preflight(tmp: Path) -> None:
    workspace = create_one_command_workspace(tmp, "one-command-resume")
    launcher = tmp / "fake-one-command-resume"
    runtime = tmp / "runtime"
    baseline = head_commit(workspace)
    if not baseline:
        raise AssertionError("one-command resume baseline commit missing")
    write_fake_one_command_launcher(launcher)
    prior = run(
        [
            str(RUNNER),
            "preflight",
            ONE_COMMAND_CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "one-command-resume-prior",
            "--launcher",
            str(launcher),
            "--json",
            "--write-status",
        ],
        env=fake_git_env(tmp, "dns"),
    )
    if prior.returncode == 0:
        raise AssertionError("one-command prior preflight unexpectedly passed")
    prior_check = publish_target_check(json.loads(prior.stdout))
    if prior_check.get("failure_class") != "dns":
        raise AssertionError(f"prior preflight did not record a transient dns failure: {prior_check}")

    resumed = run(
        [
            str(RUNNER),
            "resume",
            "--status-path",
            str(runtime / "one-command-resume-prior" / "status.json"),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "one-command-resume",
            "--launcher",
            str(launcher),
        ],
        env={**fake_git_env(tmp, "success"), "CHANGERAIL_ONE_COMMAND_MODE": "success"},
    )
    require_ok(resumed, "one-command resume")
    status = load_status(runtime, "one-command-resume")
    checks = {check["name"]: check for check in status["preflight"]["checks"]}
    if checks["resume prior status"]["status"] != "pass":
        raise AssertionError(f"resume did not accept prior remote failure: {checks['resume prior status']}")
    if checks["publish target"]["status"] != "pass":
        raise AssertionError(f"resume did not repeat successful publish-target preflight: {checks['publish target']}")
    assert_one_command_success(workspace, runtime, "one-command-resume", baseline)


def write_stale_go_verdict(workspace: Path, card: str) -> Path:
    card_name = Path(card).name.removesuffix(".md")
    data = review_fingerprint(workspace)
    verdict = {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": "2026-08-01T00:00:00Z",
        "card": {"id": card_name, "path": card},
        "workspace": {
            "root": data["workspace"],
            "head_commit": "0" * 40,
            "tree_sha": data["tree_sha"],
            "diff_fingerprint": data["diff_fingerprint"],
        },
        "reviewer": {
            "kind": "codex-exec",
            "independence": {
                "fresh_context": True,
                "did_not_plan_or_implement": True,
                "basis": "fresh smoke reviewer context with intentionally stale fingerprint",
            },
        },
        "result": "go",
        "review_cycle": 1,
        "acceptance": [
            {
                "criterion": "published payload",
                "verdict": "pass",
                "evidence": "stale smoke fixture",
            }
        ],
        "findings": [],
        "evidence_audit": {"claims_checked": 1, "claims_unbacked": 0},
    }
    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / f"{card_name}.json"
    verdict_path.parent.mkdir(parents=True, exist_ok=True)
    verdict_path.write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require_ok(run([sys.executable, str(VERDICT_HELPER), "validate", str(verdict_path), "--json"]), "stale schema validate")
    return verdict_path


RETAINED_CARD = "openspec/board/3.inprogress/retained-card.md"
RETAINED_CHANGE = "retained-resume-smoke"
RETAINED_INVESTIGATION = "openspec/board/4.done/retained-investigation.md"
RETAINED_AUTHORIZATION = "openspec/board/4.done/retained-authorization.md"
RETAINED_PAYLOAD = "bin/retained-runner"


def retained_card_text() -> str:
    return "\n".join(
        [
            "# Retained resume smoke",
            "",
            "## Status",
            "3.inprogress",
            "",
            "## Review",
            "- Risk tier: `critical`",
            "- Milestone audit: `no`",
            "- New authority or wire protocol: `yes`",
            "- Credential or mutation authority: `no`",
            "- Repeated defect class: `no`",
            "- Live admission: `no`",
            "- Final certification: `no`",
            '- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/retained-authorization.md","authorization_id":"retained-authorization"}`',
            "",
            "## Depends On",
            "- `retained-investigation`",
            "",
            "## Change Set",
            f"- `{RETAINED_CHANGE}`",
            "",
            f"## Change 1: `{RETAINED_CHANGE}`",
            "",
            "### Depends On",
            "- none",
            "",
        ]
    )


def retained_investigation_text() -> str:
    return "\n".join(
        [
            "# Retained investigation",
            "",
            "## Status",
            "4.done",
            "",
            "## Blocks",
            "- `retained-card`",
            "",
        ]
    )


def retained_authorization_text(*, successor_id: str = "retained-card", ceiling: int = 500) -> str:
    authorization = {
        "investigation_card": RETAINED_INVESTIGATION,
        "investigation_id": "retained-investigation",
        "successor_card": RETAINED_CARD,
        "successor_id": successor_id,
        "production_loc_ceiling": ceiling,
        "allow_new_authority_or_wire_protocol": True,
    }
    return "\n".join(
        [
            "# Retained authorization",
            "",
            "## Status",
            "4.done",
            "",
            "## Depends On",
            "- `retained-investigation`",
            "",
            "## Authorization",
            f"- Investigation authorization: `{json.dumps(authorization, separators=(',', ':'))}`",
            "",
        ]
    )


def retained_manifest(workspace: Path) -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": "2026-08-01T00:00:00Z",
        "workspace": {"root": str(workspace), "repository": workspace.name},
        "card": {"id": "retained-card", "path": RETAINED_CARD, "status": "3.inprogress"},
        "changes": [
            {
                "slug": RETAINED_CHANGE,
                "state": "archived",
                "order": 1,
                "archive_path": f"openspec/changes/archive/2026-08-01-{RETAINED_CHANGE}",
            }
        ],
        "committable_paths": [
            {
                "path": RETAINED_PAYLOAD,
                "kind": "helper",
                "phase": "do",
                "operation": "add",
                "target_path": RETAINED_PAYLOAD,
            }
        ],
        "excluded_runtime_paths": [
            {
                "path": ".runtime/changerail/delivery-manifests/retained-card.json",
                "kind": "manifest",
                "phase": "do",
                "reason": "ignored runtime manifest",
            }
        ],
        "preexisting_dirty": [],
        "verification_summary": {"result": "passed", "summary": "retained resume smoke fixture"},
    }


def create_retained_resume_workspace(
    tmp: Path,
    name: str,
    *,
    payload_lines: int = 3,
    successor_id: str = "retained-card",
    auth_dirty_before_fingerprint: bool = False,
    ceiling: int = 500,
) -> tuple[Path, Path, Path]:
    workspace = create_workspace(tmp, name)
    (workspace / RETAINED_CARD).parent.mkdir(parents=True, exist_ok=True)
    (workspace / RETAINED_CARD).write_text(retained_card_text(), encoding="utf-8")
    (workspace / RETAINED_INVESTIGATION).parent.mkdir(parents=True, exist_ok=True)
    (workspace / RETAINED_INVESTIGATION).write_text(retained_investigation_text(), encoding="utf-8")
    (workspace / RETAINED_AUTHORIZATION).write_text(
        retained_authorization_text(successor_id=successor_id, ceiling=ceiling),
        encoding="utf-8",
    )
    archive = workspace / "openspec" / "changes" / "archive" / f"2026-08-01-{RETAINED_CHANGE}"
    archive.mkdir(parents=True, exist_ok=True)
    (archive / "proposal.md").write_text("## Why\n\nRetained resume smoke.\n", encoding="utf-8")
    git(["add", "openspec"], workspace)
    git(
        ["-c", "user.name=ChangeRail Smoke", "-c", "user.email=changerail-smoke@example.invalid", "commit", "-m", "retained auth fixture"],
        workspace,
    )
    if auth_dirty_before_fingerprint:
        with (workspace / RETAINED_AUTHORIZATION).open("a", encoding="utf-8") as handle:
            handle.write("\n<!-- stale authorization smoke -->\n")
    payload = workspace / RETAINED_PAYLOAD
    payload.parent.mkdir(parents=True, exist_ok=True)
    payload.write_text("\n".join(f"echo retained-{index}" for index in range(payload_lines)) + "\n", encoding="utf-8")
    payload.chmod(0o755)
    manifest_path = workspace / ".runtime" / "changerail" / "delivery-manifests" / "retained-card.json"
    write_json(manifest_path, retained_manifest(workspace))
    runtime = workspace / ".runtime" / "changerail" / "delivery-runs"
    prior_path = runtime / "retained-prior" / "status.json"
    fingerprint_data = review_fingerprint(workspace)
    prior = {
        "schema": "changerail.delivery-run.v1",
        "run_id": "retained-prior",
        "updated_at": "2026-08-01T00:00:00Z",
        "workspace": {"root": str(workspace), "repository": workspace.name, "head_commit": fingerprint_data["head_commit"]},
        "card": {"id": "retained-card", "path": RETAINED_CARD},
        "phase": "terminal",
        "result": "BLOCKED",
        "terminal_outcome": "BLOCKED",
        "terminal_reason": "investigation_required",
        "timestamps": {"started_at": "2026-08-01T00:00:00Z", "ended_at": "2026-08-01T00:00:01Z"},
        "command": {"argv": ["fake"], "launcher": "fake", "stdin": "closed", "json": True},
        "usage": {"available": False, "reason": "smoke retained prior"},
        "retained_payload": {
            "schema": "changerail.retained-payload-identity.v1",
            "source_run_id": "retained-prior",
            "source_status_path": ".runtime/changerail/delivery-runs/retained-prior/status.json",
            "captured_at": "2026-08-01T00:00:00Z",
            "card": {"id": "retained-card", "path": RETAINED_CARD},
            "workspace": {"root": str(workspace)},
            "head_commit": fingerprint_data["head_commit"],
            "tree_sha": fingerprint_data["tree_sha"],
            "diff_fingerprint": fingerprint_data["diff_fingerprint"],
            "review_target": {"kind": "working-tree"},
        },
    }
    write_json(prior_path, prior)
    return workspace, runtime, prior_path


def run_retained_resume(
    workspace: Path,
    runtime: Path,
    prior_path: Path,
    launcher: Path,
    *,
    run_id: str,
    card: str = RETAINED_CARD,
) -> subprocess.CompletedProcess[str]:
    return run(
        [
            str(RUNNER),
            "resume",
            card,
            "--status-path",
            str(prior_path),
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            run_id,
            "--launcher",
            str(launcher),
        ],
        env={**runner_env(), "CHANGERAIL_FAKE_MODE": "success"},
    )


def check_retained_payload_status_schema_and_single_card_resume(tmp: Path) -> None:
    workspace, runtime, prior_path = create_retained_resume_workspace(tmp, "retained-resume-ok")
    launcher = tmp / "fake-retained-resume"
    write_fake_launcher(launcher)
    result = run_retained_resume(workspace, runtime, prior_path, launcher, run_id="retained-resume-ok")
    require_ok(result, "retained single-card resume")
    status = load_status(runtime, "retained-resume-ok")
    checks = {check["name"]: check for check in status["preflight"]["checks"]}
    if checks["retained payload fingerprint"]["status"] != "pass":
        raise AssertionError(f"retained fingerprint check did not pass: {status}")
    if checks["published investigation authorization"]["status"] != "pass":
        raise AssertionError(f"retained authorization check did not pass: {status}")

    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    invalid = json.loads(json.dumps(prior))
    invalid["retained_payload"]["raw_stdout"] = "RAW_CHILD_STDOUT_SHOULD_NOT_BE_SCHEMA_VALID"
    invalid_path = runtime / "retained-invalid" / "status.json"
    write_json(invalid_path, invalid)
    invalid_result = run_retained_resume(workspace, runtime, invalid_path, launcher, run_id="retained-invalid")
    if invalid_result.returncode == 0:
        raise AssertionError("retained status with raw stdout unexpectedly resumed")
    invalid_status = load_status(runtime, "retained-invalid")
    if invalid_status.get("terminal_reason") != "prior_status_invalid":
        raise AssertionError(f"invalid retained schema did not fail closed: {invalid_status}")


def check_retained_payload_resume_fail_closed(tmp: Path) -> None:
    launcher = tmp / "fake-retained-resume-fail"
    write_fake_launcher(launcher)

    wrong_workspace, runtime, prior_path = create_retained_resume_workspace(tmp, "retained-wrong-workspace-source")
    other_workspace = create_workspace(tmp, "retained-wrong-workspace-other")
    wrong_workspace_result = run_retained_resume(other_workspace, runtime, prior_path, launcher, run_id="retained-wrong-workspace")
    if wrong_workspace_result.returncode == 0:
        raise AssertionError("wrong workspace retained resume unexpectedly passed")
    if load_status(runtime, "retained-wrong-workspace").get("terminal_reason") != "workspace_mismatch":
        raise AssertionError("wrong workspace did not use stable reason")

    wrong_card_workspace, wrong_card_runtime, wrong_card_prior = create_retained_resume_workspace(tmp, "retained-wrong-card")
    wrong_card_result = run_retained_resume(
        wrong_card_workspace,
        wrong_card_runtime,
        wrong_card_prior,
        launcher,
        run_id="retained-wrong-card",
        card="openspec/board/3.inprogress/another-card.md",
    )
    if wrong_card_result.returncode == 0:
        raise AssertionError("wrong card retained resume unexpectedly passed")
    if load_status(wrong_card_runtime, "retained-wrong-card").get("terminal_reason") != "card_mismatch":
        raise AssertionError("wrong card did not use stable reason")

    drift_workspace, drift_runtime, drift_prior = create_retained_resume_workspace(tmp, "retained-drift")
    with (drift_workspace / RETAINED_PAYLOAD).open("a", encoding="utf-8") as handle:
        handle.write("echo drift\n")
    drift_result = run_retained_resume(drift_workspace, drift_runtime, drift_prior, launcher, run_id="retained-drift")
    if drift_result.returncode == 0:
        raise AssertionError("fingerprint drift retained resume unexpectedly passed")
    if load_status(drift_runtime, "retained-drift").get("terminal_reason") != "payload_drift":
        raise AssertionError("fingerprint drift did not use stable reason")

    stale_workspace, stale_runtime, stale_prior = create_retained_resume_workspace(
        tmp,
        "retained-stale-auth",
        auth_dirty_before_fingerprint=True,
    )
    stale_result = run_retained_resume(stale_workspace, stale_runtime, stale_prior, launcher, run_id="retained-stale-auth")
    if stale_result.returncode == 0:
        raise AssertionError("stale authorization retained resume unexpectedly passed")
    if load_status(stale_runtime, "retained-stale-auth").get("terminal_reason") != "authorization_stale":
        raise AssertionError("stale authorization did not use stable reason")

    relation_workspace, relation_runtime, relation_prior = create_retained_resume_workspace(
        tmp,
        "retained-relation-mismatch",
        successor_id="wrong-card",
    )
    relation_result = run_retained_resume(relation_workspace, relation_runtime, relation_prior, launcher, run_id="retained-relation")
    if relation_result.returncode == 0:
        raise AssertionError("relation mismatch retained resume unexpectedly passed")
    if load_status(relation_runtime, "retained-relation").get("terminal_reason") != "relation_mismatch":
        raise AssertionError("relation mismatch did not use stable reason")

    ceiling_workspace, ceiling_runtime, ceiling_prior = create_retained_resume_workspace(
        tmp,
        "retained-over-ceiling",
        payload_lines=501,
    )
    ceiling_result = run_retained_resume(ceiling_workspace, ceiling_runtime, ceiling_prior, launcher, run_id="retained-over-ceiling")
    if ceiling_result.returncode == 0:
        raise AssertionError("over-ceiling retained resume unexpectedly passed")
    if load_status(ceiling_runtime, "retained-over-ceiling").get("terminal_reason") != "authorization_ceiling_violation":
        raise AssertionError("over-ceiling authorization did not use stable reason")


def check_one_command_delivery_stale_verdict_blocks(tmp: Path) -> None:
    workspace = create_one_command_workspace(tmp, "one-command-stale-verdict")
    launcher = tmp / "fake-one-command-stale-verdict"
    runtime = tmp / "runtime"
    baseline = head_commit(workspace)
    if not baseline:
        raise AssertionError("one-command stale baseline commit missing")
    write_fake_one_command_launcher(launcher)
    write_stale_go_verdict(workspace, ONE_COMMAND_CARD)
    result = run(
        [
            str(RUNNER),
            "run",
            ONE_COMMAND_CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "one-command-stale-verdict",
            "--launcher",
            str(launcher),
        ],
        env={**runner_env(), "CHANGERAIL_ONE_COMMAND_MODE": "noop"},
    )
    if result.returncode == 0:
        raise AssertionError("stale verdict scenario unexpectedly delivered")
    status = load_status(runtime, "one-command-stale-verdict")
    if status.get("result") != "BLOCKED" or status.get("terminal_reason") != "review_verdict_invalid":
        raise AssertionError(f"stale verdict was not fail-closed: {status}")
    if remote_head(workspace) != baseline or head_commit(workspace) != baseline:
        raise AssertionError("stale verdict scenario unexpectedly committed or pushed")
    if not (workspace / ONE_COMMAND_CARD).is_file() or (workspace / ONE_COMMAND_DONE_CARD).exists():
        raise AssertionError("stale verdict scenario moved the card despite blocking")


def check_one_command_delivery_review_budget_no_go(tmp: Path) -> None:
    workspace = create_one_command_workspace(tmp, "one-command-review-budget")
    launcher = tmp / "fake-one-command-review-budget"
    runtime = tmp / "runtime"
    baseline = head_commit(workspace)
    if not baseline:
        raise AssertionError("one-command review budget baseline commit missing")
    write_fake_one_command_launcher(launcher)
    result = run(
        [
            str(RUNNER),
            "run",
            ONE_COMMAND_CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "one-command-review-budget",
            "--launcher",
            str(launcher),
        ],
        env={**runner_env(), "CHANGERAIL_ONE_COMMAND_MODE": "review-budget-exhausted"},
    )
    if result.returncode == 0:
        raise AssertionError("exhausted review budget scenario unexpectedly delivered")
    status = load_status(runtime, "one-command-review-budget")
    if status.get("result") != "NO-GO" or status.get("terminal_outcome") != "NO-GO":
        raise AssertionError(f"exhausted review budget did not report NO-GO: {status}")
    if remote_head(workspace) != baseline or head_commit(workspace) != baseline:
        raise AssertionError("exhausted review budget scenario unexpectedly committed or pushed")
    if not (workspace / ONE_COMMAND_CARD).is_file() or (workspace / ONE_COMMAND_DONE_CARD).exists():
        raise AssertionError("exhausted review budget scenario moved the card despite NO-GO")
    history_path = workspace / ".runtime" / "changerail" / "reviews" / "one-command-delivery-smoke.history.json"
    history = json.loads(history_path.read_text(encoding="utf-8"))
    if history.get("rescue_budget") != {"limit": 2, "used": 2, "remaining": 0, "exhausted": True}:
        raise AssertionError(f"review budget exhaustion was not recorded: {history}")
    verdict_path = workspace / ".runtime" / "changerail" / "reviews" / "one-command-delivery-smoke.json"
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
    require_ok(validate, "exhausted review budget verdict validate")


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
    run_dir = runtime / "success"
    require_private_mode(run_dir, 0o700)
    require_private_mode(run_dir / "status.json", 0o600)
    require_private_mode(run_dir / "stdout.jsonl", 0o600)
    require_private_mode(run_dir / "stderr.log", 0o600)
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
    if first.get("CHANGERAIL_ACTIVE_RUN_ID") != "success":
        raise AssertionError(f"active runner id was not passed to the child: {first}")
    if first.get("CHANGERAIL_ACTIVE_RUN_DIR") != str(runtime / "success"):
        raise AssertionError(f"active runner directory was not passed to the child: {first}")
    policy = first.get("CHANGERAIL_DISCOVERY_POLICY")
    if not isinstance(policy, str) or "scoped paths" not in policy or "exit 130" not in policy:
        raise AssertionError(f"child discovery policy was not passed to the child: {first}")
    threshold = first.get("CHANGERAIL_COMMAND_OUTPUT_THRESHOLD_BYTES")
    if threshold != "65536":
        raise AssertionError(f"child output threshold was not passed to the child: {first}")
    prompt = " ".join(str(part) for part in argv)
    if "ChangeRail child discovery policy:" not in prompt or "bounded excerpts" not in prompt:
        raise AssertionError(f"child prompt did not include discovery policy: {argv}")
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
    first_output = commands[0].get("output")
    if not isinstance(first_output, dict) or first_output.get("classification") != "success_bounded":
        raise AssertionError(f"bounded command output metadata missing: {commands}")
    if first_output.get("stdout_bytes") != 10 or first_output.get("threshold_exceeded") is not False:
        raise AssertionError(f"bounded byte accounting missing: {first_output}")
    command_output = performance.get("command_output")
    if not isinstance(command_output, dict):
        raise AssertionError(f"command output summary missing: {performance}")
    if command_output.get("oversized_command_count") != 0 or command_output.get("largest_command_bytes") != 10:
        raise AssertionError(f"command output aggregate was not captured: {command_output}")
    if command_output.get("threshold_bytes") != 65536:
        raise AssertionError(f"default command output threshold missing: {command_output}")
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


def check_oversized_output_summary_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "oversized-output-workspace")
    launcher = tmp / "fake-codex-oversized-output"
    runtime = workspace / ".runtime" / "changerail" / "delivery-runs"
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
            "oversized-output",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("oversized-output"),
    )
    require_ok(result, "runner oversized output")
    status = load_status(runtime, "oversized-output")
    performance = status.get("performance")
    if not isinstance(performance, dict):
        raise AssertionError(f"performance summary missing from oversized output status: {status}")
    command_output = performance.get("command_output")
    if not isinstance(command_output, dict):
        raise AssertionError(f"oversized command output summary missing: {performance}")
    if command_output.get("oversized_command_count") != 1:
        raise AssertionError(f"oversized command count missing: {command_output}")
    if command_output.get("largest_command_bytes", 0) <= command_output.get("threshold_bytes", 0):
        raise AssertionError(f"largest command did not exceed threshold: {command_output}")
    top = command_output.get("top_oversized_commands")
    if not isinstance(top, list) or len(top) != 1:
        raise AssertionError(f"top oversized command missing: {command_output}")
    top_command = top[0]
    if top_command.get("classification") != "runner_truncated" or top_command.get("truncated") is not True:
        raise AssertionError(f"truncation classification missing: {top_command}")
    label = top_command.get("command")
    if not isinstance(label, str):
        raise AssertionError(f"sanitized command label missing: {top_command}")
    for forbidden in ("user:pass", "oversized-value", str(runtime / "oversized-output")):
        if forbidden in label:
            raise AssertionError(f"oversized command label leaked sensitive detail: {label}")
    status_text = json.dumps(status, ensure_ascii=False, sort_keys=True)
    raw_fragment = "OVERSIZED_RAW_PAYLOAD_SHOULD_NOT_APPEAR"
    if raw_fragment in status_text:
        raise AssertionError("raw oversized payload was copied into status.json")
    status_path = runtime / "oversized-output" / "status.json"
    if status_path.stat().st_size >= 20000:
        raise AssertionError(f"status.json was not bounded: {status_path.stat().st_size} bytes")
    raw_stdout = Path(status["logs"]["stdout"])
    raw_text = raw_stdout.read_text(encoding="utf-8")
    if raw_fragment not in raw_text:
        raise AssertionError("raw oversized output was not retained in ignored stdout evidence")
    check_ignore = subprocess.run(
        ["git", "-C", str(workspace), "check-ignore", ".runtime/changerail/delivery-runs/oversized-output/stdout.jsonl"],
        capture_output=True,
        text=True,
        check=False,
    )
    if check_ignore.returncode != 0:
        raise AssertionError(f"raw stdout evidence is not ignored runtime state: {check_ignore.stderr or check_ignore.stdout}")
    if "oversized_commands: count=1" not in result.stdout or "remediation: use scoped paths" not in result.stdout:
        raise AssertionError(f"operator oversized output summary missing: {result.stdout}")
    for forbidden in ("OVERSIZED_RAW_PAYLOAD_SHOULD_NOT_APPEAR", "user:pass", "oversized-value"):
        if forbidden in result.stdout:
            raise AssertionError(f"operator summary leaked raw or sensitive content: {result.stdout}")


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
    commit_paths(workspace, "review no-go fallback card", card)
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
    commit_paths(workspace, "supervisor cards", first_card, second_card)
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


def check_malformed_terminal_reason_run(tmp: Path) -> None:
    workspace = create_workspace(tmp, "malformed-terminal-reason-workspace")
    launcher = tmp / "fake-codex-malformed-terminal-reason"
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
            "malformed-terminal-reason",
            "--launcher",
            str(launcher),
        ],
        env=runner_env("malformed-terminal-reason"),
    )
    if result.returncode == 0:
        raise AssertionError("malformed terminal reason run unexpectedly returned success")
    status = load_status(runtime, "malformed-terminal-reason")
    if status.get("result") != "BLOCKED" or status.get("terminal_reason") != "malformed_terminal_reason":
        raise AssertionError(f"malformed terminal reason was silently discarded: {status}")


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
        if checks["codex binary"]["status"] != "skip" or "custom launcher selected" not in checks["codex binary"]["message"]:
            raise AssertionError(f"custom launcher should skip PATH codex probe: {checks['codex binary']}")
        if checks["publish target"]["status"] != "pass" or "reachable=true" not in checks["publish target"]["message"]:
            raise AssertionError(f"publish target did not pass: {checks['publish target']}")
        if not (runtime / "preflight" / "status.json").is_file():
            raise AssertionError("preflight status was not written")
    finally:
        server.shutdown()


def check_preflight_rejects_insufficient_automation_authority(tmp: Path) -> None:
    workspace = create_workspace(tmp, "preflight-insufficient-authority")
    (workspace / ".codex" / "config.toml").write_text(
        'approval_policy = "on-request"\n'
        'sandbox_mode = "workspace-write"\n',
        encoding="utf-8",
    )
    launcher = tmp / "fake-codex-insufficient-authority"
    runtime = tmp / "runtime-insufficient-authority"
    write_fake_launcher(launcher)
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
            "insufficient-authority",
            "--launcher",
            str(launcher),
            "--json",
        ]
    )
    if result.returncode == 0:
        raise AssertionError("preflight accepted insufficient Codex automation authority")
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["preflight"]["checks"]}
    authority = checks.get("Codex automation authority")
    if not authority or authority["status"] != "fail":
        raise AssertionError(f"preflight did not report the authority failure: {checks}")
    if "never" not in authority["message"] or "danger-full-access" not in authority["message"]:
        raise AssertionError(f"authority remediation is incomplete: {authority}")


def check_custom_launcher_without_path_codex(tmp: Path) -> None:
    workspace = create_workspace(tmp, "custom-launcher-no-path-codex")
    launcher = tmp / "fake-codex-without-path-codex"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
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
            "custom-launcher-no-path-codex",
            "--launcher",
            str(launcher),
            "--json",
        ],
        env=no_codex_path_env(tmp),
    )
    require_ok(result, "custom launcher without PATH codex preflight")
    checks = {check["name"]: check for check in json.loads(result.stdout)["preflight"]["checks"]}
    if checks["codex binary"]["status"] != "skip":
        raise AssertionError(f"custom launcher should not require PATH codex: {checks['codex binary']}")


def check_default_launcher_requires_path_codex(tmp: Path) -> None:
    workspace = create_workspace(tmp, "default-launcher-no-path-codex")
    runtime = tmp / "runtime"
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
            "default-launcher-no-path-codex",
            "--json",
        ],
        env=no_codex_path_env(tmp),
    )
    if result.returncode == 0:
        raise AssertionError("default launcher without PATH codex unexpectedly passed")
    checks = {check["name"]: check for check in json.loads(result.stdout)["preflight"]["checks"]}
    if checks["codex binary"]["status"] != "fail" or checks["codex binary"]["message"] != "not found":
        raise AssertionError(f"default launcher should require PATH codex: {checks['codex binary']}")


def set_configured_upstream(workspace: Path, remote_url: str) -> None:
    branch = git(["branch", "--show-current"], workspace)
    git(["remote", "add", "origin", remote_url], workspace)
    git(["config", f"branch.{branch}.remote", "origin"], workspace)
    git(["config", f"branch.{branch}.merge", f"refs/heads/{branch}"], workspace)


def check_publish_target_preflight(tmp: Path) -> None:
    runtime = tmp / "runtime"

    missing = create_workspace(tmp, "missing-publish-target", publish_ready=False)
    launcher = tmp / "fake-codex-missing-publish"
    write_fake_launcher(launcher)
    missing_result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(missing),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "missing-publish-target",
            "--launcher",
            str(launcher),
            "--json",
            "--write-status",
        ]
    )
    if missing_result.returncode == 0:
        raise AssertionError("missing publish target preflight unexpectedly passed")
    checks = {check["name"]: check for check in json.loads(missing_result.stdout)["preflight"]["checks"]}
    if checks["publish target"]["status"] != "fail" or "upstream=missing" not in checks["publish target"]["message"]:
        raise AssertionError(f"missing upstream was not reported: {checks['publish target']}")

    no_push = create_workspace(tmp, "explicit-no-push", publish_ready=False)
    no_push_launcher = tmp / "fake-codex-no-push"
    write_fake_launcher(no_push_launcher)
    no_push_result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(no_push),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "explicit-no-push",
            "--launcher",
            str(no_push_launcher),
            "--deliver-arg=--no-push",
            "--json",
            "--write-status",
        ]
    )
    require_ok(no_push_result, "explicit no-push preflight")
    checks = {check["name"]: check for check in json.loads(no_push_result.stdout)["preflight"]["checks"]}
    if checks["publish target"]["status"] != "pass" or "mode=no-push" not in checks["publish target"]["message"]:
        raise AssertionError(f"explicit no-push was not recorded: {checks['publish target']}")

    unreachable = create_workspace(tmp, "unreachable-publish-target", publish_ready=False)
    set_configured_upstream(unreachable, str(tmp / "missing-remote.git"))
    unreachable_launcher = tmp / "fake-codex-unreachable-publish"
    write_fake_launcher(unreachable_launcher)
    unreachable_result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(unreachable),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "unreachable-publish-target",
            "--launcher",
            str(unreachable_launcher),
            "--json",
            "--write-status",
        ]
    )
    if unreachable_result.returncode == 0:
        raise AssertionError("unreachable publish target preflight unexpectedly passed")
    checks = {check["name"]: check for check in json.loads(unreachable_result.stdout)["preflight"]["checks"]}
    message = checks["publish target"]["message"]
    if checks["publish target"]["status"] != "fail" or "reachable=false" not in message:
        raise AssertionError(f"unreachable remote was not reported: {checks['publish target']}")

    credential = create_workspace(tmp, "credential-publish-target", publish_ready=False)
    set_configured_upstream(credential, "https://user:token@example.invalid/repo.git")
    credential_launcher = tmp / "fake-codex-credential-publish"
    write_fake_launcher(credential_launcher)
    credential_result = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(credential),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "credential-publish-target",
            "--launcher",
            str(credential_launcher),
            "--json",
            "--write-status",
        ]
    )
    if credential_result.returncode == 0:
        raise AssertionError("credential-bearing publish target preflight unexpectedly passed")
    checks = {check["name"]: check for check in json.loads(credential_result.stdout)["preflight"]["checks"]}
    message = checks["publish target"]["message"]
    if checks["publish target"]["status"] != "fail" or "credential_in_url=rejected" not in message:
        raise AssertionError(f"credential URL was not rejected: {checks['publish target']}")
    for forbidden in ("user:token", "example.invalid/repo.git"):
        if forbidden in message:
            raise AssertionError(f"credential diagnostic leaked raw URL data: {message}")


def remote_preflight_workspace(tmp: Path, name: str) -> tuple[Path, Path, Path]:
    workspace = create_workspace(tmp, name, publish_ready=False)
    set_configured_upstream(workspace, "example.invalid:org/repo.git")
    launcher = tmp / f"fake-codex-{name}"
    runtime = tmp / "runtime"
    write_fake_launcher(launcher)
    return workspace, launcher, runtime


def publish_target_check(payload: dict[str, Any]) -> dict[str, Any]:
    checks = {check["name"]: check for check in payload["preflight"]["checks"]}
    return checks["publish target"]


def check_remote_preflight_failure_classes(tmp: Path) -> None:
    cases = [
        ("ssh_config", False, 1, None),
        ("dns", True, 2, None),
        ("auth", False, 1, None),
        ("missing_branch", False, 1, None),
        ("timeout", True, 2, 1.0),
        ("unknown_remote_failure", True, 2, None),
    ]
    for mode, retryable, attempts, timeout in cases:
        workspace, launcher, runtime = remote_preflight_workspace(tmp, f"remote-{mode}")
        log = tmp / f"remote-{mode}-git-calls.log"
        log.write_text("", encoding="utf-8")
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
                f"remote-{mode}",
                "--launcher",
                str(launcher),
                "--json",
                "--write-status",
            ],
            env=fake_git_env(tmp, mode, timeout=timeout, log=log),
        )
        if result.returncode == 0:
            raise AssertionError(f"{mode} remote preflight unexpectedly passed")
        check = publish_target_check(json.loads(result.stdout))
        if check.get("failure_class") != mode:
            raise AssertionError(f"{mode} was not classified correctly: {check}")
        if check.get("retryable") is not retryable:
            raise AssertionError(f"{mode} retryable mismatch: {check}")
        if check.get("attempts") != attempts:
            raise AssertionError(f"{mode} attempts mismatch: {check}")
        evidence = check.get("evidence", {})
        if evidence.get("command") != "git ls-remote --exit-code <remote> refs/heads/<branch>":
            raise AssertionError(f"{mode} evidence command was not sanitized: {check}")
        detail = json.dumps(check, ensure_ascii=False)
        for forbidden in ("ssh://git@example.invalid/org/repo.git", "git@example.invalid:org/repo.git"):
            if forbidden in detail:
                raise AssertionError(f"{mode} diagnostic leaked raw remote URL: {check}")
        observed_attempts = len(log.read_text(encoding="utf-8").splitlines())
        if observed_attempts != attempts:
            raise AssertionError(f"{mode} git ls-remote attempts mismatch: {observed_attempts} != {attempts}")


def check_remote_preflight_resume_success(tmp: Path) -> None:
    workspace, launcher, runtime = remote_preflight_workspace(tmp, "remote-resume")
    prior = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(workspace),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "remote-resume-prior",
            "--launcher",
            str(launcher),
            "--json",
            "--write-status",
        ],
        env=fake_git_env(tmp, "dns"),
    )
    if prior.returncode == 0:
        raise AssertionError("prior remote failure preflight unexpectedly passed")
    prior_check = publish_target_check(json.loads(prior.stdout))
    if prior_check.get("failure_class") != "dns":
        raise AssertionError(f"prior remote preflight did not record dns: {prior_check}")

    resume = run(
        [
            str(RUNNER),
            "resume",
            "--status-path",
            str(runtime / "remote-resume-prior" / "status.json"),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "remote-resume",
            "--launcher",
            str(launcher),
        ],
        env=fake_git_env(tmp, "success"),
    )
    require_ok(resume, "remote preflight resume")
    status = load_status(runtime, "remote-resume")
    checks = {check["name"]: check for check in status["preflight"]["checks"]}
    if checks["resume prior status"]["status"] != "pass":
        raise AssertionError(f"resume did not accept prior status: {checks['resume prior status']}")
    if checks["publish target"]["status"] != "pass" or checks["publish target"].get("attempts") != 1:
        raise AssertionError(f"resume did not repeat fresh publish target proof: {checks['publish target']}")
    for required in ("launcher exists", "CODEX auth", "CODEX_HOME symlinks", "codex binary"):
        if required not in checks:
            raise AssertionError(f"resume did not repeat full preflight; missing {required}: {checks}")
    if status["result"] != "DELIVERED":
        raise AssertionError(f"resume did not continue to delivery after fresh proof: {status}")


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


def check_explicit_codex_home_preflight(tmp: Path) -> None:
    workspace = create_workspace(tmp, "explicit-codex-home-workspace")
    launcher = tmp / "fake-codex-explicit-home"
    runtime = tmp / "runtime"
    external_home = tmp / "external-codex-home"
    sentinel = "fake-secret-sentinel"
    external_home.mkdir()
    (external_home / "auth.json").write_text(sentinel + "\n", encoding="utf-8")
    (external_home / "config.toml").write_text(
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )
    (workspace / ".codex" / "auth.json").unlink()
    write_fake_launcher(launcher)
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
            "explicit-codex-home",
            "--launcher",
            str(launcher),
            "--json",
            "--write-status",
        ],
        env={**runner_env(), "CODEX_HOME": str(external_home)},
    )
    require_ok(result, "explicit CODEX_HOME preflight")
    if sentinel in result.stdout:
        raise AssertionError("explicit CODEX_HOME preflight printed credential contents")
    payload = json.loads(result.stdout)
    checks = {check["name"]: check for check in payload["preflight"]["checks"]}
    if checks["CODEX_HOME"]["status"] != "pass":
        raise AssertionError(f"explicit CODEX_HOME did not pass: {checks['CODEX_HOME']}")
    if checks["CODEX auth"]["status"] != "pass":
        raise AssertionError(f"explicit CODEX_HOME auth marker did not pass: {checks['CODEX auth']}")


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
    checks = {check["name"]: check for check in status["preflight"]["checks"]}
    auth_message = checks["CODEX auth"]["message"]
    if "docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner" not in auth_message:
        raise AssertionError(f"missing-auth remediation was not reported: {auth_message}")
    for forbidden in ("fake-secret", "raw-token"):
        if forbidden in auth_message:
            raise AssertionError(f"missing-auth diagnostic leaked secret-like value: {auth_message}")
    lines = result.stdout.splitlines()
    if lines[:2] != [
        "terminal_outcome: BLOCKED",
        f"status: {runtime / 'run-preflight-failure' / 'status.json'}",
    ]:
        raise AssertionError(f"run preflight failure did not print BLOCKED before status: {result.stdout}")


def check_single_card_dirty_workspace_blocks_ordinary_launches(tmp: Path) -> None:
    workspace = create_workspace(tmp, "dirty-ordinary-run")
    launcher = tmp / "fake-codex-dirty-ordinary-run"
    runtime = tmp / "runtime"
    call_log = tmp / "dirty-ordinary-run-calls.jsonl"
    write_fake_launcher(launcher)
    (workspace / "DIRTY.txt").write_text("ordinary run must not start with dirty tree\n", encoding="utf-8")
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
            "dirty-ordinary-run",
            "--launcher",
            str(launcher),
        ],
        env={**runner_env(), "CHANGERAIL_FAKE_CALL_LOG": str(call_log)},
    )
    if result.returncode == 0:
        raise AssertionError("dirty ordinary run unexpectedly passed")
    if call_log.exists():
        raise AssertionError("dirty ordinary run launched child despite preflight failure")
    status = load_status(runtime, "dirty-ordinary-run")
    checks = {check["name"]: check for check in status["preflight"]["checks"]}
    if checks["workspace dirty state"]["status"] != "fail":
        raise AssertionError(f"dirty ordinary run did not fail clean-tree check: {status}")

    resume_workspace, resume_launcher, resume_runtime = remote_preflight_workspace(tmp, "dirty-remote-resume")
    prior = run(
        [
            str(RUNNER),
            "preflight",
            CARD,
            "--workspace",
            str(resume_workspace),
            "--runtime-root",
            str(resume_runtime),
            "--run-id",
            "dirty-remote-resume-prior",
            "--launcher",
            str(resume_launcher),
            "--json",
            "--write-status",
        ],
        env=fake_git_env(tmp, "dns"),
    )
    if prior.returncode == 0:
        raise AssertionError("dirty remote resume prior unexpectedly passed")
    (resume_workspace / "DIRTY.txt").write_text("remote resume must stay clean-tree gated\n", encoding="utf-8")
    resume_call_log = tmp / "dirty-remote-resume-calls.jsonl"
    resume = run(
        [
            str(RUNNER),
            "resume",
            "--status-path",
            str(resume_runtime / "dirty-remote-resume-prior" / "status.json"),
            "--runtime-root",
            str(resume_runtime),
            "--run-id",
            "dirty-remote-resume",
            "--launcher",
            str(resume_launcher),
        ],
        env={**fake_git_env(tmp, "success"), "CHANGERAIL_FAKE_CALL_LOG": str(resume_call_log)},
    )
    if resume.returncode == 0:
        raise AssertionError("dirty remote preflight resume unexpectedly passed")
    if resume_call_log.exists():
        raise AssertionError("dirty remote preflight resume launched child despite preflight failure")
    resume_status = load_status(resume_runtime, "dirty-remote-resume")
    resume_checks = {check["name"]: check for check in resume_status["preflight"]["checks"]}
    if resume_checks["resume prior status"]["status"] != "pass":
        raise AssertionError(f"remote resume prior status should still be accepted: {resume_status}")
    if resume_checks["workspace dirty state"]["status"] != "fail":
        raise AssertionError(f"dirty remote resume did not fail clean-tree check: {resume_status}")


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
    stale_message = checks["CODEX_HOME symlinks"]["message"]
    if "docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner" not in stale_message:
        raise AssertionError(f"stale symlink remediation was not reported: {stale_message}")


def check_queue_plan_preflight(tmp: Path) -> None:
    consumer, service_a, _service_b = create_queue_consumer(tmp, "queue-consumer")
    runner = tmp / "fake-queue-preflight-ready-runner"
    plan = consumer / "delivery-plan.json"
    runtime = tmp / "queue-runtime"
    write_fake_queue_runner(runner)
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
            str(runner),
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


def check_queue_preflight_child_failure_compact(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-child-fail")
    runner = tmp / "fake-queue-preflight-runner"
    runtime = tmp / "queue-child-fail-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    env = runner_env()
    env["CHANGERAIL_QUEUE_PREFLIGHT_MODE"] = "auth-fail"
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
            "child-fail",
            "--launcher",
            str(runner),
        ],
        env=env,
    )
    if result.returncode == 0:
        raise AssertionError(f"child preflight unexpectedly passed: {result.stdout}")
    if "service-a-card: CODEX auth fail:" not in result.stdout:
        raise AssertionError(f"compact child diagnostic missing: {result.stdout}")
    if "RAW_CHILD_STDOUT_SHOULD_NOT_APPEAR" in result.stdout:
        raise AssertionError(f"aggregate output inlined child stdout: {result.stdout}")

    status = load_status(runtime, "child-fail")
    status_text = json.dumps(status, ensure_ascii=False, sort_keys=True)
    if "RAW_CHILD_STDOUT_SHOULD_NOT_APPEAR" in status_text or "stderr" in status_text:
        raise AssertionError(f"aggregate status inlined child logs: {status}")
    service_a_card = next(card for card in status["cards"] if card["id"] == "service-a-card")
    if service_a_card.get("reason", "").startswith("single-card preflight failed: {"):
        raise AssertionError(f"child reason still uses raw JSON: {service_a_card}")
    if "CODEX auth fail:" not in service_a_card.get("reason", ""):
        raise AssertionError(f"child reason is not compact: {service_a_card}")
    child_status_path = consumer / service_a_card.get("run_status_path", "")
    if not child_status_path.is_file():
        raise AssertionError(f"child status reference is missing: {service_a_card}")

    status_result = run([str(RUNNER), "status-plan", str(runtime / "child-fail" / "status.json")])
    if status_result.returncode == 0:
        raise AssertionError("blocked status-plan unexpectedly returned success")
    if "service-a-card: CODEX auth fail:" not in status_result.stdout:
        raise AssertionError(f"status-plan compact diagnostic missing: {status_result.stdout}")

    json_result = run([str(RUNNER), "status-plan", str(runtime / "child-fail" / "status.json"), "--json"])
    if json_result.returncode == 0:
        raise AssertionError("blocked status-plan --json unexpectedly returned success")
    json_payload = json.loads(json_result.stdout)
    if json_payload["schema"] != "changerail.delivery-plan-status.v1":
        raise AssertionError(f"status-plan --json changed schema: {json_payload}")


def check_queue_preflight_remote_failure_class(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-remote-fail")
    runner = tmp / "fake-queue-remote-preflight-runner"
    runtime = tmp / "queue-remote-fail-runtime"
    plan = consumer / "delivery-plan.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    env = runner_env()
    env["CHANGERAIL_QUEUE_PREFLIGHT_MODE"] = "remote-fail"
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
            "remote-child-fail",
            "--launcher",
            str(runner),
        ],
        env=env,
    )
    if result.returncode == 0:
        raise AssertionError(f"remote child preflight unexpectedly passed: {result.stdout}")
    if "service-a-card: publish target fail: dns:" not in result.stdout:
        raise AssertionError(f"remote class compact diagnostic missing: {result.stdout}")
    status = load_status(runtime, "remote-child-fail")
    service_a_card = next(card for card in status["cards"] if card["id"] == "service-a-card")
    if service_a_card.get("failure_class") != "dns":
        raise AssertionError(f"aggregate card did not retain remote failure class: {service_a_card}")
    if "run_status_path" not in service_a_card:
        raise AssertionError(f"aggregate card did not reference child status: {service_a_card}")
    if "RAW_CHILD_STDOUT_SHOULD_NOT_APPEAR" in json.dumps(status, ensure_ascii=False):
        raise AssertionError(f"aggregate status inlined child output: {status}")


def check_generated_queue_plan(tmp: Path) -> None:
    consumer, _service_a, _service_b = create_queue_consumer(tmp, "queue-generated")
    runner = tmp / "fake-generated-plan-preflight-runner"
    plan = consumer / "generated-delivery-plan.json"
    runtime = tmp / "queue-generated-runtime"
    write_fake_queue_runner(runner)
    generate = run(
        [
            str(RUNNER),
            "generate-plan",
            "--id",
            "queue-generated",
            "--workspace",
            "service-a=service-a",
            "--workspace",
            "service-b=service-b",
            "--card",
            "service-a-card.md",
            "--card",
            "service-b-card=service-b:service-b-card.md",
            "--depends",
            "service-b-card=service-a-card",
            "--max-parallel",
            "2",
            "--output",
            str(plan),
            "--consumer-root",
            str(consumer),
        ]
    )
    require_ok(generate, "generate-plan")
    payload = json.loads(plan.read_text(encoding="utf-8"))
    if payload["schema"] != "changerail.delivery-plan.v1" or payload["id"] != "queue-generated":
        raise AssertionError(f"generated plan contract mismatch: {payload}")
    if [card["id"] for card in payload["cards"]] != ["service-a-card", "service-b-card"]:
        raise AssertionError(f"generated plan did not preserve card order: {payload['cards']}")
    if payload["cards"][1].get("depends_on") != ["service-a-card"]:
        raise AssertionError(f"generated dependency missing: {payload['cards']}")

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
            "generated-plan",
            "--launcher",
            str(RUNNER),
            "--json",
        ]
    )
    require_ok(dry_run, "generated plan dry-run")
    dry_payload = json.loads(dry_run.stdout)
    if dry_payload["result"] != "DELIVERED":
        raise AssertionError(f"generated plan dry-run failed: {dry_payload}")

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
            "generated-preflight",
            "--launcher",
            str(runner),
            "--json",
        ]
    )
    require_ok(preflight, "generated plan preflight")
    status = load_status(runtime, "generated-preflight")
    if status["result"] != "DELIVERED" or len(status["cards"]) != 2:
        raise AssertionError(f"generated plan preflight status invalid: {status}")


def check_queue_launcher_docs() -> None:
    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "docs/how-it-works.md",
            "docs/changerail-contracts.md",
            "docs/consumer-adoption-runbook.md",
            "docs/board-and-two-agent-feature-flow.md",
        )
    )
    expected = [
        "plan runner запускает ChangeRail single-card runner",
        "single-card runner запускает Codex",
        "consumer repository не обязан иметь tracked `bin/codex`",
        "`CODEX_WORKDIR` и effective `CODEX_HOME`",
        "generate-plan",
    ]
    missing = [phrase for phrase in expected if phrase not in docs]
    if missing:
        raise AssertionError(f"queue launcher docs expectations missing: {missing}")


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
    retained_recovery: dict[str, Any] | None = None,
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
    if retained_recovery:
        source["retained_recovery"] = retained_recovery
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


def retained_recovery_fixture(status_path: str = "service-a/.runtime/changerail/delivery-runs/prior/status.json") -> dict[str, Any]:
    return {
        "kind": "original-retained-payload",
        "source_run_id": "prior-service-a-card",
        "source_run_status_path": status_path,
        "source_terminal_reason": "investigation_required",
        "card": {"id": "service-a-card", "path": "openspec/board/3.inprogress/service-a-card.md"},
        "fingerprint": {
            "head_commit": "1" * 40,
            "tree_sha": "2" * 40,
            "diff_fingerprint": "sha256:" + "3" * 64,
        },
        "review_target_kind": "working-tree",
    }


def check_queue_investigation_required_capture_and_original_resume(tmp: Path) -> None:
    consumer, service_a, _service_b = create_queue_consumer(tmp, "queue-retained-original-consumer")
    runner = tmp / "fake-queue-retained-original"
    runtime = tmp / "queue-retained-original-runtime"
    plan = consumer / "delivery-plan.json"
    call_log = tmp / "queue-retained-original-calls.jsonl"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, queue_plan_fixture())
    blocked_env = runner_env()
    blocked_env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    blocked_env["CHANGERAIL_QUEUE_FAKE_MODE"] = "investigation-required"
    blocked = run(
        [
            str(RUNNER),
            "run-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-retained-blocked",
            "--launcher",
            str(runner),
            "--no-push",
            "--json",
        ],
        env=blocked_env,
    )
    if blocked.returncode == 0:
        raise AssertionError("investigation_required queue source unexpectedly delivered")
    blocked_status = load_status(runtime, "queue-retained-blocked")
    source = blocked_status["cards"][0]
    if source.get("terminal_reason") != "investigation_required" or "retained_recovery" not in source:
        raise AssertionError(f"aggregate status did not retain investigation recovery metadata: {blocked_status}")

    (service_a / "DIRTY.txt").write_text("retained dirty payload\n", encoding="utf-8")
    resume_env = runner_env()
    resume_env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    resumed = run(
        [
            str(RUNNER),
            "resume-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-retained-resume",
            "--launcher",
            str(runner),
            "--status-path",
            str(runtime / "queue-retained-blocked" / "status.json"),
            "--no-push",
            "--json",
        ],
        env=resume_env,
    )
    require_ok(resumed, "queue retained original resume")
    calls = [json.loads(line) for line in call_log.read_text(encoding="utf-8").splitlines()]
    resume_calls = [call for call in calls if len(call.get("argv", [])) > 1 and call["argv"][1] == "resume"]
    if not resume_calls:
        raise AssertionError(f"queue retained original recovery did not launch child resume: {calls}")
    if "--status-path" not in resume_calls[0]["argv"]:
        raise AssertionError(f"child resume did not receive prior status path: {resume_calls[0]}")


def check_queue_investigation_required_original_resume_fail_closed(tmp: Path) -> None:
    cases = {
        "resume-stale-auth": "authorization_stale",
        "resume-wrong-card": "card_mismatch",
        "resume-wrong-workspace": "workspace_mismatch",
        "resume-fingerprint-drift": "payload_drift",
    }
    for mode, expected_reason in cases.items():
        consumer, service_a, _service_b = create_queue_consumer(tmp, f"queue-retained-{mode}-consumer")
        runner = tmp / f"fake-queue-retained-{mode}"
        runtime = tmp / f"queue-retained-{mode}-runtime"
        plan = consumer / "delivery-plan.json"
        call_log = tmp / f"queue-retained-{mode}-calls.jsonl"
        original = queue_plan_fixture()
        previous_path = runtime / "previous" / "status.json"
        write_fake_queue_runner(runner)
        write_queue_plan(plan, original)
        write_json(
            previous_path,
            recovery_previous_status(
                original,
                source_state="blocked",
                source_result="BLOCKED",
                terminal_reason="investigation_required",
                retained_recovery=retained_recovery_fixture(),
            ),
        )
        (service_a / "DIRTY.txt").write_text("retained dirty payload\n", encoding="utf-8")
        env = runner_env()
        env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
        env["CHANGERAIL_QUEUE_FAKE_MODE"] = mode
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
                f"queue-retained-{mode}",
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
            raise AssertionError(f"{mode} queue retained resume unexpectedly passed")
        status = load_status(runtime, f"queue-retained-{mode}")
        cards = {card["id"]: card for card in status["cards"]}
        if cards["service-a-card"].get("terminal_reason") != expected_reason:
            raise AssertionError(f"{mode} reason was not preserved: {status}")
        calls = [json.loads(line) for line in call_log.read_text(encoding="utf-8").splitlines()]
        run_cards = [call.get("card") for call in calls if len(call.get("argv", [])) > 1 and call["argv"][1] == "run"]
        if "openspec/board/2.todo/service-b-card.md" in run_cards:
            raise AssertionError(f"{mode} launched downstream after retained resume failure: {calls}")


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

    consumer, dirty_service_a, _dirty_service_b = create_queue_consumer(tmp, "queue-recovery-dirty-retained-consumer")
    runner = tmp / "fake-queue-runner-recovery-dirty-retained"
    call_log = tmp / "queue-recovery-dirty-retained-calls.jsonl"
    runtime = tmp / "queue-recovery-dirty-retained-runtime"
    plan = consumer / "delivery-plan.json"
    original, augmented = recovery_plan_fixture()
    previous_path = runtime / "previous" / "status.json"
    write_fake_queue_runner(runner)
    write_queue_plan(plan, augmented)
    write_json(
        previous_path,
        recovery_previous_status(
            original,
            source_state="blocked",
            source_result="BLOCKED",
            terminal_reason="investigation_required",
            retained_recovery=retained_recovery_fixture(),
        ),
    )
    (dirty_service_a / "DIRTY.txt").write_text("dirty retained payload cannot mix with replacement\n", encoding="utf-8")
    env = runner_env()
    env["CHANGERAIL_FAKE_CALL_LOG"] = str(call_log)
    dirty_result = run(
        [
            str(RUNNER),
            "resume-plan",
            str(plan),
            "--consumer-root",
            str(consumer),
            "--runtime-root",
            str(runtime),
            "--run-id",
            "queue-recovery-dirty-retained",
            "--launcher",
            str(runner),
            "--status-path",
            str(previous_path),
            "--no-push",
            "--json",
        ],
        env=env,
    )
    if dirty_result.returncode == 0:
        raise AssertionError("dirty retained replacement recovery unexpectedly passed")
    if call_log.exists() and queue_run_calls(call_log):
        raise AssertionError("dirty retained replacement recovery launched a child")


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
        check_single_card_status_reader(workspace)
        check_one_command_delivery_success(workspace)
        check_one_command_delivery_resume_after_preflight(workspace)
        check_one_command_delivery_stale_verdict_blocks(workspace)
        check_one_command_delivery_review_budget_no_go(workspace)
        check_success_run(workspace)
        check_default_workspace_run(workspace)
        check_performance_summary_run(workspace)
        check_oversized_output_summary_run(workspace)
        check_no_go_run(workspace)
        check_review_no_go_fallback_run(workspace)
        check_supervisor_stops_after_fallback_no_go(workspace)
        check_fix_budget_handoff_run(workspace)
        check_external_blocker_handoff_run(workspace)
        check_malformed_terminal_reason_run(workspace)
        check_unstructured_unpublished_success_run(workspace)
        check_marker_like_prose_is_not_authoritative(workspace)
        check_non_terminal_error_success_run(workspace)
        check_ordered_conflict_run(workspace)
        check_nonzero_without_outcome_run(workspace)
        check_awaiting_review_run(workspace)
        check_preflight(workspace)
        check_preflight_rejects_insufficient_automation_authority(workspace)
        check_custom_launcher_without_path_codex(workspace)
        check_default_launcher_requires_path_codex(workspace)
        check_publish_target_preflight(workspace)
        check_remote_preflight_failure_classes(workspace)
        check_remote_preflight_resume_success(workspace)
        check_retained_payload_status_schema_and_single_card_resume(workspace)
        check_retained_payload_resume_fail_closed(workspace)
        check_preflight_connectivity_failure_redaction(workspace)
        check_explicit_codex_home_preflight(workspace)
        check_run_preflight_failure(workspace)
        check_single_card_dirty_workspace_blocks_ordinary_launches(workspace)
        check_stale_symlink_preflight(workspace)
        check_queue_plan_preflight(workspace)
        check_queue_preflight_child_failure_compact(workspace)
        check_queue_preflight_remote_failure_class(workspace)
        check_generated_queue_plan(workspace)
        check_queue_launcher_docs()
        check_queue_preflight_failures(workspace)
        check_queue_run_plan(workspace)
        check_queue_fail_fast_and_locks(workspace)
        check_queue_terminal_reason_and_missing_status(workspace)
        check_queue_resume_plan(workspace)
        check_queue_investigation_required_capture_and_original_resume(workspace)
        check_queue_investigation_required_original_resume_fail_closed(workspace)
        check_queue_recovery_resume(workspace)
        check_queue_recovery_fail_closed(workspace)
        check_queue_recovery_rejects_external_and_unrelated_drift(workspace)
        check_queue_push_success_validation(workspace)
        check_queue_no_push_requires_ahead(workspace)
    print("ok: delivery runner smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
