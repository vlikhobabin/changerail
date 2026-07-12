#!/usr/bin/env python3
"""Scan ChangeRail public files for non-generic local path leaks."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA = "changerail.public-surface-scan.v1"
OPT_PATH_RE = re.compile(r"/opt/[A-Za-z0-9_-]+")
ALLOWED_OPT_PATHS = {
    "/opt/changerail",
    "/opt/example-project",
    "/opt/example-a",
    "/opt/example-b",
}
HISTORICAL_OPSX_HINTS = (
    "history",
    "historical",
    "legacy",
    "migration",
    "migrate",
    "old",
    "pre-rename",
    "rename",
    "previous",
    "compatibility",
    "stale",
)
HISTORICAL_OPSX_PATH = "/opt/" + "opsx"
PRE_RENAME_ARCHIVE_PREFIX = "openspec/changes/archive/2026-07-08-"
SKIP_DIRS = {
    ".git",
    ".runtime",
    "internal",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
}
DEFAULT_ROOTS = (
    "README.md",
    "AGENTS.md",
    "AGENTS.shared.md",
    "docs",
    "skills",
    "claude",
    "schemas",
    "scripts",
    "bin",
    "templates",
    "openspec",
    ".github",
)


@dataclass
class Finding:
    path: str
    line: int
    value: str
    message: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in chunk


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        for child in path.rglob("*"):
            if any(part in SKIP_DIRS for part in child.parts):
                continue
            if child.is_file():
                files.append(child)
    return sorted(set(files))


def allowed_opt_path(value: str, line_text: str, rel_path: str) -> bool:
    if value in ALLOWED_OPT_PATHS:
        return True
    if value.startswith("/opt/example-"):
        return True
    lowered = line_text.lower()
    lowered_path = rel_path.lower()
    if value == HISTORICAL_OPSX_PATH and (
        any(hint in lowered for hint in HISTORICAL_OPSX_HINTS)
        or "opsx" in lowered_path
        or "migration" in lowered_path
        or "drift-gate" in lowered_path
        or lowered_path.startswith("openspec/board/4.done/")
        or lowered_path.startswith(PRE_RENAME_ARCHIVE_PREFIX)
    ):
        return True
    return False


def scan_file(path: Path, root: Path) -> list[Finding]:
    if is_binary(path):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    rel = path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    findings: list[Finding] = []
    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        context = "\n".join(lines[max(0, index - 2) : min(len(lines), index + 1)])
        for match in OPT_PATH_RE.finditer(line):
            value = match.group(0)
            if not allowed_opt_path(value, context, rel):
                findings.append(
                    Finding(
                        path=rel,
                        line=index,
                        value=value,
                        message="non-generic /opt path is not allowlisted",
                    )
                )
    return findings


def scan(paths: list[Path], root: Path) -> dict[str, object]:
    files = iter_files(paths)
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root))
    return {
        "schema": SCHEMA,
        "root": str(root),
        "summary": {
            "status": "fail" if findings else "pass",
            "files_scanned": len(files),
            "findings": len(findings),
        },
        "findings": [asdict(finding) for finding in findings],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        allowed = root / "allowed.md"
        allowed.write_text(
            "\n".join(
                [
                    "Use /opt/changerail.",
                    "Use /opt/example-project.",
                    "Historical migration from /opt/opsx is documented.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        bad = root / "bad.md"
        bad.write_text("Private path " + "/opt/" + "customer-alpha" + " must fail.\n", encoding="utf-8")
        archive_leak = root / "openspec" / "changes" / "archive" / "2026-07-12-example" / "tasks.md"
        archive_leak.parent.mkdir(parents=True)
        archive_leak.write_text("Private archive path " + "/opt/" + "customer-beta" + " must fail.\n", encoding="utf-8")
        allowed_report = scan([allowed], root)
        if allowed_report["summary"]["status"] != "pass":
            print(json.dumps(allowed_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        bad_report = scan([bad], root)
        if bad_report["summary"]["status"] != "fail":
            print(json.dumps(bad_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        default_paths = [root / path for path in DEFAULT_ROOTS]
        default_report = scan(default_paths, root)
        if default_report["summary"]["status"] != "fail":
            print(json.dumps(default_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    print("PUBLIC_SURFACE_SCAN_SELF_TEST_OK")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to scan.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    root = args.root.resolve(strict=False)
    paths = [path if path.is_absolute() else root / path for path in args.paths]
    if not paths:
        paths = [root / path for path in DEFAULT_ROOTS]
    report = scan(paths, root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "summary: "
            f"{summary['status']} "
            f"({summary['files_scanned']} files scanned, {summary['findings']} findings)"
        )
        for finding in report["findings"]:
            print(f"{finding['path']}:{finding['line']}: {finding['value']}: {finding['message']}")
    return 0 if report["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
