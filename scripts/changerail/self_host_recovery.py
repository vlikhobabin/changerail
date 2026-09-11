"""Explicit, append-only transition from self-host history to a pinned engine.

Payload snapshots contain the original changed paths, with their original modes;
missing paths represent retained deletions. They are evidence, never authority to
modify the predecessor. Each transition reserves its source and destination before
publishing one successor; reconciliation never dispatches a writer.
"""

from __future__ import annotations

import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import uuid
from typing import Any

from scripts.changerail.contracts import DeliveryError
from scripts.changerail import openspec_context as native
from scripts.changerail.technical_recovery import _write, _sync

SCHEMA = "changerail.self-host-recovery.v1"
LIMIT = 32 * 1024 * 1024
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def _bytes(d: Any, path: Path, limit: int = LIMIT) -> bytes:
    path = _safe(path)
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(
            path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_nlink != 1
                or before.st_size > limit
            ):
                raise DeliveryError("unsafe self-host recovery evidence")
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
            if len(raw) != before.st_size or before.st_mtime_ns != after.st_mtime_ns:
                raise DeliveryError("self-host evidence changed while reading")
            return raw
    finally:
        os.close(directory)


def _json(d: Any, path: Path) -> dict:
    return d._check_json_bytes(_bytes(d, path, LIMIT * 32))


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _safe(path: Path) -> Path:
    path = path.absolute()
    if path.resolve() != path:
        raise DeliveryError("self-host recovery rejects linked paths")
    return path


def _run(path: Path) -> Path:
    path = _safe(path)
    if not NAME.fullmatch(path.name) or path.parent.parts[-3:] != (
        ".runtime",
        "changerail",
        "runs",
    ):
        raise DeliveryError("self-host recovery requires an exact retained run")
    return path


def _root(d: Any, run: Path) -> Path:
    return _safe(d.RUNTIME_ROOT / "self-host-recoveries" / run.name)


def _source(run: Path) -> Path:
    return run.parents[3]


def _inventory(d: Any, directory: Path) -> dict:
    _safe(directory)
    result = {".": {"directory": True, "mode": stat.S_IMODE(directory.stat().st_mode)}}
    for path in sorted(directory.rglob("*")):
        _safe(path)
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            value = {"directory": True, "mode": stat.S_IMODE(info.st_mode)}
        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            value = {
                "sha256": _digest(_bytes(d, path, LIMIT)),
                "mode": stat.S_IMODE(info.st_mode),
            }
        else:
            raise DeliveryError("self-host history contains an unsafe entry")
        result[path.relative_to(directory).as_posix()] = value
        if len(result) > 100000:
            raise DeliveryError("self-host history inventory exceeds limit")
    return result


def _engine(d: Any) -> dict:
    from scripts.changerail import engine_snapshot
    from scripts.changerail import engine_runtime

    binding = engine_snapshot.verify_binding(d.REPO_ROOT)
    # Execution must actually originate from the selected snapshot, not merely
    # have a valid binding sitting next to mutable Python modules.
    if engine_runtime.identity(d) is None:
        raise DeliveryError("self-host recovery requires an active engine binding")
    return binding


def _live(roots: list[Path]) -> None:
    for process in Path("/proc").glob("[0-9]*"):
        try:
            if process.stat().st_uid != os.getuid() or int(process.name) == os.getpid():
                continue
            environment = process.joinpath("environ").read_bytes().split(b"\0")
            for item in environment:
                if item.startswith(b"CHRL_RUN_DIR="):
                    owner = Path(os.fsdecode(item.split(b"=", 1)[1])).resolve()
                    if any(
                        owner.is_relative_to(root / ".runtime/changerail")
                        for root in roots
                    ):
                        raise DeliveryError(
                            "self-host recovery found a live process owner"
                        )
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as exc:
            # Login/service daemons may be nondumpable despite sharing the uid.
            # Their public command line still distinguishes them from execution
            # owners. An opaque runner candidate must remain fail-closed.
            command = process.joinpath("cmdline").read_bytes()
            candidates = (
                b"python",
                b"codex",
                b"chrl",
                b"changerail",
                b"pytest",
                b"bash",
                b"/sh",
            )
            if not command or any(
                word in command.split(b"\0", 1)[0] for word in candidates
            ):
                raise DeliveryError("cannot establish process quiescence") from exc


@contextmanager
def _locks(d: Any, run: Path):
    if os.environ.get("CHRL_SESSION_ROLE"):
        raise DeliveryError("self-host recovery requires an operator outside delivery")
    descriptors = []
    try:
        for root in sorted({d.REPO_ROOT, _source(run)}, key=str):
            directory = _safe(root / ".runtime/changerail")
            directory.mkdir(parents=True, exist_ok=True)
            fd = os.open(
                directory / "delivery.lock",
                os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW,
                0o600,
            )
            descriptors.append(fd)
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise DeliveryError("self-host delivery lock is unsafe")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise DeliveryError("another delivery runner holds a checkout") from exc
        _live([d.REPO_ROOT, _source(run)])
        yield
    finally:
        for fd in descriptors:
            os.close(fd)


def _lineage(d: Any, run: Path) -> list[Path]:
    result = []
    owner = None
    while True:
        if run in result or len(result) >= 1000:
            raise DeliveryError("cyclic self-host predecessor ancestry")
        value = _json(d, run / "run.json")
        if (
            value.get("schema") != "changerail.delivery-run.v2"
            or value.get("run_id") != run.name
            or value.get("execution_contract") != "changerail.native.v1"
            or value.get("lifecycle_mode") != "openspec-v1"
            or not value.get("finished_at")
            or type(value.get("exit_code")) is not int
            or value["exit_code"] in (0, 130, -2)
        ):
            raise DeliveryError(
                "self-host predecessor is not a stopped failed native run"
            )
        if owner is not None and value.get("card") != owner:
            raise DeliveryError("foreign self-host ancestor card")
        owner = value.get("card")
        result.append(run)
        previous = value.get("recovery_of")
        if previous is None:
            return result
        if not isinstance(previous, str) or not NAME.fullmatch(previous):
            raise DeliveryError("unsafe self-host ancestor")
        run = _run(run.parent / previous)


def _entry(path: Path) -> dict | None:
    _safe(path)
    if not path.exists():
        return None
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > LIMIT:
        raise DeliveryError("payload snapshot requires bounded regular files")
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "bytes": base64.b64encode(_bytes(None, path, LIMIT)).decode(),
    }


def _path_digest(relative: str, value: dict | None) -> str:
    digest = hashlib.sha256(f"path\0{relative}\0".encode())
    if value is None:
        digest.update(b"deleted\0")
    else:
        digest.update(f"mode\0{stat.S_IFREG | value['mode']:o}\0".encode())
        digest.update(b"file\0" + base64.b64decode(value["bytes"]) + b"\0")
    return "sha256:" + digest.hexdigest()


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )
    if result.returncode:
        raise DeliveryError("self-host recovery cannot verify common Git history")
    return result.stdout


def _baseline_entry(root: Path, baseline: str, relative: str) -> dict | None:
    row = _git(root, "ls-tree", "-z", baseline, "--", relative)
    if not row:
        return None
    mode, kind, _oid = row.split(b"\t", 1)[0].split()
    if kind != b"blob" or mode not in (b"100644", b"100755"):
        raise DeliveryError("self-host corrective baseline has an unsafe entry")
    raw = _git(root, "show", f"{baseline}:{relative}")
    if len(raw) > LIMIT:
        raise DeliveryError("self-host corrective baseline exceeds limit")
    return {"mode": int(mode, 8) & 0o777, "bytes": base64.b64encode(raw).decode()}


def _payload(
    d: Any, run: Path, snapshot: Path | None, retained: dict | None = None
) -> tuple[dict, list]:
    manifest = _json(d, run / "manifest.json")
    paths = manifest.get("paths")
    hashes = manifest.get("path_fingerprints")
    baseline = manifest.get("baseline_head")
    if (
        manifest.get("schema") != "changerail.delivery-manifest.v1"
        or manifest.get("run_id") != run.name
        or not isinstance(paths, list)
        or len(paths) != len(set(paths))
        or not isinstance(hashes, dict)
        or set(paths) != set(hashes)
        or not isinstance(baseline, str)
        or not re.fullmatch(r"[0-9a-f]{40,64}", baseline)
    ):
        raise DeliveryError("self-host predecessor manifest is incomplete")
    for root in (_source(run), d.REPO_ROOT):
        _git(root, "merge-base", "--is-ancestor", baseline, "HEAD")
    old = {}
    for relative in paths:
        d._safe_path(relative)
        if retained is not None:
            if (
                relative not in retained
                or _path_digest(relative, retained[relative]) != hashes[relative]
            ):
                raise DeliveryError("retained payload bytes changed in the proposal")
            old[relative] = retained[relative]
            continue
        candidates = [snapshot] if snapshot is not None else [_source(run), d.REPO_ROOT]
        for source in candidates:
            value = _entry(source / relative)
            if _path_digest(relative, value) == hashes[relative]:
                old[relative] = value
                break
        else:
            raise DeliveryError(
                f"retained payload bytes unavailable for {relative}; supply an exact payload snapshot"
            )
    digest = hashlib.sha256(f"head\0{baseline}\0".encode())
    for relative in sorted(paths):
        value = old[relative]
        digest.update(f"path\0{relative}\0".encode())
        if value is None:
            digest.update(b"deleted\0")
        else:
            digest.update(f"mode\0{stat.S_IFREG | value['mode']:o}\0".encode())
            digest.update(b"file\0" + base64.b64decode(value["bytes"]) + b"\0")
    if manifest.get("fingerprint") != {
        "head_commit": baseline,
        "payload_fingerprint": "sha256:" + digest.hexdigest(),
    }:
        raise DeliveryError("retained payload bytes differ from manifest fingerprint")
    committed = _git(
        d.REPO_ROOT, "diff", "--name-only", "--no-renames", "-z", baseline, "HEAD"
    ).split(b"\0")
    selection = sorted(
        set(paths) | set(d.changed_paths()) | {os.fsdecode(p) for p in committed if p}
    )
    delta = []
    for relative in selection:
        d._safe_path(relative)
        before = (
            old[relative]
            if relative in old
            else _baseline_entry(d.REPO_ROOT, baseline, relative)
        )
        after = _entry(d.REPO_ROOT / relative)
        if before != after:
            delta.append({"path": relative, "before": before, "after": after})
    return old, delta


def _handled_capacity(d: Any, source: Path, session: Path, lineage: list[Path]) -> dict:
    """Accept only the exact historical failure consumed by a technical receipt."""
    from types import SimpleNamespace
    from scripts.changerail import technical_recovery as technical

    reader = SimpleNamespace(
        _check_bytes=lambda path, limit=LIMIT: _bytes(d, path, limit),
        _check_json=lambda path: _json(d, path),
    )
    failure = technical.classify_session(reader, session)
    receipts = (
        _source(source) / ".runtime/changerail/technical-recoveries" / source.name
    )
    proposal = _json(d, receipts / "proposal.json")
    applied = _json(d, receipts / "applied.json")
    intent = _json(d, receipts / "successor-intent.json")
    proposal_hash = _digest(_bytes(d, receipts / "proposal.json"))
    if (
        proposal.get("schema") != technical.SCHEMA
        or proposal.get("predecessor") != source.name
        or proposal.get("failure") != failure
        or proposal.get("predecessor_inventory") != technical._inventory(reader, source)
        or proposal.get("run_sha256") != _digest(_bytes(d, source / "run.json"))
        or any(
            receipt.get("schema") != technical.SCHEMA
            or receipt.get("predecessor") != source.name
            or receipt.get("proposal_sha256") != proposal_hash
            or receipt.get("fallback") != proposal.get("fallback")
            for receipt in (applied, intent)
        )
    ):
        raise DeliveryError("self-host historical session technical receipt differs")
    children = [path for path in lineage if path.name == intent.get("successor")]
    if len(children) != 1 or children[0] == source:
        raise DeliveryError("self-host historical session has no technical successor")
    child = _json(d, children[0] / "run.json")
    authority = child.get("technical_recovery", {})
    if (
        child.get("recovery_of") != source.name
        or authority.get("schema") != technical.SCHEMA
        or authority.get("proposal_sha256") != proposal_hash
        or authority.get("next_group") != proposal.get("next_group")
        or authority.get("fallback") != proposal.get("fallback")
        or not isinstance(intent.get("run_identity"), dict)
        or any(child.get(key) != value for key, value in intent["run_identity"].items())
    ):
        raise DeliveryError("self-host historical session successor authority differs")
    return {str(receipts): _inventory(d, receipts)}


def _boundary(d: Any, run: Path) -> dict:
    engine = _engine(d)
    lineage = _lineage(d, run)
    metadata = _json(d, run / "run.json")
    reason = metadata.get("terminal_reason", "")
    if not isinstance(reason, str) or not (
        reason
        in {
            "implementation session exited without a handoff",
            "frozen execution process changed; ordinary recovery cannot adopt new code or profile",
        }
    ):
        raise DeliveryError(
            "self-host recovery requires a known pre-review finalization stop"
        )
    card = d.resolve_deliverable_card(metadata["card"])
    if (
        card.parent.name != "3.inprogress"
        or d.board_activity().get("active") != [card]
        or d.staged_paths()
    ):
        raise DeliveryError(
            "self-host recovery requires one active card and an empty index"
        )
    for ancestor in reversed(lineage):
        _copy_history(
            d,
            ancestor,
            d.RUNTIME_ROOT / "runs" / ancestor.name,
            _inventory(d, ancestor),
        )
    local_run = d.RUNTIME_ROOT / "runs" / run.name
    native.require_plan(d, card, local_run / "native-plan.json")
    plan = d.declared_change_plan(local_run)
    events = d.combined_change_events(local_run)
    if not plan or any(
        row["status"] != "complete"
        for row in d.change_checkpoint_statuses(plan, events)
    ):
        raise DeliveryError("self-host recovery requires all task groups complete")
    review_count = 0
    technical_receipts = {}
    for source_ancestor in lineage:
        ancestor = d.RUNTIME_ROOT / "runs" / source_ancestor.name
        for prohibited in (
            "reviews",
            "native-archive-intent.json",
            "native-archive.json",
            "native-review-continuation.json",
            "verification.json",
            "publication.json",
            "publication-journal.json",
        ):
            if (ancestor / prohibited).exists():
                raise DeliveryError(
                    "self-host recovery cannot cross review, archive, final or publication"
                )
        if any(
            event.get("phase") in {"review", "verify", "publish", "archive"}
            for event in d.read_phase_events(ancestor)
        ):
            raise DeliveryError("self-host recovery cannot cross a review/final event")
        if any(d.review_budget_usage(ancestor).values()):
            raise DeliveryError(
                "self-host recovery cannot cross consumed review accounting"
            )
        if d._unresolved_verification_attempt(ancestor):
            raise DeliveryError(
                "self-host recovery rejects an unresolved verification attempt"
            )
        for attempt in (ancestor / "verification-attempts").glob("*.json"):
            if _json(d, attempt).get("lane") == "final":
                raise DeliveryError(
                    "self-host recovery cannot cross a final floor attempt"
                )
        for directory in (ancestor / "sessions").glob("*"):
            session = directory / "session.json"
            if not directory.is_dir() or not session.is_file():
                raise DeliveryError("self-host recovery requires every session receipt")
            value = _json(d, session)
            terminal = value.get("stop_reason")
            if terminal == "nonzero_exit" and source_ancestor != run:
                technical_receipts.update(
                    _handled_capacity(
                        d,
                        source_ancestor,
                        source_ancestor / "sessions" / directory.name,
                        lineage,
                    )
                )
                continue
            expected_complete = {
                "completed": True,
                "incomplete_session_no_artifact": False,
            }
            if (
                not value.get("finished_at")
                or type(value.get("exit_code")) is not int
                or value["exit_code"] != 0
                or value.get("interrupted") is not False
                or value.get("timed_out") is not False
                or value.get("role") != "implementation"
                or terminal not in expected_complete
                or value.get("completed") is not expected_complete.get(terminal)
            ):
                raise DeliveryError(
                    "self-host recovery rejects unknown, live or operator-stopped session"
                )
    identity = metadata.get("process_identity")
    if not isinstance(identity, dict):
        raise DeliveryError("self-host predecessor lacks execution identity")
    from scripts.changerail.engine_runtime import project_execution_identity

    inputs = project_execution_identity(d)
    old_controls = {key for key in identity if key.startswith(".changerail/")}
    old_controls.discard(".changerail/engine-binding.json")
    for key in old_controls:
        path = _safe(d.REPO_ROOT / d._safe_path(key))
        inputs[key] = hashlib.sha256(_bytes(d, path, LIMIT)).hexdigest()
    for key in (".changerail/distribution-lock.json", ".changerail/source-link.json"):
        path = d.REPO_ROOT / key
        if path.exists() and key not in identity:
            raise DeliveryError("self-host project binding changed")
    if any(identity.get(key) != value for key, value in inputs.items()):
        raise DeliveryError("self-host project execution inputs changed")
    for key, value in inputs.items():
        path = _safe(_source(run) / key)
        if hashlib.sha256(_bytes(d, path, LIMIT)).hexdigest() != value:
            raise DeliveryError("self-host origin project execution inputs changed")
    return {
        "engine": engine,
        "card": d.repo_relative(card),
        "lineage": {str(path): _inventory(d, path) for path in lineage},
        "technical_receipts": technical_receipts,
        "accepted_plan": _json(d, run / "native-plan.json"),
        "change_events": events,
        "review_budget": {"semantic_cycles": review_count},
        "execution_identity": d.execution_identity(),
        "payload": d.payload_fingerprint(),
        "paths": d.changed_paths(),
    }


def _proposal(d: Any, run: Path) -> dict:
    value = _json(d, _root(d, run) / "proposal.json")
    if (
        value.get("schema") != SCHEMA
        or value.get("source_run") != str(run)
        or value.get("project") != str(d.REPO_ROOT)
    ):
        raise DeliveryError("self-host recovery proposal belongs to another owner")
    return value


def _corrective_intact(d: Any, run: Path, proposal: dict) -> None:
    old, delta = _payload(d, run, None, retained=proposal["old_payload"])
    if old != proposal["old_payload"] or delta != proposal["corrective_diff"]:
        raise DeliveryError("self-host exact corrective diff changed")


def _intact(d: Any, proposal: dict) -> None:
    for name, inventory in proposal["boundary"]["lineage"].items():
        if _inventory(d, Path(name)) != inventory:
            raise DeliveryError("self-host predecessor history drifted")
    if _engine(d) != proposal["boundary"]["engine"]:
        raise DeliveryError("self-host engine binding drifted")
    if d.execution_identity() != proposal["boundary"]["execution_identity"]:
        raise DeliveryError("self-host execution inputs drifted")


def prepare(d: Any, run_dir: Path, *, payload_snapshot: Path | None = None) -> dict:
    run = _run(run_dir)
    with _locks(d, run):
        directory = _root(d, run)
        if (directory / "proposal.json").exists():
            proposal = _proposal(d, run)
            _intact(d, proposal)
            if _boundary(d, run) != proposal["boundary"]:
                raise DeliveryError("self-host prepared boundary drifted")
            return {"state": "prepared", "proposal": str(directory / "proposal.json")}
        # Resolve original bytes before admission so missing history never looks
        # like an authorized hash-only corrective diff.
        before = d.payload_fingerprint()
        old, delta = _payload(
            d, run, _safe(payload_snapshot) if payload_snapshot else None
        )
        boundary = _boundary(d, run)
        if boundary["payload"] != before:
            raise DeliveryError("self-host payload changed during preparation")
        proposal = {
            "schema": SCHEMA,
            "source_run": str(run),
            "project": str(d.REPO_ROOT),
            "boundary": boundary,
            "old_payload": old,
            "corrective_diff": delta,
        }
        directory.mkdir(parents=True, exist_ok=True)
        _write(directory / "proposal.json", proposal)
        return {"state": "prepared", "proposal": str(directory / "proposal.json")}


def _copy_history(d: Any, origin: Path, target: Path, expected: dict) -> None:
    _safe(target)
    if target.exists():
        if _inventory(d, target) != expected:
            raise DeliveryError("self-host local history differs from its origin")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = target.parent / ("." + target.name + ".history-" + uuid.uuid4().hex)
    shutil.copytree(origin, staged, copy_function=shutil.copy2)
    if _inventory(d, staged) != expected or _inventory(d, origin) != expected:
        raise DeliveryError("self-host history changed while copying")
    _durable(staged)
    os.rename(staged, target)
    _sync(target.parent)


def _durable(directory: Path) -> None:
    for path in sorted(directory.rglob("*"), reverse=True):
        if path.is_file():
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        elif path.is_dir():
            _sync(path)
    _sync(directory)


def _reservation(d: Any, run: Path, proposal: dict, *, create: bool) -> dict | None:
    directory = _safe(_source(run) / ".runtime/changerail/self-host-transitions")
    path = directory / (run.name + ".json")
    expected = {
        "schema": SCHEMA,
        "source_run": str(run),
        "project": str(d.REPO_ROOT),
        "proposal_sha256": _digest(
            _bytes(d, _root(d, run) / "proposal.json", LIMIT * 32)
        ),
    }
    if not path.exists():
        if not create:
            return None
        # Detect a successor created by any existing recovery mechanism before
        # claiming the source. The shared origin lock closes the creation race.
        for root in {run.parent, d.RUNTIME_ROOT / "runs"}:
            for candidate in root.glob("*/run.json"):
                if _json(d, candidate).get("recovery_of") == run.name:
                    raise DeliveryError("self-host predecessor already has a successor")
        directory.mkdir(parents=True, exist_ok=True)
        _write(path, {**expected, "successor": "self-host-" + uuid.uuid4().hex})
    value = _json(d, path)
    if any(
        value.get(key) != item for key, item in expected.items()
    ) or not NAME.fullmatch(str(value.get("successor", ""))):
        raise DeliveryError("self-host predecessor reserved by another transition")
    return value


def _inherit_admission(d: Any, previous: Path, card: str, directory: Path) -> None:
    """Import the exact retained plan, never regenerate or re-accept it."""
    from scripts.changerail.engine_snapshot import _publish_directory

    destination = _safe(d.RUNTIME_ROOT / "native-plans" / Path(card).stem)
    raw = _bytes(d, previous / "native-plan.json", LIMIT)
    if destination.exists():
        target = destination / "native-plan.json"
        if not target.is_file() or _bytes(d, target, LIMIT) != raw:
            raise DeliveryError(
                "self-host admission differs from retained accepted plan"
            )
        return
    staged = directory / "admission-preparations" / uuid.uuid4().hex
    staged.mkdir(parents=True)
    with (staged / "native-plan.json").open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    _sync(staged)
    destination.parent.mkdir(parents=True, exist_ok=True)
    _publish_directory(staged, destination)
    _sync(destination.parent)
    _sync(staged.parent)


def _make_successor(d: Any, run: Path, proposal: dict, reservation: dict) -> Path:
    directory = _root(d, run)
    successor = _safe(d.RUNTIME_ROOT / "runs" / reservation["successor"])
    intent_path = directory / "successor-intent.json"
    if not intent_path.exists():
        if successor.exists():
            raise DeliveryError("self-host successor appeared without its intent")
        for origin, inventory in reversed(
            list(proposal["boundary"]["lineage"].items())
        ):
            _copy_history(
                d, Path(origin), d.RUNTIME_ROOT / "runs" / Path(origin).name, inventory
            )
        previous = d.RUNTIME_ROOT / "runs" / run.name
        staged = (
            directory / "successor-preparations" / uuid.uuid4().hex / successor.name
        )
        staged.mkdir(parents=True)
        selection = {
            "schema": "changerail.observed-proof-selection.v1",
            "root": d.repo_relative(successor),
            "owner": {"run_id": successor.name, "card": proposal["boundary"]["card"]},
            "required_stages": ["implementation", "review", "final"],
        }
        raw_selection = (
            json.dumps(selection, sort_keys=True, indent=2) + "\n"
        ).encode()
        reference = {
            "path": d.repo_relative(successor / "observed-proof-selection.json"),
            "sha256": hashlib.sha256(raw_selection).hexdigest(),
        }
        # Build context using its staging selection, then bind to the published
        # destination before intent. No staged paths escape the atomic publish.
        staging_selection = {**selection, "root": d.repo_relative(staged)}
        raw_staging = (
            json.dumps(staging_selection, sort_keys=True, indent=2) + "\n"
        ).encode()
        staging_reference = {
            "path": d.repo_relative(staged / "observed-proof-selection.json"),
            "sha256": hashlib.sha256(raw_staging).hexdigest(),
        }
        metadata = {
            "schema": "changerail.delivery-run.v2",
            "run_id": successor.name,
            "card": proposal["boundary"]["card"],
            "started_at": d.utc_now(),
            "baseline_head": proposal["boundary"]["payload"]["head_commit"],
            "profile": d.repo_relative(d.PROFILE_PATH),
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": _json(d, previous / "run.json")["change_plan"],
            "execution_contract": "changerail.native.v1",
            "process_identity": proposal["boundary"]["execution_identity"],
            "recovery_of": run.name,
            "self_host_recovery": reservation,
            "observed_proof_contract": {
                "schema": d._OBSERVED_PROOF_CONTRACT,
                "required_stages": ["implementation", "review", "final"],
                "selection": staging_reference,
            },
        }
        d.write_json(staged / "run.json", metadata)
        (staged / "observed-proof-selection.json").write_bytes(raw_staging)
        context_path = d.build_recovery_context(
            run_dir=staged,
            previous_run=previous,
            objective="Finalize completed groups under the frozen self-host engine, then follow ordinary review/archive/final/publication gates.",
        )
        context = _json(d, context_path)
        context.update(
            resume_strategy="fresh_finalize",
            source_thread_id=None,
            resumed_thread_id=None,
            observed_proof_selection=reference,
            previous_completed_review=None,
        )
        for evidence in context.get("retained_focused_evidence", []):
            evidence.update(
                proof_status="historical/unconfirmed", matches_current_payload=False
            )
        context["instruction"] += (
            " Self-host transition invalidates old evidence for current admission. Refresh implementation proof and semantic sync; do not replay completed groups."
        )
        if context["inherited_review_budget"] != proposal["boundary"]["review_budget"]:
            raise DeliveryError("self-host inherited review accounting differs")
        metadata.update(
            inherited_change_events=context["inherited_change_events"],
            recovery_session_strategy="fresh_finalize",
        )
        metadata["observed_proof_contract"]["selection"] = reference
        d.write_json(staged / "run.json", metadata)
        d.write_json(context_path, context)
        (staged / "observed-proof-selection.json").write_bytes(raw_selection)
        (staged / "native-plan.json").write_bytes(
            _bytes(d, previous / "native-plan.json", LIMIT)
        )
        manifest = {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": successor.name,
            "baseline_head": metadata["baseline_head"],
            "created_at": d.utc_now(),
            "card": {"id": Path(metadata["card"]).stem, "path": metadata["card"]},
            "paths": proposal["boundary"]["paths"],
            "fingerprint": proposal["boundary"]["payload"],
            "path_fingerprints": d.path_fingerprints(proposal["boundary"]["paths"]),
            "observed_proof_selection": reference,
        }
        d.write_json(staged / "manifest.json", manifest)
        if _boundary(d, run) != proposal["boundary"]:
            raise DeliveryError(
                "self-host boundary changed during successor preparation"
            )
        _durable(staged)
        _write(
            intent_path,
            {
                "schema": SCHEMA,
                "reservation": reservation,
                "staged": str(staged),
                "inventory": _inventory(d, staged),
                "metadata": metadata,
            },
        )
    intent = _json(d, intent_path)
    if intent.get("schema") != SCHEMA or intent.get("reservation") != reservation:
        raise DeliveryError("self-host successor intent authority changed")
    staged = _safe(Path(intent["staged"]))
    if (
        not staged.is_relative_to(directory / "successor-preparations")
        or staged.name != successor.name
    ):
        raise DeliveryError("self-host successor staging owner differs")
    if not successor.exists():
        if _inventory(d, staged) != intent["inventory"]:
            raise DeliveryError("self-host successor staging changed")
        successor.parent.mkdir(parents=True, exist_ok=True)
        os.rename(staged, successor)
        _sync(successor.parent)
    elif staged.exists():
        raise DeliveryError("self-host duplicate successor and staging")
    if not (directory / "dispatch.json").exists():
        if _inventory(d, successor) != intent["inventory"]:
            raise DeliveryError("self-host successor changed before dispatch")
    else:
        current = _json(d, successor / "run.json")
        for key, value in intent["metadata"].items():
            if current.get(key) != value:
                raise DeliveryError("self-host successor immutable metadata changed")
    for name in (
        "native-plan.json",
        "recovery-context.json",
        "observed-proof-selection.json",
    ):
        path = successor / name
        expected = intent["inventory"][name]
        if (
            _digest(_bytes(d, path, LIMIT)) != expected["sha256"]
            or stat.S_IMODE(path.stat().st_mode) != expected["mode"]
        ):
            raise DeliveryError("self-host successor immutable evidence changed")
    _inherit_admission(
        d, d.RUNTIME_ROOT / "runs" / run.name, proposal["boundary"]["card"], directory
    )
    pointer = d.manifest_path(Path(proposal["boundary"]["card"]).stem)
    if not (directory / "dispatch.json").exists():
        if pointer.exists() and _json(d, pointer).get("run_id") not in (
            run.name,
            successor.name,
        ):
            raise DeliveryError("self-host manifest pointer belongs to another run")
        d.write_json(pointer, _json(d, successor / "manifest.json"))
    for origin, expected in proposal["boundary"]["lineage"].items():
        local = d.RUNTIME_ROOT / "runs" / Path(origin).name
        if _inventory(d, local) != expected:
            raise DeliveryError("self-host local predecessor history drifted")
    return successor


def _reconcile(d: Any, run: Path) -> dict:
    proposal = _proposal(d, run)
    _intact(d, proposal)
    directory = _root(d, run)
    reservation = _reservation(d, run, proposal, create=False)
    result = {"state": "prepared", "proposal": str(directory / "proposal.json")}
    if not (directory / "dispatch.json").exists():
        _corrective_intact(d, run, proposal)
    if reservation is None:
        if _boundary(d, run) != proposal["boundary"]:
            raise DeliveryError("self-host prepared boundary drifted")
        return result
    if (
        not (directory / "dispatch.json").exists()
        and _boundary(d, run) != proposal["boundary"]
    ):
        raise DeliveryError("self-host boundary drifted before dispatch")
    # An origin reservation is durable authorization to finish preparing the
    # exact child; reconciliation never calls the delivery executor.
    successor = _make_successor(d, run, proposal, reservation)
    result.update(state="applied", successor=str(successor))
    if (directory / "dispatch.json").exists():
        dispatch = _json(d, directory / "dispatch.json")
        if dispatch != {"schema": SCHEMA, "reservation": reservation}:
            raise DeliveryError("self-host dispatch authority changed")
        result["state"] = "dispatched"
        metadata = _json(d, successor / "run.json")
        if metadata.get("finished_at"):
            result["exit_code"] = metadata.get("exit_code")
    return result


def reconcile(d: Any, run_dir: Path) -> dict:
    run = _run(run_dir)
    with _locks(d, run):
        return _reconcile(d, run)


def apply(d: Any, run_dir: Path, proposal_path: Path) -> dict:
    run = _run(run_dir)
    with _locks(d, run):
        directory = _root(d, run)
        if _safe(proposal_path) != directory / "proposal.json":
            raise DeliveryError("self-host apply requires the exact retained proposal")
        result = _reconcile(d, run)
        if result["state"] == "dispatched":
            return result
        proposal = _proposal(d, run)
        reservation = _reservation(d, run, proposal, create=True)
        successor = _make_successor(d, run, proposal, reservation)
        _intact(d, proposal)
        if _boundary(d, run) != proposal["boundary"]:
            raise DeliveryError("self-host boundary drifted before dispatch")
        _write(
            directory / "dispatch.json", {"schema": SCHEMA, "reservation": reservation}
        )
        code = d.execute_prepared_delivery(
            card=d.resolve_deliverable_card(proposal["boundary"]["card"]),
            run_dir=successor,
            current_profile=d.profile(),
            recovery_context=successor / "recovery-context.json",
        )
        return {
            "state": "dispatched",
            "proposal": str(directory / "proposal.json"),
            "successor": str(successor),
            "exit_code": code,
        }


def require_not_superseded(d: Any, run_dir: Path) -> None:
    """Guard direct ordinary resume selection, never ancestry/evidence reads."""
    run = _run(run_dir)
    candidates = [d.RUNTIME_ROOT / "self-host-transitions" / (run.name + ".json")]
    local_proposal = _root(d, run) / "proposal.json"
    if local_proposal.exists():
        proposal = _json(d, local_proposal)
        origin = _run(Path(proposal["source_run"]))
        candidates.append(
            _source(origin)
            / ".runtime/changerail/self-host-transitions"
            / (run.name + ".json")
        )
    for path in candidates:
        if path.exists():
            value = _json(d, path)
            if value.get("schema") != SCHEMA or not NAME.fullmatch(
                str(value.get("successor", ""))
            ):
                raise DeliveryError("invalid self-host source reservation")
            raise DeliveryError(
                f"self-host predecessor is superseded; resume {value['successor']} in {value.get('project')}"
            )
