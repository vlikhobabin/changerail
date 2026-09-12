"""Separate a receipt-bound execution engine from the mutable project."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError

BINDING = ".changerail/engine-binding.json"
RUNTIME_PREFIXES = (
    "scripts/changerail/",
    "tools/changerail/schemas/",
    "tools/changerail/skills/",
    "tools/openspec/",
)
RUNTIME_FILES = {"scripts/__init__.py", "bin/chrl", "bin/chrl-run", "bin/openspec"}


# This is only a capability for descriptor propagation, never an identity cache.
# Every binding()/identity()/require_run() still performs full verification.
_VERIFIED_USE: tuple[Path, dict[str, str], int] | None = None


def _ensure_no_pending(project: Path) -> None:
    transitions = project / ".runtime/changerail/executor-bindings"
    if transitions.is_symlink() or any(
        intent.is_symlink() or not (intent.parent / "applied.json").is_file()
        for intent in transitions.glob("*/intent.json")
    ):
        raise DeliveryError("pending executor binding requires reconcile")


def binding(project: Path) -> dict[str, Any] | None:
    global _VERIFIED_USE
    _VERIFIED_USE = None
    _ensure_no_pending(project)
    path = project / BINDING
    if not path.exists() and not path.is_symlink():
        if os.environ.get("CHRL_ENGINE_ROOT"):
            raise DeliveryError("engine environment requires an explicit binding")
        return None
    # Dispatch explicitly; v1 verification and identity remain unchanged.
    from scripts.changerail import release_executor as release

    try:
        header = release.document(path)
        if header.get("schema") == release.BINDING_SCHEMA:
            if os.path.lexists(project / ".changerail/source-link.json"):
                raise DeliveryError(
                    "release executor cannot overlap a shared-source binding"
                )
            value = release.verify_binding(
                project, expected_engine=Path(__file__).resolve().parents[2]
            )
            release.require_runtime_source(
                Path(value["engine_root"]), value["release_receipt"]
            )
            selected = os.environ.get("CHRL_ENGINE_ROOT")
            if selected is not None and selected != value["engine_root"]:
                raise DeliveryError("engine environment differs from binding")
            fd = release.child_process_kwargs(Path(value["engine_root"]))["pass_fds"][0]
            _VERIFIED_USE = (
                project,
                {
                    key: value[key]
                    for key in ("schema", "kind", "project_root", "engine_root")
                },
                fd,
            )
            return value
    except (release.ReleaseExecutorError, OSError, ValueError) as exc:
        raise DeliveryError(f"invalid release engine binding: {exc}") from exc
    from scripts.changerail.engine_snapshot import verify_binding, EngineSnapshotError

    try:
        value = verify_binding(project)
    except (EngineSnapshotError, OSError, ValueError) as exc:
        raise DeliveryError(f"invalid engine binding: {exc}") from exc
    selected = os.environ.get("CHRL_ENGINE_ROOT")
    if selected is not None and selected != value["engine_root"]:
        raise DeliveryError("engine environment differs from binding")
    return value


def require_engine(project: Path) -> dict[str, Any]:
    value = binding(project)
    if (
        value is None
        or Path(value["engine_root"]) != Path(__file__).resolve().parents[2]
    ):
        raise DeliveryError("self-host must execute from the bound engine")
    return value


def require_run(project: Path) -> None:
    """Validate nested commands against the run's frozen execution inputs."""
    if binding(project) is None or not os.environ.get("CHRL_RUN_DIR"):
        return
    require_engine(project)
    from scripts.changerail import local_delivery as delivery

    if delivery.REPO_ROOT != project:
        raise DeliveryError("nested command project differs from execution owner")
    delivery.require_frozen_execution(Path(os.environ["CHRL_RUN_DIR"]))


def runtime_path(project: Path, path: Path) -> Path:
    try:
        relative = path.relative_to(project).as_posix()
    except ValueError:
        return path
    if relative not in RUNTIME_FILES and not relative.startswith(RUNTIME_PREFIXES):
        return path
    # Installed OpenSpec dependencies are project execution inputs. Helpers,
    # schemas and runner source come from the snapshot.
    value = binding(project)
    if relative.startswith("tools/openspec/node_modules/") and not is_release(value):
        return path
    return Path(value["engine_root"]) / relative if value else path


def is_release(value: dict[str, Any] | None) -> bool:
    return value is not None and value.get("schema") == "changerail.engine-binding.v2"


def dependency_root(project: Path) -> Path:
    value = binding(project)
    return (
        Path(value["engine_root"]) if is_release(value) else project
    ) / "tools/openspec"


def runner_python(project: Path) -> Path:
    value = binding(project)
    return (
        Path(value["release_receipt"]["dependencies"]["python"]["path"])
        if is_release(value)
        else Path(sys.executable)
    )


def child_process_kwargs(project: Path) -> dict[str, Any]:
    """Parent integration: pass to every supervised session/check subprocess."""
    from scripts.changerail import release_executor as release

    if _VERIFIED_USE is not None and _VERIFIED_USE[0] == project:
        # No runtime hashing just to forward an already verified, continuously
        # held descriptor. Re-read binding and validate the kernel lease each time.
        # Full frozen checks deliberately do not consult this capability.
        _, expected, fd = _VERIFIED_USE
        root = Path(expected["engine_root"])
        _ensure_no_pending(project)
        if os.path.lexists(project / ".changerail/source-link.json"):
            raise DeliveryError(
                "release executor cannot overlap a shared-source binding"
            )
        if release.read_binding(project, expected_engine=root) != expected:
            raise DeliveryError("binding changed during executor use")
        if os.environ.get(release.USE_FD) != str(fd) or os.environ.get(
            "CHRL_ENGINE_ROOT", str(root)
        ) != str(root):
            raise DeliveryError("executor propagation environment changed")
        release._check_maintenance(root)
        release._validate_fd(root, fd)
        kwargs = release.child_process_kwargs(root)
        if kwargs["pass_fds"] != (fd,):
            raise DeliveryError("executor propagation lease changed")
        return kwargs
    value = binding(project)
    if not is_release(value):
        return {}
    return release.child_process_kwargs(Path(value["engine_root"]))


def release_identity(delivery: Any, value: dict[str, Any]) -> dict[str, str]:
    from scripts.changerail.release_executor import digest, encoded

    receipt = value["release_receipt"]
    result = {
        "engine/mode": "release-checkout-v1",
        "engine/identity": value["engine_identity"],
        "engine/root": digest(value["engine_root"].encode()),
        "engine/release-tag": receipt["release"]["tag"],
        "engine/release-commit": receipt["release"]["commit"],
        "engine/release-tree": receipt["release"]["tree"],
        "engine/release-version": receipt["release"]["version"],
        "engine/runtime-inventory": receipt["distribution"]["payload_sha256"],
        "engine/dependencies": digest(encoded(receipt["dependencies"])),
        "python/executable": receipt["dependencies"]["python"]["file"]["sha256"],
    }
    result.update(
        {"project/" + k: v for k, v in project_execution_identity(delivery).items()}
    )
    for relative in (
        BINDING,
        ".changerail/distribution-lock.json",
        ".changerail/source-link.json",
    ):
        path = delivery.REPO_ROOT / relative
        if path.exists() or path.is_symlink():
            result["project/" + relative] = digest(
                delivery._check_bytes(path, 32 * 1024 * 1024)
            )
    return result


def openspec_process(project: Path) -> tuple[Path, dict[str, str], dict[str, Any]]:
    """Verified Node plus helper dependency selector; cwd stays the project.

    Existing helpers use CHRL_PROJECT_ROOT to locate dependencies. Give only the
    helper subprocess the executor root in release mode; artifact operations use
    cwd. No project/profile selection is changed in the supervising process.
    """
    import shutil

    value = binding(project)
    if is_release(value):
        from scripts.changerail.release_executor import USE_FD, child_process_kwargs

        root = Path(value["engine_root"])
        kwargs = child_process_kwargs(root)
        return (
            Path(value["release_receipt"]["dependencies"]["node"]["path"]),
            {
                "CHRL_PROJECT_ROOT": str(root),
                USE_FD: os.environ[USE_FD],
            },
            kwargs,
        )
    node = shutil.which("node")
    if node is None:
        raise DeliveryError("Node.js executable missing from PATH")
    return Path(node).resolve(strict=True), {"CHRL_PROJECT_ROOT": str(project)}, {}


def exec_openspec(project: Path, args: list[str]) -> int:
    """Supervise helper and exec Node with the same inheritable use lease."""
    import subprocess

    require_run(project)
    node, extra, kwargs = openspec_process(project)
    dependency = dependency_root(project)
    helper = runtime_path(project, project / "tools/openspec/check-install.mjs")
    env = {
        "PATH": "/usr/bin:/bin",
        "OPENSPEC_TELEMETRY": "0",
        "DO_NOT_TRACK": "1",
        "CI": "true",
        "OPENSPEC_NO_COMPLETIONS": "1",
        "OPENSPEC_NO_AUTO_CONFIG": "1",
        "OPENSPEC_NO_UPDATE_CHECK": "1",
        "NO_UPDATE_NOTIFIER": "1",
        "npm_config_update_notifier": "false",
        **extra,
    }
    checked = subprocess.run([str(node), str(helper)], cwd=project, env=env, **kwargs)
    if checked.returncode:
        return checked.returncode
    os.chdir(project)
    os.execve(
        str(node),
        [
            str(node),
            str(dependency / "node_modules/@fission-ai/openspec/bin/openspec.js"),
            *args,
        ],
        env,
    )
    return 2


def project_execution_identity(delivery: Any) -> dict[str, str]:
    """Old-compatible authority keys kept frozen across a self-host transition."""
    launcher = (
        delivery.profile()
        .get("adapters", {})
        .get("codex", {})
        .get("launcher", "bin/codex")
    )
    paths = {delivery.PROFILE_PATH, delivery.REPO_ROOT / delivery._safe_path(launcher)}
    paths.update(
        p
        for p in (delivery.REPO_ROOT / ".changerail/adapters").rglob("*")
        if p.is_file() or p.is_symlink()
    )
    return {
        p.relative_to(delivery.REPO_ROOT).as_posix(): hashlib.sha256(
            delivery._check_bytes(p, 32 * 1024 * 1024)
        ).hexdigest()
        for p in sorted(paths)
    }


def identity(delivery: Any) -> dict[str, str] | None:
    value = binding(delivery.REPO_ROOT)
    if value is None:
        return None
    engine = Path(value["engine_root"])
    if engine != delivery._SOURCE_REPO_ROOT:
        raise DeliveryError("self-host must execute from the bound engine")
    if is_release(value):
        return release_identity(delivery, value)
    launcher = (
        delivery.profile()
        .get("adapters", {})
        .get("codex", {})
        .get("launcher", "bin/codex")
    )
    paths = {
        delivery.PROFILE_PATH,
        delivery.REPO_ROOT / delivery._safe_path(launcher),
        delivery.REPO_ROOT / BINDING,
        delivery.REPO_ROOT / ".changerail/distribution-lock.json",
        delivery.REPO_ROOT / ".changerail/source-link.json",
    }
    for directory in (".changerail/adapters", "tools/openspec/node_modules"):
        root = delivery.REPO_ROOT / directory
        for path in root.rglob("*"):
            # npm creates .bin links; these are not executable dependency bodies.
            if ".bin" in path.relative_to(root).parts:
                continue
            if path.is_symlink():
                raise DeliveryError("linked project execution input")
            if path.is_file():
                paths.add(path)
    digest = lambda data: hashlib.sha256(data).hexdigest()
    result = {
        "engine/identity": value["engine_identity"],
        "engine/root": digest(str(engine).encode()),
        "python/executable": digest(Path(sys.executable).read_bytes()),
    }
    dependency_inventory = {}
    for path in sorted(paths):
        if path.exists() or path.is_symlink():
            relative = path.relative_to(delivery.REPO_ROOT).as_posix()
            fingerprint = digest(delivery._check_bytes(path, 32 * 1024 * 1024))
            if relative.startswith("tools/openspec/node_modules/"):
                dependency_inventory[relative] = {
                    "sha256": fingerprint,
                    "mode": path.stat().st_mode & 0o7777,
                }
            else:
                result["project/" + relative] = fingerprint
    # Preserve all dependency names/bytes/modes without exceeding run receipt
    # bounds with thousands of individual keys.
    result["project/openspec-dependency-inventory"] = digest(
        json.dumps(dependency_inventory, sort_keys=True, separators=(",", ":")).encode()
    )
    return result


def pinned_prompt(project: Path, role: str, prompt: str) -> str:
    value = binding(project)
    if value is None:
        return prompt
    name = "chrl-native-review" if role == "review" else "chrl-native-deliver"
    root = Path(value["engine_root"])
    skill = root / "tools/changerail/skills" / name / "SKILL.md"
    # Inline the pinned instructions so discovery of a product-side skill does
    # not silently select the code being edited.
    request = prompt.replace("$" + name, "Execute the pinned delivery instructions for")
    return (
        f"{request}\n\nEngine: {root}\nProject: {project}\n"
        f"For nested commands use {root}/bin/chrl --project {project}.\n"
        "The following skill is the execution contract:\n" + skill.read_text()
    )


def main() -> int:
    """Bootstrap from the selected engine with cwd excluded from Python imports."""
    project = Path(os.environ["CHRL_PROJECT_ROOT"]).resolve(strict=True)
    _ensure_no_pending(project)
    source = Path(__file__).resolve().parents[2]
    if sys.argv[1:2] == ["engine-rebind"]:
        from scripts.changerail.engine_snapshot import rebind_engine, verify_snapshot

        if not (source / "ENGINE-SNAPSHOT.json").is_file():
            raise DeliveryError("engine-rebind requires a sealed engine snapshot")
        verify_snapshot(source)
        if len(sys.argv) != 4 or sys.argv[2] != "--previous-identity":
            raise DeliveryError("engine-rebind requires --previous-identity ID")
        print(json.dumps(rebind_engine(project, source, sys.argv[3]), indent=2))
        return 0
    value = binding(project)
    engine = Path(value["engine_root"]) if value else source
    if is_release(value):
        # The stdlib-only external bootstrap already selected verified Python and
        # site-packages. Do not re-exec via -m/PYTHONPATH or import dev startup code.
        import runpy

        require_engine(project)
        if sys.argv[1:] in (["--engine-root"], ["--verified-engine-root"]):
            require_run(project)
            print(engine)
            return 0
        if sys.argv[1:2] == ["--exec-openspec"]:
            return exec_openspec(project, sys.argv[2:])
        runpy.run_module(
            "scripts.changerail.local_delivery", run_name="__main__", alter_sys=True
        )
        return 0
    if sys.argv[1:] == ["--verified-engine-root"]:
        if source != engine:
            raise DeliveryError("engine bootstrap did not select bound source")
        require_run(project)
        print(engine)
        return 0
    root_only = sys.argv[1:] == ["--engine-root"]
    os.environ["PYTHONPATH"] = str(engine)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    if value:
        os.environ["CHRL_ENGINE_ROOT"] = str(engine)
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-P",
            "-m",
            "scripts.changerail.engine_runtime"
            if root_only
            else "scripts.changerail.local_delivery",
            *(["--verified-engine-root"] if root_only else sys.argv[1:]),
        ],
    )
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeliveryError, OSError, ValueError) as exc:
        print(f"ChangeRail engine: {exc}", file=sys.stderr)
        raise SystemExit(2)
