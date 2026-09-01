#!/usr/bin/env python3
"""Build the reproducible generic ChangeRail source distribution."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
from io import BytesIO
from pathlib import Path

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
class DistributionError(RuntimeError):
    pass
def git(repository: Path, *args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(repository), *args], capture_output=True, text=not binary, check=False)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace") if binary else result.stderr
        detail = stderr.strip().splitlines()[-1] if stderr.strip() else "git command failed"
        raise DistributionError(detail)
    return result.stdout
def reject_object_overrides(repository: Path) -> None:
    common = Path(str(git(repository, "rev-parse", "--git-common-dir")).strip())
    common = common if common.is_absolute() else repository / common
    grafts = common / "info" / "grafts"
    replacements = str(git(repository, "for-each-ref", "--format=%(refname)", "refs/replace/")).strip()
    if replacements or (grafts.is_file() and grafts.read_bytes().strip()):
        raise DistributionError("source repository has Git replacement or graft state")
def resolve_commit(repository: Path, source_ref: str) -> str:
    value = git(repository, "rev-parse", "--verify", "--end-of-options", f"{source_ref}^{{commit}}")
    assert isinstance(value, str)
    commit = value.strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", commit):
        raise DistributionError("source ref did not resolve to a full Git commit id")
    return commit
def tree_text(repository: Path, commit: str, path: str) -> str:
    value = git(repository, "show", f"{commit}:{path}")
    assert isinstance(value, str)
    return value
def validate_source_tree(repository: Path, commit: str) -> str:
    version = tree_text(repository, commit, "VERSION").strip()
    if not SEMVER.fullmatch(version):
        raise DistributionError("VERSION at source commit is not strict MAJOR.MINOR.PATCH")
    if not tree_text(repository, commit, "LICENSE").strip():
        raise DistributionError("LICENSE at source commit is empty")
    return version

def deterministic_gzip(payload: bytes) -> bytes:
    output = BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output, compresslevel=9, mtime=0) as stream:
        stream.write(payload)
    return output.getvalue()

def write_exclusive(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
    except BaseException:
        path.unlink(missing_ok=True)
        raise

def build(repository: Path, source_ref: str, output_dir: Path) -> dict[str, object]:
    if not repository.is_dir():
        raise DistributionError("repository directory does not exist")
    reject_object_overrides(repository)
    commit = resolve_commit(repository, source_ref)
    version = validate_source_tree(repository, commit)
    archive_name = f"changerail-{version}.tar.gz"
    checksum_name = archive_name + ".sha256"
    metadata_name = f"changerail-{version}.release-metadata.txt"
    asset_names = (archive_name, checksum_name, metadata_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [name for name in asset_names if (output_dir / name).exists()]
    if existing:
        raise DistributionError("refusing to overwrite existing release asset: " + ", ".join(existing))
    tar_payload = git(repository, "archive", "--format=tar", f"--prefix=changerail-{version}/", commit, binary=True)
    assert isinstance(tar_payload, bytes)
    archive_payload = deterministic_gzip(tar_payload)
    digest = hashlib.sha256(archive_payload).hexdigest()
    checksum_payload = f"{digest}  {archive_name}\n".encode()
    metadata_payload = (f"version={version}\nlicense=LICENSE\nsource_revision={commit}\narchive={archive_name}\nchecksum={checksum_name}\narchive_sha256={digest}\n").encode()
    created: list[Path] = []
    try:
        for name, payload in ((archive_name, archive_payload), (checksum_name, checksum_payload), (metadata_name, metadata_payload)):
            path = output_dir / name
            write_exclusive(path, payload)
            created.append(path)
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return {"status": "pass", "version": version, "source_revision": commit, "archive_sha256": digest, "assets": list(asset_names)}

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = build(args.repository.resolve(), args.source_ref, args.output_dir.resolve())
    except DistributionError as exc:
        print(f"source distribution error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"built ChangeRail {report['version']} from {report['source_revision']}")
        for asset in report["assets"]:
            print(asset)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
