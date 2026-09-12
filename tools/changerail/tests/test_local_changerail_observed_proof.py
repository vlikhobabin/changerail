"""Typed, byte-bound observed-proof contract checks."""

from __future__ import annotations

import hashlib
import copy
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import pytest
from scripts.changerail.adapters.pytest import _final_receipt_nodes as pytest_nodes


MODULE_PATH = Path(__file__).parents[3] / "scripts" / "changerail" / "local_delivery.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "local_delivery_observed", MODULE_PATH
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
delivery = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(delivery)


def _path(*parts: str) -> str:
    return "/".join(parts)


def _proof_card() -> str:
    rows = [
        {
            "condition": "C1",
            "seam": "inspection",
            "precondition": "before",
            "action": "inspect",
            "expected": "bound",
            "method": {"kind": "inspection", "target": "source.txt"},
            "stage": "implementation",
        },
        {
            "condition": "C2",
            "seam": "receipt",
            "precondition": "before",
            "action": "test",
            "expected": "bound",
            "method": {"kind": "test", "target": "tests/test_receipt.py::test_value"},
            "stage": "review",
        },
        {
            "condition": "C3",
            "seam": "runtime",
            "precondition": "before",
            "action": "observe",
            "expected": "bound",
            "method": {"kind": "runtime", "target": "offline-target"},
            "stage": "final",
        },
    ]
    risks = [
        {"kinds": [kind], "applies": False, "decision": "fixture", "conditions": []}
        for kind in (
            "input_safety",
            "mutation",
            "restart",
            "concurrency",
            "publication",
            "external_effects",
        )
    ]
    return (
        """# Proof fixture

## Lifecycle
openspec-v1

## Acceptance

### Requirement: observed proof

#### Scenario: each typed observation is bound

- [C1] WHEN an inspection records actual fragments
- [C2] THEN a pytest receipt identifies the selected parameter
- [C3] AND a runtime fixture retains its provenance records

## Design

- Fixture only.

## Verify

```json
"""
        + json.dumps(
            {
                "schema": "changerail.card-evidence.v1",
                "conditions": rows,
                "risks": risks,
            }
        )
        + """
```
"""
    )


def _proof_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "proof@example.invalid"], cwd=root, check=True
    )
    subprocess.run(["git", "config", "user.name", "Proof"], cwd=root, check=True)
    card = root / "openspec" / "board" / "3.inprogress" / "proof.md"
    card.parent.mkdir(parents=True)
    card.write_text(_proof_card(), encoding="utf-8")
    (root / "source.txt").write_text("actual inspected source\n", encoding="utf-8")
    (root / "unrelated.txt").write_text(
        "unrelated inspected source\n", encoding="utf-8"
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_receipt.py").write_text(
        "import pytest\n\n@pytest.mark.parametrize('value', ['one', 'two'])\ndef test_value(value):\n    before_state = {'value': value}\n    action_state = {'value': before_state['value'].upper()}\n    after_state = {'value': action_state['value'].lower()}\n    assert before_state['value'] in {'one', 'two'}\n    assert action_state['value'] in {'ONE', 'TWO'}\n    assert after_state['value'] == value\n\ndef test_failure():\n    assert False\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True
    )
    run_dir = root / ".runtime" / "changerail" / "runs" / "proof-run"
    run_dir.mkdir(parents=True)
    monkeypatch.setattr(delivery, "REPO_ROOT", root)
    monkeypatch.setattr(delivery, "BOARD_ROOT", root / "openspec" / "board")
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", root / ".runtime/changerail")
    monkeypatch.setattr(delivery, "checked_frozen_records", lambda: {})
    # Isolate typed evidence from artifact orchestration, covered by native integration.
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    card_name = _path("openspec", "board", "3.inprogress", "proof.md")
    selection = {
        "schema": "changerail.observed-proof-selection.v1",
        "root": delivery.repo_relative(run_dir),
        "owner": {"run_id": run_dir.name, "card": card_name},
        "required_stages": ["implementation", "review", "final"],
    }
    selection_path = run_dir / "observed-proof-selection.json"
    delivery.write_json(selection_path, selection)
    delivery.write_json(
        run_dir / "run.json",
        {
            "schema": "changerail.delivery-run.v2",
            "run_id": run_dir.name,
            "card": card_name,
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "observed_proof_contract": {
                "schema": "changerail.observed-proof.v1",
                "required_stages": ["implementation", "review", "final"],
                "selection": {
                    "path": delivery.repo_relative(selection_path),
                    "sha256": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
                },
            },
        },
    )
    return root, card, run_dir


def _reference(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": delivery.repo_relative(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _fragment(path: Path, start: int, end: int) -> dict[str, object]:
    reference = _reference(path)
    data = path.read_bytes()
    return {
        **reference,
        "start": start,
        "end": end,
        "fragment_sha256": hashlib.sha256(data[start:end]).hexdigest(),
    }


def _fragments(run_dir: Path) -> dict[str, object]:
    trace = run_dir / "observed-bytes.txt"
    trace.write_bytes(b"before state\naction performed\nafter state\n")
    data = trace.read_bytes()
    first = data.index(b"\n") + 1
    second = data.index(b"\n", first) + 1
    return {
        "before": _fragment(trace, 0, first),
        "action": _fragment(trace, first, second),
        "after": _fragment(trace, second, len(data)),
    }


def _base(
    root: Path,
    card: Path,
    run_dir: Path,
    row: dict[str, object],
    *,
    role: str,
    artifact: Path,
    fragments: dict[str, object],
    assertion_support: dict[str, object] | None = None,
) -> dict[str, object]:
    proof = {
        "schema": "changerail.card-proof.v1",
        "run": {"run_id": run_dir.name, "card": delivery.repo_relative(card)},
        "inventory_digest": delivery.derive_proof_inventory(card)["digest"],
        "payload": delivery.payload_fingerprint(),
        "condition": row["identity"],
        "method": {"kind": row["method"]["kind"], "target": row["method"]["target"]},
        "stage": row["stage"],
        "observation_id": f"{role}-{row['condition']}",
        "recorder_role": role,
        "kind": row["method"]["kind"],
        "outcome": "pass",
        "artifact": _reference(artifact),
        "fragments": fragments,
    }
    if row["method"]["kind"] == "test":
        proof["assertion_support"] = assertion_support or _assertion_support(
            root, str(row["method"]["target"])
        )
        proof["fragments"] = proof["assertion_support"]["fragments"]
    return proof


def _assertion_support(root: Path, target: str) -> dict[str, object]:
    source = root / target.partition("::")[0]
    data = source.read_bytes()
    fragments: dict[str, object] = {}
    for name in ("before", "action", "after"):
        marker = f"assert {name}_state".encode()
        start = data.index(marker)
        end = data.index(b"\n", start) + 1
        fragments[name] = _fragment(source, start, end)
    return {"source": _reference(source), "fragments": fragments}


def _inspection_proof(root: Path, card: Path, run_dir: Path) -> dict[str, object]:
    row = next(
        item
        for item in delivery.derive_proof_inventory(card)["conditions"]
        if item["condition"] == "C1"
    )
    fragments = _fragments(run_dir)
    source = _reference(root / "source.txt")
    observed = {
        "schema": "changerail.inspection-observation.v1",
        "observer": "fixture",
        "role": "implementation",
        "observed_at": "2026-09-07T00:00:00Z",
        "condition": row["identity"],
        "inspected_sources": [source],
        "fragments": fragments,
        "conclusion": "C1 fragments observed",
        "mocked_seams": ["none"],
        "residual_risks": ["offline fixture"],
    }
    artifact = run_dir / "inspection.json"
    artifact.write_text(json.dumps(observed), encoding="utf-8")
    return _base(
        root,
        card,
        run_dir,
        row,
        role="implementation",
        artifact=artifact,
        fragments=fragments,
    )


def _actual_pytest_proof(root: Path, card: Path, run_dir: Path) -> dict[str, object]:
    assert (
        delivery.run_evidence(
            "real-pytest",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-vv",
                "tests/test_receipt.py::test_value[one]",
            ],
        )
        == 0
    )
    receipt = next((run_dir / "focused-evidence").glob("*.json"))
    item, log, current = delivery.read_check_result(receipt, run_dir, "focused")
    assert current
    match = re.search(
        r"(?m)^tests/test_receipt\.py::test_value\[one\][ \t]+PASSED(?:[ \t]+\[[^\r\n]*\])?[ \t]*$",
        log.decode(),
    )
    assert match is not None
    row = next(
        item
        for item in delivery.derive_proof_inventory(card)["conditions"]
        if item["condition"] == "C2"
    )
    proof = _base(
        root,
        card,
        run_dir,
        row,
        role="review",
        artifact=receipt,
        fragments=_fragments(run_dir),
    )
    proof.update(
        {
            "lane": "focused",
            "attempt_id": item["attempt_id"],
            "command_identity": item["command_identity"],
            "selected_nodes": [
                {
                    "node": "tests/test_receipt.py::test_value[one]",
                    "start": match.start(),
                    "end": match.end(),
                }
            ],
        }
    )
    return proof


def _receipt_with_label(run_dir: Path, label: str) -> Path:
    return next(
        path
        for path in (run_dir / "focused-evidence").glob("*.json")
        if delivery._check_json(path)["label"] == label
    )


def _runtime_proof(root: Path, card: Path, run_dir: Path) -> dict[str, object]:
    row = next(
        item
        for item in delivery.derive_proof_inventory(card)["conditions"]
        if item["condition"] == "C3"
    )
    owner = {"run_id": run_dir.name, "card": delivery.repo_relative(card)}
    target = {"kind": "fixture", "identity": "offline-target"}
    session = {"identity": "fixture-session", "started_at": "2026-09-07T00:00:00Z"}
    refs: dict[str, dict[str, object]] = {}
    for kind in ("authorization", "preflight", "not_applicable"):
        record = run_dir / f"{kind}.json"
        outcome = {
            "authorization": "authorized",
            "preflight": "passed",
            "not_applicable": "not_applicable",
        }[kind]
        payload: dict[str, object] = {
            "schema": "changerail.runtime-reference.v1",
            "run": owner,
            "kind": kind,
            "outcome": outcome,
            "scope": {"target": target, "session": session},
            "fixture_only": True,
            "observed_at": "2026-09-07T00:00:00Z",
        }
        if kind == "not_applicable":
            payload["resolution"] = {
                "kind": "not_applicable",
                "reason": "fixture does not execute a native runtime",
            }
        record.write_text(json.dumps(payload), encoding="utf-8")
        refs[kind] = _reference(record)
    runtime = {
        "target": target,
        "session": session,
        "fixture_only": True,
        "authorization": refs["authorization"],
        "preflight": refs["preflight"],
        "markers": ["offline marker"],
        "recovery": {"kind": "not_applicable", "reference": refs["not_applicable"]},
    }
    fragments = _fragments(run_dir)
    observed = {
        "schema": "changerail.runtime-observation.v1",
        "observer": "fixture",
        "role": "outer",
        "observed_at": "2026-09-07T00:00:00Z",
        "condition": row["identity"],
        "inspected_sources": [],
        "fragments": fragments,
        "conclusion": "offline fixture only",
        "mocked_seams": ["native runtime"],
        "residual_risks": ["not native proof"],
        "runtime": runtime,
    }
    artifact = run_dir / "runtime.json"
    artifact.write_text(json.dumps(observed), encoding="utf-8")
    proof = _base(
        root, card, run_dir, row, role="outer", artifact=artifact, fragments=fragments
    )
    proof["runtime"] = runtime
    return proof


def _final_v2_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    final_target: str = "tests/test_receipt.py",
    additional_final_targets: tuple[str, ...] = (),
) -> tuple[Path, Path, Path, dict[str, object], dict[str, object]]:
    """Build a current v2 GO with real implementation/review receipts.

    The profile commands are intentionally harmless local pytest invocations.
    Preverification and final verification consume them normally; this helper
    only prepares the independent reviewer decision that a real model would
    have written.
    """

    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    final_method = {"kind": "test", "target": final_target}
    if additional_final_targets:
        final_method["additional_targets"] = list(additional_final_targets)
        for target in additional_final_targets:
            source = root / target.partition("::")[0]
            if not source.exists():
                source.write_bytes((root / "tests/test_receipt.py").read_bytes())
    text = _proof_card().replace(
        '"method": {"kind": "runtime", "target": "offline-target"}, "stage": "final"',
        f'"method": {json.dumps(final_method)}, "stage": "final"',
    )
    card.write_text(
        text
        + """
## Status

3.inprogress

## Depends On

- none

## Result

The isolated fixture retains substantive implementation evidence for final verification.

## Next

- runner-owned review and verification

## Log

- 2026-09-07T00:00:00Z: prepared isolated final verification fixture
""",
        encoding="utf-8",
    )
    command = (
        f"{sys.executable} -m pytest -p no:cacheprovider -vv "
        "tests/test_receipt.py::test_value[one]"
    )
    final_commands = [command] + [
        f"{sys.executable} -m pytest -p no:cacheprovider -v {target}[one]"
        for target in additional_final_targets
    ]
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "models": {
                "review": {"model": "fixture-review", "reasoning_effort": "low"}
            },
            "verification": {
                "pre_review_commands": [command],
                "final_commands": final_commands,
            },
            "budgets": {"enforce_limits": False},
        },
    )
    # This is an ordinary 03D fixture.  It deliberately has no finalizer
    # attempt/creation capability and must not borrow the offline route.
    delivery.write_json(
        delivery.manifest_path(delivery.card_id(card)),
        {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run_dir.name,
            "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
        },
    )
    delivery.capture_manifest(str(card))

    implementation = _inspection_proof(root, card, run_dir)
    delivery.record_observed_proof(run_dir, implementation)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    review = _actual_pytest_proof(root, card, run_dir)
    delivery.record_observed_proof(run_dir, review)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")

    template = delivery.verdict_template(str(card))["template"]
    decision = template["decisions"][0]
    proof_ids = {
        implementation["condition"]: implementation["observation_id"],
        review["condition"]: review["observation_id"],
    }
    for reference in decision["condition_refs"]:
        if reference["stage"] != "final":
            reference["observation_ids"] = [proof_ids[reference["condition"]]]
    decision["observation_ids"] = list(proof_ids.values())
    decision["assessment"] = (
        "The retained implementation inspection and selected review pytest node "
        "bind the current non-final clauses; final receipt evidence remains pending."
    )
    delivery.write_json(delivery.verdict_path(delivery.card_id(card)), template)
    assert delivery.validate_verdict(str(card))["result"] == "go"
    final_row = next(
        row
        for row in delivery.derive_proof_inventory(card)["conditions"]
        if row["stage"] == "final"
    )
    supplied = run_dir / "final-input.json"
    delivery.write_json(
        supplied,
        {
            "schema": "changerail.final-test-proof-input.v1",
            "run": {"run_id": run_dir.name, "card": delivery.repo_relative(card)},
            "payload": delivery.payload_fingerprint(),
            "inventory_digest": delivery.derive_proof_inventory(card)["digest"],
            "condition": final_row["identity"],
            "assertion_support": _assertion_support(
                root, str(final_row["method"]["target"])
            ),
        },
    )
    # Implementation/review may retain only this inert assertion draft. The
    # outer verify path later binds it to the real configured final receipt.
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.retain_final_test_proof_input(run_dir, supplied)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    return root, card, run_dir, implementation, review


def _proof_from_test_receipt(
    root, card, run_dir, condition, target, receipt, support=None
):
    row = copy.deepcopy(
        next(
            row
            for row in delivery.derive_proof_inventory(card)["conditions"]
            if row["condition"] == condition
        )
    )
    row["method"] = {"kind": "test", "target": target}
    item, log, current = delivery.read_check_result(receipt, run_dir, "focused")
    assert current
    support = support or _assertion_support(root, target)
    proof = _base(
        root,
        card,
        run_dir,
        row,
        role=row["stage"],
        artifact=receipt,
        fragments=support["fragments"],
        assertion_support=support,
    )
    proof.update(
        lane="focused",
        attempt_id=item["attempt_id"],
        command_identity=item["command_identity"],
        selected_nodes=pytest_nodes(item, log, target),
    )
    assert proof["selected_nodes"]
    return proof


def test_multiple_test_targets_and_shared_execution_cover_conditions(
    tmp_path, monkeypatch
):
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    primary = "tests/test_receipt.py::test_value"
    other = "tests/test_other.py::test_value"
    (root / "tests/test_other.py").write_bytes(
        (root / "tests/test_receipt.py").read_bytes()
    )
    plan = delivery._evidence_plan_json(card.read_text())
    original = json.dumps(plan)
    plan["conditions"][0]["method"] = {
        "kind": "test",
        "target": primary,
        "additional_targets": [other],
    }
    card.write_text(card.read_text().replace(original, json.dumps(plan)))
    shared = _actual_pytest_proof(root, card, run_dir)
    first = _proof_from_test_receipt(
        root,
        card,
        run_dir,
        "C1",
        primary,
        root / shared["artifact"]["path"],
    )
    delivery.record_observed_proof(run_dir, first)
    with pytest.raises(delivery.DeliveryError, match=re.escape(other)):
        delivery.require_current_stage_proofs(card, run_dir, ["implementation"])
    assert (
        delivery.run_evidence(
            "other-pytest",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-v",
                other + "[two]",
            ],
        )
        == 0
    )
    second = _proof_from_test_receipt(
        root,
        card,
        run_dir,
        "C1",
        other,
        _receipt_with_label(run_dir, "other-pytest"),
    )
    second["observation_id"] += "-other"
    delivery.record_observed_proof(run_dir, second)
    another = copy.deepcopy(first)
    another["observation_id"] += "-additional-assertions"
    delivery.record_observed_proof(run_dir, another)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.record_observed_proof(run_dir, shared)
    records = delivery.require_current_stage_proofs(
        card, run_dir, ["implementation", "review"]
    )
    assert {p["observation_id"] for p in records} == {
        p["observation_id"] for p in (first, second, another, shared)
    }
    assert first["artifact"] == shared["artifact"]
    assert first["attempt_id"] == shared["attempt_id"]
    assert first["selected_nodes"] == shared["selected_nodes"]
    assert len(list((run_dir / "focused-evidence").glob("*.json"))) == 2

    template = delivery.verdict_template(str(card))["template"]
    decision = template["decisions"][0]
    for ref in decision["condition_refs"]:
        if ref["stage"] != "final":
            ref["observation_ids"] = [
                p["observation_id"]
                for p in records
                if p["condition"] == ref["condition"]
            ]
    decision["observation_ids"] = [p["observation_id"] for p in records]
    decision["assessment"] = (
        "Both required C1 targets passed; C2 shares the actual selected execution with its own current record."
    )
    delivery.write_json(delivery.verdict_path(delivery.card_id(card)), template)
    assert delivery.validate_verdict(str(card))["result"] == "go"
    index_before = (run_dir / "proof-index.json").read_bytes()
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    with pytest.raises(delivery.DeliveryError, match="duplicate observation"):
        delivery.record_observed_proof(run_dir, first)
    for mutation, message in (
        (lambda p: p["method"].update(target="tests/foreign.py"), "foreign"),
        (
            lambda p: p["selected_nodes"].append(copy.deepcopy(p["selected_nodes"][0])),
            "schema validation|outside declared selector",
        ),
        (
            lambda p: p.update(selected_nodes=copy.deepcopy(first["selected_nodes"])),
            "outside declared selector",
        ),
    ):
        invalid = copy.deepcopy(second)
        invalid["observation_id"] = "invalid-proof"
        mutation(invalid)
        with pytest.raises(delivery.DeliveryError, match=message):
            delivery.record_observed_proof(run_dir, invalid)
        assert (run_dir / "proof-index.json").read_bytes() == index_before
    # Even surplus records remain authenticated: a broken receipt cannot hide
    # behind another record of the same condition/target.
    receipt = root / shared["artifact"]["path"]
    receipt.write_bytes(receipt.read_bytes() + b" ")
    with pytest.raises(delivery.DeliveryError, match="integrity failed"):
        delivery.require_current_stage_proofs(card, run_dir, ["implementation"])
    assert (run_dir / "proof-index.json").read_bytes() == index_before


def _executed_helper_proof(tmp_path, monkeypatch):
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    source = root / "tests/test_receipt.py"
    helper = root / "tests/helper.py"
    helper.write_text(
        "def check_value(value):\n"
        "    before_state = value\n    assert before_state == 'one'\n"
        "    action_state = value.upper()\n    assert action_state == 'ONE'\n"
        "    after_state = action_state.lower()\n    assert after_state == value\n"
    )
    source.write_text(
        "import pytest\nfrom helper import check_value\n"
        "@pytest.mark.parametrize('value', ['one'])\n"
        "def test_value(value):\n    check_value(value)\n"
    )
    target = "tests/test_receipt.py::test_value"
    assert (
        delivery.run_evidence(
            "helper-pytest",
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-v", target],
        )
        == 0
    )
    support = _assertion_support(root, "tests/helper.py")
    support["source"] = _reference(source)
    start = source.read_bytes().index(b"    check_value(value)")
    support["invocation"] = _fragment(source, start, len(source.read_bytes()))
    proof = _proof_from_test_receipt(
        root,
        card,
        run_dir,
        "C2",
        target,
        _receipt_with_label(run_dir, "helper-pytest"),
        support,
    )
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    return root, card, run_dir, source, helper, proof


def test_invoked_helper_fragments_are_authenticated_before_recording(
    tmp_path, monkeypatch
):
    root, card, run_dir, source, helper, proof = _executed_helper_proof(
        tmp_path, monkeypatch
    )
    retained = delivery.record_observed_proof(run_dir, proof)
    before = {p: p.read_bytes() for p in (retained, run_dir / "proof-index.json")}
    assert delivery.require_current_stage_proofs(card, run_dir, ["review"]) == [proof]
    helper_bytes = helper.read_bytes()
    log_source = run_dir / "fake-source.py"
    log_source.write_bytes(helper_bytes)
    alias = run_dir / "helper-alias.py"
    alias.symlink_to(helper)
    for mutation, message in (
        (lambda p: p["assertion_support"].pop("invocation"), "requires invocation"),
        (
            lambda p: p["assertion_support"].update(
                invocation=p["fragments"]["before"]
            ),
            "invocation does not bind",
        ),
        (
            lambda p: p["assertion_support"]["invocation"].update(
                end=len(source.read_bytes()) + 1
            ),
            "offsets",
        ),
        (
            lambda p: p["assertion_support"]["invocation"].update(
                fragment_sha256="0" * 64
            ),
            "fragment identity",
        ),
        (
            lambda p: p["assertion_support"]["source"].update(sha256="0" * 64),
            "integrity failed",
        ),
        (
            lambda p: p["fragments"]["after"].update(sha256="0" * 64),
            "not from its declared source",
        ),
        (
            lambda p: p["fragments"]["before"].update(end=len(helper_bytes) + 1),
            "offsets",
        ),
        (
            lambda p: p["fragments"]["before"].update(fragment_sha256="0" * 64),
            "fragment identity",
        ),
        (
            lambda p: p["fragments"]["before"].update(path="../helper.py"),
            "schema validation",
        ),
        (
            lambda p: p["fragments"]["before"].update(**_reference(log_source)),
            "not a repository source",
        ),
        (
            lambda p: p["fragments"]["before"].update(
                path=alias.relative_to(root).as_posix()
            ),
            "safely read",
        ),
    ):
        invalid = copy.deepcopy(proof)
        invalid["observation_id"] = "invalid-helper"
        mutation(invalid)
        with pytest.raises(delivery.DeliveryError, match=message):
            delivery.record_observed_proof(run_dir, invalid)
        assert {p: p.read_bytes() for p in before} == before
    helper.write_bytes(helper_bytes + b"# changed helper\n")
    with pytest.raises(delivery.DeliveryError, match="integrity failed"):
        delivery._validate_test_assertion_support(
            proof["assertion_support"], proof["method"]["target"]
        )
    with pytest.raises(delivery.DeliveryError, match="stale"):
        delivery.require_current_stage_proofs(card, run_dir, ["review"])
    assert {p: p.read_bytes() for p in before} == before


def test_helper_sources_are_read_once_per_validation(tmp_path, monkeypatch):
    _root, _card, _run_dir, source, helper, proof = _executed_helper_proof(
        tmp_path, monkeypatch
    )
    reads = {source: 0, helper: 0}
    original = {p: p.read_bytes() for p in reads}
    real_read = delivery._check_bytes

    def swap_after_read(path, limit=32 * 1024 * 1024):
        data = real_read(path, limit)
        if path in reads:
            reads[path] += 1
            path.write_bytes(b"# swapped after authenticating bytes\n")
        return data

    monkeypatch.setattr(delivery, "_check_bytes", swap_after_read)
    delivery._validate_test_assertion_support(
        proof["assertion_support"], proof["method"]["target"]
    )
    assert reads == {source: 1, helper: 1}
    source.write_bytes(original[source])
    with pytest.raises(delivery.DeliveryError, match="integrity failed"):
        delivery._validate_test_assertion_support(
            proof["assertion_support"], proof["method"]["target"]
        )
    assert reads == {source: 2, helper: 2}


@pytest.mark.parametrize("missing", ["draft", "node"])
def test_final_multiple_targets_preserve_partial_supply_and_history(
    tmp_path, monkeypatch, missing
):
    other = "tests/test_other.py::test_value"
    root, card, run_dir, _implementation, _review = _final_v2_repository(
        tmp_path,
        monkeypatch,
        additional_final_targets=(other,),
    )
    if missing == "node":
        configured = delivery.profile()
        configured["verification"]["final_commands"] = configured["verification"][
            "final_commands"
        ][:1]
        monkeypatch.setattr(delivery, "profile", lambda: configured)
    inventory = delivery.derive_proof_inventory(card)
    primary_input = delivery._check_json(run_dir / "final-input.json")
    assert "method" not in primary_input  # Existing singleton draft is unchanged.
    extra_input = copy.deepcopy(primary_input)
    extra_input.update(
        method={"kind": "test", "target": other},
        assertion_support=_assertion_support(root, other),
    )
    draft = run_dir / "extra-final-input.json"
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    for method in (
        {"kind": "test", "target": "tests/foreign.py"},
        {"kind": "test", "target": other, "additional_targets": [other]},
        {"kind": "inspection", "target": other},
    ):
        invalid = {**extra_input, "method": method}
        delivery.write_json(draft, invalid)
        with pytest.raises(delivery.DeliveryError, match="method is foreign"):
            delivery.retain_final_test_proof_input(run_dir, draft)
    delivery.write_json(draft, extra_input)
    if missing == "node":
        delivery.retain_final_test_proof_input(run_dir, draft)
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.preverify(str(card)) == 0
    with pytest.raises(delivery.DeliveryError, match=re.escape(other)):
        delivery.verify_as_outer_dispatch(str(card))
    cycles = sorted((run_dir / "verification").glob("cycle-*"))
    verification_before = (run_dir / "verification.json").read_bytes()
    records = delivery._validated_index_records(
        delivery._check_json(run_dir / "proof-index.json"),
        card=card,
        run_dir=run_dir,
        inventory=inventory,
    )
    finals = [p for p in records if p["stage"] == "final"]
    assert len(finals) == 1 and finals[0]["method"]["target"] == "tests/test_receipt.py"
    assert (
        finals[0]["observation_id"]
        == "outer-final-"
        + hashlib.sha256(finals[0]["condition"].encode()).hexdigest()[:16]
    )
    retained = {
        p: p.read_bytes()
        for directory in ("proof-records", "final-test-proof-supplies")
        for p in (run_dir / directory).glob("*.json")
    }
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    first_input_path = delivery.retain_final_test_proof_input(run_dir, draft)
    assert delivery.retain_final_test_proof_input(run_dir, draft) == first_input_path
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    if missing == "node":
        with pytest.raises(delivery.DeliveryError, match=re.escape(other)):
            delivery.verify_as_outer_dispatch(str(card))
        assert (run_dir / "verification.json").read_bytes() == verification_before
        assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
        assert {p: p.read_bytes() for p in retained} == retained
        return

    assert delivery.verify_as_outer_dispatch(str(card)) == 0
    records = delivery.require_current_stage_proofs(card, run_dir, ["final"])
    finals = [p for p in records if p["stage"] == "final"]
    assert {p["method"]["target"] for p in finals} == {"tests/test_receipt.py", other}
    assert len({p["observation_id"] for p in finals}) == 2
    supplies = delivery._final_test_proof_supplies(run_dir, inventory, records)
    assert len(supplies) == 2
    assert {p: p.read_bytes() for p in retained} == retained
    index_before = (run_dir / "proof-index.json").read_bytes()
    markers_before = {
        p: p.read_bytes()
        for p in (run_dir / "final-test-proof-supplies").glob("*.json")
    }
    assert delivery.verify_as_outer_dispatch(str(card)) == 0
    assert (run_dir / "proof-index.json").read_bytes() == index_before
    assert {p: p.read_bytes() for p in markers_before} == markers_before
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
    assert (run_dir / "verification.json").read_bytes() == verification_before

    # Explicit and old implicit drafts identify the same primary target.
    duplicate = {
        **primary_input,
        "method": {"kind": "test", "target": "tests/test_receipt.py"},
    }
    duplicate_path = run_dir / "final-test-proof-inputs" / "duplicate.json"
    delivery.write_json(duplicate_path, duplicate)
    with pytest.raises(delivery.DeliveryError, match="input is duplicate"):
        delivery._final_test_proof_inputs(card, run_dir, inventory)
    duplicate_path.unlink()
    # Losing one accepted additional-target record never permits resupply.
    additional_marker = next(
        marker for key, marker in supplies.items() if key[1] == other
    )
    (root / additional_marker["record"]["path"]).unlink()
    with pytest.raises(delivery.DeliveryError, match="safely read|missing|corrupt"):
        delivery.verify_as_outer_dispatch(str(card))
    assert (run_dir / "proof-index.json").read_bytes() == index_before
    assert {p: p.read_bytes() for p in markers_before} == markers_before
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles


def test_observed_proof_review_and_final_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir, implementation, review = _final_v2_repository(
        tmp_path, monkeypatch
    )
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.preverify(str(card)) == 0
    assert delivery.verify_as_outer_dispatch(str(card)) == 0
    assert os.environ.get("CHRL_SESSION_ROLE") is None
    verification = delivery._verified_command_set(
        run_dir / "verification.json",
        run_dir,
        card,
        delivery.payload_fingerprint(),
        delivery.verification_commands("final"),
        "final",
    )
    assert verification is not None
    records = delivery.require_current_stage_proofs(
        card, run_dir, ["implementation", "review", "final"]
    )
    final = next(record for record in records if record["stage"] == "final")
    assert final["recorder_role"] == "outer" and final["lane"] == "final"
    assert final["condition"] not in {implementation["condition"], review["condition"]}
    item, log, current = delivery.read_check_result(
        root / final["artifact"]["path"], run_dir, "final", final["command_identity"]
    )
    assert current and final["attempt_id"] == item["attempt_id"]
    for node in final["selected_nodes"]:
        assert " PASSED" in log[node["start"] : node["end"]].decode()

    cycles = sorted((run_dir / "verification").glob("cycle-*"))
    index_before_reuse = (run_dir / "proof-index.json").read_bytes()
    assert delivery.verify(str(card)) == 0
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
    assert (run_dir / "proof-index.json").read_bytes() == index_before_reuse


def test_final_test_proof_requires_its_current_configured_receipt_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A focused receipt cannot cover a final row merely by claiming final."""

    root, card, run_dir, _implementation, review = _final_v2_repository(
        tmp_path, monkeypatch
    )
    profile = delivery.profile()
    profile["verification"]["final_commands"] = ["true"]
    monkeypatch.setattr(delivery, "profile", lambda: profile)
    final_row = next(
        row
        for row in delivery.derive_proof_inventory(card)["conditions"]
        if row["stage"] == "final"
    )
    forged = json.loads(json.dumps(review))
    forged.update(
        {
            "condition": final_row["identity"],
            "method": final_row["method"],
            "stage": "final",
            "recorder_role": "outer",
            "observation_id": "manual-final-from-focused",
        }
    )
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    delivery.record_outer_observed_proof(run_dir, forged)
    assert forged["lane"] == "focused"
    assert delivery.preverify(str(card)) == 0
    card_before = card.read_bytes()
    index_before = (run_dir / "proof-index.json").read_bytes()
    records_before = {
        path: path.read_bytes() for path in (run_dir / "proof-records").glob("*.json")
    }
    with pytest.raises(
        delivery.DeliveryError, match="outside the current configured final set"
    ):
        delivery.verify_as_outer_dispatch(str(card))
    assert card.read_bytes() == card_before
    assert (run_dir / "proof-index.json").read_bytes() == index_before
    assert {path: path.read_bytes() for path in records_before} == records_before
    cycles = sorted((run_dir / "verification").glob("cycle-*"))
    with pytest.raises(
        delivery.DeliveryError, match="outside the current configured final set"
    ):
        delivery.verify_as_outer_dispatch(str(card))
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
    reached: list[bool] = []
    mutations: list[str] = []
    real_git = delivery.git
    monkeypatch.setattr(
        delivery, "_publish_continuation", lambda *_args: reached.append(True) or 0
    )

    def no_endpoint_mutation(
        *args: str, **kwargs: object
    ) -> subprocess.CompletedProcess[object]:
        if args[0] in {"add", "commit", "push"}:
            mutations.append(args[0])
            pytest.fail("publisher endpoint mutation reached")
        return real_git(*args, **kwargs)

    monkeypatch.setattr(delivery, "git", no_endpoint_mutation)
    with pytest.raises(
        delivery.DeliveryError, match="outside the current configured final set"
    ):
        delivery.publish(str(card))
    assert reached == [] and mutations == []
    assert (
        card.read_bytes() == card_before
        and (run_dir / "proof-index.json").read_bytes() == index_before
    )


def test_observed_proof_final_draft_late_reuse_preserves_accepted_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Normal reviewer drafts are inert; outer binds them once under its lock."""

    root, card, run_dir, _implementation, _review = _final_v2_repository(
        tmp_path, monkeypatch
    )
    draft = run_dir / "final-input.json"
    input_root = run_dir / "final-test-proof-inputs"
    for path in input_root.glob("*.json"):
        path.unlink()
    input_root.rmdir()
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.preverify(str(card)) == 0
    with pytest.raises(delivery.DeliveryError, match="coverage mismatch"):
        delivery.verify_as_outer_dispatch(str(card))
    cycles = sorted((run_dir / "verification").glob("cycle-*"))
    verification_before = (run_dir / "verification.json").read_bytes()
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    with pytest.raises(delivery.DeliveryError, match="implementation or review"):
        delivery.retain_final_test_proof_input(run_dir, draft)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.retain_final_test_proof_input(run_dir, draft)
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.verify_as_outer_dispatch(str(card)) == 0
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
    assert (run_dir / "verification.json").read_bytes() == verification_before
    final = next(
        item
        for item in delivery.require_current_stage_proofs(card, run_dir, ["final"])
        if item["stage"] == "final"
    )
    marker = next((run_dir / "final-test-proof-supplies").glob("*.json"))
    marker_before = marker.read_bytes()
    index_before = (run_dir / "proof-index.json").read_bytes()
    record = next(
        delivery.REPO_ROOT / item["path"]
        for item in delivery._check_json(run_dir / "proof-index.json")["records"]
        if delivery._check_json(delivery.REPO_ROOT / item["path"])["observation_id"]
        == final["observation_id"]
    )
    record_before = record.read_bytes()
    record.unlink()
    with pytest.raises(
        delivery.DeliveryError, match="missing|corrupt|integrity|safely read"
    ):
        delivery.verify_as_outer_dispatch(str(card))
    assert (run_dir / "verification.json").read_bytes() == verification_before
    assert (run_dir / "proof-index.json").read_bytes() == index_before
    assert marker.read_bytes() == marker_before
    record.write_bytes(record_before)

    unicode_log = (
        "π\ntests/test_receipt.py::test_value[ид с пробелом] PASSED\nsummary\n".encode()
    )
    nodes = pytest_nodes({"log": "unused"}, unicode_log, "tests/test_receipt.py")
    assert nodes and unicode_log[nodes[0]["start"] : nodes[0]["end"]].decode().endswith(
        "PASSED"
    )
    assert (
        pytest_nodes({"log": "unused"}, b"header\n1 passed\n", "tests/test_receipt.py")
        == []
    )

    # A forged final lane remains a retained but invalid artifact: reusing the
    # floor must fail before it can write a cycle or replace the index.
    record_path = next(
        root / reference["path"]
        for reference in delivery._check_json(run_dir / "proof-index.json")["records"]
        if delivery._check_json(root / reference["path"])["condition"]
        == final["condition"]
    )
    record_before = record_path.read_bytes()
    altered = json.loads(record_before)
    altered["lane"] = "pre_review"
    record_path.write_text(json.dumps(altered), encoding="utf-8")
    index = delivery._check_json(run_dir / "proof-index.json")
    for reference in index["records"]:
        if reference["path"] == delivery.repo_relative(record_path):
            reference.update(_reference(record_path))
    delivery.write_json(run_dir / "proof-index.json", index)
    damaged_index = (run_dir / "proof-index.json").read_bytes()
    with pytest.raises(delivery.DeliveryError, match="observed proof index"):
        delivery.verify(str(card))
    assert sorted((run_dir / "verification").glob("cycle-*")) == cycles
    assert (run_dir / "proof-index.json").read_bytes() == damaged_index
    record_path.write_bytes(record_before)

    # A successful final command with no declared final node is only a floor
    # receipt; it cannot manufacture final authority.
    _root, missing_card, missing_run, _implementation, _review = _final_v2_repository(
        tmp_path / "missing-node",
        monkeypatch,
        final_target="tests/test_receipt.py::test_failure",
    )
    assert delivery.preverify(str(missing_card)) == 0
    with pytest.raises(delivery.DeliveryError, match="coverage mismatch"):
        delivery.verify(str(missing_card))
    assert (missing_run / "verification.json").is_file()
    assert not any(
        record["stage"] == "final"
        for record in delivery._validated_index_records(
            delivery._check_json(missing_run / "proof-index.json"),
            card=missing_card,
            run_dir=missing_run,
            inventory=delivery.derive_proof_inventory(missing_card),
        )
    )


def test_observed_proof_publish_preserves_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir, _implementation, _review = _final_v2_repository(
        tmp_path, monkeypatch
    )
    assert delivery.preverify(str(card)) == 0
    assert delivery.verify(str(card)) == 0
    proof_index = run_dir / "proof-index.json"
    final_record = next(
        root / record["artifact"]["path"]
        for record in delivery.require_current_stage_proofs(card, run_dir, ["final"])
        if record["stage"] == "final"
    )
    snapshots = {
        "card": card.read_bytes(),
        "index": proof_index.read_bytes(),
        "verification": (run_dir / "verification.json").read_bytes(),
        "record": final_record.read_bytes(),
    }
    continued: list[tuple[Path, Path]] = []

    def stop_before_irreversible_publish(
        active: Path, owned_run: Path, *_args: object, **_kwargs: object
    ) -> int:
        continued.append((active, owned_run))
        return 0

    real_git = delivery.git
    mutations: list[str] = []

    def read_only_git(
        *args: str, **kwargs: object
    ) -> subprocess.CompletedProcess[object]:
        if args[0] in {"add", "commit", "push"}:
            mutations.append(args[0])
            pytest.fail(f"publisher mutation reached: {args[0]}")
        return real_git(*args, **kwargs)

    monkeypatch.setattr(delivery, "git", read_only_git)
    monkeypatch.setattr(
        delivery, "_publish_continuation", stop_before_irreversible_publish
    )
    assert delivery.publish(str(card)) == 0
    assert continued == [(card, run_dir)]
    assert mutations == []
    assert snapshots == {
        "card": card.read_bytes(),
        "index": proof_index.read_bytes(),
        "verification": (run_dir / "verification.json").read_bytes(),
        "record": final_record.read_bytes(),
    }

    # Damage the condition artifact after verification.  The real publisher
    # must refuse before the continuation, preserving the active board location
    # and every publisher-owned pointer/receipt other than this hostile input.
    final_record.write_bytes(final_record.read_bytes() + b" ")
    damaged = {
        "card": card.read_bytes(),
        "index": proof_index.read_bytes(),
        "verification": (run_dir / "verification.json").read_bytes(),
    }
    with pytest.raises(delivery.DeliveryError, match="proof artifact integrity failed"):
        delivery.publish(str(card))
    assert continued == [(card, run_dir)]
    assert mutations == []
    assert damaged == {
        "card": card.read_bytes(),
        "index": proof_index.read_bytes(),
        "verification": (run_dir / "verification.json").read_bytes(),
    }


def test_observed_proof_typed_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    inspection = _inspection_proof(root, card, run_dir)
    delivery.record_observed_proof(run_dir, inspection)
    before = (run_dir / "proof-index.json").read_bytes()
    unrelated = json.loads(json.dumps(inspection))
    unrelated["artifact"] = _reference(run_dir / "observed-bytes.txt")
    with pytest.raises(delivery.DeliveryError, match="typed proof artifact"):
        delivery.record_observed_proof(run_dir, unrelated)
    assert (run_dir / "proof-index.json").read_bytes() == before
    inspection_artifact = root / inspection["artifact"]["path"]
    original_inspection = inspection_artifact.read_bytes()
    wrong_source = json.loads(original_inspection)
    wrong_source["inspected_sources"] = [_reference(root / "unrelated.txt")]
    inspection_artifact.write_text(json.dumps(wrong_source), encoding="utf-8")
    bad_source = json.loads(json.dumps(inspection))
    bad_source["artifact"] = _reference(inspection_artifact)
    with pytest.raises(delivery.DeliveryError, match="declared source"):
        delivery._validate_observed_proof(
            bad_source,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="implementation",
        )
    inspection_artifact.write_bytes(original_inspection)

    proof = _actual_pytest_proof(root, card, run_dir)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.record_observed_proof(run_dir, proof)
    for mutate in (
        lambda value: value["selected_nodes"].__setitem__(
            0, {"node": "tests/test_receipt.py::test_value[one]x", "start": 0, "end": 1}
        ),
        lambda value: value.__setitem__("lane", "final"),
        lambda value: value.__setitem__(
            "command_identity", {"kind": "argv", "argv": ["echo", "pytest"]}
        ),
    ):
        bad = json.loads(json.dumps(proof))
        mutate(bad)
        with pytest.raises((delivery.DeliveryError, ValueError)):
            delivery._validate_observed_proof(
                bad,
                card=card,
                run_dir=run_dir,
                inventory=delivery.derive_proof_inventory(card),
                role="review",
            )

    runtime = _runtime_proof(root, card, run_dir)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    delivery.record_outer_observed_proof(run_dir, runtime)
    accepted_index = (run_dir / "proof-index.json").read_bytes()
    bad_runtime = json.loads(json.dumps(runtime))
    bad_runtime["runtime"]["preflight"]["sha256"] = "0" * 64
    runtime_artifact = root / bad_runtime["artifact"]["path"]
    original_runtime = runtime_artifact.read_bytes()
    runtime_observed = json.loads(runtime_artifact.read_text(encoding="utf-8"))
    runtime_observed["runtime"] = bad_runtime["runtime"]
    runtime_artifact.write_text(json.dumps(runtime_observed), encoding="utf-8")
    bad_runtime["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError, match="integrity"):
        delivery._validate_observed_proof(
            bad_runtime,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)
    bad_target = json.loads(json.dumps(runtime))
    bad_target["runtime"]["target"]["identity"] = "foreign-target"
    runtime_observed = json.loads(runtime_artifact.read_text(encoding="utf-8"))
    runtime_observed["runtime"] = bad_target["runtime"]
    runtime_artifact.write_text(json.dumps(runtime_observed), encoding="utf-8")
    bad_target["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError, match="declared target"):
        delivery._validate_observed_proof(
            bad_target,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)

    # Runtime labels are not authority.  Each referenced record has to carry
    # the exact target/session scope and successful outcome established by this
    # fixture-only observation; refusals never alter the accepted proof index.
    def reject_runtime_record(name: str, mutate: object) -> None:
        record = run_dir / f"{name}.json"
        original = record.read_bytes()
        changed = json.loads(original)
        assert callable(mutate)
        mutate(changed)
        record.write_text(json.dumps(changed), encoding="utf-8")
        candidate = json.loads(json.dumps(runtime))
        if name in {"authorization", "preflight"}:
            candidate["runtime"][name] = _reference(record)
        else:
            candidate["runtime"]["recovery"]["reference"] = _reference(record)
        observed = json.loads(original_runtime)
        observed["runtime"] = candidate["runtime"]
        runtime_artifact.write_text(json.dumps(observed), encoding="utf-8")
        candidate["artifact"] = _reference(runtime_artifact)
        with pytest.raises(delivery.DeliveryError):
            delivery._validate_observed_proof(
                candidate,
                card=card,
                run_dir=run_dir,
                inventory=delivery.derive_proof_inventory(card),
                role="outer",
            )
        assert (run_dir / "proof-index.json").read_bytes() == accepted_index
        record.write_bytes(original)
        runtime_artifact.write_bytes(original_runtime)

    reject_runtime_record(
        "authorization",
        lambda value: value["scope"]["target"].__setitem__("identity", "other-target"),
    )
    reject_runtime_record(
        "authorization",
        lambda value: value["scope"]["session"].__setitem__(
            "identity", "other-session"
        ),
    )
    reject_runtime_record(
        "preflight", lambda value: value.__setitem__("outcome", "failed")
    )
    reject_runtime_record(
        "authorization", lambda value: value.__setitem__("fixture_only", False)
    )
    reject_runtime_record(
        "not_applicable", lambda value: value["resolution"].__setitem__("reason", "")
    )
    missing_authorization = json.loads(json.dumps(runtime))
    missing_authorization["runtime"].pop("authorization")
    observed = json.loads(original_runtime)
    observed["runtime"] = missing_authorization["runtime"]
    runtime_artifact.write_text(json.dumps(observed), encoding="utf-8")
    missing_authorization["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError):
        delivery._validate_observed_proof(
            missing_authorization,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)
    foreign_authorization = json.loads(json.dumps(runtime))
    foreign_authorization["runtime"]["authorization"] = foreign_authorization[
        "runtime"
    ]["preflight"]
    observed = json.loads(original_runtime)
    observed["runtime"] = foreign_authorization["runtime"]
    runtime_artifact.write_text(json.dumps(observed), encoding="utf-8")
    foreign_authorization["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError):
        delivery._validate_observed_proof(
            foreign_authorization,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)
    foreign_recovery = json.loads(json.dumps(runtime))
    foreign_recovery["runtime"]["recovery"]["reference"] = foreign_recovery["runtime"][
        "authorization"
    ]
    observed = json.loads(original_runtime)
    observed["runtime"] = foreign_recovery["runtime"]
    runtime_artifact.write_text(json.dumps(observed), encoding="utf-8")
    foreign_recovery["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError):
        delivery._validate_observed_proof(
            foreign_recovery,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)
    missing_recovery = json.loads(json.dumps(runtime))
    missing_recovery["runtime"].pop("recovery")
    observed = json.loads(original_runtime)
    observed["runtime"] = missing_recovery["runtime"]
    runtime_artifact.write_text(json.dumps(observed), encoding="utf-8")
    missing_recovery["artifact"] = _reference(runtime_artifact)
    with pytest.raises(delivery.DeliveryError):
        delivery._validate_observed_proof(
            missing_recovery,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="outer",
        )
    runtime_artifact.write_bytes(original_runtime)
    assert (run_dir / "proof-index.json").read_bytes() == accepted_index
    assert {
        item["condition"]
        for item in delivery.require_current_stage_proofs(
            card, run_dir, ["implementation", "review", "final"]
        )
    } == {inspection["condition"], proof["condition"], runtime["condition"]}


def test_observed_proof_inventory_consistency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    implementation = _inspection_proof(root, card, run_dir)
    delivery.record_observed_proof(run_dir, implementation)
    review = _actual_pytest_proof(root, card, run_dir)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.record_observed_proof(run_dir, review)
    inventory = delivery.derive_proof_inventory(card)
    template = delivery.verdict_template(str(card))["template"]
    assert len(template["decisions"]) == 1
    decision = template["decisions"][0]
    assert set(decision["conditions"]) == {
        row["identity"] for row in inventory["conditions"]
    }
    refs = {item["condition"]: item for item in decision["condition_refs"]}
    refs[implementation["condition"]]["observation_ids"] = [
        implementation["observation_id"]
    ]
    refs[review["condition"]]["observation_ids"] = [review["observation_id"]]
    decision["observation_ids"] = [
        implementation["observation_id"],
        review["observation_id"],
    ]
    decision["assessment"] = (
        "The retained inspection and selected pytest node bind the current implementation and review clauses; final remains pending."
    )
    verdict = delivery.verdict_path(delivery.card_id(card))
    delivery.write_json(verdict, template)
    assert delivery.validate_verdict(str(card))["result"] == "go"
    index_before_duplicate = (run_dir / "proof-index.json").read_bytes()
    decision["observation_ids"].append(implementation["observation_id"])
    delivery.write_json(verdict, template)
    with pytest.raises(delivery.DeliveryError, match="unique|duplicate"):
        delivery.validate_verdict(str(card))
    assert (run_dir / "proof-index.json").read_bytes() == index_before_duplicate
    decision["observation_ids"] = [
        implementation["observation_id"],
        review["observation_id"],
    ]
    refs[implementation["condition"]]["observation_ids"] = [review["observation_id"]]
    delivery.write_json(verdict, template)
    with pytest.raises(delivery.DeliveryError, match="foreign or stale"):
        delivery.validate_verdict(str(card))
    refs[implementation["condition"]]["observation_ids"] = [
        implementation["observation_id"]
    ]
    refs[review["condition"]]["observation_ids"] = []
    decision["observation_ids"] = [implementation["observation_id"]]
    delivery.write_json(verdict, template)
    with pytest.raises(delivery.DeliveryError, match="passing v2 condition lacks"):
        delivery.validate_verdict(str(card))
    refs[review["condition"]]["observation_ids"] = ["stale-observation"]
    decision["observation_ids"] = [
        implementation["observation_id"],
        "stale-observation",
    ]
    delivery.write_json(verdict, template)
    with pytest.raises(delivery.DeliveryError, match="foreign or stale"):
        delivery.validate_verdict(str(card))


@pytest.mark.parametrize(
    "command",
    [
        "printf 'tests/test_receipt.py::test_value[one] PASSED\\n' pytest",
        "echo 'tests/test_receipt.py::test_value[one] PASSED' pytest",
        f"{sys.executable} -c \"print('tests/test_receipt.py::test_value[one] PASSED')\" pytest",
    ],
)
def test_observed_proof_final_receipt_requires_supported_pytest_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command: str,
) -> None:
    """Real final receipts cannot turn printed pytest-looking text into proof."""

    _root, card, run_dir, _implementation, _review = _final_v2_repository(
        tmp_path, monkeypatch
    )
    configured = delivery.profile()
    configured["verification"]["final_commands"] = [command]
    monkeypatch.setattr(delivery, "profile", lambda: configured)
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.preverify(str(card)) == 0
    with pytest.raises(
        delivery.DeliveryError, match="pytest|selected-node|coverage mismatch"
    ):
        delivery.verify_as_outer_dispatch(str(card))
    assert not (run_dir / "proof-index.json").read_bytes().count(b'"stage": "final"')


def test_observed_proof_fixture_source_set_is_hash_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    extra = root / "fixture-extra.md"
    extra.write_text(_proof_card(), encoding="utf-8")
    fixture_schema = (
        root / "tools" / "changerail" / "schemas" / "review-verdict-v2.schema.json"
    )
    fixture_schema.parent.mkdir(parents=True)
    fixture_schema.write_bytes(delivery.VERDICT_V2_SCHEMA_PATH.read_bytes())
    subprocess.run(
        ["git", "add", "fixture-extra.md", delivery.repo_relative(fixture_schema)],
        cwd=root,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "extra fixture"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    extra_data = extra.read_bytes()
    delivery.FIXTURE_PROOF_SOURCE_SETS[run_dir.name] = {
        "run": {"run_id": run_dir.name, "card": delivery.repo_relative(card)},
        "payload": delivery.payload_fingerprint(),
        "caller": "fixture-caller",
        "sources": [
            {
                "path": delivery.repo_relative(extra),
                "sha256": hashlib.sha256(extra_data).hexdigest(),
            }
        ],
    }
    try:
        inventory = delivery._current_proof_inventory(card, run_dir)
        assert inventory is not None and len(inventory["conditions"]) == 6
        # C1 and the human scenario title collide, but each independently
        # admitted source retains a namespaced decision and condition identity.
        template = delivery.verdict_template(str(card))["template"]
        assert len(template["decisions"]) == 2
        assert {row["identity"] for row in inventory["conditions"]} == {
            item["condition"]
            for decision in template["decisions"]
            for item in decision["condition_refs"]
        }
        history = run_dir / "reviews"
        history.mkdir()
        monkeypatch.setattr(delivery, "VERDICT_V2_SCHEMA_PATH", fixture_schema)
        monkeypatch.setattr(
            delivery, "_write_review_payload_diffs", lambda **_kwargs: []
        )
        manifest = {
            "paths": [delivery.repo_relative(card)],
            "fingerprint": delivery.payload_fingerprint(),
            "path_fingerprints": delivery.path_fingerprints(
                [delivery.repo_relative(card)]
            ),
        }
        context = delivery._check_json(
            delivery.build_review_context(
                card=card, run_dir=run_dir, cycle=1, manifest=manifest
            )
        )
        assert context["proof_inventory"] == inventory
        # An honest NO-GO may identify missing proof without inventing a pass.
        template["result"] = "no-go"
        for decision in template["decisions"]:
            decision["assessment"] = (
                "The reviewer has not accepted the missing current observation for this source-scoped scenario."
            )
            decision["disposition"] = "fail"
            for ref in decision["condition_refs"]:
                if ref["stage"] != "final":
                    ref["disposition"] = "fail"
            decision["observation_ids"] = []
        delivery.write_json(delivery.verdict_path(delivery.card_id(card)), template)
        assert delivery.validate_verdict(str(card))["result"] == "no-go"

        # v2 consumers share only the admitted source-set inventory.  A raw
        # bootstrap mapping cannot smuggle another source into the context;
        # template and validator remain bound to the legitimate capability set.
        run_metadata = run_dir / "run.json"
        original_run = run_metadata.read_bytes()
        injected = json.loads(original_run)
        injected["bootstrap_plan"] = {"path": "source.txt"}
        delivery.write_json(run_metadata, injected)
        with pytest.raises(delivery.DeliveryError, match="unadmitted bootstrap"):
            delivery.build_review_context(
                card=card, run_dir=run_dir, cycle=2, manifest=manifest
            )
        assert not (history / "cycle-02-context.json").exists()
        injected_template = delivery.verdict_template(str(card))["template"]
        assert {
            item["condition"]
            for decision in injected_template["decisions"]
            for item in decision["condition_refs"]
        } == {row["identity"] for row in inventory["conditions"]}
        assert delivery.validate_verdict(str(card))["result"] == "no-go"
        run_metadata.write_bytes(original_run)

        # Delta review retains the same inventory while selecting only changed
        # payload paths, rather than adopting a different source set.
        delivery.write_json(
            history / "cycle-01.json",
            {"workspace": delivery.payload_fingerprint(), "result": "no-go"},
        )
        previous = {
            **manifest,
            "path_fingerprints": {delivery.repo_relative(card): "old"},
        }
        delivery.write_json(history / "cycle-01-manifest.json", previous)
        delta = delivery._check_json(
            delivery.build_review_context(
                card=card,
                run_dir=run_dir,
                cycle=2,
                manifest=manifest,
                review_reason="delta",
            )
        )
        assert delta["proof_inventory"] == inventory
        assert delta["selected_paths"] == [delivery.repo_relative(card)]
        extra.write_text(extra.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with pytest.raises(delivery.DeliveryError, match="stale"):
            delivery._current_proof_inventory(card, run_dir)
        with pytest.raises(delivery.DeliveryError, match="stale"):
            delivery.verdict_template(str(card))
        with pytest.raises(delivery.DeliveryError, match="stale"):
            delivery.validate_verdict(str(card))
    finally:
        delivery.FIXTURE_PROOF_SOURCE_SETS.pop(run_dir.name, None)


def test_observed_proof_inventory_uses_once_validated_capability_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A capability source cannot be swapped between admission and derivation."""

    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    extra = root / "fixture-extra.md"
    original = _proof_card().encode("utf-8")
    extra.write_bytes(original)
    subprocess.run(["git", "add", "fixture-extra.md"], cwd=root, check=True)
    subprocess.run(
        ["git", "commit", "-m", "extra fixture"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    delivery.FIXTURE_PROOF_SOURCE_SETS[run_dir.name] = {
        "run": {"run_id": run_dir.name, "card": delivery.repo_relative(card)},
        "payload": delivery.payload_fingerprint(),
        "caller": "fixture-caller",
        "sources": [
            {
                "path": delivery.repo_relative(extra),
                "sha256": hashlib.sha256(original).hexdigest(),
            }
        ],
    }
    real_check_bytes = delivery._check_bytes
    reads = 0

    def checked(path: Path, limit: int = 32 * 1024 * 1024) -> bytes:
        nonlocal reads
        data = real_check_bytes(path, limit)
        if Path(path) == extra:
            reads += 1
            if reads == 1:
                # This write happens only after the no-follow reader supplied
                # the bytes.  A reopening derivation would now use a different
                # source (and a different source hash).
                extra.write_bytes(original + b"\n")
        return data

    monkeypatch.setattr(delivery, "_check_bytes", checked)
    try:
        template = delivery.verdict_template(str(card))["template"]
        assert reads == 1
        assert any(
            hashlib.sha256(original).hexdigest() in ref["condition"]
            for decision in template["decisions"]
            for ref in decision["condition_refs"]
        )
        # A new consumer decision has no cache: it reads the current changed
        # bytes and refuses the capability's original hash.
        delivery.FIXTURE_PROOF_SOURCE_SETS[run_dir.name]["payload"] = (
            delivery.payload_fingerprint()
        )
        with pytest.raises(delivery.DeliveryError, match="stale"):
            delivery._current_proof_inventory(card, run_dir)
        assert reads == 2
    finally:
        delivery.FIXTURE_PROOF_SOURCE_SETS.pop(run_dir.name, None)


def test_observed_proof_assertion_support_uses_once_validated_source_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _actual_pytest_proof(root, card, run_dir)
    support = proof["assertion_support"]
    assert isinstance(support, dict)
    source = root / "tests" / "test_receipt.py"
    original = source.read_bytes()
    real_check_bytes = delivery._check_bytes
    reads = 0

    def checked(path: Path, limit: int = 32 * 1024 * 1024) -> bytes:
        nonlocal reads
        data = real_check_bytes(path, limit)
        if Path(path) == source:
            reads += 1
            if reads == 1:
                source.write_bytes(b"# swapped after validated read\n")
        return data

    monkeypatch.setattr(delivery, "_check_bytes", checked)
    delivery._validate_test_assertion_support(
        support, "tests/test_receipt.py::test_value"
    )
    assert reads == 1
    # The next independent decision reads again and discovers that the source
    # reference no longer describes its bytes; no cross-decision cache exists.
    with pytest.raises(delivery.DeliveryError, match="integrity failed"):
        delivery._validate_test_assertion_support(
            support, "tests/test_receipt.py::test_value"
        )
    assert reads == 2
    source.write_bytes(original)
    malformed = json.loads(json.dumps(support))
    malformed["fragments"]["before"]["unclosed"] = True
    with pytest.raises(delivery.DeliveryError, match="not from its declared source"):
        delivery._validate_test_assertion_support(
            malformed, "tests/test_receipt.py::test_value"
        )


def test_observed_proof_acceptance_scenarios_are_closed_and_flat_is_explicit() -> None:
    flat = "## Acceptance\n\n- [C1] WHEN a flat clause is declared\n\n## Verify\n"
    assert delivery._acceptance_scenarios_text(flat) == {"C1": "Condition: C1"}
    structured = """## Acceptance

### Requirement: one
#### Scenario: same title
- [C1] WHEN one clause is bound
### Requirement: two
#### Scenario: same title
- [C2] WHEN another clause is bound

## Verify
"""
    parsed = delivery._acceptance_scenarios_text(structured)
    assert parsed["C1"] != parsed["C2"]
    for malformed in (
        structured.replace("#### Scenario: same title\n- [C2]", "- [C2]"),
        structured.replace("### Requirement: two", "### Requirement: one"),
        structured.replace(
            "### Requirement: two\n#### Scenario: same title",
            "#### Scenario: same title",
        ),
        flat.replace("\n\n## Verify", "\n#### Scenario: mixed\n\n## Verify"),
    ):
        with pytest.raises(delivery.DeliveryError):
            delivery._acceptance_scenarios_text(malformed)


def test_observed_proof_flat_inventory_reaches_context_template_and_validator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    card.write_text(
        _proof_card().replace(
            "### Requirement: observed proof\n\n#### Scenario: each typed observation is bound\n\n",
            "",
        ),
        encoding="utf-8",
    )
    fixture_schema = (
        root / "tools" / "changerail" / "schemas" / "review-verdict-v2.schema.json"
    )
    fixture_schema.parent.mkdir(parents=True)
    fixture_schema.write_bytes(delivery.VERDICT_V2_SCHEMA_PATH.read_bytes())
    monkeypatch.setattr(delivery, "VERDICT_V2_SCHEMA_PATH", fixture_schema)
    history = run_dir / "reviews"
    history.mkdir()
    monkeypatch.setattr(delivery, "_write_review_payload_diffs", lambda **_kwargs: [])
    inventory = delivery._current_proof_inventory(card, run_dir)
    assert inventory is not None and {
        row["scenario"].split(" / ")[-1] for row in inventory["conditions"]
    } == {"Condition: C1", "Condition: C2", "Condition: C3"}
    manifest = {
        "paths": delivery.changed_paths(),
        "fingerprint": delivery.payload_fingerprint(),
        "path_fingerprints": delivery.path_fingerprints(delivery.changed_paths()),
    }
    context = delivery._check_json(
        delivery.build_review_context(
            card=card, run_dir=run_dir, cycle=1, manifest=manifest
        )
    )
    template = delivery.verdict_template(str(card))["template"]
    assert context["proof_inventory"] == inventory and len(template["decisions"]) == 3
    template["result"] = "no-go"
    for decision in template["decisions"]:
        decision["assessment"] = (
            "This flat condition has no current observation and remains unaccepted."
        )
        if any(ref["stage"] != "final" for ref in decision["condition_refs"]):
            decision["disposition"] = "fail"
            for ref in decision["condition_refs"]:
                if ref["stage"] != "final":
                    ref["disposition"] = "fail"
    delivery.write_json(delivery.verdict_path(delivery.card_id(card)), template)
    assert delivery.validate_verdict(str(card))["result"] == "no-go"


def test_observed_proof_v2_verdict_pin_and_no_go_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    template = delivery.verdict_template(str(card))["template"]
    verdict = delivery.verdict_path(delivery.card_id(card))
    # Schema dispatch is selected from the run before an attacker-controlled
    # verdict schema gets to choose the legacy validation branch.
    for schema in ("changerail.review-verdict.v1", None, False, "unknown"):
        delivery.write_json(verdict, {"schema": schema})
        with pytest.raises(delivery.DeliveryError, match="requires a v2"):
            delivery.validate_verdict(str(card))

    template["result"] = "no-go"
    decision = template["decisions"][0]
    decision["assessment"] = (
        "The implementation observation is absent, so this scenario cannot be accepted."
    )
    decision["disposition"] = "fail"
    for ref in decision["condition_refs"]:
        if ref["stage"] != "final":
            ref["disposition"] = "fail"
    delivery.write_json(verdict, template)
    assert delivery.validate_verdict(str(card))["result"] == "no-go"
    for mutate in (
        lambda value: value["decisions"][0].__setitem__(
            "condition_refs", value["decisions"][0]["condition_refs"][:-1]
        ),
        lambda value: value["decisions"][0]["condition_refs"][0].__setitem__(
            "stage", "final"
        ),
        lambda value: value["decisions"][0]["condition_refs"].append(
            dict(value["decisions"][0]["condition_refs"][0])
        ),
        lambda value: value["decisions"][0]["condition_refs"][0].__setitem__(
            "condition", "foreign"
        ),
        lambda value: value["decisions"][0].__setitem__("assessment", "unassessed"),
    ):
        candidate = json.loads(json.dumps(template))
        mutate(candidate)
        delivery.write_json(verdict, candidate)
        with pytest.raises(delivery.DeliveryError):
            delivery.validate_verdict(str(card))


def test_observed_proof_rollout_preserves_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    profile_path = root / ".changerail" / "profile.toml"
    profile_path.parent.mkdir()
    profile_path.write_text("# fixture profile\n", encoding="utf-8")
    monkeypatch.setattr(delivery, "PROFILE_PATH", profile_path)
    todo = root / "openspec" / "board" / "2.todo" / card.name
    todo.parent.mkdir(parents=True)
    card.replace(todo)
    todo.write_text(
        todo.read_text()
        + "\n## Status\n2.todo\n\n## Result\nplanned\n\n## Log\nfixture\n"
    )
    bin_dir = root / "bin"
    bin_dir.mkdir()
    board_do = bin_dir / "board-do"
    board_do.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib, sys\n"
        "source = pathlib.Path.cwd() / sys.argv[1]\n"
        "destination = source.parents[1] / '3.inprogress' / source.name\n"
        "destination.parent.mkdir(parents=True, exist_ok=True)\n"
        "source.replace(destination)\n",
        encoding="utf-8",
    )
    board_do.chmod(0o755)
    writes: list[str] = []
    original_write_json = delivery.write_json

    def traced_write_json(path: Path, payload: object) -> None:
        writes.append(path.name)
        if path.name == "run.json":
            assert (path.parent / "observed-proof-selection.json").is_file()
        original_write_json(path, payload)

    launched: list[Path] = []

    def stop_at_model(**kwargs: object) -> int:
        model_run = kwargs["run_dir"]
        assert isinstance(model_run, Path)
        launched.append(model_run)
        assert (model_run / "observed-proof-selection.json").is_file()
        assert (model_run / "run.json").is_file()
        raise delivery.DeliveryError("fixture stops at model launch")

    monkeypatch.setattr(delivery, "write_json", traced_write_json)
    monkeypatch.setattr(delivery, "doctor", lambda *args, **kwargs: {"ok": True})
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "models": {
                "implementation": {"model": "fixture", "reasoning_effort": "low"}
            },
            "max_wall_minutes": 1,
            "budgets": {
                "enforce_limits": False,
                "first_edit_discovery_commands": 1,
                "review_commands": 1,
            },
        },
    )
    monkeypatch.setattr(delivery, "launch_codex", stop_at_model)

    assert delivery.run_delivery(str(todo)) == 2
    assert launched and writes.count("observed-proof-selection.json") == 1
    assert writes.index("observed-proof-selection.json") < writes.index("run.json")
    created = launched[0]
    moved = root / "openspec" / "board" / "3.inprogress" / todo.name
    selection_path = created / "observed-proof-selection.json"
    selection_before = selection_path.read_bytes()
    run_path = created / "run.json"
    run_before = run_path.read_bytes()
    manifest = delivery._check_json(created / "manifest.json")
    contract = delivery._run_observed_contract(created)
    assert moved.is_file()
    assert delivery._check_json(selection_path)["owner"][
        "card"
    ] == delivery.repo_relative(todo)
    assert (
        contract is not None
        and manifest["observed_proof_selection"] == contract["selection"]
    )

    cases = {
        "missing": lambda value: value.pop("owner"),
        "unknown": lambda value: value.__setitem__("unknown", True),
        "false": lambda value: value.__setitem__("required_stages", False),
        "renamed": lambda value: value["owner"].__setitem__(
            "card", delivery.repo_relative(moved.with_name("renamed.md"))
        ),
    }
    for label, mutate in cases.items():
        selection = json.loads(selection_before)
        mutate(selection)
        original_write_json(selection_path, selection)
        run = json.loads(run_before)
        run["observed_proof_contract"]["selection"]["sha256"] = hashlib.sha256(
            selection_path.read_bytes()
        ).hexdigest()
        original_write_json(run_path, run)
        attempted = {
            path: path.read_bytes()
            for path in (moved, selection_path, run_path, created / "manifest.json")
        }
        with pytest.raises(delivery.DeliveryError):
            delivery._run_observed_contract(created)
        assert {path: path.read_bytes() for path in attempted} == attempted, label

    original_write_json(selection_path, json.loads(selection_before))
    missing_reference = json.loads(run_before)
    del missing_reference["observed_proof_contract"]["selection"]
    original_write_json(run_path, missing_reference)
    before_missing = {
        path: path.read_bytes()
        for path in (moved, selection_path, run_path, created / "manifest.json")
    }
    with pytest.raises(delivery.DeliveryError, match="malformed"):
        delivery._run_observed_contract(created)
    assert {path: path.read_bytes() for path in before_missing} == before_missing

    downgraded = json.loads(run_before)
    downgraded["schema"] = "changerail.delivery-run.v1"
    original_write_json(run_path, downgraded)
    before_downgrade = {
        path: path.read_bytes()
        for path in (moved, selection_path, run_path, created / "manifest.json")
    }
    with pytest.raises(delivery.DeliveryError, match="downgraded"):
        delivery._run_observed_contract(created)
    assert {path: path.read_bytes() for path in before_downgrade} == before_downgrade

    # A new-run record cannot shed its schema, selection, and creation record
    # to become a legacy consumer.  These are production selectors; only the
    # unrelated preverification command is intercepted before real handoff
    # reaches its observed-contract gate.
    review_verdict = delivery.verdict_path(delivery.card_id(moved))
    review_verdict.parent.mkdir(parents=True, exist_ok=True)
    original_write_json(review_verdict, {"schema": "changerail.review-verdict.v1"})
    for label, mutate in {
        "missing-version-and-contract": lambda value: (
            value.pop("schema"),
            value.pop("observed_proof_contract"),
        ),
        "renamed-v1-without-pin": lambda value: (
            value.__setitem__("schema", "changerail.delivery-run.v1"),
            value.pop("observed_proof_contract"),
        ),
        "false-schema": lambda value: value.__setitem__("schema", False),
        "unknown-schema": lambda value: value.__setitem__(
            "schema", "changerail.delivery-run.v9"
        ),
    }.items():
        original_write_json(selection_path, json.loads(selection_before))
        run = json.loads(run_before)
        mutate(run)
        original_write_json(run_path, run)
        selection_path.unlink()
        attempted = {
            path: path.read_bytes()
            for path in (moved, run_path, created / "manifest.json")
        }
        with pytest.raises(delivery.DeliveryError):
            delivery._current_proof_inventory(moved, created)
        with pytest.raises(delivery.DeliveryError):
            delivery.verdict_template(str(moved))
        with pytest.raises(delivery.DeliveryError):
            delivery.validate_verdict(str(moved))
        with monkeypatch.context() as handoff:
            handoff.setattr(delivery, "preverify", lambda _value: 0)
            with pytest.raises(delivery.DeliveryError):
                delivery.implementation_handoff(str(moved))
        assert {path: path.read_bytes() for path in attempted} == attempted, label
    original_write_json(selection_path, json.loads(selection_before))

    foreign = created.parent / "foreign-selection.json"
    foreign.write_bytes(selection_before)
    run = json.loads(run_before)
    run["observed_proof_contract"]["selection"]["path"] = delivery.repo_relative(
        foreign
    )
    original_write_json(run_path, run)
    before_foreign = {
        path: path.read_bytes()
        for path in (
            moved,
            selection_path,
            run_path,
            created / "manifest.json",
            foreign,
        )
    }
    with pytest.raises(delivery.DeliveryError, match="foreign"):
        delivery._run_observed_contract(created)
    assert {path: path.read_bytes() for path in before_foreign} == before_foreign


def test_observed_proof_handoff_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    # The implementation consumer needs the card in its dirty payload; retain
    # real typed observations/index records while isolating only the unrelated
    # full-project preverification command set.
    card.write_text(
        card.read_text(encoding="utf-8")
        + "\n## Result\n\nfixture result\n\n## Log\n\nfixture log\n",
        encoding="utf-8",
    )
    manifest_file = delivery.manifest_path(delivery.card_id(card))
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    delivery.write_json(
        manifest_file,
        {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run_dir.name,
            "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
        },
    )
    monkeypatch.setattr(delivery, "preverify", lambda _value: 0)
    monkeypatch.setattr(
        delivery,
        "require_current_successful_preverification",
        lambda *_args, **_kwargs: {},
    )

    # Missing and failed observations cannot enter a real handoff.
    with pytest.raises(delivery.DeliveryError, match="missing"):
        delivery.implementation_handoff(str(card))
    failed = _inspection_proof(root, card, run_dir)
    failed["outcome"] = "fail"
    with pytest.raises(delivery.DeliveryError, match="outcome"):
        delivery.record_observed_proof(run_dir, failed)

    implementation = _inspection_proof(root, card, run_dir)
    delivery.record_observed_proof(run_dir, implementation)
    # Record a real review receipt too: handoff must not demand it, but the
    # current proof index still validates every retained artifact.
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.record_observed_proof(run_dir, _actual_pytest_proof(root, card, run_dir))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    assert delivery.implementation_handoff(str(card)) == 0
    handoff = delivery.require_current_implementation_handoff(card, run_dir)
    handoff_bytes = delivery.handoff_path(run_dir).read_bytes()
    history = next((run_dir / "implementation-handoffs").glob("handoff-*.json"))
    history_bytes = history.read_bytes()
    assert handoff["observed_proof"]["stages"] == ["implementation"]
    assert delivery.implementation_handoff(str(card)) == 0
    assert len(list((run_dir / "implementation-handoffs").glob("handoff-*.json"))) == 1

    # Duplicate and foreign records are rejected by the actual handoff reader,
    # without rewriting the current or historical handoff.
    duplicate = json.loads(json.dumps(implementation))
    duplicate["observation_id"] = "implementation-c1-duplicate"
    delivery.record_observed_proof(run_dir, duplicate)
    with pytest.raises(delivery.DeliveryError, match="duplicates"):
        delivery.require_current_implementation_handoff(card, run_dir)
    assert (
        delivery.handoff_path(run_dir).read_bytes() == handoff_bytes
        and history.read_bytes() == history_bytes
    )
    # Restore one known-good index generation and inject a corrupt retained
    # record reference; this exercises the no-follow index reader, not a stub.
    index = delivery._check_json(run_dir / "proof-index.json")
    index["records"] = index["records"][:-1]
    foreign_record = run_dir / "proof-records" / "foreign.json"
    foreign_payload = json.loads(
        next((run_dir / "proof-records").glob("*.json")).read_text(encoding="utf-8")
    )
    foreign_payload["condition"] = "foreign-condition"
    foreign_record.write_text(json.dumps(foreign_payload), encoding="utf-8")
    index["records"].append(_reference(foreign_record))
    delivery.write_json(run_dir / "proof-index.json", index)
    with pytest.raises(delivery.DeliveryError, match="foreign"):
        delivery.require_current_implementation_handoff(card, run_dir)
    assert (
        delivery.handoff_path(run_dir).read_bytes() == handoff_bytes
        and history.read_bytes() == history_bytes
    )

    # A card Result/Log edit and an unrelated payload refresh each invalidate
    # the frozen handoff; historical bytes remain exact evidence of its source.
    clean_index = delivery._check_json(run_dir / "proof-index.json")
    clean_index["records"] = clean_index["records"][:-1]
    delivery.write_json(run_dir / "proof-index.json", clean_index)
    original_card = card.read_bytes()
    for changed in (
        original_card.replace(b"fixture result", b"refreshed result"),
        original_card.replace(b"fixture log", b"refreshed log"),
    ):
        card.write_bytes(changed)
        with pytest.raises(delivery.DeliveryError, match="fingerprint"):
            delivery.require_current_implementation_handoff(card, run_dir)
        assert (
            delivery.handoff_path(run_dir).read_bytes() == handoff_bytes
            and history.read_bytes() == history_bytes
        )
        card.write_bytes(original_card)
    (root / "source.txt").write_text("refreshed non-card payload\n", encoding="utf-8")
    with pytest.raises(delivery.DeliveryError, match="fingerprint"):
        delivery.require_current_implementation_handoff(card, run_dir)
    assert (
        delivery.handoff_path(run_dir).read_bytes() == handoff_bytes
        and history.read_bytes() == history_bytes
    )

    # A future-only card has no implementation-stage conditions: no missing
    # index becomes a prerequisite, while the same reader stays strict above.
    future_root, future_card, future_run = _proof_repository(
        tmp_path / "future", monkeypatch
    )
    future_card.write_text(
        _proof_card()
        .replace('"stage": "implementation"', '"stage": "final"')
        .replace('"stage": "review"', '"stage": "final"')
        + "\n## Result\n\nfuture result\n\n## Log\n\nfuture log\n",
        encoding="utf-8",
    )
    future_manifest = delivery.manifest_path(delivery.card_id(future_card))
    future_manifest.parent.mkdir(parents=True, exist_ok=True)
    delivery.write_json(
        future_manifest,
        {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": future_run.name,
            "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
        },
    )
    assert not (future_run / "proof-index.json").exists()
    assert delivery.implementation_handoff(str(future_card)) == 0
    assert delivery.require_current_implementation_handoff(future_card, future_run)[
        "observed_proof"
    ]["stages"] == ["implementation"]


def test_observed_proof_safe_retention_refuses_unrelated_and_unsafe_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _inspection_proof(root, card, run_dir)
    before = set(run_dir.iterdir())
    outside = tmp_path / "outside-sentinel"
    outside.write_text("do not open", encoding="utf-8")
    linked = run_dir / "linked"
    linked.symlink_to(tmp_path, target_is_directory=True)
    outside_data = outside.read_bytes()
    bad = json.loads(json.dumps(proof))
    bad["artifact"] = {
        "path": _path(
            ".runtime", "changerail", "runs", run_dir.name, "linked", outside.name
        ),
        "size": len(outside_data),
        "sha256": hashlib.sha256(outside_data).hexdigest(),
    }
    with pytest.raises(delivery.DeliveryError, match="cannot be safely read"):
        delivery.record_observed_proof(run_dir, bad)
    assert outside.read_text(encoding="utf-8") == "do not open"
    assert {
        path for path in run_dir.iterdir() if path.name != ".verification.lock"
    } == before | {linked}

    bad = json.loads(json.dumps(proof))
    bad["fragments"]["before"]["end"] = 999999
    with pytest.raises(delivery.DeliveryError, match="offsets"):
        delivery.record_observed_proof(run_dir, bad)
    (run_dir / "inspection.json").write_text(
        '{"schema":"changerail.inspection-observation.v1","schema":"duplicate"}',
        encoding="utf-8",
    )
    duplicate = json.loads(json.dumps(proof))
    duplicate["artifact"] = _reference(run_dir / "inspection.json")
    with pytest.raises(delivery.DeliveryError, match="closed JSON"):
        delivery.record_observed_proof(run_dir, duplicate)


def test_observed_proof_receipt_rejects_non_pytest_failed_and_summary_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _actual_pytest_proof(root, card, run_dir)
    # A content swap after reference construction proves the receipt reader is
    # fed the exact bytes that the proof artifact hash authenticated.
    receipt = root / proof["artifact"]["path"]
    original = receipt.read_bytes()
    receipt.write_bytes(original + b" ")
    with pytest.raises(delivery.DeliveryError, match="integrity"):
        delivery._validate_observed_proof(
            proof,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="review",
        )
    receipt.write_bytes(original)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "review")
    delivery.record_observed_proof(run_dir, proof)

    assert (
        delivery.run_evidence(
            "failed-pytest",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-vv",
                "tests/test_receipt.py::test_failure",
            ],
        )
        == 1
    )
    failed_receipt = _receipt_with_label(run_dir, "failed-pytest")
    failed_item, _log, _current = delivery.read_check_result(
        failed_receipt, run_dir, "focused"
    )
    failed = json.loads(json.dumps(proof))
    failed["artifact"] = _reference(failed_receipt)
    failed.update(
        {
            "attempt_id": failed_item["attempt_id"],
            "command_identity": failed_item["command_identity"],
        }
    )
    with pytest.raises(delivery.DeliveryError, match="no current"):
        delivery._validate_observed_proof(
            failed,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="review",
        )

    assert (
        delivery.run_evidence(
            "summary-only",
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-q",
                "tests/test_receipt.py::test_value[one]",
            ],
        )
        == 0
    )
    summary_receipt = _receipt_with_label(run_dir, "summary-only")
    summary_item, summary_log, _current = delivery.read_check_result(
        summary_receipt, run_dir, "focused"
    )
    assert b"1 passed" in summary_log and b" PASSED" not in summary_log
    summary = json.loads(json.dumps(proof))
    summary["artifact"] = _reference(summary_receipt)
    summary.update(
        {
            "attempt_id": summary_item["attempt_id"],
            "command_identity": summary_item["command_identity"],
        }
    )
    with pytest.raises(delivery.DeliveryError, match="selected node"):
        delivery._validate_observed_proof(
            summary,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="review",
        )

    assert (
        delivery.run_evidence(
            "echo",
            [
                sys.executable,
                "-c",
                "print('tests/test_receipt.py::test_value[one] PASSED')",
            ],
        )
        == 0
    )
    echo_receipt = _receipt_with_label(run_dir, "echo")
    bad = json.loads(json.dumps(proof))
    bad["artifact"] = _reference(echo_receipt)
    item, _log, _current = delivery.read_check_result(echo_receipt, run_dir, "focused")
    bad.update(
        {"attempt_id": item["attempt_id"], "command_identity": item["command_identity"]}
    )
    with pytest.raises(delivery.DeliveryError, match="pytest selector"):
        delivery._validate_observed_proof(
            bad,
            card=card,
            run_dir=run_dir,
            inventory=delivery.derive_proof_inventory(card),
            role="review",
        )


def test_observed_proof_closed_types_and_wrong_kind_refuse_before_index_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    (root / "source.txt").write_bytes(b"x")
    inspection = _inspection_proof(root, card, run_dir)
    inspection_record = delivery.record_observed_proof(run_dir, inspection)
    runtime = _runtime_proof(root, card, run_dir)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    runtime_record = delivery.record_outer_observed_proof(run_dir, runtime)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    accepted_records = {
        path: path.read_bytes() for path in (inspection_record, runtime_record)
    }
    accepted_set = sorted(
        path.name for path in (run_dir / "proof-records").glob("*.json")
    )
    accepted_index = (run_dir / "proof-index.json").read_bytes()
    inventory = delivery.derive_proof_inventory(card)

    def assert_preserved() -> None:
        assert {
            path: path.read_bytes() for path in accepted_records
        } == accepted_records
        assert (
            sorted(path.name for path in (run_dir / "proof-records").glob("*.json"))
            == accepted_set
        )
        assert (run_dir / "proof-index.json").read_bytes() == accepted_index

    def reject_artifact(
        proof: dict[str, object], field: str, value: object, *, outer: bool = False
    ) -> None:
        artifact = root / str(proof["artifact"]["path"])
        original = artifact.read_bytes()
        observed = json.loads(original)
        observed[field] = value
        artifact.write_text(json.dumps(observed), encoding="utf-8")
        candidate = json.loads(json.dumps(proof))
        candidate["artifact"] = _reference(artifact)
        try:
            monkeypatch.setenv(
                "CHRL_SESSION_ROLE", "outer" if outer else "implementation"
            )
            with pytest.raises(
                delivery.DeliveryError, match="invalid observation fields"
            ):
                if outer:
                    delivery.record_outer_observed_proof(run_dir, candidate)
                else:
                    delivery.record_observed_proof(run_dir, candidate)
            with pytest.raises(
                delivery.DeliveryError, match="invalid observation fields"
            ):
                delivery._validate_observed_proof(
                    candidate,
                    card=card,
                    run_dir=run_dir,
                    inventory=inventory,
                    role="outer" if outer else "implementation",
                )
            assert_preserved()
        finally:
            artifact.write_bytes(original)

    # Every case begins with independently valid bytes and changes exactly one
    # typed list item.  The real recorder and consumer both refuse before the
    # accepted index/history can advance.
    for proof, outer in ((inspection, False), (runtime, True)):
        reject_artifact(proof, "mocked_seams", [False], outer=outer)
        reject_artifact(proof, "residual_risks", [None], outer=outer)
        foreign = json.loads(json.dumps(proof))
        foreign["assertion_support"] = _assertion_support(root, "tests/test_receipt.py")
        monkeypatch.setenv("CHRL_SESSION_ROLE", "outer" if outer else "implementation")
        with pytest.raises(delivery.DeliveryError, match="schema validation"):
            if outer:
                delivery.record_outer_observed_proof(run_dir, foreign)
            else:
                delivery.record_observed_proof(run_dir, foreign)
        assert_preserved()

    # A task-local in-memory mutant removes only the metadata item gate.  Its
    # acceptance of each freshly hashed bad artifact proves these assertions do
    # not merely trip an older timestamp/reference failure.
    source = inspect.getsource(delivery._validate_observed_proof)
    import ast

    tree = ast.parse(source)

    class RemoveItemGate(ast.NodeTransformer):
        changed = 0

        def visit_Call(self, node):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "any"
                and "mocked_seams" in ast.unparse(node)
                and "isinstance(item" in ast.unparse(node)
            ):
                self.changed += 1
                return ast.copy_location(ast.Constant(False), node)
            return self.generic_visit(node)

    mutation = RemoveItemGate()
    tree = mutation.visit(tree)
    assert mutation.changed == 1
    namespace = dict(delivery.__dict__)
    exec(
        compile(ast.fix_missing_locations(tree), "<item-gate-mutant>", "exec"),
        namespace,
    )
    mutant = namespace["_validate_observed_proof"]
    for proof, outer in ((inspection, False), (runtime, True)):
        artifact = root / str(proof["artifact"]["path"])
        original = artifact.read_bytes()
        for field, value in (("mocked_seams", [False]), ("residual_risks", [None])):
            observed = json.loads(original)
            observed[field] = value
            artifact.write_text(json.dumps(observed), encoding="utf-8")
            candidate = json.loads(json.dumps(proof))
            candidate["artifact"] = _reference(artifact)
            assert (
                mutant(
                    candidate,
                    card=card,
                    run_dir=run_dir,
                    inventory=inventory,
                    role="outer" if outer else "implementation",
                )["outcome"]
                == "pass"
            )
            artifact.write_bytes(original)
    assert_preserved()


def test_observed_proof_nested_source_references_refuse_before_index_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nested sources use the same closed reference reader before any read."""

    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    (root / "source.txt").write_bytes(b"x")
    inspection = _inspection_proof(root, card, run_dir)
    inspection_record = delivery.record_observed_proof(run_dir, inspection)
    runtime = _runtime_proof(root, card, run_dir)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    runtime_record = delivery.record_outer_observed_proof(run_dir, runtime)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    retained = {path: path.read_bytes() for path in (inspection_record, runtime_record)}
    index = (run_dir / "proof-index.json").read_bytes()
    names = sorted(path.name for path in (run_dir / "proof-records").glob("*.json"))
    inventory = delivery.derive_proof_inventory(card)

    def unchanged() -> None:
        assert {path: path.read_bytes() for path in retained} == retained
        assert (run_dir / "proof-index.json").read_bytes() == index
        assert (
            sorted(path.name for path in (run_dir / "proof-records").glob("*.json"))
            == names
        )

    artifact = root / str(inspection["artifact"]["path"])
    original = artifact.read_bytes()
    for field, value in (
        ("size", True),
        ("size", 1.5),
        ("size", -1),
        ("sha256", "not-a-hash"),
        ("path", "../outside"),
    ):
        observed = json.loads(original)
        observed["inspected_sources"][0][field] = value
        artifact.write_text(json.dumps(observed), encoding="utf-8")
        candidate = json.loads(json.dumps(inspection))
        candidate["artifact"] = _reference(artifact)
        with pytest.raises(
            delivery.DeliveryError, match="reference is not closed|path is unsafe"
        ):
            delivery.record_observed_proof(run_dir, candidate)
        with pytest.raises(
            delivery.DeliveryError, match="reference is not closed|path is unsafe"
        ):
            delivery._validate_observed_proof(
                candidate,
                card=card,
                run_dir=run_dir,
                inventory=inventory,
                role="implementation",
            )
        unchanged()
        artifact.write_bytes(original)

    artifact = root / str(runtime["artifact"]["path"])
    original = artifact.read_bytes()
    for value in ([42], [None], [{"path": "../outside", "sha256": "not-a-hash"}]):
        observed = json.loads(original)
        observed["inspected_sources"] = value
        artifact.write_text(json.dumps(observed), encoding="utf-8")
        candidate = json.loads(json.dumps(runtime))
        candidate["artifact"] = _reference(artifact)
        monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
        with pytest.raises(
            delivery.DeliveryError, match="does not support inspected sources"
        ):
            delivery.record_outer_observed_proof(run_dir, candidate)
        with pytest.raises(
            delivery.DeliveryError, match="does not support inspected sources"
        ):
            delivery._validate_observed_proof(
                candidate, card=card, run_dir=run_dir, inventory=inventory, role="outer"
            )
        unchanged()
        artifact.write_bytes(original)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    assert {
        proof["condition"]
        for proof in delivery.require_current_stage_proofs(
            card,
            run_dir,
            ["implementation", "final"],
        )
    } == {inspection["condition"], runtime["condition"]}


def test_observed_proof_safe_retention(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    first = _inspection_proof(root, card, run_dir)
    first_record = delivery.record_observed_proof(run_dir, first)
    first_bytes = first_record.read_bytes()
    initial = delivery._check_json(run_dir / "proof-index.json")
    assert (
        initial["schema"] == "changerail.proof-index.v2"
        and len(initial["records"]) == 1
    )
    index_path = run_dir / "proof-index.json"
    index_bytes = index_path.read_bytes()
    outside = tmp_path / "index-outside"
    outside.write_text("sentinel", encoding="utf-8")
    index_path.unlink()
    index_path.symlink_to(outside)
    unsafe_index = json.loads(json.dumps(first))
    unsafe_index["observation_id"] = "unsafe-index"
    with pytest.raises(delivery.DeliveryError, match="index leaf is unsafe"):
        delivery.record_observed_proof(run_dir, unsafe_index)
    assert outside.read_text(encoding="utf-8") == "sentinel"
    index_path.unlink()
    index_path.write_bytes(index_bytes)

    # Two distinct observations may support one condition in one current generation.
    support = json.loads(json.dumps(first))
    support["observation_id"] = "implementation-c1-support"
    delivery.record_observed_proof(run_dir, support)
    assert len(delivery._check_json(run_dir / "proof-index.json")["records"]) == 2
    with pytest.raises(delivery.DeliveryError, match="duplicate observation"):
        delivery.record_observed_proof(run_dir, support)

    # A non-card payload edit starts a fresh current generation; old attempts are immutable.
    (root / "tracked.txt").write_text("non-card payload drift\n", encoding="utf-8")
    refreshed = _inspection_proof(root, card, run_dir)
    refreshed_record = delivery.record_observed_proof(run_dir, refreshed)
    current = delivery._check_json(run_dir / "proof-index.json")
    assert len(current["records"]) == 1 and current["records"][0][
        "path"
    ] == delivery.repo_relative(refreshed_record)
    assert first_record.read_bytes() == first_bytes and refreshed_record != first_record

    # A card-source edit similarly replaces, rather than appends, the generation.
    card.write_text(card.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    changed_card = _inspection_proof(root, card, run_dir)
    changed_record = delivery.record_observed_proof(run_dir, changed_card)
    after_card = delivery._check_json(run_dir / "proof-index.json")
    assert len(after_card["records"]) == 1 and after_card["records"][0][
        "path"
    ] == delivery.repo_relative(changed_record)
    assert first_record.read_bytes() == first_bytes

    # A terminal index failure retains an unindexed immutable attempt, leaves the
    # accepted generation untouched, and a fresh authorized retry succeeds.
    retry_root, retry_card, retry_run = _proof_repository(
        tmp_path / "retry", monkeypatch
    )
    retry_proof = _inspection_proof(retry_root, retry_card, retry_run)
    original_write = delivery._write_json_at

    def fail_index(directory_fd, name, payload, *, replace):
        if name == "proof-index.json":
            raise OSError("injected index failure")
        return original_write(directory_fd, name, payload, replace=replace)

    monkeypatch.setattr(delivery, "_write_json_at", fail_index)
    with pytest.raises(delivery.DeliveryError, match="retention failed"):
        delivery.record_observed_proof(retry_run, retry_proof)
    assert not (retry_run / "proof-index.json").exists()
    assert len(list((retry_run / "proof-records").glob("*.json"))) == 1
    monkeypatch.setattr(delivery, "_write_json_at", original_write)
    delivery.record_observed_proof(retry_run, retry_proof)
    assert len(delivery._check_json(retry_run / "proof-index.json")["records"]) == 1


def _proof_child_bootstrap(root: Path) -> str:
    """Mirror the parent component fixture without inheriting a consumer profile."""
    source = MODULE_PATH.resolve().parents[2]
    return (
        "import importlib.util, os, time; from pathlib import Path; "
        f"os.environ['CHRL_PROJECT_ROOT']={str(source)!r}; "
        f"s=importlib.util.spec_from_file_location('proof_child_delivery',{str(MODULE_PATH)!r}); "
        "d=importlib.util.module_from_spec(s); s.loader.exec_module(d); "
        "os.environ.pop('CHRL_PROJECT_ROOT'); "
        f"d.PROFILE_PATH=Path({str(source / 'tools/changerail/templates/profile.toml')!r}); "
        f"root=Path({str(root)!r}); d.REPO_ROOT=root; "
        "d.BOARD_ROOT=root/'openspec'/'board'; d.RUNTIME_ROOT=root/'.runtime/changerail'; "
        "d.checked_frozen_records=lambda: {}; d.native.is_native=lambda card: False; "
    )


def _proof_child_env(run_dir: Path) -> dict[str, str]:
    return {
        **{
            key: value
            for key, value in os.environ.items()
            if not key.startswith("CHRL_")
        },
        "CHRL_RUN_DIR": str(run_dir),
        "CHRL_SESSION_ROLE": "implementation",
    }


def test_observed_proof_serialized_recording(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _inspection_proof(root, card, run_dir)
    input_path = run_dir / "proof-input.json"
    input_path.write_text(json.dumps(proof), encoding="utf-8")
    child = (
        _proof_child_bootstrap(root)
        + f"raise SystemExit(d.main(['proof','record',{delivery.repo_relative(input_path)!r}]))"
    )
    with delivery.verification_attempt_lock(run_dir, card, "focused"):
        contender = subprocess.run(
            [sys.executable, "-c", child],
            cwd=root,
            env=_proof_child_env(run_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        assert contender.returncode == 2 and "already running" in contender.stderr
        assert not (run_dir / "proof-index.json").exists()
        assert (
            not list((run_dir / "proof-records").glob("*.json"))
            if (run_dir / "proof-records").exists()
            else True
        )
    assert delivery.main(["proof", "record", delivery.repo_relative(input_path)]) == 0
    before = (run_dir / "proof-index.json").read_bytes()
    monkeypatch.delenv("CHRL_SESSION_ROLE")
    assert delivery.main(["proof", "record", delivery.repo_relative(input_path)]) == 2
    assert (run_dir / "proof-index.json").read_bytes() == before

    # A child that leaves a running receipt then dies is an unresolved verifier;
    # recorder re-acquisition refuses rather than certifying it.
    starter = (
        _proof_child_bootstrap(root)
        + f"d.start_check_result(Path({str(run_dir)!r}),'focused','orphan',{{'kind':'argv','argv':['true']}})"
    )
    subprocess.run(
        [sys.executable, "-c", starter],
        cwd=root,
        env=_proof_child_env(run_dir),
        check=True,
        capture_output=True,
    )
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    assert delivery.main(["proof", "record", delivery.repo_relative(input_path)]) == 2
    assert (run_dir / "proof-index.json").read_bytes() == before


def test_observed_proof_serialized_recording_post_record_barrier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _inspection_proof(root, card, run_dir)
    input_path = run_dir / "proof-input.json"
    input_path.write_text(json.dumps(proof), encoding="utf-8")
    ready, release = run_dir / "record-ready", run_dir / "record-release"
    relative = delivery.repo_relative(input_path)
    child = (
        _proof_child_bootstrap(root)
        + f"ready=Path({str(ready)!r}); release=Path({str(release)!r})\n"
        "def hook():\n ready.write_text('ready');\n while not release.exists(): time.sleep(.01)\n"
        f"d._PROOF_RECORD_POST_RETENTION_HOOK=hook; raise SystemExit(d.main(['proof','record',{relative!r}]))"
    )
    env = _proof_child_env(run_dir)
    recorder = subprocess.Popen(
        [sys.executable, "-c", child],
        cwd=root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 5
    while not ready.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    if not ready.exists():
        stdout, stderr = recorder.communicate(timeout=1)
        pytest.fail(f"recorder did not reach post-record barrier: {stdout} {stderr}")
    assert ready.read_text(encoding="utf-8") == "ready"
    contender = subprocess.run(
        [
            sys.executable,
            "-c",
            child.replace("d._PROOF_RECORD_POST_RETENTION_HOOK=hook; ", ""),
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert contender.returncode == 2 and "already running" in contender.stderr
    assert not (run_dir / "proof-index.json").exists()
    assert len(list((run_dir / "proof-records").glob("*.json"))) == 1
    release.write_text("release", encoding="utf-8")
    stdout, stderr = recorder.communicate(timeout=5)
    assert recorder.returncode == 0, (stdout, stderr)
    assert len(delivery._check_json(run_dir / "proof-index.json")["records"]) == 1


def test_ordinary_consumers_refuse_coherently_forged_finalizer_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _proof_repository(tmp_path, monkeypatch)
    proof = _inspection_proof(root, card, run_dir)
    path = delivery.record_observed_proof(run_dir, proof)
    assert (
        delivery.require_current_stage_proofs(card, run_dir, ["implementation"])[0][
            "recorder_role"
        ]
        == "implementation"
    )
    artifact = root / proof["artifact"]["path"]
    data = delivery._check_json(artifact)
    data["role"] = "finalizer"
    delivery.write_json(artifact, data)
    proof["recorder_role"] = "finalizer"
    proof["artifact"] = _reference(artifact)
    delivery.write_json(path, proof)
    index_path = run_dir / "proof-index.json"
    index = delivery._check_json(index_path)
    index["records"] = [_reference(path)]
    delivery.write_json(index_path, index)
    before = {p: p.read_bytes() for p in (artifact, path, index_path)}
    inventory = delivery._current_proof_inventory(card, run_dir)
    with pytest.raises(
        delivery.DeliveryError, match="schema validation|role cannot record"
    ):
        delivery._validated_index_records(
            index, card=card, run_dir=run_dir, inventory=inventory
        )
    for stages in (
        ["implementation"],
        ["implementation", "review"],
        ["implementation", "review", "final"],
    ):
        with pytest.raises(
            delivery.DeliveryError, match="schema validation|role cannot record"
        ):
            delivery.require_current_stage_proofs(card, run_dir, stages)
    assert {p: p.read_bytes() for p in before} == before
