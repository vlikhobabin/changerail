"""Durable executor selection for future runs, without rewriting delivery history."""

from __future__ import annotations

import argparse
from datetime import datetime
from contextlib import contextmanager, ExitStack
import fcntl
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
from typing import Any

import distribution as dist
from scripts.changerail import engine_snapshot as snapshot
from scripts.changerail import release_executor as release

SCHEMA = "changerail.executor-binding-transition.v1"
TRANSACTIONS = ".runtime/changerail/executor-bindings"
LAUNCHERS = (".changerail/chrl", ".changerail/openspec")


class ExecutorBindingError(ValueError):
    """An exact future-run transition cannot be proven safe."""


def _sync(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _mkdir(path: Path) -> None:
    if not path.exists():
        _mkdir(path.parent)
        path.mkdir()
        _sync(path.parent)
    if path.is_symlink() or not path.is_dir():
        raise ExecutorBindingError("linked or non-directory transaction path")


def _append(path: Path, value: dict[str, Any]) -> None:
    data = release.encoded(value)
    if path.exists():
        if release.regular(path) != data:
            raise ExecutorBindingError("append-only receipt drift")
        return
    _mkdir(path.parent)
    fd, name = tempfile.mkstemp(prefix=".receipt-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        os.link(name, path, follow_symlinks=False)
        _sync(path.parent)
    finally:
        Path(name).unlink(missing_ok=True)


def _state(project: Path, name: str) -> dict[str, Any] | None:
    path = dist.confined(project, name)
    if not path.exists():
        return None
    raw = release.regular(path)
    return {"bytes": raw.hex(), "mode": stat.S_IMODE(path.stat().st_mode)}


def history_inventory(project: Path) -> dict[str, Any]:
    """Hash all retained runtime bytes/modes, including counters and review evidence."""
    result = {}
    root = dist.confined(project, ".runtime/changerail")
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(project).as_posix()
        if relative == TRANSACTIONS or relative.startswith(TRANSACTIONS + "/"):
            continue
        if path.is_symlink():
            raise ExecutorBindingError("linked history refused")
        if path.is_dir():
            result[relative] = {
                "directory": True,
                "mode": stat.S_IMODE(path.stat().st_mode),
            }
        elif relative != ".runtime/changerail/delivery.lock":
            raw = release.regular(path)
            result[relative] = {
                "sha256": release.digest(raw),
                "size": len(raw),
                "mode": stat.S_IMODE(path.stat().st_mode),
            }
    return result


def _quiescent(project: Path) -> None:
    snapshot._no_live_delivery(project)
    root = project / ".runtime/changerail"
    # Fail closed on unfinished or malformed verification, including old receipts.
    for path in root.rglob("*.json"):
        if path.is_relative_to(root / "executor-bindings"):
            continue
        if "verification-attempts" in path.parts:
            item = release.document(path)
            terminal = {
                "schema",
                "attempt_id",
                "run_id",
                "card",
                "lane",
                "record",
                "state",
                "outcome",
                "exit_code",
                "finished_at",
            }
            run_dir = path.parent.parent
            valid = (
                set(item) == terminal
                and item.get("attempt_id") == path.stem
                and item.get("run_id") == run_dir.name
            )
            try:
                datetime.strptime(item["finished_at"], "%Y-%m-%dT%H:%M:%SZ")
                dist.safe_name(item["card"])
                record = project / dist.safe_name(item["record"])
                lane_root = (
                    run_dir
                    / {
                        "focused": "focused-evidence",
                        "pre_review": "preverification",
                        "final": "verification",
                    }[item["lane"]]
                )
                valid = (
                    valid
                    and record.is_relative_to(lane_root)
                    and record.stem == path.stem
                )
            except (KeyError, TypeError, ValueError):
                valid = False
            valid = valid and (
                (item.get("outcome") == "exit" and type(item.get("exit_code")) is int)
                or (
                    item.get("outcome") == "spawn_failure"
                    and item.get("exit_code") is None
                )
            )
            if (
                not valid
                or item.get("schema") != "changerail.verification-attempt-intent.v1"
                or item.get("state") != "observed_terminal"
                or item.get("outcome") not in {"exit", "spawn_failure"}
                or not item.get("finished_at")
            ):
                raise ExecutorBindingError(
                    "unresolved verification attempt blocks binding"
                )
        elif any(
            part in {"focused-evidence", "preverification", "verification"}
            for part in path.parts
        ):
            item = release.document(path)
            if item.get("schema") == "changerail.check-result.v1" and (
                item.get("state") != "terminal"
                or item.get("outcome") not in {"exit", "spawn_failure"}
                or (
                    item.get("outcome") == "exit"
                    and type(item.get("exit_code")) is not int
                )
            ):
                raise ExecutorBindingError(
                    "unresolved verification check blocks binding"
                )


def _operator() -> None:
    if any(
        os.environ.get(k) for k in ("CHRL_RUN_DIR", "CHRL_SESSION_ROLE", release.USE_FD)
    ):
        raise ExecutorBindingError(
            "binding requires a separate operator outside a shared runtime session"
        )


@contextmanager
def _locks(project: Path):
    # Same order as snapshot rebind: project delivery, then project binding lock.
    with dist.delivery_lock(project):
        parent = dist.confined(project, ".changerail")
        _mkdir(parent)
        path = dist.confined(project, ".changerail/.engine-binding.lock")
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ExecutorBindingError("invalid binding lock")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ExecutorBindingError(
                    "another binding writer holds the project"
                ) from exc
            yield
        finally:
            os.close(fd)


@contextmanager
def _release_lease(root: Path):
    # Temporary coordinator lease, never inherited or installed in runtime env.
    fd = release._open_lock(root)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ExecutorBindingError(
                "executor maintenance holds the use lock"
            ) from exc
        yield release.verify_release(root)
    finally:
        os.close(fd)


def ensure_no_pending(project: Path, *, own: Path | None = None) -> None:
    root = dist.confined(project, TRANSACTIONS)
    if not root.exists():
        return
    for directory in root.iterdir():
        if directory.is_symlink():
            raise ExecutorBindingError("linked binding transaction")
        if own is not None and directory == own:
            continue
        if (directory / "intent.json").exists() and not (
            directory / "applied.json"
        ).exists():
            raise ExecutorBindingError(
                "pending executor binding requires exact reconcile"
            )


def _local_owned(project: Path, name: str) -> None:
    dist.confined(project, name)
    tracked = subprocess.run(
        ["git", "-C", str(project), "ls-files", "--", name],
        capture_output=True,
        check=True,
    )
    ignored = subprocess.run(
        ["git", "-C", str(project), "check-ignore", "-q", "--", name],
        capture_output=True,
    )
    if tracked.stdout or ignored.returncode != 0:
        raise ExecutorBindingError(
            f"generated binding/launcher must be ignored and untracked: {name}"
        )


def launcher(project: Path, root: Path, command: str) -> bytes:
    pending = shlex.quote(str(project / TRANSACTIONS)) + "/*/intent.json"
    fence = (
        f"for chrl_intent in {pending}; do\n"
        '  if [ -e "$chrl_intent" ] && [ ! -f "${chrl_intent%/*}/applied.json" ]; then\n'
        '    echo "ChangeRail: pending executor binding requires reconcile" >&2; exit 2\n'
        "  fi\ndone\n"
    )
    return (
        "#!/bin/sh\n# Generated by ChangeRail executor-binding v1.\nset -eu\n"
        + fence
        + "exec "
        + shlex.quote(str(root / "bin" / command))
        + " --project "
        + shlex.quote(str(project))
        + ' "$@"\n'
    ).encode()


def _known_launchers(project: Path) -> None:
    for name in LAUNCHERS:
        current = _state(project, name)
        if current is None:
            continue
        found = False
        for applied in (project / TRANSACTIONS).glob("*/applied.json"):
            proposal = release.document(applied.parent / "proposal.json")
            proof = release.document(applied)
            if (
                proof.get("proposal_sha256")
                == release.digest(release.encoded(proposal))
                and proposal.get("after", {}).get(name) == current
            ):
                found = True
                break
        if not found:
            raise ExecutorBindingError(f"unrelated or unknown local launcher: {name}")


def _selected(
    project: Path, root: Path, kind: str, stack: ExitStack
) -> tuple[dict[str, Any], str]:
    release.binding_document(project, root)  # canonical paths and disjoint roots
    if kind == "release":
        receipt = stack.enter_context(_release_lease(root))
        return release.binding_document(project, root), release.digest(
            release.encoded(receipt)
        )
    manifest = snapshot.verify_snapshot(root)
    identity = snapshot.snapshot_identity(manifest)
    return {
        "schema": snapshot.BINDING_SCHEMA,
        "project_root": str(project),
        "engine_root": str(root),
        "engine_identity": identity,
    }, identity


def _previous(
    project: Path, previous_identity: str | None, stack: ExitStack
) -> str | None:
    raw = _state(project, release.BINDING)
    if raw is None:
        if previous_identity is not None:
            raise ExecutorBindingError(
                "previous identity supplied for an unbound project"
            )
        return None
    if not previous_identity:
        raise ExecutorBindingError(
            "existing binding requires --previous-identity exactly"
        )
    value = json.loads(bytes.fromhex(raw["bytes"]))
    if value.get("schema") == snapshot.BINDING_SCHEMA:
        # Missing old snapshot is not proof; receipt or caller string cannot waive it.
        verified = snapshot.verify_binding(project)
        identity = verified["engine_identity"]
    elif value.get("schema") == release.BINDING_SCHEMA:
        verified = release.read_binding(project)
        receipt = stack.enter_context(_release_lease(Path(verified["engine_root"])))
        identity = release.digest(release.encoded(receipt))
    else:
        raise ExecutorBindingError("unsupported previous binding")
    if previous_identity != identity:
        raise ExecutorBindingError(
            "previous identity differs from verified current executor"
        )
    return identity


def prepare(
    project: Path,
    executor: Path,
    *,
    previous_identity: str | None = None,
    kind: str = "release",
    dry_run: bool = False,
) -> dict[str, Any]:
    _operator()
    project = dist.git_root(release.canonical_root(project))
    executor = release.canonical_root(executor)
    if kind not in {"release", "snapshot"}:
        raise ExecutorBindingError("unsupported executor kind")
    with _locks(project), ExitStack() as stack:
        ensure_no_pending(project)
        if os.path.lexists(project / ".changerail/source-link.json"):
            raise ExecutorBindingError(
                "detach shared-source binding before selecting an executor"
            )
        _quiescent(project)
        previous = _previous(project, previous_identity, stack)
        target, identity = _selected(project, executor, kind, stack)
        names = (*LAUNCHERS, release.BINDING)
        for name in names:
            _local_owned(project, name)
        before = {name: _state(project, name) for name in names}
        _known_launchers(project)
        after = {
            name: {
                "bytes": launcher(project, executor, Path(name).name).hex(),
                "mode": 0o755,
            }
            for name in LAUNCHERS
        }
        after[release.BINDING] = {"bytes": release.encoded(target).hex(), "mode": 0o644}
        value = {
            "schema": SCHEMA,
            "project": str(project),
            "executor": str(executor),
            "kind": kind,
            "previous_identity": previous,
            "identity": identity,
            "before": before,
            "after": after,
            "history": history_inventory(project),
            "scope": "future-runs-only",
        }
        path = (
            project
            / TRANSACTIONS
            / release.digest(release.encoded(value))
            / "proposal.json"
        )
        if not dry_run:
            _local_owned(project, path.relative_to(project).as_posix())
            _append(path, value)
        return {"proposal": str(path), "dry_run": dry_run, **value}


def _load(proposal: Path) -> tuple[Path, dict[str, Any]]:
    value = release.document(proposal)
    project = release.canonical_root(Path(value["project"]))
    expected = (
        project
        / TRANSACTIONS
        / release.digest(release.encoded(value))
        / "proposal.json"
    )
    if (
        proposal != expected
        or value.get("schema") != SCHEMA
        or value.get("scope") != "future-runs-only"
    ):
        raise ExecutorBindingError(
            "invalid exact binding proposal location or authority"
        )
    if set(value["before"]) != {*LAUNCHERS, release.BINDING} or set(
        value["after"]
    ) != set(value["before"]):
        raise ExecutorBindingError("invalid proposal write scope")
    return project, value


def _replace(project: Path, name: str, state: dict[str, Any]) -> None:
    target = dist.confined(project, name)
    dist.write_atomic(target, bytes.fromhex(state["bytes"]), state["mode"])
    _sync(target.parent)


def apply(
    proposal: Path, *, reconcile: bool = False, dry_run: bool = False
) -> dict[str, Any]:
    _operator()
    project, value = _load(proposal)
    with _locks(project), ExitStack() as stack:
        ensure_no_pending(project, own=proposal.parent)
        _quiescent(project)
        if os.path.lexists(project / ".changerail/source-link.json"):
            raise ExecutorBindingError(
                "shared-source binding overlaps executor binding"
            )
        current_history = history_inventory(project)
        intent = proposal.parent / "intent.json"
        applied = proposal.parent / "applied.json"
        proof = {
            "schema": SCHEMA,
            "proposal_sha256": release.digest(release.encoded(value)),
            "identity": value["identity"],
            "scope": "future-runs-only",
        }
        interrupted = intent.exists()
        if interrupted and release.document(intent) != proof:
            raise ExecutorBindingError("binding intent drift")
        if applied.exists():
            # Later independent runs may extend history after an applied binding.
            # Re-apply is read-only, but must still preserve every original entry.
            if any(
                current_history.get(name) != expected
                for name, expected in value["history"].items()
            ):
                raise ExecutorBindingError(
                    "original retained history changed after binding"
                )
            if (
                not interrupted
                or release.document(applied) != proof
                or any(_state(project, n) != s for n, s in value["after"].items())
            ):
                raise ExecutorBindingError("applied binding drift")
            return {**proof, "state": "applied", "dry_run": dry_run}
        if current_history != value["history"]:
            raise ExecutorBindingError(
                "retained history changed after binding preparation"
            )
        if interrupted and not reconcile:
            raise ExecutorBindingError("interrupted binding requires reconcile")
        target, identity = _selected(
            project, Path(value["executor"]), value["kind"], stack
        )
        if identity != value["identity"] or value["after"][release.BINDING] != {
            "bytes": release.encoded(target).hex(),
            "mode": 0o644,
        }:
            raise ExecutorBindingError("selected executor identity changed")
        for name in LAUNCHERS:
            if value["after"][name] != {
                "bytes": launcher(
                    project, Path(value["executor"]), Path(name).name
                ).hex(),
                "mode": 0o755,
            }:
                raise ExecutorBindingError(
                    "proposal launcher differs from selected executor"
                )
        for name, before in value["before"].items():
            _local_owned(project, name)
            allowed = (before, value["after"][name]) if interrupted else (before,)
            if _state(project, name) not in allowed:
                raise ExecutorBindingError(
                    "expected before binding or launcher bytes changed"
                )
        if not interrupted:
            _previous(project, value["previous_identity"], stack)
            _known_launchers(project)
        if dry_run:
            return {**proof, "state": "preview", "dry_run": True}
        _append(intent, proof)
        # Launchers first, binding last; pending intent fences ordinary new commands.
        for name in (*LAUNCHERS, release.BINDING):
            if _state(project, name) != value["after"][name]:
                _replace(project, name, value["after"][name])
        _quiescent(project)
        if history_inventory(project) != value["history"]:
            raise ExecutorBindingError(
                "history changed during binding; reconciliation required"
            )
        _append(applied, proof)
        if reconcile:
            _append(proposal.parent / "reconciled.json", proof)
        return {**proof, "state": "applied", "dry_run": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare")
    preparation.add_argument("--project", type=Path, required=True)
    preparation.add_argument("--executor", type=Path, required=True)
    preparation.add_argument("--previous-identity")
    preparation.add_argument(
        "--kind", choices=("release", "snapshot"), default="release"
    )
    preparation.add_argument("--dry-run", action="store_true")
    for name in ("apply", "reconcile"):
        command = commands.add_parser(name)
        command.add_argument("proposal", type=Path)
        command.add_argument("--dry-run", action="store_true")
    args = vars(parser.parse_args(argv))
    command = args.pop("command")
    try:
        result = (
            prepare(**args)
            if command == "prepare"
            else apply(**args, reconcile=command == "reconcile")
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"ChangeRail executor binding: {exc}", file=sys.stderr)
        return 2
