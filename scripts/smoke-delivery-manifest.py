#!/usr/bin/env python3
"""Smoke checks for ChangeRail delivery manifest staging operations."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"
WRAPPER = ROOT / "bin" / "changerail-delivery-manifest"
TARGET = {
    "schema": "changerail.execution-target.v1",
    "id": "database-primary",
    "fingerprint": "sha256:" + ("1" * 64),
    "target_substitution_policy": "forbid",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
    raise AssertionError(f"{label} failed: {detail}")


def manifest_payload() -> dict[str, Any]:
    return {
        "schema": "changerail.delivery-manifest.v1",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": {"root": "/opt/changerail", "repository": "changerail"},
        "execution_target": dict(TARGET),
        "card": {
            "id": "harden-delivery-operations",
            "path": "openspec/board/3.inprogress/harden-delivery-operations.md",
            "status": "3.inprogress",
        },
        "changes": [
            {
                "slug": "harden-delivery-lifecycle-contract",
                "state": "active",
                "order": 1,
                "active_path": "openspec/changes/harden-delivery-lifecycle-contract",
            }
        ],
        "committable_paths": [
            {
                "path": "openspec/board/3.inprogress/harden-delivery-operations.md",
                "kind": "board",
                "phase": "ff",
                "operation": "rename",
                "source_path": "openspec/board/1.backlog/harden-delivery-operations.md",
                "target_path": "openspec/board/3.inprogress/harden-delivery-operations.md",
            },
            {
                "path": "obsolete.md",
                "kind": "docs",
                "phase": "do",
                "operation": "delete",
                "source_path": "obsolete.md",
            },
        ],
        "excluded_runtime_paths": [],
        "preexisting_dirty": [],
        "verification_summary": {
            "result": "passed",
            "summary": "focused manifest smoke checks passed",
            "commands": [
                {
                    "command": "python3 scripts/smoke-delivery-manifest.py",
                    "outcome": "passed",
                    "evidence": {
                        "id": "manifest-smoke",
                        "index_path": ".runtime/changerail/evidence/manifest-smoke/index.json",
                        "raw_output_path": ".runtime/changerail/evidence/manifest-smoke/outputs/manifest-smoke.txt",
                        "classification": "mandatory",
                    },
                }
            ],
        },
        "review_summary": {
            "result": "go",
            "summary": "schema fixture review summary",
            "review_cycle": 1,
            "verdict_path": ".runtime/changerail/reviews/harden-delivery-operations.json",
            "findings": {"blocker": 0, "major": 0, "minor": 0},
        },
        "final_card_state": {
            "path": "openspec/board/4.done/harden-delivery-operations.md",
            "status": "4.done",
            "result_summary": "finalized through scoped publish",
        },
    }


def helper_module() -> Any:
    spec = importlib.util.spec_from_file_location("changerail_delivery_manifest_smoke", HELPER)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load manifest helper module")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(HELPER.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def check_repository_identity_redaction() -> None:
    module = helper_module()
    cases = {
        "https://user:password@example.invalid/org/repo.git?access_token=secret-value": "https://example.invalid/org/repo.git",
        "https://ghp_secret@example.invalid/org/repo.git": "https://example.invalid/org/repo.git",
        "git@example.invalid:org/repo.git": "ssh://example.invalid/org/repo.git",
    }
    for raw, expected in cases.items():
        actual = module.sanitize_repository_identity(raw)
        if actual != expected:
            raise AssertionError(f"unexpected sanitized repository identity for {raw!r}: {actual!r}")
        for forbidden in ("user", "password", "secret-value", "ghp_secret", "git@"):
            if forbidden in actual:
                raise AssertionError(f"repository identity leaked {forbidden!r}: {actual!r}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(repo: Path, *args: str) -> None:
    require_ok(subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False), f"git {' '.join(args)}")


def check_derive_captures_execution_target(tmp: Path) -> None:
    repo = tmp / "target-repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "Smoke Test")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / ".changerail" / "execution-target.json", json.dumps(TARGET, ensure_ascii=True, indent=2) + "\n")
    write(repo / "openspec" / "board" / "3.inprogress" / "target-card.md", "# Target card\n\n## Status\n3.inprogress\n\n## Change 1: `target-change`\n")
    write(repo / "openspec" / "changes" / "archive" / "2026-08-17-target-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    result = run(
        [
            sys.executable,
            str(HELPER),
            "derive",
            "openspec/board/3.inprogress/target-card.md",
            "--workspace",
            str(repo),
            "--json",
        ]
    )
    require_ok(result, "derive target manifest")
    payload = json.loads(result.stdout)["data"]
    if payload.get("execution_target") != TARGET:
        raise AssertionError(f"derive did not capture execution target: {payload!r}")


def main() -> int:
    check_repository_identity_redaction()
    with tempfile.TemporaryDirectory(prefix="changerail-manifest-smoke-") as tmp:
        check_derive_captures_execution_target(Path(tmp))
        path = Path(tmp) / "manifest.json"
        path.write_text(json.dumps(manifest_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        require_ok(run([sys.executable, str(HELPER), "validate", str(path), "--json"]), "validate")
        require_ok(run([str(WRAPPER), "validate", str(path), "--json"]), "wrapper validate")
        result = run([sys.executable, str(HELPER), "staging-plan", str(path), "--json"])
        require_ok(result, "staging-plan")
        payload = json.loads(result.stdout)
        paths = payload.get("paths")
        expected = {
            "openspec/board/1.backlog/harden-delivery-operations.md",
            "openspec/board/3.inprogress/harden-delivery-operations.md",
            "obsolete.md",
        }
        if set(paths) != expected:
            raise AssertionError(f"unexpected staging paths: {paths!r}")
        result = run(
            [
                sys.executable,
                str(HELPER),
                "handoff-update",
                str(path),
                "--verification-result",
                "passed",
                "--verification-summary",
                "handoff-update smoke verification passed",
                "--verification-command",
                "python3 scripts/smoke-delivery-manifest.py",
                "--verification-outcome",
                "passed",
                "--verification-command-evidence-id",
                "manifest-smoke",
                "--verification-command-evidence-index",
                ".runtime/changerail/evidence/manifest-smoke/index.json",
                "--verification-command-output",
                ".runtime/changerail/evidence/manifest-smoke/outputs/manifest-smoke.txt",
                "--verification-command-classification",
                "mandatory",
                "--review-result",
                "go",
                "--review-summary",
                "handoff-update smoke review passed",
                "--review-cycle",
                "1",
                "--verdict-path",
                ".runtime/changerail/reviews/harden-delivery-operations.json",
                "--finding-blocker",
                "0",
                "--finding-major",
                "0",
                "--finding-minor",
                "0",
                "--final-card-path",
                "openspec/board/4.done/harden-delivery-operations.md",
                "--final-card-status",
                "4.done",
                "--final-result-summary",
                "finalized through scoped publish",
                "--json",
            ]
        )
        require_ok(result, "handoff-update")
        updated = json.loads(path.read_text(encoding="utf-8"))
        if updated["verification_summary"]["result"] != "passed" or updated["review_summary"]["result"] != "go":
            raise AssertionError(f"handoff summary was not updated: {updated!r}")
        evidence = updated["verification_summary"]["commands"][0].get("evidence")
        if not evidence or evidence.get("id") != "manifest-smoke":
            raise AssertionError(f"handoff evidence reference was not retained: {updated!r}")

    print("ok: delivery manifest smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
