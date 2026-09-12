"""Real source checkout integration; fixtures never use an installed executor."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

import distribution as dist
from scripts.changerail import executor_binding as binding
from scripts.changerail import release_executor as release
from scripts.changerail import engine_runtime as runtime
from scripts.changerail import local_delivery as d
from scripts.changerail import engine_snapshot as snapshot
from test_release_executor import FIXTURE_PYTHON, copy_runtime_dependencies

SOURCE = Path(d.__file__).resolve().parents[2]


def put(root, name, content, mode=0o644):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(mode)
    return path


def git(root, *args):
    return (
        subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.PIPE, umask=0o022
        )
        .decode()
        .strip()
    )


def init(root):
    root.mkdir(exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")


@pytest.fixture
def full_release(tmp_path, monkeypatch):
    # Restrict the real /proc scanner to this test's own subprocess fixtures.
    # Other live deliveries on the shared host are outside fixture ownership;
    # production retains its fail-closed scan of all same-user processes.
    original_scan = snapshot._no_live_delivery
    real_path = Path

    class FixtureProcesses:
        def glob(self, pattern):
            found = []
            for process in real_path("/proc").glob(pattern):
                try:
                    parent = next(
                        row.split()[1]
                        for row in (process / "status").read_text().splitlines()
                        if row.startswith("PPid:")
                    )
                    if int(parent) == os.getpid():
                        found.append(process)
                except (FileNotFoundError, ProcessLookupError, StopIteration):
                    continue
            return found

    def fixture_scan(project):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(
                snapshot,
                "Path",
                lambda value: (
                    FixtureProcesses() if value == "/proc" else real_path(value)
                ),
            )
            original_scan(project)

    monkeypatch.setattr(snapshot, "_no_live_delivery", fixture_scan)
    project, engine = tmp_path / "dev", tmp_path / "executor"
    init(project)
    init(engine)
    # Full source/test/docs checkout, not a distribution-only hand-built skeleton.
    for name in ("scripts", "tools/changerail", "tools/openspec", "bin", "docs"):
        shutil.copytree(
            SOURCE / name,
            engine / name,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "node_modules", "npm-logs", ".pytest_cache"
            ),
            dirs_exist_ok=True,
        )
    for name in (
        "distribution.py",
        "distribution.json",
        "pyproject.toml",
        "README.md",
        "DISTRIBUTION.md",
    ):
        shutil.copy2(SOURCE / name, engine / name)
    put(
        engine,
        ".gitignore",
        ".venv/\n.runtime/\n.changerail/\n__pycache__/\ntools/openspec/node_modules/\n",
    )
    for path in engine.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            path.chmod(0o755 if path.stat().st_mode & 0o111 else 0o644)
    git(engine, "add", ".")
    git(engine, "commit", "-qm", "isolated full source release fixture")
    git(engine, "tag", "fixture-v1")
    version = subprocess.check_output(
        [
            str(FIXTURE_PYTHON),
            "-I",
            "-S",
            "-c",
            "import sysconfig;print(sysconfig.get_python_version())",
        ],
        text=True,
    ).strip()
    put(
        engine,
        f".venv/lib/python{version}/site-packages/release_only.py",
        "VALUE = 'executor'\n",
    )
    put(
        engine,
        ".venv/pyvenv.cfg",
        f"home = {FIXTURE_PYTHON.parent}\ninclude-system-site-packages = false\n",
    )
    (engine / ".venv/bin").mkdir()
    (engine / ".venv/bin/python").symlink_to(FIXTURE_PYTHON)
    put(
        engine,
        "tools/openspec/node_modules/@fission-ai/openspec/package.json",
        '{"name":"@fission-ai/openspec","version":"1.3.1","type":"module"}',
    )
    put(
        engine,
        "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js",
        "console.log(JSON.stringify({cwd: process.cwd(),dependency: process.env.CHRL_PROJECT_ROOT}));\n",
    )
    receipt = release.inspect_release(
        engine, tag="fixture-v1", node=Path(shutil.which("node"))
    )
    release.receipt_path(engine).write_bytes(release.encoded(receipt))
    release.receipt_path(engine).chmod(0o600)
    put(project, ".gitignore", ".changerail/\n.runtime/\n.venv/\n__pycache__/\n")
    git(project, "add", ".gitignore")
    git(project, "commit", "-qm", "isolated consumer fixture")
    yield project, engine, receipt
    for root, fd in list(release._LEASES.items()):
        if root.is_relative_to(tmp_path):
            os.close(fd)
            del release._LEASES[root]
    monkeypatch.delenv(release.USE_FD, raising=False)


def test_full_checkout_launchers_select_executor_and_project(full_release):
    project, engine, receipt = full_release
    proposal = binding.prepare(project, engine)
    binding.apply(Path(proposal["proposal"]))
    result = subprocess.run(
        [str(project / ".changerail/chrl"), "--engine-root"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(engine)
    observed = subprocess.run(
        [str(project / ".changerail/openspec"), "status"],
        capture_output=True,
        text=True,
    )
    assert observed.returncode == 0, observed.stderr
    assert json.loads(observed.stdout) == {
        "cwd": str(project),
        "dependency": str(engine),
    }
    assert not (project / "bin/chrl").exists()
    assert (engine / "tools/changerail/tests/test_engine_runtime.py").exists()
    assert (engine / "scripts/public-surface-scan.py").exists()


def test_product_verification_imports_only_dev_and_uses_dev_environment(
    full_release, monkeypatch, tmp_path
):
    project, engine, receipt = full_release
    monkeypatch.setattr(d, "REPO_ROOT", project)
    value = {
        **release.binding_document(project, engine),
        "engine_identity": release.digest(release.encoded(receipt)),
        "release_receipt": receipt,
    }
    monkeypatch.setattr(runtime, "binding", lambda _: value)
    # Real lease is retained by supervisor throughout shell subprocess lifetime.
    release.ensure_use(engine)
    put(project, "dev_only.py", "VALUE = 'new-dev-feature'\n")
    put(
        project,
        ".venv/bin/python",
        '#!/bin/sh\nexport DEV_PYTHON_SELECTED=yes\nexec /usr/bin/python3 "$@"\n',
        0o755,
    )
    monkeypatch.setenv("PATH", str(engine / ".venv/bin") + ":/usr/bin:/bin")
    monkeypatch.setenv("PYTHONPATH", str(engine))
    code = "import dev_only, os, importlib.util; assert dev_only.VALUE == 'new-dev-feature'; assert os.environ['DEV_PYTHON_SELECTED'] == 'yes'; assert importlib.util.find_spec('release_only') is None; assert any('FLOCK' in row and 'READ' in row for row in open('/proc/self/fdinfo/' + os.environ['CHRL_ENGINE_USE_FD'])); print(dev_only.VALUE)"
    import shlex

    log = project / "verification.log"
    assert (
        d.run_shell_verification("python -c " + shlex.quote(code), log)["exit_code"]
        == 0
    )
    assert "new-dev-feature" in log.read_text()
    env = d.execution_env()
    assert env["PYTHONPATH"] == str(project)
    assert env["VIRTUAL_ENV"] == str(project / ".venv")


def test_v1_environment_and_subprocess_identity_are_unchanged(monkeypatch, tmp_path):
    monkeypatch.setattr(
        runtime,
        "binding",
        lambda _: {"engine_root": str(tmp_path), "engine_identity": "old"},
    )
    monkeypatch.setenv("PYTHONPATH", "original-path")
    monkeypatch.setenv("VIRTUAL_ENV", "original-venv")
    assert d.execution_env() == dict(os.environ)
    assert d.verification_command_identity("true") == {
        "kind": "shell",
        "argv": ["bash", "-lc", "true"],
        "shell_text": "true",
    }
    assert runtime.child_process_kwargs(tmp_path) == {}


def test_maintenance_cli_routes_exact_arguments_before_legacy_parser(monkeypatch):
    from scripts.changerail import release_update

    seen = []
    monkeypatch.setattr(release_update, "main", lambda args: seen.append(args) or 0)
    assert (
        dist.main(
            [
                "release-update",
                "prepare",
                "--root",
                "/generic/executor",
                "--tag",
                "fixture-v2",
            ]
        )
        == 0
    )
    assert seen == [["prepare", "--root", "/generic/executor", "--tag", "fixture-v2"]]
    monkeypatch.setenv(release.USE_FD, "7")
    assert dist.main(["release-update", "apply", "proposal.json"]) == 2
    assert len(seen) == 1


def test_v2_snapshot_recovery_has_explicit_unsupported_guard(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.setattr(d, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        runtime, "binding", lambda _: {"schema": release.BINDING_SCHEMA}
    )
    assert d.main(["self-host-recovery-prepare", str(tmp_path)]) == 2
    assert "snapshot-only recovery is unsupported" in capsys.readouterr().err


def test_release_source_diagnostics_are_specific(full_release, monkeypatch):
    project, engine, receipt = full_release
    monkeypatch.setattr(d, "REPO_ROOT", project)
    monkeypatch.setattr(
        runtime,
        "binding",
        lambda _: {
            "schema": release.BINDING_SCHEMA,
            "engine_root": str(engine),
            "engine_identity": "identity",
            "release_receipt": receipt,
        },
    )
    value = d.execution_source_info()
    assert value["project_root"] == str(project)
    assert value["source_root"] == str(engine)
    assert value["version"] == receipt["release"]["version"]
    assert value["revision"] == git(engine, "rev-parse", "HEAD")
    assert value["sha256"] == receipt["distribution"]["payload_sha256"]


@pytest.mark.parametrize("dependency_change", [False, True])
def test_release_update_cli_excludes_use_lease_and_selects_next_release(
    full_release, tmp_path, capsys, dependency_change
):
    from scripts.changerail import release_update

    project, engine, before = full_release
    bound = binding.prepare(project, engine)
    binding.apply(Path(bound["proposal"]))
    original_binding = (project / release.BINDING).read_bytes()
    put(
        engine,
        "README.md",
        (engine / "README.md").read_text() + "\nFixture next release.\n",
    )
    if dependency_change:
        put(
            engine,
            "pyproject.toml",
            (engine / "pyproject.toml").read_text()
            + "\n# New dependency declaration fixture.\n",
        )
        git(engine, "add", "pyproject.toml")
    git(engine, "add", "README.md")
    git(engine, "commit", "-qm", "isolated next release")
    git(engine, "tag", "fixture-v2")
    archive = tmp_path / "runtime.tar.gz"
    built = dist.build(engine, archive)
    provenance = put(
        tmp_path,
        "release-provenance.json",
        json.dumps(
            {
                "schema": "changerail.release-provenance.v1",
                "version": built["version"],
                "planned_tag": "fixture-v2",
                "source_commit": git(engine, "rev-parse", "HEAD"),
                "source_tree": git(engine, "rev-parse", "HEAD^{tree}"),
                "archive": archive.name,
                "archive_sha256": built["sha256"],
                "payload_sha256": built["payload_sha256"],
                "source_url": "https://example.invalid/operator-selected-release",
            }
        ),
    )
    git(engine, "checkout", "-q", "fixture-v1")
    proposal = tmp_path / "update"
    args = [
        "release-update",
        "prepare",
        "--root",
        str(engine),
        "--archive",
        str(archive),
        "--provenance",
        str(provenance),
        "--tag",
        "fixture-v2",
        "--proposal",
        str(proposal),
        "--node",
        shutil.which("node"),
    ]
    assert dist.main([*args, "--dry-run"]) == 0
    assert not proposal.exists()
    assert git(engine, "rev-parse", "HEAD") == before["release"]["commit"]
    assert dist.main(args) == 0
    code = "import sys;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from scripts.changerail import release_executor as r;r.ensure_use(Path(sys.argv[2]));print('ready',flush=True);input()"
    child = subprocess.Popen(
        ["/usr/bin/python3", "-I", "-S", "-B", "-c", code, str(SOURCE), str(engine)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout.readline().strip() == "ready"
        assert dist.main(["release-update", "apply", str(proposal)]) == 2
        assert not release_update.maintenance_path(engine).exists()
    finally:
        child.communicate("done\n", timeout=10)
    if dependency_change:
        assert dist.main(["release-update", "apply", str(proposal)]) == 2
        assert release_update.maintenance_path(engine).exists()
        blocked = subprocess.run(
            [str(project / ".changerail/chrl"), "--engine-root"],
            capture_output=True,
            text=True,
        )
        assert blocked.returncode != 0
        assert "maintenance" in blocked.stderr
        with release_update.provisioning(proposal):
            site = Path(before["dependencies"]["python"]["site_packages"])
            put(
                site,
                "new_provisioned_dependency.py",
                "VALUE = 'explicitly provisioned'\n",
            )
        assert dist.main(["release-update", "reconcile", str(proposal)]) == 0
        current = release.verify_release(engine)
        assert current["dependencies"] != before["dependencies"]
    else:
        assert dist.main(["release-update", "apply", str(proposal)]) == 0
    assert release.verify_release(engine)["release"]["tag"] == "fixture-v2"
    assert (project / release.BINDING).read_bytes() == original_binding
    assert subprocess.check_output(
        [str(project / ".changerail/chrl"), "--engine-root"], text=True
    ).strip() == str(engine)
    assert not release_update.maintenance_path(engine).exists()


def test_isolated_executor_python_verifies_new_dev_feature(full_release):
    import shlex

    project, engine, old = full_release
    site = Path(old["dependencies"]["python"]["site_packages"])
    # Provision only existing runtime packages into the temporary closed executor.
    # No installer/network call and no access to the real project's credentials.
    copy_runtime_dependencies(site)
    receipt = release.inspect_release(
        engine, tag="fixture-v1", node=Path(shutil.which("node"))
    )
    release.receipt_path(engine).write_bytes(release.encoded(receipt))
    prepared = binding.prepare(project, engine)
    binding.apply(Path(prepared["proposal"]))
    put(
        project,
        ".changerail/profile.toml",
        "schema = 'changerail.local-delivery.v1'\n[project]\nname = 'fixture'\n",
    )
    put(project, "dev_only.py", "VALUE = 'only present in new dev code'\n")
    put(
        project,
        ".venv/bin/python",
        '#!/bin/sh\nexport DEV_PYTHON_SELECTED=yes\nexec /usr/bin/python3 "$@"\n',
        0o755,
    )
    command = "python -c " + shlex.quote(
        "import dev_only,os,importlib.util; assert dev_only.VALUE == 'only present in new dev code'; assert os.environ['DEV_PYTHON_SELECTED'] == 'yes'; assert importlib.util.find_spec('release_only') is None; print(dev_only.VALUE)"
    )
    python = receipt["dependencies"]["python"]
    search = [
        str(engine),
        str(site),
        python["stdlib_root"],
        str(Path(python["stdlib_root"]) / "lib-dynload"),
    ]
    code = (
        f"import sys;sys.path[:]={search!r};from pathlib import Path;"
        f"from scripts.changerail import release_executor as r;r.ensure_use(Path({str(engine)!r}));"
        "from scripts.changerail import local_delivery as d;"
        f"assert d.execution_source_info()['source_root']=={str(engine)!r};"
        f"result=d.run_shell_verification({command!r},Path({str(project / 'isolated.log')!r}));"
        "assert result['exit_code']==0,result;"
        "assert sys.flags.isolated and sys.flags.no_site;print('isolated executor passed')"
    )
    result = subprocess.run(
        [python["path"], "-I", "-S", "-B", "-c", code],
        cwd=project,
        env={
            **os.environ,
            "CHRL_PROJECT_ROOT": str(project),
            "CHRL_ENGINE_ROOT": str(engine),
            "PATH": str(engine / ".venv/bin") + ":/usr/bin:/bin",
            "PYTHONPATH": str(engine),
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "isolated executor passed" in result.stdout
    assert "only present in new dev code" in (project / "isolated.log").read_text()


def closed_executor(full_release):
    """Accepted real runtime packages and a fresh subprocess (no pytest lease leak)."""
    project, engine, before = full_release
    site = Path(before["dependencies"]["python"]["site_packages"])
    copy_runtime_dependencies(site)
    receipt = release.inspect_release(
        engine, tag="fixture-v1", node=Path(shutil.which("node"))
    )
    release.receipt_path(engine).write_bytes(release.encoded(receipt))
    proposal = binding.prepare(project, engine)
    binding.apply(Path(proposal["proposal"]))
    put(
        project,
        ".changerail/profile.toml",
        "schema = 'changerail.local-delivery.v1'\n[project]\nname = 'fixture'\n",
    )
    python = receipt["dependencies"]["python"]
    search = [
        str(engine),
        str(site),
        python["stdlib_root"],
        str(Path(python["stdlib_root"]) / "lib-dynload"),
    ]
    prefix = (
        f"import sys;sys.path[:]={search!r}\nfrom pathlib import Path\n"
        f"from scripts.changerail import release_executor as r;r.ensure_use(Path({str(engine)!r}))\n"
        "from scripts.changerail import local_delivery as d\n"
        "from scripts.changerail import engine_runtime as runtime\n"
        "d.execution_source_info()\n"
    )
    env = {
        **os.environ,
        "CHRL_PROJECT_ROOT": str(project),
        "CHRL_ENGINE_ROOT": str(engine),
        "PATH": str(engine / ".venv/bin") + ":/usr/bin:/bin",
        "PYTHONPATH": str(engine),
    }
    for key in (release.USE_FD, "CHRL_RUN_DIR", "CHRL_SESSION_ROLE"):
        env.pop(key, None)

    def command(body):
        return [python["path"], "-I", "-S", "-B", "-c", prefix + body]

    return project, engine, receipt, command, env


def test_actual_codex_launcher_preserves_arbitrary_user_dispatcher(
    full_release, monkeypatch, tmp_path
):
    project, engine, _ = full_release
    (project / "bin").mkdir()
    shutil.copy2(SOURCE / "bin/codex", project / "bin/codex")
    custom = tmp_path / "operator-tools"
    put(
        custom,
        "codex",
        '#!/bin/sh\nprintf "operator-dispatcher\\n"\nprintf "%s\\n" "$@"\n',
        0o755,
    )
    monkeypatch.setattr(d, "REPO_ROOT", project)
    monkeypatch.setattr(
        runtime, "binding", lambda _: release.binding_document(project, engine)
    )
    monkeypatch.setenv(
        "PATH", str(engine / ".venv/bin") + ":" + str(custom) + ":/usr/bin:/bin"
    )
    monkeypatch.delenv("CHANGERAIL_CODEX_BIN", raising=False)
    monkeypatch.delenv("CODEX_WORKDIR", raising=False)
    env = d.execution_env()
    assert str(project / "bin") not in env["PATH"].split(os.pathsep)
    assert str(custom) in env["PATH"].split(os.pathsep)
    assert str(engine / ".venv/bin") not in env["PATH"].split(os.pathsep)
    result = subprocess.run(
        [str(project / "bin/codex"), "--version"],
        env=env,
        text=True,
        capture_output=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "operator-dispatcher",
        "-C",
        str(project),
        "--version",
    ]


def test_real_supervised_product_child_excludes_independent_updater(
    full_release, tmp_path
):
    import shlex
    import time

    project, engine, _, command, env = closed_executor(full_release)
    ready = tmp_path / "child-ready"
    child_code = (
        "import os;from pathlib import Path;"
        "fd=os.environ['CHRL_ENGINE_USE_FD'];"
        "assert any('FLOCK' in row and 'READ' in row for row in Path('/proc/self/fdinfo/'+fd).read_text().splitlines());"
        f"Path({str(ready)!r}).write_text('lease inherited');input()"
    )
    shell = shlex.join(["/usr/bin/python3", "-I", "-S", "-c", child_code])
    body = f"result=d.run_shell_verification({shell!r},Path({str(project / 'check.log')!r}));assert result['exit_code']==0,result\n"
    supervisor = subprocess.Popen(
        command(body),
        cwd=project,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # The independent updater uses the very same exclusive gate as release_update.
    updater = [
        "/usr/bin/python3",
        "-I",
        "-S",
        "-B",
        "-c",
        "import sys;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from scripts.changerail import release_executor as r\nwith r.exclusive_use(Path(sys.argv[2])): print('exclusive acquired')",
        str(SOURCE),
        str(engine),
    ]
    try:
        deadline = time.monotonic() + 15
        while (
            not ready.exists()
            and supervisor.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.02)
        assert ready.exists(), "supervised child did not become ready"
        busy = subprocess.run(updater, capture_output=True, text=True, timeout=5)
        assert busy.returncode != 0 and "lease" in busy.stderr.lower()
    finally:
        stdout, stderr = supervisor.communicate("done\n", timeout=15)
    assert supervisor.returncode == 0, (stdout, stderr)
    after = subprocess.run(updater, capture_output=True, text=True, timeout=5)
    assert after.returncode == 0, after.stderr
    assert "exclusive acquired" in after.stdout
    assert engine not in release._LEASES


def test_maintenance_help_and_binding_preview_leave_no_durable_proposal(full_release):
    project, engine, _ = full_release
    cli = ["/usr/bin/python3", "-B", str(SOURCE / "distribution.py")]
    for arguments, expected in [
        (["--help"], ["release-update", "executor-bind"]),
        (["release-update", "prepare", "--help"], ["--dry-run", "--provenance"]),
        (["executor-bind", "prepare", "--help"], ["--previous-identity", "--dry-run"]),
    ]:
        result = subprocess.run(
            [*cli, *arguments], capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0, result.stderr
        assert all(word in result.stdout for word in expected)
    result = subprocess.run(
        [
            *cli,
            "executor-bind",
            "prepare",
            "--project",
            str(project),
            "--executor",
            str(engine),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert not Path(json.loads(result.stdout)["proposal"]).exists()
    assert not (project / release.BINDING).exists()


def test_real_v2_pytest_receipt_selected_nodes_and_current_set(full_release):
    import shlex
    import sys

    project, engine, _, command, env = closed_executor(full_release)
    put(
        project,
        ".venv/bin/python",
        "#!/bin/sh\nexec " + shlex.quote(sys.executable) + ' "$@"\n',
        0o755,
    )
    put(project, "dev_feature.py", "VALUE = 'new dev behavior'\n")
    put(
        project,
        "tests/test_dev.py",
        "from dev_feature import VALUE\ndef test_new_behavior():\n    before_state = VALUE\n    action_state = before_state.upper()\n    after_state = action_state.lower()\n    assert before_state == 'new dev behavior'\n    assert action_state == 'NEW DEV BEHAVIOR'\n    assert after_state == 'new dev behavior'\n",
    )
    plan = {
        "schema": "changerail.card-evidence.v1",
        "conditions": [
            {
                "condition": "C1",
                "seam": "dev execution",
                "precondition": "new dev code",
                "action": "run pytest",
                "expected": "dev behavior verified",
                "method": {
                    "kind": "test",
                    "target": "tests/test_dev.py::test_new_behavior",
                },
                "stage": "final",
            }
        ],
        "risks": [
            {
                "kinds": [kind],
                "applies": False,
                "decision": "isolated fixture",
                "conditions": [],
            }
            for kind in (
                "input_safety",
                "mutation",
                "restart",
                "concurrency",
                "publication",
                "external_effects",
            )
        ],
    }
    put(
        project,
        "card.md",
        "# Fixture verification\n\n## Acceptance\n\n### Requirement: dev code\n\n#### Scenario: observed test\n\n- [C1] WHEN new dev code is tested\n\n## Design\n\n- Isolated verification fixture.\n\n## Verify\n\n```json\n"
        + json.dumps(plan)
        + "\n```\n",
    )
    git(project, "add", "dev_feature.py", "tests/test_dev.py", "card.md")
    git(project, "commit", "-qm", "isolated product test")
    run = project / ".runtime/changerail/runs/fixture"
    put(
        project,
        ".runtime/changerail/runs/fixture/run.json",
        json.dumps({"run_id": "fixture", "card": "card.md"}),
    )
    (run / "verification/cycle-1").mkdir(parents=True)
    shell = (
        "python -m pytest -p no:cacheprovider -v tests/test_dev.py::test_new_behavior"
    )
    body = f"""
import json
from scripts.changerail.adapters.results import receipt_nodes, validate_selected_nodes
run=Path({str(run)!r});card=d.REPO_ROOT/'card.md';shell={shell!r}
with d.verification_attempt_lock(run,card,'final'):
    row=d.run_shell_verification(shell,run/'verification/cycle-1/pytest.log',proof=(run,'final'))
assert row['exit_code']==0 and row['verified'],row
fingerprint=d.payload_fingerprint()
index={{'schema':'changerail.final-verification.v1','ok':True,'card':{{'id':'card','path':'card.md'}},'verified_at':d.utc_now(),'fingerprint':fingerprint,'configured_commands':[shell],'commands':[row]}}
d.write_json(run/'verification.json',index)
verified=d._verified_command_set(run/'verification.json',run,card,fingerprint,[shell],'final')
assert verified is not None,'configured receipt identity mismatch'
item,log,_=verified.receipts[0]
assert item['command_identity']==d.verification_command_identity(shell)
assert item['command_identity']['argv']==['bash','-c',shell]
target='tests/test_dev.py::test_new_behavior'
nodes=receipt_nodes(d.REPO_ROOT,{{}},item,log,target)
assert [n['node'] for n in nodes]==[target]
assert target in validate_selected_nodes(d.REPO_ROOT,{{}},log,item['command_identity'],target,nodes,label='observed test proof')
assert all(b'PASSED' in log[n['start']:n['end']] for n in nodes)
assert d._successful_verification_matches(run/'verification.json',card=card,fingerprint=fingerprint,commands=[shell],run_dir=run,lane='final')
# Validate a full observed card-proof with actual source assertion fragments.
import hashlib
inventory=d.derive_proof_inventory(card);condition=inventory['conditions'][0]
def reference(path):
    data=path.read_bytes()
    return {{'path':d.repo_relative(path),'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}}
source=d.REPO_ROOT/'tests/test_dev.py';source_data=source.read_bytes();fragments={{}}
for name in ('before','action','after'):
    start=source_data.index(('assert '+name+'_state').encode());end=source_data.index(b'\\n',start)+1
    fragments[name]={{**reference(source),'start':start,'end':end,'fragment_sha256':hashlib.sha256(source_data[start:end]).hexdigest()}}
proof={{'schema':'changerail.card-proof.v1','run':d._check_owner(run),'inventory_digest':inventory['digest'],'payload':fingerprint,'condition':condition['identity'],'method':condition['method'],'stage':'final','observation_id':'outer-C1','recorder_role':'outer','kind':'test','outcome':'pass','artifact':reference(d.REPO_ROOT/row['record']),'fragments':fragments,'assertion_support':{{'source':reference(source),'fragments':fragments}},'lane':'final','attempt_id':item['attempt_id'],'command_identity':item['command_identity'],'selected_nodes':nodes}}
d._validate_observed_proof(proof,card=card,run_dir=run,inventory=inventory,role='outer')
d._require_final_test_receipt_membership([proof],verified)
d.write_json(run/'observed-proof.json',proof)
# A receipt using a different shell mode cannot be reused for the selected v2 mode.
record=d.REPO_ROOT/row['record']; changed=json.loads(record.read_text());changed['command_identity']['argv'][1]='-lc';d.write_json(record,changed)
assert d._verified_command_set(run/'verification.json',run,card,fingerprint,[shell],'final') is None
print('current selected PASSED proof validated')
"""
    result = subprocess.run(
        command(body), env=env, cwd=project, capture_output=True, text=True, timeout=45
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "current selected PASSED proof validated" in result.stdout


@pytest.mark.parametrize("mode", ["-c", "-lc"])
def test_shell_pytest_grammar_and_protocol_recognizers_remain_closed(mode):
    import shlex
    from scripts.changerail.adapters.pytest import _is_pytest_command_identity

    safe = "python -m pytest -v tests/test_one.py"
    assert _is_pytest_command_identity(
        {"kind": "shell", "argv": ["bash", mode, safe], "shell_text": safe}
    )
    for unsafe in (
        safe + "; echo PASSED",
        "echo pytest",
        safe + " | cat",
        "$(printf pytest)",
        safe + " > result.log",
        safe + " && true",
    ):
        assert not _is_pytest_command_identity(
            {"kind": "shell", "argv": ["bash", mode, unsafe], "shell_text": unsafe}
        )
    assert not _is_pytest_command_identity(
        {"kind": "shell", "argv": ["bash", "-ic", safe], "shell_text": safe}
    )
    for text, check in [
        ("./bin/chrl verdict validate card", d.is_review_protocol_command),
        ("./bin/chrl handoff card", d.is_delivery_protocol_command),
        ("./bin/chrl review card", d.is_review_wrapper_command),
    ]:
        assert check(shlex.join(["bash", mode, text]))
        assert not check(shlex.join(["bash", mode, text + "; true"]))


def test_git_fd_propagation_does_not_rehash_but_full_checks_still_detect_drift(
    full_release,
):
    project, engine, _, command, env = closed_executor(full_release)
    body = """
import json,time
calls=[]
verify=r.verify_release

def counted(*a,**kw):
    calls.append(1)
    return verify(*a,**kw)
r.verify_release=counted
fast=runtime.child_process_kwargs

def previous_cost(project):
    value=runtime.binding(project)
    return r.child_process_kwargs(Path(value['engine_root']))

def measure(helper):
    runtime.child_process_kwargs=helper
    start=time.monotonic();before=len(calls)
    for _ in range(5):
        assert d.git('rev-parse','HEAD').returncode==0
    return {'seconds':time.monotonic()-start,'full_verifications':len(calls)-before}

baseline=measure(previous_cost)
optimized=measure(fast)
assert baseline['full_verifications']==5
assert optimized['full_verifications']==0
print(json.dumps({'baseline':baseline,'optimized':optimized}),flush=True)
# The fast helper re-reads binding authority, not a cached binding result.
path=d.REPO_ROOT/'.changerail/engine-binding.json';before=path.read_bytes()
changed=json.loads(before);changed['kind']='foreign';path.write_text(json.dumps(changed))
try:
    runtime.child_process_kwargs(d.REPO_ROOT)
except (ValueError,d.DeliveryError): pass
else: raise AssertionError('changed binding accepted by FD propagation')
path.write_bytes(before)
# Full binding/frozen checks still inspect exact runtime after a prior fast call.
source=Path(d._SOURCE_REPO_ROOT)/'scripts/changerail/injected.py'
source.write_text('INJECTED = True\\n')
try:
    runtime.binding(d.REPO_ROOT)
except (ValueError,d.DeliveryError): pass
else: raise AssertionError('full verification cached through source drift')
assert runtime._VERIFIED_USE is None
"""
    result = subprocess.run(
        command(body), cwd=project, env=env, capture_output=True, text=True, timeout=45
    )
    assert result.returncode == 0, result.stderr
    measured = json.loads(result.stdout.splitlines()[0])
    print("git propagation measurement: " + json.dumps(measured, sort_keys=True))
    assert measured["optimized"]["full_verifications"] == 0
    assert engine not in release._LEASES


def test_supported_release_cli_refuses_dual_source_binding(full_release):
    project, engine, _ = full_release
    prepared = binding.prepare(project, engine)
    binding.apply(Path(prepared["proposal"]))
    put(project, ".changerail/source-link.json", "{}")
    result = subprocess.run(
        [str(project / ".changerail/chrl"), "--engine-root"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert "shared-source binding" in result.stderr


def release_prepare_arguments(engine, directory, proposal):
    """Real archive/provenance for the fixture's already accepted Git tag."""
    archive = directory / "runtime.tar.gz"
    built = dist.build(engine, archive)
    provenance = put(
        directory,
        "release-provenance.json",
        json.dumps(
            {
                "schema": "changerail.release-provenance.v1",
                "version": built["version"],
                "planned_tag": "fixture-v1",
                "source_commit": git(engine, "rev-parse", "HEAD"),
                "source_tree": git(engine, "rev-parse", "HEAD^{tree}"),
                "archive": archive.name,
                "archive_sha256": built["sha256"],
                "payload_sha256": built["payload_sha256"],
                "source_url": "https://example.invalid/operator-selected-release",
            }
        ),
    )
    return [
        "release-update", "prepare", "--root", str(engine),
        "--archive", str(archive), "--provenance", str(provenance),
        "--tag", "fixture-v1", "--proposal", str(proposal),
        "--node", shutil.which("node"),
    ]


def maintenance_environment():
    env = os.environ.copy()
    # Ordinary supported invocation, without pytest's inherited bytecode guard.
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    return env


def test_release_preview_uses_intended_filesystem_despite_foreign_tmpdir(
    full_release, tmp_path
):
    import tempfile
    from scripts.changerail import release_update

    _, engine, receipt = full_release
    foreign = Path("/dev/shm")
    if not foreign.is_dir() or foreign.stat().st_dev == engine.stat().st_dev:
        pytest.skip("requires a writable second filesystem for actual CLI staging")
    parent = tmp_path / "private-receipts"
    parent.mkdir(mode=0o700)
    proposal = parent / "intended"
    args = release_prepare_arguments(engine, tmp_path, proposal)
    before = release_update._inventory(engine)
    with tempfile.TemporaryDirectory(prefix="changerail-preview-test-", dir=foreign) as directory:
        env = maintenance_environment()
        env["TMPDIR"] = directory
        result = subprocess.run(
            [str(engine / "bin/chrl-dist"), *args, "--dry-run"],
            env=env, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["proposal"] == str(proposal)
        assert json.loads(result.stdout)["dry_run"] is True
        assert list(Path(directory).iterdir()) == []
    assert list(parent.iterdir()) == []
    assert release_update._inventory(engine) == before
    assert release.verify_release(engine) == receipt


def test_release_preview_validates_real_proposal_parent(full_release, tmp_path):
    import tempfile
    from scripts.changerail import release_update

    _, engine, _ = full_release
    args = release_prepare_arguments(engine, tmp_path, tmp_path / "unused")
    before = release_update._inventory(engine)
    invalid = [(tmp_path / "missing" / "proposal", "No such file"),
               (engine / "proposal", "outside target")]
    # A distinct filesystem is optional; missing/inside paths always exercise
    # the same actual CLI validation for dry-run and real prepare.
    foreign = Path("/dev/shm")
    with tempfile.TemporaryDirectory(prefix="changerail-parent-test-", dir=foreign if foreign.is_dir() else tmp_path) as directory:
        if Path(directory).stat().st_dev != engine.stat().st_dev:
            invalid.append((Path(directory) / "proposal", "share target filesystem"))
        for proposal, message in invalid:
            actual = list(args)
            actual[actual.index("--proposal") + 1] = str(proposal)
            for flags in (["--dry-run"], []):
                result = subprocess.run(
                    [str(engine / "bin/chrl-dist"), *actual, *flags],
                    env=maintenance_environment(), capture_output=True, text=True, timeout=10,
                )
                assert result.returncode == 2, result.stdout
                assert message in result.stderr
                assert not proposal.exists()
    assert release_update._inventory(engine) == before


@pytest.mark.parametrize("direct_python", [False, True])
def test_accepted_maintenance_entrypoint_never_writes_source_bytecode(
    full_release, tmp_path, direct_python
):
    from scripts.changerail import release_update

    _, engine, receipt = full_release
    proposal = tmp_path / "prepared"
    args = release_prepare_arguments(engine, tmp_path, proposal)
    cli = (["/usr/bin/python3", str(engine / "distribution.py")] if direct_python
           else [str(engine / "bin/chrl-dist")])
    before = release_update._inventory(engine)
    accepted = release.receipt_path(engine).read_bytes()
    index = (engine / ".git/index").read_bytes()
    for command in (["--help"], ["release-update", "--help"],
                    ["executor-bind", "--help"], [*args, "--dry-run"], args):
        result = subprocess.run(
            [*cli, *command], env=maintenance_environment(),
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert release_update._inventory(engine) == before
        assert release.receipt_path(engine).read_bytes() == accepted
        assert (engine / ".git/index").read_bytes() == index
        assert release.verify_release(engine) == receipt
        assert not list((engine / "scripts").rglob("__pycache__"))
    assert (proposal / "proposal.json").exists()
    proposal_before = release_update._inventory(proposal)
    # Eager imports do not authorize mutating the coordinator underneath itself.
    for command in ("apply", "reconcile", "provision-lease"):
        result = subprocess.run(
            [*cli, "release-update", command, "--", str(proposal)],
            env=maintenance_environment(), capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 2, result.stdout
        assert "coordinator outside target checkout" in result.stderr
        assert release_update._inventory(engine) == before
        assert release_update._inventory(proposal) == proposal_before
        assert not release_update.maintenance_path(engine).exists()
