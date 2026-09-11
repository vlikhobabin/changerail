"""Pinned engine execution stays separate from product payload."""

import hashlib
import json
from pathlib import Path

import pytest

from scripts.changerail import engine_runtime
from scripts.changerail import local_delivery as d


def setup_binding(tmp_path, monkeypatch):
    project, engine = (tmp_path / name for name in ("project", "engine"))
    project.mkdir()
    engine.mkdir()
    (project / ".changerail").mkdir()
    (project / ".changerail/profile.toml").write_text("profile")
    (project / "bin").mkdir()
    (project / "bin/model").write_text("launcher")
    for root in (project, engine):
        (root / "scripts/changerail").mkdir(parents=True)
        (root / "scripts/changerail/contracts.py").write_text("original")
    binding = {"engine_root": str(engine), "engine_identity": "a" * 64}
    monkeypatch.setattr(engine_runtime, "binding", lambda *_: binding)
    monkeypatch.setattr(d, "REPO_ROOT", project)
    monkeypatch.setattr(d, "_SOURCE_REPO_ROOT", engine)
    monkeypatch.setattr(d, "PROFILE_PATH", project / ".changerail/profile.toml")
    monkeypatch.setattr(
        d, "profile", lambda: {"adapters": {"codex": {"launcher": "bin/model"}}}
    )
    return project, engine


def test_engine_identity_excludes_mutable_product_code(tmp_path, monkeypatch):
    project, engine = setup_binding(tmp_path, monkeypatch)
    identity = d.execution_identity()
    (project / "scripts/changerail/contracts.py").write_text("new product")
    (project / "scripts/changerail/added.py").write_text("new module")
    assert d.execution_identity() == identity
    (project / "bin/model").write_text("changed launcher")
    assert d.execution_identity() != identity


def test_engine_schema_read_uses_pinned_bytes(tmp_path, monkeypatch):
    project, engine = setup_binding(tmp_path, monkeypatch)
    rel = "tools/changerail/schemas/example.json"
    for root, val in ((project, "product"), (engine, "engine")):
        (root / rel).parent.mkdir(parents=True)
        (root / rel).write_text(json.dumps({"source": val}))
    assert d.load_json(project / rel) == {"source": "engine"}


def test_engine_environment_alone_has_no_authority(tmp_path, monkeypatch):
    monkeypatch.setenv("CHRL_ENGINE_ROOT", str(tmp_path))
    with pytest.raises(d.DeliveryError, match="binding"):
        engine_runtime.binding(tmp_path)


def test_interpreter_input_is_frozen(tmp_path, monkeypatch):
    setup_binding(tmp_path, monkeypatch)
    result = d.execution_identity()
    assert (
        result["python/executable"]
        == hashlib.sha256(Path(__import__("sys").executable).read_bytes()).hexdigest()
    )


def test_workflow_loader_is_resolved_from_engine(tmp_path, monkeypatch):
    from scripts.changerail.openspec_adapter import OpenSpecAdapter
    from types import SimpleNamespace
    import subprocess

    project, engine = setup_binding(tmp_path, monkeypatch)
    client = object.__new__(OpenSpecAdapter)
    client.root, client.node, client.timeout = project, Path("/usr/bin/node"), 1
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout="verified workflow", stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    assert client.workflow("verify") == "verified workflow"
    assert calls[0][0][1] == str(engine / "tools/openspec/workflow-instructions.mjs")
    assert calls[0][1]["env"]["CHRL_PROJECT_ROOT"] == str(project)
