"""Deterministic review-history analysis for exhausted native delivery.

The runner owns review, repair and verification outside the model. When two
reviews reject the same work, the reasons are already recorded in the retained
verdicts; this module turns them into an explicit, reproducible comparison so a
later repair - or an operator - sees the history instead of only the last
finding list. Nothing here grants authority or spends review allowance.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError

RECURRENCE_SCHEMA = "changerail.review-recurrence.v1"
CONDITION_SUFFIX = re.compile(r"([A-Za-z][A-Za-z0-9._-]*)$")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
FAILED = "fail"


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def condition_name(value: Any) -> str | None:
    """Reduce a qualified condition reference to its short identifier.

    Verdict decisions name conditions as ``<card>@sha256:<hash>:C1``. Reports
    and cards use the short ``C1`` form, so comparisons must use the suffix.
    """
    if not isinstance(value, str) or not value:
        return None
    match = CONDITION_SUFFIX.search(value.rsplit(":", 1)[-1])
    return match.group(1) if match else None


def _conditions(verdict: dict[str, Any]) -> dict[str, str]:
    """Short condition identifier -> disposition, from one verdict."""
    result: dict[str, str] = {}
    decisions = verdict.get("decisions")
    if not isinstance(decisions, list):
        return result
    for decision in decisions:
        if not isinstance(decision, dict):
            continue
        refs = decision.get("condition_refs")
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, dict):
                    continue
                name = condition_name(ref.get("condition"))
                disposition = ref.get("disposition") or decision.get("disposition")
                if name and isinstance(disposition, str):
                    result.setdefault(name, disposition)
        scenario = decision.get("scenario")
        disposition = decision.get("disposition")
        if isinstance(scenario, str) and isinstance(disposition, str):
            tail = re.search(r"Condition:\s*([^/]+)$", scenario.strip())
            if tail:
                name = condition_name(tail.group(1).strip())
                if name:
                    result.setdefault(name, disposition)
    return result


def _findings(verdict: dict[str, Any]) -> list[dict[str, Any]]:
    rows = verdict.get("findings")
    if not isinstance(rows, list):
        return []
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        paths = row.get("paths")
        result.append(
            {
                "id": row.get("id"),
                "severity": row.get("severity"),
                "summary": row.get("summary"),
                "paths": sorted({p for p in paths if isinstance(p, str)})
                if isinstance(paths, list)
                else [],
            }
        )
    return result


def _cycles(d: Any, run_dir: Path) -> list[dict[str, Any]]:
    """Completed verdicts of the whole recovery lineage, oldest first.

    A successor run continues the same attempt, so its reasons only make sense
    against the reviews that already rejected the lineage. Cycle numbers are
    therefore lineage-wide, and a verdict retained twice is counted once.
    """
    roots = [run_dir]
    try:
        roots = [*reversed(d.recovery_ancestors(run_dir)), run_dir]
    except DeliveryError:
        # A run outside a valid recovery chain reports its own history only.
        pass
    cycles: list[dict[str, Any]] = []
    # A successor that retained copies of its predecessor's verdicts must not
    # count them twice; genuinely identical cycles inside one run still stand.
    inherited: set[str] = set()
    for root in roots:
        retained_here: set[str] = set()
        for path in d._completed_review_verdicts(root / "reviews"):
            try:
                verdict = d.load_json(path)
            except DeliveryError:
                continue
            if not isinstance(verdict, dict):
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in inherited:
                continue
            retained_here.add(digest)
            cycles.append(
                {
                    "cycle": len(cycles) + 1,
                    "run": root.name,
                    "path": d.repo_relative(path),
                    "sha256": digest,
                    "result": verdict.get("result"),
                    "conditions": _conditions(verdict),
                    "findings": _findings(verdict),
                }
            )
        inherited |= retained_here
    return cycles


def recurrence(d: Any, run_dir: Path) -> dict[str, Any]:
    """Compare every retained verdict and report what repeats or has closed.

    Pure function of the retained verdicts: it never writes, never spends a
    review and never changes the accepted plan. A condition is recurring only
    when it failed in the latest completed review and in an earlier one, so the
    report claims nothing the records do not show.
    """
    cycles = _cycles(d, run_dir)
    if not cycles:
        raise DeliveryError("review recurrence requires at least one completed verdict")
    latest = cycles[-1]
    history: dict[str, list[dict[str, Any]]] = {}
    for cycle in cycles:
        for name, disposition in cycle["conditions"].items():
            history.setdefault(name, []).append(
                {"cycle": cycle["cycle"], "disposition": disposition}
            )

    recurring, closed, new_failures = [], [], []
    for name in sorted(history):
        entries = history[name]
        latest_entry = next(
            (item for item in entries if item["cycle"] == latest["cycle"]), None
        )
        if latest_entry is None:
            continue
        earlier_failed = any(
            item["disposition"] == FAILED
            for item in entries
            if item["cycle"] != latest["cycle"]
        )
        if latest_entry["disposition"] == FAILED:
            (recurring if earlier_failed else new_failures).append(name)
        elif earlier_failed:
            closed.append(name)

    earlier_by_path: dict[str, str] = {}
    for cycle in cycles[:-1]:
        for finding in cycle["findings"]:
            for path in finding["paths"]:
                earlier_by_path.setdefault(path, str(finding.get("id")))
    recurring_findings = []
    for finding in latest["findings"]:
        shared = sorted(p for p in finding["paths"] if p in earlier_by_path)
        if shared:
            recurring_findings.append(
                {
                    "cycle": latest["cycle"],
                    "id": finding.get("id"),
                    "severity": finding.get("severity"),
                    "summary": finding.get("summary"),
                    "shared_paths": shared,
                    "earlier_ids": sorted({earlier_by_path[p] for p in shared}),
                }
            )

    if latest["result"] != "no-go":
        observed: str | None = None
    elif recurring or recurring_findings:
        observed = "repeat_defect"
    elif new_failures:
        observed = "incomplete_work"
    else:
        observed = None

    evidence = {
        "cycles": [
            {
                "cycle": cycle["cycle"],
                "result": cycle["result"],
                "sha256": cycle["sha256"],
                "conditions": cycle["conditions"],
            }
            for cycle in cycles
        ],
        "recurring_conditions": recurring,
        "closed_conditions": closed,
        "new_failures": new_failures,
        "recurring_findings": recurring_findings,
        "observed_class": observed,
    }
    return {
        "schema": RECURRENCE_SCHEMA,
        "run": d.repo_relative(run_dir),
        "cycle_count": len(cycles),
        "latest_result": latest["result"],
        "conditions": history,
        "recurring_conditions": recurring,
        "closed_conditions": closed,
        "new_failures": new_failures,
        "recurring_findings": recurring_findings,
        "observed_class": observed,
        "recurrence_sha256": _digest(evidence),
    }


DIAGNOSIS_SCHEMA = "changerail.exhausted-review-diagnosis.v1"
CHOICE_SCHEMA = "changerail.exhausted-review-choice.v1"
AMENDMENT_SCHEMA = "changerail.criterion-amendment.v1"

# Closed class set: the class decides which transitions are offered, so an
# unknown situation must fall back to an operator menu rather than to a guess.
CLASSES = (
    "repeat_defect",
    "incomplete_work",
    "plan_conflict",
    "evidence_model_gap",
    "unreproducible",
    "infrastructure",
    "unsatisfiable",
)

OPTION_SPECS: dict[str, dict[str, Any]] = {
    "systemic-repair": {
        "preconditions": "The payload can still be repaired inside the accepted scope, and the operator grants the one review this costs.",
        "effect": "One in-scope repair that changes the approach, then one independent review.",
        "reviews": 1,
        "scope": "in-scope",
        "architecture": False,
        "transition": "repair",
    },
    "continue-repair": {
        "preconditions": "The remaining accepted work is unfinished and no accepted criterion has to change.",
        "effect": "Finish the remaining in-scope work, then one independent review.",
        "reviews": 1,
        "scope": "in-scope",
        "architecture": False,
        "transition": "repair",
    },
    "re-review": {
        "preconditions": "The payload is reviewable as it stands: the observed scope and the deterministic pre-review floor can be re-established for the same bytes.",
        "effect": "Repeat the independent review on the unchanged payload.",
        "reviews": 1,
        "scope": "in-scope",
        "architecture": False,
        "transition": "review",
    },
    "revise-plan": {
        "preconditions": "The operator accepts that the current attempt is closed as unsuccessful and that a separate new plan must be accepted.",
        "effect": "Close this attempt as unsuccessful and accept a separate new plan.",
        "reviews": 0,
        "scope": "new-plan",
        "architecture": True,
        "transition": "close-and-replan",
    },
    "extend-proof-model": {
        "preconditions": "The proof model needs a tool change, which is a separate delivery, not a repair inside this attempt.",
        "effect": "Change the tool so the required proof can be expressed, then replan.",
        "reviews": 0,
        "scope": "tool-change",
        "architecture": True,
        "transition": "close-and-replan",
    },
    "amend-criterion": {
        "preconditions": "The operator restates the criterion explicitly with `rethink --amend-criterion`, and the amended criterion is accepted before any further implementation.",
        "effect": "Restate an unachievable acceptance criterion as a separate operator decision.",
        "reviews": 1,
        "scope": "criterion",
        "architecture": False,
        "transition": "amend-criterion",
    },
    "technical-recovery": {
        "preconditions": "A retained capacity failure makes this an environment stop rather than a product defect.",
        "effect": "Treat the stop as an infrastructure failure and use the existing recovery route.",
        "reviews": 0,
        "scope": "infrastructure",
        "architecture": False,
        "transition": "technical-recovery",
    },
    "close-attempt": {
        "preconditions": "The operator decides the attempt ends without a successor plan.",
        "effect": "Close the attempt as unsuccessful without a new plan.",
        "reviews": 0,
        "scope": "terminal",
        "architecture": False,
        "transition": "close-attempt",
    },
}

CLASS_OPTIONS: dict[str, tuple[str, ...]] = {
    "repeat_defect": ("systemic-repair", "revise-plan"),
    "incomplete_work": ("continue-repair", "revise-plan"),
    "plan_conflict": ("revise-plan", "amend-criterion"),
    "evidence_model_gap": ("extend-proof-model", "amend-criterion", "revise-plan"),
    "unreproducible": ("re-review", "systemic-repair"),
    "infrastructure": ("technical-recovery",),
    "unsatisfiable": ("amend-criterion", "revise-plan"),
}
FALLBACK_OPTIONS = (
    "systemic-repair",
    "revise-plan",
    "amend-criterion",
    "technical-recovery",
    "close-attempt",
)

RECOMMENDED = {
    "repeat_defect": "systemic-repair",
    "incomplete_work": "continue-repair",
    "plan_conflict": "revise-plan",
    "evidence_model_gap": "extend-proof-model",
    "unreproducible": "re-review",
    "infrastructure": "technical-recovery",
    "unsatisfiable": "amend-criterion",
}


def options_for(primary_class: str | None) -> list[dict[str, Any]]:
    """Transitions offered for one class; an unknown class offers the full menu."""
    ids = CLASS_OPTIONS.get(primary_class or "", FALLBACK_OPTIONS)
    return [{"id": name, **OPTION_SPECS[name]} for name in ids]


def _rationale(primary: str | None, report: dict[str, Any]) -> str:
    if primary == "repeat_defect":
        parts = []
        if report["recurring_conditions"]:
            parts.append(
                "conditions already failed earlier: "
                + ", ".join(report["recurring_conditions"])
            )
        if report["recurring_findings"]:
            parts.append(
                "findings on paths reported earlier: "
                + ", ".join(str(row.get("id")) for row in report["recurring_findings"])
            )
        return (
            "The same work was rejected again ("
            + "; ".join(parts)
            + "). A repair of the same shape did not change the outcome."
        )
    if primary == "incomplete_work":
        return (
            "The latest review rejected conditions earlier reviews did not: "
            + ", ".join(report["new_failures"])
            + ". The remaining work looks incomplete rather than wrongly approached."
        )
    if primary == "infrastructure":
        return "The stop is attributable to infrastructure, not to a product defect."
    return (
        "The retained verdicts show neither a repeated condition nor a newly failed"
        " one, so the situation needs an explicit decision."
    )


def _deterministic(d: Any, run_dir: Path) -> dict[str, Any]:
    """Build a bounded diagnosis for an exhausted review lineage.

    The artifact is a proposal: it states the observed class, why, and which
    already-supported transitions are available. It spends no review, grants no
    slot and changes no criterion or plan.
    """
    report = recurrence(d, run_dir)
    primary = report["observed_class"]
    if primary is not None and primary not in CLASSES:
        raise DeliveryError(f"unsupported diagnosis class: {primary}")
    return {
        "schema": DIAGNOSIS_SCHEMA,
        "run": report["run"],
        "primary_class": primary,
        "status": "auto" if primary == "infrastructure" else "operator_required",
        "rationale": _rationale(primary, report),
        "options": options_for(primary),
        "recommendation": RECOMMENDED.get(primary or ""),
        "recurrence": report,
        "diagnosis_sha256": _state_digest(d, run_dir, report, primary),
    }


def _state_digest(
    d: Any, run_dir: Path, report: dict[str, Any], primary: str | None
) -> str:
    """Digest of the exact lineage state a diagnosis speaks about.

    The verdict history alone is not the state: a diagnosis and the choice it
    supports must become inapplicable when the accepted plan or the payload
    changes, even before another review exists. A layer that cannot observe the
    working tree records that explicitly instead of pretending the state is
    bound.
    """
    try:
        plan = d.declared_change_plan(run_dir)
    except (DeliveryError, OSError):
        plan = None
    try:
        fingerprint: str | None = d.payload_fingerprint()
    except (DeliveryError, OSError):
        fingerprint = None
    return _digest(
        {
            "run": report["run"],
            "recurrence_sha256": report["recurrence_sha256"],
            "primary_class": primary,
            "change_plan": [list(group) for group in plan] if plan else None,
            "payload_fingerprint": fingerprint,
        }
    )


MODEL_SCHEMA = "changerail.exhausted-review-diagnosis-model.v1"
MODEL_ARTIFACT = "exhausted-diagnosis-model.json"
CONTEXT_NAME = "exhausted-diagnosis-context.json"

# A model may refine the class, but it must not deny what the retained verdicts
# already show. A repeated condition cannot become "incomplete work", and a new
# failure cannot be reported as a repeat.
CONSISTENT_WITH_REPEAT = frozenset(
    {
        "repeat_defect",
        "plan_conflict",
        "evidence_model_gap",
        "unreproducible",
        "unsatisfiable",
    }
)
CONSISTENT_WITH_NEW = frozenset(
    {
        "incomplete_work",
        "plan_conflict",
        "evidence_model_gap",
        "unreproducible",
        "unsatisfiable",
    }
)
# With no comparable condition or finding in the retained history the runner
# cannot confirm any claim about the criteria or the plan, so a model may only
# report what this stop itself shows.
UNVERIFIED_BASE_CLASSES = frozenset({"unreproducible", "infrastructure"})


def route(d: Any, current_profile: dict[str, Any]) -> tuple[str, str] | None:
    """Return the optional diagnosis model route, or None when not configured.

    The route is optional by contract: without it the runner keeps the
    deterministic analysis and the operator menu, exactly as before.
    """
    configured = current_profile.get("models", {}).get("diagnosis")
    if not isinstance(configured, dict):
        return None
    return d.model_route({"models": {"diagnosis": configured}}, "diagnosis")


def _model_claim(d: Any, run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / MODEL_ARTIFACT
    if not path.is_file():
        return None
    value = d.load_json(path)
    return value if isinstance(value, dict) else None


def _refine(d: Any, run_dir: Path, base: dict[str, Any]) -> dict[str, Any]:
    claim = _model_claim(d, run_dir)
    if claim is None or claim.get("schema") != MODEL_SCHEMA:
        return base
    primary = claim.get("primary_class")
    if primary not in CLASSES:
        return base
    report = base["recurrence"]
    if report["recurring_conditions"] or report["recurring_findings"]:
        allowed = CONSISTENT_WITH_REPEAT
    elif report["new_failures"]:
        allowed = CONSISTENT_WITH_NEW
    else:
        # The retained verdicts show nothing comparable. A claim about the
        # criteria or the plan then rests on no observation at all, so only the
        # two classes that assert something about this stop itself are accepted:
        # the observation did not reproduce, or the stop is environmental.
        allowed = UNVERIFIED_BASE_CLASSES
    if primary not in allowed:
        return base
    rationale = claim.get("rationale")
    refined = {
        **base,
        "primary_class": primary,
        "status": "operator_required",
        "rationale": rationale.strip()
        if isinstance(rationale, str) and rationale.strip()
        else base["rationale"],
        "options": options_for(primary),
        "recommendation": RECOMMENDED.get(primary),
        "model": {
            "model": claim.get("model"),
            "reasoning_effort": claim.get("reasoning_effort"),
        },
    }
    refined["diagnosis_sha256"] = _state_digest(d, run_dir, report, primary)
    return refined


def diagnosis(d: Any, run_dir: Path) -> dict[str, Any]:
    """Diagnosis for the current state, refined by the model claim when present."""
    return _refine(d, run_dir, _deterministic(d, run_dir))


def diagnosis_context(d: Any, run_dir: Path) -> Path:
    """Write the bounded instruction for one diagnosis session."""
    base = _deterministic(d, run_dir)
    path = run_dir / CONTEXT_NAME
    # The session runs from the repository root, so name the artifact by its
    # repository-relative path: a bare filename would be written where the
    # runner never reads it, and the refinement would silently never apply.
    artifact = d.repo_relative(run_dir / MODEL_ARTIFACT)
    d.write_json(
        path,
        {
            "schema": "changerail.exhausted-review-diagnosis-context.v1",
            "run": base["run"],
            "deterministic": {
                "primary_class": base["primary_class"],
                "recurrence": base["recurrence"],
                "options": base["options"],
            },
            "classes": list(CLASSES),
            "artifact": artifact,
            "artifact_schema": MODEL_SCHEMA,
            "instruction": (
                "Two independent reviews rejected this lineage and the review"
                " allowance is exhausted. Diagnose why; do not implement, review,"
                " repair, publish or change any accepted plan or acceptance"
                " criterion. Read the whole review history, the accepted plan and"
                " the card. Decide whether the same defect repeats, whether the work"
                " is merely incomplete, whether the accepted plan and the review"
                " demands conflict, whether the required proof cannot be expressed,"
                " whether the observation is not reproducible, whether the stop is"
                " infrastructure, or whether a criterion cannot be achieved as"
                " written. Write "
                f"{artifact} with schema {MODEL_SCHEMA}, fields"
                " primary_class (one of the listed classes), rationale and model."
                " A class that denies an observed repetition or a newly failed"
                " condition is rejected by the runner."
            ),
        },
    )
    return path


def announce(
    d: Any,
    run_dir: Path,
    current_profile: dict[str, Any],
    *,
    reason: str,
    launch: Any = None,
) -> str:
    """Record the diagnosis and return the operator-facing stop message.

    With a configured diagnosis model route the runner refines an undetermined
    situation through one bounded session; without it the deterministic analysis
    stands. Either way the message names the class, the recommendation and the
    transitions the situation supports - the stop is a decision point, not a
    dead end.
    """
    value = write_diagnosis(d, run_dir)
    configured = route(d, current_profile)
    if configured is not None and value["primary_class"] is None and launch is not None:
        context = diagnosis_context(d, run_dir)
        launch(context=context)
        value = write_diagnosis(d, run_dir)
    options = ", ".join(item["id"] for item in value["options"])
    try:
        choice = recorded_choice(d, run_dir)
    except DeliveryError:
        choice = None
    if choice is None:
        return (
            f"{reason}; diagnosis {value['primary_class'] or 'undetermined'}"
            f" (recommended: {value['recommendation'] or 'operator judgement'});"
            f" available: {options}"
        )
    return (
        f"{reason}; operator chose {choice.get('option')}"
        f" ({choice.get('transition')}): {followup(str(choice.get('transition')))}"
    )


def followup(transition: str | None) -> str:
    """What the operator must do next for one recorded transition.

    Shared by the stop message and by the runner: a decision the runner cannot
    execute itself must name the separate route that can.
    """
    if transition in {"close-and-replan", "close-attempt"}:
        return (
            "close this attempt as unsuccessful and accept a separate new plan;"
            " no review slot is spent by this route"
        )
    if transition == "technical-recovery":
        return (
            "use the existing technical recovery route; this is not a product"
            " review decision"
        )
    if transition == "amend-criterion":
        return (
            "record the criterion amendment, then apply the new wording and"
            " re-accept the plan through the ordinary board route before any"
            " further implementation"
        )
    if transition == "review":
        return (
            "grant the next review with review-allow and resume; the runner"
            " repeats the observed scope, the pre-review floor and the review"
            " on the unchanged payload"
        )
    return (
        "grant the next review with review-allow and resume; the chosen"
        " approach applies to the repair turn"
    )


def automatic_route(d: Any, run_dir: Path, value: dict[str, Any]) -> str | None:
    """Prepare the existing technical recovery for an infrastructure stop.

    Only an infrastructure class is prepared without an operator, and this
    function only *prepares*. The class itself grants nothing: the authority is
    ``technical_recovery.prepare``, which independently requires a retained
    capacity failure and refuses an unproven or unsupported stop. A model claim
    is therefore a bounded proposal - the recovery guard decides whether it is
    even expressible, and applying the prepared proposal stays an operator
    action.
    """
    if value.get("primary_class") != "infrastructure":
        return None
    from scripts.changerail import technical_recovery

    source = "deterministic" if value.get("status") == "auto" else "proposed"
    try:
        proposal = technical_recovery.prepare(d, run_dir)
    except DeliveryError as refusal:
        return f"{source}, refused: {refusal}"
    return f"{source}, prepared: {proposal['proposal']}"


def decision_state(d: Any, run_dir: Path) -> dict[str, Any]:
    """Machine-readable state of a run that waits for an operator decision."""
    value = diagnosis(d, run_dir)
    path = _rethink_root(d, run_dir) / "diagnosis.json"
    return {
        "schema": "changerail.awaiting-operator-decision.v1",
        "run": value["run"],
        "primary_class": value["primary_class"],
        "rationale": value["rationale"],
        "recommendation": value["recommendation"],
        "options": [item["id"] for item in value["options"]],
        "diagnosis": d.repo_relative(path) if path.is_file() else None,
        "diagnosis_sha256": value["diagnosis_sha256"],
    }


def recorded_choice(d: Any, run_dir: Path) -> dict[str, Any] | None:
    """Latest recorded operator choice, refused when it no longer matches state."""
    directory = _rethink_root(d, run_dir) / "choices"
    if not directory.is_dir():
        return None
    records = sorted(directory.glob("choice-*.json"))
    if not records:
        return None
    value = d.load_json(records[-1])
    if value.get("diagnosis_sha256") != diagnosis(d, run_dir)["diagnosis_sha256"]:
        raise DeliveryError("recorded choice is stale for the current diagnosis")
    return value


def _rethink_root(d: Any, run_dir: Path) -> Path:
    """Where the diagnosis, choices and amendments of one run are retained."""
    return d.RUNTIME_ROOT / "rethink" / run_dir.name


def write_diagnosis(d: Any, run_dir: Path) -> dict[str, Any]:
    """Write the diagnosis for the current state, reusing an unchanged one."""
    root = _rethink_root(d, run_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "diagnosis.json"
    if path.is_file():
        current = d.load_json(path)
        fresh = diagnosis(d, run_dir)
        if current.get("diagnosis_sha256") == fresh["diagnosis_sha256"]:
            return current
    value = diagnosis(d, run_dir)
    d.write_json(path, value)
    return value


def load_diagnosis(d: Any, run_dir: Path) -> dict[str, Any]:
    """Load a diagnosis and refuse a stale one for changed lineage state."""
    path = _rethink_root(d, run_dir) / "diagnosis.json"
    if not path.is_file():
        raise DeliveryError("no exhausted-review diagnosis for this run")
    value = d.load_json(path)
    if value.get("diagnosis_sha256") != diagnosis(d, run_dir)["diagnosis_sha256"]:
        raise DeliveryError("diagnosis is stale for the current review history")
    return value


def _operator() -> None:
    from scripts.changerail.review_allowance import _operator as guard

    guard()


def _author() -> dict[str, Any]:
    """Audit identity of the separate operator that recorded a decision.

    This is not authentication: the trust boundary is ``_operator``, which
    refuses any worker context. Recording who ran the command keeps the
    immutable record readable as history.
    """
    try:
        user: str | None = getpass.getuser()
    except (OSError, KeyError):
        user = None
    return {"user": user, "uid": os.getuid()}


def _retained_run(d: Any, run_dir: Path, what: str) -> Path:
    """Accept one exact retained run directory, without symlinks or aliases."""
    resolved = Path(run_dir).absolute()
    if (
        resolved.parent != d.RUNTIME_ROOT / "runs"
        or not NAME.fullmatch(resolved.name)
        or resolved.resolve() != resolved
    ):
        raise DeliveryError(f"{what} requires an exact retained run directory")
    metadata = d._check_json(resolved / "run.json")
    if metadata.get("run_id") != resolved.name:
        raise DeliveryError(f"{what} requires the run's own directory")
    return resolved


def _choice_records(d: Any, run_dir: Path) -> list[Path]:
    directory = _rethink_root(d, run_dir) / "choices"
    return sorted(directory.glob("choice-*.json")) if directory.is_dir() else []


def _append(d: Any, directory: Path, prefix: str, value: dict[str, Any]) -> Path:
    from scripts.changerail import plan_restoration as retained

    directory.mkdir(parents=True, exist_ok=True)
    retained._sync(directory.parent)
    index = len(list(directory.glob(f"{prefix}-*.json"))) + 1
    path = directory / f"{prefix}-{index:04d}.json"
    retained._write(path, value)
    return path


def choose(
    d: Any,
    run_dir: Path,
    *,
    option_id: str,
    reason: str,
    authorize: str | None = None,
) -> dict[str, Any]:
    """Preview or append the one immutable operator choice for a diagnosis.

    A decision is exclusive and non-accumulating: one diagnosis supports exactly
    one transition, so a second, different choice is refused instead of silently
    replacing the first. Recording the same choice again is idempotent.
    """
    _operator()
    if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 1000:
        raise DeliveryError("choice requires a reason of 1..1000 characters")
    run_dir = _retained_run(d, run_dir, "choice")
    with d.delivery_lock():
        value = load_diagnosis(d, run_dir)
        available = {item["id"] for item in value["options"]}
        if option_id not in available:
            raise DeliveryError(f"option is not available for this diagnosis: {option_id}")
        for path in _choice_records(d, run_dir):
            recorded = d.load_json(path)
            if recorded.get("diagnosis_sha256") != value["diagnosis_sha256"]:
                continue
            if recorded.get("option") != option_id or recorded.get("reason") != reason.strip():
                raise DeliveryError(
                    "this diagnosis already carries the"
                    f" `{recorded.get('option')}` decision; one decision per"
                    " exhausted state, and the recorded one is immutable"
                )
            # The same decision recorded again is the same decision.
            return {
                "state": "chosen",
                "choice": recorded,
                "path": d.repo_relative(path),
                "reused": True,
            }
        proposal = {
            "schema": CHOICE_SCHEMA,
            "run": value["run"],
            "diagnosis_sha256": value["diagnosis_sha256"],
            "primary_class": value["primary_class"],
            "option": option_id,
            "transition": OPTION_SPECS[option_id]["transition"],
            "reviews": OPTION_SPECS[option_id]["reviews"],
            "reason": reason.strip(),
            "author": _author(),
            "observed_at": d.utc_now(),
        }
        proposal["choice_sha256"] = _digest(proposal)
        if authorize is None:
            return {"state": "preview", "proposal": proposal}
        if authorize != proposal["choice_sha256"]:
            raise DeliveryError("stale choice digest; preview the current diagnosis")
        path = _append(d, _rethink_root(d, run_dir) / "choices", "choice", proposal)
        return {"state": "chosen", "choice": proposal, "path": d.repo_relative(path)}


def amend_criterion(
    d: Any,
    run_dir: Path,
    *,
    condition: str,
    before: str,
    after: str,
    reason: str,
    authorize: str | None = None,
) -> dict[str, Any]:
    """Preview or append one immutable operator criterion amendment.

    The previous wording stays in the record, so history is preserved and the
    amendment cannot rewrite what earlier reviews judged.
    """
    _operator()
    for label, text in (("before", before), ("after", after), ("reason", reason)):
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 2000:
            raise DeliveryError(f"criterion amendment {label} must be 1..2000 characters")
    name = condition_name(condition) or condition
    run_dir = _retained_run(d, run_dir, "amendment")
    with d.delivery_lock():
        value = load_diagnosis(d, run_dir)
        # The class is advisory: a deterministic analysis cannot prove a
        # criterion unexpressible, so an undetermined situation still lets the
        # operator restate it explicitly. A repeated defect does not.
        if value["primary_class"] not in {
            None,
            "unsatisfiable",
            "evidence_model_gap",
            "plan_conflict",
        }:
            raise DeliveryError(
                "criterion amendment requires an undetermined, unachievable or "
                "unexpressible criterion diagnosis"
            )
        proposal = {
            "schema": AMENDMENT_SCHEMA,
            "run": value["run"],
            "diagnosis_sha256": value["diagnosis_sha256"],
            "condition": name,
            "before": before.strip(),
            "after": after.strip(),
            "reason": reason.strip(),
            "author": _author(),
            "observed_at": d.utc_now(),
        }
        proposal["amendment_sha256"] = _digest(proposal)
        if authorize is None:
            return {"state": "preview", "proposal": proposal}
        if authorize != proposal["amendment_sha256"]:
            raise DeliveryError("stale amendment digest; preview the current diagnosis")
        path = _append(
            d,
            _rethink_root(d, run_dir) / "criterion-amendments",
            "amendment",
            proposal,
        )
        return {"state": "amended", "amendment": proposal, "path": d.repo_relative(path)}
