#!/usr/bin/env python3
# ruff: noqa: E701, E702
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from typing import Any

from changerail_release_admitted_execution import AdmissionError, _mount, build_row
from changerail_release_semantic_scheduler import SchedulerError, run_admitted_plan

SCHEMA = "changerail.release-profile.v1"
SEMANTIC_DIGEST = "7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513"
FULL_DIGEST = "6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72"
UNICODE_RANGES = ((0,31),(127,159),(173,173),(1536,1541),(1564,1564),(1757,1757),(1807,1807),(2192,2193),(2274,2274),(6158,6158),(8203,8207),(8234,8238),(8288,8292),(8294,8303),(65279,65279),(65529,65531),(69821,69821),(69837,69837),(78896,78911),(113824,113827),(119155,119162),(917505,917505),(917536,917631))
SEMANTIC = ("openspec.validation","config.json-parse","config.toml-parse","contracts.schema-validation","python.syntax-inventory","python.runtime-selection","windows.entrypoints","project.bootstrap","project.verify-drift","windows.wiring-git-safety","windows.lab-dry-run","windows.runtime-wiring-dry-run","python.lint","ci.workflow-contract","public-surface.self-test","public-surface.current","public-surface.history","wiring.discovery","runtime.diagnostics","consumer-ci","review.verdict-validation","review.fingerprint","review.fingerprint-benchmark","review.fingerprint-cache","review.preflight","evidence.retained","maintenance.runner","delivery.manifest","delivery.manifest-derive","delivery.runner","delivery.metrics","openspec.archive-diagnostics","drift.generated-fixture","git.whitespace","git.ignored-status")
PHYSICAL = (
 ("openspec.validation",(("./bin/openspec","validate","--all","--strict"),)),("config.json-parse",(("python3","-m","json.tool",".mcp.json"),)),("config.toml-parse",(("python3","-c","import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')"),)),
 ("contracts.schema-validation",(("python3","scripts/smoke-contract-schemas.py"),)),("python.syntax-inventory",(("python3","scripts/compile-python-inventory.py"),)),("python.runtime-selection",(("python3","scripts/smoke-python-runtime.py"),)),("windows.local-matrix",(("python3","scripts/smoke-windows-matrix.py"),)),
 ("python.lint",(("ruff","check","bin","scripts"),)),("ci.workflow-contract",(("python3","scripts/smoke-release-ci.py"),)),("public-surface.self-test",(("python3","scripts/public-surface-scan.py","--self-test"),)),("public-surface.current",(("python3","scripts/public-surface-scan.py"),)),("public-surface.history",(("python3","scripts/public-surface-scan.py","--history"),)),
 ("wiring.discovery",(("python3","scripts/smoke-wiring-discovery.py"),)),("runtime.diagnostics",(("python3","scripts/smoke-runtime-diagnostics.py"),)),("consumer-ci",(("python3","scripts/smoke-consumer-ci.py"),)),("review.verdict-validation",(("python3","scripts/smoke-review-verdict-validation.py"),)),("review.fingerprint",(("python3","scripts/smoke-review-fingerprint.py"),)),("review.fingerprint-benchmark",(("python3","scripts/smoke-review-fingerprint-benchmark.py"),)),("review.fingerprint-cache",(("python3","scripts/smoke-review-fingerprint-cache.py"),)),("review.preflight",(("python3","scripts/smoke-review-preflight.py"),)),
 ("evidence.retained",(("python3","scripts/smoke-retained-evidence.py"),)),("maintenance.runner",(("python3","scripts/smoke-maintenance-runner.py"),)),("delivery.manifest",(("python3","scripts/smoke-delivery-manifest.py"),)),("delivery.manifest-derive",(("python3","scripts/smoke-delivery-manifest-derive.py"),)),("delivery.runner",(("python3","scripts/smoke-delivery-runner.py"),)),("delivery.metrics",(("python3","scripts/smoke-delivery-metrics.py"),)),("openspec.archive-diagnostics",(("python3","scripts/smoke-openspec-archive-diagnostics.py"),)),
 ("drift.generated-fixture",(("rm","-rf",".runtime/changerail/ci-drift"),("./bin/bootstrap-project",".runtime/changerail/ci-drift/example-project","--name","example-project","--kind","generic","--lock-enforcement","none"),("python3","scripts/smoke-drift.py","--project",".runtime/changerail/ci-drift/example-project"))),("git.whitespace",(("git","diff","--check"),)),("git.ignored-status",(("git","status","--short","--ignored"),)),
)
FLOOR = {"openspec.validation","public-surface.current","git.whitespace","git.ignored-status"}
WINDOWS = set(SEMANTIC[6:12])
PINS = {"jsonschema":"4.23.0","markdown-it-py":"3.0.0","PyYAML":"6.0.3","ruff":"0.6.9"}


class ProfileError(RuntimeError):
    pass


def _root(workspace: Path, value: os.PathLike[str] | str | None) -> Path:
    anchor = workspace / ".runtime" / "changerail"
    target = Path(value) if value is not None else anchor / "affected-release-v18"
    if not target.is_absolute() or target.parent != anchor or target != target.resolve(strict=True):
        raise ProfileError("runtime root is not an exact real direct child")
    if anchor.is_symlink() or target.is_symlink() or any(target.iterdir()):
        raise ProfileError("runtime root ancestry or emptiness failed")
    afd = os.open(anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        tfd = os.open(target.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=afd)
        observed = os.fstat(tfd); expected = target.stat(follow_symlinks=False)
        if (observed.st_dev, observed.st_ino, stat.S_IFMT(observed.st_mode)) != (expected.st_dev, expected.st_ino, stat.S_IFMT(expected.st_mode)) or (observed.st_dev, observed.st_ino) == (os.fstat(afd).st_dev, os.fstat(afd).st_ino) or _mount(tfd) != _mount(afd):
            raise ProfileError("runtime root identity drift")
        os.close(tfd)
    finally:
        os.close(afd)
    return target


def _environment(source: dict[str, str] | None) -> dict[str, str]:
    raw = dict(os.environ if source is None else source)
    if any(type(k) is not str or type(v) is not str or "\0" in k + v for k, v in raw.items()):
        raise ProfileError("environment is not closed text")
    search = raw.get("PATH", "")
    tools = {name: shutil.which(name, path=search) for name in ("python3","git","node","npm","npx","ruff","rm","bash","sh")}
    if raw.get("RUNNER_TOOL_CACHE"):
        architecture = {"X64":"x64","ARM64":"arm64"}.get(raw.get("RUNNER_ARCH", ""))
        roots = list(Path(raw["RUNNER_TOOL_CACHE"]).glob(f"node/20.*.*/{architecture}/bin")) if architecture else []
        if len(roots) != 1 or roots[0].is_symlink(): raise ProfileError("hosted Node root mismatch")
        for name in ("node","npm","npx"):
            candidate = roots[0]/name
            if not candidate.exists(): raise ProfileError(f"hosted {name} missing")
            if name != "node" and (not candidate.is_symlink() or os.readlink(candidate) != f"../lib/node_modules/npm/bin/{name}-cli.js"): raise ProfileError(f"hosted {name} launcher mismatch")
            tools[name] = str(candidate)
    if any(not value for value in tools.values()) or sys.version_info < (3, 11):
        raise ProfileError("required executable is unavailable")
    for distribution, version in PINS.items():
        if importlib.metadata.version(distribution) != version:
            raise ProfileError(f"distribution mismatch: {distribution}")
    keep = ("HOME","LANG","LC_ALL","TMPDIR","OPENSPEC_VERSION","OPENSPEC_TELEMETRY","npm_config_prefer_offline","RUNNER_TOOL_CACHE","RUNNER_ARCH","PYTHONPATH")
    result = {key: raw[key] for key in keep if key in raw}
    result["PATH"] = os.pathsep.join(dict.fromkeys(([str(roots[0])] if raw.get("RUNNER_TOOL_CACHE") else []) + [str(Path(value).resolve().parent) for value in tools.values() if value]))
    result.setdefault("LANG", "C.UTF-8"); result.setdefault("OPENSPEC_TELEMETRY", "0"); result.setdefault("npm_config_prefer_offline", "true")
    return result


def _git(workspace: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=workspace, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=10, check=False)
    if result.returncode or result.stderr or len(result.stdout) > 1_048_576:
        raise ProfileError("git selector command failed")
    return result.stdout


def _paths(workspace: Path, base: str) -> list[str]:
    if not base or len(base) > 128 or b"\0" in base.encode(): raise ProfileError("invalid base")
    _git(workspace,"rev-parse","--verify",f"{base}^{{commit}}")
    _git(workspace,"merge-base","--is-ancestor",base,"HEAD")
    paths: list[bytes] = []
    for args in (("diff","--name-status","-z","--find-renames","--find-copies",f"{base}...HEAD"),("diff","--cached","--name-status","-z","--find-renames","--find-copies"),("diff","--name-status","-z","--find-renames","--find-copies")):
        fields = _git(workspace,*args).split(b"\0"); fields = fields[:-1] if fields[-1:] == [b""] else (_ for _ in ()).throw(ProfileError("malformed git framing"))
        index = 0
        while index < len(fields):
            status_code = fields[index]; index += 1
            if not status_code or chr(status_code[0]) not in "AMDRC" or (status_code[:1] in b"RC" and not status_code[1:].isdigit()): raise ProfileError("unknown git status")
            count = 2 if status_code[:1] in b"RC" else 1
            if index + count > len(fields): raise ProfileError("short git status")
            paths.extend(fields[index:index+count]); index += count
    untracked = _git(workspace,"ls-files","--others","--exclude-standard","-z").split(b"\0")
    if untracked[-1:] != [b""]: raise ProfileError("malformed untracked framing")
    paths.extend(untracked[:-1])
    if not paths or len(paths) > 4096: raise ProfileError("empty or over-bound selection")
    result = []
    for raw in paths:
        value = raw.decode("utf-8", "strict"); parts = Path(value).parts
        if not value or value.startswith("/") or ".." in parts or any(a <= ord(ch) <= b for ch in value for a,b in UNICODE_RANGES): raise ProfileError("invalid git path")
        result.append(value)
    return result


def _selection(paths: list[str]) -> tuple[str, ...]:
    selected = set(FLOOR)
    self_prefixes = ("scripts/run-release-baseline.py","scripts/changerail_release_",".github/workflows/","requirements-","openspec/specs/changerail-release-ci/")
    for path in paths:
        if path.startswith(self_prefixes): raise ProfileError("selector authority changed")
        if path.endswith((".md",".rst",".txt")) or path.startswith("openspec/"): continue
        if path.endswith(".py"):
            selected.update(("python.syntax-inventory","python.lint"))
            owners = {owner for owner, commands in PHYSICAL for command in commands if path in command}
            if not owners: raise ProfileError("unknown Python ownership")
            selected.update(owners); continue
        if path == ".mcp.json": selected.add("config.json-parse"); continue
        if path == ".codex/config.toml": selected.add("config.toml-parse"); continue
        raise ProfileError("unknown path ownership")
    return tuple(item for item in SEMANTIC if item in selected)


def _failed(profile: str, reason: object) -> dict[str, Any]:
    return {"schema":SCHEMA,"requested_profile":profile,"effective_profile":"full-release","authoritative":False,"semantic_started":0,"semantic_digest":SEMANTIC_DIGEST,"full_digest":FULL_DIGEST,"selected_semantic_ids":list(SEMANTIC),"selected_physical_ids":[],"fallback_reason":str(reason)[:128],"scheduler":{"version":"changerail.release-semantic-scheduler.v1","status":"fail","jobs":0,"results":[]}}


def run_profile(profile: str, *, base: str | None = None, jobs: int = 4,
                environment: dict[str, str] | None = None,
                runtime_root: os.PathLike[str] | str | None = None) -> dict[str, Any]:
    if profile not in ("full-release","affected") or (profile == "affected") != (base is not None):
        raise ProfileError("profile/base combination is invalid")
    workspace = Path.cwd()
    try: root = _root(workspace, runtime_root); env = _environment(environment)
    except (OSError, ValueError, importlib.metadata.PackageNotFoundError, ProfileError) as exc: return _failed(profile, exc)
    fallback = None
    selected = SEMANTIC
    if profile == "affected":
        try: selected = _selection(_paths(workspace, base or ""))
        except (OSError, UnicodeError, subprocess.SubprocessError, ProfileError) as exc: fallback = str(exc)[:128]; selected = SEMANTIC
    owners = {"windows.local-matrix" if item in WINDOWS else item for item in selected}
    try: rows = [build_row(owner, [list(command) for command in commands], env) for owner, commands in PHYSICAL if owner in owners]
    except (OSError, AdmissionError) as exc: return _failed(profile, exc)
    plan = [{"id": row["owner"],"command":row["members"][0]["logical_argv"],"execution_timeout":3600.0,"cleanup_timeout":60.0,"root":row["owner"]} for row in rows]
    try: _root(workspace, root); summary = run_admitted_plan(plan, root, rows, jobs=jobs)
    except (OSError, AdmissionError, ProfileError, SchedulerError) as exc: return _failed(profile, exc)
    authoritative = profile == "full-release" and summary["status"] == "pass" and tuple(selected) == SEMANTIC
    return {"schema":SCHEMA,"requested_profile":profile,"effective_profile":"full-release" if tuple(selected)==SEMANTIC else "affected","authoritative":authoritative,"semantic_started":len(plan),"semantic_digest":SEMANTIC_DIGEST,"full_digest":FULL_DIGEST,"selected_semantic_ids":list(selected),"selected_physical_ids":[row["owner"] for row in rows],"fallback_reason":fallback,"scheduler":summary}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--profile",choices=("full-release","affected"),default="full-release"); parser.add_argument("--base"); parser.add_argument("--jobs",type=int,default=4)
    args = parser.parse_args(argv)
    anchor = Path.cwd()/".runtime"/"changerail"; anchor.mkdir(parents=True,exist_ok=True)
    root = anchor/"affected-release-v18"
    if not root.exists(): root.mkdir(mode=0o700)
    result = run_profile(args.profile,base=args.base,jobs=args.jobs,runtime_root=root)
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    return 0 if result["scheduler"]["status"] == "pass" else 1


if __name__ == "__main__": raise SystemExit(main())
