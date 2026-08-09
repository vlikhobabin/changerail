#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "changerail.bootstrap-project-smoke.v1"


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


def run(cmd: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=240,
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
                "import json, sys",
                f"MAPPING = {mapping!r}",
                "if len(sys.argv) == 5 and sys.argv[1] == 'view' and sys.argv[3] == 'dist.integrity' and sys.argv[4] == '--json':",
                "    spec = sys.argv[2]",
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


def contains_placeholder(project: Path) -> list[str]:
    offenders: list[str] = []
    for path in project.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "{{" in text or "}}" in text:
            offenders.append(str(path.relative_to(project)))
    return offenders


def machine_local_text_offenders(project: Path, changerail_root: Path) -> list[str]:
    offenders: list[str] = []
    forbidden = [str(project)]
    if changerail_root.resolve(strict=False).as_posix() != "/opt/changerail":
        forbidden.append(str(changerail_root))
    for path in project.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for value in forbidden:
            if value and value in text:
                offenders.append(f"{path.relative_to(project)} contains {value}")
    return offenders


def missing_workflow_guidance(project: Path) -> list[str]:
    checks = {
        "AGENTS.md": [
            "explore -> ff -> do -> review -> pub",
            "## Supervised Roles",
            "Reviewer работает в fresh context",
            "3.inprogress",
            "4.done",
            "max-fix-cycles",
            "max-review-cycles",
            "fix_budget_exhausted",
            "bounded same-card micro-fix",
        ],
        "openspec/board/README.md": [
            "explore -> ff -> do -> review -> pub",
            "fresh independent `go` verdict",
            "`3.inprogress -> 4.done`",
            "`review` должен быть fresh context",
        ],
    }
    missing: list[str] = []
    for rel_path, needles in checks.items():
        path = project / rel_path
        if not path.is_file():
            missing.append(f"{rel_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel_path}: missing {needle!r}")
    return missing


def missing_verification_profile_guidance(project: Path) -> list[str]:
    checks = {
        "openspec/config.yaml": [
            "verification:",
            "profile: all-surfaces",
            "codex: required",
            "claude: required",
            "legacy_mcp: required",
            "legacy_artifacts: forbidden",
            "targeted_openspec_validation: required",
            "baseline_debt: []",
        ],
        "AGENTS.md": [
            "required",
            "optional",
            "forbidden",
            "pass-with-diagnostics",
            "targeted card-owned",
        ],
    }
    missing: list[str] = []
    for rel_path, needles in checks.items():
        path = project / rel_path
        if not path.is_file():
            missing.append(f"{rel_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel_path}: missing {needle!r}")
    return missing


def check_bootstrap_success(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "example-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "example-project",
            "--kind",
            "generic",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("bootstrap valid project", "fail", result.stdout.strip())
    placeholders = contains_placeholder(project)
    if placeholders:
        return Check("bootstrap valid project", "fail", "raw placeholders remain: " + ", ".join(placeholders))
    local_paths = machine_local_text_offenders(project, changerail_root)
    if local_paths:
        return Check("bootstrap valid project", "fail", "machine-local tracked text: " + ", ".join(local_paths))
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root, extra_env)
    if verify.returncode != 0:
        return Check("bootstrap valid project", "fail", verify.stdout.strip())
    workflow_missing = missing_workflow_guidance(project)
    if workflow_missing:
        return Check("bootstrap workflow guidance", "fail", "; ".join(workflow_missing))
    profile_missing = missing_verification_profile_guidance(project)
    if profile_missing:
        return Check("bootstrap verification profile guidance", "fail", "; ".join(profile_missing))
    if (project / ".codex" / "auth.json").exists() or (project / ".codex" / "auth.json").is_symlink():
        return Check("bootstrap valid project", "fail", "default bootstrap created auth marker")
    maintenance_paths = [
        ".changerail/knowledge.yaml",
        ".changerail/maintenance.yaml",
        "bin/changerail-maintenance",
        "bin/changerail-maintenance-runner",
    ]
    present = [
        rel_path
        for rel_path in maintenance_paths
        if (project / rel_path).exists() or (project / rel_path).is_symlink()
    ]
    if present:
        return Check(
            "bootstrap valid project",
            "fail",
            "default bootstrap created maintenance opt-in paths: " + ", ".join(present),
        )
    return Check("bootstrap valid project", "pass", "project generated and verified")


def check_dry_run(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "dry-run-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "dry-run-project",
            "--kind",
            "generic",
            "--dry-run",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("dry-run no-write", "fail", result.stdout.strip())
    if project.exists():
        return Check("dry-run no-write", "fail", f"target was created: {project}")
    expected = (".claude/commands/chrl", ".codex/skills/chrl-do")
    missing = [needle for needle in expected if needle not in result.stdout]
    if missing:
        return Check("dry-run no-write", "fail", "dry-run omitted alias wiring: " + ", ".join(missing))
    forbidden = (".changerail/maintenance.yaml", "bin/changerail-maintenance")
    leaked = [needle for needle in forbidden if needle in result.stdout]
    if leaked:
        return Check(
            "dry-run no-write",
            "fail",
            "default dry-run included maintenance opt-in paths: " + ", ".join(leaked),
        )
    return Check("dry-run no-write", "pass", "dry-run printed plan and left no target")


def check_maintenance_bootstrap(
    changerail_root: Path,
    run_dir: Path,
    extra_env: dict[str, str],
) -> Check:
    project = run_dir / "maintenance-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "maintenance-project",
            "--kind",
            "generic",
            "--with-maintenance",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("maintenance opt-in bootstrap", "fail", result.stdout.strip())
    expected = [
        ".changerail/knowledge.yaml",
        ".changerail/maintenance.yaml",
        "bin/changerail-maintenance",
        "bin/changerail-maintenance-runner",
    ]
    missing = [
        rel_path
        for rel_path in expected
        if not ((project / rel_path).exists() or (project / rel_path).is_symlink())
    ]
    if missing:
        return Check(
            "maintenance opt-in bootstrap",
            "fail",
            "missing maintenance paths: " + ", ".join(missing),
        )
    verify = run(
        [str(changerail_root / "bin" / "verify-project"), str(project), "--json"],
        changerail_root,
        extra_env,
    )
    if verify.returncode != 0:
        return Check("maintenance opt-in bootstrap", "fail", verify.stdout.strip())
    try:
        data = json.loads(verify.stdout)
    except json.JSONDecodeError as exc:
        return Check("maintenance opt-in bootstrap", "fail", f"verify-project did not emit JSON: {exc}")
    checks = data.get("checks", [])
    names = {
        check.get("name")
        for check in checks
        if isinstance(check, dict) and check.get("status") == "pass"
    }
    required = {
        ".changerail/knowledge.yaml",
        ".changerail/maintenance.yaml",
        "bin/changerail-maintenance",
        "bin/changerail-maintenance-runner",
        "schemas/changerail-maintenance-run.schema.json",
    }
    missing_checks = sorted(required - names)
    if missing_checks:
        return Check(
            "maintenance opt-in bootstrap",
            "fail",
            "missing passing checks: " + ", ".join(missing_checks),
        )
    return Check(
        "maintenance opt-in bootstrap",
        "pass",
        "maintenance paths rendered, wired and verified",
    )


def check_maintenance_dry_run(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "maintenance-dry-run-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "maintenance-dry-run-project",
            "--kind",
            "generic",
            "--with-maintenance",
            "--dry-run",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("maintenance opt-in dry-run", "fail", result.stdout.strip())
    if project.exists():
        return Check("maintenance opt-in dry-run", "fail", f"target was created: {project}")
    expected = (".changerail/maintenance.yaml", ".changerail/knowledge.yaml", "bin/changerail-maintenance-runner")
    missing = [needle for needle in expected if needle not in result.stdout]
    if missing:
        return Check("maintenance opt-in dry-run", "fail", "dry-run omitted maintenance paths: " + ", ".join(missing))
    return Check("maintenance opt-in dry-run", "pass", "maintenance dry-run printed plan and left no target")


def check_windows_generated_dry_run(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "windows-generated-dry-run-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "windows-generated-dry-run-project",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "generated-copy",
            "--dry-run",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("windows generated dry-run", "fail", result.stdout.strip())
    if project.exists():
        return Check("windows generated dry-run", "fail", f"target was created: {project}")
    expected = (
        "PLAN wiring-backend generated-copy",
        "PLAN generated directory .claude/skills",
        "symlink fallback skipped",
        "junction fallback skipped",
        "openspec/changerail-wiring.json",
    )
    missing = [needle for needle in expected if needle not in result.stdout]
    if missing:
        return Check("windows generated dry-run", "fail", "dry-run omitted: " + ", ".join(missing))
    return Check("windows generated dry-run", "pass", "generated backend and fallback reasons reported")


def check_windows_generated_bootstrap(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "windows-generated-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "windows-generated-project",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "generated-copy",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("windows generated bootstrap", "fail", result.stdout.strip())
    manifest_path = project / "openspec" / "changerail-wiring.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return Check("windows generated bootstrap", "fail", f"cannot read generated manifest: {exc}")
    if manifest.get("backend") != "generated-copy" or manifest.get("platform") != "windows":
        return Check("windows generated bootstrap", "fail", "manifest backend/platform mismatch")
    artifacts = manifest.get("artifacts", [])
    kinds = {entry.get("kind") for entry in artifacts if isinstance(entry, dict)}
    if not {"file", "directory"}.issubset(kinds):
        return Check("windows generated bootstrap", "fail", "manifest does not classify file and directory wiring")
    if str(project) in manifest_path.read_text(encoding="utf-8") or str(changerail_root) in manifest_path.read_text(encoding="utf-8"):
        return Check("windows generated bootstrap", "fail", "manifest contains machine-local absolute path")
    symlinks = [
        rel
        for rel in (".claude/skills", ".claude/commands/changerail", ".codex/skills/changerail-do", "bin/openspec")
        if (project / rel).is_symlink()
    ]
    if symlinks:
        return Check("windows generated bootstrap", "fail", "generated backend created symlinks: " + ", ".join(symlinks))
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root, extra_env)
    if verify.returncode != 0:
        return Check("windows generated bootstrap", "fail", verify.stdout.strip())
    return Check("windows generated bootstrap", "pass", "generated project created, manifest-owned and verified")


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


def write_status_only_windows_fallback_proof(run_dir: Path, mode: str) -> Path:
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
    path = run_dir / f"{mode}-status-only-fallback-proof.json"
    path.write_text(
        json.dumps(
            {
                "schema": "changerail.windows-wiring-proof.v1",
                "mode": mode,
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


def write_hash_only_windows_fallback_proof(run_dir: Path, mode: str) -> Path:
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
    checks = [
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
    ]
    path = run_dir / f"{mode}-hash-only-fallback-proof.json"
    path.write_text(
        json.dumps(
            {
                "schema": "changerail.windows-wiring-proof.v1",
                "mode": mode,
                "source": {
                    "kind": "retained-command-evidence",
                    "tool": "scripts/smoke-bootstrap-project.py",
                    "fixture": "hash-only",
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
                    "tool": "scripts/smoke-bootstrap-project.py",
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


def check_windows_symlink_fallback_bootstrap(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "windows-symlink-fallback-project"
    proof = write_windows_fallback_proof(run_dir, "symlink")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "windows-symlink-fallback-project",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "symlink",
            "--windows-fallback-proof",
            str(proof),
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("windows symlink fallback bootstrap", "fail", result.stdout.strip())
    manifest_path = project / "openspec" / "changerail-wiring.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return Check("windows symlink fallback bootstrap", "fail", f"cannot read fallback manifest: {exc}")
    if manifest.get("backend") != "symlink" or manifest.get("fallback_proof", {}).get("mode") != "symlink":
        return Check("windows symlink fallback bootstrap", "fail", "symlink fallback proof was not recorded")
    if not (project / ".claude" / "skills").is_symlink() or not (project / "bin" / "openspec").is_symlink():
        return Check("windows symlink fallback bootstrap", "fail", "symlink fallback did not create expected symlinks")
    return Check("windows symlink fallback bootstrap", "pass", "validated proof created explicit symlink fallback")


def check_status_only_fallback_proof_rejected(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "status-only-fallback-proof-project"
    proof = write_status_only_windows_fallback_proof(run_dir, "symlink")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "status-only-fallback-proof-project",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "symlink",
            "--windows-fallback-proof",
            str(proof),
            "--dry-run",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode == 0:
        return Check("status-only fallback proof rejected", "fail", "status-only proof unexpectedly passed")
    if "source metadata" not in result.stdout and "concrete passed evidence" not in result.stdout:
        return Check("status-only fallback proof rejected", "fail", result.stdout.strip())
    return Check("status-only fallback proof rejected", "pass", "minimal status-only proof fails closed")


def check_hash_only_fallback_proof_rejected(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "hash-only-fallback-proof-project"
    proof = write_hash_only_windows_fallback_proof(run_dir, "symlink")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "hash-only-fallback-proof-project",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "symlink",
            "--windows-fallback-proof",
            str(proof),
            "--dry-run",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode == 0:
        return Check("hash-only fallback proof rejected", "fail", "hash-only proof unexpectedly passed")
    if "concrete passed evidence" not in result.stdout:
        return Check("hash-only fallback proof rejected", "fail", result.stdout.strip())
    return Check("hash-only fallback proof rejected", "pass", "hash-only proof fails closed")


def check_symlink_partial_rollback(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "windows-symlink-partial-failure"
    proof = write_windows_fallback_proof(run_dir, "symlink")
    env = {**extra_env, "CHANGERAIL_BOOTSTRAP_FAIL_AFTER_ARTIFACTS": "2"}
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "windows-symlink-partial-failure",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "symlink",
            "--windows-fallback-proof",
            str(proof),
            "--skip-verify",
        ],
        changerail_root,
        env,
    )
    if result.returncode == 0:
        return Check("windows symlink partial rollback", "fail", "simulated symlink failure unexpectedly succeeded")
    leftovers = [
        rel
        for rel in (".claude/skills", ".claude/commands/changerail", "openspec/changerail-wiring.json")
        if (project / rel).exists() or (project / rel).is_symlink()
    ]
    if leftovers:
        return Check("windows symlink partial rollback", "fail", "current-run symlink artifacts left behind: " + ", ".join(leftovers))
    return Check("windows symlink partial rollback", "pass", "created symlink artifacts rolled back after failure")


def check_windows_generated_partial_rollback(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "windows-generated-partial-failure"
    env = {**extra_env, "CHANGERAIL_BOOTSTRAP_FAIL_AFTER_ARTIFACTS": "2"}
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "windows-generated-partial-failure",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "generated-copy",
            "--skip-verify",
        ],
        changerail_root,
        env,
    )
    if result.returncode == 0:
        return Check("windows generated partial rollback", "fail", "simulated failure unexpectedly succeeded")
    leftovers = [
        rel
        for rel in (".claude/skills", ".claude/commands/changerail", "openspec/changerail-wiring.json")
        if (project / rel).exists() or (project / rel).is_symlink()
    ]
    if leftovers:
        return Check("windows generated partial rollback", "fail", "current-run artifacts left behind: " + ", ".join(leftovers))
    return Check("windows generated partial rollback", "pass", "created generated artifacts rolled back after failure")


def check_auth_link(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "auth-link-project"
    auth_source = run_dir / "fake-auth.json"
    sentinel = "fake-secret-sentinel"
    auth_source.write_text("{\"token\":\"" + sentinel + "\"}\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "auth-link-project",
            "--kind",
            "generic",
            "--link-codex-auth",
            str(auth_source),
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("auth link bootstrap", "fail", result.stdout.strip())
    if sentinel in result.stdout:
        return Check("auth link bootstrap", "fail", "bootstrap printed credential contents")
    marker = project / ".codex" / "auth.json"
    if not marker.is_symlink():
        return Check("auth link bootstrap", "fail", "auth marker is not a symlink")
    try:
        if marker.resolve(strict=True) != auth_source:
            return Check("auth link bootstrap", "fail", f"auth marker resolves to {marker.resolve(strict=False)}")
    except OSError as exc:
        return Check("auth link bootstrap", "fail", f"auth marker is broken: {exc}")
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root, extra_env)
    if verify.returncode != 0:
        return Check("auth link bootstrap", "fail", verify.stdout.strip())
    return Check("auth link bootstrap", "pass", "auth marker linked without exposing contents")


def check_auth_link_missing_source(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "missing-auth-source-project"
    missing = run_dir / "missing-auth.json"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "missing-auth-source-project",
            "--kind",
            "generic",
            "--link-codex-auth",
            str(missing),
        ],
        changerail_root,
    )
    if result.returncode == 0:
        return Check("auth link missing source", "fail", "bootstrap unexpectedly succeeded")
    if (project / ".codex" / "auth.json").exists() or (project / ".codex" / "auth.json").is_symlink():
        return Check("auth link missing source", "fail", "dangling auth marker was created")
    return Check("auth link missing source", "pass", "missing auth source refused without marker")


def check_auth_link_dry_run(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "auth-link-dry-run-project"
    auth_source = run_dir / "dry-run-auth.json"
    auth_source.write_text("{}\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "auth-link-dry-run-project",
            "--kind",
            "generic",
            "--link-codex-auth",
            str(auth_source),
            "--dry-run",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("auth link dry-run", "fail", result.stdout.strip())
    if project.exists():
        return Check("auth link dry-run", "fail", f"target was created: {project}")
    if ".codex/auth.json" not in result.stdout:
        return Check("auth link dry-run", "fail", "dry-run omitted auth symlink plan")
    return Check("auth link dry-run", "pass", "auth link dry-run planned without writes")


def check_local_config_warning(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "local-config-project"
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "local-config-project",
            "--kind",
            "generic",
            "--config-mode",
            "local",
            "--skip-verify",
        ],
        changerail_root,
    )
    if result.returncode != 0:
        return Check("local config warning", "fail", result.stdout.strip())
    if "warning: --config-mode local rendered machine-local absolute paths" not in result.stdout:
        return Check("local config warning", "fail", "local config warning missing")
    if str(project) not in (project / ".mcp.json").read_text(encoding="utf-8"):
        return Check("local config warning", "fail", "local config did not render absolute project path")
    return Check("local config warning", "pass", "local config required explicit mode and warned before git add")


def check_refuse_existing(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "existing-project"
    project.mkdir(parents=True)
    marker = project / "existing.txt"
    marker.write_text("keep\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "existing-project",
            "--kind",
            "generic",
        ],
        changerail_root,
    )
    if result.returncode == 0:
        return Check("refuse existing target", "fail", "bootstrap unexpectedly succeeded")
    if marker.read_text(encoding="utf-8") != "keep\n":
        return Check("refuse existing target", "fail", "existing marker changed")
    return Check("refuse existing target", "pass", "non-empty target refused without changes")


def check_backup_existing(changerail_root: Path, run_dir: Path, extra_env: dict[str, str]) -> Check:
    project = run_dir / "backup-project"
    project.mkdir(parents=True)
    marker = project / "existing.txt"
    marker.write_text("backup me\n", encoding="utf-8")
    result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--name",
            "backup-project",
            "--kind",
            "generic",
            "--backup-existing",
        ],
        changerail_root,
        extra_env,
    )
    if result.returncode != 0:
        return Check("backup existing target", "fail", result.stdout.strip())
    backups = sorted(project.parent.glob("backup-project.backup-*"))
    if not backups:
        return Check("backup existing target", "fail", "backup directory was not created")
    if not (backups[-1] / "existing.txt").is_file():
        return Check("backup existing target", "fail", "backup marker missing")
    verify = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root, extra_env)
    if verify.returncode != 0:
        return Check("backup existing target", "fail", verify.stdout.strip())
    return Check("backup existing target", "pass", "existing target backed up and new project verified")


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    fake_env = create_fake_npm(changerail_root, run_dir / "fake-bin")
    checks = [
        check_bootstrap_success(changerail_root, run_dir, fake_env),
        check_dry_run(changerail_root, run_dir),
        check_maintenance_bootstrap(changerail_root, run_dir, fake_env),
        check_maintenance_dry_run(changerail_root, run_dir),
        check_windows_generated_dry_run(changerail_root, run_dir),
        check_windows_generated_bootstrap(changerail_root, run_dir, fake_env),
        check_windows_generated_partial_rollback(changerail_root, run_dir, fake_env),
        check_windows_symlink_fallback_bootstrap(changerail_root, run_dir, fake_env),
        check_status_only_fallback_proof_rejected(changerail_root, run_dir, fake_env),
        check_hash_only_fallback_proof_rejected(changerail_root, run_dir, fake_env),
        check_symlink_partial_rollback(changerail_root, run_dir, fake_env),
        check_auth_link(changerail_root, run_dir, fake_env),
        check_auth_link_missing_source(changerail_root, run_dir),
        check_auth_link_dry_run(changerail_root, run_dir),
        check_local_config_warning(changerail_root, run_dir),
        check_refuse_existing(changerail_root, run_dir),
        check_backup_existing(changerail_root, run_dir, fake_env),
    ]
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bootstrap-project smoke checks.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "bootstrap-smoke"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"

    report = run_smoke(changerail_root, run_dir)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"report: {report_path}")
    print(
        "summary: "
        f"{summary['status']} "
        f"({summary['passed']}/{summary['total']} passed, {summary['failed']} failed)"
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
