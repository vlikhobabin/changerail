#!/usr/bin/env python3
"""Native Windows backend for bin/changerail-python.cmd."""

import importlib.util
import json
import os
import runpy
import sys
from datetime import datetime, timezone


MIN_VERSION = (3, 11)
REQUIRED_MODULES = ("tomllib", "jsonschema")


def json_line(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def fail(code, message, json_output=False):
    if json_output:
        print(
            json_line(
                {
                    "ok": False,
                    "diagnostic": {
                        "kind": "changerail_python_runtime",
                        "message": message,
                    },
                }
            )
        )
    else:
        print(message, file=sys.stderr)
    return code


def usage():
    print("usage: changerail-python.cmd [--check] [--json] [script.py [args...]]")


def parse_internal(argv):
    source = "default"
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    remaining = list(argv)
    while remaining:
        if remaining[0] == "--source" and len(remaining) >= 2:
            source = remaining[1]
            del remaining[:2]
        elif remaining[0] == "--root" and len(remaining) >= 2:
            root = os.path.abspath(remaining[1])
            del remaining[:2]
        else:
            break
    return source, root, remaining


def parse_user_args(argv):
    check_only = False
    json_output = False
    remaining = list(argv)
    while remaining:
        arg = remaining[0]
        if arg == "--check":
            check_only = True
            del remaining[0]
        elif arg == "--json":
            json_output = True
            del remaining[0]
        elif arg == "--help":
            usage()
            raise SystemExit(0)
        elif arg == "--":
            del remaining[0]
            break
        else:
            break
    target = remaining[0] if remaining else ""
    target_args = remaining[1:] if remaining else []
    return check_only, json_output, target, target_args


def validate_runtime(json_output):
    version = sys.version_info[:3]
    version_text = ".".join(str(part) for part in version)
    if version < MIN_VERSION:
        return (
            False,
            "ChangeRail Python runtime error: selected interpreter "
            f"'{sys.executable}' is Python {version_text}; Python 3.11 or "
            "newer is required. Install a supported interpreter or set "
            "CHANGERAIL_PYTHON to one.",
        )

    missing = [
        name
        for name in REQUIRED_MODULES
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        return (
            False,
            "ChangeRail Python runtime error: selected interpreter "
            f"'{sys.executable}' is missing runtime module(s): "
            f"{','.join(missing)}. Install runtime dependencies with: "
            f"{sys.executable} -m pip install -r requirements-runtime.txt",
        )
    return True, ""


def write_state(root, source):
    runtime_root = os.environ.get(
        "CHANGERAIL_RUNTIME_ROOT",
        os.path.join(root, ".runtime", "changerail"),
    )
    runtime_dir = os.path.join(runtime_root, "python-runtime")
    tmp_path = None
    try:
        os.makedirs(runtime_dir, exist_ok=True)
        state_path = os.path.join(runtime_dir, "last-check.json")
        tmp_path = state_path + f".{os.getpid()}.tmp"
        payload = {
            "schema": "changerail.python-runtime-check.v1",
            "checked_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "source": source,
            "executable": sys.executable,
            "version": ".".join(str(part) for part in sys.version_info[:3]),
            "required_modules": list(REQUIRED_MODULES),
        }
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, state_path)
    except OSError:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def execute_target(root, target, target_args):
    os.environ["CHANGERAIL_PYTHON_RESOLVED"] = sys.executable
    scripts_path = os.path.join(root, "scripts")
    current_pythonpath = os.environ.get("PYTHONPATH")
    if current_pythonpath:
        os.environ["PYTHONPATH"] = scripts_path + os.pathsep + current_pythonpath
    else:
        os.environ["PYTHONPATH"] = scripts_path
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)

    sys.argv = [target] + target_args
    runpy.run_path(target, run_name="__main__")
    return 0


def main(argv):
    source, root, remaining = parse_internal(argv)
    check_only, json_output, target, target_args = parse_user_args(remaining)

    ok, message = validate_runtime(json_output)
    if not ok:
        return fail(2, message, json_output)

    write_state(root, source)

    if check_only and json_output:
        print(
            json_line(
                {
                    "ok": True,
                    "source": source,
                    "executable": sys.executable,
                    "version": ".".join(str(part) for part in sys.version_info[:3]),
                    "required_modules": list(REQUIRED_MODULES),
                }
            )
        )

    if check_only:
        return 0

    if not target:
        return fail(
            2,
            "ChangeRail Python runtime error: no target script supplied.",
            json_output,
        )

    return execute_target(root, target, target_args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
