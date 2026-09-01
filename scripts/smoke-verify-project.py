#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import runpy
import secrets
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from multiprocessing.connection import Connection
from pathlib import Path


SCHEMA = "changerail.verify-project-smoke.v1"
SPECIAL_OUTPUTS = {
    Path("gitignore.tpl"): Path(".gitignore"),
    Path("mcp.json.tpl"): Path(".mcp.json"),
    Path("codex-config.toml.tpl"): Path(".codex/config.toml"),
}
EXPECTED_SCHEMAS = (
    "schemas/changerail-consumer-lock.schema.json",
    "schemas/changerail-execution-target.schema.json",
    "schemas/changerail-review-verdict.schema.json",
    "schemas/changerail-review-preflight-result.schema.json",
    "schemas/changerail-review-cycle-history.schema.json",
    "schemas/changerail-delivery-manifest.schema.json",
    "schemas/changerail-delivery-run.schema.json",
    "schemas/changerail-evidence-index.schema.json",
    "schemas/changerail-verification-coverage.schema.json",
    "schemas/changerail-verification-coverage-plan.schema.json",
    "schemas/changerail-verification-coverage-ledger.schema.json",
)
EXPECTED_MAINTENANCE_CHECKS = (
    ".changerail/knowledge.yaml",
    ".changerail/maintenance.yaml",
    ".gitignore maintenance runtime policy",
    "bin/changerail-maintenance",
    "bin/changerail-maintenance-runner",
    "schemas/changerail-maintenance-run.schema.json",
    "schemas/changerail-maintenance-quality-rollup.schema.json",
    "schemas/changerail-maintenance-proposal-decision.schema.json",
)
MCP_FILES = (".mcp.json", ".codex/config.toml")
OPTIONAL_BROWSER_MCP_NEEDLES = ("@playwright/mcp", "chrome-devtools-mcp")
WIRING_MANIFEST = Path("openspec/changerail-wiring.json")
CONSUMER_LOCK = Path("openspec/changerail-consumer-lock.json")
WORKER_COUNT = 2
SHARD_TIMEOUT_SECONDS = 210.0
SHARD_SCENARIOS = (
    (
        "valid fixture passes",
        "absent execution target is compatible",
        "source classification policy check passes",
        "invalid source classification blocks verify",
        "valid execution target passes",
        "untracked execution target fails",
        "unknown execution target field fails",
        "symlink execution target fails",
        "successful npm stderr warning preserves integrity verification",
        "failed npm lookup preserves stdout and stderr diagnostics",
        "npm cmd executable resolution passes",
        "missing auth advisory warns",
        "codex-only profile passes with optional diagnostics",
        "safe profile rejects full access",
        "legacy profile compatibility passes",
        "matching consumer lock passes",
        "advisory source drift is diagnostic",
        "strict source drift blocks",
        "broken advisory wiring blocks",
        "unsafe consumer lock blocks",
        "all contract schemas checked",
        "maintenance default opt-out skipped",
        "maintenance opt-in wiring passes",
        "missing maintenance quality schema fails",
        "missing maintenance proposal-decision schema fails",
        "partial maintenance opt-in fails",
        "generated Windows wiring passes",
        "stale generated wiring fails",
        "missing generated artifact fails",
        "project-owned generated divergence fails",
        "drift generated wiring passes",
        "drift stale generated wiring fails",
        "drift project-owned generated divergence fails",
        "lockless generated refresh requires adoption",
        "generated wiring refresh passes",
        "stale generated wiring refresh passes",
        "generated Windows maintenance wiring passes",
        "stale generated maintenance helper fails",
        "project-owned generated maintenance divergence fails",
    ),
    (
        "Windows symlink fallback proof verifies",
        "status-only fallback proof fails verification",
        "hash-only fallback proof fails verification",
        "Windows symlink fallback proof required",
        "Windows junction fallback proof required",
        "Windows junction fallback proof dry-run passes",
        "auth marker advisory passes",
        "auth conflict requires owner review",
        "auth environment advisory passes",
        "tracked auth.toml fails",
        "missing runtime ignore fails",
        "stale OPSX wiring fails",
        "missing chrl alias fails",
        "codex-only profile passes with diagnostics",
        "default all-surfaces missing Claude fails",
        "forbidden legacy MCP artifact fails",
        "mandatory targeted validation weakening fails",
        "configured verification coverage map validates",
        "invalid verification coverage map fails closed",
        "undeclared baseline debt fails closed",
        "declared baseline debt is diagnostic",
        "baseline debt cannot mask targeted change failure",
        "unsafe portable scope fails",
        "unpinned MCP package fails",
        "tampered MCP integrity fails",
        "optional browser MCP direct and package forms pass",
        "optional browser MCP missing version fails",
        "optional browser MCP missing lock fails",
        "optional browser MCP tampered integrity fails",
        "optional browser MCP absent from defaults",
    ),
)


@dataclass
class Check:
    name: str
    status: str
    message: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def skill_names(changerail_root: Path) -> list[str]:
    return sorted(
        path.name
        for path in (changerail_root / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def render_text(text: str, project: Path, changerail_root: Path) -> str:
    replacements = {
        "{{PROJECT_PATH}}": str(project),
        "{{PROJECT_CONFIG_SCOPE}}": ".",
        "{{CODEX_PROJECT_KEY}}": ".",
        "{{PROJECT_ROOT_LABEL}}": "this repository",
        "{{PROJECT_NAME}}": "example-project",
        "{{PROJECT_KIND}}": "generic",
        "{{PROJECT_PROFILE}}": "generic",
        "{{SURFACES_PROFILE}}": "all-surfaces",
        "{{CODEX_POLICY}}": "safe-interactive",
        "{{CODEX_APPROVAL_POLICY}}": "on-request",
        "{{CODEX_SANDBOX_MODE}}": "workspace-write",
        "{{CODEX_SURFACE_STATE}}": "required",
        "{{CLAUDE_SURFACE_STATE}}": "required",
        "{{LEGACY_MCP_SURFACE_STATE}}": "required",
        "{{LEGACY_ARTIFACTS_SURFACE_STATE}}": "forbidden",
        "{{TOPOLOGY_GUIDANCE}}": (
            "This repository uses neutral project ownership without domain-specific source generation."
        ),
        "{{CODEX_AUTHORITY_GUIDANCE}}": (
            "safe-interactive requires approval for commands and limits writes to the workspace."
        ),
        "{{CHANGERAIL_ROOT}}": str(changerail_root),
        "{{CHANGERAIL_ROOT_LABEL}}": "the linked ChangeRail source of truth",
        "{{CHANGERAIL_SHARED_SOURCE}}": "ChangeRail AGENTS.shared.md",
        "{{CHANGERAIL_SHARED_AGENTS}}": (changerail_root / "AGENTS.shared.md").read_text(encoding="utf-8"),
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def output_path_for(rel: Path) -> Path | None:
    if rel == Path("README.md"):
        return None
    if rel in SPECIAL_OUTPUTS:
        return SPECIAL_OUTPUTS[rel]
    if rel.name.endswith(".tpl"):
        return rel.with_name(rel.name[: -len(".tpl")])
    return rel


def symlink_force(target: Path, link_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.exists():
        if link_path.is_dir() and not link_path.is_symlink():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    os.symlink(target, link_path)


def create_changerail_root_fixture(source_root: Path, target_root: Path, *, missing_schemas: tuple[str, ...] = ()) -> None:
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True)
    for rel_path in (
        "AGENTS.shared.md",
        "mcp-npm-lock.json",
        "templates",
        "skills",
        "claude",
        "bin",
        "openspec",
    ):
        symlink_force(source_root / rel_path, target_root / rel_path)
    shutil.copytree(source_root / "schemas", target_root / "schemas")
    for schema in missing_schemas:
        (target_root / "schemas" / schema).unlink(missing_ok=True)


def create_fixture(project: Path, changerail_root: Path, *, with_maintenance: bool = False) -> None:
    template_root = changerail_root / "templates" / "project"
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)

    for source in template_root.rglob("*"):
        if source.is_dir():
            continue
        rel = source.relative_to(template_root)
        if rel.parts and rel.parts[0] == ".changerail" and not with_maintenance:
            continue
        if rel.parts[:2] == (".github", "workflows"):
            continue
        out_rel = output_path_for(rel)
        if out_rel is None:
            continue
        target = project / out_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.name.endswith(".tpl"):
            target.write_text(render_text(source.read_text(encoding="utf-8"), project, changerail_root), encoding="utf-8")
        else:
            shutil.copy2(source, target)

    symlink_force(changerail_root / "skills", project / ".claude" / "skills")
    symlink_force(changerail_root / "claude" / "commands" / "changerail", project / ".claude" / "commands" / "changerail")
    symlink_force(changerail_root / "claude" / "commands" / "chrl", project / ".claude" / "commands" / "chrl")
    for skill in skill_names(changerail_root):
        symlink_force(changerail_root / "skills" / skill, project / ".codex" / "skills" / skill)
    symlink_force(changerail_root / "bin" / "openspec", project / "bin" / "openspec")
    symlink_force(changerail_root / "bin" / "changerail-python", project / "bin" / "changerail-python")
    symlink_force(changerail_root / "bin" / "verify-project", project / "bin" / "verify-project")
    symlink_force(changerail_root / "bin" / "changerail-delivery-manifest", project / "bin" / "changerail-delivery-manifest")
    symlink_force(changerail_root / "bin" / "changerail-review-verdict", project / "bin" / "changerail-review-verdict")
    symlink_force(changerail_root / "bin" / "changerail-evidence", project / "bin" / "changerail-evidence")
    symlink_force(changerail_root / "bin" / "changerail-source-classification", project / "bin" / "changerail-source-classification")
    if with_maintenance:
        symlink_force(changerail_root / "bin" / "changerail-maintenance", project / "bin" / "changerail-maintenance")
        symlink_force(
            changerail_root / "bin" / "changerail-maintenance-runner",
            project / "bin" / "changerail-maintenance-runner",
        )


def run(cmd: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "OPENSPEC_TELEMETRY": "0"}
    if extra_env:
        env.update(extra_env)
    effective_cmd = list(cmd)
    if Path(effective_cmd[0]).name in {"bootstrap-project", "bootstrap-project.cmd"}:
        if "--lock-enforcement" not in effective_cmd:
            effective_cmd[2:2] = ["--lock-enforcement", "none"]
    return subprocess.run(
        effective_cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=180,
    )


def write_consumer_lock(
    project: Path,
    changerail_root: Path,
    *,
    enforcement: str = "advisory",
    revision: str | None = None,
) -> None:
    artifacts: list[dict[str, str]] = []
    for path in sorted(project.rglob("*")):
        if not path.is_symlink():
            continue
        try:
            source = path.resolve(strict=False).relative_to(changerail_root).as_posix()
        except ValueError:
            continue
        rel_path = path.relative_to(project).as_posix()
        if rel_path.startswith(".codex/skills/"):
            surface = "codex-skill"
        elif rel_path == ".claude/skills":
            surface = "claude-skills"
        elif rel_path.startswith(".claude/commands/"):
            surface = "claude-commands"
        else:
            surface = "helper"
        artifacts.append(
            {
                "path": rel_path,
                "source": source,
                "kind": "symlink",
                "surface": surface,
            }
        )
    actual_revision = revision or run(
        ["git", "rev-parse", "HEAD"],
        changerail_root,
    ).stdout.strip()
    payload = {
        "schema": "changerail.consumer-lock.v1",
        "changerail": {
            "version": (changerail_root / "VERSION").read_text(encoding="utf-8").strip(),
            "revision": actual_revision,
            "source": "https://github.com/example/changerail.git",
        },
        "wiring": {
            "platform": "posix",
            "backend": "symlink",
            "path_mode": "absolute",
            "artifacts": artifacts,
        },
        "profiles": {
            "project": "generic",
            "surfaces": "all-surfaces",
            "codex_policy": "safe-interactive",
        },
        "enforcement": enforcement,
    }
    path = project / CONSUMER_LOCK
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_generated_consumer_lock(
    project: Path,
    changerail_root: Path,
    *,
    enforcement: str = "advisory",
) -> None:
    manifest = generated_manifest(project)
    artifacts: list[dict[str, str]] = []
    backend = str(manifest.get("backend") or "generated-copy")
    for entry in manifest.get("artifacts", []):
        if not isinstance(entry, dict):
            continue
        rel_path = entry.get("path")
        source = entry.get("source")
        surface = entry.get("surface")
        if not all(isinstance(value, str) and value for value in (rel_path, source, surface)):
            continue
        artifacts.append(
            {
                "path": str(rel_path),
                "source": str(source),
                "kind": backend,
                "surface": str(surface),
            }
        )
    actual_revision = run(
        ["git", "rev-parse", "HEAD"],
        changerail_root,
    ).stdout.strip()
    payload = {
        "schema": "changerail.consumer-lock.v1",
        "changerail": {
            "version": (changerail_root / "VERSION").read_text(encoding="utf-8").strip(),
            "revision": actual_revision,
            "source": "https://github.com/example/changerail.git",
        },
        "wiring": {
            "platform": str(manifest.get("platform") or "windows"),
            "backend": backend,
            "path_mode": "not-applicable",
            "artifacts": artifacts,
        },
        "profiles": {
            "project": "generic",
            "surfaces": "all-surfaces",
            "codex_policy": "safe-interactive",
        },
        "enforcement": enforcement,
    }
    path = project / CONSUMER_LOCK
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def bootstrap_generated_project(
    changerail_root: Path,
    project: Path,
    env: dict[str, str],
    *,
    with_maintenance: bool = False,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(changerail_root / "bin" / "bootstrap-project"),
        str(project),
        "--name",
        project.name,
        "--kind",
        "generic",
        "--wiring-platform",
        "windows",
        "--wiring-backend",
        "generated-copy",
    ]
    if with_maintenance:
        cmd.append("--with-maintenance")
    return run(cmd, changerail_root, env)


def generated_manifest(project: Path) -> dict[str, object]:
    return json.loads((project / WIRING_MANIFEST).read_text(encoding="utf-8"))


def write_generated_manifest(project: Path, manifest: dict[str, object]) -> None:
    (project / WIRING_MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def set_manifest_digest(project: Path, rel_path: str, digest: str) -> None:
    manifest = generated_manifest(project)
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise RuntimeError("generated manifest artifacts must be a list")
    for entry in artifacts:
        if isinstance(entry, dict) and entry.get("path") == rel_path:
            entry["digest"] = digest
            write_generated_manifest(project, manifest)
            return
    raise RuntimeError(f"generated manifest entry missing: {rel_path}")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def proof_evidence(
    *,
    command: str | None = None,
    operation: str | None = None,
    stdout: str = "",
    exit_code: int = 0,
) -> dict[str, object]:
    evidence: dict[str, object] = {
        "exit_code": exit_code,
        "stdout_sha256": sha256_text(stdout),
    }
    if command:
        evidence["command"] = command
    if operation:
        evidence["operation"] = operation
    return evidence


def proof_check(
    name: str,
    category: str,
    message: str,
    details: dict[str, object],
    evidence: dict[str, object],
) -> dict[str, object]:
    return {
        "name": name,
        "category": category,
        "status": "passed",
        "message": message,
        "details": details,
        "evidence": evidence,
    }


def git_probe_check(proof_root: Path, name: str, command: list[str], message: str) -> dict[str, object]:
    result = subprocess.run(
        command,
        cwd=proof_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    output = result.stdout.strip()
    return proof_check(
        name,
        "git",
        message,
        {
            "exit_code": result.returncode,
            "output_line_count": len([line for line in output.splitlines() if line.strip()]),
            "safe": result.returncode == 0,
            "unsafe_paths": [],
        },
        proof_evidence(command=" ".join(command), stdout=output, exit_code=result.returncode),
    )


def status_only_windows_fallback_proof(mode: str) -> dict[str, object]:
    checks = {
        "symlink": [
            {"name": "direct_os_symlink_directory", "status": "passed"},
            {"name": "direct_os_symlink_file", "status": "passed"},
            {"name": "symlink_privilege_or_developer_mode", "status": "passed"},
        ],
        "junction": [
            {"name": "junction_directory", "status": "passed"},
            {"name": "link_aware_cleanup", "status": "passed"},
            {"name": "git_status_safe", "status": "passed"},
            {"name": "git_add_dry_run_safe", "status": "passed"},
            {"name": "git_index_safe", "status": "passed"},
        ],
    }[mode]
    return {
        "schema": "changerail.windows-wiring-proof.v1",
        "mode": mode,
        "checks": checks,
    }


def hash_only_windows_fallback_proof(mode: str) -> dict[str, object]:
    if mode == "symlink":
        check_names = (
            "direct_os_symlink_directory",
            "direct_os_symlink_file",
            "symlink_privilege_or_developer_mode",
        )
    elif mode == "junction":
        check_names = (
            "junction_directory",
            "link_aware_cleanup",
            "git_status_safe",
            "git_add_dry_run_safe",
            "git_index_safe",
        )
    else:
        raise ValueError(mode)
    return {
        "schema": "changerail.windows-wiring-proof.v1",
        "mode": mode,
        "source": {
            "kind": "retained-command-evidence",
            "tool": "scripts/smoke-verify-project.py",
            "fixture": "hash-only",
        },
        "checks": [
            proof_check(
                name,
                "fixture",
                "hash-only assertion fixture must not count as evidence",
                {"fixture": "hash-only"},
                {
                    "stdout_sha256": sha256_text(f"{mode}:{name}:stdout"),
                    "raw_output_sha256": sha256_text(f"{mode}:{name}:raw"),
                },
            )
            for name in check_names
        ],
    }


def write_windows_fallback_proof(run_dir: Path, mode: str) -> Path:
    proof_root = run_dir / f"{mode}-fallback-proof-evidence"
    if proof_root.exists():
        shutil.rmtree(proof_root)
    proof_root.mkdir(parents=True)
    if mode == "symlink":
        source_dir = proof_root / "source-dir"
        source_file = proof_root / "source-file.txt"
        directory_link = proof_root / "directory-link"
        file_link = proof_root / "file-link.txt"
        source_dir.mkdir()
        source_file.write_text("proof\n", encoding="utf-8")
        os.symlink(source_dir, directory_link, target_is_directory=True)
        os.symlink(source_file, file_link, target_is_directory=False)
        checks = [
            proof_check(
                "direct_os_symlink_directory",
                "filesystem",
                "fixture os.symlink created a directory link",
                {"link_type": "directory", "fixture": "local-retained-evidence"},
                proof_evidence(operation="os.symlink", stdout="directory link created"),
            ),
            proof_check(
                "direct_os_symlink_file",
                "filesystem",
                "fixture os.symlink created a file link",
                {"link_type": "file", "fixture": "local-retained-evidence"},
                proof_evidence(operation="os.symlink", stdout="file link created"),
            ),
            proof_check(
                "symlink_privilege_or_developer_mode",
                "filesystem",
                "fixture proved directory and file symlink capability",
                {"directory_link": "passed", "file_link": "passed", "fixture": "local-retained-evidence"},
                proof_evidence(operation="os.symlink", stdout="directory and file symlink capability proved"),
            ),
        ]
    elif mode == "junction":
        git_root = proof_root / "git-consumer"
        git_root.mkdir()
        (git_root / "README.md").write_text("junction proof fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(git_root), "init"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=30)
        checks = [
            proof_check(
                "junction_directory",
                "filesystem",
                "retained Windows probe transcript recorded junction creation",
                {"link_type": "junction", "fixture": "local-retained-evidence"},
                proof_evidence(
                    command="cmd /c mklink /J .codex\\skills\\changerail-ff-junction <source>",
                    stdout="Junction created for retained proof fixture",
                ),
            ),
            proof_check(
                "link_aware_cleanup",
                "cleanup",
                "retained cleanup transcript recorded link path removal without target traversal",
                {"cleanup": "passed", "fixture": "local-retained-evidence"},
                proof_evidence(operation="remove-created-link-path", stdout="link path removed; target retained"),
            ),
            git_probe_check(
                git_root,
                "git_status_safe",
                ["git", "-C", str(git_root), "status", "--porcelain=v1", "--untracked-files=all"],
                "git status porcelain completed for retained fixture",
            ),
            git_probe_check(
                git_root,
                "git_add_dry_run_safe",
                ["git", "-C", str(git_root), "add", "--dry-run", "."],
                "git add dry-run completed for retained fixture",
            ),
            git_probe_check(
                git_root,
                "git_index_safe",
                ["git", "-C", str(git_root), "ls-files", "--stage"],
                "git index inspection completed for retained fixture",
            ),
        ]
    else:
        raise ValueError(mode)
    path = run_dir / f"{mode}-fallback-proof.json"
    path.write_text(
        json.dumps(
            {
                "schema": "changerail.windows-wiring-proof.v1",
                "mode": mode,
                "source": {
                    "kind": "retained-command-evidence",
                    "tool": "scripts/smoke-verify-project.py",
                    "fixture": "local",
                },
                "checks": checks,
            },
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=60,
    )


def create_fake_npm(changerail_root: Path, fake_bin: Path) -> dict[str, str]:
    fake_bin.mkdir(parents=True, exist_ok=True)
    lock = json.loads((changerail_root / "mcp-npm-lock.json").read_text(encoding="utf-8"))
    mapping = {
        f"{package['name']}@{package['version']}": package["integrity"]
        for package in lock.get("packages", [])
        if isinstance(package, dict)
    }
    npm = fake_bin / "npm"
    npm.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                f"MAPPING = {mapping!r}",
                "if len(sys.argv) == 5 and sys.argv[1] == 'view' and sys.argv[3] == 'dist.integrity' and sys.argv[4] == '--json':",
                "    spec = sys.argv[2]",
                "    if os.environ.get('CHANGERAIL_FAKE_NPM_FAIL') == spec:",
                "        print('registry stdout detail')",
                "        print('registry stderr detail', file=sys.stderr)",
                "        raise SystemExit(1)",
                "    if os.environ.get('CHANGERAIL_FAKE_NPM_WARNING') == spec:",
                "        print('npm warn Unknown builtin config', file=sys.stderr)",
                "    if os.environ.get('CHANGERAIL_FAKE_NPM_TAMPER') == spec:",
                "        print(json.dumps('sha512-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='))",
                "        raise SystemExit(0)",
                "    if spec in MAPPING:",
                "        print(json.dumps(MAPPING[spec]))",
                "        raise SystemExit(0)",
                "print('unsupported fake npm invocation: ' + ' '.join(sys.argv[1:]), file=sys.stderr)",
                "raise SystemExit(1)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    npm.chmod(0o755)
    return {"PATH": str(fake_bin) + os.pathsep + os.environ.get("PATH", "")}


def check_npm_cmd_resolution(changerail_root: Path, run_dir: Path) -> tuple[bool, str]:
    lock = json.loads((changerail_root / "mcp-npm-lock.json").read_text(encoding="utf-8"))
    packages = [package for package in lock.get("packages", []) if isinstance(package, dict)]
    if not packages:
        return False, "mcp-npm-lock.json has no package entries"
    package = packages[0]
    name = package["name"]
    version = package["version"]
    integrity = package["integrity"]
    fake_bin = run_dir / "fake-npm-cmd-bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    npm_cmd = fake_bin / "npm.cmd"
    npm_cmd.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                "if [ \"$1\" = \"view\" ] && [ \"$2\" = " + json.dumps(f"{name}@{version}") + " ] && "
                + "[ \"$3\" = \"dist.integrity\" ] && [ \"$4\" = \"--json\" ]; then",
                "  printf '%s\\n' " + json.dumps(json.dumps(integrity)),
                "  exit 0",
                "fi",
                "printf '%s\\n' \"unsupported fake npm invocation: $*\" >&2",
                "exit 1",
                "",
            ]
        ),
        encoding="utf-8",
    )
    npm_cmd.chmod(0o755)
    namespace = runpy.run_path(str(changerail_root / "bin" / "verify-project"))
    old_path = os.environ.get("PATH", "")
    try:
        os.environ["PATH"] = str(fake_bin)
        value, error = namespace["npm_registry_integrity"](name, version)
    finally:
        os.environ["PATH"] = old_path
    if error:
        return False, error
    return value == integrity, f"{name}@{version}"


def add_json_mcp_server(project: Path, name: str, args: list[str]) -> None:
    path = project / ".mcp.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("mcpServers", {})[name] = {
        "command": "npx",
        "args": args,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_codex_mcp_server(project: Path, name: str, args: list[str]) -> None:
    path = project / ".codex" / "config.toml"
    quoted_args = ", ".join(json.dumps(arg) for arg in args)
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n"
        + f"[mcp_servers.{name}]\n"
        + 'command = "npx"\n'
        + f"args = [{quoted_args}]\n"
        + "startup_timeout_sec = 60\n"
        + "enabled = true\n",
        encoding="utf-8",
    )


def set_verification_policy(
    project: Path,
    *,
    surfaces: dict[str, str] | None = None,
    targeted: str = "required",
    profile: str = "smoke",
) -> None:
    path = project / "openspec" / "config.yaml"
    text = path.read_text(encoding="utf-8")
    marker = "\nverification:\n"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n"
    surface_policy = {
        "codex": "required",
        "claude": "required",
        "legacy_mcp": "required",
        "legacy_artifacts": "forbidden",
    }
    if surfaces:
        surface_policy.update(surfaces)
    policy = [
        "",
        "verification:",
        f"  profile: {profile}",
        "  surfaces:",
    ]
    for name, state in surface_policy.items():
        policy.append(f"    {name}: {state}")
    policy.extend(
        [
            "  mandatory:",
            f"    targeted_openspec_validation: {targeted}",
            "  baseline_debt: []",
            "",
        ]
    )
    path.write_text(text + "\n".join(policy), encoding="utf-8")


def set_bootstrap_profiles(
    project: Path,
    *,
    project_profile: str,
    surfaces_profile: str,
    codex_policy: str,
) -> None:
    path = project / "openspec" / "config.yaml"
    text = path.read_text(encoding="utf-8")
    marker = "\nbootstrap:\n"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n"
    text += (
        "\nbootstrap:\n"
        f"  project_profile: {project_profile}\n"
        f"  surfaces_profile: {surfaces_profile}\n"
        f"  codex_policy: {codex_policy}\n"
    )
    path.write_text(text, encoding="utf-8")


def configure_verification_coverage(project: Path, map_text: str) -> None:
    map_path = project / ".changerail" / "verification-coverage.yaml"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(map_text, encoding="utf-8")
    config = project / "openspec" / "config.yaml"
    text = config.read_text(encoding="utf-8")
    if "  coverage_map:" in text:
        text = text.replace("  coverage_map: null", "  coverage_map: .changerail/verification-coverage.yaml")
    else:
        text = text.replace(
            "  profile: all-surfaces",
            "  profile: all-surfaces\n  coverage_map: .changerail/verification-coverage.yaml",
        )
    config.write_text(text, encoding="utf-8")
    if (project / ".git").exists():
        run(["git", "add", "openspec/config.yaml", ".changerail/verification-coverage.yaml"], project)


def remove_surface_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def verify_json(changerail_root: Path, project: Path, env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    result = run([str(changerail_root / "bin" / "verify-project"), str(project), "--json"], changerail_root, env)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}
    return result, data


def write_execution_target(project: Path, payload: dict[str, object] | None = None) -> Path:
    path = project / ".changerail" / "execution-target.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = payload or {
        "schema": "changerail.execution-target.v1",
        "id": "database-primary",
        "fingerprint": "sha256:" + ("1" * 64),
        "target_substitution_policy": "forbid",
    }
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def init_git_and_track(project: Path, *paths: str) -> None:
    git(project, "init")
    git(project, "config", "user.email", "smoke@example.invalid")
    git(project, "config", "user.name", "Smoke Test")
    if paths:
        git(project, "add", "--", *paths)


def drift_report(
    changerail_root: Path,
    project: Path,
    report_path: Path,
    env: dict[str, str],
) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
    result = run(
        [
            "python3",
            "scripts/smoke-drift.py",
            "--project",
            str(project),
            "--report",
            str(report_path),
        ],
        changerail_root,
        env,
    )
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return result, data


def check_result(
    data: dict[str, object],
    *,
    name: str,
    status: str | None = None,
    severity: str | None = None,
) -> bool:
    checks = data.get("checks", [])
    if not isinstance(checks, list):
        return False
    for check in checks:
        if not isinstance(check, dict) or check.get("name") != name:
            continue
        if status is not None and check.get("status") != status:
            continue
        if severity is not None and check.get("severity") != severity:
            continue
        return True
    return False


def browser_mcp_default_offenders(changerail_root: Path) -> list[str]:
    files = [
        changerail_root / ".mcp.json",
        changerail_root / ".codex" / "config.toml",
    ]
    files.extend(
        path
        for path in sorted((changerail_root / "templates" / "project").rglob("*"))
        if path.is_file()
    )
    offenders: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for needle in OPTIONAL_BROWSER_MCP_NEEDLES:
            if needle in text:
                offenders.append(f"{path.relative_to(changerail_root)} contains {needle}")
    return offenders


def first_project_class(data: dict[str, object]) -> str:
    projects = data.get("projects", [])
    if not projects or not isinstance(projects[0], dict):
        return ""
    value = projects[0].get("class")
    return value if isinstance(value, str) else ""


def run_smoke_shard(changerail_root: Path, run_dir: Path, shard: int) -> dict[str, object]:
    checks: list[Check] = []
    fake_env = create_fake_npm(changerail_root, run_dir / "fake-bin")
    fake_env.update({"CODEX_HOME": "", "CODEX_AUTH_TOKEN": "", "OPENAI_API_KEY": ""})
    good_project = run_dir / "example-project"
    create_fixture(good_project, changerail_root)

    if shard == 0:
        verify = run([str(changerail_root / "bin" / "verify-project"), str(good_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "valid fixture passes",
                "pass" if verify.returncode == 0 else "fail",
                verify.stdout.strip(),
            )
        )
        checks.append(
            Check(
                "absent execution target is compatible",
                "pass" if verify.returncode == 0 and "PASS .changerail/execution-target.json: optional declaration absent" in verify.stdout else "fail",
                verify.stdout.strip(),
            )
        )
        checks.append(
            Check(
                "source classification policy check passes",
                "pass" if verify.returncode == 0 and "PASS source classification profile check" in verify.stdout else "fail",
                verify.stdout.strip(),
            )
        )
        bad_source_project = run_dir / "bad-source-classification-project"
        shutil.copytree(good_project, bad_source_project, symlinks=True)
        (bad_source_project / ".changerail").mkdir(exist_ok=True)
        (bad_source_project / ".changerail" / "source-classification.yaml").write_text(
            "schema: changerail.source-classification.v1\n"
            "source_kinds:\n"
            "  - id: python\n"
            "    suffixes: [\".py\"]\n"
            "    production_roots: [\"/absolute\"]\n"
            "    measure: lines\n",
            encoding="utf-8",
        )
        bad_source_verify = run([str(changerail_root / "bin" / "verify-project"), str(bad_source_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "invalid source classification blocks verify",
                "pass" if bad_source_verify.returncode != 0 and "source classification profile check" in bad_source_verify.stdout else "fail",
                bad_source_verify.stdout.strip(),
            )
        )
        target_project = run_dir / "execution-target-project"
        shutil.copytree(good_project, target_project, symlinks=True)
        write_execution_target(target_project)
        init_git_and_track(target_project, ".changerail/execution-target.json")
        target_verify = run([str(changerail_root / "bin" / "verify-project"), str(target_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "valid execution target passes",
                "pass" if target_verify.returncode == 0 and "declares id=database-primary" in target_verify.stdout else "fail",
                target_verify.stdout.strip(),
            )
        )
        untracked_target_project = run_dir / "bad-untracked-execution-target"
        shutil.copytree(good_project, untracked_target_project, symlinks=True)
        write_execution_target(untracked_target_project)
        init_git_and_track(untracked_target_project)
        untracked_target = run(
            [str(changerail_root / "bin" / "verify-project"), str(untracked_target_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "untracked execution target fails",
                "pass"
                if untracked_target.returncode != 0 and ".changerail/execution-target.json must be tracked by git" in untracked_target.stdout
                else "fail",
                untracked_target.stdout.strip(),
            )
        )
        unknown_target_project = run_dir / "bad-unknown-field-execution-target"
        shutil.copytree(good_project, unknown_target_project, symlinks=True)
        write_execution_target(
            unknown_target_project,
            {
                "schema": "changerail.execution-target.v1",
                "id": "database-primary",
                "fingerprint": "sha256:" + ("1" * 64),
                "target_substitution_policy": "forbid",
                "endpoint": "database.example.invalid",
            },
        )
        init_git_and_track(unknown_target_project, ".changerail/execution-target.json")
        unknown_target = run(
            [str(changerail_root / "bin" / "verify-project"), str(unknown_target_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "unknown execution target field fails",
                "pass"
                if unknown_target.returncode != 0 and "Additional properties are not allowed" in unknown_target.stdout
                else "fail",
                unknown_target.stdout.strip(),
            )
        )
        symlink_target_project = run_dir / "bad-symlink-execution-target"
        shutil.copytree(good_project, symlink_target_project, symlinks=True)
        outside_target = run_dir / "outside-execution-target.json"
        outside_target.write_text("{}", encoding="utf-8")
        (symlink_target_project / ".changerail").mkdir(exist_ok=True)
        os.symlink(outside_target, symlink_target_project / ".changerail" / "execution-target.json")
        symlink_target = run(
            [str(changerail_root / "bin" / "verify-project"), str(symlink_target_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "symlink execution target fails",
                "pass" if symlink_target.returncode != 0 and "must be a regular file, not a symlink" in symlink_target.stdout else "fail",
                symlink_target.stdout.strip(),
            )
        )
        warning_env = {
            **fake_env,
            "CHANGERAIL_FAKE_NPM_WARNING": "@modelcontextprotocol/server-filesystem@2026.7.10",
        }
        warning = run(
            [str(changerail_root / "bin" / "verify-project"), str(good_project)],
            changerail_root,
            warning_env,
        )
        checks.append(
            Check(
                "successful npm stderr warning preserves integrity verification",
                "pass"
                if warning.returncode == 0 and "PASS MCP npm pins" in warning.stdout
                else "fail",
                warning.stdout.strip(),
            )
        )
        failure_env = {
            **fake_env,
            "CHANGERAIL_FAKE_NPM_FAIL": "@modelcontextprotocol/server-filesystem@2026.7.10",
        }
        failure = run(
            [str(changerail_root / "bin" / "verify-project"), str(good_project)],
            changerail_root,
            failure_env,
        )
        checks.append(
            Check(
                "failed npm lookup preserves stdout and stderr diagnostics",
                "pass"
                if failure.returncode != 0
                and "registry stdout detail" in failure.stdout
                and "registry stderr detail" in failure.stdout
                else "fail",
                failure.stdout.strip(),
            )
        )
        npm_cmd_ok, npm_cmd_message = check_npm_cmd_resolution(changerail_root, run_dir)
        checks.append(
            Check(
                "npm cmd executable resolution passes",
                "pass" if npm_cmd_ok else "fail",
                npm_cmd_message,
            )
        )
        checks.append(
            Check(
                "missing auth advisory warns",
                "pass"
                if verify.returncode == 0
                and "WARN delivery runner auth readiness" in verify.stdout
                and "codex-auth-for-delivery-runner" in verify.stdout
                and str(changerail_root / "docs" / "consumer-adoption-runbook.md") in verify.stdout
                and "--configure-existing --link-codex-auth AUTH_JSON" in verify.stdout
                else "fail",
                verify.stdout.strip(),
            )
        )

        codex_only_project = run_dir / "profile-codex-only"
        shutil.copytree(good_project, codex_only_project, symlinks=True)
        remove_surface_path(codex_only_project / ".claude")
        set_verification_policy(
            codex_only_project,
            surfaces={"claude": "optional", "legacy_mcp": "optional"},
            profile="codex-only",
        )
        set_bootstrap_profiles(
            codex_only_project,
            project_profile="generic",
            surfaces_profile="codex-only",
            codex_policy="safe-interactive",
        )
        codex_only_verify, codex_only_data = verify_json(changerail_root, codex_only_project, fake_env)
        checks.append(
            Check(
                "codex-only profile passes with optional diagnostics",
                "pass"
                if codex_only_verify.returncode == 0
                and check_result(codex_only_data, name="bootstrap profile consistency", status="pass")
                and check_result(codex_only_data, name=".claude/skills", status="fail", severity="non-blocking")
                else "fail",
                codex_only_verify.stdout.strip(),
            )
        )

        unsafe_safe_project = run_dir / "bad-safe-profile-authority"
        shutil.copytree(good_project, unsafe_safe_project, symlinks=True)
        unsafe_codex_path = unsafe_safe_project / ".codex" / "config.toml"
        unsafe_codex_text = unsafe_codex_path.read_text(encoding="utf-8")
        unsafe_codex_text = unsafe_codex_text.replace(
            'approval_policy = "on-request"',
            'approval_policy = "never"',
        ).replace(
            'sandbox_mode = "workspace-write"',
            'sandbox_mode = "danger-full-access"',
        )
        unsafe_codex_path.write_text(unsafe_codex_text, encoding="utf-8")
        set_bootstrap_profiles(
            unsafe_safe_project,
            project_profile="generic",
            surfaces_profile="all-surfaces",
            codex_policy="safe-interactive",
        )
        unsafe_safe_verify, unsafe_safe_data = verify_json(changerail_root, unsafe_safe_project, fake_env)
        checks.append(
            Check(
                "safe profile rejects full access",
                "pass"
                if unsafe_safe_verify.returncode != 0
                and check_result(
                    unsafe_safe_data,
                    name="bootstrap profile consistency",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                unsafe_safe_verify.stdout.strip(),
            )
        )

        legacy_profile_project = run_dir / "legacy-profile-project"
        shutil.copytree(good_project, legacy_profile_project, symlinks=True)
        legacy_profile_path = legacy_profile_project / "openspec" / "config.yaml"
        legacy_profile_text = legacy_profile_path.read_text(encoding="utf-8")
        if "\nbootstrap:\n" in legacy_profile_text:
            legacy_profile_text = legacy_profile_text.split("\nbootstrap:\n", 1)[0].rstrip() + "\n"
            legacy_profile_path.write_text(legacy_profile_text, encoding="utf-8")
        legacy_profile_verify = run(
            [str(changerail_root / "bin" / "verify-project"), str(legacy_profile_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "legacy profile compatibility passes",
                "pass" if legacy_profile_verify.returncode == 0 else "fail",
                legacy_profile_verify.stdout.strip(),
            )
        )

        locked_project = run_dir / "locked-consumer-project"
        shutil.copytree(good_project, locked_project, symlinks=True)
        write_consumer_lock(locked_project, changerail_root)
        locked_verify, locked_data = verify_json(changerail_root, locked_project, fake_env)
        locked_checks = (
            "consumer lock schema",
            "consumer wiring validity",
            "consumer source revision",
        )
        checks.append(
            Check(
                "matching consumer lock passes",
                "pass"
                if locked_verify.returncode == 0
                and all(check_result(locked_data, name=name, status="pass") for name in locked_checks)
                else "fail",
                locked_verify.stdout.strip(),
            )
        )

        advisory_drift_project = run_dir / "advisory-source-drift"
        shutil.copytree(good_project, advisory_drift_project, symlinks=True)
        write_consumer_lock(
            advisory_drift_project,
            changerail_root,
            enforcement="advisory",
            revision="0" * 40,
        )
        advisory_drift_verify, advisory_drift_data = verify_json(
            changerail_root,
            advisory_drift_project,
            fake_env,
        )
        checks.append(
            Check(
                "advisory source drift is diagnostic",
                "pass"
                if advisory_drift_verify.returncode == 0
                and check_result(
                    advisory_drift_data,
                    name="consumer source revision",
                    status="fail",
                    severity="non-blocking",
                )
                else "fail",
                advisory_drift_verify.stdout.strip(),
            )
        )

        strict_drift_project = run_dir / "strict-source-drift"
        shutil.copytree(good_project, strict_drift_project, symlinks=True)
        write_consumer_lock(
            strict_drift_project,
            changerail_root,
            enforcement="strict",
            revision="0" * 40,
        )
        strict_drift_verify, strict_drift_data = verify_json(
            changerail_root,
            strict_drift_project,
            fake_env,
        )
        checks.append(
            Check(
                "strict source drift blocks",
                "pass"
                if strict_drift_verify.returncode != 0
                and check_result(
                    strict_drift_data,
                    name="consumer source revision",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                strict_drift_verify.stdout.strip(),
            )
        )

        broken_locked_project = run_dir / "broken-advisory-wiring"
        shutil.copytree(good_project, broken_locked_project, symlinks=True)
        write_consumer_lock(broken_locked_project, changerail_root, enforcement="advisory")
        remove_surface_path(broken_locked_project / "bin" / "openspec")
        broken_locked_verify, broken_locked_data = verify_json(
            changerail_root,
            broken_locked_project,
            fake_env,
        )
        checks.append(
            Check(
                "broken advisory wiring blocks",
                "pass"
                if broken_locked_verify.returncode != 0
                and check_result(
                    broken_locked_data,
                    name="consumer wiring validity",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                broken_locked_verify.stdout.strip(),
            )
        )

        unsafe_lock_project = run_dir / "unsafe-consumer-lock"
        shutil.copytree(good_project, unsafe_lock_project, symlinks=True)
        write_consumer_lock(unsafe_lock_project, changerail_root)
        unsafe_lock_path = unsafe_lock_project / CONSUMER_LOCK
        unsafe_lock = json.loads(unsafe_lock_path.read_text(encoding="utf-8"))
        unsafe_lock["changerail"]["source"] = "/opt/changerail"
        unsafe_lock_path.write_text(
            json.dumps(unsafe_lock, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        unsafe_lock_verify, unsafe_lock_data = verify_json(changerail_root, unsafe_lock_project, fake_env)
        checks.append(
            Check(
                "unsafe consumer lock blocks",
                "pass"
                if unsafe_lock_verify.returncode != 0
                and check_result(
                    unsafe_lock_data,
                    name="consumer lock schema",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                unsafe_lock_verify.stdout.strip(),
            )
        )

        missing_schema_checks = [schema for schema in EXPECTED_SCHEMAS if schema not in verify.stdout]
        checks.append(
            Check(
                "all contract schemas checked",
                "pass" if verify.returncode == 0 and not missing_schema_checks else "fail",
                "all expected schemas present" if not missing_schema_checks else "missing: " + ", ".join(missing_schema_checks),
            )
        )
        checks.append(
            Check(
                "maintenance default opt-out skipped",
                "pass"
                if verify.returncode == 0
                and "SKIP maintenance opt-in: not configured" in verify.stdout
                and "bin/changerail-maintenance" not in verify.stdout
                else "fail",
                verify.stdout.strip(),
            )
        )

        maintenance_project = run_dir / "maintenance-project"
        create_fixture(maintenance_project, changerail_root, with_maintenance=True)
        maintenance_verify, maintenance_data = verify_json(changerail_root, maintenance_project, fake_env)
        missing_maintenance_checks = [
            name
            for name in EXPECTED_MAINTENANCE_CHECKS
            if not check_result(maintenance_data, name=name, status="pass")
        ]
        checks.append(
            Check(
                "maintenance opt-in wiring passes",
                "pass"
                if maintenance_verify.returncode == 0
                and not missing_maintenance_checks
                else "fail",
                (
                    "all maintenance checks passed"
                    if not missing_maintenance_checks
                    else "missing passing maintenance checks: " + ", ".join(missing_maintenance_checks)
                )
                + "\n"
                + maintenance_verify.stdout.strip(),
            )
        )

        missing_quality_root = run_dir / "changerail-root-missing-maintenance-quality-schema"
        create_changerail_root_fixture(
            changerail_root,
            missing_quality_root,
            missing_schemas=("changerail-maintenance-quality-rollup.schema.json",),
        )
        missing_quality_project = run_dir / "bad-maintenance-missing-quality-schema"
        create_fixture(missing_quality_project, missing_quality_root, with_maintenance=True)
        missing_quality = run(
            [
                str(changerail_root / "bin" / "verify-project"),
                str(missing_quality_project),
                "--changerail-root",
                str(missing_quality_root),
                "--json",
            ],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "missing maintenance quality schema fails",
                "pass"
                if missing_quality.returncode != 0
                and "schemas/changerail-maintenance-quality-rollup.schema.json" in missing_quality.stdout
                else "fail",
                missing_quality.stdout.strip(),
            )
        )

        missing_proposal_root = run_dir / "changerail-root-missing-maintenance-proposal-schema"
        create_changerail_root_fixture(
            changerail_root,
            missing_proposal_root,
            missing_schemas=("changerail-maintenance-proposal-decision.schema.json",),
        )
        missing_proposal_project = run_dir / "bad-maintenance-missing-proposal-schema"
        create_fixture(missing_proposal_project, missing_proposal_root, with_maintenance=True)
        missing_proposal = run(
            [
                str(changerail_root / "bin" / "verify-project"),
                str(missing_proposal_project),
                "--changerail-root",
                str(missing_proposal_root),
                "--json",
            ],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "missing maintenance proposal-decision schema fails",
                "pass"
                if missing_proposal.returncode != 0
                and "schemas/changerail-maintenance-proposal-decision.schema.json" in missing_proposal.stdout
                else "fail",
                missing_proposal.stdout.strip(),
            )
        )

        partial_maintenance_project = run_dir / "bad-partial-maintenance-project"
        shutil.copytree(good_project, partial_maintenance_project, symlinks=True)
        maintenance_dir = partial_maintenance_project / ".changerail"
        maintenance_dir.mkdir(parents=True, exist_ok=True)
        (maintenance_dir / "knowledge.yaml").write_text(
            "schema: changerail.repository-knowledge.v1\nrecords: []\n",
            encoding="utf-8",
        )
        (maintenance_dir / "maintenance.yaml").write_text(
            "schema: changerail.maintenance-policy.v1\n"
            "catalog_path: .changerail/knowledge.yaml\n"
            "generated_index_path: .changerail/KNOWLEDGE.md\n",
            encoding="utf-8",
        )
        partial_maintenance, partial_maintenance_data = verify_json(changerail_root, partial_maintenance_project, fake_env)
        checks.append(
            Check(
                "partial maintenance opt-in fails",
                "pass"
                if partial_maintenance.returncode != 0
                and check_result(
                    partial_maintenance_data,
                    name="bin/changerail-maintenance",
                    status="fail",
                    severity="blocking",
                )
                and check_result(
                    partial_maintenance_data,
                    name="bin/changerail-maintenance-runner",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                partial_maintenance.stdout.strip(),
            )
        )

        generated_project = run_dir / "generated-windows-project"
        generated_bootstrap = bootstrap_generated_project(changerail_root, generated_project, fake_env)
        if generated_bootstrap.returncode != 0:
            checks.append(Check("generated Windows wiring passes", "fail", generated_bootstrap.stdout.strip()))
        else:
            generated_verify, generated_data = verify_json(changerail_root, generated_project, fake_env)
            checks.append(
                Check(
                    "generated Windows wiring passes",
                    "pass"
                    if generated_verify.returncode == 0
                    and generated_data.get("summary", {}).get("status") in {"pass", "pass-with-diagnostics"}
                    and check_result(generated_data, name="openspec/changerail-wiring.json", status="pass")
                    and check_result(generated_data, name="bin/openspec.cmd", status="pass")
                    else "fail",
                    generated_verify.stdout.strip(),
                )
            )

            stale_project = run_dir / "bad-generated-stale"
            shutil.copytree(generated_project, stale_project, symlinks=True)
            old_text = "stale generated copy fixture fake-secret-sentinel\n"
            stale_target = stale_project / "bin" / "openspec"
            stale_target.write_text(old_text, encoding="utf-8")
            set_manifest_digest(stale_project, "bin/openspec", digest_file(stale_target))
            stale_generated, _ = verify_json(changerail_root, stale_project, fake_env)
            checks.append(
                Check(
                    "stale generated wiring fails",
                    "pass"
                    if stale_generated.returncode != 0
                    and "stale generated wiring" in stale_generated.stdout
                    and "--refresh-wiring" in stale_generated.stdout
                    and "fake-secret-sentinel" not in stale_generated.stdout
                    else "fail",
                    stale_generated.stdout.strip(),
                )
            )

            missing_project = run_dir / "bad-generated-missing"
            shutil.copytree(generated_project, missing_project, symlinks=True)
            (missing_project / "bin" / "openspec").unlink()
            missing_generated, missing_data = verify_json(changerail_root, missing_project, fake_env)
            checks.append(
                Check(
                    "missing generated artifact fails",
                    "pass"
                    if missing_generated.returncode != 0
                    and "generated artifact missing" in missing_generated.stdout
                    and check_result(missing_data, name="bin/openspec", status="fail", severity="blocking")
                    else "fail",
                    missing_generated.stdout.strip(),
                )
            )

            divergent_project = run_dir / "bad-generated-project-owned-divergence"
            shutil.copytree(generated_project, divergent_project, symlinks=True)
            (divergent_project / "bin" / "openspec").write_text(
                "project-owned change fake-secret-sentinel\n",
                encoding="utf-8",
            )
            divergent_generated, _ = verify_json(changerail_root, divergent_project, fake_env)
            checks.append(
                Check(
                    "project-owned generated divergence fails",
                    "pass"
                    if divergent_generated.returncode != 0
                    and "project-owned divergence" in divergent_generated.stdout
                    and "fake-secret-sentinel" not in divergent_generated.stdout
                    else "fail",
                    divergent_generated.stdout.strip(),
                )
            )

            drift_valid, drift_valid_data = drift_report(
                changerail_root,
                generated_project,
                run_dir / "drift-generated-valid.json",
                fake_env,
            )
            checks.append(
                Check(
                    "drift generated wiring passes",
                    "pass"
                    if drift_valid.returncode == 0
                    and first_project_class(drift_valid_data) == "changerail_source"
                    and drift_valid_data.get("summary", {}).get("status") == "pass"
                    else "fail",
                    drift_valid.stdout.strip(),
                )
            )

            drift_stale, drift_stale_data = drift_report(
                changerail_root,
                stale_project,
                run_dir / "drift-generated-stale.json",
                fake_env,
            )
            checks.append(
                Check(
                    "drift stale generated wiring fails",
                    "pass"
                    if drift_stale.returncode != 0
                    and first_project_class(drift_stale_data) == "broken_wiring"
                    and "stale generated wiring" in json.dumps(drift_stale_data, ensure_ascii=False)
                    and "fake-secret-sentinel" not in json.dumps(drift_stale_data, ensure_ascii=False)
                    else "fail",
                    drift_stale.stdout.strip(),
                )
            )

            drift_divergent, drift_divergent_data = drift_report(
                changerail_root,
                divergent_project,
                run_dir / "drift-generated-diverged.json",
                fake_env,
            )
            checks.append(
                Check(
                    "drift project-owned generated divergence fails",
                    "pass"
                    if drift_divergent.returncode != 0
                    and first_project_class(drift_divergent_data) == "broken_wiring"
                    and "project-owned divergence" in json.dumps(drift_divergent_data, ensure_ascii=False)
                    and "fake-secret-sentinel" not in json.dumps(drift_divergent_data, ensure_ascii=False)
                    else "fail",
                    drift_divergent.stdout.strip(),
                )
            )

            lockless_refresh = run(
                [
                    str(changerail_root / "bin" / "bootstrap-project"),
                    str(generated_project),
                    "--refresh-wiring",
                    "--skip-verify",
                ],
                changerail_root,
                fake_env,
            )
            checks.append(
                Check(
                    "lockless generated refresh requires adoption",
                    "pass"
                    if lockless_refresh.returncode != 0
                    and "adopt-lockless-wiring" in lockless_refresh.stdout
                    and not (generated_project / CONSUMER_LOCK).exists()
                    else "fail",
                    lockless_refresh.stdout.strip(),
                )
            )
            write_generated_consumer_lock(generated_project, changerail_root)
            refresh = run(
                [
                    str(changerail_root / "bin" / "bootstrap-project"),
                    str(generated_project),
                    "--refresh-wiring",
                ],
                changerail_root,
                fake_env,
            )
            checks.append(
                Check(
                    "generated wiring refresh passes",
                    "pass" if refresh.returncode == 0 and "wiring refreshed" in refresh.stdout else "fail",
                    refresh.stdout.strip(),
                )
            )
            stale_refresh_project = run_dir / "generated-windows-stale-refresh"
            shutil.copytree(generated_project, stale_refresh_project, symlinks=True)
            set_manifest_digest(stale_refresh_project, "bin/verify-project.cmd", "sha256:" + "0" * 64)
            stale_refresh_before, _ = verify_json(changerail_root, stale_refresh_project, fake_env)
            stale_refresh = run(
                [
                    str(changerail_root / "bin" / "bootstrap-project"),
                    str(stale_refresh_project),
                    "--refresh-wiring",
                    "--skip-verify",
                ],
                changerail_root,
                fake_env,
            )
            stale_refresh_after, _ = verify_json(changerail_root, stale_refresh_project, fake_env)
            checks.append(
                Check(
                    "stale generated wiring refresh passes",
                    "pass"
                    if stale_refresh_before.returncode != 0
                    and "stale generated wiring" in stale_refresh_before.stdout
                    and stale_refresh.returncode == 0
                    and "wiring refreshed" in stale_refresh.stdout
                    and stale_refresh_after.returncode == 0
                    else "fail",
                    "\n".join(
                        part.strip()
                        for part in (stale_refresh_before.stdout, stale_refresh.stdout, stale_refresh_after.stdout)
                        if part.strip()
                    ),
                )
            )

            maintenance_generated_project = run_dir / "generated-windows-maintenance-project"
            maintenance_generated_bootstrap = bootstrap_generated_project(
                changerail_root,
                maintenance_generated_project,
                fake_env,
                with_maintenance=True,
            )
            if maintenance_generated_bootstrap.returncode != 0:
                checks.append(
                    Check(
                        "generated Windows maintenance wiring passes",
                        "fail",
                        maintenance_generated_bootstrap.stdout.strip(),
                    )
                )
            else:
                maintenance_generated_verify, maintenance_generated_data = verify_json(
                    changerail_root,
                    maintenance_generated_project,
                    fake_env,
                )
                checks.append(
                    Check(
                        "generated Windows maintenance wiring passes",
                        "pass"
                        if maintenance_generated_verify.returncode == 0
                        and check_result(
                            maintenance_generated_data,
                            name="bin/changerail-maintenance",
                            status="pass",
                        )
                        and check_result(
                            maintenance_generated_data,
                            name="bin/changerail-maintenance-runner",
                            status="pass",
                        )
                        and check_result(
                            maintenance_generated_data,
                            name="bin/changerail-maintenance.cmd",
                            status="pass",
                        )
                        and check_result(
                            maintenance_generated_data,
                            name="bin/changerail-maintenance-runner.cmd",
                            status="pass",
                        )
                        else "fail",
                        maintenance_generated_verify.stdout.strip(),
                    )
                )

                stale_maintenance_project = run_dir / "bad-generated-maintenance-stale"
                shutil.copytree(maintenance_generated_project, stale_maintenance_project, symlinks=True)
                stale_maintenance_target = stale_maintenance_project / "bin" / "changerail-maintenance-runner"
                stale_maintenance_target.write_text(
                    "stale generated maintenance runner fake-secret-sentinel\n",
                    encoding="utf-8",
                )
                set_manifest_digest(
                    stale_maintenance_project,
                    "bin/changerail-maintenance-runner",
                    digest_file(stale_maintenance_target),
                )
                stale_maintenance, _ = verify_json(changerail_root, stale_maintenance_project, fake_env)
                checks.append(
                    Check(
                        "stale generated maintenance helper fails",
                        "pass"
                        if stale_maintenance.returncode != 0
                        and "stale generated wiring" in stale_maintenance.stdout
                        and "--refresh-wiring" in stale_maintenance.stdout
                        and "fake-secret-sentinel" not in stale_maintenance.stdout
                        else "fail",
                        stale_maintenance.stdout.strip(),
                    )
                )

                divergent_maintenance_project = run_dir / "bad-generated-maintenance-divergence"
                shutil.copytree(maintenance_generated_project, divergent_maintenance_project, symlinks=True)
                (divergent_maintenance_project / "bin" / "changerail-maintenance-runner").write_text(
                    "project-owned maintenance runner change fake-secret-sentinel\n",
                    encoding="utf-8",
                )
                divergent_maintenance, _ = verify_json(changerail_root, divergent_maintenance_project, fake_env)
                checks.append(
                    Check(
                        "project-owned generated maintenance divergence fails",
                        "pass"
                        if divergent_maintenance.returncode != 0
                        and "project-owned divergence" in divergent_maintenance.stdout
                        and "fake-secret-sentinel" not in divergent_maintenance.stdout
                        else "fail",
                        divergent_maintenance.stdout.strip(),
                    )
                )

    if shard == 1:
        symlink_proof_project = run_dir / "symlink-fallback-proof-project"
        symlink_proof = write_windows_fallback_proof(run_dir, "symlink")
        symlink_positive = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(symlink_proof_project),
                "--name",
                "symlink-fallback-proof-project",
                "--kind",
                "generic",
                "--wiring-platform",
                "windows",
                "--wiring-backend",
                "symlink",
                "--windows-fallback-proof",
                str(symlink_proof),
            ],
            changerail_root,
            fake_env,
        )
        if symlink_positive.returncode != 0:
            checks.append(Check("Windows symlink fallback proof verifies", "fail", symlink_positive.stdout.strip()))
        else:
            symlink_verify, symlink_data = verify_json(changerail_root, symlink_proof_project, fake_env)
            checks.append(
                Check(
                    "Windows symlink fallback proof verifies",
                    "pass"
                    if symlink_verify.returncode == 0
                    and check_result(symlink_data, name="Windows symlink fallback proof", status="pass")
                    else "fail",
                    symlink_verify.stdout.strip(),
                )
            )
            manifest = generated_manifest(symlink_proof_project)
            manifest["fallback_proof"] = status_only_windows_fallback_proof("symlink")
            write_generated_manifest(symlink_proof_project, manifest)
            status_only_verify = run(
                [str(changerail_root / "bin" / "verify-project"), str(symlink_proof_project)],
                changerail_root,
                fake_env,
            )
            checks.append(
                Check(
                    "status-only fallback proof fails verification",
                    "pass"
                    if status_only_verify.returncode != 0
                    and "invalid symlink fallback proof" in status_only_verify.stdout
                    else "fail",
                    status_only_verify.stdout.strip(),
                )
            )
            manifest = generated_manifest(symlink_proof_project)
            manifest["fallback_proof"] = hash_only_windows_fallback_proof("symlink")
            write_generated_manifest(symlink_proof_project, manifest)
            hash_only_verify = run(
                [str(changerail_root / "bin" / "verify-project"), str(symlink_proof_project)],
                changerail_root,
                fake_env,
            )
            checks.append(
                Check(
                    "hash-only fallback proof fails verification",
                    "pass"
                    if hash_only_verify.returncode != 0
                    and "invalid symlink fallback proof" in hash_only_verify.stdout
                    else "fail",
                    hash_only_verify.stdout.strip(),
                )
            )

        symlink_fallback = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(run_dir / "bad-windows-symlink-fallback"),
                "--name",
                "bad-windows-symlink-fallback",
                "--kind",
                "generic",
                "--wiring-platform",
                "windows",
                "--wiring-backend",
                "symlink",
                "--skip-verify",
            ],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "Windows symlink fallback proof required",
                "pass"
                if symlink_fallback.returncode != 0
                and "--windows-fallback-proof" in symlink_fallback.stdout
                else "fail",
                symlink_fallback.stdout.strip(),
            )
        )

        junction_fallback = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(run_dir / "bad-windows-junction-fallback"),
                "--name",
                "bad-windows-junction-fallback",
                "--kind",
                "generic",
                "--wiring-platform",
                "windows",
                "--wiring-backend",
                "junction",
                "--skip-verify",
            ],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "Windows junction fallback proof required",
                "pass"
                if junction_fallback.returncode != 0
                and "--windows-fallback-proof" in junction_fallback.stdout
                else "fail",
                junction_fallback.stdout.strip(),
            )
        )

        junction_dry_run = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(run_dir / "junction-fallback-dry-run"),
                "--name",
                "junction-fallback-dry-run",
                "--kind",
                "generic",
                "--wiring-platform",
                "windows",
                "--wiring-backend",
                "junction",
                "--windows-fallback-proof",
                str(write_windows_fallback_proof(run_dir, "junction")),
                "--dry-run",
            ],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "Windows junction fallback proof dry-run passes",
                "pass"
                if junction_dry_run.returncode == 0
                and "PLAN fallback-proof" in junction_dry_run.stdout
                and "PLAN junction directory" in junction_dry_run.stdout
                else "fail",
                junction_dry_run.stdout.strip(),
            )
        )

        auth_marker_project = run_dir / "auth-marker-project"
        shutil.copytree(good_project, auth_marker_project, symlinks=True)
        sentinel = "fake-secret-sentinel"
        (auth_marker_project / ".codex" / "auth.json").write_text(sentinel + "\n", encoding="utf-8")
        auth_marker = run([str(changerail_root / "bin" / "verify-project"), str(auth_marker_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "auth marker advisory passes",
                "pass"
                if auth_marker.returncode == 0
                and "INFO delivery runner auth readiness" in auth_marker.stdout
                and ".codex/auth.json" in auth_marker.stdout
                and sentinel not in auth_marker.stdout
                else "fail",
                auth_marker.stdout.strip(),
            )
        )

        auth_conflict_project = run_dir / "auth-conflict-project"
        shutil.copytree(good_project, auth_conflict_project, symlinks=True)
        os.symlink("../missing-auth.json", auth_conflict_project / ".codex" / "auth.json")
        auth_conflict = run(
            [str(changerail_root / "bin" / "verify-project"), str(auth_conflict_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "auth conflict requires owner review",
                "pass"
                if auth_conflict.returncode == 0
                and "WARN delivery runner auth readiness" in auth_conflict.stdout
                and "manual owner review" in auth_conflict.stdout
                and "--link-codex-auth" not in auth_conflict.stdout
                else "fail",
                auth_conflict.stdout.strip(),
            )
        )

        auth_env = {**fake_env, "CODEX_AUTH_TOKEN": sentinel}
        auth_env_result = run([str(changerail_root / "bin" / "verify-project"), str(good_project)], changerail_root, auth_env)
        checks.append(
            Check(
                "auth environment advisory passes",
                "pass"
                if auth_env_result.returncode == 0
                and "INFO delivery runner auth readiness" in auth_env_result.stdout
                and "CODEX_AUTH_TOKEN" in auth_env_result.stdout
                and sentinel not in auth_env_result.stdout
                else "fail",
                auth_env_result.stdout.strip(),
            )
        )

        tracked_auth_toml_project = run_dir / "bad-tracked-auth-toml"
        shutil.copytree(good_project, tracked_auth_toml_project, symlinks=True)
        (tracked_auth_toml_project / ".codex" / "auth.toml").write_text("token = \"fake-secret-sentinel\"\n", encoding="utf-8")
        for git_args in (
            ("init",),
            ("add", ".gitignore"),
            ("add", "-f", ".codex/auth.toml"),
        ):
            git_result = git(tracked_auth_toml_project, *git_args)
            if git_result.returncode != 0:
                checks.append(Check("tracked auth.toml fails", "fail", git_result.stdout.strip()))
                break
        else:
            tracked_auth = run(
                [str(changerail_root / "bin" / "verify-project"), str(tracked_auth_toml_project)],
                changerail_root,
                fake_env,
            )
            checks.append(
                Check(
                    "tracked auth.toml fails",
                    "pass"
                    if tracked_auth.returncode != 0
                    and "tracked runtime/auth files" in tracked_auth.stdout
                    and ".codex/auth.toml" in tracked_auth.stdout
                    and "fake-secret-sentinel" not in tracked_auth.stdout
                    else "fail",
                    tracked_auth.stdout.strip(),
                )
            )

        bad_project = run_dir / "bad-missing-runtime-ignore"
        shutil.copytree(good_project, bad_project, symlinks=True)
        gitignore = bad_project / ".gitignore"
        gitignore.write_text(
            "\n".join(line for line in gitignore.read_text(encoding="utf-8").splitlines() if line.strip() != ".runtime/")
            + "\n",
            encoding="utf-8",
        )
        negative = run([str(changerail_root / "bin" / "verify-project"), str(bad_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "missing runtime ignore fails",
                "pass" if negative.returncode != 0 else "fail",
                negative.stdout.strip(),
            )
        )

        stale_project = run_dir / "bad-stale-opsx-wiring"
        shutil.copytree(good_project, stale_project, symlinks=True)
        symlink_force(changerail_root / "claude" / "commands" / "changerail", stale_project / ".claude" / "commands" / "opsx")
        symlink_force(changerail_root / "skills" / "changerail-do", stale_project / ".codex" / "skills" / "opsx-do")
        symlink_force(changerail_root / "bin" / "changerail-review-verdict", stale_project / "bin" / "opsx-review-verdict")
        stale = run([str(changerail_root / "bin" / "verify-project"), str(stale_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "stale OPSX wiring fails",
                "pass" if stale.returncode != 0 and "stale OPSX wiring" in stale.stdout else "fail",
                stale.stdout.strip(),
            )
        )

        missing_chrl_project = run_dir / "bad-missing-chrl-alias"
        shutil.copytree(good_project, missing_chrl_project, symlinks=True)
        (missing_chrl_project / ".codex" / "skills" / "chrl-do").unlink()
        (missing_chrl_project / ".claude" / "commands" / "chrl").unlink()
        missing_chrl = run(
            [str(changerail_root / "bin" / "verify-project"), str(missing_chrl_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "missing chrl alias fails",
                "pass" if missing_chrl.returncode != 0 and "chrl" in missing_chrl.stdout else "fail",
                missing_chrl.stdout.strip(),
            )
        )

        codex_only_project = run_dir / "codex-only-profile-project"
        shutil.copytree(good_project, codex_only_project, symlinks=True)
        set_verification_policy(codex_only_project, surfaces={"claude": "optional"})
        remove_surface_path(codex_only_project / ".claude" / "skills")
        remove_surface_path(codex_only_project / ".claude" / "commands" / "changerail")
        remove_surface_path(codex_only_project / ".claude" / "commands" / "chrl")
        codex_only, codex_only_data = verify_json(changerail_root, codex_only_project, fake_env)
        checks.append(
            Check(
                "codex-only profile passes with diagnostics",
                "pass"
                if codex_only.returncode == 0
                and codex_only_data.get("summary", {}).get("status") == "pass-with-diagnostics"
                and check_result(codex_only_data, name=".claude/skills", status="fail", severity="non-blocking")
                else "fail",
                codex_only.stdout.strip(),
            )
        )

        strict_missing_claude_project = run_dir / "bad-strict-missing-claude"
        shutil.copytree(good_project, strict_missing_claude_project, symlinks=True)
        remove_surface_path(strict_missing_claude_project / ".claude" / "commands" / "changerail")
        strict_missing_claude, strict_missing_claude_data = verify_json(
            changerail_root,
            strict_missing_claude_project,
            fake_env,
        )
        checks.append(
            Check(
                "default all-surfaces missing Claude fails",
                "pass"
                if strict_missing_claude.returncode != 0
                and strict_missing_claude_data.get("summary", {}).get("status") == "fail"
                and check_result(
                    strict_missing_claude_data,
                    name=".claude/commands/changerail",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                strict_missing_claude.stdout.strip(),
            )
        )

        forbidden_mcp_project = run_dir / "bad-forbidden-legacy-mcp"
        shutil.copytree(good_project, forbidden_mcp_project, symlinks=True)
        set_verification_policy(forbidden_mcp_project, surfaces={"legacy_mcp": "forbidden"})
        forbidden_mcp, forbidden_mcp_data = verify_json(changerail_root, forbidden_mcp_project, fake_env)
        checks.append(
            Check(
                "forbidden legacy MCP artifact fails",
                "pass"
                if forbidden_mcp.returncode != 0
                and forbidden_mcp_data.get("summary", {}).get("status") == "fail"
                and check_result(forbidden_mcp_data, name=".mcp.json", status="fail", severity="blocking")
                else "fail",
                forbidden_mcp.stdout.strip(),
            )
        )

        weaken_target_project = run_dir / "bad-weaken-targeted-validation"
        shutil.copytree(good_project, weaken_target_project, symlinks=True)
        set_verification_policy(weaken_target_project, targeted="optional")
        weaken_target, weaken_target_data = verify_json(changerail_root, weaken_target_project, fake_env)
        checks.append(
            Check(
                "mandatory targeted validation weakening fails",
                "pass"
                if weaken_target.returncode != 0
                and weaken_target_data.get("summary", {}).get("status") == "fail"
                and check_result(weaken_target_data, name="verification policy", status="fail", severity="blocking")
                else "fail",
                weaken_target.stdout.strip(),
            )
        )

        coverage_project = run_dir / "coverage-map-project"
        shutil.copytree(good_project, coverage_project, symlinks=True)
        configure_verification_coverage(
            coverage_project,
            "schema: changerail.verification-coverage.v1\n"
            "entries:\n"
            "  - id: python-runtime-route\n"
            "    applies_to:\n"
            "      path_globs: [\"src/**/*.py\"]\n"
            "      operation_kinds: [add, modify]\n"
            "      surface_kinds: [python.runtime]\n"
            "    invariant: \"positive runtime route remains observable\"\n"
            "    oracle:\n"
            "      kind: command\n"
            "      ref: pytest-positive-route\n"
            "    required_evidence:\n"
            "      - kind: command\n"
            "        oracle_ref: pytest-positive-route\n"
            "      - kind: runtime\n"
            "        oracle_ref: pytest-positive-route\n"
            "  - id: python-type-policy\n"
            "    applies_to:\n"
            "      path_globs: [\"src/**/*.py\"]\n"
            "    invariant: \"project-owned type policy remains clean when configured\"\n"
            "    oracle:\n"
            "      kind: typecheck\n"
            "      ref: mypy-explicit-policy\n"
            "    required_evidence:\n"
            "      - kind: typecheck\n"
            "        oracle_ref: mypy-explicit-policy\n",
        )
        coverage_valid, coverage_valid_data = verify_json(changerail_root, coverage_project, fake_env)
        checks.append(
            Check(
                "configured verification coverage map validates",
                "pass"
                if coverage_valid.returncode == 0
                and check_result(
                    coverage_valid_data,
                    name="verification coverage map",
                    status="pass",
                    severity="blocking",
                )
                else "fail",
                coverage_valid.stdout.strip(),
            )
        )

        bad_coverage_project = run_dir / "bad-coverage-map-project"
        shutil.copytree(good_project, bad_coverage_project, symlinks=True)
        configure_verification_coverage(
            bad_coverage_project,
            "schema: changerail.verification-coverage.v1\n"
            "entries:\n"
            "  - id: python-runtime-route\n"
            "    applies_to:\n"
            "      path_globs: [\"/absolute/**/*.py\"]\n"
            "    invariant: \"unsafe selector should fail\"\n"
            "    oracle:\n"
            "      kind: command\n"
            "      ref: pytest-positive-route\n"
            "    required_evidence:\n"
            "      - kind: command\n"
            "        oracle_ref: another-oracle\n",
        )
        coverage_invalid, coverage_invalid_data = verify_json(changerail_root, bad_coverage_project, fake_env)
        checks.append(
            Check(
                "invalid verification coverage map fails closed",
                "pass"
                if coverage_invalid.returncode != 0
                and coverage_invalid_data.get("summary", {}).get("status") == "fail"
                and check_result(
                    coverage_invalid_data,
                    name="verification coverage map",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                coverage_invalid.stdout.strip(),
            )
        )

        baseline_debt_project = run_dir / "baseline-debt-project"
        shutil.copytree(good_project, baseline_debt_project, symlinks=True)
        bad_spec = baseline_debt_project / "openspec" / "specs" / "bad" / "spec.md"
        bad_spec.parent.mkdir(parents=True, exist_ok=True)
        bad_spec.write_text(
            "# bad Specification\n\n"
            "## Purpose\nBad.\n"
            "## Requirements\n"
            "### Requirement: Bad baseline\n"
            "No normative keyword here.\n\n"
            "#### Scenario: Bad\n"
            "- **WHEN** it runs\n"
            "- **THEN** it fails\n",
            encoding="utf-8",
        )
        undeclared_baseline, undeclared_baseline_data = verify_json(changerail_root, baseline_debt_project, fake_env)
        checks.append(
            Check(
                "undeclared baseline debt fails closed",
                "pass"
                if undeclared_baseline.returncode != 0
                and undeclared_baseline_data.get("summary", {}).get("status") == "fail"
                and check_result(
                    undeclared_baseline_data,
                    name="bin/openspec validate --all --strict",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                undeclared_baseline.stdout.strip(),
            )
        )
        config = baseline_debt_project / "openspec" / "config.yaml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "  baseline_debt: []",
                "  baseline_debt:\n"
                "    - command: \"bin/openspec validate --all --strict\"\n"
                "      residual_risk: \"known project-wide OpenSpec baseline debt\"\n"
                "      rationale: \"fixture debt is not card-owned\"",
            ),
            encoding="utf-8",
        )
        declared_baseline, declared_baseline_data = verify_json(changerail_root, baseline_debt_project, fake_env)
        checks.append(
            Check(
                "declared baseline debt is diagnostic",
                "pass"
                if declared_baseline.returncode == 0
                and declared_baseline_data.get("summary", {}).get("status") == "pass-with-diagnostics"
                and check_result(
                    declared_baseline_data,
                    name="bin/openspec validate --all --strict",
                    status="fail",
                    severity="non-blocking",
                )
                else "fail",
                declared_baseline.stdout.strip(),
            )
        )

        targeted_debt_project = run_dir / "bad-baseline-debt-targeted-change"
        shutil.copytree(good_project, targeted_debt_project, symlinks=True)
        set_verification_policy(
            targeted_debt_project,
            surfaces=None,
            targeted="required",
        )
        config = targeted_debt_project / "openspec" / "config.yaml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "  baseline_debt: []",
                "  baseline_debt:\n"
                "    - command: \"bin/openspec validate --all --strict\"\n"
                "      residual_risk: \"known project-wide OpenSpec baseline debt\"\n"
                "      rationale: \"fixture debt is not card-owned\"",
            ),
            encoding="utf-8",
        )
        active_spec = targeted_debt_project / "openspec" / "changes" / "card-owned-invalid" / "specs" / "broken" / "spec.md"
        active_spec.parent.mkdir(parents=True, exist_ok=True)
        active_spec.write_text(
            "## ADDED Requirements\n\n"
            "### Requirement: Card-owned invalid requirement\n"
            "No normative keyword here.\n\n"
            "#### Scenario: Card-owned invalid scenario\n"
            "- **WHEN** the targeted change is validated\n"
            "- **THEN** validation fails\n",
            encoding="utf-8",
        )
        (targeted_debt_project / "openspec" / "changes" / "card-owned-invalid" / "proposal.md").write_text(
            "## Why\n\nTest.\n",
            encoding="utf-8",
        )
        (targeted_debt_project / "openspec" / "changes" / "card-owned-invalid" / "tasks.md").write_text(
            "- [ ] Test\n",
            encoding="utf-8",
        )
        targeted_debt, targeted_debt_data = verify_json(changerail_root, targeted_debt_project, fake_env)
        checks.append(
            Check(
                "baseline debt cannot mask targeted change failure",
                "pass"
                if targeted_debt.returncode != 0
                and targeted_debt_data.get("summary", {}).get("status") == "fail"
                and check_result(
                    targeted_debt_data,
                    name="targeted OpenSpec validation",
                    status="fail",
                    severity="blocking",
                )
                else "fail",
                targeted_debt.stdout.strip(),
            )
        )

        bad_scope_project = run_dir / "bad-portable-scope"
        shutil.copytree(good_project, bad_scope_project, symlinks=True)
        mcp = bad_scope_project / ".mcp.json"
        mcp.write_text(mcp.read_text(encoding="utf-8").replace('"."', '".."'), encoding="utf-8")
        codex = bad_scope_project / ".codex" / "config.toml"
        codex.write_text(codex.read_text(encoding="utf-8").replace('"."]', '".."]'), encoding="utf-8")
        bad_scope = run([str(changerail_root / "bin" / "verify-project"), str(bad_scope_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "unsafe portable scope fails",
                "pass" if bad_scope.returncode != 0 and "scope does not cover project root" in bad_scope.stdout else "fail",
                bad_scope.stdout.strip(),
            )
        )

        unpinned_project = run_dir / "bad-unpinned-mcp"
        shutil.copytree(good_project, unpinned_project, symlinks=True)
        for rel_path in MCP_FILES:
            path = unpinned_project / rel_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "@modelcontextprotocol/server-filesystem@2026.7.10",
                    "@modelcontextprotocol/server-filesystem",
                ),
                encoding="utf-8",
            )
        unpinned = run([str(changerail_root / "bin" / "verify-project"), str(unpinned_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "unpinned MCP package fails",
                "pass" if unpinned.returncode != 0 and "MCP npm pins" in unpinned.stdout else "fail",
                unpinned.stdout.strip(),
            )
        )

        tampered_env = {
            **fake_env,
            "CHANGERAIL_FAKE_NPM_TAMPER": "@modelcontextprotocol/server-filesystem@2026.7.10",
        }
        tampered = run([str(changerail_root / "bin" / "verify-project"), str(good_project)], changerail_root, tampered_env)
        checks.append(
            Check(
                "tampered MCP integrity fails",
                "pass" if tampered.returncode != 0 and "registry integrity mismatch" in tampered.stdout else "fail",
                tampered.stdout.strip(),
            )
        )

        optional_project = run_dir / "optional-browser-mcp-project"
        shutil.copytree(good_project, optional_project, symlinks=True)
        add_json_mcp_server(optional_project, "playwrightDirect", ["-y", "@playwright/mcp@0.0.68"])
        add_json_mcp_server(
            optional_project,
            "chromePackageEquals",
            ["-y", "--package=chrome-devtools-mcp@0.20.3", "chrome-devtools-mcp"],
        )
        add_codex_mcp_server(
            optional_project,
            "playwright_package_space",
            ["-y", "--package", "@playwright/mcp@0.0.68", "playwright-mcp"],
        )
        optional = run([str(changerail_root / "bin" / "verify-project"), str(optional_project)], changerail_root, fake_env)
        checks.append(
            Check(
                "optional browser MCP direct and package forms pass",
                "pass" if optional.returncode == 0 else "fail",
                optional.stdout.strip(),
            )
        )

        missing_version_project = run_dir / "bad-optional-browser-missing-version"
        shutil.copytree(good_project, missing_version_project, symlinks=True)
        add_json_mcp_server(missing_version_project, "playwrightMissingVersion", ["-y", "--package=@playwright/mcp"])
        missing_version = run(
            [str(changerail_root / "bin" / "verify-project"), str(missing_version_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "optional browser MCP missing version fails",
                "pass" if missing_version.returncode != 0 and "not exact-version pinned" in missing_version.stdout else "fail",
                missing_version.stdout.strip(),
            )
        )

        missing_lock_project = run_dir / "bad-optional-browser-missing-lock"
        shutil.copytree(good_project, missing_lock_project, symlinks=True)
        add_json_mcp_server(missing_lock_project, "playwrightMissingLock", ["-y", "@playwright/mcp@0.0.69"])
        missing_lock = run(
            [str(changerail_root / "bin" / "verify-project"), str(missing_lock_project)],
            changerail_root,
            fake_env,
        )
        checks.append(
            Check(
                "optional browser MCP missing lock fails",
                "pass" if missing_lock.returncode != 0 and "absent from mcp-npm-lock.json" in missing_lock.stdout else "fail",
                missing_lock.stdout.strip(),
            )
        )

        optional_tampered_env = {
            **fake_env,
            "CHANGERAIL_FAKE_NPM_TAMPER": "@playwright/mcp@0.0.68",
        }
        optional_tampered = run(
            [str(changerail_root / "bin" / "verify-project"), str(optional_project)],
            changerail_root,
            optional_tampered_env,
        )
        checks.append(
            Check(
                "optional browser MCP tampered integrity fails",
                "pass"
                if optional_tampered.returncode != 0
                and "registry integrity mismatch for @playwright/mcp@0.0.68" in optional_tampered.stdout
                else "fail",
                optional_tampered.stdout.strip(),
            )
        )

        default_offenders = browser_mcp_default_offenders(changerail_root)
        checks.append(
            Check(
                "optional browser MCP absent from defaults",
                "pass" if not default_offenders else "fail",
                "no browser MCP packages in root config or templates"
                if not default_offenders
                else "; ".join(default_offenders),
            )
        )

    failed = sum(1 for check in checks if check.status != "pass")
    return {
        "schema": SCHEMA,
        "run_dir": str(run_dir),
        "changerail_root": str(changerail_root),
        "summary": {
            "status": "fail" if failed else "pass",
            "total": len(checks),
            "passed": len(checks) - failed,
            "failed": failed,
        },
        "checks": [asdict(check) for check in checks],
    }


class WorkerProtocolError(RuntimeError):
    pass


def summarize_checks(checks: list[dict[str, str]]) -> dict[str, object]:
    failed = sum(1 for check in checks if check["status"] != "pass")
    return {
        "status": "fail" if failed else "pass",
        "total": len(checks),
        "passed": len(checks) - failed,
        "failed": failed,
    }


def synthetic_shard_report(changerail_root: Path, run_dir: Path, shard: int) -> dict[str, object]:
    checks = [
        {
            "name": name,
            "status": "pass",
            "message": f"test-only root={run_dir};pid={os.getpid()}",
        }
        for name in SHARD_SCENARIOS[shard]
    ]
    return {
        "schema": SCHEMA,
        "run_dir": str(run_dir),
        "changerail_root": str(changerail_root),
        "summary": summarize_checks(checks),
        "checks": checks,
    }


def smoke_worker(
    changerail_root: Path,
    worker_root: Path,
    shard: int,
    terminal: Connection,
    test_fault: str | None,
    test_synthetic: bool,
) -> None:
    try:
        if hasattr(os, "setsid"):
            os.setsid()
        if test_fault == "crash":
            os._exit(86)
        if test_fault == "timeout":
            time.sleep(3600)
        if test_fault == "exception":
            raise RuntimeError("injected worker exception")

        worker_root.mkdir(parents=True, exist_ok=False)
        with tempfile.TemporaryDirectory(prefix="fixture-", dir=worker_root) as fixture_root:
            fixture_path = Path(fixture_root)
            report = (
                synthetic_shard_report(changerail_root, fixture_path, shard)
                if test_synthetic
                else run_smoke_shard(changerail_root, fixture_path, shard)
            )
            if test_fault == "scenario-failure":
                report["checks"][0]["status"] = "fail"
                report["checks"][0]["message"] = "injected scenario failure"
                report["summary"] = summarize_checks(report["checks"])
            if test_fault == "delay":
                time.sleep(0.15)
            if test_fault == "missing":
                return

            envelope: object = {"shard": shard, "report": report}
            if test_fault == "malformed":
                envelope = {"shard": shard, "report": "malformed"}
            terminal.send(envelope)
            if test_fault == "duplicate":
                terminal.send(envelope)
    except BaseException as exc:
        try:
            terminal.send(
                {
                    "shard": shard,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(limit=8),
                }
            )
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        terminal.close()


def terminate_worker(process: multiprocessing.Process) -> None:
    if process.pid is None or not process.is_alive():
        return
    if hasattr(os, "killpg"):
        try:
            if os.getpgid(process.pid) == process.pid:
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except ProcessLookupError:
            pass
    else:
        process.terminate()
    process.join(timeout=2)
    if process.is_alive():
        if hasattr(os, "killpg"):
            try:
                if os.getpgid(process.pid) == process.pid:
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.join(timeout=2)


def validate_shard_report(shard: int, report: object) -> dict[str, object]:
    if not isinstance(report, dict):
        raise WorkerProtocolError(f"worker {shard}: malformed terminal report (expected object)")
    if report.get("schema") != SCHEMA:
        raise WorkerProtocolError(f"worker {shard}: malformed terminal report schema")
    checks = report.get("checks")
    if not isinstance(checks, list):
        raise WorkerProtocolError(f"worker {shard}: malformed terminal checks")
    for index, check in enumerate(checks):
        if not isinstance(check, dict) or set(check) != {"name", "status", "message"}:
            raise WorkerProtocolError(f"worker {shard}: malformed check result at index {index}")
        if not all(isinstance(check[field], str) for field in ("name", "status", "message")):
            raise WorkerProtocolError(f"worker {shard}: non-string check result at index {index}")
        if check["status"] not in {"pass", "fail"}:
            raise WorkerProtocolError(f"worker {shard}: invalid check status at index {index}")
    names = tuple(check["name"] for check in checks)
    expected = SHARD_SCENARIOS[shard]
    if names != expected:
        missing = [name for name in expected if name not in names]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        unexpected = [name for name in names if name not in expected]
        raise WorkerProtocolError(
            f"worker {shard}: scenario parity failure: expected={len(expected)} actual={len(names)} "
            f"missing={missing} duplicate={duplicates} unexpected={unexpected}"
        )
    summary = report.get("summary")
    expected_summary = summarize_checks(checks)
    if summary != expected_summary:
        raise WorkerProtocolError(f"worker {shard}: malformed or inconsistent terminal summary")
    return report


def run_smoke(
    changerail_root: Path,
    run_dir: Path,
    *,
    _worker_timeout: float = SHARD_TIMEOUT_SECONDS,
    _test_faults: dict[int, str] | None = None,
    _test_synthetic: bool = False,
) -> dict[str, object]:
    if WORKER_COUNT != 2 or len(SHARD_SCENARIOS) != WORKER_COUNT:
        raise WorkerProtocolError("verify-project smoke requires exactly two configured workers")
    if _worker_timeout <= 0:
        raise ValueError("worker timeout must be positive")

    context = multiprocessing.get_context("fork" if hasattr(os, "fork") else "spawn")
    controller_root = Path(tempfile.mkdtemp(prefix=".workers-", dir=run_dir))
    states: list[dict[str, object]] = []
    try:
        for shard in range(WORKER_COUNT):
            receiver, sender = context.Pipe(duplex=False)
            process = context.Process(
                name=f"verify-project-smoke-{shard}",
                target=smoke_worker,
                args=(
                    changerail_root,
                    controller_root / f"shard-{shard}",
                    shard,
                    sender,
                    (_test_faults or {}).get(shard),
                    _test_synthetic,
                ),
            )
            process.start()
            sender.close()
            states.append(
                {
                    "shard": shard,
                    "process": process,
                    "receiver": receiver,
                    "deadline": time.monotonic() + _worker_timeout,
                    "messages": [],
                    "timed_out": False,
                }
            )

        while any(state["process"].is_alive() for state in states):
            for state in states:
                receiver = state["receiver"]
                while receiver.poll():
                    try:
                        state["messages"].append(receiver.recv())
                    except EOFError:
                        break
                process = state["process"]
                process.join(timeout=0)
                if process.is_alive() and time.monotonic() >= state["deadline"]:
                    state["timed_out"] = True
                    terminate_worker(process)
            time.sleep(0.01)

        for state in states:
            process = state["process"]
            process.join(timeout=0)
            receiver = state["receiver"]
            while receiver.poll(0.05):
                try:
                    state["messages"].append(receiver.recv())
                except EOFError:
                    break
            receiver.close()

        reports: list[dict[str, object]] = []
        protocol_errors: list[str] = []
        for state in states:
            shard = state["shard"]
            process = state["process"]
            messages = state["messages"]
            if state["timed_out"]:
                protocol_errors.append(f"worker {shard}: timeout after {_worker_timeout:.3f}s")
                continue
            if len(messages) == 0:
                if process.exitcode:
                    protocol_errors.append(
                        f"worker {shard}: child crash exit={process.exitcode}; missing terminal result"
                    )
                else:
                    protocol_errors.append(f"worker {shard}: missing terminal result (exit=0)")
                continue
            if len(messages) != 1:
                protocol_errors.append(f"worker {shard}: duplicate terminal results ({len(messages)})")
                continue
            message = messages[0]
            if not isinstance(message, dict) or message.get("shard") != shard:
                protocol_errors.append(f"worker {shard}: malformed terminal envelope")
                continue
            if "error" in message:
                protocol_errors.append(f"worker {shard}: child exception: {message['error']}")
                continue
            if process.exitcode != 0:
                protocol_errors.append(f"worker {shard}: child crash exit={process.exitcode}")
                continue
            try:
                reports.append(validate_shard_report(shard, message.get("report")))
            except WorkerProtocolError as exc:
                protocol_errors.append(str(exc))
        if protocol_errors:
            raise WorkerProtocolError("; ".join(protocol_errors))

        reports.sort(key=lambda report: SHARD_SCENARIOS.index(tuple(check["name"] for check in report["checks"])))
        checks = [check for report in reports for check in report["checks"]]
        expected_names = tuple(name for shard_names in SHARD_SCENARIOS for name in shard_names)
        actual_names = tuple(check["name"] for check in checks)
        if actual_names != expected_names or len(checks) != 69:
            raise WorkerProtocolError("parent aggregation violated the frozen 69-scenario order")
        return {
            "schema": SCHEMA,
            "run_dir": str(run_dir),
            "changerail_root": str(changerail_root),
            "summary": summarize_checks(checks),
            "checks": checks,
        }
    finally:
        for state in states:
            process = state["process"]
            terminate_worker(process)
            receiver = state["receiver"]
            try:
                receiver.close()
            except OSError:
                pass
        shutil.rmtree(controller_root, ignore_errors=True)


def report_exit_code(report: dict[str, object]) -> int:
    return 0 if report["summary"]["status"] == "pass" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run verify-project smoke checks.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "verify-project-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        report = run_smoke(changerail_root, run_dir)
    except WorkerProtocolError as exc:
        print(f"ERROR verify-project smoke controller: {exc}", file=sys.stderr)
        return 1
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"report: {report_path}")
    print(
        "summary: "
        f"{summary['status']} "
        f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
    )
    return report_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
