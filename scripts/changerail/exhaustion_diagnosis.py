"""Deterministic review-history analysis for exhausted native delivery.

The runner owns review, repair and verification outside the model. When two
reviews reject the same work, the reasons are already recorded in the retained
verdicts; this module turns them into an explicit, reproducible comparison so a
later repair - or an operator - sees the history instead of only the last
finding list. Nothing here grants authority or spends review allowance.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError

RECURRENCE_SCHEMA = "changerail.review-recurrence.v1"
CONDITION_SUFFIX = re.compile(r"([A-Za-z][A-Za-z0-9._-]*)$")
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
    history = run_dir / "reviews"
    cycles = []
    for index, path in enumerate(d._completed_review_verdicts(history), start=1):
        try:
            verdict = d.load_json(path)
        except DeliveryError:
            continue
        if not isinstance(verdict, dict):
            continue
        cycles.append(
            {
                "cycle": index,
                "path": d.repo_relative(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "result": verdict.get("result"),
                "conditions": _conditions(verdict),
                "findings": _findings(verdict),
            }
        )
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
