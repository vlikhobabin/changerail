#!/usr/bin/env python3
"""Smoke-test the reproducible generic ChangeRail source distribution."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-source-distribution.py"

def run(command: list[str], *, cwd: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != expected:
        raise AssertionError(f"unexpected exit {result.returncode} (wanted {expected}): {command}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result

def git(repository: Path, *args: str) -> str:
    return run(["git", *args], cwd=repository).stdout.strip()

def write(path: Path, content: str, *, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)

def build(repository: Path, source_ref: str, output: Path, *, expected: int = 0) -> dict[str, object]:
    result = run([sys.executable, str(BUILDER), "--repository", str(repository), "--source-ref", source_ref, "--output-dir", str(output), "--json"], cwd=ROOT, expected=expected)
    return json.loads(result.stdout) if expected == 0 else {}

def assert_true(value: bool, message: str, checks: list[str]) -> None:
    if not value:
        raise AssertionError(message)
    checks.append(message)

def main() -> int:
    checks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="changerail-source-dist-") as raw:
        temp = Path(raw)
        repository = temp / "repository"
        repository.mkdir()
        git(repository, "init", "--initial-branch=main")
        git(repository, "config", "user.name", "ChangeRail Smoke")
        git(repository, "config", "user.email", "smoke@example.invalid")
        write(repository / "VERSION", "1.0.0\n")
        write(repository / "LICENSE", "Example public license fixture.\n")
        write(repository / "README.md", "# Example ChangeRail source\n")
        write(repository / "bin" / "example-tool", "#!/bin/sh\nexit 0\n", mode=0o755)
        git(repository, "add", "--", "VERSION", "LICENSE", "README.md", "bin/example-tool")
        git(repository, "commit", "-m", "fixture")
        commit = git(repository, "rev-parse", "HEAD")
        write(repository / "README.md", "# Dirty working-tree substitution\n")
        write(repository / "local-only.txt", "must not be archived\n")
        first, second = temp / "first", temp / "second"
        report = build(repository, commit, first)
        build(repository, commit, second)
        archive_name = "changerail-1.0.0.tar.gz"
        checksum_name = archive_name + ".sha256"
        metadata_name = "changerail-1.0.0.release-metadata.txt"
        expected_assets = {archive_name, checksum_name, metadata_name}
        assert_true(set(report["assets"]) == expected_assets, "reports the exact three assets", checks)
        assert_true(report["version"] == "1.0.0", "reports the exact semantic version", checks)
        assert_true(report["source_revision"] == commit, "reports the dereferenced source commit", checks)
        for name in sorted(expected_assets):
            assert_true((first / name).read_bytes() == (second / name).read_bytes(), f"reproduces {name} bytes", checks)
        archive = first / archive_name
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        checksum = (first / checksum_name).read_text(encoding="utf-8")
        assert_true(checksum == f"{digest}  {archive_name}\n", "writes a standard SHA-256 sidecar", checks)
        metadata = dict(line.split("=", 1) for line in (first / metadata_name).read_text(encoding="utf-8").splitlines())
        for field, value in (("version", "1.0.0"), ("license", "LICENSE"), ("source_revision", commit), ("archive", archive_name), ("checksum", checksum_name), ("archive_sha256", digest)):
            assert_true(metadata[field] == value, f"metadata identifies {field}", checks)
        with tarfile.open(archive, mode="r:gz") as bundle:
            members = {member.name: member for member in bundle.getmembers()}
            prefix = "changerail-1.0.0/"
            tracked = {line for line in git(repository, "ls-tree", "-r", "--name-only", commit).splitlines() if line}
            assert_true(all(name == prefix.rstrip("/") or name.startswith(prefix) for name in members), "uses one versioned root", checks)
            assert_true({prefix + name for name in tracked}.issubset(members), "contains every tracked source file", checks)
            assert_true(prefix + "local-only.txt" not in members, "excludes untracked working-tree state", checks)
            assert_true(bundle.extractfile(prefix + "VERSION").read() == b"1.0.0\n", "archives matching VERSION", checks)
            assert_true(bundle.extractfile(prefix + "README.md").read() == b"# Example ChangeRail source\n", "archives committed bytes instead of dirty tracked working-tree bytes", checks)
            assert_true(prefix + "LICENSE" in members, "archives the declared license", checks)
            assert_true(members[prefix + "bin/example-tool"].mode & 0o111 != 0, "preserves executable mode", checks)
        write(repository / "README.md", "# Replacement source bytes\n")
        git(repository, "add", "--", "README.md")
        git(repository, "commit", "-m", "replacement fixture")
        git(repository, "replace", commit, git(repository, "rev-parse", "HEAD"))
        build(repository, commit, temp / "replacement", expected=2)
        assert_true(not (temp / "replacement").exists(), "rejects replacement refs before writing substituted source bytes", checks)
        git(repository, "replace", "-d", commit)
        grafts = repository / ".git" / "info" / "grafts"
        write(grafts, f"{commit}\n")
        build(repository, commit, temp / "graft", expected=2)
        assert_true(not (temp / "graft").exists(), "rejects graft state before writing source assets", checks)
        grafts.unlink()
        build(repository, "missing-source-ref", temp / "invalid-ref", expected=2)
        checks.append("rejects a source ref that is not a commit")
        write(repository / "VERSION", "version-one\n")
        git(repository, "add", "--", "VERSION")
        git(repository, "commit", "-m", "invalid version")
        build(repository, "HEAD", temp / "invalid-version", expected=2)
        checks.append("rejects an invalid semantic version")
        git(repository, "rm", "--", "LICENSE")
        write(repository / "VERSION", "1.0.0\n")
        git(repository, "add", "--", "VERSION")
        git(repository, "commit", "-m", "missing license")
        build(repository, "HEAD", temp / "missing-license", expected=2)
        checks.append("rejects a source tree without LICENSE")
    print(json.dumps({"status": "pass", "checks": len(checks)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
