"""Shared JSON Schema validation for ChangeRail runtime contracts."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
DATE_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def _format_path(parts: object) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _resolve_ref(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return schema
    current: Any = root_schema
    for part in ref.removeprefix("#/").split("/"):
        if not isinstance(current, dict):
            return schema
        current = current.get(part)
    return current if isinstance(current, dict) else schema


def _is_date_time(value: str) -> bool:
    if not DATE_TIME_RE.match(value):
        return False
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return True


def _format_validation_errors(data: Any, schema: dict[str, Any], root_schema: dict[str, Any], path: str) -> list[str]:
    schema = _resolve_ref(schema, root_schema)
    errors: list[str] = []
    if schema.get("format") == "date-time" and isinstance(data, str) and not _is_date_time(data):
        errors.append(f"{path}: {data!r} is not a 'date-time'")
    for key in ("allOf", "anyOf", "oneOf"):
        for child in schema.get(key, []):
            if isinstance(child, dict):
                errors.extend(_format_validation_errors(data, child, root_schema, path))
    if isinstance(data, dict):
        properties = schema.get("properties")
        if isinstance(properties, dict):
            for key, child in properties.items():
                if key in data and isinstance(child, dict):
                    errors.extend(_format_validation_errors(data[key], child, root_schema, f"{path}.{key}"))
    if isinstance(data, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(data):
                errors.extend(_format_validation_errors(item, items, root_schema, f"{path}[{index}]"))
    return errors


def validate_with_schema(data: Any, schema_filename: str) -> list[str]:
    try:
        import jsonschema
    except Exception as exc:
        return [f"schema validation unavailable: {type(exc).__name__}: {exc}"]

    schema_path = SCHEMA_ROOT / schema_filename
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"schema cannot be read: {schema_path}: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"schema JSON is invalid: {schema_path}: {exc}"]

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.SchemaError as exc:
        return [f"schema is invalid: {schema_path}: {exc.message}"]

    errors = [f"{_format_path(error.absolute_path)}: {error.message}" for error in sorted(
        validator.iter_errors(data), key=lambda error: list(error.absolute_path)
    )]
    errors.extend(_format_validation_errors(data, schema, schema, "$"))
    return errors
