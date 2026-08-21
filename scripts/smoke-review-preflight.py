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
TARGET = {
    "schema": "changerail.execution-target.v1",
    "id": "database-primary",
    "fingerprint": "sha256:" + ("1" * 64),
    "target_substitution_policy": "forbid",
}
ALT_TARGET = {
    "schema": "changerail.execution-target.v1",
    "id": "database-rebound",
    "fingerprint": "sha256:" + ("2" * 64),
    "target_substitution_policy": "forbid",
}


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


def write_execution_target(repo: Path, identity: dict[str, str] = TARGET) -> None:
    write(repo / ".changerail" / "execution-target.json", json.dumps(identity, ensure_ascii=True, indent=2) + "\n")


def attach_target_evidence(repo: Path, manifest: Path, identities: list[dict[str, str]]) -> None:
    refs: list[dict[str, str]] = []
    for index, identity in enumerate(identities, start=1):
        evidence_id = f"target-evidence-{index}"
        index_path = repo / ".runtime" / "changerail" / "evidence" / evidence_id / "index.json"
        output_path = index_path.parent / "outputs" / f"{evidence_id}.txt"
        write(output_path, "target evidence fixture\n")
        write(
            index_path,
            json.dumps(
                {
                    "schema": "changerail.evidence-index.v1",
                    "updated_at": "2026-08-17T00:00:00Z",
                    "workspace": {"root": str(repo)},
                    "scope": {"card_id": "example-card", "changes": ["example-change"]},
                    "execution_target": identity,
                    "entries": [
                        {
                            "id": evidence_id,
                            "path": output_path.relative_to(repo).as_posix(),
                            "role": "raw_output",
                            "storage": "runtime",
                            "phase": "do",
                            "classification": "mandatory",
                            "status": "passed",
                            "started_at": "2026-08-17T00:00:00Z",
                            "ended_at": "2026-08-17T00:00:01Z",
                            "summary": "target evidence fixture passed",
                            "raw_output_path": output_path.relative_to(repo).as_posix(),
                            "command": {"argv": ["true"], "display": "true"},
                            "execution_target": identity,
                        }
                    ],
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
        )
        refs.append(
            {
                "id": evidence_id,
                "index_path": index_path.relative_to(repo).as_posix(),
                "raw_output_path": output_path.relative_to(repo).as_posix(),
                "classification": "mandatory",
            }
        )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["verification_summary"] = {
        "result": "passed",
        "summary": "target-bound evidence retained",
        "evidence_refs": refs,
    }
    manifest.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


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
              self_authorize_reference: bool = False, investigation_block_reference: str = "example-card",
              source_classification: str | None = None, bsl_lines: int = 0,
              bsl_path: str = "src/production/module.bsl", xml_text: str | None = None,
              xml_path: str = "src/designer/Form.xml", execution_target: bool = False) -> tuple[Path, Path]:
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
    if source_classification is not None:
        write(repo / ".changerail" / "source-classification.yaml", source_classification)
    if execution_target:
        write_execution_target(repo)
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
    if bsl_lines:
        write(repo / bsl_path, "\n".join(f"Procedure Synthetic{index}() EndProcedure" for index in range(bsl_lines)) + "\n")
    if xml_text is not None:
        write(repo / xml_path, xml_text)
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", str(card.relative_to(repo)), "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def source_classification(*, bsl: bool = False, designer_xml: bool = False, root: str = "src") -> str:
    kinds: list[str] = []
    if bsl:
        kinds.append(
            "  - id: bsl\n"
            "    suffixes: [\".bsl\"]\n"
            f"    production_roots: [\"{root}\"]\n"
            "    measure: lines\n"
        )
    if designer_xml:
        kinds.append(
            "  - id: designer-xml\n"
            "    suffixes: [\".xml\"]\n"
            f"    production_roots: [\"{root}\"]\n"
            "    measure: xml-structure\n"
        )
    return "schema: changerail.source-classification.v1\nsource_kinds:\n" + "".join(kinds)


def breakdown_entry(data: dict[str, Any], source_kind: str) -> dict[str, Any]:
    for entry in data["complexity_guard"]["source_breakdown"]:
        if entry["source_kind"] == source_kind:
            return entry
    raise AssertionError(f"missing source_breakdown entry for {source_kind}")


def verbose_xml(raw_lines: int = 360) -> str:
    comments = "\n".join(f"  <!-- synthetic formatter line {index} -->" for index in range(raw_lines))
    return f"<Form>\n{comments}\n  <Attribute>Value</Attribute>\n</Form>\n"


def preflight(
    repo: Path,
    manifest: Path,
    *options: str,
    card_path: str = "openspec/board/3.inprogress/example-card.md",
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    result = run(
        [str(HELPER), "preflight", card_path, "--workspace", str(repo), "--manifest", str(manifest), "--json", *options],
        repo,
    )
    if not result.stdout.strip():
        raise AssertionError(f"preflight emitted no machine result: {result.stderr}")
    return result, json.loads(result.stdout)


def exact_bounded_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-review-fingerprint-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-review-fingerprint-payload"
    successor_id = "deliver-bounded-review-fingerprint-optimization"
    authorization_id = "authorize-bounded-review-fingerprint-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": False,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("ordinary", authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-19-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact bounded authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_runner_retained_resume_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-runner-retained-resume-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-runner-retained-resume-payload-boundary"
    successor_id = "support-runner-resume-after-investigation-required"
    authorization_id = "authorize-bounded-runner-retained-resume-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("critical", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-19-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact runner retained-resume authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_live_progress_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-live-progress-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-field-validation-batch"
    successor_id = "expose-structured-live-delivery-progress"
    authorization_id = "authorize-bounded-live-progress-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("ordinary", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-21-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact live-progress authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_external_blocker_resume_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-external-blocker-resume-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-field-validation-batch"
    successor_id = "resume-retained-payload-after-external-blocker"
    authorization_id = "authorize-bounded-external-blocker-resume-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("critical", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-21-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact external-blocker resume authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_recovery_episodes_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-recovery-episodes-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-field-validation-batch"
    successor_id = "report-recovery-aware-delivery-episodes"
    authorization_id = "authorize-bounded-recovery-episodes-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("ordinary", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-21-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "runner_lineage.py", "\n".join(f"RUNNER_{index} = {index}" for index in range(300)) + "\n")
    write(repo / "src" / "metrics_rollup.py", "\n".join(f"METRIC_{index} = {index}" for index in range(144)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact recovery-episodes authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_verification_coverage_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-verification-coverage-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-field-validation-batch"
    successor_id = "define-verification-coverage-map"
    authorization_id = "authorize-bounded-verification-coverage-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("critical", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-21-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact verification-coverage authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


def exact_source_profile_authorization_workspace(root: Path) -> tuple[Path, Path]:
    repo = root / "repo-bounded-source-profile-authorization"
    while repo.exists():
        repo = repo.with_name(repo.name + "-next")
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.invalid")
    git(repo, "config", "user.name", "ChangeRail Smoke")
    write(repo / ".gitignore", ".runtime/\n")
    write(repo / "docs" / "base.md", "baseline\n")
    write(repo / "src" / "base.py", "BASE = True\n")
    investigation_id = "investigate-bounded-field-validation-batch"
    successor_id = "materialize-versioned-source-classification-profiles"
    authorization_id = "authorize-bounded-source-profile-payload"
    authorization_reference = json.dumps(
        {
            "authorization_card": f"openspec/board/4.done/{authorization_id}.md",
            "authorization_id": authorization_id,
        },
        separators=(",", ":"),
    )
    authorization_payload = json.dumps(
        {
            "investigation_card": f"openspec/board/4.done/{investigation_id}.md",
            "investigation_id": investigation_id,
            "successor_card": f"openspec/board/3.inprogress/{successor_id}.md",
            "successor_id": successor_id,
            "production_loc_ceiling": 500,
            "allow_new_authority_or_wire_protocol": True,
        },
        separators=(",", ":"),
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{investigation_id}.md",
        f"# Investigation\n\n## Status\n4.done\n\n## Blocks\n- `{successor_id}`\n",
    )
    write(
        repo / "openspec" / "board" / "4.done" / f"{authorization_id}.md",
        "# Authorization\n\n## Status\n4.done\n\n## Depends On\n"
        f"- `{investigation_id}`\n\n## Authorization\n"
        f"- Investigation authorization: `{authorization_payload}`\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    successor_path = f"openspec/board/3.inprogress/{successor_id}.md"
    write(
        repo / successor_path,
        card_text("critical", protocol=True, authorization=authorization_reference, blocks=investigation_id),
    )
    write(repo / "openspec" / "changes" / "archive" / "2026-08-21-example-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
    write(repo / "src" / "new.py", "\n".join(f"VALUE_{index} = {index}" for index in range(444)) + "\n")
    derived = run(
        [sys.executable, str(MANIFEST_HELPER), "derive", successor_path, "--workspace", str(repo), "--write", "--json"],
        repo,
    )
    require_ok(derived, "derive exact source-profile authorization manifest")
    return repo, Path(json.loads(derived.stdout)["manifest"])


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
        scope_repo, scope_manifest = repo, manifest

        repo, manifest = workspace(root, "ordinary", execution_target=True)
        attach_target_evidence(repo, manifest, [TARGET])
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "declared target preflight")
        assert data["outcome"] == "ready-for-llm-review"
        assert next(item for item in data["checks"] if item["id"] == "execution-target")["status"] == "pass"
        assert data["execution_target"]["evidence_identity_count"] == 1

        repo, manifest = workspace(root, "ordinary", execution_target=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert "missing execution_target" in next(item for item in data["checks"] if item["id"] == "execution-target")["detail"]

        repo, manifest = workspace(root, "ordinary", execution_target=True)
        attach_target_evidence(repo, manifest, [ALT_TARGET])
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert "differs from current declaration" in next(
            item for item in data["checks"] if item["id"] == "execution-target"
        )["detail"]

        repo, manifest = workspace(root, "ordinary", execution_target=True)
        attach_target_evidence(repo, manifest, [TARGET, ALT_TARGET])
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert "multiple execution targets" in next(
            item for item in data["checks"] if item["id"] == "execution-target"
        )["detail"]

        repo, manifest = scope_repo, scope_manifest
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

        repo, manifest = workspace(root, "ordinary", bsl_lines=301)
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "legacy unclassified BSL preflight")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["complexity_guard"]["added_production_loc"] == 0

        repo, manifest = workspace(
            root,
            "ordinary",
            bsl_lines=301,
            source_classification=source_classification(bsl=True),
        )
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["added_production_loc"] == 301
        bsl = breakdown_entry(data, "bsl")
        assert bsl["measure_strategy"] == "lines"
        assert bsl["path_count"] == 1
        assert bsl["raw_added_lines"] == 301
        assert bsl["effective_complexity"] == 301

        repo, manifest = workspace(
            root,
            "ordinary",
            bsl_lines=301,
            bsl_path="src/tests/module.bsl",
            source_classification=source_classification(bsl=True),
        )
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "non-production BSL exclusion")
        assert data["complexity_guard"]["added_production_loc"] == 0
        bsl = breakdown_entry(data, "bsl")
        assert bsl["path_count"] == 0
        assert bsl["excluded_path_count"] == 1
        assert bsl["excluded_raw_added_lines"] == 301

        invalid_classification = (
            "schema: changerail.source-classification.v1\n"
            "source_kinds:\n"
            "  - id: bsl\n"
            "    suffixes: [\".bsl\"]\n"
            "    production_roots: [\"/absolute\"]\n"
            "    measure: lines\n"
        )
        repo, manifest = workspace(root, "ordinary", source_classification=invalid_classification)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "blocked"
        assert next(item for item in data["checks"] if item["id"] == "source-classification")["status"] == "fail"

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

        exact_successor_path = "openspec/board/3.inprogress/deliver-bounded-review-fingerprint-optimization.md"
        repo, manifest = exact_bounded_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact bounded review fingerprint authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md",
                "authorization_id": "authorize-bounded-review-fingerprint-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-fingerprint-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "ordinary",
                authorization=authorization_reference,
                blocks="investigate-bounded-review-fingerprint-payload",
            ).replace("example-change", "mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-19-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched bounded authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md"
        repo, manifest = exact_runner_retained_resume_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact runner retained-resume authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "critical"
        assert data["risk"]["reasoning_effort"] == "xhigh"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact runner successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-runner-retained-resume-payload.md",
                "authorization_id": "authorize-bounded-runner-retained-resume-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-runner-resume-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "critical",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-runner-retained-resume-payload-boundary",
            ).replace("example-change", "runner-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-19-runner-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched runner retained-resume authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/expose-structured-live-delivery-progress.md"
        repo, manifest = exact_live_progress_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact live-progress authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "ordinary"
        assert data["risk"]["reasoning_effort"] == "high"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact live-progress successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-live-progress-payload.md",
                "authorization_id": "authorize-bounded-live-progress-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-live-progress-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "ordinary",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-bounded-field-validation-batch",
            ).replace("example-change", "live-progress-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-21-live-progress-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched live-progress authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/resume-retained-payload-after-external-blocker.md"
        repo, manifest = exact_external_blocker_resume_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact external-blocker resume authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "critical"
        assert data["risk"]["reasoning_effort"] == "xhigh"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact external-blocker successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-external-blocker-resume-payload.md",
                "authorization_id": "authorize-bounded-external-blocker-resume-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-external-blocker-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "critical",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-bounded-field-validation-batch",
            ).replace("example-change", "external-blocker-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-21-external-blocker-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched external-blocker resume authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/report-recovery-aware-delivery-episodes.md"
        repo, manifest = exact_recovery_episodes_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact recovery-episodes authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "ordinary"
        assert data["risk"]["reasoning_effort"] == "high"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact recovery-episodes successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-recovery-episodes-payload.md",
                "authorization_id": "authorize-bounded-recovery-episodes-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-recovery-episodes-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "ordinary",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-bounded-field-validation-batch",
            ).replace("example-change", "recovery-episodes-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-21-recovery-episodes-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched recovery-episodes authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/define-verification-coverage-map.md"
        repo, manifest = exact_verification_coverage_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact verification-coverage authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "critical"
        assert data["risk"]["reasoning_effort"] == "xhigh"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact verification-coverage successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-verification-coverage-payload.md",
                "authorization_id": "authorize-bounded-verification-coverage-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-verification-coverage-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "critical",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-bounded-field-validation-batch",
            ).replace("example-change", "verification-coverage-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-21-verification-coverage-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched verification-coverage authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "invalid"

        exact_successor_path = "openspec/board/3.inprogress/materialize-versioned-source-classification-profiles.md"
        repo, manifest = exact_source_profile_authorization_workspace(root)
        result, data = preflight(repo, manifest, "--normalize", card_path=exact_successor_path)
        require_ok(result, "exact source-profile authorization")
        assert data["outcome"] == "ready-for-llm-review"
        assert data["risk"]["tier"] == "critical"
        assert data["risk"]["reasoning_effort"] == "xhigh"
        assert data["complexity_guard"]["added_production_loc"] == 444
        assert data["complexity_guard"]["limit"] == 500
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True
        assert data["complexity_guard"]["published_investigation_authorization"]["status"] == "valid"

        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "exact source-profile successor payload")
        authorization_reference = json.dumps(
            {
                "authorization_card": "openspec/board/4.done/authorize-bounded-source-profile-payload.md",
                "authorization_id": "authorize-bounded-source-profile-payload",
            },
            separators=(",", ":"),
        )
        mismatched_path = "openspec/board/3.inprogress/other-source-profile-successor.md"
        write(
            repo / mismatched_path,
            card_text(
                "critical",
                protocol=True,
                authorization=authorization_reference,
                blocks="investigate-bounded-field-validation-batch",
            ).replace("example-change", "source-profile-mismatch-change"),
        )
        write(repo / "openspec" / "changes" / "archive" / "2026-08-21-source-profile-mismatch-change" / "tasks.md", "## Tasks\n\n- [x] done\n")
        derived = run(
            [sys.executable, str(MANIFEST_HELPER), "derive", mismatched_path, "--workspace", str(repo), "--write", "--json"],
            repo,
        )
        require_ok(derived, "derive mismatched source-profile authorization manifest")
        result, data = preflight(repo, Path(json.loads(derived.stdout)["manifest"]), "--normalize", card_path=mismatched_path)
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

        repo, manifest = workspace(
            root,
            "ordinary",
            xml_text="<Form>\n  <Attribute>Value</Attribute>\n</Form>\n",
            source_classification=source_classification(designer_xml=True, root="src/designer"),
        )
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "classified Designer XML preflight")
        designer = breakdown_entry(data, "designer-xml")
        assert designer["measure_strategy"] == "xml-structure"
        assert designer["path_count"] == 1
        assert designer["raw_added_lines"] == 3
        assert designer["effective_complexity"] == 3
        assert data["complexity_guard"]["added_production_loc"] == 3

        repo, manifest = workspace(root, "ordinary", xml_text=verbose_xml(), xml_path="schemas/generic.xml")
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "generic XML suffix remains non-production")
        assert data["complexity_guard"]["added_production_loc"] == 0

        repo, manifest = workspace(
            root,
            "ordinary",
            xml_text=verbose_xml(),
            source_classification=source_classification(designer_xml=True, root="src/designer"),
        )
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "verbose Designer XML structural measure")
        designer = breakdown_entry(data, "designer-xml")
        assert designer["raw_added_lines"] > 300
        assert designer["effective_complexity"] <= 300
        assert designer["fallback"] == "none"
        assert data["complexity_guard"]["added_production_loc"] == designer["effective_complexity"]

        repo, manifest = workspace(
            root,
            "ordinary",
            xml_text="<Form>\n  <Broken>\n",
            source_classification=source_classification(designer_xml=True, root="src/designer"),
        )
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "malformed Designer XML raw-line fallback")
        designer = breakdown_entry(data, "designer-xml")
        assert designer["fallback"] == "raw-lines"
        assert designer["raw_added_lines"] == 2
        assert designer["effective_complexity"] == 2

        repo, manifest = workspace(
            root,
            "ordinary",
            bsl_lines=5,
            xml_text="<Form>\n  <Attribute>Value</Attribute>\n</Form>\n",
            source_classification=source_classification(bsl=True, designer_xml=True, root="src"),
        )
        result, data = preflight(repo, manifest, "--normalize")
        require_ok(result, "mixed BSL and Designer XML preflight")
        assert breakdown_entry(data, "bsl")["effective_complexity"] == 5
        assert breakdown_entry(data, "designer-xml")["effective_complexity"] == 3
        assert data["complexity_guard"]["added_production_loc"] == 8

        repo, manifest = workspace(root, "ordinary", protocol=True)
        result, data = preflight(repo, manifest, "--normalize")
        assert result.returncode == 1
        assert data["outcome"] == "investigation-required"
        assert data["complexity_guard"]["new_authority_or_wire_protocol"] is True

        repo, manifest = workspace(root, "ordinary")
        card = repo / "openspec" / "board" / "3.inprogress" / "example-card.md"
        write(
            card,
            card.read_text(encoding="utf-8").replace(
                "- New authority or wire protocol: `no`",
                "- New authority or wire protocol: `yes`; explanation",
            ),
        )
        result = run(
            [
                str(HELPER),
                "preflight",
                "openspec/board/3.inprogress/example-card.md",
                "--workspace",
                str(repo),
                "--manifest",
                str(manifest),
                "--normalize",
                "--json",
            ],
            repo,
        )
        assert result.returncode == 1
        diagnostic = json.loads(result.stderr)
        assert diagnostic["diagnostic"]["code"] == "validation_failed"
        assert "New authority or wire protocol must be yes or no" in diagnostic["diagnostic"]["message"]

    print("review preflight smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
