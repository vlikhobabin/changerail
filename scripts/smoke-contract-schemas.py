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


def delivery_run() -> dict[str, Any]:
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


FIXTURES: dict[str, tuple[Callable[[], dict[str, Any]], Validator]] = {
    "changerail-review-verdict.schema.json": (review_verdict, _validate_verdict),
    "changerail-delivery-manifest.schema.json": (delivery_manifest, validate_manifest),
    "changerail-delivery-run.schema.json": (delivery_run, schema_validator("changerail-delivery-run.schema.json")),
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
        negative = mutate_invalid(positive)
        negative_errors = validator(negative)
        if not negative_errors:
            failures.append(f"{name}: negative date-time fixture unexpectedly passed")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(f"SMOKE_CONTRACT_SCHEMAS_OK ({len(FIXTURES)} schemas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
