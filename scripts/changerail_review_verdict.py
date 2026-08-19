#!/usr/bin/env python3
"""Validate ChangeRail review verdicts and compute working-tree freshness fingerprints.

The review verdict (`changerail.review-verdict.v1`) is the machine gate between
`$changerail-do` and `$changerail-pub`: a card publish that is part of the review-gated
flow requires a verdict that is valid, `result: go`, and fresh against the
current working tree. This helper provides:

- `validate <verdict.json>`: schema-shape plus consistency validation
  (blocker findings force `no-go`; `no-go` requires a blocker or a failed
  acceptance criterion; reviewer independence attestation is required), with
  optional `--check-fresh` freshness comparison;
- `fingerprint --workspace <root>`: deterministic sha256 fingerprint over
  `git status --porcelain`, `git diff HEAD` and untracked non-ignored file
  content, plus the Git tree SHA that would be committed for that reviewed
  working tree, shared by the reviewer that embeds it and every consumer that
  re-checks it;
- `preflight <card>`: deterministic manifest, board, scope, strict-check,
  risk-route and rescue-complexity gate before any LLM payload review.

Exit codes follow the shared ChangeRail helper convention: 0 valid, 1 validation
failed, 2 input error.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from changerail_contract_schema import validate_with_schema

SCHEMA_ID = "changerail.review-verdict.v1"
SCHEMA_FILE = "changerail-review-verdict.schema.json"
ACCEPTED_SCHEMA_IDS = (SCHEMA_ID,)
REVIEWER_KINDS = ("codex-exec", "claude-subagent", "external-session", "operator")
RESULTS = ("go", "no-go")
ACCEPTANCE_VERDICTS = ("pass", "fail", "unverifiable", "not-applicable")
SEVERITIES = ("blocker", "major", "minor")
AREAS = ("evidence", "code", "tests", "scope", "docs", "process")
FINDING_ID_RE = re.compile(r"^R[0-9]+$")
FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TREE_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TOP_LEVEL_KEYS = {
    "schema",
    "reviewed_at",
    "card",
    "workspace",
    "reviewer",
    "result",
    "review_cycle",
    "acceptance",
    "findings",
    "evidence_audit",
    "notes",
}
READ_CHUNK_SIZE = 1024 * 1024
EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
CACHE_SCHEMA = "changerail.review-fingerprint-cache.v1"
CACHE_VERSION = 1
FINGERPRINT_KEYS = ("head_commit", "tree_sha", "diff_fingerprint")


class VerdictError(Exception):
    """Validation or input failure with an explicit exit code."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _require_str(errors: list[str], data: dict[str, Any], field: str, label: str) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{field} must be a non-empty string")
        return None
    return value


def _validate_verdict(data: Any) -> list[str]:
    errors = validate_with_schema(data, SCHEMA_FILE)
    if errors:
        return errors
    return _validate_verdict_semantics(data)


def _validate_verdict_semantics(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    has_failed_acceptance = False
    acceptance = data.get("acceptance")
    for entry in acceptance:
        if entry.get("verdict") == "fail":
            has_failed_acceptance = True

    has_blocker = False
    findings = data.get("findings")
    seen_ids: set[str] = set()
    for index, entry in enumerate(findings):
        label = f"findings[{index}]"
        finding_id = entry.get("id")
        if finding_id in seen_ids:
            errors.append(f"{label}.id duplicates {finding_id}")
        else:
            seen_ids.add(finding_id)
        if entry.get("severity") == "blocker":
            has_blocker = True

    result = data.get("result")
    if result == "go" and (has_blocker or has_failed_acceptance):
        errors.append("result 'go' is inconsistent with blocker findings or failed acceptance criteria")
    if result == "no-go" and not (has_blocker or has_failed_acceptance):
        errors.append("result 'no-go' requires at least one blocker finding or one failed acceptance criterion")
    return errors


def _git_env(extra: dict[str, str] | None = None) -> dict[str, str] | None:
    if extra is None:
        return None
    env = os.environ.copy()
    env.update(extra)
    return env


def _git_output(workspace: Path, args: list[str], *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        text=True,
        check=False,
        env=_git_env(env),
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise VerdictError(f"git {' '.join(args)}: {detail}", exit_code=2)
    return result.stdout


def _git_output_bytes(
    workspace: Path,
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    input_data: bytes | None = None,
) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(workspace), *args],
        capture_output=True,
        check=False,
        env=_git_env(env),
        input=input_data,
    )
    if result.returncode != 0:
        detail = (
            result.stderr.decode("utf-8", errors="replace").strip()
            or result.stdout.decode("utf-8", errors="replace").strip()
            or "git command failed"
        )
        raise VerdictError(f"git {' '.join(args)}: {detail}", exit_code=2)
    return result.stdout


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timed(timings: list[dict[str, Any]], phase: str, func: Any) -> Any:
    start = time.perf_counter()
    try:
        return func()
    finally:
        timings.append({"phase": phase, "duration_ms": round((time.perf_counter() - start) * 1000, 3)})


def _hash_untracked_files(digest: Any, workspace: Path) -> None:
    output = _git_output_bytes(workspace, ["ls-files", "--others", "--exclude-standard", "-z"])
    paths = sorted(path for path in output.split(b"\x00") if path)
    for raw_path in paths:
        path = workspace / os.fsdecode(raw_path)
        digest.update(b"untracked:path\x00")
        digest.update(raw_path)
        digest.update(b"\x00")
        try:
            if path.is_symlink():
                digest.update(b"untracked:symlink\x00")
                digest.update(os.fsencode(os.readlink(path)))
                digest.update(b"\x00")
                continue
            if not path.is_file():
                digest.update(b"untracked:missing-or-non-regular\x00")
                continue
            digest.update(b"untracked:file\x00")
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    digest.update(chunk)
            digest.update(b"\x00")
        except FileNotFoundError:
            digest.update(b"untracked:missing\x00")
        except OSError as exc:
            raise VerdictError(f"untracked file cannot be read: {path}: {exc}", exit_code=2) from exc


def _head_commit(workspace: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    inside = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    if inside.returncode == 0 and inside.stdout.strip() == "true":
        return "unborn"
    detail = result.stderr.strip() or result.stdout.strip() or "HEAD cannot be resolved"
    raise VerdictError(f"git rev-parse --verify HEAD: {detail}", exit_code=2)


def _changed_paths_from_status(status: bytes) -> list[bytes]:
    records = [record for record in status.split(b"\x00") if record]
    paths: set[bytes] = set()
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4:
            raise VerdictError("git status produced an invalid porcelain record", exit_code=2)
        code = record[:2].decode("ascii", errors="replace")
        if "U" in code:
            raise VerdictError("unmerged paths cannot be fingerprinted safely", exit_code=2)
        path = record[3:]
        if not path:
            raise VerdictError("git status produced an empty changed path", exit_code=2)
        paths.add(path)
        if "R" in code or "C" in code:
            index += 1
            if index >= len(records):
                raise VerdictError(f"git status missing source path for {code}", exit_code=2)
            paths.add(records[index])
        index += 1
    return sorted(paths)


def _compute_reviewed_tree_reference(workspace: Path, head_commit: str) -> str:
    with tempfile.TemporaryDirectory(prefix="changerail-review-index-") as raw:
        index_path = Path(raw) / "index"
        env = {"GIT_INDEX_FILE": str(index_path)}
        if head_commit != "unborn":
            _git_output(workspace, ["read-tree", head_commit], env=env)
        _git_output(workspace, ["add", "-A"], env=env)
        tree_sha = _git_output(workspace, ["write-tree"], env=env).strip()
    if not TREE_SHA_RE.fullmatch(tree_sha):
        raise VerdictError("reviewed tree SHA could not be computed", exit_code=2)
    return tree_sha


def _compute_reviewed_tree_optimized(workspace: Path, head_commit: str, changed_paths: list[bytes]) -> str:
    if not changed_paths:
        if head_commit == "unborn":
            return EMPTY_TREE_SHA
        return _git_output(workspace, ["rev-parse", f"{head_commit}^{{tree}}"]).strip()
    pathspecs = b"".join(path + b"\x00" for path in changed_paths)
    with tempfile.TemporaryDirectory(prefix="changerail-review-index-") as raw:
        index_path = Path(raw) / "index"
        env = {"GIT_INDEX_FILE": str(index_path), "GIT_LITERAL_PATHSPECS": "1"}
        if head_commit != "unborn":
            _git_output(workspace, ["read-tree", head_commit], env=env)
        _git_output_bytes(
            workspace,
            ["add", "-A", "--pathspec-from-file=-", "--pathspec-file-nul"],
            env=env,
            input_data=pathspecs,
        )
        tree_sha = _git_output(workspace, ["write-tree"], env=env).strip()
    if not TREE_SHA_RE.fullmatch(tree_sha):
        raise VerdictError("optimized reviewed tree SHA could not be computed", exit_code=2)
    return tree_sha


def compute_reviewed_tree(
    workspace: Path,
    head_commit: str,
    changed_paths: list[bytes] | None = None,
    diagnostics: dict[str, Any] | None = None,
    timings: list[dict[str, Any]] | None = None,
) -> str:
    timings = timings if timings is not None else []
    if changed_paths is None:
        tree_sha = _timed(timings, "reviewed-tree-construction", lambda: _compute_reviewed_tree_reference(workspace, head_commit))
        if diagnostics is not None:
            diagnostics["tree_builder"] = {"mode": "reference", "changed_path_count": None, "full_index_refresh": True}
        return tree_sha
    try:
        tree_sha = _timed(
            timings,
            "reviewed-tree-construction",
            lambda: _compute_reviewed_tree_optimized(workspace, head_commit, changed_paths),
        )
        if diagnostics is not None:
            diagnostics["tree_builder"] = {
                "mode": "optimized",
                "changed_path_count": len(changed_paths),
                "full_index_refresh": False,
            }
        return tree_sha
    except VerdictError as exc:
        tree_sha = _timed(timings, "reviewed-tree-reference-fallback", lambda: _compute_reviewed_tree_reference(workspace, head_commit))
        if diagnostics is not None:
            diagnostics["tree_builder"] = {
                "mode": "fallback",
                "changed_path_count": len(changed_paths),
                "full_index_refresh": True,
                "reason": str(exc)[:500],
            }
        return tree_sha


def _path_metadata_fingerprint(workspace: Path, head_commit: str, status: bytes, changed_paths: list[bytes]) -> str:
    digest = hashlib.sha256()
    digest.update(b"head\x00")
    digest.update(head_commit.encode("utf-8"))
    digest.update(b"\x00status-v1-z\x00")
    digest.update(status)
    for raw_path in changed_paths:
        path = os.fsdecode(raw_path)
        absolute = workspace / path
        digest.update(b"\x00path\x00")
        digest.update(raw_path)
        try:
            stat_result = absolute.lstat()
        except FileNotFoundError:
            digest.update(b"\x00missing")
            continue
        digest.update(f"\x00mode:{stat_result.st_mode:o}\x00size:{stat_result.st_size}\x00".encode("ascii"))
        if absolute.is_symlink():
            digest.update(b"symlink\x00")
            digest.update(os.fsencode(os.readlink(absolute)))
        elif absolute.is_file():
            digest.update(b"file\x00")
            digest.update(_git_output_bytes(workspace, ["hash-object", f"--path={path}", "--", path]).strip())
        else:
            raise VerdictError(f"changed path is not a regular file or symlink: {path}", exit_code=2)
    return f"sha256:{digest.hexdigest()}"


def _cache_path(workspace: Path) -> Path:
    return workspace / ".runtime" / "changerail" / "review-fingerprint-cache" / "fingerprint.json"


def _load_cache(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return {"malformed": True}
    return data if isinstance(data, dict) else {"malformed": True}


def _cache_status(
    data: dict[str, Any] | None,
    workspace: Path,
    head_commit: str,
    status: bytes,
    metadata_fingerprint: str,
) -> str:
    if data is None:
        return "miss"
    if data.get("malformed"):
        return "malformed"
    if (
        data.get("schema") == CACHE_SCHEMA
        and data.get("version") == CACHE_VERSION
        and data.get("workspace_root") == str(workspace)
        and data.get("head_commit") == head_commit
        and data.get("status_fingerprint") == f"sha256:{hashlib.sha256(status).hexdigest()}"
        and data.get("changed_path_metadata_fingerprint") == metadata_fingerprint
        and TREE_SHA_RE.fullmatch(str(data.get("tree_sha", "")))
        and FINGERPRINT_RE.fullmatch(str(data.get("diff_fingerprint", "")))
    ):
        return "hit"
    return "stale"


def _write_cache(
    path: Path,
    *,
    workspace: Path,
    head_commit: str,
    status: bytes,
    metadata_fingerprint: str,
    tree_sha: str,
    diff_fingerprint: str,
    tree_builder: dict[str, Any],
) -> None:
    payload = {
        "schema": CACHE_SCHEMA,
        "version": CACHE_VERSION,
        "created_at": _utc_now(),
        "workspace_root": str(workspace),
        "head_commit": head_commit,
        "status_fingerprint": f"sha256:{hashlib.sha256(status).hexdigest()}",
        "changed_path_metadata_fingerprint": metadata_fingerprint,
        "tree_sha": tree_sha,
        "diff_fingerprint": diff_fingerprint,
        "tree_builder": tree_builder,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _diff_fingerprint(workspace: Path, head_commit: str, status: bytes, tree_sha: str, timings: list[dict[str, Any]]) -> str:
    diff = b"" if head_commit == "unborn" else _timed(
        timings,
        "tracked-diff",
        lambda: _git_output_bytes(workspace, ["diff", "HEAD", "--no-color", "--binary"]),
    )
    digest = hashlib.sha256()
    digest.update(b"status-v1-z\x00")
    digest.update(status)
    digest.update(b"\x00tracked-diff\x00")
    digest.update(diff)
    digest.update(b"\x00reviewed-tree\x00")
    digest.update(tree_sha.encode("ascii"))
    _timed(timings, "untracked-content-hashing", lambda: _hash_untracked_files(digest, workspace))
    _timed(timings, "fingerprint-assembly", lambda: digest.update(b"\x00"))
    return f"sha256:{digest.hexdigest()}"


def compute_fingerprint(
    workspace: Path,
    *,
    use_cache: bool = False,
    diagnostics: bool = False,
    force_reference: bool = False,
) -> dict[str, Any]:
    if not workspace.is_dir():
        raise VerdictError(f"workspace directory cannot be read: {workspace}", exit_code=2)
    workspace = workspace.resolve(strict=False)
    timings: list[dict[str, Any]] = []
    helper_diagnostics: dict[str, Any] = {}
    head_commit = _timed(timings, "head-commit", lambda: _head_commit(workspace))
    status = _timed(
        timings,
        "changed-path-discovery",
        lambda: _git_output_bytes(workspace, ["status", "--porcelain=v1", "-z", "--untracked-files=all"]),
    )
    changed_paths = _changed_paths_from_status(status)
    metadata_fingerprint = _timed(
        timings,
        "changed-path-metadata",
        lambda: _path_metadata_fingerprint(workspace, head_commit, status, changed_paths),
    )
    cache = _load_cache(_cache_path(workspace)) if use_cache and not force_reference else None
    cache_state = (
        "disabled"
        if not use_cache or force_reference
        else _cache_status(cache, workspace, head_commit, status, metadata_fingerprint)
    )
    if cache_state == "hit" and cache is not None:
        tree_sha = str(cache["tree_sha"])
        diff_fingerprint = str(cache["diff_fingerprint"])
        helper_diagnostics["tree_builder"] = {"mode": "cache", "changed_path_count": len(changed_paths), "full_index_refresh": False}
    else:
        paths = None if force_reference else changed_paths
        tree_sha = compute_reviewed_tree(workspace, head_commit, paths, helper_diagnostics, timings)
        diff_fingerprint = _diff_fingerprint(workspace, head_commit, status, tree_sha, timings)
        if use_cache and not force_reference:
            try:
                _write_cache(
                    _cache_path(workspace),
                    workspace=workspace,
                    head_commit=head_commit,
                    status=status,
                    metadata_fingerprint=metadata_fingerprint,
                    tree_sha=tree_sha,
                    diff_fingerprint=diff_fingerprint,
                    tree_builder=helper_diagnostics.get("tree_builder", {}),
                )
            except OSError:
                cache_state = "write-failed"
    result: dict[str, Any] = {
        "workspace": str(workspace),
        "head_commit": head_commit,
        "tree_sha": tree_sha,
        "diff_fingerprint": diff_fingerprint,
    }
    if diagnostics:
        result["diagnostics"] = {
            "cache": {
                "schema": CACHE_SCHEMA,
                "status": cache_state,
                "path": os.path.relpath(_cache_path(workspace), workspace),
            },
            "tree_builder": helper_diagnostics.get("tree_builder", {}),
            "timings": timings,
        }
    return result


def _load_verdict(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerdictError(f"verdict cannot be read: {exc}", exit_code=2) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise VerdictError(f"verdict JSON is invalid: {exc}", exit_code=2) from exc


def _cmd_validate(args: argparse.Namespace) -> int:
    data = _load_verdict(args.verdict)
    errors = _validate_verdict(data)
    freshness: dict[str, Any] | None = None
    if not errors and args.check_fresh:
        current = compute_fingerprint(Path(args.workspace), use_cache=True, diagnostics=args.diagnostics)
        recorded = data["workspace"]
        fresh = (
            recorded.get("diff_fingerprint") == current["diff_fingerprint"]
            and recorded.get("head_commit") == current["head_commit"]
            and recorded.get("tree_sha") == current["tree_sha"]
        )
        freshness = {
            "fresh": fresh,
            "recorded": {
                "head_commit": recorded.get("head_commit"),
                "tree_sha": recorded.get("tree_sha"),
                "diff_fingerprint": recorded.get("diff_fingerprint"),
            },
            "current": {
                "head_commit": current["head_commit"],
                "tree_sha": current["tree_sha"],
                "diff_fingerprint": current["diff_fingerprint"],
            },
        }
        if not fresh:
            errors.append(
                "verdict is stale: recorded fingerprint, head commit or reviewed tree does not match the current working tree; re-review required"
            )
        if args.diagnostics and "diagnostics" in current:
            freshness["diagnostics"] = current["diagnostics"]
    if errors:
        raise VerdictError("; ".join(errors), exit_code=1)
    payload: dict[str, Any] = {
        "ok": True,
        "command": "validate",
        "verdict": str(args.verdict),
        "schema": SCHEMA_ID,
        "accepted_schema": data["schema"],
        "result": data["result"],
    }
    if freshness is not None:
        payload["freshness"] = freshness
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"ok: valid {SCHEMA_ID} verdict ({data['result']}) at {args.verdict}")
    return 0


def _cmd_fingerprint(args: argparse.Namespace) -> int:
    payload = {
        "ok": True,
        "command": "fingerprint",
        **compute_fingerprint(Path(args.workspace), use_cache=args.cache, diagnostics=args.diagnostics),
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _cmd_preflight(args: argparse.Namespace) -> int:
    from changerail_delivery_manifest import ManifestError
    from changerail_review_preflight import run_preflight

    try:
        code, payload = run_preflight(
            card_path=args.card, workspace=Path(args.workspace), manifest_path=args.manifest,
            normalize=args.normalize, risk_override=args.risk_tier, output=args.output,
            fingerprint_fn=compute_fingerprint, validate_verdict=_validate_verdict,
            diagnostics=args.diagnostics,
        )
    except (ManifestError, ValueError, RuntimeError) as exc:
        raise VerdictError(str(exc), exit_code=1) from exc
    print(json.dumps(payload, ensure_ascii=False))
    return code


def _print_json_diagnostic(message: str, command: str, code: str) -> None:
    diagnostic = {
        "kind": "changerail_review_verdict",
        "code": code,
        "message": message,
    }
    payload = {
        "schema": SCHEMA_ID,
        "ok": False,
        "command": command,
        "diagnostic": diagnostic,
        "diagnostics": [diagnostic],
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a v1 review verdict")
    validate.add_argument("verdict", type=Path)
    validate.add_argument(
        "--check-fresh",
        action="store_true",
        help="also compare the recorded fingerprint against the current working tree",
    )
    validate.add_argument(
        "--workspace",
        default=".",
        help="workspace root for --check-fresh (default: current directory)",
    )
    validate.add_argument("--json", action="store_true", help="emit structured JSON result or diagnostic")
    validate.add_argument("--diagnostics", action="store_true", help="include cache/timing diagnostics in freshness output")
    validate.set_defaults(func=_cmd_validate)

    fingerprint = subparsers.add_parser(
        "fingerprint", help="compute the working-tree freshness fingerprint"
    )
    fingerprint.add_argument(
        "--workspace",
        default=".",
        help="workspace root to fingerprint (default: current directory)",
    )
    fingerprint.add_argument("--cache", action="store_true", help="reuse a validated ignored runtime cache entry")
    fingerprint.add_argument("--diagnostics", action="store_true", help="include public-safe timing and cache diagnostics")
    fingerprint.set_defaults(func=_cmd_fingerprint)

    preflight = subparsers.add_parser("preflight", help="run deterministic gates before payload review")
    preflight.add_argument("card", type=Path)
    preflight.add_argument("--workspace", default=".")
    preflight.add_argument("--manifest", type=Path)
    preflight.add_argument("--normalize", action="store_true")
    preflight.add_argument("--risk-tier", choices=["process", "deterministic", "ordinary", "critical"])
    preflight.add_argument("--output", type=Path)
    preflight.add_argument("--json", action="store_true", help="accepted for CLI symmetry; output is always JSON")
    preflight.add_argument("--diagnostics", action="store_true", help="include public-safe timing and fingerprint diagnostics")
    preflight.set_defaults(func=_cmd_preflight)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except VerdictError as exc:
        if getattr(args, "json", False) or args.command == "fingerprint":
            _print_json_diagnostic(
                str(exc),
                getattr(args, "command", "unknown"),
                "input_error" if exc.exit_code == 2 else "validation_failed",
            )
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        if getattr(args, "json", False):
            _print_json_diagnostic(str(exc), getattr(args, "command", "unknown"), "input_error")
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
