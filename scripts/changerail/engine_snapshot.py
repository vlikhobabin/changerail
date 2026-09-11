"""Committed engine snapshots, sealed inventories and explicit project bindings.

Read-only permissions prevent accidental writes; inventory verification detects
changes even by the owning account. A symlink is never binding authority.
"""

from __future__ import annotations

from contextlib import contextmanager
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from typing import Any

import distribution

MANIFEST = "ENGINE-SNAPSHOT.json"
BINDING = ".changerail/engine-binding.json"
SCHEMA = "changerail.engine-snapshot.v1"
BINDING_SCHEMA = "changerail.engine-binding.v1"


class EngineSnapshotError(ValueError):
    """The engine inventory or project ownership cannot be verified."""


def _encoded(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode()


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _path(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    for parent in [*reversed(path.parents), path]:
        if parent.is_symlink():
            raise EngineSnapshotError(f"symlink refused: {parent}")
    return path


def _read(path: Path) -> tuple[bytes, os.stat_result]:
    _path(path)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
                or info.st_size > distribution.MAX_FILE
            ):
                raise EngineSnapshotError(
                    f"not a bounded unlinked regular file: {path}"
                )
            data = stream.read(distribution.MAX_FILE + 1)
            after = os.fstat(stream.fileno())
        if len(data) != info.st_size or (
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise EngineSnapshotError(f"file changed while reading: {path}")
        return data, info
    except OSError as exc:
        raise EngineSnapshotError(f"cannot read engine file: {path}: {exc}") from exc


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path)[0])
    except (UnicodeError, ValueError) as exc:
        raise EngineSnapshotError(f"invalid engine JSON: {path}") from exc
    if not isinstance(value, dict):
        raise EngineSnapshotError(f"engine JSON must be an object: {path}")
    return value


def _git(source: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(source), *args], capture_output=True)
    if result.returncode:
        raise EngineSnapshotError("engine source must be a readable Git checkout")
    return result.stdout


def _clean_head(source: Path) -> str:
    if _git(source, "status", "--porcelain=v1", "--untracked-files=normal"):
        raise EngineSnapshotError("engine source must be clean and committed")
    return _git(source, "rev-parse", "HEAD").decode().strip()


def _source_inventory(source: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    commit = _clean_head(source)
    try:
        _config, payload = distribution.source_payload(source)
    except (distribution.DistributionError, OSError, ValueError, KeyError) as exc:
        raise EngineSnapshotError(f"invalid engine source payload: {exc}") from exc
    files, contents = {}, {}
    for name, (data, mode) in payload.items():
        actual, _info = _read(source / name)
        committed = subprocess.run(
            ["git", "-C", str(source), "show", f"{commit}:{name}"], capture_output=True
        )
        if committed.returncode or committed.stdout != data or actual != data:
            raise EngineSnapshotError(f"engine payload is not committed: {name}")
        tree_entry = _git(source, "ls-tree", commit, "--", name).split(b" ", 1)[0]
        if tree_entry != (b"100755" if mode == 0o755 else b"100644"):
            raise EngineSnapshotError(f"engine payload mode is not committed: {name}")
        sealed_mode = mode & ~0o222
        files[name] = {"sha256": _digest(data), "size": len(data), "mode": sealed_mode}
        contents[name] = data
    if _clean_head(source) != commit:
        raise EngineSnapshotError("engine source changed during snapshot preparation")
    manifest = {
        "schema": SCHEMA,
        "source_commit": commit,
        "files": files,
        "payload_sha256": _digest(_encoded(files)),
    }
    return manifest, contents


def snapshot_identity(manifest: dict[str, Any]) -> str:
    """Hash the complete provenance and inventory, independent of its location."""
    return _digest(_encoded(manifest))


def verify_snapshot(snapshot: Path) -> dict[str, Any]:
    """Verify every file, directory and permission, including unexpected entries."""
    snapshot = _path(snapshot)
    manifest = _json(snapshot / MANIFEST)
    files = manifest.get("files")
    if (
        set(manifest) != {"schema", "source_commit", "files", "payload_sha256"}
        or manifest.get("schema") != SCHEMA
        or not isinstance(files, dict)
        or not files
    ):
        raise EngineSnapshotError("invalid engine snapshot manifest")
    commit = manifest.get("source_commit")
    if (
        not isinstance(commit, str)
        or len(commit) not in {40, 64}
        or any(c not in "0123456789abcdef" for c in commit)
    ):
        raise EngineSnapshotError("invalid engine source commit")
    if _digest(_encoded(files)) != manifest["payload_sha256"]:
        raise EngineSnapshotError("engine inventory digest mismatch")
    directories = {"."}
    for name, entry in files.items():
        try:
            distribution.allowed_payload(name)
        except (distribution.DistributionError, TypeError) as exc:
            raise EngineSnapshotError(f"unsafe engine inventory path: {name}") from exc
        if (
            not isinstance(entry, dict)
            or set(entry) != {"sha256", "size", "mode"}
            or entry.get("mode") not in {0o444, 0o555}
        ):
            raise EngineSnapshotError(f"invalid engine inventory entry: {name}")
        directories.update(parent.as_posix() for parent in Path(name).parents)
    seen = set()
    for directory, dirnames, filenames in os.walk(snapshot, followlinks=False):
        root = Path(directory)
        relative = root.relative_to(snapshot).as_posix()
        info = root.lstat()
        if (
            relative not in directories
            or not stat.S_ISDIR(info.st_mode)
            or stat.S_IMODE(info.st_mode) != 0o555
        ):
            raise EngineSnapshotError(f"engine directory drift: {relative}")
        for name in dirnames:
            if (root / name).is_symlink():
                raise EngineSnapshotError(f"engine directory symlink: {name}")
        for name in filenames:
            path = root / name
            relative = path.relative_to(snapshot).as_posix()
            data, info = _read(path)
            if relative == MANIFEST:
                if stat.S_IMODE(info.st_mode) != 0o444 or data != _encoded(manifest):
                    raise EngineSnapshotError("engine manifest drift")
                continue
            actual = {
                "sha256": _digest(data),
                "size": len(data),
                "mode": stat.S_IMODE(info.st_mode),
            }
            if files.get(relative) != actual:
                raise EngineSnapshotError(f"engine file drift: {relative}")
            seen.add(relative)
    if seen != set(files):
        raise EngineSnapshotError("engine inventory contains missing files")
    return manifest


@contextmanager
def _lock(path: Path):
    _path(path)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EngineSnapshotError(f"unsafe engine publication lock: {path}")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def _sync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_DIRECTORY | os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path: Path, data: bytes, mode: int) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fchmod(stream.fileno(), mode)
        os.fsync(stream.fileno())


def _publish_directory(source: Path, destination: Path) -> None:
    # Linux RENAME_NOREPLACE preserves an existing destination even when a
    # non-cooperating publisher ignores our advisory lock.
    library = ctypes.CDLL(None, use_errno=True)
    rename = library.renameat2
    rename.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def create_snapshot(source: Path, destination: Path) -> dict[str, Any]:
    """Atomically publish one sealed copy of a clean committed runtime payload."""
    source, destination = _path(source), _path(destination)
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise EngineSnapshotError("engine snapshot must be outside source checkout")
    manifest, contents = _source_inventory(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with _lock(destination.parent / f".{destination.name}.lock"):
        if destination.exists():
            existing = verify_snapshot(destination)
            if existing != manifest:
                raise EngineSnapshotError(
                    "engine destination already contains a different snapshot"
                )
            return existing
        stage = Path(
            tempfile.mkdtemp(
                prefix=f".{destination.name}.staging-", dir=destination.parent
            )
        )
        try:
            for name, data in contents.items():
                path = stage / name
                path.parent.mkdir(parents=True, exist_ok=True)
                _write(path, data, manifest["files"][name]["mode"])
            _write(stage / MANIFEST, _encoded(manifest), 0o444)
            for directory, _dirs, _files in os.walk(stage, topdown=False):
                _sync_directory(Path(directory))
                Path(directory).chmod(0o555)
            verify_snapshot(stage)
            _publish_directory(stage, destination)
            _sync_directory(destination.parent)
        finally:
            if stage.exists():
                for directory, _dirs, _files in os.walk(stage):
                    Path(directory).chmod(0o755)
                shutil.rmtree(stage)
    return verify_snapshot(destination)


def bind_engine(project: Path, snapshot: Path) -> dict[str, Any]:
    """Create an explicit immutable engine binding; never silently rebind."""
    project, snapshot = _path(project), _path(snapshot)
    if snapshot.is_relative_to(project) or project.is_relative_to(snapshot):
        raise EngineSnapshotError("engine must be outside mutable project")
    manifest = verify_snapshot(snapshot)
    binding = {
        "schema": BINDING_SCHEMA,
        "project_root": str(project),
        "engine_root": str(snapshot),
        "engine_identity": snapshot_identity(manifest),
    }
    target = _path(project / BINDING)
    target.parent.mkdir(parents=True, exist_ok=True)
    with _lock(target.parent / ".engine-binding.lock"):
        if target.exists():
            if verify_binding(project) != binding:
                raise EngineSnapshotError(
                    "project already has a different engine binding"
                )
            return binding
        descriptor, temporary = tempfile.mkstemp(
            prefix=".engine-binding-", dir=target.parent
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(_encoded(binding))
                stream.flush()
                os.fsync(stream.fileno())
            _publish_directory(Path(temporary), target)
            _sync_directory(target.parent)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return verify_binding(project, expected_engine=snapshot)


def verify_binding(
    project: Path, *, expected_engine: Path | None = None
) -> dict[str, Any]:
    """Verify project ownership, engine location and current full inventory."""
    project = _path(project)
    binding = _json(project / BINDING)
    if (
        set(binding) != {"schema", "project_root", "engine_root", "engine_identity"}
        or binding.get("schema") != BINDING_SCHEMA
        or binding.get("project_root") != str(project)
    ):
        raise EngineSnapshotError("invalid project engine binding")
    if (
        not isinstance(binding["engine_root"], str)
        or not Path(binding["engine_root"]).is_absolute()
    ):
        raise EngineSnapshotError("invalid bound engine path")
    snapshot = _path(Path(binding["engine_root"]))
    if snapshot.is_relative_to(project) or project.is_relative_to(snapshot):
        raise EngineSnapshotError("bound engine overlaps mutable project")
    if expected_engine is not None and snapshot != _path(expected_engine):
        raise EngineSnapshotError("loaded engine does not match project binding")
    if snapshot_identity(verify_snapshot(snapshot)) != binding["engine_identity"]:
        raise EngineSnapshotError("bound engine identity drift")
    return binding


def _sync_file(path: Path) -> None:
    fd = os.open(_path(path), os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _sync_ancestors(directory: Path) -> None:
    for parent in (directory, *directory.parents):
        _sync_directory(parent)


def _mkdir_durable(path: Path) -> None:
    missing = []
    directory = path
    while not directory.exists():
        missing.append(directory)
        directory = directory.parent
    for directory in reversed(missing):
        _path(directory).mkdir(exist_ok=True)
        _sync_directory(directory.parent)
    _sync_ancestors(path)


def _rebind_receipt(path: Path, value: dict[str, Any]) -> None:
    data = _encoded(value)
    if path.exists():
        if _read(path)[0] != data:
            raise EngineSnapshotError("engine rebind receipt drift")
        _sync_file(path)
        _sync_ancestors(path.parent)
        return
    _mkdir_durable(path.parent)
    fd, name = tempfile.mkstemp(prefix=".receipt-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        _publish_directory(temporary, path)
        _sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _replace_binding(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=".engine-binding-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def process_exited(process: Path) -> bool:
    """Only kernel terminal states prove an opaque process cannot write again."""
    try:
        for line in (process / "status").read_text().splitlines():
            if line.startswith("State:"):
                fields = line.split()
                return len(fields) >= 2 and fields[1] in {"Z", "X"}
    except (FileNotFoundError, ProcessLookupError):
        return True
    except PermissionError:
        pass
    return False


def _no_live_delivery(project: Path) -> None:
    for process in Path("/proc").glob("[0-9]*"):
        try:
            if int(process.name) == os.getpid() or process.stat().st_uid != os.getuid():
                continue
            environment = (process / "environ").read_bytes().split(b"\0")
            for item in environment:
                if item.startswith(b"CHRL_RUN_DIR="):
                    owner = Path(os.fsdecode(item.split(b"=", 1)[1])).resolve()
                    if owner.is_relative_to(project / ".runtime/changerail"):
                        raise EngineSnapshotError("live process owns delivery project")
        except (ProcessLookupError, FileNotFoundError):
            continue
        except PermissionError:
            if process_exited(process):
                continue
            try:
                command = (process / "cmdline").read_bytes().lower()
            except (FileNotFoundError, ProcessLookupError):
                continue
            if (not command or any(
                name in command.split(b"\0", 1)[0]
                for name in (b"python", b"codex", b"chrl", b"changerail", b"pytest", b"bash", b"/sh")
            )) and not process_exited(process):
                raise EngineSnapshotError("cannot prove delivery runner is inactive")


def rebind_engine(
    project: Path, snapshot: Path, previous_identity: str
) -> dict[str, Any]:
    """Explicit operator transition; old run execution identity is never rewritten."""
    project, snapshot = _path(project), _path(snapshot)
    if os.environ.get("CHRL_RUN_DIR") or os.environ.get("CHRL_SESSION_ROLE"):
        raise EngineSnapshotError("engine rebind requires an operator outside delivery")
    if snapshot.is_relative_to(project) or project.is_relative_to(snapshot):
        raise EngineSnapshotError("engine must be outside mutable project")
    after = {
        "schema": BINDING_SCHEMA,
        "project_root": str(project),
        "engine_root": str(snapshot),
        "engine_identity": snapshot_identity(verify_snapshot(snapshot)),
    }
    request = {
        "project": str(project),
        "previous_identity": previous_identity,
        "after": after,
    }
    runtime = _path(project / ".runtime/changerail")
    _mkdir_durable(runtime)
    lock = os.open(
        runtime / "delivery.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
    )
    try:
        info = os.fstat(lock)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EngineSnapshotError("unsafe delivery lock")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise EngineSnapshotError("delivery lock is held") from exc
        with _lock(project / ".changerail/.engine-binding.lock"):
            _no_live_delivery(project)
            directory = _path(runtime / "engine-rebind" / _digest(_encoded(request)))
            target = _path(project / BINDING)
            current = verify_binding(project)
            raw = _read(target)[0]
            intent_path = directory / "intent.json"
            if intent_path.exists():
                intent = _json(intent_path)
                if intent.get("request") != request or intent.get("after") != after:
                    raise EngineSnapshotError("engine rebind intent differs")
                try:
                    before = intent["before"]
                    before_bytes = intent["before_bytes"].encode("utf-8")
                    valid_intent = (
                        intent["schema"] == "changerail.engine-rebind.v1"
                        and json.loads(before_bytes) == before
                        and before["schema"] == BINDING_SCHEMA
                        and before["project_root"] == str(project)
                        and _digest(before_bytes) == intent["before_sha256"]
                        and _digest(_encoded(after)) == intent["after_sha256"]
                    )
                except (KeyError, TypeError, ValueError, AttributeError) as exc:
                    raise EngineSnapshotError("invalid engine rebind intent") from exc
                if not valid_intent:
                    raise EngineSnapshotError("engine rebind intent drift")
                if before.get("engine_identity") != previous_identity:
                    raise EngineSnapshotError("previous identity differs")
                if (
                    snapshot_identity(verify_snapshot(Path(before["engine_root"])))
                    != previous_identity
                ):
                    raise EngineSnapshotError("previous engine snapshot drift")
                if raw not in (intent["before_bytes"].encode(), _encoded(after)):
                    raise EngineSnapshotError("exact engine binding bytes drift")
                if _digest(intent["before_bytes"].encode()) != intent["before_sha256"]:
                    raise EngineSnapshotError("engine rebind receipt drift")
                _rebind_receipt(intent_path, intent)
            else:
                if current["engine_identity"] != previous_identity:
                    raise EngineSnapshotError("previous identity differs")
                for other in (runtime / "engine-rebind").glob("*/intent.json"):
                    if (
                        _json(other).get("before", {}).get("engine_identity")
                        == previous_identity
                    ):
                        raise EngineSnapshotError(
                            "previous engine already has another rebind intent"
                        )
                intent = {
                    "schema": "changerail.engine-rebind.v1",
                    "request": request,
                    "before": current,
                    "after": after,
                    "before_bytes": raw.decode("utf-8"),
                    "before_sha256": _digest(raw),
                    "after_sha256": _digest(_encoded(after)),
                }
                _rebind_receipt(intent_path, intent)
            applied = {
                "schema": "changerail.engine-rebind.v1",
                "intent_sha256": _digest(_read(intent_path)[0]),
                "binding_sha256": _digest(_encoded(after)),
            }
            applied_path = directory / "applied.json"
            if applied_path.exists():
                if _json(applied_path) != applied or raw != _encoded(after):
                    raise EngineSnapshotError(
                        "engine rebind applied receipt or binding drift"
                    )
            elif raw != _encoded(after):
                if _read(target)[0] != raw:
                    raise EngineSnapshotError("exact engine binding bytes drift")
                if verify_binding(project) != intent["before"]:
                    raise EngineSnapshotError("previous binding drift")
                if snapshot_identity(verify_snapshot(snapshot)) != after["engine_identity"]:
                    raise EngineSnapshotError("new engine snapshot drift")
                _no_live_delivery(project)
                _replace_binding(target, _encoded(after))
            _sync_file(target)
            _sync_ancestors(target.parent)
            _rebind_receipt(applied_path, applied)
            return {
                "binding": verify_binding(project, expected_engine=snapshot),
                "receipt": str(directory),
            }
    finally:
        os.close(lock)


def verify_previous_binding(project: Path, identity: dict[str, str]) -> None:
    """Bind a predecessor's three engine keys to a completed, intact rebind."""
    project = _path(project)
    current = verify_binding(project)
    raw = _read(project / BINDING)[0]

    def matches(binding: dict, data: bytes) -> bool:
        return (
            identity.get("engine/identity") == binding.get("engine_identity")
            and identity.get("engine/root") == _digest(binding["engine_root"].encode())
            and identity.get("project/" + BINDING) == _digest(data)
        )

    if matches(current, raw):
        return
    for path in (project / ".runtime/changerail/engine-rebind").glob("*/intent.json"):
        intent = _json(path)
        try:
            before, after = intent["before"], intent["after"]
            before_bytes = intent["before_bytes"].encode()
            if not matches(before, before_bytes) or after != current:
                continue
            request = {"project": str(project), "previous_identity": before["engine_identity"], "after": after}
            if (
                intent["schema"] != "changerail.engine-rebind.v1"
                or intent["request"] != request
                or path.parent.name != _digest(_encoded(request))
                or before["schema"] != BINDING_SCHEMA
                or before["project_root"] != str(project)
                or json.loads(before_bytes) != before
                or intent["before_sha256"] != _digest(before_bytes)
                or intent["after_sha256"] != _digest(raw)
                or raw != _encoded(after)
            ):
                raise EngineSnapshotError("previous binding receipt drift")
            old_root = _path(Path(before["engine_root"]))
            if old_root.is_relative_to(project) or project.is_relative_to(old_root):
                raise EngineSnapshotError("previous engine overlaps project")
            if snapshot_identity(verify_snapshot(old_root)) != before["engine_identity"]:
                raise EngineSnapshotError("previous engine snapshot drift")
            if _json(path.parent / "applied.json") != {
                "schema": "changerail.engine-rebind.v1",
                "intent_sha256": _digest(_read(path)[0]),
                "binding_sha256": _digest(raw),
            }:
                raise EngineSnapshotError("previous binding lacks completed rebind")
            return
        except (KeyError, TypeError, AttributeError, UnicodeError) as exc:
            raise EngineSnapshotError("invalid previous binding receipt") from exc
    raise EngineSnapshotError("previous binding has no matching completed rebind")
