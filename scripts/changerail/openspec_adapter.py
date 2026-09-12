"""Pinned project-local OpenSpec 1.3.1 command boundary.

The adapter invokes only the dependency installed below ``tools/openspec``.
It never searches PATH for OpenSpec, invokes npx, installs a package, or falls
back to a user-global schema/configuration directory.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import tempfile
import threading
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError


@dataclass(frozen=True)
class Task:
    """One task returned by the stock OpenSpec apply instructions."""

    id: str
    description: str
    done: bool


@dataclass(frozen=True)
class ApplyContext:
    """Normalized stock apply state."""

    state: str
    tasks: tuple[Task, ...]
    context_files: tuple[Path, ...]
    instruction: str

    @property
    def tasks_complete(self) -> bool:
        return (
            bool(self.tasks)
            and self.state == "all_done"
            and all(task.done for task in self.tasks)
        )


_LOCK = threading.Lock()
_INSTANCES: "OrderedDict[tuple, OpenSpecAdapter]" = OrderedDict()
_PROBES: "OrderedDict[tuple, None]" = OrderedDict()
_READONLY: "OrderedDict[tuple, subprocess.CompletedProcess[str]]" = OrderedDict()
_INSTANCE_LIMIT = 64
_PROBE_LIMIT = 512
_READONLY_LIMIT = 512


def _digest_file(path: Path) -> str:
    """Content identity of one pinned dependency file; '-' when absent."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "-"


def _digest_tree(root: Path) -> str:
    """Content identity of the stock OpenSpec artifacts that CLI reads depend on."""
    base = root / "openspec"
    paths = []
    for directory in ("changes", "specs"):
        top = base / directory
        if top.is_dir():
            paths.extend(
                path
                for path in top.rglob("*")
                if path.is_file() and not path.is_symlink()
            )
    config = base / "config.yaml"
    if config.is_file() and not config.is_symlink():
        paths.append(config)
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes())
        except OSError:
            digest.update(b"?")
        digest.update(b"\0")
    return digest.hexdigest()


def _remember(cache: OrderedDict, key: tuple, value: Any, limit: int) -> None:
    cache[key] = value
    while len(cache) > limit:
        cache.popitem(last=False)


class OpenSpecAdapter:
    """Read and validate stock OpenSpec artifacts through the pinned CLI."""

    VERSION = "1.3.1"
    CHANGE_ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")

    def __init__(self, root: Path, *, timeout: float = 40.0) -> None:
        self.root = root.resolve(strict=True)
        from scripts.changerail.engine_runtime import dependency_root, openspec_process

        dependency = dependency_root(self.root)
        self.package = (dependency / "node_modules/@fission-ai/openspec").resolve()
        self.node, _env, _kwargs = openspec_process(self.root)
        self.cli = self.package / "bin/openspec.js"
        self.timeout = timeout
        manifest = self.package / "package.json"
        if not self.package.is_relative_to(dependency.resolve()):
            raise DeliveryError("OpenSpec package must remain project-local")
        if not self.node.is_file() or not manifest.is_file() or not self.cli.is_file():
            raise DeliveryError(
                "local OpenSpec dependency missing; run "
                "./tools/openspec/bootstrap.sh --offline"
            )
        try:
            metadata = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise DeliveryError("invalid local OpenSpec manifest") from exc
        if (
            metadata.get("name") != "@fission-ai/openspec"
            or metadata.get("version") != self.VERSION
        ):
            raise DeliveryError("only project-local OpenSpec 1.3.1 is supported")
        self._verify_cli()

    @classmethod
    def create(cls, root: Path, *, timeout: float = 40.0) -> "OpenSpecAdapter":
        """Return the process-local adapter for an unchanged pinned dependency.

        The adapter is immutable apart from its timeout, so one verified
        instance per (root, node, package bytes) is reused. Any change to the
        pinned manifest or CLI yields a different key and is re-validated.
        """
        from scripts.changerail.engine_runtime import dependency_root, openspec_process

        resolved = root.resolve(strict=True)
        dependency = dependency_root(resolved)
        package = dependency / "node_modules/@fission-ai/openspec"
        node, _env, _kwargs = openspec_process(resolved)
        key = (
            str(resolved),
            str(node),
            str(package),
            _digest_file(package / "package.json"),
            _digest_file(package / "bin/openspec.js"),
            timeout,
        )
        with _LOCK:
            cached = _INSTANCES.get(key)
        if cached is not None:
            return cached
        instance = cls(resolved, timeout=timeout)
        with _LOCK:
            _remember(_INSTANCES, key, instance, _INSTANCE_LIMIT)
        return instance

    def _dependency_identity(self) -> tuple:
        """Byte identity of the pinned dependency, independent of project path.

        A verified CLI proves ``node`` runs these exact package bytes; the same
        bytes under another project root give the same result, so the probe is
        shared across isolated project copies instead of repeated per project.
        The path is deliberately excluded: only bytes and the Node executable
        decide the verified outcome.
        """
        return (
            str(self.node),
            _digest_file(self.package / "package.json"),
            _digest_file(self.cli),
        )

    def _verify_cli(self) -> None:
        """Prove the pinned CLI reports the supported version, once per identity.

        The probe is deterministic for fixed dependency bytes, so its result is
        memoized. A changed manifest or CLI changes the key, so drift is still
        rejected. The running ``subprocess.run`` object is part of the key so a
        substituted runner is never answered from another runner's cache, and an
        unsupported project schema override keeps its own key.
        """
        key = (
            *self._dependency_identity(),
            (self.root / "openspec/schemas").exists(),
            id(subprocess.run),
        )
        with _LOCK:
            if key in _PROBES:
                return
        version = self._invoke("--version")
        if version.returncode or version.stdout.strip() != self.VERSION:
            raise DeliveryError("installed OpenSpec CLI does not match version 1.3.1")
        with _LOCK:
            _remember(_PROBES, key, None, _PROBE_LIMIT)

    def _change_id(self, change_id: str) -> str:
        if not self.CHANGE_ID.fullmatch(change_id) or change_id == "archive":
            raise DeliveryError(f"invalid OpenSpec change ID: {change_id}")
        return change_id

    def change_root(self, change_id: str) -> Path:
        root = self.root / "openspec/changes" / self._change_id(change_id)
        if (
            root.is_symlink()
            or not root.is_dir()
            or not root.resolve().is_relative_to(self.root / "openspec/changes")
        ):
            raise DeliveryError(f"active OpenSpec change is absent: {change_id}")
        return root.resolve()

    def _invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        from scripts.changerail.engine_runtime import require_run, openspec_process

        require_run(self.root)
        node, extra, kwargs = openspec_process(self.root, selected_node=self.node)
        if node != self.node:
            raise DeliveryError("OpenSpec Node executable changed")
        if (self.root / "openspec/schemas").exists():
            raise DeliveryError("project OpenSpec schema overrides are unsupported")
        with tempfile.TemporaryDirectory(prefix="chrl-openspec-") as isolated:
            env = {
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "TZ": "UTC",
                "XDG_DATA_HOME": isolated,
                "XDG_CONFIG_HOME": isolated,
                "OPENSPEC_TELEMETRY": "0",
                "DO_NOT_TRACK": "1",
                "CI": "true",
                "OPENSPEC_NO_UPDATE_CHECK": "1",
                "OPENSPEC_NO_COMPLETIONS": "1",
                "OPENSPEC_NO_AUTO_CONFIG": "1",
                "NO_UPDATE_NOTIFIER": "1",
                "npm_config_update_notifier": "false",
                **extra,
            }
            try:
                return subprocess.run(
                    [str(self.node), str(self.cli), *args],
                    cwd=self.root,
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=self.timeout,
                    **kwargs,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise DeliveryError(f"local OpenSpec command failed: {args}") from exc

    def _readonly_invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run one non-mutating stock command, reusing the answer for fixed inputs.

        Stock validation/status answers depend only on the pinned dependency and
        the OpenSpec artifact bytes of one project. Memoizing them removes the
        repeated CLI spawns that dominated the suite; any change to the
        change/spec tree, the project, the pinned dependency or the running
        ``subprocess.run`` object misses the cache, so drift and substituted
        runners are still observed. The project root is part of the key because
        stock output embeds absolute context-file paths.
        """
        key = (
            str(self.root),
            *self._dependency_identity(),
            args,
            _digest_tree(self.root),
            id(subprocess.run),
        )
        with _LOCK:
            cached = _READONLY.get(key)
        if cached is not None:
            return cached
        result = self._invoke(*args)
        with _LOCK:
            _remember(_READONLY, key, result, _READONLY_LIMIT)
        return result

    def _json(self, *args: str) -> dict[str, Any]:
        """Run one stock JSON query through the non-mutating cache."""
        result = self._readonly_invoke(*args, "--json")
        if result.returncode:
            raise DeliveryError(
                f"OpenSpec exited {result.returncode}: {result.stderr.strip()}"
            )
        try:
            value = json.loads(result.stdout)
        except ValueError as exc:
            raise DeliveryError("OpenSpec returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise DeliveryError("OpenSpec JSON result must be an object")
        return copy.deepcopy(value)

    def inspect_complete_plan(self, change_id: str) -> None:
        root = self.change_root(change_id)
        data = self._json("status", "--change", change_id, "--schema", "spec-driven")
        if (
            data.get("changeName") != change_id
            or data.get("schemaName") != "spec-driven"
        ):
            raise DeliveryError("OpenSpec status returned a foreign change")
        if data.get("isComplete") is not True:
            raise DeliveryError(
                "OpenSpec proposal/specs/design/tasks plan is incomplete"
            )
        required = (root / "proposal.md", root / "design.md", root / "tasks.md")
        if not all(path.is_file() for path in required) or not any(
            (root / "specs").glob("*/spec.md")
        ):
            raise DeliveryError("OpenSpec stock artifact set is incomplete")

    def apply_context(self, change_id: str) -> ApplyContext:
        root = self.change_root(change_id)
        data = self._json(
            "instructions", "apply", "--change", change_id, "--schema", "spec-driven"
        )
        if (
            data.get("changeName") != change_id
            or data.get("schemaName") != "spec-driven"
        ):
            raise DeliveryError("OpenSpec apply returned a foreign change")
        rows = data.get("tasks")
        if not isinstance(rows, list):
            raise DeliveryError("OpenSpec apply tasks are malformed")
        tasks: list[Task] = []
        for row in rows:
            if (
                not isinstance(row, dict)
                or not isinstance(row.get("id"), str)
                or not isinstance(row.get("description"), str)
                or type(row.get("done")) is not bool
            ):
                raise DeliveryError("OpenSpec apply task is malformed")
            tasks.append(Task(row["id"], row["description"], row["done"]))
        if not tasks or len({task.id for task in tasks}) != len(tasks):
            raise DeliveryError("OpenSpec requires nonempty uniquely identified tasks")
        state = data.get("state")
        if state not in {"ready", "all_done"}:
            raise DeliveryError(f"OpenSpec apply is not executable: {state}")
        files: list[Path] = []
        context_files = data.get("contextFiles")
        if not isinstance(context_files, dict):
            raise DeliveryError("OpenSpec contextFiles are malformed")
        for values in context_files.values():
            if not isinstance(values, list):
                raise DeliveryError("OpenSpec context file list is malformed")
            for value in values:
                path = Path(value)
                if (
                    not path.is_absolute()
                    or not path.is_file()
                    or not path.resolve().is_relative_to(root)
                ):
                    raise DeliveryError("OpenSpec context file escapes its change")
                files.append(path.resolve())
        instruction = data.get("instruction")
        if not isinstance(instruction, str) or not instruction.strip():
            raise DeliveryError("OpenSpec apply instruction is absent")
        return ApplyContext(state, tuple(tasks), tuple(files), instruction)

    def validate_change(self, change_id: str) -> None:
        self.change_root(change_id)
        result = self._readonly_invoke(
            "validate", change_id, "--strict", "--no-interactive"
        )
        if result.returncode:
            raise DeliveryError(
                "strict OpenSpec change validation failed: " + result.stderr.strip()
            )

    def validate_specs(self) -> None:
        result = self._readonly_invoke(
            "validate", "--specs", "--strict", "--no-interactive"
        )
        if result.returncode:
            raise DeliveryError(
                "strict canonical OpenSpec validation failed: " + result.stderr.strip()
            )

    def workflow(self, name: str) -> str:
        """Read stock methodology from the pinned package, not global skills."""
        if name not in {"apply", "sync", "verify"}:
            raise DeliveryError("unknown stock OpenSpec workflow")
        from scripts.changerail.engine_runtime import (
            runtime_path,
            require_run,
            openspec_process,
        )

        require_run(self.root)
        node, extra, kwargs = openspec_process(self.root, selected_node=self.node)
        if node != self.node:
            raise DeliveryError("OpenSpec Node executable changed")
        loader = runtime_path(
            self.root, self.root / "tools/openspec/workflow-instructions.mjs"
        )
        result = subprocess.run(
            [str(self.node), str(loader), name],
            cwd=self.root,
            env={
                "PATH": "/usr/bin:/bin",
                "OPENSPEC_TELEMETRY": "0",
                "CI": "true",
                **extra,
            },
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
            **kwargs,
        )
        if result.returncode or not result.stdout.strip():
            raise DeliveryError(
                "cannot read pinned stock workflow: " + result.stderr.strip()
            )
        return result.stdout

    def archive(self, change_id: str) -> Path:
        """Move already semantically synchronized artifacts using stock archive."""

        self.inspect_complete_plan(change_id)
        if not self.apply_context(change_id).tasks_complete:
            raise DeliveryError("OpenSpec archive requires all tasks complete")
        self.validate_change(change_id)
        self.validate_specs()
        date = datetime.now(timezone.utc).date().isoformat()
        destination = self.root / "openspec/changes/archive" / f"{date}-{change_id}"
        if destination.exists():
            raise DeliveryError(f"OpenSpec archive destination exists: {destination}")
        result = self._invoke("archive", change_id, "--yes", "--skip-specs")
        source = self.root / "openspec/changes" / change_id
        if result.returncode or source.exists() or not destination.is_dir():
            raise DeliveryError(
                "OpenSpec archive/sync did not complete: "
                + (result.stderr.strip() or result.stdout.strip())
            )
        self.validate_specs()
        return destination.resolve()

    def artifact_identity(
        self, root: Path, *, normalize_tasks: bool = True
    ) -> dict[str, str]:
        if root.is_symlink() or any(path.is_symlink() for path in root.rglob("*")):
            raise DeliveryError("OpenSpec artifact tree contains a symlink")
        files = sorted(path for path in root.rglob("*") if path.is_file())
        artifacts: dict[str, str] = {}
        for path in files:
            raw = path.read_bytes()
            if normalize_tasks and path == root / "tasks.md":
                text = raw.decode("utf-8")
                raw = re.sub(
                    r"^([-*][ \t]*\[)[ xX](\][ \t]*\S[^\r\n]*)$",
                    r"\1 \2",
                    text,
                    flags=re.MULTILINE,
                ).encode("utf-8")
            artifacts[path.relative_to(root).as_posix()] = hashlib.sha256(
                raw
            ).hexdigest()
        return artifacts

    def identity(self, change_id: str) -> dict[str, Any]:
        from scripts.changerail.engine_runtime import dependency_root

        root = self.change_root(change_id)
        return {
            "schema": "changerail.openspec-plan.v1",
            "change_id": change_id,
            "openspec_version": self.VERSION,
            "package_lock_sha256": hashlib.sha256(
                (dependency_root(self.root) / "package-lock.json").read_bytes()
            ).hexdigest(),
            "artifacts": self.artifact_identity(root),
        }
