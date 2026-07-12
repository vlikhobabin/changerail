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


def main() -> int:
    check_repository_identity_redaction()
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
