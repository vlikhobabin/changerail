"""Non-Python project parsers retain the same selected-node proof boundary."""

from __future__ import annotations

import os

import pytest

from scripts.changerail.adapters.pytest import _validate_pytest_selected_nodes
from scripts.changerail.adapters.results import receipt_nodes, validate_selected_nodes
from scripts.changerail.contracts import DeliveryError


CUSTOM_PARSER = """
import re
def parse_results(log, command_identity, target):
    if command_identity != {"kind": "argv", "argv": ["node", "--test"]}:
        return {}
    return {m.group("node").decode("utf-8"): (m.start(), m.end())
            for m in re.finditer(rb"(?m)^PASS (?P<node>[^\\r\\n]+)$", log)}
"""


@pytest.fixture
def project(tmp_path):
    module = tmp_path / ".changerail/adapters/test_results.py"
    module.parent.mkdir(parents=True)
    module.write_text(CUSTOM_PARSER)
    profile = {"adapters": {"tests": {"module": str(module.relative_to(tmp_path))}}}
    identity = {"kind": "argv", "argv": ["node", "--test"]}
    item = {
        "state": "terminal",
        "verdict": "verified",
        "outcome": "exit",
        "exit_code": 0,
        "command_identity": identity,
    }
    return tmp_path, module, profile, identity, item


def test_nonpython_parser_selects_only_actual_passing_nodes_with_byte_offsets(project):
    root, _, profile, identity, item = project
    data = "PASS tests/spec.js::test_é\nFAIL tests/spec.js::test_bad\nPASS tests/other.js::test_other\n2 passed\n".encode()
    target = "tests/spec.js"
    selected = receipt_nodes(root, profile, item, data, target)
    assert selected == [
        {"node": "tests/spec.js::test_é", "start": 0, "end": len(data.splitlines()[0])}
    ]
    assert validate_selected_nodes(
        root, profile, data, identity, target, selected, "test proof"
    ) == {
        selected[0]["node"]: (selected[0]["start"], selected[0]["end"]),
    }


def test_default_adapter_preserves_pytest_validation(tmp_path):
    data = b"tests/test_one.py::test_ok PASSED [100%]\n1 passed\n"
    identity = {"kind": "argv", "argv": ["uv", "run", "pytest", "-v"]}
    item = {
        "state": "terminal",
        "verdict": "verified",
        "outcome": "exit",
        "exit_code": 0,
        "command_identity": identity,
    }
    selected = receipt_nodes(tmp_path, {}, item, data, "tests/test_one.py")
    assert selected and validate_selected_nodes(
        tmp_path, {}, data, identity, "tests/test_one.py", selected, "proof"
    ) == _validate_pytest_selected_nodes(
        data,
        identity,
        "tests/test_one.py",
        selected,
        label="proof",
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("state", "running"),
        ("verdict", "unconfirmed"),
        ("outcome", "interrupted"),
        ("exit_code", 1),
    ],
)
def test_failed_or_incomplete_receipt_cannot_supply_nodes(project, field, value):
    root, _, profile, _, item = project
    item[field] = value
    assert (
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )
        == []
    )


@pytest.mark.parametrize(
    "data",
    [
        b"FAIL tests/spec.js::test_bad\n",
        b"1 passed\n",
        b"PASS tests/other.js::test_ok\n",
    ],
)
def test_failed_aggregate_or_unselected_logs_cannot_be_proofs(project, data):
    root, _, profile, identity, item = project
    assert receipt_nodes(root, profile, item, data, "tests/spec.js") == []
    with pytest.raises(DeliveryError, match="selected-node"):
        validate_selected_nodes(
            root, profile, data, identity, "tests/spec.js", [], "proof"
        )


def test_parser_checks_runner_command_identity(project):
    root, _, profile, _, item = project
    item["command_identity"] = {"kind": "argv", "argv": ["echo", "PASS"]}
    assert (
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )
        == []
    )


@pytest.mark.parametrize(
    "path",
    [
        "/tmp/test_results.py",
        "scripts/test_results.py",
        ".changerail/adapters/../test_results.py",
        ".changerail/adapters/results.so",
    ],
)
def test_adapter_path_must_be_confined_python_source(project, path):
    root, _, profile, _, item = project
    profile["adapters"]["tests"]["module"] = path
    with pytest.raises(DeliveryError, match="under .changerail/adapters"):
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )


@pytest.mark.parametrize("component", ["leaf", "parent"])
def test_adapter_symlinks_are_refused(project, component):
    root, module, profile, _, item = project
    if component == "leaf":
        actual = root / "actual.py"
        module.rename(actual)
        module.symlink_to(actual)
    else:
        actual = root / "actual"
        module.parent.rename(actual)
        module.parent.symlink_to(actual, target_is_directory=True)
    with pytest.raises(DeliveryError, match="unsafe"):
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )


def test_nonregular_adapter_does_not_wait_for_fifo_writer(project):
    root, module, profile, _, item = project
    module.unlink()
    os.mkfifo(module)
    with pytest.raises(DeliveryError, match="nonregular"):
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )


@pytest.mark.parametrize(
    "output",
    [
        "[]",
        "{'tests/spec.js::test_ok': (True, 30)}",
        "{'tests/spec.js::test_ok': (-1, 30)}",
        "{'tests/spec.js::test_ok': (0, 9999)}",
        "{'tests/spec.js::test_fake': (0, 27)}",
        "{'tests/spec.js::test_ok': (1, 27)}",
        "{'tests/spec.js::test_ok': (0, 8)}",
    ],
)
def test_malformed_or_unbound_parser_output_is_refused(project, output):
    root, module, profile, _, item = project
    module.write_text(
        f"def parse_results(log, command_identity, target): return {output}\n"
    )
    with pytest.raises(DeliveryError):
        receipt_nodes(
            root, profile, item, b"PASS tests/spec.js::test_ok\n", "tests/spec.js"
        )


@pytest.mark.parametrize("mutation", ["node", "span", "duplicate", "empty"])
def test_selected_nodes_must_match_actual_parser_observation(project, mutation):
    root, _, profile, identity, item = project
    data = b"PASS tests/spec.js::test_ok\n"
    selected = receipt_nodes(root, profile, item, data, "tests/spec.js")
    if mutation == "node":
        selected[0]["node"] = "tests/other.js::test_ok"
    elif mutation == "span":
        selected[0]["end"] -= 1
    elif mutation == "duplicate":
        selected.append(dict(selected[0]))
    else:
        selected = []
    with pytest.raises(DeliveryError):
        validate_selected_nodes(
            root, profile, data, identity, "tests/spec.js", selected, "proof"
        )


def test_current_adapter_source_is_reloaded(project):
    root, module, profile, _, item = project
    data = b"PASS tests/spec.js::test_ok\n"
    assert receipt_nodes(root, profile, item, data, "tests/spec.js")
    module.write_text("def parse_results(log, command_identity, target): return {}\n")
    assert receipt_nodes(root, profile, item, data, "tests/spec.js") == []
