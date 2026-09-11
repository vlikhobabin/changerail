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


def binding(project: Path) -> dict[str, Any] | None:
    path = project / BINDING
    if not path.exists() and not path.is_symlink():
        if os.environ.get("CHRL_ENGINE_ROOT"):
            raise DeliveryError("engine environment requires an explicit binding")
        return None
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
    if relative.startswith("tools/openspec/node_modules/"):
        return path
    value = binding(project)
    return Path(value["engine_root"]) / relative if value else path


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
    source = Path(__file__).resolve().parents[2]
    value = binding(project)
    engine = Path(value["engine_root"]) if value else source
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
