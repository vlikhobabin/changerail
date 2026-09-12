"""Focused receipt/lease tests; only generic temporary release checkouts mutate."""

import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from scripts.changerail import engine_runtime as runtime
from scripts.changerail import release_executor as release

SOURCE = Path(release.__file__).resolve().parents[2]


def put(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)
    return path


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True
    ).stdout


def accept(root, tag="v1"):
    receipt = release.inspect_release(root, tag=tag, node=Path(shutil.which("node")))
    path = release.receipt_path(root)
    path.write_bytes(release.encoded(receipt))
    path.chmod(0o600)
    return receipt


@pytest.fixture
def release_pair(tmp_path, monkeypatch):
    for key in tuple(os.environ):
        if key.startswith("CHRL_"):
            monkeypatch.delenv(key)
    project, engine = tmp_path / "product", tmp_path / "executor"
    project.mkdir()
    engine.mkdir()
    for name in (
        "scripts/changerail/release_executor.py",
        "scripts/changerail/engine_runtime.py",
        "scripts/changerail/openspec_adapter.py",
        "bin/chrl",
        "bin/openspec",
    ):
        destination = engine / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / name, destination)
    put(engine, "scripts/__init__.py", "")
    put(
        engine,
        "scripts/changerail/contracts.py",
        "class DeliveryError(ValueError): pass\n",
    )
    put(
        engine,
        "scripts/changerail/local_delivery.py",
        """import json, os, sys
from pathlib import Path
from scripts.changerail import engine_runtime as runtime
REPO_ROOT = Path(os.environ['CHRL_PROJECT_ROOT'])
_SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPO_ROOT / '.changerail/profile.toml'
def profile(): return {'adapters': {'codex': {'launcher': 'bin/model'}}}
def _safe_path(value): return Path(value)
def _check_bytes(path, limit): return path.read_bytes()
def require_frozen_execution(run):
    if json.loads((run / 'run.json').read_text())['process_identity'] != runtime.identity(sys.modules[__name__]):
        raise ValueError('frozen execution process changed')
if __name__ == '__main__':
    runtime.require_run(REPO_ROOT)
    if '--product-test' in sys.argv:
        import subprocess
        result = subprocess.run([str(REPO_ROOT / 'bin/test-changerail')], cwd=REPO_ROOT,
                                **runtime.child_process_kwargs(REPO_ROOT))
        raise SystemExit(result.returncode)
    if '--adapter' in sys.argv:
        from scripts.changerail.openspec_adapter import OpenSpecAdapter
        adapter = OpenSpecAdapter(REPO_ROOT)
        print(json.dumps({'package': str(adapter.package), 'workflow': adapter.workflow('verify')}))
        raise SystemExit(0)
    import executor_dependency
    print(json.dumps({'source': str(_SOURCE_REPO_ROOT), 'cwd': str(Path.cwd()),
        'profile': PROFILE_PATH.read_text(), 'dependency': executor_dependency.VALUE,
        'identity': runtime.identity(sys.modules[__name__]),
        'schema': runtime.runtime_path(REPO_ROOT, REPO_ROOT / 'tools/changerail/schemas/example.json').read_text(),
        'prompt': runtime.pinned_prompt(REPO_ROOT, 'implementation', '$chrl-native-deliver'),
        'python': sys.executable}), flush=True)
    if '--hold' in sys.argv: input()
""",
    )
    put(
        engine,
        "scripts/changerail/product_module.py",
        "raise RuntimeError('RELEASE PRODUCT IMPORTED')\n",
    )
    put(engine, "distribution.py", "# fixture distribution\n")
    put(engine, "tools/changerail/schemas/example.json", '"RELEASE SCHEMA"')
    put(engine, "tools/changerail/skills/chrl-native-deliver/SKILL.md", "RELEASE SKILL")
    put(engine, "tools/openspec/package-lock.json", "{}")
    put(
        engine,
        "tools/openspec/package.json",
        '{"dependencies":{"@fission-ai/openspec":"1.3.1"}}',
    )
    put(
        engine,
        "tools/openspec/check-install.mjs",
        """import {readFileSync} from 'node:fs';
const p = process.env.CHRL_PROJECT_ROOT + '/tools/openspec/node_modules/@fission-ai/openspec/package.json';
if (JSON.parse(readFileSync(p)).version !== '1.3.1') throw Error('wrong dependency');
""",
    )
    put(
        engine,
        "tools/openspec/workflow-instructions.mjs",
        "console.log('RELEASE WORKFLOW');\n",
    )
    names = sorted(
        p.relative_to(engine).as_posix() for p in engine.rglob("*") if p.is_file()
    )
    names.append("distribution.json")
    put(
        engine,
        "distribution.json",
        json.dumps(
            {
                "schema": "changerail.distribution-config.v1",
                "version": "1.0.0",
                "execution_contract": "changerail.native.v1",
                "files": names,
                "trees": {},
            }
        ),
    )
    git(engine, "init", "-b", "main")
    git(engine, "config", "user.name", "Fixture")
    git(engine, "config", "user.email", "fixture@example.invalid")
    git(engine, "add", ".")
    git(engine, "commit", "-m", "fixture release")
    git(engine, "tag", "v1")
    version = subprocess.check_output(
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            "import sysconfig;print(sysconfig.get_python_version())",
        ],
        text=True,
    ).strip()
    put(
        engine,
        f".venv/lib/python{version}/site-packages/executor_dependency.py",
        "VALUE = 'RELEASE DEPENDENCY'\n",
    )
    # Poisoned .pth is intentionally ignored by the isolated bootstrap.
    put(
        engine,
        f".venv/lib/python{version}/site-packages/poison.pth",
        "import sys; raise RuntimeError('PTH EXECUTED')\n",
    )
    put(
        engine,
        ".venv/pyvenv.cfg",
        "home = /usr/bin\ninclude-system-site-packages = false\n",
    )
    (engine / ".venv/bin").mkdir()
    (engine / ".venv/bin/python").symlink_to("/usr/bin/python3")
    (engine / ".venv/lib64").symlink_to("lib", target_is_directory=True)
    put(
        engine,
        "tools/openspec/node_modules/@fission-ai/openspec/package.json",
        '{"name":"@fission-ai/openspec","version":"1.3.1","type":"module"}',
    )
    put(
        engine,
        "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js",
        """
if (process.argv.includes('--version')) { console.log('1.3.1'); }
else { console.log(JSON.stringify({cwd: process.cwd(), dependency: process.env.CHRL_PROJECT_ROOT})); }
if (process.argv.includes('--hold')) { process.stdin.resume(); process.stdin.once('data', () => process.exit(0)); }
""",
    )
    (engine / "tools/openspec/node_modules/.bin").mkdir()
    (engine / "tools/openspec/node_modules/.bin/openspec").symlink_to(
        "../@fission-ai/openspec/bin/openspec.js"
    )
    accept(engine)
    put(project, release.BINDING, json.dumps(release.binding_document(project, engine)))
    put(project, ".changerail/profile.toml", "DEV PROFILE")
    put(project, "bin/model", "DEV MODEL")
    yield project, engine
    for root, fd in list(release._LEASES.items()):
        if root.is_relative_to(tmp_path):
            os.close(fd)
            del release._LEASES[root]
    monkeypatch.delenv(release.USE_FD, raising=False)


def test_receipt_accepts_overlays_and_standard_dependency_links(release_pair):
    project, engine = release_pair
    put(engine, "openspec/board/local.md", "local overlay")
    put(engine, ".changerail/profile.toml", "local profile")
    value = release.verify_binding(project)
    assert value["release_receipt"]["release"]["tag"] == "v1"
    assert (
        value["release_receipt"]["dependencies"]["files"][".venv"]["bin/python"]["link"]
        == "/usr/bin/python3"
    )
    assert release.read_binding(project) == release.binding_document(project, engine)
    assert "engine_identity" not in release.read_binding(project)


@pytest.mark.parametrize(
    "name",
    [
        "scripts/changerail/contracts.py",
        "scripts/changerail/undeclared.py",
        "scripts/changerail/undeclared.pyc",
        ".venv/lib64/injected.py",
        "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js",
    ],
)
def test_changed_code_or_dependencies_refused(release_pair, name):
    project, engine = release_pair
    put(engine, name, "CHANGED")
    with pytest.raises(release.ReleaseExecutorError):
        release.verify_binding(project)


def test_wrong_binding_source_overlap_and_receipt(release_pair):
    project, engine = release_pair
    with pytest.raises(release.ReleaseExecutorError, match="executing source"):
        release.read_binding(project, expected_engine=project)
    with pytest.raises(release.ReleaseExecutorError, match="overlaps"):
        release.binding_document(project, project)
    receipt = release.document(release.receipt_path(engine))
    receipt["release"]["tree"] = "0" * 40
    with pytest.raises(release.ReleaseExecutorError, match="differ"):
        release.verify_release(engine, accepted=receipt)
    value = release.binding_document(project, engine)
    value["project_root"] = str(engine)
    put(project, release.BINDING, json.dumps(value))
    with pytest.raises(release.ReleaseExecutorError, match="binding"):
        release.read_binding(project)


def test_unlocked_or_foreign_inherited_fd_is_not_authority(
    release_pair, monkeypatch, tmp_path
):
    _, engine = release_pair
    for path in (release.lock_path(engine), tmp_path / "foreign"):
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        monkeypatch.setenv(release.USE_FD, str(fd))
        try:
            with pytest.raises(release.ReleaseExecutorError, match="inherited"):
                release.ensure_use(engine)
        finally:
            os.close(fd)


def test_shared_readers_exclude_updater_without_waiting(release_pair, monkeypatch):
    _, engine = release_pair
    fd = release.ensure_use(engine)
    assert os.get_inheritable(fd)
    assert release.child_process_kwargs(engine) == {"pass_fds": (fd,)}
    independent = os.open(release.lock_path(engine), os.O_RDWR)
    try:
        with pytest.raises(BlockingIOError):
            fcntl.flock(independent, fcntl.LOCK_EX | fcntl.LOCK_NB)
    finally:
        os.close(independent)
    with pytest.raises(release.ReleaseExecutorError, match="outside"):
        with release.exclusive_use(engine):
            pytest.fail("upgraded reader")


def test_snapshot_identity_wire_is_unchanged(tmp_path, monkeypatch):
    project, engine = tmp_path / "project", tmp_path / "snapshot"
    project.mkdir()
    engine.mkdir()
    put(project, ".changerail/profile.toml", "profile")
    put(project, "bin/model", "model")
    put(project, "tools/openspec/node_modules/package/code.js", "old dependency")
    value = {
        "schema": "changerail.engine-binding.v1",
        "engine_root": str(engine),
        "engine_identity": "a" * 64,
    }
    monkeypatch.setattr(runtime, "binding", lambda _: value)
    delivery = SimpleNamespace(
        REPO_ROOT=project,
        _SOURCE_REPO_ROOT=engine,
        PROFILE_PATH=project / ".changerail/profile.toml",
        profile=lambda: {"adapters": {"codex": {"launcher": "bin/model"}}},
        _safe_path=Path,
        _check_bytes=lambda p, _: p.read_bytes(),
    )
    import hashlib

    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    dep = project / "tools/openspec/node_modules/package/code.js"
    deps = {
        "tools/openspec/node_modules/package/code.js": {
            "sha256": sha(dep.read_bytes()),
            "mode": dep.stat().st_mode & 0o7777,
        }
    }
    import sys

    assert runtime.identity(delivery) == {
        "engine/identity": "a" * 64,
        "engine/root": sha(str(engine).encode()),
        "python/executable": sha(Path(sys.executable).read_bytes()),
        "project/.changerail/profile.toml": sha(b"profile"),
        "project/bin/model": sha(b"model"),
        "project/openspec-dependency-inventory": sha(
            json.dumps(deps, sort_keys=True, separators=(",", ":")).encode()
        ),
    }
    assert runtime.dependency_root(project) == project / "tools/openspec"
    assert runtime.runtime_path(project, dep) == dep


def test_verification_does_not_execute_python_probe(release_pair, monkeypatch):
    project, _engine = release_pair
    original = subprocess.run

    def run(argv, **kwargs):
        assert "-I" not in argv, (
            "verifier executed an interpreter before dependency verification"
        )
        return original(argv, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    assert release.verify_binding(project)["engine_identity"]


def test_top_level_python_shadow_refused(release_pair):
    project, engine = release_pair
    put(engine, "jsonschema.py", "raise RuntimeError('UNDECLARED PYTHON')")
    with pytest.raises(release.ReleaseExecutorError, match="undeclared Python"):
        release.verify_binding(project)


def test_cannot_accept_venv_bootstrap_from_mutable_project(release_pair):
    project, engine = release_pair
    put(engine, ".venv/pyvenv.cfg", f"home = {project}\n")
    with pytest.raises(release.ReleaseExecutorError, match="venv home"):
        release.inspect_release(engine, tag="v1", node=Path(shutil.which("node")))


def test_committed_checkout_tools_do_not_expand_distribution(release_pair):
    _project, engine = release_pair
    extras = (
        "scripts/public-surface-scan.py",
        "tools/openspec/test-wrapper.mjs",
        "source_audit.py",
    )
    for name in extras:
        put(engine, name, "# committed checkout tool\n")
    git(engine, "add", *extras)
    git(engine, "commit", "-m", "complete checkout tools")
    commit = git(engine, "rev-parse", "HEAD").decode().strip()
    inventory = release.runtime_inventory(engine, commit)
    assert not set(extras) & inventory.keys()
    for name in extras:
        path = engine / name
        before = path.read_bytes()
        path.write_text("# drift without changing Git\n")
        with pytest.raises(release.ReleaseExecutorError, match="Git tree"):
            release.runtime_inventory(engine, commit)
        path.write_bytes(before)
    for name in (
        "scripts/injected.py",
        "tools/openspec/injected.mjs",
        "jsonschema.py",
        "__pycache__/distribution.pyc",
    ):
        path = put(engine, name, "unexpected body")
        with pytest.raises(release.ReleaseExecutorError, match="undeclared"):
            release.runtime_inventory(engine, commit)
        path.unlink()
    put(engine, "tools/openspec/npm-logs/install.log", "npm diagnostic")
    assert release.runtime_inventory(engine, commit) == inventory
    put(engine, "tools/openspec/npm-logs/injected.mjs", "unexpected body")
    with pytest.raises(release.ReleaseExecutorError, match="undeclared"):
        release.runtime_inventory(engine, commit)


@pytest.mark.parametrize("marker_kind", ["stale", "invalid", "symlink"])
def test_maintenance_fence_requires_explicit_receipt_and_exclusive_lease(
    release_pair, marker_kind
):
    _project, engine = release_pair
    accepted = release.document(release.receipt_path(engine))
    marker = release.maintenance_path(engine)
    if marker_kind == "symlink":
        marker.symlink_to(engine.parent / "missing-maintenance-target")
    else:
        marker.write_text('{"state":"stale"}' if marker_kind == "stale" else "not JSON")
    with pytest.raises(release.ReleaseExecutorError, match="maintenance"):
        release.verify_release(engine)
    with pytest.raises(release.ReleaseExecutorError, match="maintenance"):
        release.verify_release(engine, accepted=accepted)
    with pytest.raises(release.ReleaseExecutorError, match="maintenance"):
        release.inspect_release(engine, tag="v1", node=Path(shutil.which("node")))
    with release.exclusive_use(engine):
        # Default runtime API remains fenced even inside an updater context.
        with pytest.raises(release.ReleaseExecutorError, match="maintenance"):
            release.verify_release(engine)
        assert release.verify_release(engine, accepted=accepted) == accepted
        assert (
            release.inspect_release(engine, tag="v1", node=Path(shutil.which("node")))
            == accepted
        )
    assert os.path.lexists(marker)


@pytest.mark.parametrize(
    "surface",
    [
        "runtime-root",
        "runtime-root-dynamic",
        "venv",
        "runner-tree",
        "openspec",
        "stdlib",
    ],
)
def test_unlistable_importable_packages_refuse_receipt_as_ordinary_uid(
    release_pair, tmp_path, surface
):
    """0111 still permits known-file imports: verify must fail on enumeration."""
    import tempfile

    _project, original = release_pair
    worker = r"""
import importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
assert os.geteuid() != 0, "root bypasses the permission failure under test"
engine, work, surface = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location("permission_release", engine / "scripts/changerail/release_executor.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
node = Path(shutil.which("node"))
accepted = release.inspect_release(engine, tag="v1", node=node)
if surface == "stdlib":
    stdlib = work / "stdlib"
    stdlib.mkdir()
    info = dict(accepted["dependencies"]["python"], stdlib_root=str(stdlib))
    accepted = release.inspect_release(engine, tag="v1", node=node, python_info=info)
receipt = release.receipt_path(engine)
receipt.write_bytes(release.encoded(accepted))
receipt.chmod(0o600)
release.ensure_use(engine)
assert release.verify_release(engine) == accepted
original_receipt = receipt.read_bytes()
python = accepted["dependencies"]["python"]
parent, name, module = {
    "runtime-root": (engine, "jsonschema", "jsonschema"),
    "runtime-root-dynamic": (engine, "unaccepted-package", "unaccepted-package"),
    "venv": (Path(python["site_packages"]), "executor_dependency", "executor_dependency"),
    "runner-tree": (engine / "scripts/changerail", "unaccepted", "scripts.changerail.unaccepted"),
    "openspec": (engine / "tools/openspec/node_modules", "unaccepted", "unaccepted"),
    "stdlib": (Path(python["stdlib_root"]), "unaccepted", "unaccepted"),
}[surface]
package = parent / name
package.mkdir()
marker = "UNACCEPTED PACKAGE EXECUTED"
if surface == "openspec":
    (package / "index.js").write_text("module.exports = " + json.dumps(marker) + ";\n")
else:
    (package / "__init__.py").write_text("VALUE = " + repr(marker) + "\n")
package.chmod(0o111)
try:
    try:
        with os.scandir(package) as entries:
            list(entries)
    except PermissionError:
        pass
    else:
        raise AssertionError("ordinary UID could enumerate 0111 directory")
    # Verification precedes the separate reachability probe below; the receipt
    # may never be accepted just because its executable additions were hidden.
    try:
        release.verify_release(engine)
    except release.ReleaseExecutorError as exc:
        assert "cannot enumerate inventory directory" in str(exc), str(exc)
        assert isinstance(exc.__cause__, PermissionError)
    else:
        raise AssertionError("unchanged receipt accepted an unlistable package")
    assert receipt.read_bytes() == original_receipt
    if surface == "openspec":
        command = [str(node), "-e", "console.log(require(" + json.dumps(str(package)) + "))"]
    else:
        paths = [str(engine), python["site_packages"], python["stdlib_root"],
                 str(Path(python["stdlib_root"]) / "lib-dynload")]
        code = f"import sys, importlib; sys.path[:] = {paths!r}; loaded = importlib.import_module({module!r}); print(loaded.VALUE)"
        command = [python["target"], "-I", "-S", "-B", "-c", code]
    reached = subprocess.run(command, cwd=work, env={"PATH": "/usr/bin:/bin"},
                             text=True, capture_output=True, check=True)
    assert reached.stdout.strip() == marker
finally:
    package.chmod(0o775)
    shutil.rmtree(package)
assert release.verify_release(engine) == accepted
assert receipt.read_bytes() == original_receipt
os.close(release._LEASES.pop(engine))
print(json.dumps({"uid": os.geteuid(), "surface": surface, "refused": True,
                  "known_file_import_succeeded": True, "receipt_unchanged": True}))
"""
    # Root CI must reproduce real permission denial, not silently pass because
    # CAP_DAC_OVERRIDE makes 0111 readable. Copy only this generic fixture to an
    # independent temp tree accessible to UID 1000; never chmod workspace parents.
    with tempfile.TemporaryDirectory(
        prefix="chrl-ordinary-inventory-", dir=None if os.geteuid() == 0 else tmp_path
    ) as temporary:
        work = Path(temporary)
        engine = work / "executor"
        shutil.copytree(original, engine, symlinks=True)
        process_options = {}
        if os.geteuid() == 0:
            actor = 1000
            os.chown(work, actor, actor)
            for directory, dirs, files in os.walk(engine, followlinks=False):
                os.chown(directory, actor, actor, follow_symlinks=False)
                for name in dirs + files:
                    os.chown(
                        Path(directory) / name, actor, actor, follow_symlinks=False
                    )
            process_options = {"user": actor, "group": actor, "extra_groups": []}
        else:
            actor = os.geteuid()
        result = subprocess.run(
            [
                "/usr/bin/python3",
                "-I",
                "-S",
                "-B",
                "-c",
                worker,
                str(engine),
                str(work),
                surface,
            ],
            cwd=work,
            env={"PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=40,
            **process_options,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {
            "uid": actor,
            "surface": surface,
            "refused": True,
            "known_file_import_succeeded": True,
            "receipt_unchanged": True,
        }


def test_distribution_glob_selection_does_not_hide_traversal_errors(
    release_pair, monkeypatch
):
    _project, engine = release_pair
    config = release.document(engine / "distribution.json")
    config["trees"] = {"scripts/changerail": "**/*.py"}
    put(engine, "distribution.json", json.dumps(config))
    denied = engine / "scripts/changerail"
    original = os.scandir

    def scandir(path):
        if Path(path) == denied:
            raise PermissionError(13, "fixture cannot enumerate", str(path))
        return original(path)

    monkeypatch.setattr(os, "scandir", scandir)
    commit = git(engine, "rev-parse", "HEAD").decode().strip()
    with pytest.raises(release.ReleaseExecutorError, match="cannot enumerate") as error:
        release.runtime_inventory(engine, commit)
    assert isinstance(error.value.__cause__, PermissionError)


def test_inventory_entry_stat_error_is_not_silently_skipped(tmp_path, monkeypatch):
    class Entry:
        path = str(tmp_path / "hidden")

        def stat(self, **kwargs):
            raise PermissionError(13, "fixture cannot stat", self.path)

    class Entries:
        def __enter__(self):
            return iter([Entry()])

        def __exit__(self, *_args):
            pass

    monkeypatch.setattr(os, "scandir", lambda _path: Entries())
    with pytest.raises(release.ReleaseExecutorError, match="cannot enumerate") as error:
        list(release._walk(tmp_path))
    assert isinstance(error.value.__cause__, PermissionError)
