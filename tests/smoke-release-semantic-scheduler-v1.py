#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def task(identity: str, *, root: str | None = None,
         code: str = "pass", execution: float = 1.0,
         cleanup: float = 1.0) -> dict:
    return {
        "id": identity,
        "command": [sys.executable, "-c", code],
        "execution_timeout": execution,
        "cleanup_timeout": cleanup,
        "root": root or identity,
    }


def passed(delay: float = 0.0) -> dict:
    if delay:
        time.sleep(delay)
    return {
        "status": "pass", "reason": "completed", "returncode": 0,
        "output_bytes": 0, "cleanup_complete": True, "messages": 3,
    }


def failed(reason: str = "child_failed") -> dict:
    return {
        "status": "fail", "reason": reason, "returncode": 1,
        "output_bytes": 0, "cleanup_complete": True, "messages": 3,
    }


def wait_dead(pid: int, timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not Path(f"/proc/{pid}").exists():
            return True
        time.sleep(0.02)
    return not Path(f"/proc/{pid}").exists()


@contextlib.contextmanager
def environment(**values: str | None):
    old = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def expect_invalid(module, plan, root: Path, *, jobs: object = 1) -> None:
    calls: list[tuple] = []

    def supervisor(command, **kwargs):
        calls.append(tuple(command))
        return passed()

    try:
        module.run_plan(plan, root, jobs=jobs, supervisor=supervisor)
    except module.SchedulerError:
        pass
    else:
        raise AssertionError(f"invalid plan passed: {plan!r}, jobs={jobs!r}")
    require(not calls, "invalid plan launched supervisor")


def check_validation_and_roots(module, directory: Path) -> None:
    expect_invalid(module, [], directory)
    expect_invalid(module, [task(str(index)) for index in range(65)], directory)
    for jobs in (True, 0, 5, 1.0, math.nan):
        expect_invalid(module, [task("one")], directory, jobs=jobs)
    invalid = [
        [task("dup"), task("dup", root="other")],
        [task("one", root="same"), task("two", root="same")],
        [task("../bad")], [task("one", root="../bad")],
        [task("one") | {"extra": 1}],
        [task("one") | {"command": []}],
        [task("one") | {"command": ["a\0b"]}],
        [task("one") | {"execution_timeout": float("inf")}],
        [task("one") | {"cleanup_timeout": 61.0}],
    ]
    for index, plan in enumerate(invalid):
        with tempfile.TemporaryDirectory(dir=directory, prefix=f"invalid-{index}-") as raw:
            expect_invalid(module, plan, Path(raw))

    collision_root = directory / "collision"
    collision_root.mkdir()
    (collision_root / "occupied").mkdir()
    expect_invalid(module, [task("one", root="fresh"),
                            task("two", root="occupied")], collision_root)
    require(not (collision_root / "fresh").exists(),
            "failed reservation left its empty root")
    exact = module.run_plan([task(f"bound-{index}") for index in range(64)],
                            directory / "exact-64", jobs=4,
                            supervisor=lambda _command, **_kwargs: passed())
    require(len(exact["results"]) == 64 and exact["status"] == "pass",
            "exact 64-task boundary failed")


def check_jobs_order_exact_once(module, directory: Path) -> None:
    plan = [task(f"case-{index}") for index in range(8)]

    def execute(jobs: int, root: Path) -> tuple[dict, list[str]]:
        calls: list[str] = []
        lock = threading.Lock()

        def supervisor(command, **_kwargs):
            identity = Path(command[-1]).name if command[-1].startswith("case-") else ""
            # Task ID is added as a harmless final command argument below.
            identity = command[-1]
            with lock:
                calls.append(identity)
            return passed((7 - int(identity.rsplit("-", 1)[1])) * 0.002)

        tagged = [item | {"command": item["command"] + [item["id"]]} for item in plan]
        return module.run_plan(tagged, root, jobs=jobs, supervisor=supervisor), calls

    serial, serial_calls = execute(1, directory / "serial")
    parallel, parallel_calls = execute(4, directory / "parallel")
    expected = [item["id"] for item in plan]
    require([item["id"] for item in serial["results"]] == expected,
            "serial result order drifted")
    require([item["id"] for item in parallel["results"]] == expected,
            "parallel result order followed completion")
    require(sorted(serial_calls) == expected and sorted(parallel_calls) == expected,
            "task did not execute exactly once")
    require(serial["status"] == parallel["status"] == "pass", "jobs parity failed")
    require(all((directory / "parallel" / item).is_dir() for item in expected),
            "scheduler did not reserve every task root")
    for result in parallel["results"]:
        require(set(result) == module.RESULT_FIELDS, "result fields are not closed")
    raw = json.dumps(parallel, allow_nan=False, separators=(",", ":")).encode()
    require(len(raw) <= module.MAX_SUMMARY and b"stdout" not in raw and b"stderr" not in raw,
            "summary bound/raw-output contract failed")


def check_failure_cancellation(module, directory: Path) -> None:
    plan = [task(f"stop-{index}") | {"command": ["fake", str(index)]}
            for index in range(6)]
    calls: list[str] = []

    def supervisor(command, **_kwargs):
        calls.append(command[-1])
        return failed() if command[-1] == "0" else passed()

    result = module.run_plan(plan, directory / "cancel", jobs=1,
                             supervisor=supervisor)
    require(calls == ["0"], f"pending tasks launched after failure: {calls}")
    require(result["status"] == "fail", "failure manufactured pass")
    require([item["reason"] for item in result["results"]] ==
            ["child_failed"] + ["cancelled"] * 5,
            "cancelled results are not deterministic")

    for name, value in (
        ("exception", RuntimeError("boom")),
        ("malformed", {"status": "pass"}),
    ):
        seen = 0

        def broken(_command, **_kwargs):
            nonlocal seen
            seen += 1
            if isinstance(value, BaseException):
                raise value
            return value

        result = module.run_plan([task(f"{name}-0"), task(f"{name}-1")],
                                 directory / name, jobs=1, supervisor=broken)
        require(seen == 1 and result["status"] == "fail",
                f"{name} did not stop new work")
        require(result["results"][1]["reason"] == "cancelled",
                f"{name} missing cancellation result")


def check_parallel_stop_and_result_table(module, directory: Path) -> None:
    real_executor = module.ThreadPoolExecutor
    calls: list[str] = []

    def one_worker_executor(*, max_workers):
        require(max_workers == 4, "scheduler did not request jobs=4")
        return real_executor(max_workers=1)

    def supervisor(command, **_kwargs):
        calls.append(command[-1])
        return failed() if command[-1] == "0" else passed()

    module.ThreadPoolExecutor = one_worker_executor
    try:
        plan = [task(f"parallel-stop-{index}") |
                {"command": ["fake", str(index)]} for index in range(6)]
        result = module.run_plan(plan, directory / "parallel-stop", jobs=4,
                                 supervisor=supervisor)
    finally:
        module.ThreadPoolExecutor = real_executor
    require(calls == ["0"], f"queued wrappers bypassed stop event: {calls}")
    require([item["reason"] for item in result["results"]] ==
            ["child_failed"] + ["cancelled"] * 5,
            "parallel cancellation results drifted")

    invalid_results = [
        failed("unknown_failure"),
        failed() | {"reason": "completed", "returncode": 0},
        failed("output_limit") | {"output_bytes": 8193, "messages": 0},
        failed("protocol_error") | {"output_bytes": 8193, "messages": 0,
                                    "cleanup_complete": False},
        failed("internal_error") | {"output_bytes": 8193},
    ]
    for index, invalid in enumerate(invalid_results):
        seen = 0

        def malformed(_command, **_kwargs):
            nonlocal seen
            seen += 1
            return invalid

        result = module.run_plan(
            [task(f"invalid-result-{index}-0"), task(f"invalid-result-{index}-1")],
            directory / f"invalid-result-{index}", jobs=1, supervisor=malformed)
        require(seen == 1, "malformed result did not stop pending work")
        require([item["reason"] for item in result["results"]] ==
                ["supervisor_result_error", "cancelled"],
                f"malformed failure state passed: {invalid}")


def check_executor_faults(module, directory: Path) -> None:
    real_executor = module.ThreadPoolExecutor
    real_wait = module.wait
    calls: list[tuple[str, ...]] = []

    def supervisor(command, **_kwargs):
        calls.append(tuple(command))
        return passed()

    class ConstructorFault:
        def __init__(self, **_kwargs):
            raise RuntimeError("constructor fault")

    class SubmitFault:
        def __init__(self, **_kwargs):
            pass

        def submit(self, *_args):
            raise RuntimeError("submit fault")

        def shutdown(self, **_kwargs):
            pass

    class ShutdownFault:
        def __init__(self, **_kwargs):
            self.inner = real_executor(max_workers=1)

        def submit(self, *args):
            return self.inner.submit(*args)

        def shutdown(self, **kwargs):
            self.inner.shutdown(**kwargs)
            raise RuntimeError("shutdown fault")

    plan = [task("executor-0"), task("executor-1")]
    for name, executor, expected_calls in (
        ("constructor", ConstructorFault, 0),
        ("submit", SubmitFault, 0),
        ("shutdown", ShutdownFault, 2),
    ):
        calls.clear()
        module.ThreadPoolExecutor = executor
        try:
            result = module.run_plan(plan, directory / f"executor-{name}",
                                     jobs=1, supervisor=supervisor)
        finally:
            module.ThreadPoolExecutor = real_executor
        require(len(calls) == expected_calls, f"{name} fault call count drifted")
        require(len(result["results"]) == 2 and result["status"] == "fail",
                f"{name} fault escaped total ordered result")
        require(result["results"][0]["reason"] == "executor_error",
                f"{name} fault lost executor failure")

    calls.clear()
    module.wait = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        RuntimeError("wait fault"))
    try:
        result = module.run_plan(plan, directory / "executor-wait", jobs=1,
                                 supervisor=supervisor)
    finally:
        module.wait = real_wait
    require(len(result["results"]) == 2 and result["status"] == "fail",
            "wait fault escaped total ordered result")
    require([item["reason"] for item in result["results"]] ==
            ["executor_error", "cancelled"], "wait fault result drifted")


def real_plan(module, directory: Path, identity: str, code: str,
              *, execution: float = 1.0, cleanup: float = 1.0) -> dict:
    return module.run_plan([task(identity, code=code, execution=execution,
                                 cleanup=cleanup)], directory, jobs=1)


def check_real_broker(module, directory: Path) -> None:
    normal = real_plan(module, directory / "normal", "normal", "print('ok')")
    require(normal["status"] == "pass", f"real broker normal failed: {normal}")
    parallel_plan = [task(f"real-{index}", code=f"print({index})")
                     for index in range(4)]
    parallel = module.run_plan(parallel_plan, directory / "real-parallel", jobs=4)
    require(parallel["status"] == "pass" and
            [item["id"] for item in parallel["results"]] ==
            [item["id"] for item in parallel_plan],
            f"real jobs=4 path failed: {parallel}")
    over = real_plan(module, directory / "over", "over",
                     "import os; os.write(1, b'x' * 8193)")
    require(over["results"][0]["reason"] == "output_limit",
            f"output overflow escaped: {over}")
    timeout = real_plan(module, directory / "timeout", "timeout",
                        "import time; time.sleep(30)", execution=0.12)
    require(timeout["results"][0]["reason"] == "execution_timeout",
            f"timeout escaped: {timeout}")
    with environment(CHANGERAIL_BROKER_PROTOCOL_FAULT="malformed"):
        malformed = real_plan(module, directory / "protocol", "protocol", "pass")
    require(malformed["results"][0]["reason"] == "protocol_error",
            f"protocol fault escaped: {malformed}")

    marker = directory / "descendant.pid"
    code = (
        "import os,sys,time; child=os.fork(); "
        "(os.setsid(), open(sys.argv[1],'w').write(str(os.getpid())), time.sleep(30)) "
        "if child==0 else time.sleep(30)"
    )
    plan = [task("descendant", code=code, execution=0.12, cleanup=0.9) |
            {"command": [sys.executable, "-c", code, str(marker)]}]
    result = module.run_plan(plan, directory / "descendant-root", jobs=1)
    deadline = time.monotonic() + 1.0
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    require(marker.exists(), "descendant fixture did not start")
    pid = int(marker.read_text())
    require(result["status"] == "fail" and result["results"][0]["cleanup_complete"],
            f"descendant cleanup result failed: {result}")
    require(wait_dead(pid), "real broker descendant survived scheduler return")


def check_dormancy() -> None:
    token = "changerail_release_semantic_scheduler"
    output = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    allowed = {"tests/smoke-release-semantic-scheduler-v1.py"}
    for relative in output.stdout.splitlines():
        path = ROOT / relative
        if relative in allowed or not path.is_file():
            continue
        if path.suffix not in {".py", ".yml", ".yaml"} and not relative.startswith("bin/"):
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        require(token not in text, f"premature scheduler activation in {relative}")


def main() -> int:
    module = importlib.import_module("changerail_release_semantic_scheduler")
    require(module.AUTHORIZATION == {
        "authorization_card": "openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md",
        "authorization_id": "authorize-bounded-release-semantic-scheduler-v1",
    }, "authorization reference drift")
    with tempfile.TemporaryDirectory(prefix="changerail-scheduler-v1-") as raw:
        directory = Path(raw)
        check_validation_and_roots(module, directory)
        check_jobs_order_exact_once(module, directory)
        check_failure_cancellation(module, directory)
        check_parallel_stop_and_result_table(module, directory)
        check_executor_faults(module, directory)
        check_real_broker(module, directory)
        check_dormancy()
    print(json.dumps({"status": "pass", "checks": 7}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
