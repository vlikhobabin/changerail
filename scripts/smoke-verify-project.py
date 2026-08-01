#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = "changerail.verify-project-smoke.v1"
SPECIAL_OUTPUTS = {
    Path("gitignore.tpl"): Path(".gitignore"),
    Path("mcp.json.tpl"): Path(".mcp.json"),
    Path("codex-config.toml.tpl"): Path(".codex/config.toml"),
}
EXPECTED_SCHEMAS = (
    "schemas/changerail-review-verdict.schema.json",
    "schemas/changerail-review-cycle-history.schema.json",
    "schemas/changerail-delivery-manifest.schema.json",
    "schemas/changerail-delivery-run.schema.json",
    "schemas/changerail-evidence-index.schema.json",
)
MCP_FILES = (".mcp.json", ".codex/config.toml")
OPTIONAL_BROWSER_MCP_NEEDLES = ("@playwright/mcp", "chrome-devtools-mcp")


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


def create_fixture(project: Path, changerail_root: Path) -> None:
    template_root = changerail_root / "templates" / "project"
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)

    for source in template_root.rglob("*"):
        if source.is_dir():
            continue
        rel = source.relative_to(template_root)
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
    symlink_force(changerail_root / "bin" / "changerail-review-verdict", project / "bin" / "changerail-review-verdict")
    symlink_force(changerail_root / "bin" / "changerail-evidence", project / "bin" / "changerail-evidence")


def run(cmd: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "OPENSPEC_TELEMETRY": "0"}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=180,
    )


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


def set_verification_policy(project: Path, *, surfaces: dict[str, str] | None = None, targeted: str = "required") -> None:
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
        "  profile: smoke",
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


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    checks: list[Check] = []
    fake_env = create_fake_npm(changerail_root, run_dir / "fake-bin")
    fake_env.update({"CODEX_HOME": "", "CODEX_AUTH_TOKEN": "", "OPENAI_API_KEY": ""})
    good_project = run_dir / "example-project"
    create_fixture(good_project, changerail_root)

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
            "missing auth advisory warns",
            "pass"
            if verify.returncode == 0
            and "WARN delivery runner auth readiness" in verify.stdout
            and "codex-auth-for-delivery-runner" in verify.stdout
            else "fail",
            verify.stdout.strip(),
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
