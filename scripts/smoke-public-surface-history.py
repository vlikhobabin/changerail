#!/usr/bin/env python3
"""Exercise bounded public-history semantics, framing and Git lifecycle."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "scripts" / "public-surface-scan.py"
ZERO = "0" * 40


def load_scanner():
    spec = importlib.util.spec_from_file_location("public_surface_scan", SCANNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def raw_header(old_mode: str, new_mode: str, old: str, new: str, status: str) -> bytes:
    return f":{old_mode} {new_mode} {old} {new} {status}".encode()


def raw_stream(*fields: bytes) -> bytes:
    return b"\0".join(fields) + b"\0"


def framing_oracle(scanner) -> None:
    commit_a, commit_b = "a" * 40, "b" * 40
    blob_a, blob_b, link, submodule = "1" * 40, "2" * 40, "3" * 40, "4" * 40
    valid = raw_stream(
        b"\x1e" + commit_a.encode(),
        b"\n" + raw_header("000000", "100644", ZERO, blob_a, "A"),
        b"docs/root.md",
        raw_header("100644", "100755", blob_a, blob_b, "M"),
        b"docs/root.md",
        raw_header("100755", "000000", blob_b, ZERO, "D"),
        b"docs/old.md",
        raw_header("000000", "100644", ZERO, blob_b, "A"),
        b"docs/new.md",
        b"\x1e" + commit_b.encode(),
        b"\n" + raw_header("100644", "120000", blob_b, link, "T"),
        b"docs/link",
        raw_header("000000", "160000", ZERO, submodule, "A"),
        b"docs/vendor",
    )
    parsed = scanner._parse_raw(valid, 40, ["docs"])
    assert parsed[blob_a] == [(commit_a, "docs/root.md")]
    assert parsed[blob_b] == [(commit_a, "docs/root.md"), (commit_a, "docs/new.md")]
    assert parsed[link] == [(commit_b, "docs/link")]
    assert submodule not in parsed

    bad = [
        raw_stream(b"not-a-marker"),
        raw_stream(b"\x1e" + b"z" * 40),
        b"\x1e" + commit_a.encode(),
        raw_stream(b"\x1e" + commit_a.encode(), raw_header("000000", "100644", ZERO, blob_a, "A")),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n:100644 100644 too few", b"docs/a"),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n" + raw_header("100644", "100644", ZERO, blob_a, "A"), b"docs/a"),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n" + raw_header("100644", "100644", blob_a, blob_b, "R100"), b"docs/a"),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n" + raw_header("100644", "120000", blob_a, link, "M"), b"docs/a"),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n" + raw_header("000000", "100644", ZERO, blob_a, "A"), b""),
        raw_stream(b"\x1e" + commit_a.encode(), b"\n" + raw_header("000000", "100644", ZERO, blob_a, "A"), b"docs/a", b"orphan"),
    ]
    for payload in bad:
        try:
            scanner._parse_raw(payload, 40, ["docs"])
        except ValueError:
            pass
        else:
            raise AssertionError(f"raw framing accepted malformed fixture {bad.index(payload)}")

    batch = (
        f"{blob_a} blob 5\n".encode() + b"hello\n" + f"{blob_b} blob 0\n\n".encode()
    )
    assert scanner._parse_batch(batch, [blob_a, blob_b]) == {blob_a: b"hello", blob_b: b""}
    bad_batch = [
        f"{blob_b} blob 5\nhello\n".encode(),
        f"{blob_a} tree 5\nhello\n".encode(),
        f"{blob_a} blob nope\n".encode(),
        f"{blob_a} blob 6\nhello\n".encode(),
        f"{blob_a} blob 5\nhello".encode(),
        f"{blob_a} blob 5\nhello\nextra".encode(),
    ]
    for payload in bad_batch:
        try:
            scanner._parse_batch(payload, [blob_a])
        except ValueError:
            pass
        else:
            raise AssertionError(f"batch framing accepted malformed fixture {bad_batch.index(payload)}")


def lifecycle_oracle(scanner) -> None:
    oid = "a" * 40
    resolve = subprocess.CompletedProcess([], 0, f"false\n{oid}\n".encode(), b"")
    marker = raw_stream(b"\x1e" + oid.encode())
    good_log = subprocess.CompletedProcess([], 0, marker, b"")
    failures = [
        [subprocess.TimeoutExpired(["git"], 1)],
        [subprocess.CompletedProcess([], 1, b"", b"sensitive resolve output")],
        [resolve, subprocess.TimeoutExpired(["git"], 1)],
        [resolve, subprocess.CompletedProcess([], 1, b"", b"sensitive log output")],
        [resolve, subprocess.CompletedProcess([], 0, b"truncated", b"")],
        [BrokenPipeError("sensitive pipe output")],
    ]
    for effects in failures:
        with mock.patch.object(scanner, "_run_git", side_effect=effects):
            findings = scanner.scan_history([Path("docs")], Path("."))
        rendered = str(findings)
        assert len(findings) == 1 and findings[0].kind == "history"
        assert "sensitive" not in rendered and findings[0].value == "<unavailable>"

    blob = "1" * 40
    raw = raw_stream(
        b"\x1e" + oid.encode(),
        b"\n" + raw_header("000000", "100644", ZERO, blob, "A"),
        b"docs/a.md",
    )
    for effect in (
        subprocess.TimeoutExpired(["git"], 1),
        subprocess.CompletedProcess([], 1, b"", b"sensitive batch output"),
        subprocess.CompletedProcess([], 0, f"{blob} blob 4\nabc".encode(), b""),
    ):
        with mock.patch.object(scanner, "_run_git", side_effect=[resolve, subprocess.CompletedProcess([], 0, raw, b""), effect]):
            findings = scanner.scan_history([Path("docs")], Path("."))
        assert len(findings) == 1 and findings[0].kind == "history"
        assert "sensitive" not in str(findings)

    with mock.patch.object(scanner, "_run_git", side_effect=[resolve, good_log]) as run:
        assert scanner.scan_history([Path("docs")], Path(".")) == []
        assert run.call_count == 2


def build_fixture(repo: Path) -> tuple[str, str]:
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "scan@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Scan")
    docs = repo / "docs"
    docs.mkdir()
    paths = [docs / f"path-{index:02d}.md" for index in range(20)]
    for index, path in enumerate(paths):
        path.write_text(f"public fixture {index}\n", encoding="utf-8")
    commit(repo, "initial public roots")
    for index in range(245):
        paths[index % len(paths)].write_text(f"reused value {index % 3}\n", encoding="utf-8")
        git(repo, "commit", "-qam", f"history {index:03d}")

    secret = "A1B2" + "C3D4" + "E5F6" + "G7H8"
    secret_text = "SERVICE_" + 'TOKEN = "' + secret + '"\n'
    (docs / "secret-a.md").write_text(secret_text, encoding="utf-8")
    (docs / "secret-b.md").write_text(secret_text, encoding="utf-8")
    secret_commit = commit(repo, "reachable redacted finding")
    (docs / "secret-a.md").write_text("clean\n", encoding="utf-8")
    (docs / "secret-b.md").unlink()
    commit(repo, "remove finding")
    (docs / "binary.dat").write_bytes(b"binary\0payload")
    (docs / "invalid.txt").write_bytes(b"invalid\xffutf8")
    commit(repo, "binary fixtures")
    paths[0].unlink()
    commit(repo, "delete path")
    git(repo, "mv", str(paths[1].relative_to(repo)), "docs/renamed.md")
    commit(repo, "rename path")

    git(repo, "switch", "-q", "-c", "feature")
    paths[2].write_text("feature side\n", encoding="utf-8")
    commit(repo, "feature side")
    git(repo, "switch", "-q", "main")
    paths[2].write_text("main side\n", encoding="utf-8")
    commit(repo, "main side")
    merge = subprocess.run(["git", "merge", "--no-commit", "feature"], cwd=repo, capture_output=True)
    assert merge.returncode != 0
    paths[2].write_text("merge resolution\n", encoding="utf-8")
    commit(repo, "merge resolution")

    git(repo, "switch", "-q", "-c", "unrelated")
    (docs / "unrelated.md").write_text(secret_text, encoding="utf-8")
    unrelated_commit = commit(repo, "unrelated ref finding")
    git(repo, "switch", "-q", "main")
    return secret_commit, unrelated_commit


def semantic_oracle(scanner) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        secret_commit, unrelated_commit = build_fixture(repo)
        calls = 0
        scans: list[str] = []
        original_git, original_scan = scanner._run_git, scanner.scan_text

        def counted_git(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original_git(*args, **kwargs)

        def counted_scan(text, *args, **kwargs):
            scans.append(text)
            return original_scan(text, *args, **kwargs)

        with mock.patch.object(scanner, "_run_git", counted_git), mock.patch.object(scanner, "scan_text", counted_scan):
            findings = scanner.scan_history([repo / "docs"], repo)
        assert calls <= 3
        finding_paths = {(item.ref, item.path) for item in findings if item.kind == "secret"}
        assert (secret_commit[:12], "docs/secret-a.md") in finding_paths
        assert (secret_commit[:12], "docs/secret-b.md") in finding_paths
        assert all(ref != unrelated_commit[:12] for ref, _ in finding_paths)
        assert sum("SERVICE_TOKEN" in text for text in scans) == 1
        assert all("A1B2C3D4" not in item.value for item in findings)


def main() -> int:
    scanner = load_scanner()
    framing_oracle(scanner)
    lifecycle_oracle(scanner)
    semantic_oracle(scanner)
    print("PUBLIC_SURFACE_HISTORY_SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
