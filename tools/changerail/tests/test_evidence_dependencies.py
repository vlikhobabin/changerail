"""Local reuse preserves observed executions and refuses invalidated inputs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.changerail.evidence_dependencies import (
    MAX_RECEIPT_BYTES,
    capture_dependency_snapshot,
    create_reuse_receipt,
    selected_dependencies,
    validate_dependency_snapshot,
    validate_reuse_receipt,
)


@pytest.fixture
def case(tmp_path):
    root = tmp_path
    (root / "src").mkdir()
    (root / "src/mod.py").write_text("VALUE = 1\n")
    (root / "tests").mkdir()
    (root / "tests/test_mod.py").write_text("def test_value(): assert True\n")
    run = root / ".runtime/run1"
    (run / "focused-evidence").mkdir(parents=True)
    command = {
        "kind": "argv",
        "argv": [sys.executable, "-m", "pytest", "-v", "tests/test_mod.py"],
    }
    env = {"PATH": "/usr/bin", "API_KEY": "value-never-retained"}
    profile = {
        "evidence": {
            "reuse": "dependencies",
            "checks": [
                {
                    "argv": command["argv"],
                    "dependencies": ["src", "tests"],
                    "kind": "local",
                    "external_state": False,
                },
            ],
        }
    }
    old = {"head_commit": "a" * 40, "payload_fingerprint": "sha256:" + "b" * 64}
    current = {**old, "payload_fingerprint": "sha256:" + "c" * 64}
    source = run / "focused-evidence" / ("1" * 32 + ".json")
    log = source.with_suffix(".log")
    output = b"tests/test_mod.py::test_value PASSED [100%]\n"
    log.write_bytes(output)
    snapshot = capture_dependency_snapshot(
        root, ["src", "tests"], command=command["argv"], environment=env
    )
    item = {
        "schema": "changerail.check-result.v1",
        "state": "terminal",
        "lane": "focused",
        "run_id": run.name,
        "card": "openspec/board/3.inprogress/card.md",
        "attempt_id": source.stem,
        "command_identity": command,
        "before": old,
        "fingerprint": old,
        "verdict": "verified",
        "outcome": "exit",
        "exit_code": 0,
        "duration_seconds": 1.5,
        "started_at": "2026-01-01T00:00:00Z",
        "observed_at": "2026-01-01T00:00:02Z",
        "log": str(log.relative_to(root)),
        "log_size": len(output),
        "log_sha256": hashlib.sha256(output).hexdigest(),
        "dependency_snapshot": snapshot,
    }
    source.write_text(json.dumps(item))

    def reader(path):
        value = json.loads(path.read_text())
        data = (root / value["log"]).read_bytes()
        return value, data, value["fingerprint"] == current

    shared = dict(
        profile=profile,
        command=command,
        environment=env,
        read_source=reader,
        fingerprint=current,
    )
    return root, run, source, log, item, shared


def make_receipt(case):
    root, run, source, _, _, shared = case
    path = run / "focused-evidence" / ("2" * 32 + ".json")
    receipt = create_reuse_receipt(
        root,
        run,
        source,
        receipt_id=path.stem,
        observed_at="2026-01-02T00:00:00Z",
        **shared,
    )
    path.write_text(json.dumps(receipt))
    return path, receipt


def test_default_reruns_and_runtime_or_shell_never_reuses(case):
    *_, shared = case
    command = shared["command"]
    assert selected_dependencies({}, command) is None
    assert selected_dependencies(shared["profile"], command, kind="runtime") is None
    assert selected_dependencies(shared["profile"], command, kind="final") is None
    assert (
        selected_dependencies(
            shared["profile"], {"kind": "shell", "argv": command["argv"]}
        )
        is None
    )
    assert (
        selected_dependencies(shared["profile"], {"kind": "argv", "argv": ["other"]})
        is None
    )


def test_mutable_external_allowlist_refused(case):
    *_, shared = case
    shared["profile"]["evidence"]["checks"][0]["external_state"] = True
    with pytest.raises(ValueError, match="local-only"):
        make_receipt(case)


def test_archive_move_preserves_exact_execution_lineage(case):
    root, run, source, log, original, shared = case
    before = source.read_bytes(), log.read_bytes()
    change = root / "openspec/changes/example"
    change.mkdir(parents=True)
    (change / "tasks.md").write_text("- [x] 1.1 Done\n")
    archive = root / "openspec/changes/archive"
    archive.mkdir()
    change.rename(archive / "2026-01-02-example")
    path, receipt = make_receipt(case)
    item, data, current = validate_reuse_receipt(root, run, path, receipt, **shared)
    assert current and item == original and data == before[1]
    assert (source.read_bytes(), log.read_bytes()) == before
    assert item["fingerprint"] != shared["fingerprint"]
    assert item["attempt_id"] == source.stem
    assert (
        "duration_seconds" not in receipt
        and "exit_code" not in receipt
        and "log" not in receipt
    )
    assert not path.with_suffix(".log").exists()
    assert receipt["source"]["sha256"] == hashlib.sha256(before[0]).hexdigest()


@pytest.mark.parametrize(
    "changed",
    [
        "source",
        "new_source",
        "deleted_source",
        "harness",
        "environment",
        "command",
        "log",
        "record",
        "policy",
    ],
)
def test_every_consumer_revalidates_reuse(case, changed):
    root, run, source, log, _, shared = case
    path, receipt = make_receipt(case)
    if changed == "source":
        (root / "src/mod.py").write_text("VALUE = 2\n")
    elif changed == "new_source":
        (root / "src/new.py").write_text("VALUE = 3\n")
    elif changed == "deleted_source":
        (root / "src/mod.py").unlink()
    elif changed == "harness":
        (root / "tests/conftest.py").write_text("def pytest_configure(config): pass\n")
    elif changed == "environment":
        shared["environment"]["API_KEY"] = "changed"
    elif changed == "command":
        shared["command"] = {
            "kind": "argv",
            "argv": [sys.executable, "-m", "pytest", "--collect-only"],
        }
    elif changed == "log":
        log.write_bytes(b"fake PASSED\n")
    elif changed == "record":
        source.write_text(source.read_text() + "\n")
    elif changed == "policy":
        shared["profile"]["evidence"]["reuse"] = "rerun"
    with pytest.raises(ValueError):
        validate_reuse_receipt(root, run, path, receipt, **shared)


def test_secret_values_are_only_hashed(case):
    *_, item, _ = case
    assert "value-never-retained" not in json.dumps(item)


def test_bytecode_ignored_but_hidden_real_dependencies_are_not(case):
    root, _, _, _, item, shared = case
    cache = root / "src/__pycache__"
    cache.mkdir()
    (cache / "mod.cpython-313.pyc").write_bytes(b"generated")
    validate_dependency_snapshot(
        root,
        item["dependency_snapshot"],
        command=shared["command"]["argv"],
        environment=shared["environment"],
    )
    (cache / "hidden.py").write_text("value = 1")
    with pytest.raises(ValueError, match="changed"):
        make_receipt(case)


def test_symlink_dependency_refused(case):
    root, *_ = case
    (root / "src/link").symlink_to(root / "tests/test_mod.py")
    with pytest.raises(ValueError, match="symlink"):
        make_receipt(case)


@pytest.mark.parametrize(
    "key,value",
    [
        ("verdict", "unconfirmed"),
        ("lane", "final"),
        ("exit_code", 1),
        ("outcome", "interrupted"),
    ],
)
def test_non_success_and_nonfocused_sources_cannot_be_reused(case, key, value):
    _, _, source, _, item, _ = case
    item[key] = value
    source.write_text(json.dumps(item))
    with pytest.raises(ValueError, match="original check"):
        make_receipt(case)


def test_receipt_is_not_reused_recursively(case):
    root, run, _, _, _, shared = case
    path, _ = make_receipt(case)

    def reader(source):
        raise AssertionError(
            "a reuse source must be rejected before invoking its reader"
        )

    shared["read_source"] = reader
    with pytest.raises(ValueError, match="original check"):
        create_reuse_receipt(
            root,
            run,
            path,
            receipt_id="3" * 32,
            observed_at="2026-01-03T00:00:00Z",
            **shared,
        )


@pytest.mark.parametrize("unsafe", ["fifo", "oversized"])
def test_nonregular_and_oversized_originals_refuse_without_blocking(case, unsafe):
    root, run, source, _, _, shared = case
    source.unlink()
    if unsafe == "fifo":
        os.mkfifo(source)
    else:
        with source.open("wb") as stream:
            stream.truncate(MAX_RECEIPT_BYTES + 1)
    arguments = {key: value for key, value in shared.items() if key != "read_source"}
    program = """
import json
import sys
from pathlib import Path
from scripts.changerail.evidence_dependencies import create_reuse_receipt
def forbidden_reader(path):
    raise AssertionError('unsafe source reached the host reader')
args = json.loads(sys.stdin.read())
try:
    create_reuse_receipt(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]),
                         receipt_id='3' * 32, observed_at='2026-01-03T00:00:00Z',
                         read_source=forbidden_reader, **args)
except ValueError as exc:
    assert 'nonregular or oversized' in str(exc), str(exc)
else:
    raise AssertionError('unsafe source accepted')
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(root), str(run), str(source)],
        cwd=Path(__file__).resolve().parents[3],
        input=json.dumps(arguments),
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stdout + result.stderr
