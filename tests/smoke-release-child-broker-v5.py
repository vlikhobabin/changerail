#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "changerail_release_child_broker.py"
PYTHON = sys.executable


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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


def alive(pid: int) -> bool:
    try:
        Path(f"/proc/{pid}/stat").read_bytes()
    except (FileNotFoundError, ProcessLookupError):
        return False
    return True


def wait_dead(pid: int, timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not alive(pid):
            return True
        time.sleep(0.02)
    return not alive(pid)


def marker_pid(path: Path) -> int:
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline:
        if path.exists() and path.read_text().strip():
            return int(path.read_text().strip())
        time.sleep(0.01)
    raise AssertionError(f"missing pid marker: {path}")


def supervise(module: ModuleType, code: str, *, execution: float = 0.25,
              cleanup: float = 0.75, args: tuple[str, ...] = ()) -> dict:
    result = module.supervise(
        [PYTHON, "-c", code, *args],
        execution_timeout=execution,
        cleanup_timeout=cleanup,
    )
    require(type(result) is dict, "supervise result must be a dict")
    json.dumps(result, allow_nan=False)
    return result


def mutate(source: str, old: str, new: str, target: Path) -> None:
    require(source.count(old) == 1, f"mutation target must be unique: {old}")
    changed = source.replace(old, new)
    require(changed != source and old not in changed, "mutation must be effective")
    target.write_text(changed)


def check_normal_and_bounds(module: ModuleType) -> None:
    normal = supervise(module, "print('ok')", execution=1.0)
    require(normal["status"] == "pass", f"normal child failed: {normal}")
    exact = supervise(module, "import os; os.write(1, b'x' * 8192)", execution=1.0)
    require(exact["status"] == "pass" and exact["output_bytes"] == 8192,
            f"exact output bound failed: {exact}")
    over = supervise(module, "import os; os.write(1, b'x' * 8193)", execution=1.0)
    require(over["status"] == "fail" and over["reason"] == "output_limit",
            f"output overflow did not fail closed: {over}")
    eof = supervise(module, "import os,time; os.close(1); os.close(2); time.sleep(5)")
    require(eof["status"] == "fail" and eof["reason"] == "execution_timeout",
            f"pipe EOF manufactured completion: {eof}")


def check_protocol_faults(module: ModuleType) -> None:
    for fault in ("malformed", "duplicate", "eof"):
        with environment(CHANGERAIL_BROKER_PROTOCOL_FAULT=fault):
            result = supervise(module, "pass", execution=1.0)
        require(result["status"] == "fail" and result["reason"] == "protocol_error",
                f"protocol fault {fault} did not fail closed: {result}")


def fatal_scenario(module: ModuleType, directory: Path) -> tuple[dict, int]:
    marker = directory / f"fatal-{time.monotonic_ns()}.pid"
    code = (
        "import os,sys,time; p=sys.argv[1]; "
        "open(p,'w').write(str(os.getpid())); time.sleep(30)"
    )
    with environment(
        CHANGERAIL_BROKER_HARD_EXIT_AFTER_START="1",
        CHANGERAIL_BROKER_TARGET_MARKER=str(marker),
    ):
        result = supervise(module, code, execution=1.0, args=(str(marker),))
    return result, marker_pid(marker)


def check_connected_outer_cleanup(module: ModuleType, source: str,
                                  directory: Path) -> None:
    canonical, canonical_pid = fatal_scenario(module, directory)
    require(canonical["status"] == "fail" and canonical["reason"] == "broker_lost",
            f"fatal broker loss did not fail closed: {canonical}")
    require(wait_dead(canonical_pid), "canonical public supervise left target alive")

    mutated_path = directory / "broker_without_outer_cleanup.py"
    mutate(
        source,
        "        _stop_group(proc)  # CONNECTED_OUTER_CLEANUP",
        "        pass  # CONNECTED_OUTER_CLEANUP_REMOVED",
        mutated_path,
    )
    mutated = load(mutated_path, "broker_without_outer_cleanup")
    counterfactual, survivor = fatal_scenario(mutated, directory)
    require(counterfactual["status"] == "fail", "mutated broker loss must fail")
    require(alive(survivor), "cleanup-removal mutation did not expose survivor")
    os.kill(survivor, signal.SIGKILL)
    require(wait_dead(survivor), "test cleanup could not remove mutation survivor")


def pidfd_scenario(module: ModuleType, pid_marker: Path,
                   pidfd_marker: Path) -> dict:
    real_kill = os.kill
    real_pidfd = signal.pidfd_send_signal

    def forbidden_pid_kill(pid: int, sig: int) -> None:
        pid_marker.write_text(f"{pid}:{sig}")
        raise RuntimeError("PID-only signal backend used")

    def observed_pidfd(fd: int, sig: int, siginfo=None, flags: int = 0) -> None:
        pidfd_marker.write_text(f"{fd}:{sig}")
        real_pidfd(fd, sig, siginfo, flags)

    module.os.kill = forbidden_pid_kill
    module.signal.pidfd_send_signal = observed_pidfd
    try:
        return supervise(
            module,
            "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)",
            execution=0.12,
            cleanup=0.8,
        )
    finally:
        module.os.kill = real_kill
        module.signal.pidfd_send_signal = real_pidfd


def check_connected_pidfd(module: ModuleType, source: str, directory: Path) -> None:
    canonical_marker = directory / "canonical-pid-only"
    canonical_pidfd = directory / "canonical-pidfd"
    canonical = pidfd_scenario(module, canonical_marker, canonical_pidfd)
    require(canonical["status"] == "fail" and canonical["reason"] == "execution_timeout",
            f"canonical timeout result is wrong: {canonical}")
    require(not canonical_marker.exists(), "canonical path used PID-only signaling")
    require(canonical_pidfd.exists(), "canonical path did not reach pidfd signaling")
    require(canonical["cleanup_complete"] is True, "canonical pidfd cleanup incomplete")

    mutated_path = directory / "broker_with_pid_only_signal.py"
    mutate(
        source,
        "        signal.pidfd_send_signal(fd, sig)  # CONNECTED_PIDFD_SIGNAL",
        "        os.kill(pid, sig)  # CONNECTED_PIDFD_SIGNAL_MUTATED",
        mutated_path,
    )
    mutated = load(mutated_path, "broker_with_pid_only_signal")
    mutation_marker = directory / "mutated-pid-only"
    mutation_pidfd = directory / "mutated-pidfd"
    counterfactual = pidfd_scenario(mutated, mutation_marker, mutation_pidfd)
    require(mutation_marker.exists(), "pidfd mutation never reached signaling")
    require(not mutation_pidfd.exists(), "mutated path still used pidfd signaling")
    require(counterfactual["status"] == "fail" and not counterfactual["cleanup_complete"],
            f"PID-only mutation did not turn connected proof red: {counterfactual}")


def check_detached_cleanup(module: ModuleType, directory: Path) -> None:
    marker = directory / "detached.pid"
    code = (
        "import os,sys,time; p=sys.argv[1]; child=os.fork(); "
        "(os.setsid(), open(p,'w').write(str(os.getpid())), time.sleep(30)) "
        "if child==0 else time.sleep(30)"
    )
    result = supervise(module, code, execution=0.15, cleanup=0.9,
                       args=(str(marker),))
    pid = marker_pid(marker)
    require(result["status"] == "fail" and result["cleanup_complete"] is True,
            f"detached cleanup failed: {result}")
    require(wait_dead(pid), "detached target descendant survived")


def check_dormancy() -> None:
    needle = "changerail_release_child_broker"
    for path in (
        ROOT / "scripts" / "run-release-baseline.py",
        ROOT / "scripts" / "smoke-release-ci.py",
        ROOT / ".github" / "workflows" / "changerail-ci.yml",
    ):
        require(needle not in path.read_text(), f"premature activation in {path}")


def main() -> int:
    require(sys.platform.startswith("linux"), "v5 smoke requires Linux")
    source = SOURCE.read_text()
    module = load(SOURCE, "changerail_release_child_broker_v5")
    with tempfile.TemporaryDirectory(prefix="changerail-broker-v5-") as raw:
        directory = Path(raw)
        check_normal_and_bounds(module)
        check_protocol_faults(module)
        check_connected_outer_cleanup(module, source, directory)
        check_connected_pidfd(module, source, directory)
        check_detached_cleanup(module, directory)
        check_dormancy()
    print(json.dumps({"status": "pass", "checks": 6}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
