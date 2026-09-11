"""Subprocess imports and nested launchers use the sealed engine."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import distribution
from scripts.changerail import engine_snapshot

SOURCE = Path(__file__).resolve().parents[3]


def test_nested_commands_do_not_import_mutable_product(tmp_path):
    source, project, engine = (
        tmp_path / name for name in ("source", "project", "engine")
    )
    _, payload = distribution.source_payload(SOURCE)
    for root in (source, project):
        for name, (data, mode) in payload.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(mode)
    for args in (
        ("init", "-b", "main"),
        ("config", "user.name", "Fixture"),
        ("config", "user.email", "fixture@example.invalid"),
        ("add", "."),
        ("commit", "-m", "sealed engine"),
    ):
        subprocess.run(
            ["git", "-C", str(source), *args], check=True, capture_output=True
        )
    engine_snapshot.create_snapshot(source, engine)
    (project / ".changerail").mkdir()
    (project / ".changerail/profile.toml").write_bytes(
        (SOURCE / "tools/changerail/templates/profile.toml").read_bytes()
    )
    engine_snapshot.bind_engine(project, engine)
    shutil.copytree(
        SOURCE / "tools/openspec/node_modules", project / "tools/openspec/node_modules"
    )
    # Poison both code and helpers in the mutable checkout. Every invocation
    # below would fail observably if the current working directory won imports.
    (project / "scripts/changerail/local_delivery.py").write_text(
        'raise RuntimeError("PRODUCT IMPORTED")\n'
    )
    (project / "tools/openspec/check-install.mjs").write_text(
        'throw new Error("PRODUCT HELPER");\n'
    )
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for key in tuple(env):
        if key.startswith("CHRL_") or key == "PYTHONPATH":
            env.pop(key)
    for entry in (project / "bin/chrl", engine / "bin/chrl"):
        result = subprocess.run(
            [str(entry), "--project", str(project), "--help"],
            cwd=project,
            env=env,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert "self-host-recovery-apply" in result.stdout
    for entry in (project / "bin/openspec", engine / "bin/openspec"):
        result = subprocess.run(
            [str(entry), "--project", str(project), "--version"],
            cwd=project,
            env=env,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "1.3.1"
    env["CHRL_PROJECT_ROOT"] = str(project)
    env["PYTHONPATH"] = str(engine)
    result = subprocess.run(
        [
            shutil.which("python3"),
            "-P",
            "-c",
            'import json; from scripts.changerail import local_delivery as d; print(json.dumps({"source":str(d._SOURCE_REPO_ROOT), "identity":d.execution_identity()}))',
        ],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["source"] == str(engine)
    assert json.loads(result.stdout)["identity"]["engine/identity"]
    # Freeze actual dependency bytes, then change code without changing version.
    run = project / ".runtime/changerail/runs/nested"
    run.mkdir(parents=True)
    (run / "run.json").write_text(
        json.dumps(
            {
                "process_identity": json.loads(result.stdout)["identity"],
                "execution_contract": "changerail.native.v1",
                "mode": "delivery",
                "lifecycle_mode": "openspec-v1",
            }
        )
    )
    env["CHRL_RUN_DIR"] = str(run)
    entry = engine / "bin/openspec"
    before = subprocess.run(
        [str(entry), "--project", str(project), "--version"],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
    )
    assert before.returncode == 0, before.stderr
    cli = project / "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js"
    cli.write_text("console.log('MUTATED DEPENDENCY EXECUTED');\n")
    after = subprocess.run(
        [str(entry), "--project", str(project), "--version"],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
    )
    assert after.returncode != 0
    assert "frozen execution process changed" in after.stderr
    assert "MUTATED DEPENDENCY EXECUTED" not in after.stdout
    # No bytecode or other runtime file may have appeared in the snapshot.
    engine_snapshot.verify_snapshot(engine)
