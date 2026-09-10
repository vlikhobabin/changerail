from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from scripts.changerail import local_delivery as delivery

PROJECT = Path(__file__).resolve().parents[3]
FIXTURE_BOARD = "openspec/" + "board"


def test_card_template_acceptance_has_a_scenario_owner():
    template = (PROJECT / "tools/changerail/templates/card-template.md").read_text()
    assert "C1" in delivery._acceptance_scenarios_text(template)


def _repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for args in (
        ("init", "-b", "main"),
        ("config", "user.name", "Fixture"),
        ("config", "user.email", "fixture@example.invalid"),
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    (root / "baseline.txt").write_text("baseline\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True
    )
    monkeypatch.setattr(delivery, "REPO_ROOT", root)
    return root


def test_tracked_codex_config_affects_fingerprint_but_runtime_does_not(
    tmp_path, monkeypatch
):
    root = _repo(tmp_path, monkeypatch)
    config = root / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('model = "fixture-model"\n')
    before = delivery.payload_fingerprint()
    assert ".codex/config.toml" in delivery.changed_paths()
    for relative in (
        ".codex/auth.json",
        ".codex/sessions/test.json",
        "runtime/output.txt",
        ".runtime/run.json",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture data\n")
    assert delivery.payload_fingerprint() == before
    config.write_text('model = "changed-model"\n')
    assert delivery.payload_fingerprint() != before


@pytest.mark.parametrize("role", ["review", "implementation"])
@pytest.mark.parametrize("resume", [None, "fixture-thread"])
def test_routes_survive_new_and_resumed_cli_sessions(tmp_path, role, resume):
    configured = delivery.profile()
    model, reasoning = delivery.model_route(configured, role)
    assert model == configured["models"][role]["model"]
    assert reasoning == configured["models"][role]["reasoning_effort"]
    argv = delivery.codex_session_command(
        model=model,
        reasoning=reasoning,
        prompt="fixture",
        last_message=tmp_path / "result.md",
        resume_thread_id=resume,
    )
    assert argv[argv.index("--model") + 1] == model
    assert f'model_reasoning_effort="{reasoning}"' in argv
    assert ("resume" in argv) == bool(resume)


@pytest.mark.parametrize("effort", ["none", "minimal"])
def test_astra_unsupported_reasoning_is_explicit(effort):
    with pytest.raises(delivery.DeliveryError, match="Astra"):
        delivery.model_route(
            {
                "models": {
                    "review": {"model": "gpt-6-astra", "reasoning_effort": effort}
                }
            },
            "review",
        )


def test_local_openspec_runs_pinned_cli_without_npx_fallback():
    result = subprocess.run(
        [str(PROJECT / "bin/openspec"), "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "1.3.1"
    wrapper = (PROJECT / "bin/openspec").read_text(encoding="utf-8")
    assert "npx" not in wrapper
    assert "node_modules/@fission-ai/openspec/bin/openspec.js" in wrapper


def test_tracked_link_can_become_local_command_directory(tmp_path, monkeypatch):
    root = _repo(tmp_path, monkeypatch)
    path = root / "commands"
    path.symlink_to("old-external-source")
    subprocess.run(["git", "add", "commands"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "old link"], cwd=root, check=True, capture_output=True
    )
    path.unlink()
    path.mkdir()
    (path / "local.md").write_text("local command\n")
    before = delivery.payload_fingerprint()
    (path / "local.md").write_text("updated command\n")
    assert delivery.payload_fingerprint() != before
