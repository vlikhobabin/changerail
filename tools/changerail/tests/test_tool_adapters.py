"""Tool contracts are reusable across repositories without modifying the engine."""

from pathlib import Path

import pytest

from scripts.changerail.adapters.codex import session_command
from scripts.changerail.adapters.pytest import _validate_pytest_selected_nodes
from scripts.changerail.contracts import DeliveryError


def test_local_launcher_preserves_prompt_as_one_argument(tmp_path: Path) -> None:
    prompt = "Inspect `source.py`; preserve $VALUE and literal newlines\nThen review."
    command = session_command(
        tmp_path,
        {"adapters": {"codex": {"launcher": "bin/project-agent"}}},
        model="example-model",
        reasoning="high",
        last_message=tmp_path / "reply.md",
        prompt=prompt,
        resume_thread_id="retained-thread",
    )
    assert command[0] == str(tmp_path / "bin/project-agent")
    assert command[1:3] == ["exec", "resume"]
    assert command[-2:] == ["retained-thread", prompt]


@pytest.mark.parametrize(
    "launcher", ["../foreign/agent", "/opt/example-foreign/agent", ""]
)
def test_launcher_cannot_escape_project(tmp_path: Path, launcher: str) -> None:
    with pytest.raises(DeliveryError):
        session_command(
            tmp_path,
            {"adapters": {"codex": {"launcher": launcher}}},
            model="example-model",
            reasoning="high",
            last_message=tmp_path / "reply.md",
            prompt="review",
        )


def test_pytest_adapter_requires_actual_selected_passing_node() -> None:
    node = "tests/test_example.py::test_contract[данные]"
    line = f"{node} PASSED [100%]".encode()
    command = {
        "kind": "argv",
        "argv": ["python3", "-m", "pytest", "-v", "tests/test_example.py"],
    }
    selected = [{"node": node, "start": 0, "end": len(line)}]
    assert node in _validate_pytest_selected_nodes(
        line,
        command,
        "tests/test_example.py::test_contract",
        selected,
        label="fixture",
    )
    for log, identity in [
        (b"1 passed in 0.01s", command),
        (line.replace(b"PASSED", b"FAILED"), command),
        (line, {"kind": "argv", "argv": ["echo", "pytest"]}),
    ]:
        with pytest.raises(DeliveryError):
            _validate_pytest_selected_nodes(
                log,
                identity,
                "tests/test_example.py::test_contract",
                selected,
                label="fixture",
            )
