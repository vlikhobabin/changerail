#!/usr/bin/env python3
# ruff: noqa: E701, E702
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import stat
import sys
import time
from typing import Any

import changerail_release_child_broker as legacy_broker

VERSION = "changerail.release-admitted-execution.v1"
ROW_FIELDS = {"version", "owner", "kind", "members", "digest"}
MEMBER_FIELDS = {"id", "logical_argv", "physical_argv", "fd_map", "executable", "operands", "environment", "digest"}
MAX_BUNDLE = 65536
class AdmissionError(RuntimeError):
    pass
def _json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()
def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value)).hexdigest()
def _mount(fd: int) -> int:
    for line in Path(f"/proc/self/fdinfo/{fd}").read_text().splitlines():
        if line.startswith("mnt_id:"):
            return int(line.split()[1])
    raise AdmissionError("missing mount identity")
def _identity(path: Path) -> dict[str, Any]:
    lexical = Path(os.path.abspath(path)); real = path.resolve(strict=True)
    if lexical != real: raise AdmissionError(f"lexical path has symlink or alias ancestry: {path.name}")
    chain = []; seen = set(); fd = os.open(real.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for index, part in enumerate(real.parts[1:]):
            flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
            if index + 1 < len(real.parts) - 1: flags |= os.O_DIRECTORY
            child = os.open(part, flags, dir_fd=fd); os.close(fd); fd = child
            info = os.fstat(fd); identity = (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode), _mount(fd))
            if identity in seen: raise AdmissionError("repeated ancestry identity")
            seen.add(identity); chain.append(list(identity))
        info = os.fstat(fd)
        return {"path": str(real), "device": info.st_dev, "inode": info.st_ino, "size": info.st_size,
                "mtime_ns": info.st_mtime_ns, "mode": stat.S_IFMT(info.st_mode), "mount": _mount(fd), "chain": chain}
    finally:
        os.close(fd)
def _member(owner: str, index: int, command: list[str], environment: dict[str, str]) -> dict[str, Any]:
    logical = list(command)
    first = Path(logical[0])
    candidate = first if first.is_absolute() else Path.cwd() / first
    script = candidate if (first.is_absolute() or "/" in logical[0]) and candidate.read_bytes()[:2] == b"#!" else None
    executable = Path(shutil.which(logical[0], path=environment["PATH"]) or "").resolve(strict=True)
    operands: list[dict[str, Any]] = []
    if script is not None:
        script = script.resolve(strict=True)
        shell = "/usr/bin/bash" if script.name == "openspec" else "/bin/sh"
        executable = Path(shell).resolve(strict=True)
        operands.append({"index": 0, "needle": logical[0], "identity": _identity(script)})
    elif first.is_absolute() or "/" in logical[0]:
        executable = candidate.resolve(strict=True)
    elif logical[0].startswith("python") or Path(executable).name.startswith("python"):
        executable = Path(sys.executable).resolve(strict=True)
        if len(logical) > 1 and "/" in logical[1] and (Path.cwd() / logical[1]).is_file():
            operands.append({"index": 1, "needle": logical[1],
                             "identity": _identity(Path.cwd() / logical[1])})
    if not executable.is_file():
        raise AdmissionError(f"unresolved executable for {owner}")
    for position, token in enumerate(logical[1:], 1):
        candidate = Path.cwd() / token
        if candidate.exists() and not any(item["index"] == position for item in operands):
            operands.append({"index": position, "needle": token, "identity": _identity(candidate)})
    if ".codex/config.toml" in " ".join(logical):
        operands.append({"index": -1, "needle": ".codex/config.toml",
                         "identity": _identity(Path.cwd() / ".codex/config.toml")})
    return {"id": f"{owner}:{index}", "logical_argv": logical,
            "executable": _identity(executable), "operands": operands,
            "environment": environment}
def _physical(member: dict[str, Any], fds: list[int], bundle: bool = False) -> tuple[list[str], dict[str, Any]]:
    argv = list(member["logical_argv"]); offset = 1
    for operand, fd in zip(member["operands"], fds[1:], strict=True):
        if operand["index"] == 0: argv = [argv[0], f"/proc/self/fd/{fd}", *argv[1:]]; offset = 2
        elif operand["index"] == -1: argv = [item.replace(operand["needle"], f"/proc/self/fd/{fd}") for item in argv]
        else: argv[operand["index"] + offset - 1] = f"/proc/self/fd/{fd}"
    if bundle: argv.append("199")
    return argv, {"executable": fds[0], "operands": fds[1:], "bundle": 199 if bundle else None}
def build_row(owner: str, commands: list[list[str]], environment: dict[str, str]) -> dict[str, Any]:
    kind = "direct" if len(commands) == 1 else "sequential-group"
    members = [_member(owner, index, command, environment)
               for index, command in enumerate(commands)]
    if kind == "sequential-group":
        outer = _member(owner, -1, [sys.executable, str(Path(__file__).resolve()), "--group"], environment)
        members.insert(0, outer)
    next_fd = 200
    for index, member in enumerate(members):
        fds = list(range(next_fd, next_fd + 1 + len(member["operands"]))); next_fd += len(fds)
        member["physical_argv"], member["fd_map"] = _physical(member, fds, kind == "sequential-group" and index == 0)
        member["digest"] = _digest(member)
    body = {"version": VERSION, "owner": owner, "kind": kind, "members": members}
    return body | {"digest": _digest(body)}
def validate_table(plan: list[dict[str, Any]], table: Any) -> tuple[dict[str, Any], ...]:
    if type(table) is not list or len(table) != len(plan):
        raise AdmissionError("admission table cardinality mismatch")
    rows: list[dict[str, Any]] = []
    for task, row in zip(plan, table, strict=True):
        if type(row) is not dict or set(row) != ROW_FIELDS or row["version"] != VERSION:
            raise AdmissionError("admission row fields mismatch")
        body = {key: row[key] for key in ("version", "owner", "kind", "members")}
        if row["digest"] != _digest(body) or row["owner"] != task["id"]:
            raise AdmissionError("admission row digest or owner mismatch")
        if row["kind"] not in ("direct", "sequential-group"):
            raise AdmissionError("unknown admission kind")
        expected = 1 if row["kind"] == "direct" else 2
        if type(row["members"]) is not list or len(row["members"]) < expected:
            raise AdmissionError("admission members mismatch")
        for member in row["members"]:
            if type(member) is not dict or set(member) != MEMBER_FIELDS:
                raise AdmissionError("admission member fields mismatch")
            member_body = {key: member[key] for key in MEMBER_FIELDS - {"digest"}}
            if member["digest"] != _digest(member_body):
                raise AdmissionError("admission member digest mismatch")
        if task["command"] != row["members"][0]["logical_argv"]:
            raise AdmissionError("plan argv mismatch")
        rows.append(row)
    if len({row["owner"] for row in rows}) != len(rows):
        raise AdmissionError("duplicate admission owner")
    return tuple(rows)
def _open_bundle(row: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    bindings = []
    next_fd = 200
    for member in row["members"]:
        identities = [member["executable"]] + [item["identity"] for item in member["operands"]]
        fds = []
        for identity in identities:
            raw = os.open(identity["path"], os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
            try:
                info = os.fstat(raw); observed = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, stat.S_IFMT(info.st_mode), _mount(raw))
                expected = tuple(identity[key] for key in ("device", "inode", "size", "mtime_ns", "mode", "mount"))
                if observed != expected:
                    raise AdmissionError("opened identity drift")
                os.dup2(raw, next_fd, inheritable=True)
                fds.append(next_fd)
                next_fd += 1
            finally:
                os.close(raw)
        argv, fd_map = _physical(member, fds, row["kind"] == "sequential-group" and not bindings)
        if argv != member["physical_argv"] or fd_map != member["fd_map"]: raise AdmissionError("physical execution binding drift")
        bindings.append({"member": member, "exec_fd": fds[0], "operand_fds": fds[1:], "argv": argv})
    payload = _json({"version": VERSION, "row": row, "bindings": bindings})
    if len(payload) > MAX_BUNDLE:
        raise AdmissionError("sealed bundle exceeds bound")
    raw = os.memfd_create("changerail-admission", os.MFD_ALLOW_SEALING | os.MFD_CLOEXEC)
    os.write(raw, payload)
    fcntl.fcntl(raw, fcntl.F_ADD_SEALS, fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK |
                fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE)
    os.dup2(raw, 199, inheritable=True)
    os.close(raw)
    return 199, bindings


def _supervise_fd(binding: dict[str, Any], execution: float, cleanup: float) -> dict[str, Any]:
    legacy_broker._enable_subreaper()
    output_r, output_w = os.pipe2(os.O_CLOEXEC)
    error_r, error_w = os.pipe2(os.O_CLOEXEC)
    status_r, status_w = os.pipe2(os.O_CLOEXEC)
    pid = os.fork()
    if pid == 0:
        try:
            os.close(output_r); os.close(error_r); os.close(status_r)
            os.setsid(); os.dup2(output_w, 1); os.dup2(error_w, 2)
            os.execve(binding["exec_fd"], binding["argv"], binding["member"]["environment"])
        except BaseException as exc:
            os.write(status_w, str(type(exc).__name__).encode()[:128])
        os._exit(127)
    os.close(output_w); os.close(error_w); os.close(status_w)
    ready = selectors.DefaultSelector(); ready.register(status_r, selectors.EVENT_READ)
    if not ready.select(min(1.0, execution)) or os.read(status_r, 128):
        ready.close(); os.close(status_r); os.waitpid(pid, 0)
        os.close(output_r); os.close(error_r)
        return {"status": "fail", "reason": "internal_error", "returncode": 127,
                "output_bytes": 0, "cleanup_complete": True, "messages": 3}
    ready.close(); os.close(status_r)
    poll = selectors.DefaultSelector()
    for fd in (output_r, error_r):
        os.set_blocking(fd, False); poll.register(fd, selectors.EVENT_READ)
    deadline = time.monotonic() + execution; total = 0; status = None; reason = "completed"
    while time.monotonic() < deadline and status is None:
        for key, _mask in poll.select(0.02):
            chunk = os.read(key.fd, min(4096, 8193 - total))
            if not chunk: poll.unregister(key.fd)
            total += len(chunk)
            if total > 8192: reason = "output_limit"; break
        found, status = os.waitpid(pid, os.WNOHANG)
        status = status if found else None
        if reason == "output_limit": break
    if status is None:
        if reason == "completed": reason = "execution_timeout"
        try: os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError: pass
        _found, status = os.waitpid(pid, 0)
    poll.close(); os.close(output_r); os.close(error_r)
    cleanup_complete = legacy_broker._cleanup(os.getpid(), cleanup)
    code = os.waitstatus_to_exitcode(status)
    if reason == "completed" and code != 0: reason = "child_failed"
    if not cleanup_complete: reason = "cleanup_incomplete"
    passed = reason == "completed" and code == 0 and cleanup_complete
    return {"status": "pass" if passed else "fail", "reason": reason,
            "returncode": code, "output_bytes": min(total, 8193),
            "cleanup_complete": cleanup_complete, "messages": 3}


def admitted_supervisor(command: Any, *, execution_timeout: float, cleanup_timeout: float,
                        admission: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    matches = [row for row in admission if row["members"][0]["logical_argv"] == list(command)]
    if len(matches) != 1:
        raise AdmissionError("admitted command lookup mismatch")
    bundle_fd, bindings = _open_bundle(matches[0])
    if matches[0]["kind"] == "direct":
        return _supervise_fd(bindings[0], execution_timeout, cleanup_timeout)
    return _supervise_fd(bindings[0], execution_timeout, cleanup_timeout)


def _group(bundle_fd: int) -> int:
    seals = fcntl.fcntl(bundle_fd, fcntl.F_GET_SEALS)
    required = fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE
    if seals != required:
        return 2
    os.lseek(bundle_fd, 0, os.SEEK_SET)
    payload = json.loads(os.read(bundle_fd, MAX_BUNDLE + 1))
    row = payload["row"]
    if row["digest"] != _digest({key: row[key] for key in ("version", "owner", "kind", "members")}):
        return 2
    for binding in payload["bindings"][1:]:
        result = _supervise_fd(binding, 3600.0, 60.0)
        if result["status"] != "pass":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_group(int(sys.argv[2])) if sys.argv[1:2] == ["--group"] and len(sys.argv) == 3 else 2)
