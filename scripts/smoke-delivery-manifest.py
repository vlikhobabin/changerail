#!/usr/bin/env python3
"""Smoke checks for ChangeRail delivery manifest staging operations."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"


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
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-manifest-smoke-") as tmp:
        path = Path(tmp) / "manifest.json"
        path.write_text(json.dumps(manifest_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        require_ok(run([sys.executable, str(HELPER), "validate", str(path), "--json"]), "validate")
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

    print("ok: delivery manifest smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
