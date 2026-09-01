#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import multiprocessing
import os
import re
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "smoke-verify-project.py"
SPEC = importlib.util.spec_from_file_location("smoke_verify_project", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
SMOKE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SMOKE
SPEC.loader.exec_module(SMOKE)


def assert_clean(run_dir: Path) -> None:
    leftovers = sorted(path.name for path in run_dir.glob(".workers-*"))
    if leftovers:
        raise AssertionError(f"controller temporary roots leaked: {leftovers}")


def run_success(*, faults: dict[int, str] | None = None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="verify-project-controller-test-") as raw_root:
        run_dir = Path(raw_root)
        before = {process.pid for process in multiprocessing.active_children()}
        report = SMOKE.run_smoke(
            ROOT,
            run_dir,
            _worker_timeout=2.0,
            _test_faults=faults,
            _test_synthetic=True,
        )
        assert_clean(run_dir)
        after = {process.pid for process in multiprocessing.active_children()}
        if after != before:
            raise AssertionError(f"worker processes were not reaped: before={before} after={after}")
        return report


def expect_protocol_error(label: str, fault: str, needle: str, *, timeout: float = 2.0) -> None:
    with tempfile.TemporaryDirectory(prefix=f"verify-project-{label}-") as raw_root:
        run_dir = Path(raw_root)
        started = time.monotonic()
        try:
            SMOKE.run_smoke(
                ROOT,
                run_dir,
                _worker_timeout=timeout,
                _test_faults={0: fault},
                _test_synthetic=True,
            )
        except SMOKE.WorkerProtocolError as exc:
            if needle not in str(exc):
                raise AssertionError(f"{label}: missing diagnostic {needle!r}: {exc}") from exc
        else:
            raise AssertionError(f"{label}: controller unexpectedly passed")
        elapsed = time.monotonic() - started
        if elapsed > max(3.0, timeout + 2.0):
            raise AssertionError(f"{label}: failure was not bounded ({elapsed:.3f}s)")
        assert_clean(run_dir)


def main() -> int:
    expected_names = tuple(name for shard in SMOKE.SHARD_SCENARIOS for name in shard)
    if len(SMOKE.SHARD_SCENARIOS) != 2 or tuple(map(len, SMOKE.SHARD_SCENARIOS)) != (39, 30):
        raise AssertionError("frozen inventory is not exactly two shards of 39 and 30")
    if len(expected_names) != 69 or len(set(expected_names)) != 69:
        raise AssertionError("frozen inventory is not 69 unique scenarios")

    parity = run_success()
    parity_names = tuple(check["name"] for check in parity["checks"])
    if parity_names != expected_names or parity["summary"] != {
        "status": "pass",
        "total": 69,
        "passed": 69,
        "failed": 0,
    }:
        raise AssertionError("full-set parity failed")
    if SMOKE.report_exit_code(parity) != 0:
        raise AssertionError("passing parity report produced non-zero exit")

    delayed = run_success(faults={0: "delay"})
    if tuple(check["name"] for check in delayed["checks"]) != expected_names:
        raise AssertionError("completion order changed deterministic scenario order")
    stable_parity = json.dumps(
        [(check["name"], check["status"]) for check in parity["checks"]],
        ensure_ascii=True,
    )
    stable_delayed = json.dumps(
        [(check["name"], check["status"]) for check in delayed["checks"]],
        ensure_ascii=True,
    )
    if stable_parity != stable_delayed:
        raise AssertionError("deterministic aggregate changed when completion order reversed")

    root_pid_pattern = re.compile(r"^test-only root=(.*);pid=(\d+)$")
    worker_samples = (parity["checks"][0]["message"], parity["checks"][39]["message"])
    roots: list[Path] = []
    pids: list[int] = []
    for sample in worker_samples:
        match = root_pid_pattern.fullmatch(sample)
        if match is None:
            raise AssertionError(f"malformed isolation marker: {sample}")
        roots.append(Path(match.group(1)))
        pids.append(int(match.group(2)))
    if roots[0] == roots[1] or pids[0] == pids[1]:
        raise AssertionError(f"workers shared fixture/process identity: roots={roots} pids={pids}")
    if any(root.exists() for root in roots):
        raise AssertionError(f"worker fixture roots were not cleaned: {roots}")
    for pid in pids:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        raise AssertionError(f"worker process was not reaped: pid={pid}")

    failure = run_success(faults={0: "scenario-failure"})
    if failure["summary"]["failed"] != 1 or SMOKE.report_exit_code(failure) != 1:
        raise AssertionError("single scenario failure did not propagate to exit code")

    expect_protocol_error("exception", "exception", "child exception")
    expect_protocol_error("crash", "crash", "child crash exit=86")
    expect_protocol_error("timeout", "timeout", "timeout after", timeout=0.1)
    expect_protocol_error("missing", "missing", "missing terminal result")
    expect_protocol_error("duplicate", "duplicate", "duplicate terminal results")
    expect_protocol_error("malformed", "malformed", "malformed terminal report")

    print("PASS verify-project sharding: 69-scenario parity, deterministic order, fail-closed faults, isolation, cleanup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
