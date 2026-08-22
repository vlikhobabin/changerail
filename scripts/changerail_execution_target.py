"""Shared execution-target declaration loader for ChangeRail contracts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from changerail_contract_schema import validate_with_schema

DECLARATION_REL_PATH = ".changerail/execution-target.json"
SCHEMA_FILE = "changerail-execution-target.schema.json"
SCHEMA_ID = "changerail.execution-target.v1"
SECRET_MARKER_RE = re.compile(r"(?i)(token|secret|password|passwd|credential|authorization|api[_-]?key)")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def execution_target_projection(data: dict[str, Any]) -> dict[str, str]:
    return {
        "schema": SCHEMA_ID,
        "id": str(data["id"]),
        "fingerprint": str(data["fingerprint"]),
        "target_substitution_policy": str(data["target_substitution_policy"]),
    }


def execution_targets_match(first: Any, second: Any) -> bool:
    if not isinstance(first, dict) or not isinstance(second, dict):
        return False
    return execution_target_key(first) == execution_target_key(second)


def execution_target_key(value: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None]:
    return (
        value.get("schema") if isinstance(value.get("schema"), str) else None,
        value.get("id") if isinstance(value.get("id"), str) else None,
        value.get("fingerprint") if isinstance(value.get("fingerprint"), str) else None,
        value.get("target_substitution_policy") if isinstance(value.get("target_substitution_policy"), str) else None,
    )


def describe_execution_target(value: Any) -> str:
    if not isinstance(value, dict):
        return "absent"
    target_id = value.get("id")
    fingerprint = value.get("fingerprint")
    policy = value.get("target_substitution_policy")
    return f"id={target_id} fingerprint={fingerprint} policy={policy}"


def _git_is_repo(workspace: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(workspace), "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _git_tracked(workspace: Path, rel_path: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(workspace), "ls-files", "--error-unmatch", "--", rel_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _value_safety_errors(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []
    errors: list[str] = []
    for field in ("id", "fingerprint"):
        value = data.get(field)
        if not isinstance(value, str):
            continue
        if "://" in value or "@" in value:
            errors.append(f"{field} must not contain endpoint-like values")
        if SECRET_MARKER_RE.search(value):
            errors.append(f"{field} must not contain credential-like markers")
    return errors


def load_execution_target(workspace: Path, *, require_tracked: bool = False) -> dict[str, Any]:
    root = workspace.resolve(strict=False)
    path = root / DECLARATION_REL_PATH
    result: dict[str, Any] = {"present": False, "path": DECLARATION_REL_PATH, "errors": []}
    if not path.exists() and not path.is_symlink():
        return result

    errors: list[str] = []
    if path.is_symlink():
        errors.append(f"{DECLARATION_REL_PATH} must be a regular file, not a symlink")
    resolved = path.resolve(strict=False)
    if not _is_relative_to(resolved, root):
        errors.append(f"{DECLARATION_REL_PATH} resolves outside the workspace")
    if path.exists() and not path.is_file():
        errors.append(f"{DECLARATION_REL_PATH} must be a regular file")
    if require_tracked and _git_is_repo(root) and not _git_tracked(root, DECLARATION_REL_PATH):
        errors.append(f"{DECLARATION_REL_PATH} must be tracked by git")

    data: Any = None
    if not errors:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(f"{DECLARATION_REL_PATH} cannot be read: {exc}")
        except json.JSONDecodeError as exc:
            errors.append(f"{DECLARATION_REL_PATH} JSON is invalid: {exc}")
    if data is not None:
        errors.extend(validate_with_schema(data, SCHEMA_FILE))
        errors.extend(_value_safety_errors(data))

    result["present"] = True
    result["errors"] = errors
    if not errors and isinstance(data, dict):
        result["identity"] = execution_target_projection(data)
    return result
