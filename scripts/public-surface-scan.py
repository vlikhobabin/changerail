#!/usr/bin/env python3
"""Scan ChangeRail public files for non-generic local path leaks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA = "changerail.public-surface-scan.v1"
OPT_PATH_RE = re.compile(r"/opt/[A-Za-z0-9_-]+")
HOME_PATH_RE = re.compile(r"(?:/home|/Users)/[A-Za-z0-9._-]+|[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b[A-Z0-9_.-]*(?:TOKEN|SECRET|PASSWORD|API[_-]?KEY|ACCESS[_-]?KEY)[A-Z0-9_.-]*\b"
    r"\s*[:=]\s*[\"']?([A-Za-z0-9_./+=:-]{12,})"
)
ALLOWED_PLACEHOLDER_SECRET_VALUES = {
    "dummy-token-value",
    "example-secret-value",
    "example-token-value",
    "fake-token-value",
    "placeholder-secret",
    "placeholder-token",
    "raw-token",
    "redacted-secret",
    "secret-value",
}
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
    ".codex/config.toml",
    ".gitignore",
    ".mcp.json",
    "CHANGELOG.md",
    "CLAUDE.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "VERSION",
    "AGENTS.md",
    "AGENTS.shared.md",
    "mcp-npm-lock.json",
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
    kind: str
    value: str
    message: str
    ref: str | None = None


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


def allowed_opt_path(value: str, line_text: str, rel_path: str, *, history: bool = False) -> bool:
    if value in ALLOWED_OPT_PATHS:
        return True
    if value.startswith("/opt/example-"):
        return True
    if history and re.match(r"^/opt/(?:app|service)-[a-z0-9-]+$", value):
        return True
    if history and value == HISTORICAL_OPSX_PATH:
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


def allowed_home_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    tail = normalized.rstrip("/").split("/")[-1].lower()
    return tail.startswith("example") or tail in {"runner", "user"}


def allowed_secret_value(value: str) -> bool:
    lowered = value.lower()
    if len(value) < 12:
        return True
    return lowered in ALLOWED_PLACEHOLDER_SECRET_VALUES


def scan_text(text: str, rel: str, *, history: bool = False, ref: str | None = None) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        context = "\n".join(lines[max(0, index - 2) : min(len(lines), index + 1)])
        for match in OPT_PATH_RE.finditer(line):
            value = match.group(0)
            if not allowed_opt_path(value, context, rel, history=history):
                findings.append(
                    Finding(
                        path=rel,
                        line=index,
                        kind="path",
                        value=value,
                        message="non-generic /opt path is not allowlisted",
                        ref=ref,
                    )
                )
        for match in HOME_PATH_RE.finditer(line):
            value = match.group(0)
            if not allowed_home_path(value):
                findings.append(
                    Finding(
                        path=rel,
                        line=index,
                        kind="home-path",
                        value=value,
                        message="machine-local home path is not allowlisted",
                        ref=ref,
                    )
                )
        for match in SECRET_ASSIGNMENT_RE.finditer(line):
            value = match.group(1)
            if not allowed_secret_value(value):
                findings.append(
                    Finding(
                        path=rel,
                        line=index,
                        kind="secret",
                        value="<redacted:secret>",
                        message="token-like assignment is not allowed in public files",
                        ref=ref,
                    )
                )
    return findings


def scan_file(path: Path, root: Path) -> list[Finding]:
    if is_binary(path):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    rel = path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    return scan_text(text, rel)


def rel_scan_roots(paths: list[Path], root: Path) -> list[str]:
    roots: list[str] = []
    for path in paths:
        try:
            rel = path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
        except ValueError:
            continue
        roots.append(rel)
    return roots or list(DEFAULT_ROOTS)


def path_in_roots(path: str, roots: list[str]) -> bool:
    return any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots)


def scan_history(paths: list[Path], root: Path) -> list[Finding]:
    revs = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if revs.returncode != 0:
        return [
            Finding(
                path="<git-history>",
                line=0,
                kind="history",
                value="<unavailable>",
                message=(revs.stderr.strip() or "git rev-list failed"),
            )
        ]
    roots = rel_scan_roots(paths, root)
    findings: list[Finding] = []
    for ref in revs.stdout.splitlines():
        tree = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "-z", "--name-only", ref],
            capture_output=True,
            check=False,
        )
        if tree.returncode != 0:
            continue
        for raw_path in tree.stdout.split(b"\0"):
            if not raw_path:
                continue
            rel = raw_path.decode("utf-8", "replace")
            if any(part in SKIP_DIRS for part in Path(rel).parts):
                continue
            if not path_in_roots(rel, roots):
                continue
            blob = subprocess.run(
                ["git", "-C", str(root), "show", f"{ref}:{rel}"],
                capture_output=True,
                check=False,
            )
            if blob.returncode != 0 or b"\x00" in blob.stdout[:4096]:
                continue
            try:
                text = blob.stdout.decode("utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(scan_text(text, rel, history=True, ref=ref[:12]))
    return findings


def scan(paths: list[Path], root: Path, *, history: bool = False) -> dict[str, object]:
    files = iter_files(paths)
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root))
    if history:
        findings.extend(scan_history(paths, root))
    return {
        "schema": SCHEMA,
        "root": str(root),
        "history": history,
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
        secret_value = "A1B2" + "C3D4" + "E5F6" + "G7H8"
        secret = root / "secret.md"
        secret.write_text("API_TOKEN = \"" + secret_value + "\"\n", encoding="utf-8")
        home = root / "home.md"
        home.write_text("Private home /Users/" + "customer-alpha/project must fail.\n", encoding="utf-8")
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
        secret_report = scan([secret], root)
        if secret_report["summary"]["status"] != "fail" or secret_value in json.dumps(secret_report):
            print(json.dumps(secret_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        broad_placeholder_value = "real-token-" + "A1B2C3D4E5F6"
        broad_placeholder = root / "broad-placeholder.md"
        broad_placeholder.write_text("SERVICE_TOKEN = \"" + broad_placeholder_value + "\"\n", encoding="utf-8")
        broad_placeholder_report = scan([broad_placeholder], root)
        if broad_placeholder_report["summary"]["status"] != "fail" or broad_placeholder_value in json.dumps(
            broad_placeholder_report
        ):
            print(json.dumps(broad_placeholder_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        placeholder = root / "placeholder.md"
        placeholder.write_text("ACCESS_TOKEN = \"secret-value\"\n", encoding="utf-8")
        placeholder_report = scan([placeholder], root)
        if placeholder_report["summary"]["status"] != "pass":
            print(json.dumps(placeholder_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        home_report = scan([home], root)
        if home_report["summary"]["status"] != "fail":
            print(json.dumps(home_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        default_paths = [root / path for path in DEFAULT_ROOTS]
        default_mcp_secret_value = "MCP1" + "TOKEN2" + "VALUE3"
        default_mcp = root / ".mcp.json"
        default_mcp.write_text("MCP_API_TOKEN = \"" + default_mcp_secret_value + "\"\n", encoding="utf-8")
        default_report = scan(default_paths, root)
        default_mcp_findings = [
            finding
            for finding in default_report["findings"]
            if finding["path"] == ".mcp.json" and finding["kind"] == "secret"
        ]
        if (
            default_report["summary"]["status"] != "fail"
            or not default_mcp_findings
            or default_mcp_secret_value in json.dumps(default_report)
        ):
            print(json.dumps(default_report, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        history_root = root / "history"
        history_root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=history_root, check=True)
        subprocess.run(["git", "config", "user.email", "scan@example.invalid"], cwd=history_root, check=True)
        subprocess.run(["git", "config", "user.name", "ChangeRail Scan"], cwd=history_root, check=True)
        history_file = history_root / "README.md"
        history_file.write_text("PASSWORD = \"" + secret_value + "\"\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=history_root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "add secret"], cwd=history_root, check=True)
        history_file.write_text("clean\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=history_root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "remove secret"], cwd=history_root, check=True)
        history_report = scan([history_file], history_root, history=True)
        if history_report["summary"]["status"] != "fail" or secret_value in json.dumps(history_report):
            print(json.dumps(history_report, ensure_ascii=False, indent=2), file=sys.stderr)
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
    parser.add_argument("--history", action="store_true", help="Scan reachable git history for public-safety leaks.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    root = args.root.resolve(strict=False)
    paths = [path if path.is_absolute() else root / path for path in args.paths]
    if not paths:
        paths = [root / path for path in DEFAULT_ROOTS]
    report = scan(paths, root, history=args.history)
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
            ref = f"{finding['ref']}:" if finding.get("ref") else ""
            print(
                f"{ref}{finding['path']}:{finding['line']}: "
                f"{finding['kind']} {finding['value']}: {finding['message']}"
            )
    return 0 if report["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
