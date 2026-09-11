"""Fail-closed receipts for a pre-group technical model failure.

This module deliberately only authorizes recovery.  Creating the successor and
launching its one pending group is a separate transition, so a receipt can never
silently turn an ambiguous stopped session into a new writer.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError


SCHEMA = "changerail.technical-model-recovery.v1"
LIMIT = 32 * 1024 * 1024
_CAPACITY_MARKER = "selected model is at capacity"


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _root(delivery: Any, run_dir: Path) -> Path:
    root = delivery.RUNTIME_ROOT / "technical-recoveries" / run_dir.name
    if root.resolve(strict=False) != root.absolute():
        raise DeliveryError("technical recovery receipt root must not contain symlinks")
    return root


def _sync(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path: Path, value: dict[str, Any]) -> None:
    """Publish one receipt only after its bytes reached stable storage."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write((json.dumps(value, sort_keys=True, indent=2) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path, follow_symlinks=False)
        _sync(path.parent)
    finally:
        temporary.unlink(missing_ok=True)
        _sync(path.parent)


def _safe_run(delivery: Any, run_dir: Path) -> Path:
    run = run_dir.absolute()
    expected = (delivery.RUNTIME_ROOT / "runs").absolute()
    if run.parent != expected or run.resolve() != run:
        raise DeliveryError(
            "select an exact local retained run directory without symlinks"
        )
    return run


def _successor_path(delivery: Any, name: str) -> Path:
    if not name or any(part in {"", ".", ".."} for part in Path(name).parts):
        raise DeliveryError("technical recovery successor name is unsafe")
    path = (delivery.RUNTIME_ROOT / "runs" / name).absolute()
    if path.parent != (delivery.RUNTIME_ROOT / "runs").absolute():
        raise DeliveryError(
            "technical recovery successor must be an exact run directory"
        )
    return path


def _inventory(delivery: Any, run_dir: Path) -> dict[str, str]:
    """Hash every predecessor file; directory names alone are not authority."""
    result: dict[str, str] = {}
    for path in sorted(run_dir.rglob("*")):
        if path.is_symlink():
            raise DeliveryError("technical recovery predecessor contains a symlink")
        if path.is_file():
            result[path.relative_to(run_dir).as_posix()] = _digest(
                delivery._check_bytes(path, LIMIT)
            )
    return result


def _fallback(delivery: Any, failed_model: str) -> dict[str, str]:
    route = delivery.profile().get("models", {}).get("technical_recovery")
    if not isinstance(route, dict):
        raise DeliveryError("profile lacks models.technical_recovery fallback route")
    model = route.get("model")
    reasoning = route.get("reasoning_effort")
    if (
        not isinstance(model, str)
        or not model
        or not isinstance(reasoning, str)
        or not reasoning
    ):
        raise DeliveryError("technical recovery fallback route is invalid")
    if model == failed_model:
        raise DeliveryError(
            "technical recovery fallback model must differ from failed model"
        )
    # Keep model validation aligned with the executable adapter, without treating
    # implementation/review routing as recovery authority.
    delivery.model_route(
        {"models": {"technical-recovery": route}}, "technical-recovery"
    )
    return {"model": model, "reasoning_effort": reasoning}


def classify_session(delivery: Any, session_dir: Path) -> dict[str, Any]:
    """Classify only a retained, terminal capacity failure from the allowlist."""
    metadata = delivery._check_json(session_dir / "session.json")
    if (
        metadata.get("role") != "implementation"
        or not isinstance(metadata.get("session"), str)
        or not metadata.get("finished_at")
        or type(metadata.get("exit_code")) is not int
        or metadata.get("exit_code") <= 0
        or metadata.get("completed") is not False
        or metadata.get("timed_out") is not False
        or metadata.get("interrupted") is not False
        or metadata.get("budget_violation") is not None
        or metadata.get("stop_reason") != "nonzero_exit"
        or metadata.get("streams_complete") is not True
        or metadata.get("process_group_quiescent") is not True
    ):
        raise DeliveryError(
            "technical recovery requires a proven terminal nonzero model session"
        )
    model = metadata.get("model")
    if not isinstance(model, str) or not model:
        raise DeliveryError("technical recovery session lacks its model identity")
    stderr = session_dir / "stderr.log"
    if not stderr.is_file() or stderr.is_symlink():
        raise DeliveryError(
            "technical recovery session has no retained terminal stderr"
        )
    raw = delivery._check_bytes(stderr, LIMIT)
    if _CAPACITY_MARKER not in raw.decode("utf-8", errors="replace").casefold():
        raise DeliveryError(
            "technical recovery failure is not in the model capacity allowlist"
        )
    # A capacity response is admissible only before the native writer.  Keep
    # the streamed event log as an independent proof; stderr text alone is
    # trivially forgeable and can follow a partially applied change.
    stream = session_dir / "stdout.jsonl"
    events = session_dir / "events.jsonl"
    if (
        not stream.is_file()
        or stream.is_symlink()
        or not events.is_file()
        or events.is_symlink()
    ):
        raise DeliveryError(
            "technical recovery session lacks retained execution streams"
        )
    stdout_events = []
    for line in delivery._check_bytes(stream, LIMIT).splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DeliveryError("technical recovery session stream is invalid") from exc
        stdout_events.append(event)
        if not isinstance(event, dict):
            raise DeliveryError("technical recovery session has an unknown event")
        kind = event.get("type")
        if kind in {"item.completed", "item.started"}:
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") not in {
                "agent_message",
                "reasoning",
            }:
                raise DeliveryError(
                    "technical recovery rejects a session with execution or unknown item"
                )
        elif kind in {"error", "turn.failed"}:
            error = event.get("error", event)
            if (
                not isinstance(error, dict)
                or _CAPACITY_MARKER not in str(error.get("message", "")).casefold()
            ):
                raise DeliveryError(
                    "technical recovery session has an unknown failure event"
                )
        elif kind not in {"thread.started", "turn.started"}:
            raise DeliveryError("technical recovery session has an unknown event")
    event_events = []
    for line in delivery._check_bytes(events, LIMIT).splitlines():
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DeliveryError("technical recovery session stream is invalid") from exc
        event = envelope.get("event", envelope) if isinstance(envelope, dict) else {}
        event_events.append(event)
    if stdout_events != event_events:
        raise DeliveryError("technical recovery session streams disagree")
    return {
        "session": metadata["session"],
        "session_sha256": _digest(
            delivery._check_bytes(session_dir / "session.json", LIMIT)
        ),
        "stderr": session_dir.relative_to(session_dir.parents[1]).as_posix()
        + "/stderr.log",
        "stderr_sha256": _digest(raw),
        "failed_model": model,
        "failure_class": "model_capacity",
    }


def _boundary(delivery: Any, run_dir: Path) -> dict[str, Any]:
    run_dir = _safe_run(delivery, run_dir)
    metadata = delivery.require_current_execution(run_dir)
    # Recovery is a continuation of the exact execution contract.  It must
    # never adopt edited runner code or profile bytes silently.
    delivery.require_frozen_execution(run_dir)
    card_value = metadata.get("card")
    if (
        metadata.get("run_id") != run_dir.name
        or not isinstance(card_value, str)
        or "change_plan" not in metadata
        or "process_identity" not in metadata
    ):
        raise DeliveryError("technical recovery run identity is inconsistent")
    if (
        not metadata.get("finished_at")
        or not isinstance(metadata.get("exit_code"), int)
        or metadata.get("exit_code") == 0
        or metadata.get("completed") is True
    ):
        raise DeliveryError("technical recovery requires a stopped terminal run")
    if metadata.get("recovery_of") is not None:
        raise DeliveryError(
            "technical recovery only accepts the original stopped native run"
        )
    if delivery.staged_paths():
        raise DeliveryError("technical recovery requires an empty index")
    permitted_successor = None
    proposal_path = _root(delivery, run_dir) / "proposal.json"
    if proposal_path.is_file():
        proposal = _proposal(delivery, run_dir, proposal_path)
        intent = _successor_intent(delivery, run_dir, proposal)
        if intent is not None:
            permitted_successor = intent["successor"]
    for candidate in run_dir.parent.iterdir():
        owner_path = candidate / "run.json"
        if candidate == run_dir or not owner_path.is_file():
            continue
        owner = delivery._check_json(owner_path)
        if (
            owner.get("recovery_of") == run_dir.name
            and candidate.name != permitted_successor
        ):
            raise DeliveryError(
                "technical recovery predecessor already has a continuation"
            )
    if not isinstance(card_value, str):
        raise DeliveryError("technical recovery run lacks its card owner")
    card = delivery.resolve_deliverable_card(card_value)
    if card.parent.name != "3.inprogress":
        raise DeliveryError("technical recovery requires the sole in-progress card")
    if delivery.board_activity().get("active") != [card]:
        raise DeliveryError("technical recovery requires one active card")
    from scripts.changerail import openspec_context as native

    native.require_plan(delivery, card, run_dir / "native-plan.json")
    if (run_dir / "reviews").exists() or any(
        (run_dir / name).exists()
        for name in (
            "verification.json",
            "verification",
            "preverification.json",
            "preverification",
            "publication-journal.json",
            "native-sync.json",
            "native-archive-intent.json",
            "native-archive.json",
            "publication.json",
            "implementation-handoff.json",
            "native-finalization.json",
        )
    ):
        raise DeliveryError(
            "technical recovery is unavailable after review, verification, archive or publication intent"
        )
    if delivery._unresolved_verification_attempt(run_dir):
        raise DeliveryError(
            "technical recovery rejects an unresolved verification attempt"
        )
    plan = delivery.declared_change_plan(run_dir)
    if not plan:
        raise DeliveryError("technical recovery requires a retained native change plan")
    events = delivery.combined_change_events(run_dir)
    states = delivery.change_checkpoint_statuses(plan, events)
    if any(row["status"] == "started" for row in states):
        raise DeliveryError(
            "technical recovery rejects a writer-started native task group"
        )
    pending = next((row for row in states if row["status"] == "pending"), None)
    if pending is None:
        raise DeliveryError("technical recovery has no pending native task group")
    number = pending["number"]
    sessions = run_dir / "sessions"
    candidates = []
    if sessions.is_dir() and not sessions.is_symlink():
        for session in sessions.iterdir():
            if (
                session.is_dir()
                and not session.is_symlink()
                and (session / "session.json").is_file()
            ):
                value = delivery._check_json(session / "session.json")
                if not value.get("finished_at") or value.get("exit_code") is None:
                    raise DeliveryError(
                        "technical recovery requires a proven terminal session"
                    )
                if value.get("native_change_number") == number:
                    candidates.append(session)
            elif session.is_dir():
                raise DeliveryError("technical recovery rejects an unknown session")
    if len(candidates) != 1:
        raise DeliveryError(
            "technical recovery requires one retained failed session for the pending group"
        )
    failure = classify_session(delivery, candidates[0])
    manifest = delivery._check_json(run_dir / "manifest.json")
    paths = manifest.get("paths")
    fingerprint = manifest.get("fingerprint")
    if (
        manifest.get("run_id") != run_dir.name
        or manifest.get("schema") != "changerail.delivery-manifest.v1"
        or manifest.get("baseline_head")
        != delivery.git("rev-parse", "HEAD").stdout.strip()
        or not isinstance(paths, list)
        or not all(isinstance(path, str) for path in paths)
        or fingerprint != delivery.payload_fingerprint(paths)
        or sorted(paths) != delivery.changed_paths()
    ):
        raise DeliveryError(
            "technical recovery payload differs from the retained manifest"
        )
    return {
        "run_dir": run_dir,
        "card": card,
        "metadata": metadata,
        "manifest": manifest,
        "next_group": number,
        "failure": failure,
        "fallback": _fallback(delivery, failure["failed_model"]),
        "inventory": _inventory(delivery, run_dir),
        "payload": fingerprint,
    }


def _proposal(delivery: Any, run_dir: Path, path: Path) -> dict[str, Any]:
    root = _root(delivery, run_dir)
    if (
        path.absolute().parent != root
        or path.name != "proposal.json"
        or path.is_symlink()
    ):
        raise DeliveryError(
            "technical recovery proposal must be the retained exact proposal"
        )
    value = delivery._check_json(path)
    if value.get("schema") != SCHEMA or value.get("predecessor") != run_dir.name:
        raise DeliveryError("technical recovery proposal owner differs")
    return value


def _successor_intent(
    delivery: Any, run_dir: Path, proposal: dict[str, Any]
) -> dict[str, Any] | None:
    path = _root(delivery, run_dir) / "successor-intent.json"
    if not path.exists():
        return None
    if path.is_symlink():
        raise DeliveryError("technical recovery successor intent is linked")
    value = delivery._check_json(path)
    expected = {
        "schema": SCHEMA,
        "predecessor": run_dir.name,
        "proposal_sha256": _digest(
            delivery._check_bytes(_root(delivery, run_dir) / "proposal.json", LIMIT)
        ),
        "fallback": proposal["fallback"],
    }
    if {key: value.get(key) for key in expected} != expected:
        raise DeliveryError("technical recovery successor intent differs from proposal")
    if (
        not isinstance(value.get("successor"), str)
        or not isinstance(value.get("staged"), str)
        or not isinstance(value.get("inventory"), dict)
        or not isinstance(value.get("run_identity"), dict)
    ):
        raise DeliveryError("technical recovery successor intent is malformed")
    _successor_path(delivery, value["successor"])
    staged = (_root(delivery, run_dir) / value["staged"]).absolute()
    if (
        not staged.is_relative_to(_root(delivery, run_dir) / "successor-preparations")
        or staged.resolve(strict=False) != staged
    ):
        raise DeliveryError("technical recovery successor staging path is unsafe")
    return value


def _successor_inventory(delivery: Any, directory: Path) -> dict[str, str]:
    if directory.is_symlink():
        raise DeliveryError("technical recovery successor is linked")
    return _inventory(delivery, directory)


def _retains_successor_base(
    delivery: Any, successor: Path, expected: dict[str, str]
) -> bool:
    """Allow a dispatched group to append receipts without changing its base."""
    observed = _successor_inventory(delivery, successor)
    # The normal lifecycle owns run/manifest terminal updates.  All other
    # bootstrap receipts are immutable authority and must remain byte exact.
    mutable = {"run.json", "manifest.json"}
    return all(
        path in observed and (path in mutable or observed[path] == digest)
        for path, digest in expected.items()
    )


def _publish_successor(
    delivery: Any, run_dir: Path, proposal: dict[str, Any], intent: dict[str, Any]
) -> Path:
    successor = _successor_path(delivery, intent["successor"])
    root = _root(delivery, run_dir)
    staged = (root / intent["staged"]).absolute()
    if successor.exists():
        # A retry after dispatch necessarily sees new session/event/evidence
        # receipts.  The atomically published base remains immutable authority;
        # later records are validated by the assigned-group launch guard.
        if staged.exists() or not _retains_successor_base(
            delivery, successor, intent["inventory"]
        ):
            raise DeliveryError(
                "technical recovery successor already started or changed"
            )
    else:
        if (
            not staged.is_dir()
            or _successor_inventory(delivery, staged) != intent["inventory"]
        ):
            raise DeliveryError("technical recovery successor staging changed")
        # The predecessor is authority until the atomic rename itself.
        if proposal != _value(delivery, _boundary(delivery, run_dir)):
            raise DeliveryError(
                "technical recovery predecessor changed before publication"
            )
        successor.parent.mkdir(parents=True, exist_ok=True)
        os.rename(staged, successor)
        _sync(successor.parent)
        _sync(staged.parent)
    metadata = delivery._check_json(successor / "run.json")
    if any(metadata.get(key) != value for key, value in intent["run_identity"].items()):
        raise DeliveryError("technical recovery successor immutable metadata changed")
    manifest = delivery._check_json(successor / "manifest.json")
    if (
        manifest.get("run_id") != successor.name
        or manifest.get("schema") != "changerail.delivery-manifest.v1"
        or manifest.get("baseline_head") != metadata.get("baseline_head")
    ):
        raise DeliveryError("technical recovery successor manifest owner changed")
    if (
        metadata.get("run_id") != successor.name
        or metadata.get("recovery_of") != run_dir.name
        or metadata.get("technical_recovery", {}).get("proposal_sha256")
        != intent["proposal_sha256"]
    ):
        raise DeliveryError(
            "technical recovery successor identity differs from receipt"
        )
    # The card-level manifest is the runner's active owner pointer.  Transfer
    # it only after the successor directory is durably published; predecessor
    # run bytes remain untouched and its receipt is the audit record.
    card = delivery.resolve_deliverable_card(proposal["card"])
    pointer = delivery.manifest_path(delivery.card_id(card))
    current_owner = (
        delivery._check_json(pointer).get("run_id") if pointer.exists() else None
    )
    if current_owner in {None, run_dir.name}:
        delivery.write_json(pointer, delivery._check_json(successor / "manifest.json"))
    elif current_owner != successor.name:
        # An ordinary continuation may already own the card. Reconciliation
        # never rewinds that pointer or creates another writer.
        if not (successor / "technical-recovery-dispatch.json").is_file():
            raise DeliveryError("technical recovery card manifest has another owner")
    return successor


def _create_successor_locked(
    delivery: Any, run_dir: Path, proposal: dict[str, Any]
) -> Path:
    """Create one fully initialized run off-line, then publish it atomically."""
    root = _root(delivery, run_dir)
    intent = _successor_intent(delivery, run_dir, proposal)
    if intent is not None:
        return _publish_successor(delivery, run_dir, proposal, intent)
    if (root / "consumed.json").exists():
        raise DeliveryError(
            "technical recovery receipt was consumed without its successor intent"
        )
    card = delivery.resolve_deliverable_card(proposal["card"])
    run_id = (
        f"{delivery.utc_now().replace('-', '').replace(':', '')}-"
        f"{card.stem}-{uuid.uuid4().hex[:8]}"
    )
    successor = _successor_path(delivery, run_id)
    staged = root / "successor-preparations" / uuid.uuid4().hex / run_id
    staged.mkdir(parents=True)
    selection = {
        "schema": "changerail.observed-proof-selection.v1",
        "root": delivery.repo_relative(staged),
        "owner": {"run_id": run_id, "card": proposal["card"]},
        "required_stages": ["implementation", "review", "final"],
    }
    selection_bytes = (json.dumps(selection, sort_keys=True, indent=2) + "\n").encode()
    selection_reference = {
        "path": delivery.repo_relative(staged / "observed-proof-selection.json"),
        "sha256": _digest(selection_bytes).removeprefix("sha256:"),
    }
    predecessor_manifest = delivery._check_json(run_dir / "manifest.json")
    if predecessor_manifest.get("fingerprint") != proposal["payload"]:
        raise DeliveryError(
            "technical recovery predecessor manifest differs from proposal"
        )
    metadata = {
        "schema": "changerail.delivery-run.v2",
        "run_id": run_id,
        "card": proposal["card"],
        "started_at": delivery.utc_now(),
        "baseline_head": predecessor_manifest.get("baseline_head"),
        "profile": delivery.repo_relative(delivery.PROFILE_PATH),
        "mode": "delivery",
        "lifecycle_mode": "openspec-v1",
        "change_plan": delivery._check_json(run_dir / "run.json").get("change_plan"),
        "execution_contract": "changerail.native.v1",
        "process_identity": delivery.execution_identity(),
        "observed_proof_contract": {
            "schema": delivery._OBSERVED_PROOF_CONTRACT,
            "required_stages": ["implementation", "review", "final"],
            "selection": selection_reference,
        },
        "recovery_of": run_dir.name,
        "technical_recovery": {
            "schema": SCHEMA,
            "proposal_sha256": _digest(
                delivery._check_bytes(root / "proposal.json", LIMIT)
            ),
            "next_group": proposal["next_group"],
            "fallback": proposal["fallback"],
        },
    }
    delivery.write_json(staged / "run.json", metadata)
    (staged / "observed-proof-selection.json").write_bytes(selection_bytes)
    # This existing context format is also the review-budget inheritance contract.
    context_path = delivery.build_recovery_context(
        run_dir=staged,
        previous_run=run_dir,
        objective="Continue only the recovered native task group with its fixed fallback model.",
    )
    context = delivery._check_json(context_path)
    context["technical_recovery"] = metadata["technical_recovery"]
    final_selection = {**selection, "root": delivery.repo_relative(successor)}
    final_selection_bytes = (
        json.dumps(final_selection, sort_keys=True, indent=2) + "\n"
    ).encode()
    final_selection_reference = {
        "path": delivery.repo_relative(successor / "observed-proof-selection.json"),
        "sha256": _digest(final_selection_bytes).removeprefix("sha256:"),
    }
    context["observed_proof_selection"] = final_selection_reference
    metadata.update(
        recovery_session_strategy="fresh_fallback_model",
        inherited_change_events=context["inherited_change_events"],
    )
    metadata["observed_proof_contract"]["selection"] = final_selection_reference
    manifest = {
        **predecessor_manifest,
        "run_id": run_id,
        "created_at": delivery.utc_now(),
        "observed_proof_selection": final_selection_reference,
    }
    delivery.write_json(staged / "run.json", metadata)
    delivery.write_json(staged / "recovery-context.json", context)
    (staged / "observed-proof-selection.json").write_bytes(final_selection_bytes)
    delivery.write_json(staged / "manifest.json", manifest)
    plan_bytes = delivery._check_bytes(run_dir / "native-plan.json", LIMIT)
    (staged / "native-plan.json").write_bytes(plan_bytes)
    for path in staged.iterdir():
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    _sync(staged)
    _sync(staged.parent)
    intent = {
        "schema": SCHEMA,
        "predecessor": run_dir.name,
        "proposal_sha256": _digest(
            delivery._check_bytes(root / "proposal.json", LIMIT)
        ),
        "fallback": proposal["fallback"],
        "successor": run_id,
        "staged": staged.relative_to(root).as_posix(),
        "inventory": _successor_inventory(delivery, staged),
        "run_identity": delivery._check_json(staged / "run.json"),
    }
    _write(root / "successor-intent.json", intent)
    return _publish_successor(delivery, run_dir, proposal, intent)


def _launch_successor_group(
    delivery: Any, run_dir: Path, proposal: dict[str, Any], successor: Path
) -> int:
    dispatch_path = successor / "technical-recovery-dispatch.json"
    if dispatch_path.exists():
        # A previous attempt owns the writer, even if its helper stopped
        # before opening a session. Never replay an ambiguous dispatch.
        dispatch = delivery._check_json(dispatch_path)
        if (
            dispatch.get("schema") != SCHEMA
            or dispatch.get("predecessor") != run_dir.name
            or dispatch.get("successor") != successor.name
            or dispatch.get("next_group") != proposal["next_group"]
            or dispatch.get("proposal_sha256")
            != _digest(
                delivery._check_bytes(_root(delivery, run_dir) / "proposal.json", LIMIT)
            )
        ):
            raise DeliveryError("technical recovery dispatch receipt differs")
        result = delivery._check_json(successor / "run.json")
        code = result.get("exit_code")
        return code if result.get("finished_at") and type(code) is int else 2
    states = delivery.change_checkpoint_statuses(
        delivery.declared_change_plan(successor) or [],
        delivery.combined_change_events(successor),
    )
    state = next(
        (row for row in states if row["number"] == proposal["next_group"]), None
    )
    if state is None:
        raise DeliveryError("technical recovery successor lacks its assigned group")
    if state["status"] == "complete":
        return 0
    if state["status"] != "pending":
        raise DeliveryError("technical recovery successor group was already started")
    sessions = successor / "sessions"
    if sessions.exists() and any(
        (path / "session.json").is_file()
        and delivery._check_json(path / "session.json").get("native_change_number")
        == proposal["next_group"]
        for path in sessions.iterdir()
        if path.is_dir() and not path.is_symlink()
    ):
        raise DeliveryError("technical recovery successor already dispatched its group")
    profile = delivery.profile()
    if _fallback(delivery, proposal["failure"]["failed_model"]) != proposal["fallback"]:
        raise DeliveryError("technical recovery fallback route drifted after receipt")
    profile = {
        **profile,
        "models": {
            **profile.get("models", {}),
            "technical-recovery": proposal["fallback"],
        },
    }
    from scripts.changerail.native_workflow import launch_groups

    card = delivery.resolve_deliverable_card(proposal["card"])
    context = successor / "recovery-context.json"
    proposal_sha = _digest(
        delivery._check_bytes(_root(delivery, run_dir) / "proposal.json", LIMIT)
    )

    _write(
        dispatch_path,
        {
            "schema": SCHEMA,
            "predecessor": run_dir.name,
            "successor": successor.name,
            "next_group": proposal["next_group"],
            "proposal_sha256": proposal_sha,
            "reserved_at": delivery.utc_now(),
        },
    )

    def launch_fallback_group() -> None:
        launch_groups(
            delivery,
            card=card,
            run_dir=successor,
            current_profile=profile,
            recovery_context=context,
            only_group=proposal["next_group"],
            model_route_name="technical-recovery",
        )

    # Let the ordinary runner own the CHRL_RUN_DIR environment, terminal
    # metadata and subsequent groups/review/final stages.  The fallback group
    # is the only special operation injected into that lifecycle.
    return delivery.execute_prepared_delivery(
        card=card,
        run_dir=successor,
        current_profile=profile,
        recovery_context=context,
        before_orchestrate=launch_fallback_group,
    )


def prepare(delivery: Any, run_dir: Path) -> dict[str, Any]:
    if os.environ.get("CHRL_SESSION_ROLE"):
        raise DeliveryError(
            "technical recovery preparation requires an operator outside delivery"
        )
    with delivery.delivery_lock():
        run_dir = _safe_run(delivery, run_dir)
        root = _root(delivery, run_dir)
        proposal_path = root / "proposal.json"
        if proposal_path.exists():
            proposal = _proposal(delivery, run_dir, proposal_path)
            current = _boundary(delivery, run_dir)
            if proposal != _value(delivery, current):
                raise DeliveryError(
                    "technical recovery proposal no longer matches predecessor state"
                )
            return {"proposal": str(proposal_path), "state": "prepared"}
        current = _boundary(delivery, run_dir)
        root.mkdir(parents=True, exist_ok=True)
        _write(proposal_path, _value(delivery, current))
        return {"proposal": str(proposal_path), "state": "prepared"}


def _value(delivery: Any, current: dict[str, Any]) -> dict[str, Any]:
    run_dir = current["run_dir"]
    return {
        "schema": SCHEMA,
        "predecessor": run_dir.name,
        "run_sha256": _digest(delivery._check_bytes(run_dir / "run.json", LIMIT)),
        "card": delivery.repo_relative(current["card"]),
        "next_group": current["next_group"],
        "failure": current["failure"],
        "fallback": current["fallback"],
        "payload": current["payload"],
        "predecessor_inventory": current["inventory"],
    }


def _predecessor_intact(delivery: Any, run_dir: Path, proposal: dict[str, Any]) -> None:
    """After dispatch, only the predecessor bytes remain authoritative."""
    observed = _inventory(delivery, run_dir)
    if observed != proposal.get("predecessor_inventory"):
        raise DeliveryError("technical recovery predecessor was changed")
    manifest = delivery._check_json(run_dir / "manifest.json")
    if manifest.get("fingerprint") != proposal.get("payload"):
        raise DeliveryError("technical recovery predecessor manifest was changed")


def _reconcile_locked(delivery: Any, run_dir: Path) -> dict[str, Any]:
    run_dir = _safe_run(delivery, run_dir)
    root = _root(delivery, run_dir)
    proposal_path = root / "proposal.json"
    if not proposal_path.is_file():
        raise DeliveryError("technical recovery proposal is absent")
    proposal = _proposal(delivery, run_dir, proposal_path)
    intent = _successor_intent(delivery, run_dir, proposal)
    if intent is None:
        if proposal != _value(delivery, _boundary(delivery, run_dir)):
            raise DeliveryError(
                "technical recovery predecessor, payload or fallback drifted"
            )
    else:
        _predecessor_intact(delivery, run_dir, proposal)
        successor = _successor_path(delivery, intent["successor"])
        if not (successor / "technical-recovery-dispatch.json").exists():
            if proposal != _value(delivery, _boundary(delivery, run_dir)):
                raise DeliveryError("technical recovery drifted before dispatch")
    applied_path = root / "applied.json"
    if not applied_path.exists():
        return {"proposal": str(proposal_path), "state": "prepared"}
    applied = delivery._check_json(applied_path)
    expected = {
        "schema": SCHEMA,
        "predecessor": run_dir.name,
        "proposal_sha256": _digest(delivery._check_bytes(proposal_path, LIMIT)),
        "fallback": proposal["fallback"],
    }
    if {key: applied.get(key) for key in expected} != expected:
        raise DeliveryError("technical recovery applied receipt differs from proposal")
    return {
        "proposal": str(proposal_path),
        "receipt": str(applied_path),
        "state": "applied",
    }


def reconcile(delivery: Any, run_dir: Path) -> dict[str, Any]:
    """Revalidate an existing proposal/applied receipt without creating a writer."""
    with delivery.delivery_lock():
        run_dir = _safe_run(delivery, run_dir)
        result = _reconcile_locked(delivery, run_dir)
        if result["state"] != "applied":
            return result
        proposal = _proposal(
            delivery, run_dir, _root(delivery, run_dir) / "proposal.json"
        )
        intent = _successor_intent(delivery, run_dir, proposal)
        if intent is None:
            return result
        successor = _publish_successor(delivery, run_dir, proposal, intent)
        return {**result, "successor": str(successor)}


def apply(delivery: Any, run_dir: Path, proposal_path: Path) -> dict[str, Any]:
    if os.environ.get("CHRL_SESSION_ROLE"):
        raise DeliveryError(
            "technical recovery apply requires an operator outside delivery"
        )
    with delivery.delivery_lock():
        run_dir = _safe_run(delivery, run_dir)
        root = _root(delivery, run_dir)
        retained = root / "proposal.json"
        if proposal_path.absolute() != retained.absolute():
            raise DeliveryError(
                "technical recovery apply requires its exact retained proposal"
            )
        result = _reconcile_locked(delivery, run_dir)
        proposal = _proposal(delivery, run_dir, retained)
        if result["state"] != "applied":
            receipt = {
                "schema": SCHEMA,
                "predecessor": run_dir.name,
                "proposal_sha256": _digest(delivery._check_bytes(retained, LIMIT)),
                "fallback": proposal["fallback"],
                "applied_at": delivery.utc_now(),
            }
            path = root / "applied.json"
            _write(path, receipt)
            result = {
                "proposal": str(retained),
                "receipt": str(path),
                "state": "applied",
            }
        successor = _create_successor_locked(delivery, run_dir, proposal)
        exit_code = _launch_successor_group(delivery, run_dir, proposal, successor)
        return {
            **result,
            "successor": str(successor),
            "state": "dispatched",
            "exit_code": exit_code,
        }
