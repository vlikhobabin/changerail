#!/usr/bin/env python3
"""Smoke-test all public ChangeRail contract schemas."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCHEMAS = ROOT / "schemas"
sys.path.insert(0, str(SCRIPTS))

from changerail_contract_schema import validate_with_schema  # noqa: E402
from changerail_delivery_manifest import validate_manifest  # noqa: E402
from changerail_review_verdict import _validate_verdict  # noqa: E402


Validator = Callable[[Any], list[str]]
SHA = "sha256:" + ("0" * 64)
DATE = "2026-07-12T00:00:00Z"


def review_verdict() -> dict[str, Any]:
    return {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": DATE,
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123", "diff_fingerprint": SHA},
        "reviewer": {
            "kind": "codex-exec",
            "independence": {
                "fresh_context": True,
                "did_not_plan_or_implement": True,
                "basis": "fresh schema smoke fixture",
            },
        },
        "result": "go",
        "review_cycle": 1,
        "acceptance": [{"criterion": "example", "verdict": "pass", "evidence": "schema smoke"}],
        "findings": [],
        "evidence_audit": {"claims_checked": 1, "claims_unbacked": 0},
    }


def delivery_manifest() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "repository": "ssh://github.com/vlikhobabin/changerail.git"},
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "changes": [{"slug": "example-change", "state": "active", "order": 1}],
        "committable_paths": [],
        "excluded_runtime_paths": [],
        "preexisting_dirty": [],
        "publish": {"status": "pending"},
    }


def delivery_run_minimal() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-run.v1",
        "run_id": "example-run",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123"},
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "phase": "terminal",
        "result": "DELIVERED",
        "terminal_outcome": "DELIVERED",
        "timestamps": {"started_at": DATE, "ended_at": DATE},
        "command": {"argv": ["bin/codex", "exec"], "launcher": "bin/codex", "stdin": "closed", "json": True},
        "usage": {"available": False, "reason": "not observed in schema smoke"},
    }


def delivery_run() -> dict[str, Any]:
    payload = delivery_run_minimal()
    payload["usage"] = {
        "available": True,
        "input_tokens": 10,
        "cached_input_tokens": 4,
        "uncached_input_tokens": 6,
        "output_tokens": 5,
        "reasoning_tokens": 2,
        "total_tokens": 15,
    }
    payload["performance"] = {
        "wall_time_seconds": 12.5,
        "event_counts": {"exec_command": 2, "agent_message": 1},
        "agent_message_count": 1,
        "command_execution_count": 2,
        "file_change_count": 3,
        "commands": [
            {
                "command_id": "cmd-1",
                "command": "python3 scripts/smoke-contract-schemas.py",
                "started_at": DATE,
                "ended_at": DATE,
                "duration_seconds": 0.2,
                "exit_code": 0,
            }
        ],
        "slowest_commands": [
            {
                "command_id": "cmd-1",
                "command": "python3 scripts/smoke-contract-schemas.py",
                "duration_seconds": 0.2,
                "exit_code": 0,
            }
        ],
        "timeline": [
            {
                "observed_at": DATE,
                "event_id": "event-1",
                "event_type": "exec_command.completed",
                "command_id": "cmd-1",
                "command": "python3 scripts/smoke-contract-schemas.py",
                "duration_seconds": 0.2,
            }
        ],
        "review": {
            "cycle_count": 1,
            "first_review_latency_seconds": 10.0,
            "time_to_final_go_seconds": 10.0,
            "cycles": [{"review_cycle": 1, "result": "go", "reviewed_at": DATE, "latency_seconds": 10.0}],
        },
        "publish": {"latency_seconds": 2.0, "pushed_at": DATE},
    }
    return payload


def delivery_plan() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-plan.v1",
        "id": "example-plan",
        "description": "schema smoke multi-workspace plan",
        "max_parallel": 2,
        "per_workspace_parallelism": 1,
        "push_mode": "push",
        "workspaces": [
            {"alias": "service-a", "path": "service-a"},
            {"alias": "service-b", "path": "service-b"},
        ],
        "waves": [
            {"id": 1, "name": "foundation"},
            {"id": 2, "name": "dependent", "depends_on": [1]},
        ],
        "cards": [
            {
                "id": "service-a-card",
                "workspace": "service-a",
                "card": "openspec/board/3.inprogress/service-a-card.md",
                "wave": 1,
                "model": "gpt-test",
                "reasoning_effort": "medium",
            },
            {
                "id": "service-b-card",
                "workspace": "service-b",
                "card": "service-b-card.md",
                "depends_on": ["service-a-card"],
                "wave": 2,
            },
        ],
    }


def delivery_plan_status() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-plan-status.v1",
        "run_id": "example-plan-run",
        "updated_at": DATE,
        "plan": {
            "id": "example-plan",
            "path": "delivery-plan.json",
            "fingerprint": SHA,
        },
        "phase": "terminal",
        "result": "DELIVERED",
        "terminal_outcome": "DELIVERED",
        "mode": "push",
        "timestamps": {"started_at": DATE, "ended_at": DATE},
        "max_parallel": 2,
        "per_workspace_parallelism": 1,
        "workspaces": [
            {"alias": "service-a", "path": "service-a", "state": "delivered", "head_commit": "abc123"},
            {"alias": "service-b", "path": "service-b", "state": "delivered", "head_commit": "def456"},
        ],
        "cards": [
            {
                "id": "service-a-card",
                "workspace": "service-a",
                "card": "openspec/board/3.inprogress/service-a-card.md",
                "resolved_path": "openspec/board/4.done/service-a-card.md",
                "state": "delivered",
                "wave": 1,
                "run_id": "child-a",
                "run_status_path": ".runtime/changerail/delivery-runs/child-a/status.json",
                "result": "DELIVERED",
            },
            {
                "id": "service-b-card",
                "workspace": "service-b",
                "card": "service-b-card.md",
                "resolved_path": "openspec/board/4.done/service-b-card.md",
                "state": "delivered",
                "wave": 2,
                "depends_on": ["service-a-card"],
                "run_id": "child-b",
                "run_status_path": ".runtime/changerail/delivery-runs/child-b/status.json",
                "result": "DELIVERED",
            },
        ],
        "summary": {"total_cards": 2, "delivered": 2, "blocked": 0, "no_go": 0, "skipped": 0},
    }


def review_cycle_history() -> dict[str, Any]:
    return {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": DATE,
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123"},
        "cycles": [
            {
                "review_cycle": 1,
                "result": "go",
                "reviewed_at": DATE,
                "verdict_path": ".runtime/changerail/reviews/example-card.json",
                "findings": {"blocker": 0, "major": 0, "minor": 0},
                "finding_details": [],
                "acceptance": {"pass": 1, "fail": 0, "unverifiable": 0, "not_applicable": 0},
            }
        ],
    }


def evidence_index() -> dict[str, Any]:
    return {
        "schema": "changerail.evidence-index.v1",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "repository": "ssh://github.com/vlikhobabin/changerail.git"},
        "scope": {"card_id": "example-card", "changes": ["example-change"]},
        "entries": [],
    }


def schema_validator(schema_file: str) -> Validator:
    return lambda payload: validate_with_schema(payload, schema_file)


def validate_delivery_plan(payload: Any) -> list[str]:
    errors = validate_with_schema(payload, "changerail-delivery-plan.schema.json")
    if errors or not isinstance(payload, dict):
        return errors

    workspaces = payload.get("workspaces")
    cards = payload.get("cards")
    waves = payload.get("waves", [])
    if not isinstance(workspaces, list) or not isinstance(cards, list):
        return errors

    workspace_aliases: set[str] = set()
    for workspace in workspaces:
        if not isinstance(workspace, dict):
            continue
        alias = workspace.get("alias")
        if isinstance(alias, str):
            if alias in workspace_aliases:
                errors.append(f"duplicate workspace alias: {alias}")
            workspace_aliases.add(alias)

    wave_ids: set[int] = set()
    if isinstance(waves, list):
        for wave in waves:
            if not isinstance(wave, dict):
                continue
            wave_id = wave.get("id")
            if isinstance(wave_id, int):
                if wave_id in wave_ids:
                    errors.append(f"duplicate wave id: {wave_id}")
                wave_ids.add(wave_id)
            for dependency in wave.get("depends_on", []) if isinstance(wave.get("depends_on"), list) else []:
                if isinstance(dependency, int) and dependency >= wave_id:
                    errors.append(f"wave {wave_id} depends on non-earlier wave {dependency}")

    card_ids: set[str] = set()
    card_waves: dict[str, int] = {}
    for card in cards:
        if not isinstance(card, dict):
            continue
        card_id = card.get("id")
        if isinstance(card_id, str):
            if card_id in card_ids:
                errors.append(f"duplicate card id: {card_id}")
            card_ids.add(card_id)
        workspace = card.get("workspace")
        if isinstance(workspace, str) and workspace not in workspace_aliases:
            errors.append(f"unknown workspace for card {card_id}: {workspace}")
        wave = card.get("wave")
        if isinstance(wave, int):
            if wave_ids and wave not in wave_ids:
                errors.append(f"unknown wave for card {card_id}: {wave}")
            if isinstance(card_id, str):
                card_waves[card_id] = wave

    for card in cards:
        if not isinstance(card, dict):
            continue
        card_id = card.get("id")
        wave = card_waves.get(card_id) if isinstance(card_id, str) else None
        for dependency in card.get("depends_on", []) if isinstance(card.get("depends_on"), list) else []:
            if dependency not in card_ids:
                errors.append(f"unknown dependency for card {card_id}: {dependency}")
            dependency_wave = card_waves.get(dependency)
            if isinstance(wave, int) and isinstance(dependency_wave, int) and dependency_wave > wave:
                errors.append(f"card {card_id} depends on later-wave card {dependency}")
    return errors


def validate_delivery_plan_status(payload: Any) -> list[str]:
    errors = validate_with_schema(payload, "changerail-delivery-plan-status.schema.json")
    if errors or not isinstance(payload, dict):
        return errors
    card_ids: set[str] = set()
    for card in payload.get("cards", []) if isinstance(payload.get("cards"), list) else []:
        if not isinstance(card, dict):
            continue
        card_id = card.get("id")
        if isinstance(card_id, str):
            if card_id in card_ids:
                errors.append(f"duplicate status card id: {card_id}")
            card_ids.add(card_id)
    return errors


FIXTURES: dict[str, tuple[Callable[[], dict[str, Any]], Validator]] = {
    "changerail-review-verdict.schema.json": (review_verdict, _validate_verdict),
    "changerail-delivery-manifest.schema.json": (delivery_manifest, validate_manifest),
    "changerail-delivery-run.schema.json": (delivery_run, schema_validator("changerail-delivery-run.schema.json")),
    "changerail-delivery-plan.schema.json": (delivery_plan, validate_delivery_plan),
    "changerail-delivery-plan-status.schema.json": (delivery_plan_status, validate_delivery_plan_status),
    "changerail-review-cycle-history.schema.json": (
        review_cycle_history,
        schema_validator("changerail-review-cycle-history.schema.json"),
    ),
    "changerail-evidence-index.schema.json": (evidence_index, schema_validator("changerail-evidence-index.schema.json")),
}


def mutate_invalid(payload: dict[str, Any]) -> dict[str, Any]:
    invalid = copy.deepcopy(payload)
    invalid["updated_at" if "updated_at" in invalid else "reviewed_at"] = "not-a-date-time"
    return invalid


def check_schema_file(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def main() -> int:
    failures: list[str] = []
    schema_files = sorted(path.name for path in SCHEMAS.glob("changerail-*.schema.json"))
    missing = sorted(set(FIXTURES) - set(schema_files))
    extra = sorted(set(schema_files) - set(FIXTURES))
    if missing:
        failures.append(f"missing schema files: {', '.join(missing)}")
    if extra:
        failures.append(f"schema lacks smoke fixture: {', '.join(extra)}")

    for name in schema_files:
        try:
            check_schema_file(SCHEMAS / name)
        except Exception as exc:
            failures.append(f"{name}: invalid Draft 2020-12 schema: {exc}")

    for name, (factory, validator) in FIXTURES.items():
        positive = factory()
        positive_errors = validator(positive)
        if positive_errors:
            failures.append(f"{name}: positive fixture failed: {positive_errors}")
        if name == "changerail-delivery-run.schema.json":
            minimal_errors = validator(delivery_run_minimal())
            if minimal_errors:
                failures.append(f"{name}: minimal fixture without performance failed: {minimal_errors}")
        negative = mutate_invalid(positive)
        negative_errors = validator(negative)
        if not negative_errors:
            failures.append(f"{name}: negative date-time fixture unexpectedly passed")

    unsafe_plan = delivery_plan()
    unsafe_plan["workspaces"][0]["path"] = "/opt/example-a"
    if not validate_delivery_plan(unsafe_plan):
        failures.append("changerail-delivery-plan.schema.json: unsafe absolute workspace path unexpectedly passed")

    duplicate_plan = delivery_plan()
    duplicate_plan["cards"].append(copy.deepcopy(duplicate_plan["cards"][0]))
    if not validate_delivery_plan(duplicate_plan):
        failures.append("changerail-delivery-plan.schema.json: duplicate card id unexpectedly passed")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(f"SMOKE_CONTRACT_SCHEMAS_OK ({len(FIXTURES)} schemas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
