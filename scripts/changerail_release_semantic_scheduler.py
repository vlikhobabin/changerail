#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import (
    FIRST_COMPLETED,
    Future,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    wait,
)
from dataclasses import dataclass
import json
import math
import multiprocessing
import os
from pathlib import Path
import threading
from typing import Any, Callable

from changerail_release_child_broker import supervise as _broker_supervise

VERSION = "changerail.release-semantic-scheduler.v1"
AUTHORIZATION = {
    "authorization_card": "openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md",
    "authorization_id": "authorize-bounded-release-semantic-scheduler-v1",
}
MAX_TASKS = 64
MAX_JOBS = 4
MAX_ARGUMENTS = 64
MAX_ARGUMENT_BYTES = 4096
MAX_ID_BYTES = 128
MAX_OUTPUT = 8192
MAX_SUMMARY = 65536
MAX_EXECUTION = 3600.0
MAX_CLEANUP = 60.0
TASK_FIELDS = {"id", "command", "execution_timeout", "cleanup_timeout", "root"}
BROKER_FIELDS = {
    "status", "reason", "returncode", "output_bytes", "cleanup_complete", "messages"
}
RESULT_FIELDS = BROKER_FIELDS | {"id"}
TERMINAL_FAILURES = {
    "child_failed", "output_limit", "execution_timeout",
    "cleanup_incomplete", "internal_error",
}
OUTER_FAILURES = {
    "protocol_error", "broker_lost", "outer_timeout", "outer_cleanup_error",
}
CANCELLED = {"scheduler_cancelled": True}


class SchedulerError(RuntimeError):
    pass


@dataclass(frozen=True)
class _Task:
    identity: str
    command: tuple[str, ...]
    execution_timeout: float
    cleanup_timeout: float
    root: str


def _token(value: Any, name: str) -> str:
    if type(value) is not str or not value or len(value.encode()) > MAX_ID_BYTES:
        raise SchedulerError(f"{name} must be bounded text")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise SchedulerError(f"{name} must be ASCII") from exc
    if not value[0].isalnum() or any(
        not (character.isalnum() or character in "._-") for character in value
    ):
        raise SchedulerError(f"{name} has invalid characters")
    if value in (".", ".."):
        raise SchedulerError(f"{name} is not a direct-child token")
    return value


def _number(value: Any, name: str, maximum: float) -> float:
    if type(value) not in (int, float):
        raise SchedulerError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result) or result <= 0 or result > maximum:
        raise SchedulerError(f"{name} is outside its bound")
    return result


def _command(value: Any) -> tuple[str, ...]:
    if type(value) not in (list, tuple) or not 1 <= len(value) <= MAX_ARGUMENTS:
        raise SchedulerError("command must contain 1..64 arguments")
    result: list[str] = []
    for argument in value:
        if (type(argument) is not str or not argument or "\0" in argument
                or len(argument.encode()) > MAX_ARGUMENT_BYTES):
            raise SchedulerError("command contains an invalid argument")
        result.append(argument)
    return tuple(result)


def _validate_plan(plan: Any, jobs: Any) -> tuple[list[_Task], int]:
    if type(jobs) is not int or not 1 <= jobs <= MAX_JOBS:
        raise SchedulerError("jobs must be an integer from 1 through 4")
    if type(plan) is not list or not 1 <= len(plan) <= MAX_TASKS:
        raise SchedulerError("plan must contain 1..64 tasks")
    tasks: list[_Task] = []
    identities: set[str] = set()
    roots: set[str] = set()
    for raw in plan:
        if type(raw) is not dict or set(raw) != TASK_FIELDS:
            raise SchedulerError("task fields mismatch")
        identity = _token(raw["id"], "task id")
        root = _token(raw["root"], "task root")
        if identity in identities or root in roots:
            raise SchedulerError("task ids and roots must be unique")
        identities.add(identity)
        roots.add(root)
        tasks.append(_Task(
            identity,
            _command(raw["command"]),
            _number(raw["execution_timeout"], "execution_timeout", MAX_EXECUTION),
            _number(raw["cleanup_timeout"], "cleanup_timeout", MAX_CLEANUP),
            root,
        ))
    return tasks, jobs


def _runtime_root(value: Any) -> tuple[Path, bool]:
    if not isinstance(value, (str, os.PathLike)):
        raise SchedulerError("runtime_root must be a path")
    path = Path(value)
    if path.name in ("", ".", ".."):
        raise SchedulerError("runtime_root must name a dedicated directory")
    parent = path.parent.resolve(strict=True)
    target = parent / path.name
    if target.exists():
        if target.is_symlink() or not target.is_dir():
            raise SchedulerError("runtime_root must be a real directory")
        return target.resolve(strict=True), False
    try:
        target.mkdir(mode=0o700)
    except OSError as exc:
        raise SchedulerError("cannot create runtime_root") from exc
    return target.resolve(strict=True), True


def _reserve_roots(tasks: list[_Task], runtime_root: Any) -> Path:
    base, base_created = _runtime_root(runtime_root)
    created: list[Path] = []
    try:
        for task in tasks:
            target = base / task.root
            target.mkdir(mode=0o700)
            if target.resolve(strict=True).parent != base:
                raise SchedulerError("task root escaped runtime_root")
            created.append(target)
    except (OSError, SchedulerError) as exc:
        for target in reversed(created):
            try:
                target.rmdir()
            except OSError:
                pass
        if base_created:
            try:
                base.rmdir()
            except OSError:
                pass
        raise SchedulerError("cannot reserve all task roots") from exc
    return base


def _observe_call(stop: Any, task: _Task,
                  call: Callable[[], Any]) -> Any:
    if stop.is_set():
        return CANCELLED
    try:
        raw = call()
        normalized = _normalize(task.identity, raw)
    except Exception:
        stop.set()
        raise
    if normalized["status"] == "fail":
        stop.set()
    return raw


def _default_call(task: _Task, stop: Any) -> dict[str, Any]:
    return _observe_call(stop, task, lambda: _broker_supervise(
        task.command,
        execution_timeout=task.execution_timeout,
        cleanup_timeout=task.cleanup_timeout,
    ))


def _injected_call(supervisor: Callable[..., Any], task: _Task,
                   stop: Any) -> Any:
    return _observe_call(stop, task, lambda: supervisor(
        task.command,
        execution_timeout=task.execution_timeout,
        cleanup_timeout=task.cleanup_timeout,
    ))


def _bounded_reason(value: Any) -> str:
    if type(value) is not str or not value or len(value.encode()) > 64:
        raise SchedulerError("invalid result reason")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise SchedulerError("invalid result reason") from exc
    if any(not (character.isalnum() or character in "._-") for character in value):
        raise SchedulerError("invalid result reason")
    return value


def _normalize(identity: str, raw: Any) -> dict[str, Any]:
    if type(raw) is not dict or set(raw) != BROKER_FIELDS:
        raise SchedulerError("supervisor result fields mismatch")
    status = raw["status"]
    if status not in ("pass", "fail"):
        raise SchedulerError("invalid result status")
    reason = _bounded_reason(raw["reason"])
    returncode = raw["returncode"]
    if returncode is not None and type(returncode) is not int:
        raise SchedulerError("invalid result returncode")
    output_bytes = raw["output_bytes"]
    messages = raw["messages"]
    if type(output_bytes) is not int or not 0 <= output_bytes <= MAX_OUTPUT + 1:
        raise SchedulerError("invalid result output_bytes")
    if type(messages) is not int or not 0 <= messages <= 3:
        raise SchedulerError("invalid result messages")
    if type(raw["cleanup_complete"]) is not bool:
        raise SchedulerError("invalid result cleanup_complete")
    if status == "pass" and not (
        reason == "completed" and returncode == 0
        and output_bytes <= MAX_OUTPUT
        and raw["cleanup_complete"] is True and messages == 3
    ):
        raise SchedulerError("inconsistent passing result")
    if status == "fail":
        if reason not in TERMINAL_FAILURES | OUTER_FAILURES:
            raise SchedulerError("unknown failure reason")
        if reason in OUTER_FAILURES and not (
            returncode is None or type(returncode) is int
        ):
            raise SchedulerError("invalid outer failure returncode")
        if reason in OUTER_FAILURES and not (
            output_bytes == 0 and raw["cleanup_complete"] is False
            and messages <= 2
        ):
            raise SchedulerError("inconsistent outer failure result")
        if reason in TERMINAL_FAILURES and messages != 3:
            raise SchedulerError("terminal failure must have three messages")
        if reason == "child_failed" and not (
            type(returncode) is int and returncode != 0
            and output_bytes <= MAX_OUTPUT and raw["cleanup_complete"] is True
        ):
            raise SchedulerError("inconsistent child failure result")
        if reason == "execution_timeout" and not (
            type(returncode) is int and output_bytes <= MAX_OUTPUT
            and raw["cleanup_complete"] is True
        ):
            raise SchedulerError("inconsistent timeout result")
        if reason == "output_limit" and not (
            type(returncode) is int and output_bytes == MAX_OUTPUT + 1
            and raw["cleanup_complete"] is True
        ):
            raise SchedulerError("inconsistent output failure result")
        if reason == "cleanup_incomplete" and raw["cleanup_complete"] is not False:
            raise SchedulerError("inconsistent cleanup failure result")
        if reason == "internal_error" and output_bytes > MAX_OUTPUT:
            raise SchedulerError("inconsistent internal failure result")
    return {
        "id": identity,
        "status": status,
        "reason": reason,
        "returncode": returncode,
        "output_bytes": output_bytes,
        "cleanup_complete": raw["cleanup_complete"],
        "messages": messages,
    }


def _synthetic(identity: str, reason: str) -> dict[str, Any]:
    return {
        "id": identity,
        "status": "fail",
        "reason": reason,
        "returncode": None,
        "output_bytes": 0,
        "cleanup_complete": reason == "cancelled",
        "messages": 0,
    }


def _future_result(future: Future[Any], task: _Task) -> dict[str, Any]:
    try:
        raw = future.result()
    except SchedulerError:
        return _synthetic(task.identity, "supervisor_result_error")
    except Exception:
        return _synthetic(task.identity, "supervisor_error")
    if raw == CANCELLED:
        return _synthetic(task.identity, "cancelled")
    try:
        return _normalize(task.identity, raw)
    except SchedulerError:
        return _synthetic(task.identity, "supervisor_result_error")


def _execute(tasks: list[_Task], jobs: int,
             supervisor: Callable[..., Any] | None) -> list[dict[str, Any]]:
    results: list[dict[str, Any] | None] = [None] * len(tasks)
    manager = None
    executor = None
    try:
        if supervisor is None:
            context = multiprocessing.get_context("spawn")
            manager = context.Manager()
            stop = manager.Event()
            executor = ProcessPoolExecutor(max_workers=jobs, mp_context=context)
            submit = lambda item: executor.submit(_default_call, item, stop)  # noqa: E731
        else:
            stop = threading.Event()
            executor = ThreadPoolExecutor(max_workers=jobs)
            submit = lambda item: executor.submit(_injected_call, supervisor, item, stop)  # noqa: E731
    except Exception:
        if manager is not None:
            try:
                manager.shutdown()
            except Exception:
                pass
        return [_synthetic(tasks[0].identity, "executor_error")] + [
            _synthetic(task.identity, "cancelled") for task in tasks[1:]
        ]
    active: dict[Future[Any], int] = {}
    next_index = 0
    failed = False

    def start(index: int) -> bool:
        nonlocal failed
        try:
            active[submit(tasks[index])] = index
            return True
        except Exception:
            stop.set()
            results[index] = _synthetic(tasks[index].identity, "executor_error")
            failed = True
            return False

    try:
        while next_index < len(tasks) and len(active) < jobs:
            started = start(next_index)
            next_index += 1
            if not started:
                break
        while active:
            completed, _pending = wait(active, return_when=FIRST_COMPLETED)
            for future in sorted(completed, key=lambda item: active[item]):
                index = active.pop(future)
                result = _future_result(future, tasks[index])
                results[index] = result
                failed = failed or result["status"] == "fail"
                if failed:
                    stop.set()
            while not failed and next_index < len(tasks) and len(active) < jobs:
                started = start(next_index)
                next_index += 1
                if not started:
                    break
        if failed:
            for index in range(next_index, len(tasks)):
                results[index] = _synthetic(tasks[index].identity, "cancelled")
    except Exception:
        stop.set()
        failed = True
        unresolved = [index for index, result in enumerate(results)
                      if result is None]
        if unresolved:
            results[unresolved[0]] = _synthetic(
                tasks[unresolved[0]].identity, "executor_error")
            for index in unresolved[1:]:
                results[index] = _synthetic(tasks[index].identity, "cancelled")
    finally:
        try:
            executor.shutdown(wait=True, cancel_futures=True)
        except Exception:
            failed = True
            results[0] = _synthetic(tasks[0].identity, "executor_error")
        if manager is not None:
            try:
                manager.shutdown()
            except Exception:
                results[0] = _synthetic(tasks[0].identity, "executor_error")
    unresolved = [index for index, result in enumerate(results) if result is None]
    if unresolved:
        results[unresolved[0]] = _synthetic(
            tasks[unresolved[0]].identity, "executor_error")
        for index in unresolved[1:]:
            results[index] = _synthetic(tasks[index].identity, "cancelled")
    return [result for result in results if result is not None]


def run_plan(plan: Any, runtime_root: Any, *, jobs: Any = 4,
             supervisor: Callable[..., Any] | None = None) -> dict[str, Any]:
    tasks, checked_jobs = _validate_plan(plan, jobs)
    _reserve_roots(tasks, runtime_root)
    results = _execute(tasks, checked_jobs, supervisor)
    summary = {
        "version": VERSION,
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "jobs": checked_jobs,
        "results": results,
    }
    try:
        raw = json.dumps(summary, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise SchedulerError("scheduler summary is not canonical JSON") from exc
    if len(raw) > MAX_SUMMARY:
        raise SchedulerError("scheduler summary exceeds bound")
    return summary
