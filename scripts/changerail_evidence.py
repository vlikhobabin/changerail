#!/usr/bin/env python3
"""Capture and validate retained ChangeRail verification evidence."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from changerail_contract_schema import validate_with_schema

SCHEMA_ID = "changerail.evidence-index.v1"
SCHEMA_FILE = "changerail-evidence-index.schema.json"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SECRET_KEY_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|authorization|credential)")
SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b(token|secret|password|passwd|api[_-]?key|authorization|credential)\b\s*[:=]\s*([^\s;&|]+)"
)
SECRET_OUTPUT_RE = re.compile(
    r"(?im)\b(token|secret|password|passwd|api[_-]?key|authorization|credential)\b\s*[:=]\s*([^\r\n]*)"
)
SCP_REMOTE_RE = re.compile(r"^(?:(?P<user>[^@/:]+)@)?(?P<host>[^:/]+):(?P<path>.+)$")


class EvidenceError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise EvidenceError(f"evidence index cannot be read: {exc}", 2) from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"evidence index JSON is invalid: {exc}", 2) from exc


def relpath(path: Path, workspace: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(workspace.resolve(strict=False)).as_posix()
    except ValueError as exc:
        raise EvidenceError(f"evidence path must stay inside workspace: {path}", 2) from exc


def sanitize_repository_identity(raw: str) -> str:
    if not raw:
        return "repository"
    if "://" in raw:
        parts = urlsplit(raw)
        host = parts.hostname or ""
        if parts.port:
            host = f"{host}:{parts.port}"
        return urlunsplit((parts.scheme, host, parts.path, "", ""))
    match = SCP_REMOTE_RE.match(raw)
    if match:
        host = match.group("host")
        path = match.group("path").lstrip("/")
        return f"ssh://{host}/{path}"
    if raw.startswith("/") or raw.startswith("./") or raw.startswith("../"):
        return Path(raw).name or "repository"
    return raw


def git_repository_identity(workspace: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(workspace), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return sanitize_repository_identity(result.stdout.strip())


def safe_scope_segment(value: str | None) -> str:
    if not value:
        return "general"
    lowered = value.lower()
    safe = re.sub(r"[^a-z0-9._-]+", "-", lowered).strip("-._")
    return safe or "general"


def default_index_path(workspace: Path, args: argparse.Namespace) -> Path:
    if args.index:
        candidate = args.index if args.index.is_absolute() else workspace / args.index
        return require_runtime_index_path(workspace, candidate)
    scope = safe_scope_segment(args.card_id or args.run_id or args.trace_id)
    return workspace / ".runtime" / "changerail" / "evidence" / scope / "index.json"


def require_runtime_index_path(workspace: Path, index_path: Path) -> Path:
    resolved = index_path.resolve(strict=False)
    evidence_root = (workspace / ".runtime" / "changerail" / "evidence").resolve(strict=False)
    try:
        resolved.relative_to(evidence_root)
    except ValueError as exc:
        raise EvidenceError("--index must resolve under .runtime/changerail/evidence/", 2) from exc
    return index_path


def normalize_argv(argv: list[str]) -> list[str]:
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        raise EvidenceError("capture requires an argv after --", 2)
    return argv


def is_secret_like_argv(arg: str) -> bool:
    if "://" in arg and "@" in urlsplit(arg).netloc:
        return True
    if SECRET_ASSIGN_RE.search(arg):
        return True
    if arg.startswith("--") and "=" in arg:
        key = arg[2:].split("=", 1)[0]
        return bool(SECRET_KEY_RE.search(key))
    return False


def check_argv_safe(argv: list[str]) -> None:
    for index, arg in enumerate(argv):
        if is_secret_like_argv(arg):
            raise EvidenceError(
                f"command argv contains a secret-like value at position {index}; capture refused",
                2,
            )


def redact_text(text: str) -> tuple[str, bool]:
    redacted = False

    def replace(match: re.Match[str]) -> str:
        nonlocal redacted
        redacted = True
        key = match.group(1)
        return f"{key}=<REDACTED>"

    return SECRET_OUTPUT_RE.sub(replace, text), redacted


def concise_text(value: str, max_length: int = 500) -> str:
    compact = " ".join(value.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."


def summarize_output(output: str, status: str) -> str:
    for line in output.splitlines():
        compact = line.strip()
        if compact:
            return concise_text(f"{status}: {compact}")
    return f"{status}: command produced no output"


def base_index(workspace: Path, args: argparse.Namespace) -> dict[str, Any]:
    scope: dict[str, Any] = {}
    if args.card_id:
        scope["card_id"] = args.card_id
    if args.card_path:
        scope["card_path"] = args.card_path
    if args.change:
        scope["changes"] = args.change
    if args.trace_id:
        scope["trace_id"] = args.trace_id
    if args.run_id:
        scope["run_id"] = args.run_id
    workspace_data = {"root": str(workspace.resolve(strict=False))}
    repository = git_repository_identity(workspace)
    if repository:
        workspace_data["repository"] = repository
    return {
        "schema": SCHEMA_ID,
        "updated_at": utc_now(),
        "workspace": workspace_data,
        "scope": scope,
        "entries": [],
    }


def load_or_create_index(path: Path, workspace: Path, args: argparse.Namespace) -> dict[str, Any]:
    if not path.exists():
        return base_index(workspace, args)
    data = load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("evidence index must be an object", 1)
    return data


def upsert_entry(index: dict[str, Any], entry: dict[str, Any]) -> None:
    entries = index.setdefault("entries", [])
    if not isinstance(entries, list):
        raise EvidenceError("evidence index entries must be an array", 1)
    entries[:] = [existing for existing in entries if not isinstance(existing, dict) or existing.get("id") != entry["id"]]
    entries.append(entry)
    index["updated_at"] = utc_now()


def combined_output(stdout: str | bytes | None, stderr: str | bytes | None) -> str:
    def as_text(value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value

    parts: list[str] = []
    stdout_text = as_text(stdout)
    stderr_text = as_text(stderr)
    if stdout_text:
        parts.append("[stdout]\n" + stdout_text)
    if stderr_text:
        parts.append("[stderr]\n" + stderr_text)
    return "\n".join(parts)


def command_display(argv: list[str]) -> str:
    return concise_text(shlex.join(argv), 500)


def command_entry(
    args: argparse.Namespace,
    workspace: Path,
    index_path: Path,
    output_path: Path,
    argv: list[str],
    result: subprocess.CompletedProcess[str] | subprocess.TimeoutExpired[str] | None,
    started_at: str,
    ended_at: str,
    duration_seconds: float,
    status: str,
    redacted: bool,
    output_text: str,
    diagnostic: str | None = None,
) -> dict[str, Any]:
    exit_code: int | None = None
    timed_out = status == "timeout"
    if isinstance(result, subprocess.CompletedProcess):
        exit_code = result.returncode
    summary = args.summary or summarize_output(output_text, status)
    diagnostics: list[str] = []
    if redacted:
        diagnostics.append("secret-like output was redacted before retention")
    if diagnostic:
        diagnostics.append(diagnostic)
    entry: dict[str, Any] = {
        "id": args.id,
        "path": relpath(output_path, workspace),
        "role": "raw_output",
        "storage": "runtime",
        "phase": args.phase,
        "classification": args.classification,
        "command": {
            "argv": argv,
            "display": command_display(argv),
        },
        "status": status,
        "exit_code": exit_code,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
        "summary": concise_text(summary, 2000),
        "raw_output_path": relpath(output_path, workspace),
        "redacted": redacted,
        "timed_out": timed_out,
    }
    if args.change:
        entry["change"] = args.change[0]
    if diagnostics:
        entry["diagnostics"] = diagnostics
    entry["kind"] = "verification_command"
    entry["reason"] = f"captured in {relpath(index_path, workspace)}"
    return entry


def validate_evidence_index(data: Any, workspace: Path) -> list[str]:
    errors = validate_with_schema(data, SCHEMA_FILE)
    if errors or not isinstance(data, dict):
        return errors
    for index, entry in enumerate(data.get("entries", [])):
        if not isinstance(entry, dict):
            continue
        label = f"entries[{index}]"
        role = entry.get("role")
        if role == "raw_output":
            for field in ("command", "status", "started_at", "ended_at", "raw_output_path", "summary"):
                if field not in entry:
                    errors.append(f"{label}.{field} must be present for raw_output evidence")
        paths = []
        if entry.get("storage") == "runtime":
            for field in ("path", "raw_output_path"):
                value = entry.get(field)
                if isinstance(value, str) and value not in paths:
                    paths.append(value)
        for evidence_path in paths:
            if not (workspace / evidence_path).exists():
                errors.append(f"{label} references missing runtime evidence path: {evidence_path}")
    return errors


def cmd_capture(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    if not ID_RE.fullmatch(args.id):
        raise EvidenceError("--id must match ^[a-z0-9][a-z0-9._-]*$", 2)
    argv = normalize_argv(args.argv)
    check_argv_safe(argv)
    index_path = default_index_path(workspace, args)
    output_dir = index_path.parent / "outputs"
    output_path = output_dir / f"{args.id}.txt"
    started_at = utc_now()
    started = time.monotonic()
    result: subprocess.CompletedProcess[str] | subprocess.TimeoutExpired[str] | None = None
    diagnostic = None
    try:
        result = subprocess.run(
            argv,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
        status = "passed" if result.returncode == 0 else "failed"
        output = combined_output(result.stdout, result.stderr)
    except subprocess.TimeoutExpired as exc:
        result = exc
        status = "timeout"
        diagnostic = f"command timed out after {args.timeout} seconds"
        output = combined_output(exc.stdout, exc.stderr)
    except OSError as exc:
        status = "blocked"
        diagnostic = f"command could not be started: {type(exc).__name__}"
        output = diagnostic
    ended_at = utc_now()
    duration_seconds = round(max(0.0, time.monotonic() - started), 3)
    redacted_output, redacted = redact_text(output)
    atomic_write_text(output_path, redacted_output)
    index = load_or_create_index(index_path, workspace, args)
    entry = command_entry(
        args,
        workspace,
        index_path,
        output_path,
        argv,
        result,
        started_at,
        ended_at,
        duration_seconds,
        status,
        redacted,
        redacted_output,
        diagnostic,
    )
    upsert_entry(index, entry)
    errors = validate_evidence_index(index, workspace)
    if errors:
        raise EvidenceError("; ".join(errors), 1)
    write_json(index_path, index)
    payload = {
        "ok": status == "passed",
        "command": "capture",
        "schema": SCHEMA_ID,
        "id": args.id,
        "status": status,
        "exit_code": entry.get("exit_code"),
        "index_path": relpath(index_path, workspace),
        "raw_output_path": entry["raw_output_path"],
        "redacted": redacted,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"{status}: retained evidence {args.id} at {payload['index_path']}")
    return 0 if status == "passed" else 1


def cmd_note(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    if not ID_RE.fullmatch(args.id):
        raise EvidenceError("--id must match ^[a-z0-9][a-z0-9._-]*$", 2)
    index_path = default_index_path(workspace, args)
    index = load_or_create_index(index_path, workspace, args)
    entry: dict[str, Any] = {
        "id": args.id,
        "path": relpath(index_path, workspace),
        "role": "curated_summary",
        "storage": "runtime",
        "phase": args.phase,
        "classification": "not_applicable",
        "status": "not_applicable",
        "summary": concise_text(args.reason, 2000),
        "reason": args.reason,
    }
    if args.change:
        entry["change"] = args.change[0]
    upsert_entry(index, entry)
    write_json(index_path, index)
    errors = validate_evidence_index(index, workspace)
    if errors:
        raise EvidenceError("; ".join(errors), 1)
    payload = {
        "ok": True,
        "command": "note",
        "schema": SCHEMA_ID,
        "id": args.id,
        "index_path": relpath(index_path, workspace),
    }
    print(json.dumps(payload, ensure_ascii=False) if args.json else f"ok: retained note {args.id}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve(strict=False)
    data = load_json(args.index)
    errors = validate_evidence_index(data, workspace)
    if errors:
        raise EvidenceError("; ".join(errors), 1)
    payload = {
        "ok": True,
        "command": "validate",
        "schema": SCHEMA_ID,
        "index": str(args.index),
        "entries": len(data.get("entries", [])) if isinstance(data, dict) else 0,
    }
    print(json.dumps(payload, ensure_ascii=False) if args.json else f"ok: valid {SCHEMA_ID} index")
    return 0


def add_scope_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--index", type=Path)
    parser.add_argument("--card-id")
    parser.add_argument("--card-path")
    parser.add_argument("--change", action="append", default=[])
    parser.add_argument("--trace-id")
    parser.add_argument("--run-id")
    parser.add_argument("--phase", choices=["ff", "do", "review", "pub", "manual"], default="do")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture", help="run a command and retain verification evidence")
    add_scope_args(capture)
    capture.add_argument("--id", required=True)
    capture.add_argument("--classification", choices=["mandatory", "diagnostic"], default="mandatory")
    capture.add_argument("--timeout", type=float, default=300.0)
    capture.add_argument("--summary")
    capture.add_argument("--json", action="store_true")
    capture.add_argument("argv", nargs=argparse.REMAINDER)
    capture.set_defaults(func=cmd_capture)

    note = subparsers.add_parser("note", help="record not-applicable evidence without running a command")
    add_scope_args(note)
    note.add_argument("--id", required=True)
    note.add_argument("--reason", required=True)
    note.add_argument("--json", action="store_true")
    note.set_defaults(func=cmd_note)

    validate = subparsers.add_parser("validate", help="validate an evidence index")
    validate.add_argument("index", type=Path)
    validate.add_argument("--workspace", type=Path, default=Path("."))
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_validate)
    return parser


def print_json_diagnostic(message: str, command: str, code: str) -> None:
    diagnostic = {
        "kind": "changerail_evidence",
        "code": code,
        "message": message,
    }
    payload = {
        "schema": SCHEMA_ID,
        "ok": False,
        "command": command,
        "diagnostic": diagnostic,
        "diagnostics": [diagnostic],
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except EvidenceError as exc:
        if getattr(args, "json", False):
            code = "input_error" if exc.exit_code == 2 else "validation_failed"
            print_json_diagnostic(str(exc), getattr(args, "command", "unknown"), code)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        if getattr(args, "json", False):
            print_json_diagnostic(str(exc), getattr(args, "command", "unknown"), "input_error")
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
