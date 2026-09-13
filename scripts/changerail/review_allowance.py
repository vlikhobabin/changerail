"""Two autonomous reviews, then one immutable operator decision per extra slot.

This is a cooperative same-UID protocol, not OS authentication. Authorization
changes only review allowance; ordinary recovery still owns execution rights.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from scripts.changerail import plan_restoration as retained
from scripts.changerail.contracts import DeliveryError, ReviewExhausted

SCHEMA = "changerail.review-authorization.v1"
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
HASH = re.compile(r"[0-9a-f]{64}")
FIELDS = {
    "schema", "project", "root_run", "predecessor", "lineage", "history",
    "accepted_plan", "plan", "execution", "proof_contract", "starting",
    "previous_review", "scope", "spent_before", "grants_before",
    "additional_reviews", "review_number", "previous_authorization", "reason",
    "operation", "successor_run_id", "proposal_sha256", "observed_at",
}


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def _operator() -> None:
    # CHRL_ENGINE_USE_FD is the ordinary release launcher's shared-use lease,
    # not worker authority. The launcher/runtime validate that descriptor.
    if any(value and (key in {"CHRL_RUN_DIR", "CHRL_SESSION_ROLE", "CHRL_SESSION_NAME",
                             "CHRL_REPAIR_CONTEXT", "CHRL_REVIEW_CONTEXT"}
                      or key.startswith(("CHRL_NATIVE_", "CHRL_RECOVERY_")))
           for key, value in os.environ.items()):
        raise DeliveryError("review allowance requires a separate operator outside worker context")


def _safe(d: Any, path: Path) -> Path:
    path = path.absolute()
    if path.resolve() != path or not path.is_relative_to(d.REPO_ROOT):
        raise DeliveryError("review authorization path must be local without symlinks")
    return path


def _run(d: Any, path: Path) -> Path:
    path = _safe(d, path)
    if path.parent != d.RUNTIME_ROOT / "runs" or not NAME.fullmatch(path.name):
        raise DeliveryError("review allowance requires an exact retained run directory")
    return path


def _json(d: Any, path: Path) -> dict:
    try:
        return d._check_json_bytes(d._check_bytes(_safe(d, path), retained.LIMIT))
    except (OSError, ValueError, TypeError) as exc:
        raise DeliveryError(f"invalid review authorization history: {exc}") from exc


def _reference(d: Any, path: Path) -> dict:
    return {"path": d.repo_relative(path),
            "sha256": hashlib.sha256(d._check_bytes(_safe(d, path), retained.LIMIT)).hexdigest()}


def _lineage(d: Any, run: Path) -> list[Path]:
    paths = [_run(d, run), *d.recovery_ancestors(run)]
    owner = _json(d, run / "run.json").get("card")
    for path in paths:
        _run(d, path)
        metadata = _json(d, path / "run.json")
        if metadata.get("run_id") != path.name or metadata.get("card") != owner:
            raise DeliveryError("foreign review allowance lineage owner")
    return paths


def _project(d: Any) -> dict:
    common = d.git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return {"root": str(d.REPO_ROOT.resolve()), "git_common_dir": str(Path(common).resolve())}


def _technical_history(d: Any, lineage: list[Path]) -> dict:
    """Retain completed technical transitions; never reconcile by dispatching."""
    try:
        return _read_technical_history(d, lineage)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise DeliveryError(f"invalid technical recovery authority: {exc}") from exc


def _read_technical_history(d: Any, lineage: list[Path]) -> dict:
    from scripts.changerail import technical_recovery as technical

    history = {}
    for index, origin in enumerate(lineage):
        root = _safe(d, d.RUNTIME_ROOT / "technical-recoveries" / origin.name)
        if not root.exists():
            continue
        if index == 0:
            raise DeliveryError("conflicting recovery intent blocks review authorization")
        child = lineage[index - 1]
        proposal = _json(d, root / "proposal.json")
        intent = technical._successor_intent(d, origin, proposal)
        if (intent is None or intent["successor"] != child.name
                or not (child / "technical-recovery-dispatch.json").exists()
                or technical._reconcile_locked(d, origin)["state"] != "applied"
                or not technical._retains_successor_base(d, child, intent["inventory"])):
            raise DeliveryError("unresolved or foreign technical recovery blocks review authorization")
        metadata = _json(d, child / "run.json")
        dispatch = _json(d, child / "technical-recovery-dispatch.json")
        expected = {"schema": technical.SCHEMA, "predecessor": origin.name,
                    "successor": child.name, "next_group": proposal["next_group"],
                    "proposal_sha256": intent["proposal_sha256"]}
        if (any(metadata.get(key) != value for key, value in intent["run_identity"].items())
                or any(dispatch.get(key) != value for key, value in expected.items())
                or metadata.get("recovery_of") != origin.name
                or metadata.get("technical_recovery", {}).get("proposal_sha256") != intent["proposal_sha256"]):
            raise DeliveryError("technical recovery successor authority changed")
        history[f"technical-recoveries/{origin.name}"] = retained._inventory(d, root)
    return history


def _basis(d: Any, run: Path) -> dict:
    lineage = _lineage(d, run)
    metadata = _json(d, run / "run.json")
    manifest = _json(d, run / "manifest.json")
    plan_path = run / "native-plan.json"
    plan = _json(d, plan_path)
    admission = d.RUNTIME_ROOT / "native-plans" / Path(metadata["card"]).stem / "native-plan.json"
    if _json(d, admission) != plan:
        raise DeliveryError("review authorization accepted plan differs from admission")
    previous = None
    for origin in lineage:
        reviews = d._completed_review_verdicts(origin / "reviews")
        if reviews:
            verdict = reviews[-1]
            review_manifest = verdict.with_name(verdict.stem + "-manifest.json")
            value = _json(d, verdict)
            if value.get("workspace") != _json(d, review_manifest).get("fingerprint"):
                raise DeliveryError("review authorization verdict manifest mismatch")
            previous = {"verdict": _reference(d, verdict),
                        "manifest": _reference(d, review_manifest),
                        "context": _reference(d, verdict.with_name(verdict.stem + "-context.json")),
                        "result": value.get("result"), "findings": value.get("findings", [])}
            break
    paths = manifest.get("paths")
    if (not isinstance(paths, list) or not all(isinstance(p, str) for p in paths)
            or paths != sorted(set(paths))
            or manifest.get("run_id") != run.name
            or manifest.get("card") != {"id": Path(metadata["card"]).stem, "path": metadata["card"]}):
        raise DeliveryError("review authorization starting manifest is invalid")
    for path in paths:
        d._safe_path(path)
    return {
        "project": _project(d), "root_run": lineage[-1].name,
        "predecessor": run.name, "lineage": [p.name for p in lineage],
        "history": {**{p.name: retained._inventory(d, p) for p in lineage},
                    **_technical_history(d, lineage)},
        "accepted_plan": _reference(d, admission), "plan": _reference(d, plan_path),
        "execution": metadata.get("process_identity"),
        "proof_contract": metadata.get("observed_proof_contract"),
        "starting": {"fingerprint": manifest.get("fingerprint"), "paths": paths, "index": [],
                     "path_fingerprints": manifest.get("path_fingerprints")},
        "previous_review": previous, "scope": {"card": metadata["card"], "groups": plan.get("groups"),
                                                "change_id": plan.get("change_id")},
        "spent_before": d.review_budget_usage(run)["semantic_cycles"],
    }


def _proposal_digest(record: dict) -> str:
    return _hash({k: v for k, v in record.items() if k not in {"proposal_sha256", "observed_at"}})


def _successor(record: dict) -> str:
    return "review-allow-" + _hash({k: record[k] for k in
                                  ("project", "root_run", "predecessor", "grants_before", "starting")})[:32]


def _records(d: Any, run: Path) -> list[tuple[Path, dict]]:
    try:
        return _read_records(d, run)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise DeliveryError(f"invalid review authorization: {exc}") from exc


def _read_records(d: Any, run: Path) -> list[tuple[Path, dict]]:
    lineage = _lineage(d, run)
    directory = _safe(d, d.RUNTIME_ROOT / "review-authorizations" / lineage[-1].name)
    if not directory.exists():
        return []
    found = []
    previous = None
    # Padded ordinals remain ordered after 9999; there is no lifetime ceiling.
    for path in sorted(directory.iterdir(), key=lambda p: (len(p.name), p.name)):
        # A pre-publication temporary is never an authorization.
        if re.fullmatch(r"\.\d{4,}\.json\.pending-[0-9a-f]{32}", path.name):
            _safe(d, path)
            continue
        number = len(found) + 1
        if path.name != f"{number:04d}.json":
            raise DeliveryError("review authorization sequence is corrupt")
        record = _json(d, path)
        if set(record) != FIELDS or record.get("schema") != SCHEMA:
            raise DeliveryError("review authorization has unknown or missing fields")
        for key in ("spent_before", "grants_before", "additional_reviews", "review_number"):
            if type(record[key]) is not int or record[key] < 0:
                raise DeliveryError("review authorization counters must be nonnegative integers")
        if (record["grants_before"] != number - 1 or record["additional_reviews"] != 1
                or record["spent_before"] != 2 + number - 1
                or record["review_number"] != record["spent_before"] + 1
                or record["previous_authorization"] != previous
                or record["operation"] != "repair-and-one-review"
                or not isinstance(record["reason"], str) or not 1 <= len(record["reason"].strip()) <= 1000
                or len(record["reason"]) > 1000
                or not isinstance(record["observed_at"], str)
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", record["observed_at"])
                or not isinstance(record["predecessor"], str) or not NAME.fullmatch(record["predecessor"])):
            raise DeliveryError("review authorization sequence or operation is invalid")
        origin = _run(d, d.RUNTIME_ROOT / "runs" / record["predecessor"])
        basis = _basis(d, origin)
        states = record["starting"].get("path_states") if isinstance(record["starting"], dict) else None
        if not isinstance(states, dict) or set(states) != set(basis["starting"]["paths"]):
            raise DeliveryError("review authorization starting path states are invalid")
        for name, state in states.items():
            if (not isinstance(state, dict) or set(state) != {"kind", "mode", "digest"}
                    or state["kind"] not in {"file", "deleted"} or type(state["mode"]) is not int
                    or not 0 <= state["mode"] <= 0o7777
                    or (state["kind"] == "deleted" and state["mode"] != 0)
                    or state["digest"] != basis["starting"]["path_fingerprints"].get(name)):
                raise DeliveryError("review authorization starting path state is corrupt")
        basis["starting"]["path_states"] = states
        if any(_hash(record[k]) != _hash(v) for k, v in basis.items()):
            raise DeliveryError("review authorization immutable history or project changed")
        if (record["root_run"] != lineage[-1].name
                or record["successor_run_id"] != _successor(record)
                or record["proposal_sha256"] != _proposal_digest(record)):
            raise DeliveryError("review authorization digest or successor is invalid")
        # Every later grant must descend from the previous decision's sole child.
        if found and found[-1][1]["successor_run_id"] not in record["lineage"]:
            raise DeliveryError("review authorization forks or replays a lineage")
        previous = _reference(d, path)["sha256"]
        found.append((path, record))
    return found


def _reference_for(d: Any, path: Path, record: dict) -> dict:
    return {**_reference(d, path), "review_number": record["review_number"]}


def _quiescent(d: Any) -> None:
    from scripts.changerail.engine_snapshot import _no_live_delivery, EngineSnapshotError

    try:
        _no_live_delivery(d.REPO_ROOT)
    except EngineSnapshotError as exc:
        raise DeliveryError(str(exc)) from exc


def allowance(d: Any, run: Path) -> dict:
    """Read history/context authority; never recheck pre-claim working bytes."""
    spent = d.review_budget_usage(run)["semantic_cycles"]
    # Historical unit/read-only inputs with no current owner retain default two.
    if not (run / "run.json").exists():
        if spent > 2:
            raise DeliveryError("review allowance has negative remaining accounting")
        return {"autonomous_allowance": 2, "operator_granted_slots": 0,
                "spent_reviews": spent, "remaining": 2 - spent, "in_flight": False,
                "authorizations": []}
    paths = _lineage(d, run)
    names = {p.name for p in paths}
    references = []
    claims = {}
    for path, record in _records(d, run):
        successor = record["successor_run_id"]
        if successor not in names and record["predecessor"] != run.name:
            continue
        reference = _reference_for(d, path, record)
        if successor in names:
            child = d.RUNTIME_ROOT / "runs" / successor
            context = _json(d, child / "recovery-context.json")
            metadata = _json(d, child / "run.json")
            if (_hash(context.get("review_authorization")) != _hash(reference)
                    or context.get("run_id") != successor
                    or context.get("recovery_of") != record["predecessor"]
                    or metadata.get("recovery_of") != record["predecessor"]
                    or context.get("current_fingerprint") != record["starting"]["fingerprint"]
                    or metadata.get("process_identity") != record["execution"]
                    or metadata.get("card") != record["scope"]["card"]):
                raise DeliveryError("review authorization claim context is foreign or changed")
            claims[successor] = reference
        references.append(reference)
    for origin in paths:
        context = origin / "recovery-context.json"
        if context.exists() and "review_authorization" in _json(d, context):
            if _hash(_json(d, context)["review_authorization"]) != _hash(claims.get(origin.name)):
                raise DeliveryError("review authorization claim has no matching immutable record")
    remaining = 2 + len(references) - spent
    if remaining < 0:
        raise DeliveryError("review allowance has negative remaining accounting")
    context = run / "reviews" / f"cycle-{len(d._completed_review_verdicts(run / 'reviews')) + 1:02d}-context.json"
    pending = run / "native-review-continuation.json"
    in_flight = context.exists() or (pending.exists() and _json(d, pending).get("complete") is not True)
    return {"autonomous_allowance": 2, "operator_granted_slots": len(references),
            "spent_reviews": spent, "remaining": remaining, "in_flight": in_flight,
            "authorizations": references}


def _leaf(d: Any, run: Path) -> None:
    ancestors = set(_lineage(d, run))
    owner = _json(d, run / "run.json")["card"]
    for candidate in (d.RUNTIME_ROOT / "runs").iterdir():
        _safe(d, candidate)
        if not candidate.is_dir() or not (candidate / "run.json").exists():
            continue
        metadata = _json(d, candidate / "run.json")
        if metadata.get("recovery_of") == run.name:
            raise DeliveryError("review authorization requires the current terminal leaf; use its successor")
        if metadata.get("card") == owner and candidate not in ancestors:
            raise DeliveryError("another run owns this card outside the selected review lineage")


def _eligible(d: Any, run: Path) -> None:
    metadata = d.require_frozen_execution(run)
    d._run_observed_contract(run)
    if (not metadata.get("finished_at") or type(metadata.get("exit_code")) is not int
            or metadata["exit_code"] in (0, 130, -2)
            or metadata.get("stop_reason") == "operator_interrupt"):
        raise DeliveryError("review authorization requires a terminal failed run, not operator stop")
    _leaf(d, run)
    for origin in _lineage(d, run):
        d.require_unreserved_run(origin)
        for directory in ("plan-restorations", "self-host-recoveries", "runtime-repairs"):
            if (d.RUNTIME_ROOT / directory / origin.name).exists():
                raise DeliveryError("conflicting recovery intent blocks review authorization")
        owner = _json(d, origin / "run.json")
        if owner.get("stop_reason") == "operator_interrupt" or owner.get("exit_code") in (130, -2):
            raise DeliveryError("operator-stopped lineage cannot receive review allowance")
        if (not owner.get("finished_at") or type(owner.get("exit_code")) is not int
                or owner["exit_code"] == 0):
            raise DeliveryError("review authorization ancestor is not terminal failed history")
        if d._unresolved_verification_attempt(origin):
            raise DeliveryError("unresolved verification blocks review authorization")
        continuation = origin / "native-review-continuation.json"
        if continuation.exists() and _json(d, continuation).get("complete") is not True:
            raise DeliveryError("pending native review blocks review authorization")
        for session in (origin / "sessions").glob("*"):
            value = _json(d, session / "session.json")
            if not value.get("finished_at") or value.get("stop_reason") == "operator_interrupt":
                raise DeliveryError("unfinished or operator-stopped session blocks review authorization")
            if value.get("role") == "review" and value.get("completed") is not True:
                raise DeliveryError("unresolved review session blocks review authorization")
        for context in (origin / "reviews").glob("cycle-*-context.json"):
            if re.fullmatch(r"cycle-\d+-context.json", context.name):
                verdict = context.with_name(context.name.replace("-context", ""))
                if not verdict.exists():
                    raise DeliveryError("unresolved review allocation blocks review authorization")
    if any((run / name).exists() for name in ("publication.json", "publication-journal.json")):
        raise DeliveryError("publication boundary cannot receive review allowance")
    basis = _basis(d, run)
    last = basis["previous_review"]
    final = run / "verification.json"
    if not last or (last["result"] != "no-go" and not (
            last["result"] == "go" and final.exists() and _json(d, final).get("ok") is False)):
        raise DeliveryError("review allowance requires completed NO-GO or failed final verification")
    card = d.resolve_deliverable_card(metadata["card"])
    if d.native.is_native(card):
        changes = d.declared_change_plan(run)
        if not changes or [list(group) for group in changes] != basis["scope"]["groups"]:
            raise DeliveryError("review authorization checkpoint plan differs from accepted predecessor")
        d.validate_change_event_prefix(changes, d.combined_change_events(run))
    # Existing archive validation selects its receipt from the run environment.
    # This read-only scope follows the already checked operator entrypoint.
    previous = os.environ.get("CHRL_RUN_DIR")
    os.environ["CHRL_RUN_DIR"] = str(run)
    try:
        d.native.require_plan(d, card, run / "native-plan.json")
    finally:
        if previous is None:
            os.environ.pop("CHRL_RUN_DIR", None)
        else:
            os.environ["CHRL_RUN_DIR"] = previous
    if d.staged_paths():
        raise DeliveryError("review authorization requires an empty index")
    ok, detail, manifest = d.recovery_source(card, d.changed_paths(), required_run_id=run.name)
    if not ok or not manifest or manifest.get("run_id") != run.name:
        raise DeliveryError("review authorization requires exact starting payload: " + detail)


def review_allow(d: Any, run: Path, *, reason: str, authorize: str | None = None) -> dict:
    """Preview a stable digest or exclusively append its one-slot decision."""
    _operator()
    if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 1000 or len(reason) > 1000:
        raise DeliveryError("review allowance requires a reason of 1..1000 characters")
    if authorize is not None and (not isinstance(authorize, str) or not HASH.fullmatch(authorize)):
        raise DeliveryError("review allowance authorization must be a preview SHA256")
    run = _run(d, run)
    with d.delivery_lock():
        _quiescent(d)
        records = _records(d, run)
        for path, record in records:
            if record["predecessor"] == run.name and record["reason"] == reason.strip():
                if authorize is not None and authorize != record["proposal_sha256"]:
                    raise DeliveryError("stale review authorization digest")
                return {"state": "authorized", "authorization": _reference_for(d, path, record),
                        "proposal_sha256": record["proposal_sha256"], "proposal": record, "reused": True}
        _eligible(d, run)
        status = allowance(d, run)
        if status["remaining"] != 0 or status["in_flight"]:
            raise DeliveryError("review allowance is not exhausted; operator slots cannot be accumulated")
        proposal = {"schema": SCHEMA, **_basis(d, run), "grants_before": len(records),
                    "additional_reviews": 1, "review_number": status["spent_reviews"] + 1,
                    "previous_authorization": _reference(d, records[-1][0])["sha256"] if records else None,
                    "reason": reason.strip(), "operation": "repair-and-one-review"}
        proposal["starting"]["path_states"] = {p: d._path_state(p) for p in proposal["starting"]["paths"]}
        proposal["successor_run_id"] = _successor(proposal)
        proposal["proposal_sha256"] = _proposal_digest(proposal)
        if authorize is None:
            return {"state": "preview", "proposal": proposal, "proposal_sha256": proposal["proposal_sha256"]}
        if authorize != proposal["proposal_sha256"]:
            raise DeliveryError("stale review authorization digest; preview the current state")
        proposal["observed_at"] = d.utc_now()
        directory = _safe(d, d.RUNTIME_ROOT / "review-authorizations" / proposal["root_run"])
        directory.mkdir(parents=True, exist_ok=True)
        retained._sync(directory.parent)
        path = directory / f"{len(records) + 1:04d}.json"
        retained._write(path, proposal)
        return {"state": "authorized", "authorization": _reference_for(d, path, proposal),
                "proposal_sha256": authorize, "proposal": proposal, "reused": False}


def require_remaining(d: Any, run: Path, *, after: str = "") -> dict:
    status = allowance(d, run)
    if status["remaining"] <= 0:
        label = "review allowance exhausted" if status["operator_granted_slots"] else "shared two-review budget exhausted"
        raise ReviewExhausted(
            f"{label}{after}; autonomous=2, operator={status['operator_granted_slots']}, "
            f"spent={status['spent_reviews']}, remaining=0; operator review-allow +1 required"
        )
    return status


def recovery_authorization(d: Any, run: Path, *, check_live: bool = True) -> tuple[str, dict] | None:
    """Under delivery_lock, bind an unused grant before any child/writer exists."""
    status = require_remaining(d, run)
    for path, record in _records(d, run):
        if record["predecessor"] != run.name:
            continue
        _eligible(d, run)
        child = _safe(d, d.RUNTIME_ROOT / "runs" / record["successor_run_id"])
        if child.exists():
            raise DeliveryError("review authorization successor already exists; ambiguous dispatch cannot be replayed")
        states = {p: d._path_state(p) for p in record["starting"]["paths"]}
        if states != record["starting"]["path_states"]:
            raise DeliveryError("review authorization starting payload changed before claim")
        if check_live:
            _quiescent(d)
        return record["successor_run_id"], _reference_for(d, path, record)
    if status["operator_granted_slots"]:
        # A partial claimed child cannot turn its pending slot into a new child.
        # Native provisional continuation uses its existing supported route.
        if not d._completed_review_verdicts(run / "reviews"):
            raise DeliveryError("claimed review successor has no completed review; ambiguous dispatch cannot be replayed")
        _eligible(d, run)
    return None


def review_slot(d: Any, run: Path, *, continuation: bool = False) -> dict:
    status = require_remaining(d, run)
    number = status["spent_reviews"] + 1
    reference = next((r for r in status["authorizations"] if r["review_number"] == number), None)
    if number > 2:
        if reference is None:
            raise DeliveryError("review ordinal lacks operator authorization")
        record = _json(d, d.REPO_ROOT / reference["path"])
        if record["successor_run_id"] not in {p.name for p in _lineage(d, run)}:
            raise DeliveryError("operator review slot must be claimed through recovery before review")
        if status["in_flight"] and not continuation:
            raise DeliveryError("review allocation is unresolved; another independent launch is prohibited")
    return {"lineage_review_number": number, "review_authorization": reference}
