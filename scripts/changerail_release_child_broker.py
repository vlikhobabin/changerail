#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
from typing import Any

VERSION = "changerail.release-child-broker.v1"
MAX_FRAME = 4096
MAX_STREAM = 16384
MAX_OUTPUT = 8192
MAX_IDENTITIES = 128
MAX_SCANS = 32
MAX_EXECUTION = 3600.0
MAX_CLEANUP = 60.0


class BrokerError(RuntimeError):
    pass


def _number(value: Any, name: str, maximum: float) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result) or result <= 0 or result > maximum:
        raise ValueError(f"{name} is outside its bound")
    return result


def _command(value: Any) -> tuple[str, ...]:
    if type(value) not in (list, tuple) or not value or len(value) > 64:
        raise ValueError("command must contain 1..64 arguments")
    result: list[str] = []
    for item in value:
        if type(item) is not str or not item or "\0" in item:
            raise ValueError("command arguments must be non-empty text")
        if len(item.encode()) > 4096:
            raise ValueError("command argument exceeds 4096 bytes")
        result.append(item)
    return tuple(result)


def _write_line(fd: int, message: dict[str, Any]) -> None:
    raw = json.dumps(message, separators=(",", ":"), sort_keys=True,
                     allow_nan=False).encode() + b"\n"
    if len(raw) > MAX_FRAME:
        raise BrokerError("protocol frame exceeds bound")
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        view = view[written:]


def _emit(fd: int, seq: int, kind: str, **fields: Any) -> None:
    _write_line(fd, {"v": VERSION, "seq": seq, "type": kind, **fields})


def _enable_subreaper() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                      ctypes.c_ulong, ctypes.c_ulong]
    prctl.restype = ctypes.c_int
    if prctl(36, 1, 0, 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _identity(pid: int) -> tuple[int, int, int, str] | None:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except (FileNotFoundError, ProcessLookupError):
        return None
    close = raw.rfind(")")
    if close < 0:
        raise BrokerError("malformed proc stat")
    fields = raw[close + 2:].split()
    if len(fields) < 20:
        raise BrokerError("short proc stat")
    return pid, int(fields[19]), int(fields[1]), fields[0]


def _descendants(root: int) -> list[tuple[int, int]]:
    by_parent: dict[int, list[tuple[int, int]]] = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        item = _identity(int(entry.name))
        if item is None:
            continue
        pid, started, parent, _state = item
        by_parent.setdefault(parent, []).append((pid, started))
    result: list[tuple[int, int]] = []
    queue = [root]
    while queue:
        parent = queue.pop(0)
        for identity in sorted(by_parent.get(parent, [])):
            result.append(identity)
            queue.append(identity[0])
            if len(result) > MAX_IDENTITIES:
                raise BrokerError("identity_limit")
    return result


def _same_identity(identity: tuple[int, int]) -> bool:
    current = _identity(identity[0])
    return current is not None and current[1] == identity[1]


def _signal_identity(identity: tuple[int, int], sig: int) -> bool:
    pid, _started = identity
    if not _same_identity(identity):
        return False
    try:
        fd = os.pidfd_open(pid, 0)
    except ProcessLookupError:
        return False
    try:
        if not _same_identity(identity):
            return False
        signal.pidfd_send_signal(fd, sig)  # CONNECTED_PIDFD_SIGNAL
        return True
    except ProcessLookupError:
        return False
    finally:
        os.close(fd)


def _reap() -> None:
    while True:
        try:
            pid, _status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0:
            return


def _cleanup(root: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    term_until = min(deadline, time.monotonic() + min(0.15, timeout / 2))
    empty = 0
    scans = 0
    while time.monotonic() < deadline and scans < MAX_SCANS:
        scans += 1
        identities = _descendants(root)
        if identities:
            empty = 0
            sig = signal.SIGTERM if time.monotonic() < term_until else signal.SIGKILL
            for identity in reversed(identities):
                _signal_identity(identity, sig)
        else:
            empty += 1
            if empty == 2:
                return True
        _reap()
        time.sleep(0.01)
    return False


def _capture(process: subprocess.Popen[bytes], timeout: float) -> tuple[str, int]:
    selector = selectors.DefaultSelector()
    streams = [process.stdout, process.stderr]
    for stream in streams:
        if stream is None:
            raise BrokerError("missing target pipe")
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    total = 0
    try:
        while time.monotonic() < deadline:
            for key, _mask in selector.select(0.02):
                chunk = os.read(key.fd, min(4096, MAX_OUTPUT + 1 - total))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                total += len(chunk)
                if total > MAX_OUTPUT:
                    return "output_limit", total
            code = process.poll()
            if code is not None:
                return ("completed" if code == 0 else "child_failed"), total
        return "execution_timeout", total
    finally:
        selector.close()
        for stream in streams:
            if stream is not None:
                stream.close()


def _wait_marker_before_fatal() -> None:
    marker = os.environ.get("CHANGERAIL_BROKER_TARGET_MARKER")
    if not marker:
        time.sleep(0.05)
        return
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        if Path(marker).exists():
            return
        time.sleep(0.005)


def _terminal(fd: int, seq: int, status: str, reason: str,
              returncode: int | None, output_bytes: int,
              cleanup_complete: bool) -> None:
    _emit(fd, seq, "terminal", status=status, reason=reason,
          returncode=returncode, output_bytes=output_bytes,
          cleanup_complete=cleanup_complete)


def _broker(fd: int, command: tuple[str, ...], execution: float,
            cleanup: float) -> int:
    process: subprocess.Popen[bytes] | None = None
    seq = 1
    output_bytes = 0
    reason = "internal_error"
    cleanup_complete = False
    try:
        _enable_subreaper()
        fault = os.environ.get("CHANGERAIL_BROKER_PROTOCOL_FAULT")
        if fault == "malformed":
            os.write(fd, b"{not-json}\n")
            return 2
        _emit(fd, seq, "ready")
        seq += 1
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, close_fds=True)
        _emit(fd, seq, "started", pid=process.pid)
        if fault == "duplicate":
            _emit(fd, seq, "started", pid=process.pid)
        seq += 1
        if fault == "eof":
            os.close(fd)
            fd = -1
            time.sleep(execution + cleanup + 1)
            return 2
        if os.environ.get("CHANGERAIL_BROKER_HARD_EXIT_AFTER_START") == "1":
            _wait_marker_before_fatal()
            os._exit(91)
        reason, output_bytes = _capture(process, execution)
        cleanup_complete = _cleanup(os.getpid(), cleanup)
        code = process.poll()
        passed = reason == "completed" and code == 0 and cleanup_complete
        if not cleanup_complete:
            reason = "cleanup_incomplete"
        _terminal(fd, seq, "pass" if passed else "fail", reason, code,
                  output_bytes, cleanup_complete)
        return 0 if passed else 1
    except BaseException:
        try:
            cleanup_complete = _cleanup(os.getpid(), cleanup) if process else True
        except BaseException:
            cleanup_complete = False
        if fd >= 0:
            try:
                _terminal(fd, seq, "fail", "internal_error",
                          process.poll() if process else None, output_bytes,
                          cleanup_complete)
            except BaseException:
                pass
        return 2
    finally:
        if fd >= 0:
            os.close(fd)


class _ForkProcess:
    def __init__(self, pid: int):
        self.pid = pid
        self._status: int | None = None

    def poll(self) -> int | None:
        if self._status is not None:
            return os.waitstatus_to_exitcode(self._status)
        try:
            info = os.waitid(os.P_PID, self.pid,
                             os.WEXITED | os.WNOHANG | os.WNOWAIT)
        except ChildProcessError:
            return 0
        if info is None or info.si_pid == 0:
            return None
        return info.si_status

    def wait(self, timeout: float) -> int:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.poll() is not None:
                _pid, self._status = os.waitpid(self.pid, 0)
                return os.waitstatus_to_exitcode(self._status)
            time.sleep(0.005)
        raise TimeoutError("broker wait timeout")


def _spawn(command: tuple[str, ...], execution: float,
           cleanup: float) -> tuple[_ForkProcess, int]:
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(read_fd)
            os.setsid()
            code = _broker(write_fd, command, execution, cleanup)
        except BaseException:
            code = 2
        os._exit(code)
    os.close(write_fd)
    os.set_blocking(read_fd, False)
    return _ForkProcess(pid), read_fd


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _stop_group(process: _ForkProcess) -> None:
    for sig, delay in ((signal.SIGTERM, 0.08), (signal.SIGKILL, 0.08)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + delay
        while time.monotonic() < deadline:
            time.sleep(0.005)
    try:
        process.wait(0.5)
    except (ChildProcessError, TimeoutError):
        pass
    deadline = time.monotonic() + 0.5
    while _group_exists(process.pid) and time.monotonic() < deadline:
        time.sleep(0.01)


def _failure(proc: _ForkProcess, reason: str,
             messages: int) -> dict[str, Any]:
    try:
        _stop_group(proc)  # CONNECTED_OUTER_CLEANUP
    except BaseException:
        reason = "outer_cleanup_error"
    return {"status": "fail", "reason": reason, "returncode": proc.poll(),
            "output_bytes": 0, "cleanup_complete": False,
            "messages": messages}


def _decode(line: bytes, expected_seq: int,
            expected_type: str) -> dict[str, Any]:
    if not line or len(line) > MAX_FRAME or line.endswith(b"\r"):
        raise BrokerError("invalid protocol frame")
    try:
        message = json.loads(line)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BrokerError("invalid protocol JSON") from exc
    if type(message) is not dict:
        raise BrokerError("protocol message must be object")
    base = {"v", "seq", "type"}
    allowed = {
        "ready": base,
        "started": base | {"pid"},
        "terminal": base | {"status", "reason", "returncode",
                            "output_bytes", "cleanup_complete"},
    }
    if expected_type not in allowed or set(message) != allowed[expected_type]:
        raise BrokerError("protocol fields mismatch")
    if (message["v"] != VERSION or type(message["seq"]) is not int
            or message["seq"] != expected_seq or message["type"] != expected_type):
        raise BrokerError("protocol order mismatch")
    if expected_type == "started" and (type(message["pid"]) is not int
                                        or message["pid"] <= 0):
        raise BrokerError("invalid started pid")
    if expected_type == "terminal":
        if message["status"] not in ("pass", "fail"):
            raise BrokerError("invalid terminal status")
        if type(message["reason"]) is not str or not message["reason"]:
            raise BrokerError("invalid terminal reason")
        if message["returncode"] is not None and type(message["returncode"]) is not int:
            raise BrokerError("invalid return code")
        if type(message["output_bytes"]) is not int or message["output_bytes"] < 0:
            raise BrokerError("invalid output count")
        if type(message["cleanup_complete"]) is not bool:
            raise BrokerError("invalid cleanup result")
    return message


def supervise(command: Any, *, execution_timeout: Any = 30.0,
              cleanup_timeout: Any = 2.0) -> dict[str, Any]:
    if not sys.platform.startswith("linux"):
        raise RuntimeError("broker supervisor requires Linux")
    checked = _command(command)
    execution = _number(execution_timeout, "execution_timeout", MAX_EXECUTION)
    cleanup = _number(cleanup_timeout, "cleanup_timeout", MAX_CLEANUP)
    process, read_fd = _spawn(checked, execution, cleanup)
    selector = selectors.DefaultSelector()
    selector.register(read_fd, selectors.EVENT_READ)
    buffer = bytearray()
    total = 0
    expected = ["ready", "started", "terminal"]
    messages = 0
    deadline = time.monotonic() + execution + cleanup + 1.0
    try:
        while time.monotonic() < deadline:
            events = selector.select(0.02)
            for _key, _mask in events:
                chunk = os.read(read_fd, min(4096, MAX_STREAM + 1 - total))
                if not chunk:
                    for _attempt in range(10):
                        if process.poll() is not None:
                            break
                        time.sleep(0.005)
                    reason = "broker_lost" if process.poll() is not None else "protocol_error"
                    return _failure(process, reason, messages)
                total += len(chunk)
                if total > MAX_STREAM:
                    return _failure(process, "protocol_error", messages)
                buffer.extend(chunk)
                while b"\n" in buffer:
                    line, _, rest = buffer.partition(b"\n")
                    buffer[:] = rest
                    if messages >= len(expected):
                        return _failure(process, "protocol_error", messages)
                    try:
                        message = _decode(bytes(line), messages + 1,
                                          expected[messages])
                    except BrokerError:
                        return _failure(process, "protocol_error", messages)
                    messages += 1
                    if message["type"] == "terminal":
                        if buffer:
                            return _failure(process, "protocol_error", messages)
                        if not message["cleanup_complete"]:
                            _stop_group(process)
                        else:
                            try:
                                process.wait(0.5)
                            except TimeoutError:
                                return _failure(process, "broker_lost", messages)
                        return {key: message[key] for key in (
                            "status", "reason", "returncode", "output_bytes",
                            "cleanup_complete"
                        )} | {"messages": messages}
            if process.poll() is not None and not events:
                return _failure(process, "broker_lost", messages)
        return _failure(process, "outer_timeout", messages)
    finally:
        selector.close()
        os.close(read_fd)
