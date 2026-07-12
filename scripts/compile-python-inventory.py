#!/usr/bin/env python3
"""Compile tracked ChangeRail Python helpers discovered from git inventory."""

from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "bin", "scripts"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip() or "git ls-files failed"
        raise RuntimeError(detail)
    return [ROOT / raw.decode("utf-8", errors="surrogateescape") for raw in result.stdout.split(b"\x00") if raw]


def is_python(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("scripts/") and path.suffix == ".py":
        return True
    if not rel.startswith("bin/") or path.name.startswith("."):
        return False
    try:
        first = path.open("rb").readline(200)
    except OSError:
        return False
    return first.startswith(b"#!/") and b"python" in first


def main() -> int:
    files = sorted(path for path in git_files() if is_python(path))
    if not files:
        sys.stderr.write("no tracked Python files discovered under bin/ or scripts/\n")
        return 1
    failures = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures += 1
            sys.stderr.write(f"FAIL {rel}: {exc.msg}\n")
        else:
            print(f"ok {rel}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
