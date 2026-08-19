#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
    effective_cmd = list(cmd)
    if Path(effective_cmd[0]).name in {"bootstrap-project", "bootstrap-project.cmd"}:
        if "--configure-existing" not in effective_cmd and "--lock-enforcement" not in effective_cmd:
            effective_cmd[2:2] = ["--lock-enforcement", "none"]
    return subprocess.run(
        effective_cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=240,
    )


def create_clean_changerail_fixture(changerail_root: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    for rel_path in (
        "AGENTS.shared.md",
        "VERSION",
        "mcp-npm-lock.json",
        "templates",
        "skills",
        "claude",
        "bin",
        "schemas",
        "scripts",
    ):
        source = changerail_root / rel_path
        target = destination / rel_path
        if source.is_dir():
            shutil.copytree(source, target, symlinks=True)
        else:
            shutil.copy2(source, target)
    commands = (
        ["git", "init", "--initial-branch=main"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=ChangeRail Smoke",
            "-c",
            "user.email=smoke@example.invalid",
            "commit",
            "-m",
            "clean fixture",
        ],
        ["git", "remote", "add", "origin", "https://github.com/example/changerail.git"],
    )
    for command in commands:
        result = run(command, destination)
        if result.returncode != 0:
            raise RuntimeError(result.stdout.strip())
    return destination


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
        template_text = re.sub(r"\$\{\{.*?\}\}", "", text)
        if "{{" in template_text or "}}" in template_text:
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
            "fresh machine receipt или independent `go` verdict",
            "`3.inprogress -> 4.done`",
            "До model launch выполняется deterministic preflight",
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
    codex_config = (project / ".codex" / "config.toml").read_text(encoding="utf-8")
    agents_size = len((project / "AGENTS.md").read_text(encoding="utf-8").encode("utf-8"))
    if "project_doc_max_bytes = 32768" not in codex_config or agents_size * 100 >= 32768 * 85:
        return Check(
            "bootstrap valid project",
            "fail",
            f"instruction budget missing or default AGENTS.md too large: {agents_size}/32768 bytes",
        )
    maintenance_paths = [
        ".changerail/KNOWLEDGE.md",
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


def check_profile_matrix(changerail_root: Path, run_dir: Path) -> Check:
    cases = (
        (
            "default",
            [],
            {
                ".codex/config.toml": ('approval_policy = "on-request"', 'sandbox_mode = "workspace-write"'),
                "openspec/config.yaml": (
                    "project_profile: generic",
                    "surfaces_profile: all-surfaces",
                    "codex_policy: safe-interactive",
                ),
            },
        ),
        (
            "workspace-root",
            ["--profile", "workspace-root"],
            {"AGENTS.md": ("aggregator ownership", "independent child repositories")},
        ),
        (
            "service",
            ["--profile", "service"],
            {"AGENTS.md": ("single-repository delivery ownership",)},
        ),
        (
            "codex-only",
            ["--surfaces", "codex-only"],
            {"openspec/config.yaml": ("claude: optional", "legacy_mcp: optional")},
        ),
        (
            "trusted-automation",
            ["--codex-policy", "trusted-automation"],
            {
                ".codex/config.toml": ('approval_policy = "never"', 'sandbox_mode = "danger-full-access"'),
                "AGENTS.md": ("trusted-automation", "explicit operator choice"),
            },
        ),
    )
    failures: list[str] = []
    for name, args, expected in cases:
        project = run_dir / f"profile-{name}"
        result = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(project),
                "--skip-verify",
                *args,
            ],
            changerail_root,
        )
        if result.returncode != 0:
            failures.append(f"{name}: {result.stdout.strip()}")
            continue
        if name == "codex-only" and (project / ".claude").exists():
            failures.append("codex-only: optional Claude wiring was generated")
        for rel_path, needles in expected.items():
            path = project / rel_path
            if not path.is_file():
                failures.append(f"{name}: missing {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")
            missing = [needle for needle in needles if needle not in text]
            if missing:
                failures.append(f"{name}: {rel_path} missing {', '.join(missing)}")
    if failures:
        return Check("bootstrap profile matrix", "fail", "; ".join(failures))
    return Check("bootstrap profile matrix", "pass", "all supported profile selections rendered coherently")


def check_profile_fail_before_write(changerail_root: Path, run_dir: Path) -> Check:
    cases = (
        ("unknown", ["--profile", "unknown"]),
        ("conflict", ["--kind", "generic", "--profile", "service"]),
    )
    failures: list[str] = []
    for name, args in cases:
        project = run_dir / f"bad-profile-{name}"
        result = run(
            [str(changerail_root / "bin" / "bootstrap-project"), str(project), *args],
            changerail_root,
        )
        if result.returncode == 0:
            failures.append(f"{name}: command unexpectedly passed")
        if project.exists():
            failures.append(f"{name}: target was mutated")

    dry_run_project = run_dir / "profile-dry-run"
    dry_run = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(dry_run_project),
            "--codex-policy",
            "trusted-automation",
            "--dry-run",
        ],
        changerail_root,
    )
    if dry_run.returncode != 0 or "PLAN codex-policy trusted-automation" not in dry_run.stdout:
        failures.append("dry-run: selected Codex authority was not reported")
    if dry_run_project.exists():
        failures.append("dry-run: target was mutated")

    oversized_root = run_dir / "oversized-instruction-root"
    shutil.copytree(changerail_root / "templates", oversized_root / "templates")
    (oversized_root / "AGENTS.shared.md").write_text("x" * 33000, encoding="utf-8")
    oversized_project = run_dir / "oversized-instruction-project"
    oversized = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(oversized_project),
            "--changerail-root",
            str(oversized_root),
            "--skip-verify",
        ],
        changerail_root,
    )
    if (
        oversized.returncode == 0
        or oversized_project.exists()
        or "UTF-8 bytes" not in oversized.stdout
        or "32768" not in oversized.stdout
    ):
        failures.append("oversized generated instructions did not fail before target mutation")

    if failures:
        return Check("profile validation before write", "fail", "; ".join(failures))
    return Check("profile validation before write", "pass", "invalid profiles failed before target mutation")


def check_consumer_lock_and_path_modes(
    changerail_root: Path,
    run_dir: Path,
    extra_env: dict[str, str],
) -> Check:
    clean_root = create_clean_changerail_fixture(changerail_root, run_dir / "clean-changerail")
    failures: list[str] = []
    cases = (("absolute", []), ("relative", ["--wiring-path-mode", "relative"]))
    for path_mode, extra_args in cases:
        project = run_dir / f"locked-{path_mode}"
        result = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(project),
                "--changerail-root",
                str(clean_root),
                "--lock-enforcement",
                "advisory",
                "--skip-verify",
                *extra_args,
            ],
            changerail_root,
        )
        if result.returncode != 0:
            failures.append(f"{path_mode}: {result.stdout.strip()}")
            continue
        lock_path = project / "openspec" / "changerail-consumer-lock.json"
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path_mode}: lock unreadable: {exc}")
            continue
        if lock.get("schema") != "changerail.consumer-lock.v1":
            failures.append(f"{path_mode}: lock schema missing")
        wiring = lock.get("wiring", {})
        if wiring.get("path_mode") != path_mode:
            failures.append(f"{path_mode}: lock path mode mismatch")
        changerail = lock.get("changerail", {})
        source = str(changerail.get("source", ""))
        if not source.startswith("https://") or str(clean_root) in source or "@" in source:
            failures.append(f"{path_mode}: unsafe source reference {source!r}")
        link = project / "bin" / "openspec"
        if not link.is_symlink():
            failures.append(f"{path_mode}: bin/openspec is not a symlink")
        elif Path(os.readlink(link)).is_absolute() != (path_mode == "absolute"):
            failures.append(f"{path_mode}: raw symlink target contradicts path mode")

    relative_project = run_dir / "locked-relative"
    relative_link = relative_project / "bin" / "openspec"
    relative_link.unlink()
    refresh = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(relative_project),
            "--changerail-root",
            str(clean_root),
            "--refresh-wiring",
            "--skip-verify",
        ],
        changerail_root,
    )
    if refresh.returncode != 0 or not relative_link.is_symlink():
        failures.append("lock-owned refresh did not repair a missing symlink")
    elif Path(os.readlink(relative_link)).is_absolute():
        failures.append("lock-owned refresh did not preserve relative path mode")

    configure_auth_source = run_dir / "configure-auth-source.json"
    configure_auth_source.write_text("credential-sentinel-value\n", encoding="utf-8")
    relative_link.unlink(missing_ok=True)
    configure_command = [
        str(changerail_root / "bin" / "bootstrap-project"),
        str(relative_project),
        "--changerail-root",
        str(clean_root),
        "--configure-existing",
        "--refresh-wiring",
        "--link-codex-auth",
        str(configure_auth_source),
        "--skip-verify",
    ]
    configured = run(configure_command, changerail_root)
    repeated = run(configure_command, changerail_root)
    configured_auth = relative_project / ".codex" / "auth.json"
    if (
        configured.returncode != 0
        or repeated.returncode != 0
        or not relative_link.is_symlink()
        or not configured_auth.is_symlink()
        or configured_auth.resolve() != configure_auth_source.resolve()
    ):
        failures.append("configure mode did not idempotently combine lock repair and auth")

    relative_link.unlink()
    relative_link.write_text("project-owned\n", encoding="utf-8")
    owned_refresh = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(relative_project),
            "--changerail-root",
            str(clean_root),
            "--refresh-wiring",
            "--skip-verify",
        ],
        changerail_root,
    )
    if owned_refresh.returncode == 0 or relative_link.read_text(encoding="utf-8") != "project-owned\n":
        failures.append("refresh replaced project-owned non-symlink content")

    absolute_project = run_dir / "locked-absolute"
    git_commands = (
        ["git", "init", "--initial-branch=main"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=ChangeRail Smoke",
            "-c",
            "user.email=smoke@example.invalid",
            "commit",
            "-m",
            "locked consumer fixture",
        ],
    )
    for command in git_commands:
        git_result = run(command, absolute_project)
        if git_result.returncode != 0:
            failures.append(f"clean-clone fixture Git setup failed: {git_result.stdout.strip()}")
            break
    else:
        clone = run_dir / "non-sibling" / "layout" / "consumer-clone"
        clone.parent.mkdir(parents=True)
        clone_result = run(["git", "clone", str(absolute_project), str(clone)], run_dir)
        if clone_result.returncode != 0:
            failures.append(f"non-sibling clone failed: {clone_result.stdout.strip()}")
        else:
            clone_verify = run(
                [
                    str(changerail_root / "bin" / "verify-project"),
                    str(clone),
                    "--changerail-root",
                    str(clean_root),
                ],
                changerail_root,
                extra_env,
            )
            if clone_verify.returncode != 0 or "PASS consumer wiring validity" not in clone_verify.stdout:
                failures.append(f"non-sibling clean clone did not verify: {clone_verify.stdout.strip()}")

        dirty_owned_link = absolute_project / "bin" / "openspec"
        dirty_owned_link.unlink()
        agents_path = absolute_project / "AGENTS.md"
        agents_path.write_text(
            agents_path.read_text(encoding="utf-8") + "\nunrelated project change\n",
            encoding="utf-8",
        )
        dirty_refresh = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(absolute_project),
                "--changerail-root",
                str(clean_root),
                "--refresh-wiring",
                "--skip-verify",
            ],
            changerail_root,
        )
        if dirty_refresh.returncode == 0 or dirty_owned_link.exists() or dirty_owned_link.is_symlink():
            failures.append("refresh ignored unrelated consumer Git dirty state")

    parent_project = run_dir / "locked-parent-escape"
    parent_bootstrap = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(parent_project),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "advisory",
            "--skip-verify",
        ],
        changerail_root,
    )
    if parent_bootstrap.returncode == 0:
        parent_lock_path = parent_project / "openspec" / "changerail-consumer-lock.json"
        parent_lock = json.loads(parent_lock_path.read_text(encoding="utf-8"))
        parent_lock["wiring"]["artifacts"][0]["path"] = "escaped/owned-link"
        parent_lock_path.write_text(
            json.dumps(parent_lock, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        outside = run_dir / "outside-parent"
        outside.mkdir()
        os.symlink(outside, parent_project / "escaped")
        parent_refresh = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(parent_project),
                "--changerail-root",
                str(clean_root),
                "--refresh-wiring",
                "--skip-verify",
            ],
            changerail_root,
        )
        if parent_refresh.returncode == 0 or (outside / "owned-link").exists():
            failures.append("refresh followed a symlink parent outside project scope")
    else:
        failures.append(f"parent escape fixture bootstrap failed: {parent_bootstrap.stdout.strip()}")

    incompatible = run_dir / "bad-path-mode-backend"
    incompatible_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(incompatible),
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "generated-copy",
            "--wiring-path-mode",
            "relative",
            "--lock-enforcement",
            "none",
        ],
        changerail_root,
    )
    if incompatible_result.returncode == 0 or incompatible.exists():
        failures.append("incompatible backend/path mode mutated target or passed")

    (clean_root / "VERSION").write_text("0.4.0-dirty\n", encoding="utf-8")
    dirty_target = run_dir / "bad-dirty-locked-source"
    dirty_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(dirty_target),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "strict",
        ],
        changerail_root,
    )
    if dirty_result.returncode == 0 or dirty_target.exists():
        failures.append("dirty locked source mutated target or passed")

    if failures:
        return Check("consumer lock and POSIX path modes", "fail", "; ".join(failures))
    return Check("consumer lock and POSIX path modes", "pass", "lock and path-mode contracts passed")


def check_lockless_wiring_adoption(
    changerail_root: Path,
    run_dir: Path,
    extra_env: dict[str, str],
) -> Check:
    clean_root = create_clean_changerail_fixture(changerail_root, run_dir / "adoption-clean-changerail")
    other_root = create_clean_changerail_fixture(changerail_root, run_dir / "adoption-other-changerail")
    failures: list[str] = []

    def bootstrap_lockless(project: Path) -> subprocess.CompletedProcess[str]:
        return run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(project),
                "--changerail-root",
                str(clean_root),
                "--lock-enforcement",
                "none",
                "--skip-verify",
            ],
            changerail_root,
            extra_env,
        )

    def adopt_command(project: Path, *extra: str) -> list[str]:
        return [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--changerail-root",
            str(clean_root),
            "--configure-existing",
            "--adopt-lockless-wiring",
            *extra,
        ]

    project = run_dir / "lockless-adoption-project"
    initial = bootstrap_lockless(project)
    missing_helper = project / "bin" / "changerail-evidence"
    if initial.returncode != 0:
        failures.append(f"legacy fixture bootstrap failed: {initial.stdout.strip()}")
    else:
        legacy_verify = run([str(changerail_root / "bin" / "verify-project"), str(project), "--changerail-root", str(clean_root)], changerail_root, extra_env)
        if (
            legacy_verify.returncode != 0
            or "lockless symlink wiring has" not in legacy_verify.stdout
            or "adopt-lockless-wiring" not in legacy_verify.stdout
        ):
            failures.append(f"lockless verifier did not report adoption advisory: {legacy_verify.stdout.strip()}")
        missing_helper.unlink()
        dry_run = run(adopt_command(project, "--dry-run", "--skip-verify"), changerail_root, extra_env)
        if dry_run.returncode != 0:
            failures.append(f"adoption dry-run failed: {dry_run.stdout.strip()}")
        expected_dry_run = (
            "PLAN adopt-lockless-wiring",
            "PLAN keep symlink bin/openspec",
            "PLAN add symlink bin/changerail-evidence",
            "PLAN consumer-lock openspec/changerail-consumer-lock.json",
        )
        missing = [needle for needle in expected_dry_run if needle not in dry_run.stdout]
        if missing:
            failures.append("adoption dry-run omitted: " + ", ".join(missing))
        if (project / "openspec" / "changerail-consumer-lock.json").exists() or missing_helper.exists():
            failures.append("adoption dry-run mutated lockless consumer")

        applied = run(adopt_command(project), changerail_root, extra_env)
        verify = run([str(changerail_root / "bin" / "verify-project"), str(project), "--changerail-root", str(clean_root)], changerail_root, extra_env)
        if (
            applied.returncode != 0
            or not missing_helper.is_symlink()
            or not (project / "openspec" / "changerail-consumer-lock.json").is_file()
            or verify.returncode != 0
            or "PASS consumer wiring validity" not in verify.stdout
            or "consumer lock exists" not in verify.stdout
        ):
            failures.append(f"successful adoption did not become lock-backed: {applied.stdout.strip()} {verify.stdout.strip()}")

        repeated = run(adopt_command(project, "--skip-verify"), changerail_root, extra_env)
        if repeated.returncode != 0 or "wiring refreshed from consumer lock" not in repeated.stdout:
            failures.append(f"second adoption run was not idempotent: {repeated.stdout.strip()}")

    mixed_project = run_dir / "lockless-mixed-root"
    mixed_initial = bootstrap_lockless(mixed_project)
    if mixed_initial.returncode == 0:
        mixed_link = mixed_project / "bin" / "openspec"
        mixed_link.unlink()
        os.symlink(other_root / "bin" / "openspec", mixed_link)
        mixed = run(adopt_command(mixed_project, "--dry-run", "--skip-verify"), changerail_root, extra_env)
        if mixed.returncode == 0 or "mixed ChangeRail source root" not in mixed.stdout or str(other_root) in mixed.stdout:
            failures.append("mixed-root adoption did not fail closed with public-safe diagnostics")
    else:
        failures.append(f"mixed-root fixture bootstrap failed: {mixed_initial.stdout.strip()}")

    conflict_project = run_dir / "lockless-regular-conflict"
    conflict_initial = bootstrap_lockless(conflict_project)
    if conflict_initial.returncode == 0:
        conflict_path = conflict_project / "bin" / "openspec"
        conflict_path.unlink()
        conflict_path.write_text("project-owned\n", encoding="utf-8")
        conflict_verify = run(
            [str(changerail_root / "bin" / "verify-project"), str(conflict_project), "--changerail-root", str(clean_root)],
            changerail_root,
            extra_env,
        )
        if "lockless wiring is unsafe for automatic adoption" not in conflict_verify.stdout:
            failures.append("verifier did not report unsafe lockless adoption")
        conflict = run(adopt_command(conflict_project, "--skip-verify"), changerail_root, extra_env)
        if (
            conflict.returncode == 0
            or conflict_path.read_text(encoding="utf-8") != "project-owned\n"
            or (conflict_project / "openspec" / "changerail-consumer-lock.json").exists()
        ):
            failures.append("regular-file conflict was replaced or adopted")
    else:
        failures.append(f"regular-conflict fixture bootstrap failed: {conflict_initial.stdout.strip()}")

    dirty_project = run_dir / "lockless-dirty-unrelated"
    dirty_initial = bootstrap_lockless(dirty_project)
    if dirty_initial.returncode == 0:
        commands = (
            ["git", "init", "--initial-branch=main"],
            ["git", "add", "."],
            [
                "git",
                "-c",
                "user.name=ChangeRail Smoke",
                "-c",
                "user.email=smoke@example.invalid",
                "commit",
                "-m",
                "legacy lockless consumer",
            ],
        )
        for command in commands:
            result = run(command, dirty_project)
            if result.returncode != 0:
                failures.append(f"dirty fixture Git setup failed: {result.stdout.strip()}")
                break
        else:
            (dirty_project / "src").mkdir()
            (dirty_project / "src" / "project-owned.txt").write_text("unrelated\n", encoding="utf-8")
            dirty = run(adopt_command(dirty_project, "--skip-verify"), changerail_root, extra_env)
            if dirty.returncode == 0 or "unrelated dirty state" not in dirty.stdout:
                failures.append("unrelated dirty state did not block adoption")
            if (dirty_project / "openspec" / "changerail-consumer-lock.json").exists():
                failures.append("dirty blocked adoption left a consumer lock")
    else:
        failures.append(f"dirty fixture bootstrap failed: {dirty_initial.stdout.strip()}")

    windows_project = run_dir / "lockless-windows-unsupported"
    windows_initial = bootstrap_lockless(windows_project)
    if windows_initial.returncode == 0:
        windows = run(
            adopt_command(
                windows_project,
                "--wiring-platform",
                "windows",
                "--wiring-backend",
                "generated-copy",
                "--dry-run",
                "--skip-verify",
            ),
            changerail_root,
            extra_env,
        )
        if windows.returncode == 0 or "generated-copy adoption requires" not in windows.stdout:
            failures.append("unsupported Windows generated-copy inference did not fail closed")
    else:
        failures.append(f"windows unsupported fixture bootstrap failed: {windows_initial.stdout.strip()}")

    if failures:
        return Check("lockless wiring adoption", "fail", "; ".join(failures))
    return Check(
        "lockless wiring adoption",
        "pass",
        "legacy lockless adoption, unsafe ownership gates and idempotency passed",
    )


def check_consumer_ci_opt_in(changerail_root: Path, run_dir: Path) -> Check:
    clean_root = create_clean_changerail_fixture(changerail_root, run_dir / "ci-clean-changerail")
    failures: list[str] = []

    default_project = run_dir / "ci-default-omitted"
    default_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(default_project),
            "--lock-enforcement",
            "none",
            "--skip-verify",
        ],
        changerail_root,
    )
    workflow_rel = Path(".github/workflows/changerail-consumer-verify.yml")
    if default_result.returncode != 0 or (default_project / workflow_rel).exists():
        failures.append("default bootstrap generated consumer CI or failed")

    advisory_target = run_dir / "bad-advisory-ci"
    advisory = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(advisory_target),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "advisory",
            "--with-ci",
        ],
        changerail_root,
    )
    if advisory.returncode == 0 or advisory_target.exists():
        failures.append("advisory CI request passed or mutated target")

    strict_target = run_dir / "strict-consumer-ci"
    strict = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(strict_target),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "strict",
            "--with-ci",
            "--skip-verify",
        ],
        changerail_root,
    )
    if strict.returncode != 0 or not (strict_target / workflow_rel).is_file():
        failures.append(f"strict CI workflow was not generated: {strict.stdout.strip()}")

    dry_target = run_dir / "strict-ci-dry-run"
    dry_run = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(dry_target),
            "--changerail-root",
            str(clean_root),
            "--lock-enforcement",
            "strict",
            "--with-ci",
            "--dry-run",
        ],
        changerail_root,
    )
    if (
        dry_run.returncode != 0
        or str(workflow_rel) not in dry_run.stdout
        or "PLAN lock-enforcement strict" not in dry_run.stdout
        or dry_target.exists()
    ):
        failures.append("strict CI dry-run did not report workflow and exact lock requirement")

    if failures:
        return Check("consumer CI opt-in", "fail", "; ".join(failures))
    return Check("consumer CI opt-in", "pass", "CI remained opt-in and required a strict lock")


def check_post_bootstrap_configuration(changerail_root: Path, run_dir: Path) -> Check:
    failures: list[str] = []
    project = run_dir / "post-bootstrap-project"
    initial = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(project),
            "--lock-enforcement",
            "none",
            "--skip-verify",
        ],
        changerail_root,
    )
    auth_source = run_dir / "auth-source.json"
    sentinel = "credential-sentinel-value"
    auth_source.write_text(sentinel + "\n", encoding="utf-8")
    configure_command = [
        str(changerail_root / "bin" / "bootstrap-project"),
        str(project),
        "--configure-existing",
        "--link-codex-auth",
        str(auth_source),
        "--skip-verify",
    ]
    configured = run(configure_command, changerail_root)
    repeated = run(configure_command, changerail_root)
    auth_marker = project / ".codex" / "auth.json"
    if initial.returncode != 0 or configured.returncode != 0 or repeated.returncode != 0:
        failures.append("idempotent auth configuration failed")
    if not auth_marker.is_symlink() or auth_marker.resolve() != auth_source.resolve():
        failures.append("auth configuration did not create the desired symlink")
    combined_output = configured.stdout + repeated.stdout
    if sentinel in combined_output or str(auth_source) in combined_output:
        failures.append("auth configuration output exposed credential content or source path")

    auth_marker.unlink(missing_ok=True)
    auth_marker.write_text("project-owned\n", encoding="utf-8")
    conflict = run(configure_command, changerail_root)
    if conflict.returncode == 0 or auth_marker.read_text(encoding="utf-8") != "project-owned\n":
        failures.append("auth configuration replaced project-owned content")

    mixed_project = run_dir / "post-bootstrap-mixed-flags"
    mixed_project.mkdir()
    mixed = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(mixed_project),
            "--configure-existing",
            "--link-codex-auth",
            str(auth_source),
            "--profile",
            "service",
            "--skip-verify",
        ],
        changerail_root,
    )
    if mixed.returncode == 0 or (mixed_project / ".codex").exists():
        failures.append("configure mode accepted template/profile flags")

    readme_project = run_dir / "readme-project"
    readme = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(readme_project),
            "--name",
            "readme-project",
            "--profile",
            "service",
            "--with-readme",
            "--lock-enforcement",
            "none",
            "--skip-verify",
        ],
        changerail_root,
    )
    readme_path = readme_project / "README.md"
    if readme.returncode != 0 or not readme_path.is_file():
        failures.append("README opt-in did not render")
    else:
        readme_text = readme_path.read_text(encoding="utf-8")
        for needle in ("readme-project", "service", "bin/verify-project ."):
            if needle not in readme_text:
                failures.append(f"generated README missing {needle!r}")
        if str(readme_project) in readme_text or str(changerail_root) in readme_text:
            failures.append("generated README contains machine-local paths")

    readme_conflict_project = run_dir / "readme-conflict"
    readme_conflict_project.mkdir()
    existing_readme = readme_conflict_project / "README.md"
    existing_readme.write_text("project-owned README\n", encoding="utf-8")
    readme_conflict = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(readme_conflict_project),
            "--with-readme",
            "--lock-enforcement",
            "none",
        ],
        changerail_root,
    )
    if readme_conflict.returncode == 0 or existing_readme.read_text(encoding="utf-8") != "project-owned README\n":
        failures.append("README conflict was overwritten or accepted")

    git_project = run_dir / "git-init-project"
    git_init = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(git_project),
            "--init-git",
            "--default-branch",
            "trunk",
            "--remote",
            "https://github.com/example/consumer.git",
            "--lock-enforcement",
            "none",
            "--skip-verify",
        ],
        changerail_root,
    )
    if git_init.returncode != 0 or not git_project.is_dir():
        failures.append("Git init did not preserve no-stage/no-commit boundary")
    else:
        branch = run(["git", "symbolic-ref", "--short", "HEAD"], git_project)
        remote = run(["git", "remote", "get-url", "origin"], git_project)
        staged = run(["git", "diff", "--cached", "--quiet"], git_project)
        commits = run(["git", "rev-parse", "HEAD"], git_project)
        if (
            branch.stdout.strip() != "trunk"
            or remote.stdout.strip() != "https://github.com/example/consumer.git"
            or staged.returncode != 0
            or commits.returncode == 0
        ):
            failures.append("Git init did not preserve no-stage/no-commit boundary")
        if "no files were staged, committed or pushed" not in git_init.stdout:
            failures.append("Git init output omitted operator-owned publication boundary")
        dirty_auth = run(
            [
                str(changerail_root / "bin" / "bootstrap-project"),
                str(git_project),
                "--configure-existing",
                "--link-codex-auth",
                str(auth_source),
                "--skip-verify",
            ],
            changerail_root,
        )
        dirty_marker = git_project / ".codex" / "auth.json"
        if dirty_auth.returncode == 0 or dirty_marker.exists() or dirty_marker.is_symlink():
            failures.append("auth configuration ignored unrelated Git dirty state")

    bad_git_target = run_dir / "bad-git-options"
    bad_git = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(bad_git_target),
            "--default-branch",
            "trunk",
            "--lock-enforcement",
            "none",
        ],
        changerail_root,
    )
    if bad_git.returncode == 0 or bad_git_target.exists():
        failures.append("Git detail without --init-git mutated target or passed")

    secret_remote_target = run_dir / "secret-remote"
    credential_remote = "https://user:remote-secret@example.invalid/consumer.git"
    bad_remote = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(secret_remote_target),
            "--init-git",
            "--remote",
            credential_remote,
            "--lock-enforcement",
            "none",
        ],
        changerail_root,
    )
    if bad_remote.returncode == 0 or secret_remote_target.exists() or "remote-secret" in bad_remote.stdout:
        failures.append("credential-bearing remote passed, mutated target or leaked credential")

    if failures:
        return Check("post-bootstrap configuration", "fail", "; ".join(failures))
    return Check(
        "post-bootstrap configuration",
        "pass",
        "auth, README and Git configuration remained idempotent and bounded",
    )


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
        ".changerail/KNOWLEDGE.md",
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
    validate = run(
        [str(project / "bin" / "changerail-maintenance"), "validate-catalog", "--json"],
        project,
        extra_env,
    )
    if validate.returncode != 0:
        return Check(
            "maintenance opt-in bootstrap",
            "fail",
            "first-run validate-catalog failed; starter catalog regression would not be caught: "
            + validate.stdout.strip(),
        )
    render = run(
        [str(project / "bin" / "changerail-maintenance"), "render-index", "--check"],
        project,
        extra_env,
    )
    if render.returncode != 0:
        return Check(
            "maintenance opt-in bootstrap",
            "fail",
            "first-run render-index --check failed; missing generated index regression would not be caught: "
            + render.stdout.strip(),
        )
    scan = run(
        [str(project / "bin" / "changerail-maintenance"), "scan", "--json"],
        project,
        extra_env,
    )
    if scan.returncode != 0:
        return Check(
            "maintenance opt-in bootstrap",
            "fail",
            "first-run scan failed; uncovered starter catalog regression would not be caught: "
            + scan.stdout.strip(),
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
        "schemas/changerail-maintenance-quality-rollup.schema.json",
        "schemas/changerail-maintenance-proposal-decision.schema.json",
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
        "maintenance paths rendered, first-run checks green and wiring verified",
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
    expected = (
        ".changerail/KNOWLEDGE.md",
        ".changerail/maintenance.yaml",
        ".changerail/knowledge.yaml",
        "bin/changerail-maintenance-runner",
    )
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
        check_profile_matrix(changerail_root, run_dir),
        check_profile_fail_before_write(changerail_root, run_dir),
        check_consumer_lock_and_path_modes(changerail_root, run_dir, fake_env),
        check_lockless_wiring_adoption(changerail_root, run_dir, fake_env),
        check_consumer_ci_opt_in(changerail_root, run_dir),
        check_post_bootstrap_configuration(changerail_root, run_dir),
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
