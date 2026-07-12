#!/usr/bin/env python3
"""Smoke-test ChangeRail OpenSpec archive diagnostics for already-synced specs."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENSPEC = ROOT / "bin" / "openspec"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_archive(project: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["OPENSPEC_WORKDIR"] = str(project)
    return subprocess.run(
        [str(OPENSPEC), "archive", "duplicate-requirement", "--yes", *extra],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )


def make_project(root: Path) -> Path:
    project = root / "project"
    write(project / "openspec" / "config.yaml", "schema: spec-driven\n")
    write(
        project / "openspec" / "specs" / "example" / "spec.md",
        """# example Specification

## Purpose
Temporary smoke capability.
## Requirements
### Requirement: Duplicate behavior
The example capability MUST already contain this requirement.

#### Scenario: Existing requirement
- **WHEN** the smoke fixture is created
- **THEN** the main spec already has the requirement
""",
    )
    write(project / "openspec" / "changes" / "duplicate-requirement" / ".openspec.yaml", "schema: spec-driven\n")
    write(
        project / "openspec" / "changes" / "duplicate-requirement" / "proposal.md",
        "# duplicate-requirement\n\n## Why\n\nSmoke fixture.\n",
    )
    write(
        project / "openspec" / "changes" / "duplicate-requirement" / "tasks.md",
        "## 1. Tasks\n\n- [x] 1.1 Complete fixture task.\n",
    )
    write(
        project
        / "openspec"
        / "changes"
        / "duplicate-requirement"
        / "specs"
        / "example"
        / "spec.md",
        """## ADDED Requirements

### Requirement: Duplicate behavior
The example capability MUST already contain this requirement.

#### Scenario: Existing requirement
- **WHEN** the smoke fixture is archived
- **THEN** duplicate sync is detected
""",
    )
    return project


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp))
        result = run_archive(project)
        output = result.stdout + result.stderr
        if result.returncode == 0:
            sys.stderr.write("archive without --skip-specs unexpectedly exited 0\n")
            sys.stderr.write(output)
            return 1
        if "ChangeRail diagnostic" not in output or "--skip-specs" not in output:
            sys.stderr.write("archive diagnostic did not mention ChangeRail diagnostic and --skip-specs\n")
            sys.stderr.write(output)
            return 1

        project = make_project(Path(tmp) / "skip")
        skip_result = run_archive(project, "--skip-specs")
        skip_output = skip_result.stdout + skip_result.stderr
        if skip_result.returncode != 0:
            sys.stderr.write("archive with --skip-specs failed\n")
            sys.stderr.write(skip_output)
            return 1
        if "ChangeRail diagnostic" in skip_output:
            sys.stderr.write("archive with --skip-specs emitted duplicate diagnostic unexpectedly\n")
            sys.stderr.write(skip_output)
            return 1

    print("SMOKE_OPENSPEC_ARCHIVE_DIAGNOSTICS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
