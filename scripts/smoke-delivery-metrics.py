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
) -> dict[str, Any]:
    record = {
        "schema": "changerail.delivery-run.v1",
        "run_id": run_id,
        "updated_at": "2026-07-11T00:00:10Z",
        "workspace": {"root": "/opt/changerail"},
        "card": {"id": card_id, "path": f"openspec/board/3.inprogress/{card_id}.md"},
        "phase": "terminal",
        "result": result,
        "terminal_outcome": result,
        "timestamps": {"started_at": "2026-07-11T00:00:00Z", "ended_at": "2026-07-11T00:00:10Z"},
        "command": {"argv": ["bin/codex", "exec"], "launcher": "bin/codex", "stdin": "closed", "json": True},
        "usage": usage,
    }
    if performance is not None:
        record["performance"] = performance
    return record


def history(card_id: str, cycles: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "changerail.review-cycle-history.v1",
        "updated_at": "2026-07-11T00:00:20Z",
        "workspace": {"root": "/opt/changerail"},
        "card": {"id": card_id, "path": f"openspec/board/3.inprogress/{card_id}.md"},
        "cycles": cycles,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-delivery-metrics-") as tmp:
        root = Path(tmp)
        runs = root / "runs"
        reviews = root / "reviews"
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
                    "file_change_count": 7,
                    "slowest_commands": [
                        {"command": "/bin/echo one", "duration_seconds": 1.5, "exit_code": 0},
                        {"command": "/bin/echo two", "duration_seconds": 0.25, "exit_code": 0},
                    ],
                    "review": {
                        "cycle_count": 2,
                        "first_review_latency_seconds": 11.0,
                        "time_to_final_go_seconds": 19.0,
                    },
                },
            ),
        )
        write_json(
            runs / "run-2" / "status.json",
            run_record("run-2", "card-b", "DELIVERED", {"available": False, "reason": "usage not observed"}),
        )
        write_json(
            reviews / "card-a.history.json",
            history(
                "card-a",
                [
                    {
                        "review_cycle": 1,
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
            ),
        )
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
            ),
        )

        text = run([str(METRICS), "--runs-dir", str(runs), "--reviews-dir", str(reviews)])
        require_ok(text, "metrics text")
        if "first_pass_go_rate: 1/2" not in text.stdout or "findings_blocker: 1" not in text.stdout:
            raise AssertionError(f"unexpected text metrics: {text.stdout}")
        if "finding_ids=R1;R2;R3" not in text.stdout:
            raise AssertionError(f"prior no-go finding details were not surfaced: {text.stdout}")
        for expected in (
            "total_tokens=15",
            "cached_input_tokens=4",
            "uncached_input_tokens=6",
            "reasoning_tokens=2",
            "slowest_commands=/bin/echo one:1.5s;/bin/echo two:0.25s",
            "review_timeline=1:no-go@2026-07-11T00:00:11Z;2:go@2026-07-11T00:00:19Z",
        ):
            if expected not in text.stdout:
                raise AssertionError(f"metrics text missing {expected}: {text.stdout}")

        csv_result = run([str(METRICS), "--runs-dir", str(runs), "--reviews-dir", str(reviews), "--csv"])
        require_ok(csv_result, "metrics csv")
        lines = csv_result.stdout.splitlines()
        for header in ("total_tokens", "cached_input_tokens", "slowest_commands", "review_timeline"):
            if not lines or header not in lines[0]:
                raise AssertionError(f"CSV header missing {header}: {csv_result.stdout}")
        if "run-1,card-a,DELIVERED,10.5,10,4,6,5,2,15" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render derived/breakdown usage: {csv_result.stdout}")
        if "run-2,card-b,DELIVERED,10,unknown,unknown,unknown,unknown,unknown,unknown" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render missing usage as unknown: {csv_result.stdout}")
        if "unknown,unknown,unknown,unknown,unknown,unknown" not in csv_result.stdout:
            raise AssertionError(f"CSV did not render missing optional performance as unknown: {csv_result.stdout}")

    print("ok: delivery metrics smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
