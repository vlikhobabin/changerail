#!/usr/bin/env python3
"""Smoke-test deterministic review preflight routing and stops."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "bin" / "changerail-review-verdict"
MANIFEST_HELPER = ROOT / "scripts" / "changerail_delivery_manifest.py"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=240)


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode:
        raise AssertionError(f"{label} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(workspace: Path, *args: str) -> None:
    require_ok(run(["git", *args], workspace), f"git {' '.join(args)}")


def card_text(risk: str, *, protocol: bool = False, authorization: str = "none", blocks: str | None = None) -> str:
    blocks_section = f"\n## Depends On\n- `{blocks}`\n" if blocks else ""
    return f"""# Example review preflight

## Status
3.inprogress

## Owner
agent

## OpenSpec Stage
archived

## Review
- Risk tier: `{risk}`
- Milestone audit: `no`
- New authority or wire protocol: `{'yes' if protocol else 'no'}`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{authorization}`

## Change Set
- `example-change`
{blocks_section}

## Result
implemented

## Change 1: `example-change`

### Acceptance
- behavior delivered
"""


def workspace(root: Path, risk: str, *, production_lines: int = 0, protocol: bool = False,
              executable_lines: int = 0, executable_path: str = "bin/new-helper", go_test_lines: int = 0,
              authorization: bool = False, authorization_protocol: bool = False, authorization_ceiling: int = 500,
              mismatched_blocks: bool = False, investigation_status: str = "4.done",
              self_authorize_reference: bool = False, investigation_block_reference: str = "example-card") -> tuple[Path, Path]:
    repo = root / f"repo-{risk}-{production_lines}-{int(protocol)}"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    if authorization:
        write(
            repo / "openspec" / "board" / "4.done" / "published-investigation.md",
            f"# Published investigation\n\n## Status\n{investigation_status}\n\n## Blocks\n- `{investigation_block_reference}`\n",
        )
        source_authorization = json.dumps({
            "investigation_card": "openspec/board/4.done/published-investigation.md",
            "investigation_id": "published-investigation",
            "successor_card": "openspec/board/3.inprogress/example-card.md",
            "successor_id": "example-card",
            "production_loc_ceiling": authorization_ceiling,
            "allow_new_authority_or_wire_protocol": authorization_protocol,
        }, separators=(",", ":"))
        write(
            repo / "openspec" / "board" / "4.done" / "published-investigation-authorization.md",
            "# Published investigation authorization\n\n## Status\n4.done\n\n## Depends On\n"
            "- `published-investigation`\n\n## Authorization\n"
            f"- Investigation authorization: `{source_authorization}`\n",
        )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    card = repo / "openspec" / "board" / "3.inprogress" / "example-card.md"
    authorization_value = "none"
    blocks = None
    if authorization:
        authorization_reference = {
            "authorization_card": "openspec/board/4.done/published-investigation-authorization.md",
            "authorization_id": "published-investigation-authorization",
        }
        if self_authorize_reference:
            authorization_reference["production_loc_ceiling"] = 500
        authorization_value = json.dumps(authorization_reference, separators=(",", ":"))
        blocks = "different-investigation" if mismatched_blocks else "published-investigation"
    write(card, card_text(risk, protocol=protocol, authorization=authorization_value, blocks=blocks))
    write(repo / "openspec" / "changes" / "archive" / "2026-08-17-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "docs" / "base.md", "changed\n")
    if production_lines:
        write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(production_lines)) + "\n")
    if go_test_lines:
        write(repo / "src" / "new_test.go", "\n".join(f"// test {index}" for index in range(go_test_lines)) + "\n")
    if executable_lines:
        helper = repo / executable_path
        write(helper, "\n".join(f"command-{index}" for index in range(executable_lines)) + "\n")
        helper.chmod(0o755)
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", str(card.relative_to(repo)), "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def preflight(repo: Path, manifest: Path, *options: str) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    result = run(
        [str(HELPER), "preflight", "openspec/board/3.inprogress/example-card.md", "--workspace", str(repo), "--manifest", str(manifest), "--json", *options],
        repo,
    )
    if not result.stdout.strip():
        raise AssertionError(f"preflight emitted no machine result: {result.stderr}")
    return result, json.loads(result.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="changerail-review-preflight-") as temp:
        root = Path(temp)

        repo, manifest = workspace(root, "ordinary", production_lines=3)
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        source = next(item for item in payload["committable_paths"] if item.get("path") == "src/new.py")
        source["operation"] = "modify"
        source.pop("target_path", None)
        source["target_path"] = "src/new.py"
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "ordinary normalized preflight")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["reasoning_effort"] == "high"
        assert data["manifest"]["normalized"] is True
        normalized = json.loads(manifest.read_text(encoding="utf-8"))
        source = next(item for item in normalized["committable_paths"] if item.get("path") == "src/new.py")
        assert source["operation"] == "add"

        write(repo / "unexpected.txt", "not in manifest\n")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert data["llm_review"]["required"] is False
        assert next(item for item in data["checks"] if item["id"] == "scope")["status"] == "fail"

        repo, manifest = workspace(root, "deterministic")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "deterministic machine review")
        assert data["outcome"] == "machine-reviewed"
        assert data["risk"]["reasoning_effort"] == "none"

        repo, manifest = workspace(root, "critical", production_lines=3)
        result, data = preflight(repo, manifest, "--normalize", "--risk-tier", "ordinary")
        require_ok(result, "critical preflight")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "critical"
        assert data["risk"]["reasoning_effort"] == "xhigh"

        repo, manifest = workspace(root, "ordinary")
        write(repo / "docs" / "base.md", "trailing whitespace  \n")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert next(item for item in data["checks"] if item["id"] == "diff")["status"] == "fail"

        repo, manifest = workspace(root, "ordinary")
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["card"]["id"] = "different-card"
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert data["manifest"]["normalized"] is False

        repo, manifest = workspace(root, "ordinary", production_lines=301)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["added_production_loc"] == 301

        repo, manifest = workspace(root, "ordinary", go_test_lines=301)
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "Go test LOC exclusion")
        assert data["complexity_guard"]["added_production_loc"] == 0

        repo, manifest = workspace(root, "ordinary", production_lines=444, go_test_lines=120,
                                   protocol=True, authorization=True, authorization_protocol=True)
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "published investigation authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   investigation_block_reference="example-card.md")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "published investigation filename reference")
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   investigation_block_reference="openspec/board/3.inprogress/example-card.md")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "published investigation board-path reference")
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   investigation_block_reference="other-card.md")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   investigation_block_reference="docs/example-card.md")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, protocol=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "not-declared"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   investigation_status="3.inprogress")
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True, mismatched_blocks=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True)
        source = repo / "openspec" / "board" / "4.done" / "published-investigation-authorization.md"
        write(source, source.read_text(encoding="utf-8").replace("# Published", "# Altered published", 1))
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", "openspec/board/3.inprogress/example-card.md", "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive manifest with stale authorization source")
        manifest = Path(json.loads(derived.stdout)["manifest"])
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=444, authorization=True,
                                   self_authorize_reference=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        repo, manifest = workspace(root, "ordinary", production_lines=501, authorization=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["limit"] == 500

        repo, manifest = workspace(root, "ordinary", executable_lines=302)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["added_production_loc"] == 302

        repo, manifest = workspace(root, "deterministic", executable_lines=1)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert next(item for item in data["checks"] if item["id"] == "risk-tier")["status"] == "fail"

        repo, manifest = workspace(root, "ordinary", executable_lines=302, executable_path="docs/helper")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "nonproduction executable preflight")
        assert data["complexity_guard"]["added_production_loc"] == 0

        repo, manifest = workspace(root, "ordinary", protocol=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True

    print("review preflight smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
