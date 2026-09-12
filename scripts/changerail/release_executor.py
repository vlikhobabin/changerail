"""Verified release-checkout executors; stdlib-only bootstrap and lease protocol.

The accepted receipt and permanent use-lock live beside the checkout. Only an
explicit local acceptance/update operation may publish a receipt. The verifier
proves consistency with that authority, not who signed a remote release.

Updater: hold exclusive_use(root) before any checkout/dependency/receipt change;
never unlink/replace the lock inode. Readers retain their shared descriptor until
exit. A supervisor must pass child_process_kwargs(root) to Popen AND retain its
own descriptor while waiting: arbitrary model launchers may close inherited FDs.
"""

from __future__ import annotations

from contextlib import contextmanager
import fcntl
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any

BINDING = ".changerail/engine-binding.json"
BINDING_SCHEMA = "changerail.engine-binding.v2"
RECEIPT_SCHEMA = "changerail.accepted-release.v1"
USE_FD = "CHRL_ENGINE_USE_FD"
DEPENDENCY_DIRS = (".venv", "tools/openspec/node_modules")
# Entire execution directories are closed, including untracked .pyc/.so helpers.
EXECUTION_DIRS = (
    "scripts",
    "tools/changerail/schemas",
    "tools/changerail/skills",
    "tools/openspec",
)
REQUIRED = {
    "distribution.json",
    "distribution.py",
    "scripts/__init__.py",
    "scripts/changerail/release_executor.py",
    "scripts/changerail/engine_runtime.py",
    "bin/chrl",
    "bin/openspec",
    "tools/openspec/package-lock.json",
}
_LEASES: dict[Path, int] = {}
_EXCLUSIVE_LEASES: dict[Path, int] = {}


class ReleaseExecutorError(ValueError):
    """An explicit release authority or execution lease failed verification."""


def encoded(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_root(root: Path) -> Path:
    root = Path(root)
    if not root.is_absolute() or root.resolve(strict=True) != root:
        raise ReleaseExecutorError(
            "executor/project root must be canonical, without links"
        )
    if not root.is_dir():
        raise ReleaseExecutorError("executor/project root is not a directory")
    return root


def regular(path: Path) -> bytes:
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ReleaseExecutorError(f"linked authority/source: {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 128 * 1024 * 1024:
            raise ReleaseExecutorError(f"not a bounded regular file: {path}")
        data = stream.read()
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or len(data) != before.st_size:
            raise ReleaseExecutorError(f"file changed during verification: {path}")
        return data


def document(path: Path) -> dict[str, Any]:
    value = json.loads(regular(path))
    if not isinstance(value, dict):
        raise ReleaseExecutorError(f"expected object: {path}")
    return value


def receipt_path(root: Path) -> Path:
    return root.parent / f".{root.name}.accepted-release.json"


def lock_path(root: Path) -> Path:
    return root.parent / f".{root.name}.executor-use.lock"


def maintenance_path(root: Path) -> Path:
    """Shared fence location with release_update; existence alone blocks readers."""
    return root.parent / f".{root.name}.release-maintenance.json"


def _check_maintenance(root: Path, *, updater: bool = False) -> None:
    # lexists includes dangling links; malformed/stale contents never un-fence a
    # release. Only an explicit updater API under our verified exclusive lease
    # can inspect/verify before its transaction removes the marker.
    if not os.path.lexists(maintenance_path(root)):
        return
    fd = _EXCLUSIVE_LEASES.get(root) if updater else None
    if fd is None:
        raise ReleaseExecutorError("executor is fenced by release maintenance")
    _validate_fd(root, fd, exclusive=True)


def _safe_owned(info: os.stat_result) -> bool:
    return (
        stat.S_ISREG(info.st_mode)
        and info.st_nlink == 1
        and info.st_uid == os.geteuid()
        and not info.st_mode & 0o022
    )


def _validate_fd(root: Path, fd: int, *, exclusive: bool = False) -> None:
    expected = lock_path(canonical_root(root))
    if expected.is_symlink():
        raise ReleaseExecutorError("linked executor use lock")
    info, actual = expected.stat(), os.fstat(fd)
    if (
        not _safe_owned(info)
        or not _safe_owned(actual)
        or (info.st_dev, info.st_ino) != (actual.st_dev, actual.st_ino)
    ):
        raise ReleaseExecutorError("inherited executor FD has wrong inode/ownership")
    if fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDWR:
        raise ReleaseExecutorError("inherited executor FD has wrong access mode")
    # Linux fdinfo describes the open-file-description lock, including inherited
    # locks whose original PID differs. An integer or an unlocked same-inode FD
    # alone is not authority. Never convert/downgrade a supplied exclusive lock.
    rows = Path(f"/proc/self/fdinfo/{fd}").read_text().splitlines()
    lock_mode = "WRITE" if exclusive else "READ"
    if not any(
        re.search(rf"^lock:.* FLOCK +ADVISORY +{lock_mode} ", row) for row in rows
    ):
        raise ReleaseExecutorError(f"executor FD does not hold a {lock_mode} lease")


def _open_lock(root: Path) -> int:
    path = lock_path(canonical_root(root))
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    if not _safe_owned(os.fstat(fd)):
        os.close(fd)
        raise ReleaseExecutorError("unsafe executor use lock ownership/permissions")
    return fd


def ensure_use(root: Path) -> int:
    """Acquire/reuse a nonblocking shared lease, retained until process exit."""
    root = canonical_root(root)
    if root in _LEASES:
        fd = _LEASES[root]
        _validate_fd(root, fd)
        return fd
    inherited = os.environ.get(USE_FD)
    if inherited is not None:
        try:
            fd = int(inherited)
            _validate_fd(root, fd)
        except (ValueError, OSError) as exc:
            raise ReleaseExecutorError(
                f"invalid inherited executor lease: {exc}"
            ) from exc
    else:
        fd = _open_lock(root)
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            _validate_fd(root, fd)
        except (OSError, ValueError) as exc:
            os.close(fd)
            raise ReleaseExecutorError(
                f"executor is updating or lease is invalid: {exc}"
            ) from exc
    os.set_inheritable(fd, True)
    os.environ[USE_FD] = str(fd)
    _LEASES[root] = fd
    return fd


def child_process_kwargs(root: Path) -> dict[str, Any]:
    """Use with subprocess.run/Popen; propagate USE_FD in the child's env too."""
    return {"pass_fds": (ensure_use(root),)}


@contextmanager
def exclusive_use(root: Path):
    """Updater lease. Never upgrade an inherited reader or wait for active runs."""
    root = canonical_root(root)
    if root in _LEASES or os.environ.get(USE_FD) is not None:
        raise ReleaseExecutorError("updater must run outside an executor use session")
    fd = _open_lock(root)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReleaseExecutorError("executor is in use") from exc
        _validate_fd(root, fd, exclusive=True)
        _EXCLUSIVE_LEASES[root] = fd
        yield fd
    finally:
        _EXCLUSIVE_LEASES.pop(root, None)
        os.close(fd)


def read_binding(
    project: Path, *, expected_engine: Path | None = None
) -> dict[str, Any]:
    project = canonical_root(project)
    value = document(project / BINDING)
    if set(value) != {"schema", "kind", "project_root", "engine_root"} or (
        value.get("schema") != BINDING_SCHEMA
        or value.get("kind") != "release-checkout"
        or value.get("project_root") != str(project)
        or not isinstance(value.get("engine_root"), str)
    ):
        raise ReleaseExecutorError("invalid release-checkout binding")
    root = canonical_root(Path(value["engine_root"]))
    if root.is_relative_to(project) or project.is_relative_to(root):
        raise ReleaseExecutorError("executor overlaps mutable project")
    if expected_engine is not None and root != canonical_root(expected_engine):
        raise ReleaseExecutorError("executing source differs from release binding")
    return value


def binding_document(project: Path, root: Path) -> dict[str, str]:
    """Prepare binding bytes for next-stage publisher; does not write or accept."""
    project, root = canonical_root(project), canonical_root(root)
    if root.is_relative_to(project) or project.is_relative_to(root):
        raise ReleaseExecutorError("executor overlaps mutable project")
    return {
        "schema": BINDING_SCHEMA,
        "kind": "release-checkout",
        "project_root": str(project),
        "engine_root": str(root),
    }


def _git(root: Path, *args: str) -> bytes:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", "-C", str(root), *args],
        env=env,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ReleaseExecutorError(f"cannot verify release Git authority: {args[0]}")
    return result.stdout


def _name(name: str) -> str:
    if (
        not isinstance(name, str)
        or not name
        or "\\" in name
        or Path(name).is_absolute()
        or any(p in {"", ".", ".."} for p in name.split("/"))
    ):
        raise ReleaseExecutorError("unsafe release inventory name")
    return name


def _entry(path: Path) -> dict[str, Any]:
    data = regular(path)
    return {
        "sha256": digest(data),
        "size": len(data),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }


def _scan(directory: Path) -> list[tuple[Path, os.stat_result]]:
    """Enumerate and stat every entry; an unreadable tree is never empty proof."""
    try:
        if not stat.S_ISDIR(directory.lstat().st_mode):
            raise ReleaseExecutorError(f"not an inventory directory: {directory}")
        with os.scandir(directory) as entries:
            return sorted(
                (
                    (Path(entry.path), entry.stat(follow_symlinks=False))
                    for entry in entries
                ),
                key=lambda item: item[0].name,
            )
    except OSError as exc:
        raise ReleaseExecutorError(
            f"cannot enumerate inventory directory: {directory}"
        ) from exc


def _walk(root: Path):
    """Strict no-follow walk; callers may prune dirs before the next iteration.

    Unlike os.walk's default and pathlib glob, neither scandir nor per-entry stat
    errors are suppressed. Symlinks are yielded as leaves for caller validation.
    """
    pending = [root]
    while pending:
        directory = pending.pop()
        entries = _scan(directory)
        dirs = [path.name for path, info in entries if stat.S_ISDIR(info.st_mode)]
        files = [path.name for path, info in entries if not stat.S_ISDIR(info.st_mode)]
        yield directory, dirs, files
        pending.extend(directory / name for name in reversed(dirs))


def _glob_match(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    """Match declared glob components against an already strictly enumerated path."""
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return any(
            _glob_match(parts[offset:], pattern[1:]) for offset in range(len(parts) + 1)
        )
    return (
        bool(parts)
        and fnmatch.fnmatchcase(parts[0], pattern[0])
        and _glob_match(parts[1:], pattern[1:])
    )


def runtime_inventory(root: Path, commit: str) -> dict[str, Any]:
    """Distribution inventory, checked against Git plus closed execution trees."""
    config = document(root / "distribution.json")
    if config.get("schema") != "changerail.distribution-config.v1":
        raise ReleaseExecutorError("unsupported runtime distribution")
    names = {_name(n) for n in config["files"]}
    for directory, pattern in config["trees"].items():
        location = root / _name(directory)
        components = tuple(_name(pattern).split("/"))
        for parent, dirs, files in _walk(location):
            for leaf in dirs + files:
                path = parent / leaf
                if _glob_match(path.relative_to(location).parts, components):
                    names.add(path.relative_to(root).as_posix())
    if not REQUIRED <= names:
        raise ReleaseExecutorError("distribution omits required executor files")
    tree = {}
    for row in _git(root, "ls-tree", "-rz", commit).split(b"\0"):
        if row:
            header, name = row.split(b"\t", 1)
            mode, kind, oid = header.split()
            tree[name.decode()] = (mode, kind, oid.decode())
    # A checkout also contains committed tools not shipped in the distribution.
    # Verify these against the accepted Git tree without expanding archive
    # ownership. Importable roots remain closed against untracked injections.
    auxiliary = {
        name
        for name in tree
        if name not in names
        and (
            (name.startswith("scripts/") and not name.startswith("scripts/changerail/"))
            or (
                name.startswith("tools/openspec/")
                and not name.startswith("tools/openspec/node_modules/")
            )
            or ("/" not in name and Path(name).suffix in {".py", ".pyc", ".so"})
        )
    }
    for directory in EXECUTION_DIRS:
        for parent, dirs, leaves in _walk(root / directory):
            # Dependencies have their own strict inventory; do not traverse them
            # twice or mistake their conventional links for source additions.
            if parent == root / "tools/openspec" and "node_modules" in dirs:
                dirs.remove("node_modules")
            for leaf in dirs + leaves:
                path = parent / leaf
                name = path.relative_to(root).as_posix()
                if name == "tools/openspec/node_modules":
                    continue
                info = path.lstat()
                if stat.S_ISLNK(info.st_mode):
                    raise ReleaseExecutorError(f"linked execution input: {name}")
                if stat.S_ISDIR(info.st_mode):
                    continue
                if name in names or name in auxiliary:
                    continue
                # npm diagnostics are data, never Python/Node helper bodies.
                if (
                    name.startswith("tools/openspec/npm-logs/")
                    and path.suffix == ".log"
                    and stat.S_ISREG(info.st_mode)
                    and not info.st_mode & 0o111
                ):
                    continue
                raise ReleaseExecutorError(f"undeclared executable input: {name}")
    for path, info in _scan(root):
        if path.name == "__pycache__" and (
            not stat.S_ISDIR(info.st_mode) or _scan(path)
        ):
            raise ReleaseExecutorError("undeclared Python input: __pycache__")
        # Dotted overlay directories (.git/.runtime/.venv/...) are not top-level
        # Python package names. For potential packages a failed listing cannot
        # prove absence of __init__; searchable-only 0111 directories can import.
        package = False
        if stat.S_ISDIR(info.st_mode) and not path.name.startswith("."):
            package = any(
                child.name.startswith("__init__.") for child, _ in _scan(path)
            )
        elif (
            stat.S_ISLNK(info.st_mode)
            and not path.name.startswith(".")
            and stat.S_ISDIR(path.stat().st_mode)
        ):
            raise ReleaseExecutorError(f"linked Python input: {path.name}")
        importable = path.suffix in {".py", ".pyc", ".so"} or package
        if importable and path.name != "scripts" and path.name not in names | auxiliary:
            raise ReleaseExecutorError(f"undeclared Python input: {path.name}")
    files = {}
    for name in sorted(names | auxiliary):
        path = root / _name(name)
        data = regular(path)
        mode, kind, oid = tree.get(name, (None, None, ""))
        actual_mode = stat.S_IMODE(path.stat().st_mode)
        hasher = hashlib.sha1 if len(oid) == 40 else hashlib.sha256
        blob = hasher(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if (
            kind != b"blob"
            or mode not in {b"100644", b"100755"}
            or blob != oid
            or (bool(actual_mode & 0o111) != (mode == b"100755"))
        ):
            raise ReleaseExecutorError(
                f"runtime differs from accepted Git tree: {name}"
            )
        if name in names:
            files[name] = {
                "sha256": digest(data),
                "size": len(data),
                "mode": actual_mode,
            }
    return files


def _dependency_tree(root: Path, *, python_links: bool = False) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise ReleaseExecutorError(f"invalid dependency directory: {root}")
    result = {}
    for directory, dirs, files in _walk(root):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                target = path.resolve(strict=True)
                external_python = python_links and re.fullmatch(
                    r"bin/python(?:[0-9.]+)?", relative
                )
                if not target.is_relative_to(root) and not external_python:
                    raise ReleaseExecutorError(
                        f"dependency link escapes environment: {path}"
                    )
                entry = {"link": os.readlink(path), "resolved": str(target)}
                if target.is_file():
                    entry["target"] = _entry(target)
                elif not target.is_dir() or not target.is_relative_to(root):
                    raise ReleaseExecutorError(f"invalid dependency link: {path}")
                result[relative] = entry
            elif path.is_file():
                result[relative] = _entry(path)
            elif not path.is_dir():
                raise ReleaseExecutorError(f"special dependency input: {path}")
    return result


def dependency_inventory(
    root: Path, *, node: Path, python_info: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Hash installed bodies, symlinks and external interpreter/stdlib inputs.

    -I -S bootstrap ignores all .pth, sitecustomize and user/site paths. Venv
    site-packages is added explicitly after verification. External dependency
    links are forbidden except conventional venv Python executables.
    """
    python = root / ".venv/bin/python"
    target = python.resolve(strict=True)
    config = {}
    for line in regular(root / ".venv/pyvenv.cfg").decode().splitlines():
        key, separator, value = line.partition("=")
        if separator:
            key = key.strip().lower()
            if key in config:
                raise ReleaseExecutorError("duplicate executor venv configuration key")
            config[key] = value.strip()
    home = Path(config.get("home", ""))
    if not home.is_absolute() or home.resolve(strict=True) != target.parent:
        raise ReleaseExecutorError(
            "executor venv home differs from its base interpreter"
        )
    if python_info is None:
        # Acceptance-only inspection of the operator-selected interpreter.
        probe = subprocess.run(
            [
                str(target),
                "-I",
                "-S",
                "-B",
                "-c",
                "import json,sysconfig; print(json.dumps({'stdlib':sysconfig.get_path('stdlib'),'version':sysconfig.get_python_version()}))",
            ],
            env={"PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=True,
        )
        base = json.loads(probe.stdout)
        stdlib = canonical_root(Path(base["stdlib"]))
        site = root / f".venv/lib/python{base['version']}/site-packages"
    else:
        # Verification never executes the dependency being checked, even to
        # discover paths: these were explicitly accepted with its byte inventory.
        stdlib = canonical_root(Path(python_info["stdlib_root"]))
        site = Path(python_info["site_packages"])
        if not site.is_relative_to(root) or not re.fullmatch(
            r"\.venv/lib/python[0-9]+\.[0-9]+/site-packages",
            site.relative_to(root).as_posix(),
        ):
            raise ReleaseExecutorError("invalid accepted Python site-packages")
    # System site-packages are never on runner sys.path and may be very large.
    standard = {}
    for directory, dirs, files in _walk(stdlib):
        dirs[:] = [d for d in dirs if d not in {"site-packages", "dist-packages"}]
        for name in files:
            path = Path(directory) / name
            if path.is_symlink():
                target_path = path.resolve(strict=True)
                if target_path.is_dir():
                    raise ReleaseExecutorError("linked standard library directory")
                entry = {
                    "link": os.readlink(path),
                    "resolved": str(target_path),
                    "target": _entry(target_path),
                }
            else:
                entry = _entry(path)
            standard[path.relative_to(stdlib).as_posix()] = entry
        if any((Path(directory) / d).is_symlink() for d in dirs):
            raise ReleaseExecutorError("linked standard library directory")
    if not site.is_dir() or site.is_symlink():
        raise ReleaseExecutorError("executor venv site-packages missing")
    node = node.resolve(strict=True)
    return {
        "python": {
            "path": str(python),
            "target": str(target),
            "file": _entry(target),
            "stdlib_root": str(stdlib),
            "stdlib_sha256": digest(encoded(standard)),
            "site_packages": str(site),
        },
        "node": {"path": str(node), "file": _entry(node)},
        "files": {
            name: _dependency_tree(root / name, python_links=name == ".venv")
            for name in DEPENDENCY_DIRS
        },
    }


def inspect_release(
    root: Path, *, tag: str, node: Path, python_info: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Prepare an UNACCEPTED receipt candidate under updater's exclusive lease.

    Caller reviews provenance then atomically publishes encoded(result) at
    receipt_path(root), owner-only writable, while retaining the exclusive lock.
    This function neither accepts a release nor writes any authority.
    """
    root = canonical_root(root)
    _check_maintenance(root, updater=True)
    if not isinstance(tag, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._/-]*", tag
    ):
        raise ReleaseExecutorError("invalid explicit release tag")
    commit = (
        _git(root, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
        .decode()
        .strip()
    )
    tag_object = (
        _git(root, "rev-parse", "--verify", f"refs/tags/{tag}").decode().strip()
    )
    if _git(root, "rev-parse", "HEAD").decode().strip() != commit:
        raise ReleaseExecutorError("executor HEAD differs from accepted release tag")
    tree = _git(root, "rev-parse", f"{commit}^{{tree}}").decode().strip()
    files = runtime_inventory(root, commit)
    config = document(root / "distribution.json")
    dependencies = dependency_inventory(root, node=node, python_info=python_info)
    return {
        "schema": RECEIPT_SCHEMA,
        "engine_root": str(root),
        "release": {
            "tag": tag,
            "tag_object": tag_object,
            "commit": commit,
            "tree": tree,
            "version": config["version"],
        },
        "distribution": {
            "execution_contract": config["execution_contract"],
            "files": files,
            "payload_sha256": digest(encoded(files)),
        },
        "dependencies": dependencies,
    }


def verify_release(
    root: Path, *, accepted: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Verify exact accepted tag/commit/tree, distribution and dependency bytes.

    accepted is only for the trusted updater's already-authorized receipt. Normal
    execution MUST omit it and read the fixed external receipt authority.
    During maintenance, accepted= is the deliberate updater-only path and requires
    this process to hold exclusive_use(root). inspect_release has the same lease
    requirement during maintenance. No environment variable bypasses the fence.
    Caller must hold a use/exclusive lease over verification and subsequent use.
    """
    root = canonical_root(root)
    _check_maintenance(root, updater=accepted is not None)
    if accepted is None:
        path = receipt_path(root)
        accepted = document(path)
        if not _safe_owned(path.stat()):
            raise ReleaseExecutorError(
                "unsafe accepted release receipt ownership/permissions"
            )
    try:
        if accepted.get("schema") != RECEIPT_SCHEMA or accepted.get(
            "engine_root"
        ) != str(root):
            raise ReleaseExecutorError("invalid accepted release receipt")
        # Never execute a changed interpreter even for the isolated stdlib probe.
        interpreter = accepted["dependencies"]["python"]
        target = (root / ".venv/bin/python").resolve(strict=True)
        if (
            str(target) != interpreter["target"]
            or _entry(target) != interpreter["file"]
        ):
            raise ReleaseExecutorError(
                "Python dependency differs from accepted release receipt"
            )
        current = inspect_release(
            root,
            tag=accepted["release"]["tag"],
            node=Path(accepted["dependencies"]["node"]["path"]),
            python_info=interpreter,
        )
        if current != accepted:
            raise ReleaseExecutorError(
                "executor or dependencies differ from accepted release receipt"
            )
        return current
    except (KeyError, TypeError, AttributeError) as exc:
        raise ReleaseExecutorError("malformed accepted release receipt") from exc


def verify_binding(
    project: Path, *, expected_engine: Path | None = None
) -> dict[str, Any]:
    value = read_binding(project, expected_engine=expected_engine)
    root = Path(value["engine_root"])
    ensure_use(root)
    receipt = verify_release(root)
    dependencies = receipt["dependencies"]
    for path in (
        dependencies["python"]["target"],
        dependencies["python"]["stdlib_root"],
        dependencies["node"]["path"],
    ):
        if Path(path).is_relative_to(project):
            raise ReleaseExecutorError("executor dependency overlaps mutable project")
    return {
        **value,
        "engine_identity": digest(encoded(receipt)),
        "release_receipt": receipt,
    }


def require_runtime_source(root: Path, receipt: dict[str, Any]) -> None:
    """Reject direct imports using another interpreter/site or product sys.path."""
    python = receipt["dependencies"]["python"]
    expected = [
        str(root),
        python["site_packages"],
        python["stdlib_root"],
        str(Path(python["stdlib_root"]) / "lib-dynload"),
    ]
    if (
        not sys.flags.isolated
        or not sys.flags.no_site
        or Path(sys.executable).resolve(strict=True) != Path(python["target"])
        or sys.path != expected
    ):
        raise ReleaseExecutorError(
            "release runtime requires its isolated executor Python bootstrap"
        )


def bootstrap() -> None:
    """Invoked by an external launcher with system Python -I -S, never dev Python."""
    source = Path(__file__).resolve().parents[2]
    project = canonical_root(Path(os.environ["CHRL_PROJECT_ROOT"]))
    value = verify_binding(project, expected_engine=source)
    selected = os.environ.get("CHRL_ENGINE_ROOT")
    if selected is not None and selected != str(source):
        raise ReleaseExecutorError("engine environment differs from binding")
    python = value["release_receipt"]["dependencies"]["python"]
    for key in ("PYTHONPATH", "PYTHONHOME", "NODE_OPTIONS", "NODE_PATH"):
        os.environ.pop(key, None)
    os.environ.update(CHRL_ENGINE_ROOT=str(source), PYTHONDONTWRITEBYTECODE="1")
    # -I ignores PYTHONPATH, Python startup variables and cwd. -S prevents any
    # .pth/editable/sitecustomize execution; add only the verified executor site.
    code = (
        "import sys,runpy; "
        f"sys.path[:] = {[str(source), python['site_packages'], python['stdlib_root'], str(Path(python['stdlib_root']) / 'lib-dynload')]!r}; "
        "runpy.run_module('scripts.changerail.engine_runtime',run_name='__main__',alter_sys=True)"
    )
    os.chdir(project)
    os.execv(
        python["target"], [python["path"], "-I", "-S", "-B", "-c", code, *sys.argv[1:]]
    )


if __name__ == "__main__":
    try:
        bootstrap()
    except (
        ReleaseExecutorError,
        OSError,
        ValueError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"ChangeRail release executor: {exc}", file=sys.stderr)
        raise SystemExit(2)
