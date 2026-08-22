#!/usr/bin/env python3
"""Smoke checks for ChangeRail delivery metrics."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "bin" / "changerail-delivery-metrics"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
    raise AssertionError(f"{label} failed: {detail}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_record(
    run_id: str,
    card_id: str,
    result: str,
    usage: dict[str, Any],
    performance: dict[str, Any] | None = None,
    *,
    episode_id: str | None = None,
    attempt_kind: str = "delivery",
    phase: str = "terminal",
    started_at: str = "2026-07-11T00:00:00Z",
    ended_at: str = "2026-07-11T00:00:10Z",
) -> dict[str, Any]:
    record = {
        "schema": "changerail.delivery-run.v1",
        "run_id": run_id,
        "updated_at": "2026-07-11T00:00:10Z",
        "workspace": {"root": "/opt/changerail"},
        "card": {"id": card_id, "path": f"openspec/board/3.inprogress/{card_id}.md"},
        "phase": phase,
        "result": result,
        "terminal_outcome": result,
        "timestamps": {"started_at": started_at, "ended_at": ended_at},
        "command": {"argv": ["bin/codex", "exec"], "launcher": "bin/codex", "stdin": "closed", "json": True},
        "usage": usage,
    }
    if episode_id:
        record["episode"] = {"schema": "changerail.delivery-episode-lineage.v1", "id": episode_id}
        record["attempt"] = {"schema": "changerail.delivery-attempt.v1", "id": run_id, "kind": attempt_kind}
    if performance is not None:
        record["performance"] = performance
    return record


def history(card_id: str, cycles: list[dict[str, Any]], episode_id: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": "2026-07-11T00:00:20Z",
        "workspace": {"root": "/opt/changerail"},
        "card": {"id": card_id, "path": f"openspec/board/3.inprogress/{card_id}.md"},
        "cycles": cycles,
    }
    if episode_id:
        payload["episode"] = {"schema": "changerail.delivery-episode-lineage.v1", "id": episode_id}
    return payload


def queue_status() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-plan-status.v1",
        "run_id": "queue-1",
        "updated_at": "2026-07-11T00:00:30Z",
        "plan": {
            "id": "example-plan",
            "path": "delivery-plan.json",
            "fingerprint": "sha256:" + ("1" * 64),
        },
        "phase": "terminal",
        "result": "DELIVERED",
        "terminal_outcome": "DELIVERED",
        "mode": "no-push",
        "timestamps": {"started_at": "2026-07-11T00:00:00Z", "ended_at": "2026-07-11T00:00:30Z"},
        "cards": [
            {
                "id": "card-a",
                "workspace": "service-a",
                "card": "card-a.md",
                "state": "delivered",
                "run_id": "run-1",
                "episode_id": "episode-a",
                "run_status_path": "runs/run-1/status.json",
                "result": "DELIVERED",
            },
            {
                "id": "card-b",
                "workspace": "service-b",
                "card": "card-b.md",
                "state": "delivered",
                "run_id": "run-2",
                "episode_id": "episode-b",
                "run_status_path": "runs/run-2/status.json",
                "result": "DELIVERED",
            },
        ],
        "summary": {"total_cards": 2, "delivered": 2, "blocked": 0, "no_go": 0, "skipped": 0},
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-delivery-metrics-") as tmp:
        root = Path(tmp)
        runs = root / "runs"
        episodes = root / "episodes"
        reviews = root / "reviews"
        plans = root / "plans"
        write_json(
            episodes / "episode-d.json",
            {
                "schema": "changerail.delivery-episode.v1",
                "episode_id": "episode-d",
                "updated_at": "2026-07-11T00:00:20Z",
                "workspace": {"root": "/opt/changerail"},
                "card": {"id": "card-d", "path": "openspec/board/3.inprogress/card-d.md"},
                "attempts": [
                    {
                        "id": "episode-d-run",
                        "kind": "delivery",
                        "started_at": "2026-07-11T00:00:00Z",
                        "ended_at": "2026-07-11T00:00:04Z",
                        "terminal_state": "delivered",
                        "usage": {"available": True, "input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
                        "owner_artifact": {"kind": "derived-episode", "path": ".runtime/changerail/delivery-episodes/episode-d.json"},
                    }
                ],
                "final_outcome": "delivered",
            },
        )
        write_json(
            runs / "run-0" / "status.json",
            run_record(
                "run-0",
                "card-a",
                "BLOCKED",
                {"available": True, "input_tokens": 0, "cached_input_tokens": 0, "uncached_input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0},
                episode_id="episode-a",
                attempt_kind="delivery",
                started_at="2026-07-11T00:00:00Z",
                ended_at="2026-07-11T00:00:05Z",
            ),
        )
        write_json(
            runs / "run-1" / "status.json",
            run_record(
                "run-1",
                "card-a",
                "DELIVERED",
                {
                    "available": True,
                    "input_tokens": 10,
                    "cached_input_tokens": 4,
                    "uncached_input_tokens": 6,
                    "output_tokens": 5,
                    "reasoning_tokens": 2,
                },
                {
                    "wall_time_seconds": 10.5,
                    "agent_message_count": 3,
                    "command_execution_count": 2,
                    "command_samples": {"observed_count": 455, "retained_count": 50, "limit": 50, "truncated": True},
                    "file_change_count": 7,
                    "slowest_commands": [
                        {"command": "/bin/echo one", "duration_seconds": 1.5, "exit_code": 0},
                        {"command": "/bin/echo two", "duration_seconds": 0.25, "exit_code": 0},
                    ],
                    "command_output": {
                        "threshold_bytes": 65536,
                        "observed_command_count": 2,
                        "oversized_command_count": 1,
                        "largest_command_bytes": 90000,
                        "top_oversized_commands": [
                            {
                                "command_id": "cmd-big",
                                "command": "rg --count example openspec/specs",
                                "stdout_bytes": 90000,
                                "stderr_bytes": 0,
                                "total_bytes": 90000,
                                "threshold_bytes": 65536,
                                "classification": "success_oversized",
                            }
                        ],
                    },
                    "review": {
                        "cycle_count": 2,
                        "first_review_latency_seconds": 11.0,
                        "time_to_final_go_seconds": 19.0,
                        "rescue_budget": {"limit": 5, "used": 4, "remaining": 1, "exhausted": False},
                    },
                },
                episode_id="episode-a",
                attempt_kind="recovery",
                started_at="2026-07-11T00:00:05Z",
                ended_at="2026-07-11T00:00:10Z",
            ),
        )
        write_json(
            runs / "run-2" / "status.json",
            run_record(
                "run-2",
                "card-b",
                "DELIVERED",
                {"available": False, "reason": "usage not observed"},
                episode_id="episode-b",
                attempt_kind="delivery",
            ),
        )
        write_json(
            runs / "run-preflight" / "status.json",
            run_record(
                "run-preflight",
                "card-b",
                "DELIVERED",
                {"available": False, "reason": "usage not observed"},
                episode_id="episode-preflight",
                attempt_kind="preflight",
                phase="preflight",
                started_at="2026-07-11T00:00:01Z",
                ended_at="2026-07-11T00:00:02Z",
            ),
        )
        write_json(
            runs / "run-3" / "status.json",
            run_record(
                "run-3",
                "card-c",
                "DELIVERED",
                {"available": False, "reason": "usage not observed"},
                {
                    "review": {
                        "cycle_count": 3,
                        "rescue_budget": {"limit": 3, "used": 2, "remaining": 1, "exhausted": False},
                    }
                },
            ),
        )
        write_json(
            reviews / "card-a.history.json",
            history(
                "card-a",
                [
                    {
                        "review_cycle": 1,
                        "same_card_rescue_attempt": 0,
                        "result": "no-go",
                        "reviewed_at": "2026-07-11T00:00:11Z",
                        "verdict_path": ".runtime/changerail/reviews/card-a.json",
                        "verdict_snapshot_path": ".runtime/changerail/reviews/card-a.cycle-1.json",
                        "findings": {"blocker": 1, "major": 1, "minor": 0},
                        "finding_details": [
                            {
                                "id": "R1",
                                "severity": "blocker",
                                "summary": "workspace not honored",
                                "detail": "child process ran outside the requested workspace",
                                "paths": ["bin/changerail-delivery-runner"],
                            },
                            {
                                "id": "R2",
                                "severity": "major",
                                "summary": "evidence incomplete",
                            },
                        ],
                        "acceptance": {"pass": 2, "fail": 1, "unverifiable": 0, "not_applicable": 0},
                    },
                    {
                        "review_cycle": 2,
                        "same_card_rescue_attempt": 1,
                        "result": "go",
                        "reviewed_at": "2026-07-11T00:00:19Z",
                        "verdict_path": ".runtime/changerail/reviews/card-a.json",
                        "findings": {"blocker": 0, "major": 0, "minor": 1},
                        "finding_details": [
                            {
                                "id": "R3",
                                "severity": "minor",
                                "summary": "small cleanup",
                            }
                        ],
                        "acceptance": {"pass": 3, "fail": 0, "unverifiable": 0, "not_applicable": 0},
                    },
                ],
                "episode-a",
            ),
        )
        card_a_history = json.loads((reviews / "card-a.history.json").read_text(encoding="utf-8"))
        card_a_history["rescue_budget"] = {"limit": 5, "used": 1, "remaining": 4, "exhausted": False}
        write_json(reviews / "card-a.history.json", card_a_history)
        write_json(
            reviews / "card-b.history.json",
            history(
                "card-b",
                [
                    {
                        "review_cycle": 1,
                        "result": "go",
                        "reviewed_at": "2026-07-11T00:00:12Z",
                        "verdict_path": ".runtime/changerail/reviews/card-b.json",
                        "findings": {"blocker": 0, "major": 0, "minor": 0},
                        "finding_details": [],
                        "acceptance": {"pass": 1, "fail": 0, "unverifiable": 0, "not_applicable": 0},
                    }
                ],
                "episode-b",
            ),
        )
        write_json(plans / "queue-1" / "status.json", queue_status())

        text = run([str(METRICS), "--runs-dir", str(runs), "--episodes-dir", str(episodes), "--reviews-dir", str(reviews), "--plans-dir", str(plans)])
        require_ok(text, "metrics text")
        if "first_pass_go_rate: 1/2" not in text.stdout or "findings_blocker: 1" not in text.stdout:
            raise AssertionError(f"unexpected text metrics: {text.stdout}")
        if "preflight_only: 1" not in text.stdout or "delivery_episodes: 4" not in text.stdout:
            raise AssertionError(f"preflight-only denominator accounting missing: {text.stdout}")
        if "episode-d attempts=1 ids=episode-d-run kinds=delivery card=card-d result=DELIVERED" not in text.stdout:
            raise AssertionError(f"canonical episode row missing: {text.stdout}")
        if "queues:" not in text.stdout or "queue-1 plan=example-plan result=DELIVERED" not in text.stdout:
            raise AssertionError(f"queue metrics were not reported: {text.stdout}")
        if "child_run_ids=run-1;run-2" not in text.stdout:
            raise AssertionError(f"queue child run references were not reported: {text.stdout}")
        if "child_episode_ids=episode-a;episode-b" not in text.stdout:
            raise AssertionError(f"queue child episode references were not reported: {text.stdout}")
        if "finding_ids=R1;R2;R3" not in text.stdout:
            raise AssertionError(f"prior no-go finding details were not surfaced: {text.stdout}")
        for expected in (
            "total_tokens=15",
            "cached_input_tokens=4",
            "uncached_input_tokens=6",
            "reasoning_tokens=2",
            "command_sample_observed=455",
            "command_sample_retained=50",
            "command_sample_limit=50",
            "command_sample_truncated=yes",
            "oversized_command_count=1",
            "largest_command_output_bytes=90000",
            "command_output_threshold_bytes=65536",
            "top_oversized_command=rg --count example openspec/specs:90000b:success_oversized",
            "slowest_commands=/bin/echo one:1.5s;/bin/echo two:0.25s",
            "review_timeline=1:no-go@2026-07-11T00:00:11Z;2:go@2026-07-11T00:00:19Z",
            "episode-a attempts=2 ids=run-0;run-1 kinds=delivery;recovery card=card-a result=DELIVERED preflight_only=no recovery_count=1 first_review=no-go latest_review=go review_cycles=2 wall_time_seconds=10 rescue_budget_limit=5 rescue_budget_used=1 rescue_budget_remaining=4 rescue_budget_exhausted=no",
            "episode-b attempts=1 ids=run-2 kinds=delivery card=card-b result=DELIVERED preflight_only=no recovery_count=0 first_review=go latest_review=go review_cycles=1 wall_time_seconds=10 rescue_budget_limit=unknown rescue_budget_used=unknown rescue_budget_remaining=unknown rescue_budget_exhausted=unknown",
            "episode-preflight attempts=1 ids=run-preflight kinds=preflight card=card-b result=PREFLIGHT_ONLY preflight_only=yes recovery_count=0 first_review=unknown latest_review=unknown review_cycles=unknown wall_time_seconds=1",
            "unknown attempts=1 ids=run-3 kinds=delivery card=card-c result=DELIVERED preflight_only=no recovery_count=0 first_review=unknown latest_review=unknown review_cycles=3 wall_time_seconds=10 rescue_budget_limit=3 rescue_budget_used=2 rescue_budget_remaining=1 rescue_budget_exhausted=no",
        ):
            if expected not in text.stdout:
                raise AssertionError(f"metrics text missing {expected}: {text.stdout}")

        json_result = run([str(METRICS), "--runs-dir", str(runs), "--episodes-dir", str(episodes), "--reviews-dir", str(reviews), "--plans-dir", str(plans), "--json"])
        require_ok(json_result, "metrics json")
        json_payload = json.loads(json_result.stdout)
        if json_payload["queue_aggregate"]["queues_delivered"] != 1:
            raise AssertionError(f"queue aggregate missing from JSON metrics: {json_result.stdout}")
        rows_by_episode = {row["episode_id"]: row for row in json_payload["rows"]}
        rows_by_card = {row["card_id"]: row for row in json_payload["rows"] if row["card_id"] != "card-b"}
        if rows_by_episode["episode-a"]["rescue_budget_used"] != "1":
            raise AssertionError(f"history rescue budget did not win in JSON metrics: {json_result.stdout}")
        if rows_by_card["card-c"]["rescue_budget_remaining"] != "1":
            raise AssertionError(f"run fallback rescue budget missing in JSON metrics: {json_result.stdout}")
        if rows_by_episode["episode-b"]["rescue_budget_limit"] != "unknown":
            raise AssertionError(f"legacy rescue budget should be unknown: {json_result.stdout}")
        if rows_by_episode["episode-a"]["oversized_command_count"] != "1":
            raise AssertionError(f"oversized command count missing in JSON metrics: {json_result.stdout}")
        if rows_by_episode["episode-b"]["largest_command_output_bytes"] != "unknown":
            raise AssertionError(f"legacy output metadata should be unknown: {json_result.stdout}")
        if rows_by_episode["episode-preflight"]["latest_review_result"] != "unknown":
            raise AssertionError(f"preflight-only row inherited unrelated card history: {json_result.stdout}")
        if rows_by_episode["episode-d"]["total_tokens"] != "3":
            raise AssertionError(f"canonical episode record was not consumed: {json_result.stdout}")
        if json_payload["aggregate"]["oversized_command_count"] != 1:
            raise AssertionError(f"oversized aggregate missing from JSON metrics: {json_result.stdout}")

        csv_result = run([str(METRICS), "--runs-dir", str(runs), "--episodes-dir", str(episodes), "--reviews-dir", str(reviews), "--plans-dir", str(plans), "--csv"])
        require_ok(csv_result, "metrics csv")
        lines = csv_result.stdout.splitlines()
        for header in (
            "total_tokens",
            "cached_input_tokens",
            "command_sample_observed",
            "command_sample_truncated",
            "oversized_command_count",
            "largest_command_output_bytes",
            "command_output_threshold_bytes",
            "top_oversized_command",
            "slowest_commands",
            "review_timeline",
            "rescue_budget_limit",
            "rescue_budget_used",
            "rescue_budget_remaining",
            "rescue_budget_exhausted",
        ):
            if not lines or header not in lines[0]:
                raise AssertionError(f"CSV header missing {header}: {csv_result.stdout}")
        if "episode-a,run-1,run-0;run-1,2,delivery;recovery,no,1,card-a,DELIVERED,10,10,4,6,5,2,15" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render derived/breakdown usage: {csv_result.stdout}")
        if "455,50,50,yes,1,90000,65536,rg --count example openspec/specs:90000b:success_oversized" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render output amplification metrics: {csv_result.stdout}")
        if "episode-b,run-2,run-2,1,delivery,no,0,card-b,DELIVERED,10,unknown,unknown,unknown,unknown,unknown,unknown" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render missing usage as unknown: {csv_result.stdout}")
        if "unknown,unknown,unknown,unknown,unknown,unknown" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render missing optional performance as unknown: {csv_result.stdout}")

    print("ok: delivery metrics smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
