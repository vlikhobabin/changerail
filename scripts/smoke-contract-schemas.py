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
from changerail_repository_knowledge import (  # noqa: E402
    validate_detector_result,
    validate_lifecycle_report,
    validate_maintenance_baseline,
    validate_maintenance_run,
    validate_maintenance_state,
    validate_maintenance_triage,
    validate_proposal_decision,
    validate_quality_rollup,
    validate_scan_report,
)
from changerail_review_verdict import _validate_verdict  # noqa: E402


Validator = Callable[[Any], list[str]]
SHA = "sha256:" + ("0" * 64)
TREE = "0" * 40
DATE = "2026-07-12T00:00:00Z"
TARGET = {
    "schema": "changerail.execution-target.v1",
    "id": "database-primary",
    "fingerprint": "sha256:" + ("1" * 64),
    "target_substitution_policy": "forbid",
}


def execution_target() -> dict[str, Any]:
    return dict(TARGET)


def review_verdict() -> dict[str, Any]:
    return {
        "schema": "changerail.review-verdict.v1",
        "reviewed_at": DATE,
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "workspace": {
            "root": "/opt/changerail",
            "head_commit": "abc123",
            "tree_sha": TREE,
            "diff_fingerprint": SHA,
        },
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
        "acceptance": [
            {
                "criterion": "example",
                "verdict": "pass",
                "evidence": "schema smoke",
                "evidence_refs": [
                    {
                        "id": "schema-smoke",
                        "index_path": ".runtime/changerail/evidence/schema-smoke/index.json",
                        "raw_output_path": ".runtime/changerail/evidence/schema-smoke/outputs/schema-smoke.txt",
                        "classification": "mandatory",
                    }
                ],
            }
        ],
        "findings": [],
        "evidence_audit": {"claims_checked": 1, "claims_unbacked": 0},
    }


def delivery_manifest() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "repository": "ssh://github.com/vlikhobabin/changerail.git"},
        "execution_target": dict(TARGET),
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "changes": [{"slug": "example-change", "state": "active", "order": 1}],
        "committable_paths": [],
        "excluded_runtime_paths": [],
        "preexisting_dirty": [],
        "verification_summary": {
            "result": "passed",
            "summary": "schema smoke verification passed",
            "commands": [
                {
                    "command": "python3 scripts/smoke-contract-schemas.py",
                    "outcome": "passed",
                    "evidence_path": ".runtime/changerail/evidence/schema-smoke.log",
                    "evidence": {
                        "id": "schema-smoke",
                        "index_path": ".runtime/changerail/evidence/schema-smoke/index.json",
                        "raw_output_path": ".runtime/changerail/evidence/schema-smoke/outputs/schema-smoke.txt",
                        "classification": "mandatory",
                    },
                }
            ],
            "evidence_paths": [".runtime/changerail/evidence/schema-smoke.log"],
            "evidence_refs": [
                {
                    "id": "schema-smoke",
                    "index_path": ".runtime/changerail/evidence/schema-smoke/index.json",
                    "raw_output_path": ".runtime/changerail/evidence/schema-smoke/outputs/schema-smoke.txt",
                    "classification": "mandatory",
                }
            ],
        },
        "review_summary": {
            "result": "go",
            "summary": "fresh independent schema smoke review passed",
            "review_cycle": 1,
            "verdict_path": ".runtime/changerail/reviews/example-card.json",
            "findings": {"blocker": 0, "major": 0, "minor": 0},
        },
        "final_card_state": {
            "path": "openspec/board/4.done/example-card.md",
            "status": "4.done",
            "result_summary": "finalized through scoped publish",
        },
        "publish": {
            "status": "pushed",
            "payload_commit": "payload123",
            "published_commit": "published456",
            "remote": "origin",
            "branch": "main",
            "pushed_at": DATE,
            "mode": "review-gated",
        },
    }


def consumer_lock() -> dict[str, Any]:
    return {
        "schema": "changerail.consumer-lock.v1",
        "changerail": {
            "version": "0.4.0",
            "revision": "0" * 40,
            "source": "https://github.com/example/changerail.git",
        },
        "wiring": {
            "platform": "posix",
            "backend": "symlink",
            "path_mode": "absolute",
            "artifacts": [
                {
                    "path": "bin/openspec",
                    "source": "bin/openspec",
                    "kind": "symlink",
                    "surface": "helper",
                }
            ],
        },
        "profiles": {
            "project": "generic",
            "surfaces": "all-surfaces",
            "codex_policy": "safe-interactive",
        },
        "enforcement": "advisory",
    }


def delivery_run_minimal() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-run.v1",
        "run_id": "example-run",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123"},
        "execution_target": dict(TARGET),
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "phase": "terminal",
        "result": "DELIVERED",
        "terminal_outcome": "DELIVERED",
        "timestamps": {"started_at": DATE, "ended_at": DATE},
        "command": {"argv": ["bin/codex", "exec"], "launcher": "bin/codex", "stdin": "closed", "json": True},
        "usage": {"available": False, "reason": "not observed in schema smoke"},
    }


def retained_payload_identity() -> dict[str, Any]:
    return {
        "schema": "changerail.retained-payload-identity.v1",
        "source_run_id": "example-run",
        "source_status_path": ".runtime/changerail/delivery-runs/example-run/status.json",
        "captured_at": DATE,
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "workspace": {"root": "/opt/changerail"},
        "head_commit": "abc123",
        "tree_sha": TREE,
        "diff_fingerprint": SHA,
        "review_target": {"kind": "working-tree"},
        "execution_target": dict(TARGET),
    }


def external_blocker() -> dict[str, Any]:
    return {
        "schema": "changerail.external-blocker.v1",
        "blocker_id": "external-gate-ready",
        "class": "external_service",
        "observed_at": DATE,
        "retryable": True,
        "evidence_policy": {
            "required_ids": ["external-gate-ready"],
            "max_age_seconds": 3600,
        },
    }


def delivery_progress(phase: str = "do", stage: str = "implementation", counter: int = 3) -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-progress.v1",
        "phase": phase,
        "stage": stage,
        "heartbeat_at": DATE,
        "event_counter": counter,
    }


def progress_health(state: str = "active", age: float = 0.0, process_alive: bool = True) -> dict[str, Any]:
    return {
        "state": state,
        "heartbeat_age_seconds": age,
        "process_alive": process_alive,
    }


def delivery_run() -> dict[str, Any]:
    payload = delivery_run_minimal()
    payload["progress"] = delivery_progress()
    payload["progress_health"] = progress_health()
    payload["usage"] = {
        "available": True,
        "input_tokens": 10,
        "cached_input_tokens": 4,
        "uncached_input_tokens": 6,
        "output_tokens": 5,
        "reasoning_tokens": 2,
        "total_tokens": 15,
    }
    payload["preflight"] = {
        "checks": [
            {
                "name": "publish target",
                "status": "fail",
                "message": "mode=remote-push remote=origin branch=main remote_url_class=ssh reachable=false failure_class=dns detail=ssh: Could not resolve hostname example.invalid",
                "result": "failed",
                "remote": "origin",
                "branch": "main",
                "remote_url_class": "ssh",
                "failure_class": "dns",
                "retryable": True,
                "attempts": 2,
                "detail": "ssh: Could not resolve hostname example.invalid",
                "evidence": {
                    "command": "git ls-remote --exit-code <remote> refs/heads/<branch>",
                    "result": "failed",
                    "detail": "ssh: Could not resolve hostname example.invalid",
                },
            }
        ]
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
                "output": {
                    "stdout_bytes": 128,
                    "stderr_bytes": 0,
                    "total_bytes": 128,
                    "threshold_bytes": 65536,
                    "threshold_exceeded": False,
                    "classification": "success_bounded",
                    "truncated": False,
                },
            }
        ],
        "slowest_commands": [
            {
                "command_id": "cmd-1",
                "command": "python3 scripts/smoke-contract-schemas.py",
                "duration_seconds": 0.2,
                "exit_code": 0,
                "output": {
                    "stdout_bytes": 128,
                    "stderr_bytes": 0,
                    "total_bytes": 128,
                    "threshold_bytes": 65536,
                    "threshold_exceeded": False,
                    "classification": "success_bounded",
                },
            }
        ],
        "command_output": {
            "threshold_bytes": 65536,
            "observed_command_count": 1,
            "oversized_command_count": 1,
            "largest_command_bytes": 70000,
            "top_oversized_commands": [
                {
                    "command_id": "cmd-big",
                    "command": "rg --count example openspec/specs",
                    "stdout_bytes": 70000,
                    "stderr_bytes": 0,
                    "total_bytes": 70000,
                    "threshold_bytes": 65536,
                    "truncated": True,
                    "classification": "runner_truncated",
                }
            ],
        },
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
            "rescue_budget": {"limit": 2, "used": 0, "remaining": 2, "exhausted": False},
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
            {
                "alias": "service-a",
                "path": "service-a",
                "state": "delivered",
                "head_commit": "abc123",
                "execution_target": dict(TARGET),
            },
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
                "progress": delivery_progress("publish", "complete", 5),
                "progress_health": progress_health("terminated", 0.0, False),
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


def retained_external_recovery() -> dict[str, Any]:
    return {
        "kind": "original-retained-payload",
        "source_run_id": "child-a",
        "source_run_status_path": ".runtime/changerail/delivery-runs/child-a/status.json",
        "source_terminal_reason": "recoverable_external_blocker",
        "card": {"id": "service-a-card", "path": "openspec/board/3.inprogress/service-a-card.md"},
        "fingerprint": {
            "head_commit": "abc123",
            "tree_sha": TREE,
            "diff_fingerprint": SHA,
        },
        "review_target_kind": "working-tree",
        "execution_target": dict(TARGET),
        "external_blocker": external_blocker(),
    }


def review_cycle_history() -> dict[str, Any]:
    return {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": DATE,
        "card": {"id": "example-card", "path": "openspec/board/3.inprogress/example-card.md"},
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123"},
        "rescue_budget": {"limit": 2, "used": 0, "remaining": 2, "exhausted": False},
        "phase_counters": {
            "planning_cycles": 1,
            "delivery_fix_cycles": 1,
            "implementation_review_cycles": 1,
            "live_admission_reviews": 0,
        },
        "cycles": [
            {
                "review_cycle": 1,
                "same_card_rescue_attempt": 0,
                "result": "go",
                "reviewed_at": DATE,
                "verdict_path": ".runtime/changerail/reviews/example-card.json",
                "findings": {"blocker": 0, "major": 0, "minor": 0},
                "finding_details": [],
                "acceptance": {"pass": 1, "fail": 0, "unverifiable": 0, "not_applicable": 0},
            }
        ],
    }


def source_classification() -> dict[str, Any]:
    return {
        "schema": "changerail.source-classification.v1",
        "source_kinds": [
            {
                "id": "bsl",
                "suffixes": [".bsl"],
                "production_roots": ["src/production"],
                "measure": "lines",
            },
            {
                "id": "designer-xml",
                "suffixes": [".xml"],
                "production_roots": ["src/designer"],
                "measure": "xml-structure",
            },
        ],
        "non_production_roots": ["src/examples"],
    }


def review_preflight_result() -> dict[str, Any]:
    return {
        "schema": "changerail.review-preflight-result.v1",
        "checked_at": DATE,
        "ok": True,
        "outcome": "ready-for-llm-review",
        "workspace": {
            "root": "/opt/changerail",
            "head_commit": "abc123",
            "tree_sha": TREE,
            "diff_fingerprint": SHA,
        },
        "card": {
            "id": "example-card",
            "path": "openspec/board/3.inprogress/example-card.md",
            "status": "3.inprogress",
        },
        "manifest": {
            "path": ".runtime/changerail/delivery-manifests/example-card.json",
            "valid": True,
            "normalized": False,
            "scope_ok": True,
        },
        "execution_target": {
            "present": True,
            "path": ".changerail/execution-target.json",
            "identity": dict(TARGET),
            "manifest_identity": dict(TARGET),
            "evidence_identity_count": 1,
        },
        "risk": {
            "tier": "ordinary",
            "source": "card",
            "review_mode": "llm",
            "reasoning_effort": "high",
            "milestone_audit": False,
            "critical_boundary": False,
            "live_admission": False,
            "final_certification": False,
        },
        "complexity_guard": {
            "added_production_loc": 20,
            "limit": 300,
            "new_authority_or_wire_protocol": False,
            "repeated_defect_class": False,
            "published_investigation_authorization": {
                "status": "not-declared",
                "detail": "no published investigation authorization is declared",
            },
            "stop_required": False,
            "reasons": [],
            "source_breakdown": [
                {
                    "source_kind": "builtin",
                    "measure_strategy": "lines",
                    "path_count": 1,
                    "raw_added_lines": 20,
                    "effective_complexity": 20,
                    "fallback": "none",
                    "paths": ["src/example.py"],
                }
            ],
        },
        "checks": [{"id": "scope", "status": "pass", "detail": "exact scope"}],
        "llm_review": {"required": True, "reason": "ordinary semantic payload review"},
        "diagnostics": {
            "fingerprint": {
                "cache": {
                    "schema": "changerail.review-fingerprint-cache.v1",
                    "status": "hit",
                    "path": ".runtime/changerail/review-fingerprint-cache/fingerprint.json",
                },
                "tree_builder": {
                    "mode": "cache",
                    "changed_path_count": 2,
                    "full_index_refresh": False,
                },
                "timings": [
                    {"phase": "changed-path-discovery", "duration_ms": 1.0},
                    {"phase": "changed-path-metadata", "duration_ms": 1.0},
                ],
            },
            "preflight_timings": [
                {"phase": "fingerprint", "duration_ms": 2.0},
                {"phase": "openspec-validation", "duration_ms": 3.0},
                {"phase": "scoped-whitespace-check", "duration_ms": 1.0},
                {"phase": "public-surface-scan", "duration_ms": 4.0},
            ],
        },
    }


def evidence_index() -> dict[str, Any]:
    return {
        "schema": "changerail.evidence-index.v1",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "repository": "ssh://github.com/vlikhobabin/changerail.git"},
        "scope": {"card_id": "example-card", "changes": ["example-change"]},
        "execution_target": dict(TARGET),
        "entries": [
            {
                "id": "schema-smoke",
                "path": ".runtime/changerail/evidence/schema-smoke/outputs/schema-smoke.txt",
                "role": "raw_output",
                "storage": "runtime",
                "phase": "do",
                "classification": "mandatory",
                "change": "example-change",
                "kind": "verification_command",
                "reason": "schema smoke fixture",
                "command": {
                    "argv": ["python3", "scripts/smoke-contract-schemas.py"],
                    "display": "python3 scripts/smoke-contract-schemas.py",
                },
                "status": "passed",
                "exit_code": 0,
                "started_at": DATE,
                "ended_at": DATE,
                "duration_seconds": 0.1,
                "summary": "schema smoke passed",
                "raw_output_path": ".runtime/changerail/evidence/schema-smoke/outputs/schema-smoke.txt",
                "redacted": False,
                "timed_out": False,
                "execution_target": dict(TARGET),
            }
        ],
    }


def repository_knowledge_catalog() -> dict[str, Any]:
    return {
        "schema": "changerail.repository-knowledge.v1",
        "records": [
            {
                "path": "docs/changerail-contracts.md",
                "status": "active",
                "type": "reference",
                "owner": "ChangeRail core",
                "source_globs": ["schemas/changerail-*.schema.json"],
                "verify": ["python3 scripts/smoke-contract-schemas.py"],
                "review_after": None,
                "supersedes": [],
            },
            {
                "path": ".changerail/KNOWLEDGE.md",
                "status": "generated",
                "type": "generated",
                "owner": "ChangeRail core",
                "source_globs": [".changerail/knowledge.yaml"],
                "verify": ["bin/changerail-maintenance render-index --check"],
                "review_after": "2026-12-31",
                "supersedes": [],
            },
        ],
    }


def maintenance_policy() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-policy.v1",
        "catalog_path": ".changerail/knowledge.yaml",
        "generated_index_path": ".changerail/KNOWLEDGE.md",
        "scan": {
            "include_globs": ["docs/**/*.md"],
            "exclude_globs": ["docs/archive/**/*.md"],
            "active_scope_globs": ["docs/**/*.md"],
            "enabled_detectors": [
                "catalog-coverage",
                "repository-orphans",
                "markdown-local-links",
                "generated-freshness",
                "forbidden-active-references",
                "adapters",
            ],
            "fail_on": "major",
            "timeout_seconds": 30,
            "detectors": {
                "markdown_local_links": {"extensions": [".md"]},
                "generated_freshness": {"check_render_index": True},
                "forbidden_active_references": {
                    "patterns": [
                        {
                            "id": "private-path",
                            "pattern": "/home/example",
                            "severity": "major",
                            "message": "private path must not be active knowledge",
                        }
                    ]
                },
            },
            "adapters": [
                {
                    "id": "architecture-check",
                    "argv": ["python3", "scripts/example-adapter.py"],
                    "timeout_seconds": 10,
                    "options": {"profile": "architecture"},
                }
            ],
        },
    }


def maintenance_detector_result() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-detector-result.v1",
        "id": "adapter-architecture-check",
        "status": "error",
        "summary": "schema smoke detector result",
        "findings": [
            {
                "id": "adapter-architecture-check:architecture-rule:docs:example-md",
                "severity": "major",
                "code": "architecture_rule_violation",
                "message": "adapter reported a generic architecture finding",
                "path": "docs/example.md",
                "evidence": {"line": 1},
            }
        ],
        "errors": [
            {
                "code": "adapter_timeout",
                "message": "adapter exceeded timeout",
                "severity": "blocker",
            }
        ],
    }


def maintenance_scan_report() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-scan-report.v1",
        "generated_at": DATE,
        "workspace": {"root": "/opt/changerail"},
        "catalog_path": ".changerail/knowledge.yaml",
        "policy_path": ".changerail/maintenance.yaml",
        "complete": True,
        "fail_on": "major",
        "detectors": [maintenance_detector_result()],
        "configuration_diagnostics": [],
        "summary": {
            "detectors": 1,
            "findings": 1,
            "errors": 0,
            "max_severity": "major",
            "threshold_reached": True,
        },
    }


def maintenance_report() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-report.v1",
        "generated_at": DATE,
        "workspace": {"root": "/opt/changerail"},
        "source_scan": {
            "schema": "changerail.maintenance-scan-report.v1",
            "generated_at": DATE,
            "catalog_path": ".changerail/knowledge.yaml",
            "policy_path": ".changerail/maintenance.yaml",
            "complete": True,
        },
        "state": {
            "path": ".runtime/changerail/maintenance/state.json",
            "restored": True,
            "written": False,
            "continuity": "restored",
        },
        "complete": True,
        "fail_on": "major",
        "detectors": [{"id": "catalog-coverage", "status": "fail", "findings": 1, "errors": 0}],
        "findings": [
            {
                "fingerprint": SHA,
                "evidence_fingerprint": "sha256:" + ("1" * 64),
                "detector": "catalog-coverage",
                "rule": "uncovered_knowledge_file",
                "severity": "major",
                "confidence": 1.0,
                "path": "docs/example.md",
                "subject": {"path": "docs/example.md"},
                "evidence_refs": [{"kind": "detector-evidence", "key": "line", "value": 1}],
                "remediation": None,
                "first_seen": DATE,
                "last_seen": DATE,
                "owner": None,
                "risk_class": "maintenance",
                "status": "open",
            }
        ],
        "diagnostics": [],
        "summary": {
            "detectors": 1,
            "findings": 1,
            "open": 1,
            "accepted": 0,
            "waived": 0,
            "diagnostics": 0,
            "max_severity": "major",
            "threshold_reached": True,
        },
    }


def maintenance_state() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-state.v1",
        "updated_at": DATE,
        "identity_version": 1,
        "findings": {
            SHA: {
                "first_seen": DATE,
                "last_seen": DATE,
                "evidence_fingerprint": "sha256:" + ("1" * 64),
                "status": "open",
            }
        },
    }


def maintenance_baseline() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-baseline.v1",
        "accepted": [
            {
                "fingerprint": SHA,
                "owner": "ChangeRail core",
                "reason": "schema smoke accepted finding",
                "accepted_at": DATE,
            }
        ],
        "waivers": [
            {
                "fingerprint": "sha256:" + ("2" * 64),
                "owner": "ChangeRail core",
                "reason": "schema smoke waiver",
                "expires_at": "2026-12-31",
            }
        ],
    }


def maintenance_triage() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-triage.v1",
        "generated_at": DATE,
        "annotations": [
            {
                "fingerprint": SHA,
                "owner": "ChangeRail core",
                "risk_class": "maintenance",
                "remediation": "update tracked knowledge artifact",
                "status": "open",
                "reason": "schema smoke annotation",
            }
        ],
    }


def maintenance_quality_rollup() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-quality-rollup.v1",
        "generated_at": DATE,
        "workspace": {"root": "/opt/changerail"},
        "inputs": {
            "reports": [".runtime/changerail/maintenance/report-latest.json"],
            "histories": [".runtime/changerail/maintenance/report-earlier.json"],
            "triage": [".runtime/changerail/maintenance/triage.json"],
            "proposals": [".runtime/changerail/maintenance/proposals/proposal-accepted.json"],
        },
        "metrics": [
            {"id": "findings.open", "value": 1, "unit": "count", "status": "known"},
            {"id": "instruction.bytes", "value": "unknown", "unit": "bytes", "status": "unknown"},
        ],
        "diagnostics": [],
    }


def maintenance_proposal_decision() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-proposal-decision.v1",
        "proposal_id": "schema-smoke-proposal",
        "finding_fingerprint": SHA,
        "transformation_class": "docs-update",
        "decision": "accepted",
        "decided_at": DATE,
        "evidence_refs": [
            {
                "kind": "proposal",
                "key": "path",
                "value": ".runtime/changerail/maintenance/proposals/schema-smoke-proposal.json",
            }
        ],
    }


def maintenance_run() -> dict[str, Any]:
    return {
        "schema": "changerail.maintenance-run.v1",
        "run_id": "maintenance-schema-smoke",
        "updated_at": DATE,
        "workspace": {"root": "/opt/changerail", "head_commit": "abc123"},
        "mode": "scan",
        "phase": "terminal",
        "result": "SUCCEEDED",
        "timestamps": {"started_at": DATE, "ended_at": DATE},
        "command": {
            "argv": ["bin/changerail-maintenance", "report", "--json"],
            "stdin": "closed",
            "json": True,
            "timeout_seconds": 900,
        },
        "process": {"exit_code": 0, "timed_out": False},
        "lock": {
            "path": ".runtime/changerail/maintenance/maintenance.lock",
            "acquired": True,
            "released": True,
            "diagnostics": [],
        },
        "artifacts": {
            "lifecycle_report": ".runtime/changerail/maintenance/runs/maintenance-schema-smoke/maintenance-report.json"
        },
        "usage": {"available": False, "reason": "scan mode has no agent usage"},
        "diagnostics": [],
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
    "changerail-consumer-lock.schema.json": (
        consumer_lock,
        schema_validator("changerail-consumer-lock.schema.json"),
    ),
    "changerail-execution-target.schema.json": (
        execution_target,
        schema_validator("changerail-execution-target.schema.json"),
    ),
    "changerail-review-verdict.schema.json": (review_verdict, _validate_verdict),
    "changerail-review-preflight-result.schema.json": (
        review_preflight_result,
        schema_validator("changerail-review-preflight-result.schema.json"),
    ),
    "changerail-delivery-manifest.schema.json": (delivery_manifest, validate_manifest),
    "changerail-delivery-run.schema.json": (delivery_run, schema_validator("changerail-delivery-run.schema.json")),
    "changerail-delivery-plan.schema.json": (delivery_plan, validate_delivery_plan),
    "changerail-delivery-plan-status.schema.json": (delivery_plan_status, validate_delivery_plan_status),
    "changerail-review-cycle-history.schema.json": (
        review_cycle_history,
        schema_validator("changerail-review-cycle-history.schema.json"),
    ),
    "changerail-source-classification.schema.json": (
        source_classification,
        schema_validator("changerail-source-classification.schema.json"),
    ),
    "changerail-evidence-index.schema.json": (evidence_index, schema_validator("changerail-evidence-index.schema.json")),
    "changerail-repository-knowledge.schema.json": (
        repository_knowledge_catalog,
        schema_validator("changerail-repository-knowledge.schema.json"),
    ),
    "changerail-maintenance-policy.schema.json": (
        maintenance_policy,
        schema_validator("changerail-maintenance-policy.schema.json"),
    ),
    "changerail-maintenance-detector-result.schema.json": (
        maintenance_detector_result,
        validate_detector_result,
    ),
    "changerail-maintenance-scan-report.schema.json": (
        maintenance_scan_report,
        validate_scan_report,
    ),
    "changerail-maintenance-report.schema.json": (
        maintenance_report,
        validate_lifecycle_report,
    ),
    "changerail-maintenance-state.schema.json": (
        maintenance_state,
        validate_maintenance_state,
    ),
    "changerail-maintenance-baseline.schema.json": (
        maintenance_baseline,
        validate_maintenance_baseline,
    ),
    "changerail-maintenance-triage.schema.json": (
        maintenance_triage,
        validate_maintenance_triage,
    ),
    "changerail-maintenance-quality-rollup.schema.json": (
        maintenance_quality_rollup,
        validate_quality_rollup,
    ),
    "changerail-maintenance-proposal-decision.schema.json": (
        maintenance_proposal_decision,
        validate_proposal_decision,
    ),
    "changerail-maintenance-run.schema.json": (
        maintenance_run,
        validate_maintenance_run,
    ),
}


def mutate_invalid(payload: dict[str, Any]) -> dict[str, Any]:
    invalid = copy.deepcopy(payload)
    invalid["updated_at" if "updated_at" in invalid else "reviewed_at"] = "not-a-date-time"
    return invalid


def check_schema_file(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def expect_invalid(
    failures: list[str],
    label: str,
    validator: Validator,
    payload: dict[str, Any],
    needle: str,
) -> None:
    errors = validator(payload)
    if not errors:
        failures.append(f"{label}: invalid fixture unexpectedly passed")
        return
    if not any(needle in error for error in errors):
        failures.append(f"{label}: invalid fixture did not report {needle!r}: {errors}")


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
            reason_fixture = delivery_run_minimal()
            reason_fixture["result"] = "BLOCKED"
            reason_fixture["terminal_outcome"] = "BLOCKED"
            reason_fixture["terminal_reason"] = "fix_budget_exhausted"
            reason_errors = validator(reason_fixture)
            if reason_errors:
                failures.append(f"{name}: terminal reason fixture failed: {reason_errors}")
            external_fixture = delivery_run_minimal()
            external_fixture["result"] = "BLOCKED"
            external_fixture["terminal_outcome"] = "BLOCKED"
            external_fixture["terminal_reason"] = "recoverable_external_blocker"
            external_fixture["retained_payload"] = retained_payload_identity()
            external_fixture["external_blocker"] = external_blocker()
            external_errors = validator(external_fixture)
            if external_errors:
                failures.append(f"{name}: external blocker fixture failed: {external_errors}")
            unknown_external = copy.deepcopy(external_fixture)
            unknown_external["external_blocker"]["class"] = "project_specific_outage"
            if not validator(unknown_external):
                failures.append(f"{name}: unknown external blocker class unexpectedly passed")
            content_external = copy.deepcopy(external_fixture)
            content_external["external_blocker"]["response_body"] = "RESPONSE_BODY_SHOULD_NOT_PASS"
            if not validator(content_external):
                failures.append(f"{name}: content-bearing external blocker unexpectedly passed")
            missing_retained_external = copy.deepcopy(external_fixture)
            missing_retained_external.pop("retained_payload")
            if not validator(missing_retained_external):
                failures.append(f"{name}: external blocker without retained identity unexpectedly passed")
            invalid_reason = copy.deepcopy(reason_fixture)
            invalid_reason["terminal_reason"] = "free form reason"
            if not validator(invalid_reason):
                failures.append(f"{name}: invalid terminal reason unexpectedly passed")
            invalid_alias = delivery_run_minimal()
            invalid_alias["status"] = "BLOCKED"
            if not validator(invalid_alias):
                failures.append(f"{name}: duplicate top-level status alias unexpectedly passed")
            invalid_output = delivery_run()
            invalid_output["performance"]["commands"][0]["output"]["raw_stdout"] = "raw payload must not be accepted"
            if not validator(invalid_output):
                failures.append(f"{name}: raw command output payload unexpectedly passed")
            running_stale = delivery_run_minimal()
            running_stale["phase"] = "delivery"
            running_stale["result"] = "RUNNING"
            running_stale["progress"] = delivery_progress("do", "verification", 7)
            running_stale["progress_health"] = progress_health("stale", 12.5, True)
            if validator(running_stale):
                failures.append(f"{name}: running stale progress fixture failed")
            invalid_progress_enum = delivery_run()
            invalid_progress_enum["progress"]["phase"] = "raw-child-output"
            if not validator(invalid_progress_enum):
                failures.append(f"{name}: unknown progress phase unexpectedly passed")
            invalid_progress_content = delivery_run()
            invalid_progress_content["progress"]["raw_log_excerpt"] = "synthetic raw child output"
            if not validator(invalid_progress_content):
                failures.append(f"{name}: content-bearing progress unexpectedly passed")
        if name == "changerail-consumer-lock.schema.json":
            unsafe_source = consumer_lock()
            unsafe_source["changerail"]["source"] = "https://user:secret@example.invalid/changerail.git"
            expect_invalid(failures, f"{name} credential source", validator, unsafe_source, "source")
            absolute_source = consumer_lock()
            absolute_source["changerail"]["source"] = "/opt/changerail"
            expect_invalid(failures, f"{name} absolute source", validator, absolute_source, "source")
            incomplete_revision = consumer_lock()
            incomplete_revision["changerail"]["revision"] = "abc123"
            expect_invalid(failures, f"{name} incomplete revision", validator, incomplete_revision, "revision")
        if name == "changerail-review-cycle-history.schema.json":
            legacy_history = review_cycle_history()
            legacy_history.pop("rescue_budget")
            legacy_history.pop("phase_counters")
            for cycle in legacy_history["cycles"]:
                cycle.pop("same_card_rescue_attempt", None)
            legacy_errors = validator(legacy_history)
            if legacy_errors:
                failures.append(f"{name}: legacy fixture without rescue budget failed: {legacy_errors}")
        if name == "changerail-source-classification.schema.json":
            unsafe_source_root = source_classification()
            unsafe_source_root["source_kinds"][0]["production_roots"] = ["/absolute"]
            expect_invalid(failures, f"{name} unsafe production root", validator, unsafe_source_root, "production_roots")
            traversal_root = source_classification()
            traversal_root["non_production_roots"] = ["src/../fixtures"]
            expect_invalid(failures, f"{name} traversal non-production root", validator, traversal_root, "non_production_roots")
        if name == "changerail-maintenance-report.schema.json":
            missing_detectors = copy.deepcopy(positive)
            missing_detectors.pop("detectors")
            if not validator(missing_detectors):
                failures.append(f"{name}: missing detector summary unexpectedly passed")
        if name == "changerail-maintenance-run.schema.json":
            invalid_alias = copy.deepcopy(positive)
            invalid_alias["status"] = "success"
            if not validator(invalid_alias):
                failures.append(f"{name}: duplicate top-level status alias unexpectedly passed")
        negative = mutate_invalid(positive)
        negative_errors = validator(negative)
        if not negative_errors:
            failures.append(f"{name}: negative date-time fixture unexpectedly passed")

    pushed_status_only = delivery_manifest()
    pushed_status_only["publish"] = {"status": "pushed"}
    for label, validator in (
        ("changerail-delivery-manifest.schema.json schema pushed status-only", schema_validator("changerail-delivery-manifest.schema.json")),
        ("changerail-delivery-manifest.schema.json helper pushed status-only", validate_manifest),
    ):
        expect_invalid(failures, label, validator, copy.deepcopy(pushed_status_only), "payload_commit")

    pushed_missing_pushed_at = delivery_manifest()
    pushed_missing_pushed_at["publish"].pop("pushed_at")
    for label, validator in (
        (
            "changerail-delivery-manifest.schema.json schema pushed missing pushed_at",
            schema_validator("changerail-delivery-manifest.schema.json"),
        ),
        ("changerail-delivery-manifest.schema.json helper pushed missing pushed_at", validate_manifest),
    ):
        expect_invalid(failures, label, validator, copy.deepcopy(pushed_missing_pushed_at), "pushed_at")

    bad_manifest_evidence = delivery_manifest()
    del bad_manifest_evidence["verification_summary"]["commands"][0]["evidence"]["index_path"]
    for label, validator in (
        (
            "changerail-delivery-manifest.schema.json schema malformed evidence ref",
            schema_validator("changerail-delivery-manifest.schema.json"),
        ),
        ("changerail-delivery-manifest.schema.json helper malformed evidence ref", validate_manifest),
    ):
        expect_invalid(failures, label, validator, copy.deepcopy(bad_manifest_evidence), "index_path")

    bad_verdict_evidence = review_verdict()
    del bad_verdict_evidence["acceptance"][0]["evidence_refs"][0]["index_path"]
    expect_invalid(
        failures,
        "changerail-review-verdict.schema.json malformed evidence ref",
        _validate_verdict,
        bad_verdict_evidence,
        "index_path",
    )

    unsafe_plan = delivery_plan()
    unsafe_plan["workspaces"][0]["path"] = "/opt/example-a"
    if not validate_delivery_plan(unsafe_plan):
        failures.append("changerail-delivery-plan.schema.json: unsafe absolute workspace path unexpectedly passed")

    duplicate_plan = delivery_plan()
    duplicate_plan["cards"].append(copy.deepcopy(duplicate_plan["cards"][0]))
    if not validate_delivery_plan(duplicate_plan):
        failures.append("changerail-delivery-plan.schema.json: duplicate card id unexpectedly passed")

    recovery_plan = delivery_plan()
    recovery_plan["cards"].append(
        {
            "id": "service-a-recovery",
            "workspace": "service-a",
            "card": "service-a-recovery.md",
            "wave": 1,
            "recovery_for": "service-a-card",
        }
    )
    if validate_delivery_plan(recovery_plan):
        failures.append("changerail-delivery-plan.schema.json: recovery card fixture failed")

    recovery_status = delivery_plan_status()
    recovery_status["cards"][0]["state"] = "recovered"
    recovery_status["cards"][0]["result"] = "NO-GO"
    recovery_status["cards"][0]["terminal_reason"] = "review_no_go"
    recovery_status["cards"][0]["recovered_by"] = "service-a-recovery"
    recovery_status["summary"]["recovered"] = 1
    if validate_delivery_plan_status(recovery_status):
        failures.append("changerail-delivery-plan-status.schema.json: recovery status fixture failed")

    external_recovery_status = delivery_plan_status()
    external_recovery_status["result"] = "BLOCKED"
    external_recovery_status["terminal_outcome"] = "BLOCKED"
    external_recovery_status["cards"][0]["state"] = "blocked"
    external_recovery_status["cards"][0]["result"] = "BLOCKED"
    external_recovery_status["cards"][0]["terminal_reason"] = "recoverable_external_blocker"
    external_recovery_status["cards"][0]["retained_recovery"] = retained_external_recovery()
    external_recovery_status["summary"]["delivered"] = 1
    external_recovery_status["summary"]["blocked"] = 1
    if validate_delivery_plan_status(external_recovery_status):
        failures.append("changerail-delivery-plan-status.schema.json: external retained recovery fixture failed")

    invalid_external_recovery = copy.deepcopy(external_recovery_status)
    invalid_external_recovery["cards"][0]["retained_recovery"]["external_blocker"]["entered_credential"] = "secret"
    if not validate_delivery_plan_status(invalid_external_recovery):
        failures.append("changerail-delivery-plan-status.schema.json: content-bearing external retained recovery unexpectedly passed")

    invalid_plan_progress = delivery_plan_status()
    invalid_plan_progress["cards"][0]["progress"]["stage"] = "free-form-child-prose"
    if not validate_delivery_plan_status(invalid_plan_progress):
        failures.append("changerail-delivery-plan-status.schema.json: unknown progress stage unexpectedly passed")

    remote_failure_status = delivery_plan_status()
    remote_failure_status["result"] = "BLOCKED"
    remote_failure_status["terminal_outcome"] = "BLOCKED"
    remote_failure_status["cards"][0]["state"] = "blocked"
    remote_failure_status["cards"][0]["result"] = "BLOCKED"
    remote_failure_status["cards"][0]["failure_class"] = "timeout"
    remote_failure_status["cards"][0]["reason"] = "publish target fail: timeout"
    remote_failure_status["summary"]["delivered"] = 1
    remote_failure_status["summary"]["blocked"] = 1
    if validate_delivery_plan_status(remote_failure_status):
        failures.append("changerail-delivery-plan-status.schema.json: remote failure status fixture failed")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(f"SMOKE_CONTRACT_SCHEMAS_OK ({len(FIXTURES)} schemas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
