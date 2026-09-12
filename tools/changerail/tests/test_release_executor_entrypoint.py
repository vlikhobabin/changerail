"""External release Python/Node entrypoints retain isolation, identity and leases."""

import fcntl
import json
import os
import selectors
import subprocess

import pytest

from scripts.changerail import release_executor as release
from test_release_executor import SOURCE, accept, git, put
from test_release_executor import release_pair as fixture_release_pair

release_pair = fixture_release_pair


def environment():
    return {
        k: v for k, v in os.environ.items() if not k.startswith(("CHRL_", "PYTHON"))
    }


def invoke(project, engine, entry="chrl", *args, env=None):
    return subprocess.run(
        [str(engine / "bin" / entry), "--project", str(project), *args],
        cwd=engine,
        env=environment() if env is None else env,
        text=True,
        capture_output=True,
        timeout=30,
    )


def test_external_launcher_never_imports_poisoned_dev(release_pair):
    project, engine = release_pair
    for name in (
        "scripts/__init__.py",
        "scripts/changerail/engine_runtime.py",
        "scripts/changerail/release_executor.py",
        "scripts/changerail/local_delivery.py",
    ):
        put(project, name, "raise RuntimeError('DEV PYTHON IMPORTED')\n")
    put(project, "tools/openspec/check-install.mjs", "throw Error('DEV HELPER')\n")
    put(project, "tools/changerail/schemas/example.json", "DEV SCHEMA")
    put(project, "tools/changerail/skills/chrl-native-deliver/SKILL.md", "DEV SKILL")
    poisoned = put(
        project,
        ".venv/bin/python",
        "#!/bin/sh\necho DEV_PYTHON_EXECUTED >&2\nexit 99\n",
    )
    poisoned.chmod(0o755)
    result = invoke(project, engine)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["source"] == str(engine)
    assert data["cwd"] == str(project)
    assert data["profile"] == "DEV PROFILE"
    assert data["schema"] == '"RELEASE SCHEMA"'
    assert "RELEASE SKILL" in data["prompt"] and "DEV SKILL" not in data["prompt"]
    assert data["dependency"] == "RELEASE DEPENDENCY"
    before = data["identity"]
    put(project, "scripts/changerail/new.py", "DEV EDIT")
    assert json.loads(invoke(project, engine).stdout)["identity"] == before
    put(project, "bin/model", "NEW DEV LAUNCHER")
    assert json.loads(invoke(project, engine).stdout)["identity"] != before
    node = invoke(project, engine, "openspec")
    assert node.returncode == 0, node.stderr
    assert json.loads(node.stdout) == {"cwd": str(project), "dependency": str(engine)}


def test_release_drift_refused_before_dependency_execution(release_pair):
    project, engine = release_pair
    put(
        engine,
        "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js",
        "console.log('DRIFT EXECUTED');",
    )
    result = invoke(project, engine, "openspec", "--version")
    assert result.returncode != 0
    assert "DRIFT EXECUTED" not in result.stdout
    assert "accepted release" in result.stderr


def test_wrong_external_launcher_and_invalid_binding_refused(release_pair):
    project, engine = release_pair
    env = environment() | {"CHRL_ENGINE_ROOT": str(project)}
    result = invoke(project, engine, env=env)
    assert result.returncode != 0 and "differs from binding" in result.stderr
    # Calling the mutable checkout's copied launcher cannot masquerade as executor.
    import shutil

    for name in ("bin/chrl", "scripts/changerail/release_executor.py"):
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(engine / name, path)
    result = invoke(project, project)
    assert result.returncode != 0 and "executing source" in result.stderr
    put(
        project,
        release.BINDING,
        '{"schema":"changerail.engine-binding.v2","kind":"wrong"}',
    )
    result = invoke(project, engine)
    assert result.returncode != 0 and "binding" in result.stderr


@pytest.mark.parametrize("entry", ["chrl", "openspec"])
def test_use_lock_survives_python_exec_and_node_until_exit(release_pair, entry):
    project, engine = release_pair
    process = subprocess.Popen(
        [str(engine / "bin" / entry), "--project", str(project), "--hold"],
        cwd=engine,
        env=environment(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        assert selector.select(timeout=30), "executor did not reach held stage"
        line = process.stdout.readline()
        assert line, process.stderr.read()
        assert json.loads(line)["cwd"] == str(project)
        fd = os.open(release.lock_path(engine), os.O_RDWR)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            process.communicate("\n", timeout=10)
            assert process.returncode == 0
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)
    finally:
        selector.close()
        if process.poll() is None:
            # Own test fixture only, never a production process.
            process.kill()
            process.communicate()


def test_explicit_release_upgrade_changes_new_identity_and_refuses_old_run(
    release_pair,
):
    project, engine = release_pair
    result = invoke(project, engine)
    assert result.returncode == 0, result.stderr
    previous = json.loads(result.stdout)["identity"]
    binding_bytes = (project / release.BINDING).read_bytes()
    run = project / ".runtime/run"
    put(run, "run.json", json.dumps({"process_identity": previous}))
    put(
        engine,
        "tools/changerail/skills/chrl-native-deliver/SKILL.md",
        "NEXT RELEASE SKILL",
    )
    git(engine, "add", "tools/changerail/skills/chrl-native-deliver/SKILL.md")
    git(engine, "commit", "-m", "next explicit fixture release")
    git(engine, "tag", "v2")
    with release.exclusive_use(engine):
        accept(engine, "v2")
    result = invoke(project, engine)
    assert result.returncode == 0, result.stderr
    current = json.loads(result.stdout)["identity"]
    assert current != previous and current["engine/release-tag"] == "v2"
    assert (project / release.BINDING).read_bytes() == binding_bytes
    result = invoke(project, engine, env=environment() | {"CHRL_RUN_DIR": str(run)})
    assert (
        result.returncode != 0 and "frozen execution process changed" in result.stderr
    )


def test_helper_drift_refused_before_import(release_pair):
    project, engine = release_pair
    put(
        engine,
        "scripts/changerail/release_executor.py",
        "raise RuntimeError('HELPER EXECUTED')\n",
    )
    result = invoke(project, engine)
    assert result.returncode != 0 and "bootstrap differs" in result.stderr
    assert "HELPER EXECUTED" not in result.stderr


def test_inherited_lease_reaches_nested_launcher(release_pair):
    project, engine = release_pair
    fd = release.ensure_use(engine)
    child = subprocess.run(
        [str(engine / "bin/chrl"), "--project", str(project)],
        cwd=project,
        env=environment() | {release.USE_FD: str(fd)},
        **release.child_process_kwargs(engine),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert child.returncode == 0, child.stderr
    assert json.loads(child.stdout)["source"] == str(engine)
    assert release.ensure_use(engine) == fd


def test_openspec_adapter_selects_release_package_and_workflow(release_pair):
    project, engine = release_pair
    put(
        project,
        "tools/openspec/workflow-instructions.mjs",
        "throw Error('DEV WORKFLOW');",
    )
    result = invoke(project, engine, "chrl", "--adapter")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "package": str(engine / "tools/openspec/node_modules/@fission-ai/openspec"),
        "workflow": "RELEASE WORKFLOW\n",
    }


def test_product_test_launcher_imports_dev_inside_release_session(release_pair):
    import shutil

    project, engine = release_pair
    shutil.copy2(SOURCE / "bin/test-changerail", project / "bin/test-changerail")
    put(project, "scripts/__init__.py", "")
    put(project, "scripts/changerail/__init__.py", "")
    put(project, "scripts/changerail/product_module.py", "VALUE = 'DEV PRODUCT'\n")
    put(
        project,
        "pytest.py",
        "from scripts.changerail.product_module import VALUE; print(VALUE)\n",
    )
    (project / ".venv/bin").mkdir(parents=True)
    (project / ".venv/bin/python").symlink_to("/usr/bin/python3")
    result = invoke(project, engine, "chrl", "--product-test")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "DEV PRODUCT"


def test_direct_wrong_python_bootstrap_is_refused(release_pair):
    project, engine = release_pair
    result = subprocess.run(
        ["/usr/bin/python3", "-P", "-B", "-m", "scripts.changerail.engine_runtime"],
        env=environment()
        | {"CHRL_PROJECT_ROOT": str(project), "PYTHONPATH": str(engine)},
        cwd=project,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "isolated executor Python bootstrap" in result.stderr


@pytest.mark.parametrize("marker_kind", ["stale", "invalid", "symlink"])
def test_launchers_refuse_maintenance_before_loading_helper(release_pair, marker_kind):
    project, engine = release_pair
    marker = release.maintenance_path(engine)
    if marker_kind == "symlink":
        marker.symlink_to(engine.parent / "missing-maintenance-target")
    else:
        marker.write_text('{"state":"stale"}' if marker_kind == "stale" else "not JSON")
    # Old accepted receipt and every execution byte remain unchanged.
    for entry in ("chrl", "openspec"):
        result = invoke(
            project,
            engine,
            entry,
            "--version",
            env=environment()
            | {
                "CHRL_ENGINE_USE_FD": "999999",
                "CHRL_ALLOW_MAINTENANCE": "1",
            },
        )
        assert result.returncode != 0 and "release maintenance" in result.stderr
    # A damaged helper must not even be read/compiled through the marker fence.
    put(
        engine,
        "scripts/changerail/release_executor.py",
        "raise RuntimeError('HELPER EXECUTED')",
    )
    result = invoke(project, engine)
    assert result.returncode != 0 and "release maintenance" in result.stderr
    assert (
        "HELPER EXECUTED" not in result.stderr
        and "bootstrap differs" not in result.stderr
    )


def test_nested_close_fds_transport_reacquires_own_lease(release_pair, monkeypatch):
    project, engine = release_pair
    initial = invoke(project, engine)
    assert initial.returncode == 0, initial.stderr
    identity = json.loads(initial.stdout)["identity"]
    run = project / ".runtime/frozen"
    put(run, "run.json", json.dumps({"process_identity": identity}))
    original_run = (run / "run.json").read_bytes()
    fd = release.ensure_use(engine)
    intermediate = """import os, subprocess, sys
os.fstat(int(os.environ['CHRL_ENGINE_USE_FD']))
os.close(int(os.environ['CHRL_ENGINE_USE_FD']))
raise SystemExit(subprocess.call(sys.argv[1:], close_fds=True))
"""
    process = subprocess.Popen(
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-B",
            "-c",
            intermediate,
            str(engine / "bin/chrl"),
            "--project",
            str(project),
            "--hold",
        ],
        env=environment() | {release.USE_FD: str(fd), "CHRL_RUN_DIR": str(run)},
        pass_fds=(fd,),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    selector = selectors.DefaultSelector()
    try:
        selector.register(process.stdout, selectors.EVENT_READ)
        assert selector.select(timeout=30), "nested CLI did not reach held stage"
        line = process.stdout.readline()
        assert line, process.stderr.read()
        assert json.loads(line)["identity"] == identity
        probe = os.open(release.lock_path(engine), os.O_RDWR)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # The nested launcher owns its own lease, independent of supervisor FD.
            os.close(release._LEASES.pop(engine))
            monkeypatch.delenv(release.USE_FD)
            with pytest.raises(BlockingIOError):
                fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
            process.communicate("\n", timeout=10)
            assert process.returncode == 0
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(probe)
        assert (run / "run.json").read_bytes() == original_run
    finally:
        selector.close()
        if process.poll() is None:
            process.communicate("\n", timeout=10)


def test_full_git_source_checkout_acceptance_and_real_cli(release_pair, tmp_path):
    import io
    from pathlib import Path
    import shutil
    import sys
    import tarfile

    project, dependency_fixture = release_pair
    # Export the entire committed repository, NOT distribution.source_payload.
    # In the candidate harness SOURCE is beneath the real checkout; after apply
    # SOURCE itself is that checkout. No actual Git state is written.
    repository = Path(git(SOURCE, "rev-parse", "--show-toplevel").decode().strip())
    engine = tmp_path / "full-release"
    engine.mkdir()
    with tarfile.open(
        fileobj=io.BytesIO(git(repository, "archive", "HEAD"))
    ) as archive:
        archive.extractall(engine, filter="data")
    assert (engine / "scripts/public-surface-scan.py").is_file()
    assert (engine / "tools/openspec/test-wrapper.mjs").is_file()
    assert (engine / "tools/changerail/tests/test_engine_runtime.py").is_file()
    assert (engine / "docs").is_dir()
    for name in (
        "scripts/changerail/release_executor.py",
        "scripts/changerail/engine_runtime.py",
        "scripts/changerail/openspec_adapter.py",
        "bin/chrl",
        "bin/openspec",
    ):
        shutil.copy2(SOURCE / name, engine / name)
    put(engine, "source_audit.py", "# committed source outside runtime distribution\n")
    git(engine, "init", "-b", "main")
    git(engine, "config", "user.name", "Fixture")
    git(engine, "config", "user.email", "fixture@example.invalid")
    git(engine, "add", ".")
    git(engine, "commit", "-m", "full source with candidate overlay")
    git(engine, "tag", "v1")
    shutil.copytree(dependency_fixture / ".venv", engine / ".venv", symlinks=True)
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    installed = Path(sys.prefix) / f"lib/python{version}/site-packages"
    site = engine / f".venv/lib/python{version}/site-packages"
    for package in (
        "jsonschema",
        "jsonschema_specifications",
        "referencing",
        "rpds",
        "attrs",
        "attr",
    ):
        shutil.copytree(installed / package, site / package, symlinks=True)
        for metadata in installed.glob(package + "-*.dist-info"):
            shutil.copytree(metadata, site / metadata.name)
    shutil.copytree(
        repository / "tools/openspec/node_modules",
        engine / "tools/openspec/node_modules",
        symlinks=True,
    )
    put(engine, "tools/openspec/npm-logs/install.log", "local npm output\n")
    receipt = accept(engine)
    assert "scripts/public-surface-scan.py" not in receipt["distribution"]["files"]
    assert "tools/openspec/test-wrapper.mjs" not in receipt["distribution"]["files"]
    assert "source_audit.py" not in receipt["distribution"]["files"]
    put(project, release.BINDING, json.dumps(release.binding_document(project, engine)))
    shutil.copy2(
        engine / "tools/changerail/templates/profile.toml",
        project / ".changerail/profile.toml",
    )
    put(project, "bin/codex", "project model launcher")
    put(project, "scripts/__init__.py", "raise RuntimeError('DEV IMPORTED')")
    put(project, "tools/openspec/check-install.mjs", "throw Error('DEV HELPER');")
    result = invoke(project, engine, "chrl", "--help")
    assert result.returncode == 0, result.stderr
    assert "self-host-recovery-apply" in result.stdout
    result = invoke(project, engine, "openspec", "--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "1.3.1"
    # The real OpenSpec command must inspect the selected empty project, not the
    # full release checkout's retained board/changes/specs.
    (project / "openspec/changes").mkdir(parents=True)
    result = invoke(project, engine, "openspec", "list", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["changes"] == []
    schema_name = "tools/changerail/schemas/card-proof.schema.json"
    put(project, schema_name, "INVALID DEV SCHEMA")
    put(project, "tools/changerail/skills/chrl-native-deliver/SKILL.md", "DEV SKILL")
    python = receipt["dependencies"]["python"]
    paths = [
        str(engine),
        python["site_packages"],
        python["stdlib_root"],
        str(Path(python["stdlib_root"]) / "lib-dynload"),
    ]
    code = f"""import sys; sys.path[:] = {paths!r}
import json, jsonschema
from scripts.changerail import local_delivery as d, engine_runtime as runtime
schema = d.load_json(d.REPO_ROOT / {schema_name!r})
jsonschema.Draft202012Validator.check_schema(schema)
print(json.dumps({{'schema': schema, 'prompt': runtime.pinned_prompt(d.REPO_ROOT, 'implementation', '$chrl-native-deliver')}}))
"""
    result = subprocess.run(
        [python["target"], "-I", "-S", "-B", "-c", code],
        cwd=project,
        env=environment() | {"CHRL_PROJECT_ROOT": str(project)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["schema"] == json.loads((engine / schema_name).read_text())
    assert (
        engine / "tools/changerail/skills/chrl-native-deliver/SKILL.md"
    ).read_text() in data["prompt"]
    assert "DEV SKILL" not in data["prompt"]
