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


SCHEMA = "changerail.windows-wiring-git-safety-smoke.v1"
SENTINEL = "fake-secret-sentinel"
GIT_SAFETY_CHECK_NAMES = {
    "git_status_safe",
    "git_add_dry_run_safe",
    "git_index_safe",
}
UNSAFE_GIT_PATH_FIXTURE = (
    f".runtime/{SENTINEL}.log",
    ".codex/auth.json",
    r"C:\changerail-smoke\secret.txt",
)
UNSAFE_MARKERS = (
    ".runtime/",
    ".artifacts/",
    ".ai/",
    ".codex/auth.json",
    ".codex/auth.toml",
    ".claude/settings.local.json",
    r"C:\changerail-smoke",
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
        timeout=240,
    )


def git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(project), *args], project)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def proof_evidence(command: str, stdout: str = "", exit_code: int = 0) -> dict[str, object]:
    return {
        "command": command,
        "exit_code": exit_code,
        "stdout_sha256": sha256_text(stdout),
    }


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


def safe_git_details(command: str, *, paths: list[str] | None = None) -> tuple[dict[str, object], dict[str, object]]:
    stdout = "\n".join(paths or [])
    details = {
        "safe": True,
        "unsafe_paths": [],
        "stageable_paths": paths or [],
    }
    return details, proof_evidence(command, stdout=stdout)


def unsafe_git_details(command: str, unsafe_paths: list[str]) -> tuple[dict[str, object], dict[str, object]]:
    stdout = "\n".join(unsafe_paths)
    details = {
        "safe": False,
        "unsafe_paths": unsafe_paths,
        "stageable_paths": [],
    }
    return details, proof_evidence(command, stdout=stdout)


def write_fallback_proof(path: Path, mode: str, *, unsafe: bool = False, incomplete_git_details: bool = False) -> Path:
    if mode == "symlink":
        checks = [
            proof_check(
                "direct_os_symlink_directory",
                "filesystem",
                "retained fixture recorded directory symlink creation",
                {"link_type": "directory", "fixture": "git-safety"},
                proof_evidence("os.symlink(directory)"),
            ),
            proof_check(
                "direct_os_symlink_file",
                "filesystem",
                "retained fixture recorded file symlink creation",
                {"link_type": "file", "fixture": "git-safety"},
                proof_evidence("os.symlink(file)"),
            ),
            proof_check(
                "symlink_privilege_or_developer_mode",
                "filesystem",
                "retained fixture recorded symlink capability",
                {"directory_link": "passed", "file_link": "passed", "fixture": "git-safety"},
                proof_evidence("os.symlink(directory-and-file)"),
            ),
        ]
    elif mode == "junction":
        checks = [
            proof_check(
                "junction_directory",
                "filesystem",
                "retained fixture recorded junction creation",
                {"link_type": "junction", "fixture": "git-safety"},
                proof_evidence("cmd /c mklink /J .codex\\skills\\changerail-do <source>"),
            ),
            proof_check(
                "link_aware_cleanup",
                "cleanup",
                "retained fixture recorded link path cleanup",
                {"cleanup": "passed", "fixture": "git-safety"},
                proof_evidence("remove-created-link-path"),
            ),
        ]
        for name, command in (
            ("git_status_safe", "git status --porcelain=v1 --untracked-files=all"),
            ("git_add_dry_run_safe", "git add --dry-run ."),
            ("git_index_safe", "git ls-files --stage"),
        ):
            if unsafe:
                details, evidence = unsafe_git_details(command, list(UNSAFE_GIT_PATH_FIXTURE))
            else:
                details, evidence = safe_git_details(command, paths=[".codex/skills/changerail-do"])
            if incomplete_git_details:
                details.pop("safe", None)
                details.pop("unsafe_paths", None)
            checks.append(proof_check(name, "git", f"{command} completed", details, evidence))
    else:
        raise ValueError(mode)

    path.write_text(
        json.dumps(
            {
                "schema": "changerail.windows-wiring-proof.v1",
                "mode": mode,
                "source": {
                    "kind": "retained-command-evidence",
                    "tool": "scripts/smoke-windows-wiring-git-safety.py",
                    "fixture": "unsafe" if unsafe else "safe",
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


def generated_manifest_paths(manifest: dict[str, object]) -> set[str]:
    entries = manifest.get("artifacts")
    if not isinstance(entries, list):
        return set()
    paths: set[str] = set()
    for entry in entries:
        if isinstance(entry, dict) and entry.get("owner") == "generated" and isinstance(entry.get("path"), str):
            paths.add(entry["path"])
    return paths


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def rename_generated_path(project: Path, manifest: dict[str, object], source_rel: str, target_rel: str) -> str | None:
    owned_paths = generated_manifest_paths(manifest)
    if source_rel not in owned_paths:
        return f"source is not generated-owned: {source_rel}"
    source = project / source_rel
    target = project / target_rel
    if not source.exists() and not source.is_symlink():
        return f"source path is missing: {source_rel}"
    if target.exists() or target.is_symlink():
        if target_rel not in owned_paths:
            return f"refusing to rename over project-owned path: {target_rel}"
        remove_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    source.rename(target)
    return None


def uninstall_generated_paths(project: Path, manifest: dict[str, object]) -> None:
    for rel in sorted(generated_manifest_paths(manifest), key=lambda value: value.count("/"), reverse=True):
        path = project / rel
        if path.exists() or path.is_symlink():
            remove_path(path)


def bootstrap_project(
    changerail_root: Path,
    project: Path,
    *,
    backend: str,
    proof: Path | None = None,
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
        backend,
        "--skip-verify",
    ]
    if proof is not None:
        cmd.extend(["--windows-fallback-proof", str(proof)])
    return run(cmd, changerail_root)


def seed_git_fixture(project: Path) -> None:
    (project / "src").mkdir(parents=True, exist_ok=True)
    (project / "src" / "project-owned.txt").write_text("project-owned source\n", encoding="utf-8")
    (project / ".runtime").mkdir(parents=True, exist_ok=True)
    (project / ".runtime" / "secret.log").write_text(SENTINEL + "\n", encoding="utf-8")
    (project / ".codex").mkdir(parents=True, exist_ok=True)
    (project / ".codex" / "auth.json").write_text('{"token":"' + SENTINEL + '"}\n', encoding="utf-8")
    git(project, "init", "-q")


def combined_output(results: list[subprocess.CompletedProcess[str]]) -> str:
    return "\n".join(result.stdout for result in results)


def unsafe_output_findings(text: str, changerail_root: Path) -> list[str]:
    findings = [marker for marker in UNSAFE_MARKERS if marker in text]
    if SENTINEL in text:
        findings.append("credential contents")
    if str(changerail_root) in text:
        findings.append("absolute ChangeRail source path")
    return sorted(set(findings))


def unsafe_proof_diagnostic_findings(text: str) -> list[str]:
    findings = [path for path in UNSAFE_GIT_PATH_FIXTURE if path in text]
    if SENTINEL in text:
        findings.append("credential contents")
    return sorted(set(findings))


def git_safety_check(
    project: Path,
    changerail_root: Path,
    *,
    name: str,
    expected_visible: tuple[str, ...],
    forbidden_visible: tuple[str, ...] = (),
    expect_symlink_index: bool = False,
) -> Check:
    seed_git_fixture(project)
    status = git(project, "status", "--porcelain=v1", "--untracked-files=all")
    dry_run = git(project, "add", "--dry-run", ".")
    add = git(project, "add", "--all", ".")
    index = git(project, "ls-files", "--stage")
    results = [status, dry_run, add, index]
    failures = [result.stdout.strip() for result in results if result.returncode != 0]
    if failures:
        return Check(name, "fail", "; ".join(failures))
    text = combined_output([status, dry_run, index])
    unsafe = unsafe_output_findings(text, changerail_root)
    if unsafe:
        return Check(name, "fail", "unsafe Git evidence leaked: " + ", ".join(unsafe))
    missing = [path for path in expected_visible if path not in text]
    if missing:
        return Check(name, "fail", "expected Git evidence missing paths: " + ", ".join(missing))
    forbidden = [path for path in forbidden_visible if path in text]
    if forbidden:
        return Check(name, "fail", "forbidden traversal visible in Git evidence: " + ", ".join(forbidden))
    if expect_symlink_index and "120000" not in index.stdout:
        return Check(name, "fail", "index did not record symlink mode 120000")
    if "src/project-owned.txt" not in text:
        return Check(name, "fail", "project-owned source was hidden from Git evidence")
    return Check(name, "pass", "porcelain, dry-run and index evidence stayed within fixture scope")


def check_generated_git_safety(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "generated-git-safe"
    result = bootstrap_project(changerail_root, project, backend="generated-copy")
    if result.returncode != 0:
        return Check("generated Git safety", "fail", result.stdout.strip())
    return git_safety_check(
        project,
        changerail_root,
        name="generated Git safety",
        expected_visible=("bin/openspec", ".codex/skills/changerail-do/SKILL.md"),
    )


def check_symlink_git_safety(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "symlink-git-safe"
    proof = write_fallback_proof(run_dir / "symlink-proof.json", "symlink")
    result = bootstrap_project(changerail_root, project, backend="symlink", proof=proof)
    if result.returncode != 0:
        return Check("symlink Git safety", "fail", result.stdout.strip())
    return git_safety_check(
        project,
        changerail_root,
        name="symlink Git safety",
        expected_visible=("bin/openspec", ".claude/skills"),
        forbidden_visible=(".claude/skills/changerail-do/SKILL.md",),
        expect_symlink_index=True,
    )


def check_junction_proof_safety(changerail_root: Path, run_dir: Path) -> Check:
    safe_proof = write_fallback_proof(run_dir / "junction-proof-safe.json", "junction")
    safe_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(run_dir / "junction-safe-dry-run"),
            "--name",
            "junction-safe-dry-run",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "junction",
            "--windows-fallback-proof",
            str(safe_proof),
            "--dry-run",
        ],
        changerail_root,
    )
    if safe_result.returncode != 0:
        return Check("junction proof Git safety", "fail", safe_result.stdout.strip())

    incomplete_proof = write_fallback_proof(
        run_dir / "junction-proof-incomplete.json",
        "junction",
        incomplete_git_details=True,
    )
    incomplete_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(run_dir / "junction-incomplete-dry-run"),
            "--name",
            "junction-incomplete-dry-run",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "junction",
            "--windows-fallback-proof",
            str(incomplete_proof),
            "--dry-run",
        ],
        changerail_root,
    )
    if incomplete_result.returncode == 0 or "missing positive Git safety classification" not in incomplete_result.stdout:
        return Check("junction proof Git safety", "fail", incomplete_result.stdout.strip())

    unsafe_proof = write_fallback_proof(run_dir / "junction-proof-unsafe.json", "junction", unsafe=True)
    unsafe_result = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(run_dir / "junction-unsafe-dry-run"),
            "--name",
            "junction-unsafe-dry-run",
            "--kind",
            "generic",
            "--wiring-platform",
            "windows",
            "--wiring-backend",
            "junction",
            "--windows-fallback-proof",
            str(unsafe_proof),
            "--dry-run",
        ],
        changerail_root,
    )
    if unsafe_result.returncode == 0 or "unsafe Git evidence" not in unsafe_result.stdout:
        return Check("junction proof Git safety", "fail", unsafe_result.stdout.strip())
    leaks = unsafe_proof_diagnostic_findings(combined_output([incomplete_result, unsafe_result]))
    if leaks:
        return Check("junction proof Git safety", "fail", "diagnostics exposed unsafe proof material: " + ", ".join(leaks))
    return Check(
        "junction proof Git safety",
        "pass",
        "safe proof accepted, incomplete proof rejected and unsafe proof rejected with scrubbed diagnostics",
    )


def check_verify_rejects_unsafe_junction_proof(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "verify-unsafe-junction-proof"
    generated = bootstrap_project(changerail_root, project, backend="generated-copy")
    if generated.returncode != 0:
        return Check("verify rejects unsafe junction proof", "fail", generated.stdout.strip())
    manifest_path = project / "openspec" / "changerail-wiring.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["backend"] = "junction"
    manifest["platform"] = "windows"
    manifest["fallback_proof"] = json.loads(
        write_fallback_proof(run_dir / "verify-junction-proof-unsafe.json", "junction", unsafe=True).read_text(
            encoding="utf-8"
        )
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = run([str(changerail_root / "bin" / "verify-project"), str(project)], changerail_root)
    if result.returncode == 0:
        return Check("verify rejects unsafe junction proof", "fail", "verify-project unexpectedly passed")
    if "invalid junction fallback proof" not in result.stdout or "unsafe Git" not in result.stdout:
        return Check("verify rejects unsafe junction proof", "fail", result.stdout.strip())
    leaks = unsafe_proof_diagnostic_findings(result.stdout)
    if leaks:
        return Check(
            "verify rejects unsafe junction proof",
            "fail",
            "diagnostics exposed unsafe proof material: " + ", ".join(leaks),
        )
    return Check("verify rejects unsafe junction proof", "pass", "unsafe Git proof failed closed")


def check_cleanup_and_refresh_boundaries(changerail_root: Path, run_dir: Path) -> Check:
    generated_project = run_dir / "generated-partial-cleanup"
    env = {"CHANGERAIL_BOOTSTRAP_FAIL_AFTER_ARTIFACTS": "2"}
    generated = run(
        [
            str(changerail_root / "bin" / "bootstrap-project"),
            str(generated_project),
            "--name",
            generated_project.name,
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
    if generated.returncode == 0:
        return Check("cleanup and refresh boundaries", "fail", "generated failure fixture unexpectedly passed")
    leftovers = [
        rel
        for rel in (".claude/skills", ".claude/commands/changerail", "openspec/changerail-wiring.json")
        if (generated_project / rel).exists() or (generated_project / rel).is_symlink()
    ]
    if leftovers:
        return Check("cleanup and refresh boundaries", "fail", "partial cleanup left: " + ", ".join(leftovers))

    refresh_project = run_dir / "generated-refresh-boundary"
    refreshed = bootstrap_project(changerail_root, refresh_project, backend="generated-copy")
    if refreshed.returncode != 0:
        return Check("cleanup and refresh boundaries", "fail", refreshed.stdout.strip())
    project_owned = refresh_project / "src" / "project-owned.txt"
    project_owned.parent.mkdir(parents=True, exist_ok=True)
    project_owned.write_text("project-owned source\n", encoding="utf-8")
    refresh = run(
        [str(changerail_root / "bin" / "bootstrap-project"), str(refresh_project), "--refresh-wiring", "--skip-verify"],
        changerail_root,
    )
    if refresh.returncode != 0:
        return Check("cleanup and refresh boundaries", "fail", refresh.stdout.strip())
    if project_owned.read_text(encoding="utf-8") != "project-owned source\n":
        return Check("cleanup and refresh boundaries", "fail", "refresh modified project-owned source")
    return Check("cleanup and refresh boundaries", "pass", "cleanup and refresh stayed within owned wiring paths")


def check_rename_and_uninstall_boundaries(changerail_root: Path, run_dir: Path) -> Check:
    project = run_dir / "generated-rename-uninstall"
    result = bootstrap_project(changerail_root, project, backend="generated-copy")
    if result.returncode != 0:
        return Check("rename and uninstall boundaries", "fail", result.stdout.strip())

    manifest_path = project / "openspec" / "changerail-wiring.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_rel = "bin/openspec"
    target_rel = "bin/openspec-renamed"
    project_owned_target = project / target_rel
    project_owned_target.write_text("project-owned target\n", encoding="utf-8")
    rename_error = rename_generated_path(project, manifest, source_rel, target_rel)
    if rename_error is None:
        return Check("rename and uninstall boundaries", "fail", "rename overwrote a project-owned target")
    if "project-owned" not in rename_error:
        return Check("rename and uninstall boundaries", "fail", rename_error)
    if project_owned_target.read_text(encoding="utf-8") != "project-owned target\n":
        return Check("rename and uninstall boundaries", "fail", "rename modified a project-owned target")
    if not (project / source_rel).exists():
        return Check("rename and uninstall boundaries", "fail", "refused rename removed generated source")

    source_file = project / "src" / "project-owned.txt"
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("project-owned source\n", encoding="utf-8")
    auth_file = project / ".codex" / "auth.json"
    auth_file.parent.mkdir(parents=True, exist_ok=True)
    auth_file.write_text('{"token":"' + SENTINEL + '"}\n', encoding="utf-8")
    runtime_file = project / ".runtime" / "secret.log"
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.write_text(SENTINEL + "\n", encoding="utf-8")

    uninstall_generated_paths(project, manifest)
    remaining_generated = [
        rel
        for rel in sorted(generated_manifest_paths(manifest))
        if (project / rel).exists() or (project / rel).is_symlink()
    ]
    if remaining_generated:
        return Check("rename and uninstall boundaries", "fail", "uninstall left generated paths: " + ", ".join(remaining_generated))
    if source_file.read_text(encoding="utf-8") != "project-owned source\n":
        return Check("rename and uninstall boundaries", "fail", "uninstall modified project-owned source")
    if project_owned_target.read_text(encoding="utf-8") != "project-owned target\n":
        return Check("rename and uninstall boundaries", "fail", "uninstall removed project-owned rename target")
    if auth_file.read_text(encoding="utf-8") != '{"token":"' + SENTINEL + '"}\n':
        return Check("rename and uninstall boundaries", "fail", "uninstall touched auth file")
    if runtime_file.read_text(encoding="utf-8") != SENTINEL + "\n":
        return Check("rename and uninstall boundaries", "fail", "uninstall touched runtime file")
    return Check(
        "rename and uninstall boundaries",
        "pass",
        "rename refused project-owned targets and uninstall removed only generated manifest paths",
    )


def run_smoke(changerail_root: Path, run_dir: Path) -> dict[str, object]:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    checks = [
        check_generated_git_safety(changerail_root, run_dir),
        check_symlink_git_safety(changerail_root, run_dir),
        check_junction_proof_safety(changerail_root, run_dir),
        check_verify_rejects_unsafe_junction_proof(changerail_root, run_dir),
        check_cleanup_and_refresh_boundaries(changerail_root, run_dir),
        check_rename_and_uninstall_boundaries(changerail_root, run_dir),
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
    parser = argparse.ArgumentParser(description="Run Windows wiring Git safety smoke checks.")
    parser.add_argument("--changerail-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--runtime-root", type=Path, default=None)
    parser.add_argument("--run-id", default=utc_run_id())
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changerail_root = args.changerail_root.resolve()
    runtime_root = args.runtime_root or changerail_root / ".runtime" / "changerail" / "windows-wiring-git-safety"
    run_dir = runtime_root / args.run_id
    report_path = args.report or run_dir / "report.json"

    report = run_smoke(changerail_root, run_dir)
    report_path.parent.mkdir(parents=True, exist_ok=True)
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
