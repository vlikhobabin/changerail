from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
import signal
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path

import pytest

from tools.changerail.tests.test_native_openspec_integration import project as project

# Synthetic locators belong to isolated test boards, not the checkout board.
# Keep actual repository references literal so the live-link gate checks them.
FIXTURE_BOARD = "openspec/board"

MODULE_PATH = Path(__file__).parents[3] / "scripts" / "changerail" / "local_delivery.py"
MODULE_SPEC = importlib.util.spec_from_file_location("local_delivery", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
delivery = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(delivery)


class _FixtureProcessGroups:
    """Own only test-created sessions, including a verifier's FIFO-held child."""

    def __init__(self) -> None:
        self.processes: list[subprocess.Popen[str]] = []

    def start(self, args: list[str], *, cwd: Path, **kwargs) -> subprocess.Popen[str]:
        process = subprocess.Popen(args, cwd=cwd, start_new_session=True, **kwargs)
        self.processes.append(process)
        return process

    def close(self) -> None:
        for process in reversed(self.processes):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if process.poll() is None:
                process.wait(timeout=5)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    )


def _repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Test")
    _git(root, "config", "user.email", "test@example.invalid")
    (root / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git(root, "add", "--", "tracked.txt")
    _git(root, "commit", "-m", "baseline")
    monkeypatch.setattr(delivery, "REPO_ROOT", root)
    monkeypatch.setattr(delivery, "BOARD_ROOT", root / "openspec" / "board")
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", root / ".runtime" / "changerail")
    original_profile = delivery.profile()
    monkeypatch.setattr(
        delivery, "profile", lambda: {**original_profile, "history": {}}
    )
    # These component tests own receipt/lock/review mechanics. Full native artifact
    # and typed proof gates are exercised separately in native/observed integration.
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    from scripts.changerail import native_workflow

    monkeypatch.setattr(native_workflow, "checkpoint", lambda *args: None)
    monkeypatch.setattr(delivery, "_run_observed_contract", lambda run: None)
    original_retain = delivery.retain_recovery_manifest

    def retain_native_fixture(*, card_name, run_dir, manifest):
        run_path = run_dir / "run.json"
        owner = delivery.load_json(run_path) if run_path.is_file() else {}
        owner.update(
            execution_contract="changerail.native.v1",
            mode="delivery",
            lifecycle_mode="openspec-v1",
        )
        delivery.write_json(run_path, owner)
        return original_retain(card_name=card_name, run_dir=run_dir, manifest=manifest)

    monkeypatch.setattr(delivery, "retain_recovery_manifest", retain_native_fixture)

    return root


def _legacy_observed_anchor(run_dir: Path, card: Path) -> None:
    """Current native owner metadata for isolated receipt component fixtures."""
    delivery.write_json(
        run_dir / "run.json",
        {
            "schema": "changerail.delivery-run.v2",
            "run_id": run_dir.name,
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "card": delivery.repo_relative(card),
            "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
            "started_at": delivery.utc_now(),
            "change_plan": [],
        },
    )


def _trust_legacy_observed_fixture(run_dir: Path, card: Path) -> None:
    """Historical helper name retained inside receipt tests; no trust registry."""
    return None


def _copy_exact_legacy_recovery_source(
    source_run: Path, run_dir: Path, card: Path
) -> None:
    """Create an independently pinned exact-v1 recovery target for a fixture.

    The source payload is unchanged.  This deliberately writes a complete new
    run-local manifest and then pins its bytes; it never asks production code to
    treat missing run metadata as legacy.
    """

    _legacy_observed_anchor(run_dir, card)
    manifest = delivery.load_json(source_run / "manifest.json")
    manifest["run_id"] = run_dir.name
    manifest["card"] = {"id": card.stem, "path": delivery.repo_relative(card)}
    delivery.write_json(run_dir / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run_dir, card)


def _anchor_exact_legacy_recovery_source(run_dir: Path, card: Path) -> None:
    """Seed one genuine exact-v1 source without using a v2 adoption path."""

    _legacy_observed_anchor(run_dir, card)
    paths = delivery.changed_paths()
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": run_dir.name,
        "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
        "created_at": "2026-09-04T00:00:00Z",
        "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        "paths": paths,
        "fingerprint": delivery.payload_fingerprint(paths),
        "path_fingerprints": delivery.path_fingerprints(paths),
    }
    delivery.write_json(run_dir / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run_dir, card)


def _isolate_legacy_review_cycle_unit(
    monkeypatch: pytest.MonkeyPatch, run_dir: Path
) -> None:
    """Keep old mutable-cycle accounting units outside the C4 selector.

    These cases deliberately change a legacy fixture payload between review
    cycles to test accounting/delta mechanics.  Exact-v1 continuation correctly
    refuses that as a recovery source; the v1/v2 selector is not their unit
    boundary and is covered by the real C4 integrations.  This is an explicit
    per-test seam, not an autouse/module policy fallback.
    """

    contract = delivery._run_observed_contract
    monkeypatch.setattr(
        delivery,
        "_run_observed_contract",
        lambda selected_run: (
            None if selected_run == run_dir else contract(selected_run)
        ),
    )


def _recovery_card_baseline(root: Path) -> Path:
    """Add the active fixture card before dirty recovery payload is created."""

    card = root / f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    card.parent.mkdir(parents=True, exist_ok=True)
    card.write_text(_card_text(), encoding="utf-8")
    _git(root, "add", "--", delivery.repo_relative(card))
    _git(root, "commit", "-m", "fixture card baseline")
    return card


def _frozen_records(root: Path, monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    records = {}
    for index in range(4):
        relative = f"openspec/board/3.inprogress/old-{index}.md"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            _card_text() + f"\n{FIXTURE_BOARD}/1.backlog/card.md\n"
            f"{FIXTURE_BOARD}/2.todo/card.md\n"
            f"{FIXTURE_BOARD}/3.inprogress/card.md\n"
        )
        records[relative] = (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "superseded-no-go" if index < 3 else "suspended-not-verifiable",
        )
    manifest = root / ".changerail/history.json"
    manifest.parent.mkdir(exist_ok=True)
    delivery.write_json(
        manifest,
        {
            "schema": "changerail.project-history.v1",
            "board_records": {
                p: {"sha256": v[0], "disposition": v[1]} for p, v in records.items()
            },
            "files": {},
        },
    )
    current = delivery.profile()
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {**current, "history": {"manifest": ".changerail/history.json"}},
    )
    return [root / path for path in records]


def test_frozen_records_are_not_active_and_copies_are(tmp_path, monkeypatch):
    root = _repository(tmp_path, monkeypatch)
    frozen = _frozen_records(root, monkeypatch)
    activity = delivery.board_activity()
    assert activity == {
        "active": [],
        "superseded-no-go": frozen[:3],
        "suspended-not-verifiable": frozen[3:],
    }
    copy = frozen[0].with_name("old-0-copy.md")
    copy.write_bytes(frozen[0].read_bytes())
    assert delivery.board_activity()["active"] == [copy]


@pytest.mark.parametrize(
    "mutation", ["edit", "delete", "move", "file-link", "ancestor-link"]
)
def test_frozen_integrity_rechecks_bytes_and_fails_closed(
    tmp_path, monkeypatch, mutation
):
    root = _repository(tmp_path, monkeypatch)
    frozen = _frozen_records(root, monkeypatch)
    delivery.checked_frozen_records()
    _git(root, "add", ".")
    _git(root, "commit", "-m", "frozen fixture")
    before = delivery.payload_fingerprint()
    path = frozen[0]
    if mutation == "edit":
        path.write_text(path.read_text() + "forged READY\n")
    elif mutation == "delete":
        path.unlink()
    elif mutation == "move":
        path.rename(path.with_name("moved.md"))
    elif mutation == "file-link":
        moved = path.rename(root / "outside.md")
        path.symlink_to(moved)
    else:
        moved = path.parent.rename(root / "outside")
        path.parent.symlink_to(moved, target_is_directory=True)
    assert delivery.payload_fingerprint() != before
    for check in (delivery.board_activity, delivery.live_board_reference_sources):
        with pytest.raises(delivery.DeliveryError, match="frozen board integrity"):
            check()
    with pytest.raises(delivery.DeliveryError, match="frozen board integrity"):
        delivery.rewrite_active_board_references("card.md", "unused")


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize(
    "entry",
    [
        "admission",
        "doctor",
        "run",
        "recovery",
        "review",
        "handoff",
        "publish",
        "start",
        "finalize",
        "manifest",
        "verdict",
        "recovery-source",
    ],
)
def test_frozen_targets_reject_before_side_effects(tmp_path, monkeypatch, index, entry):
    root = _repository(tmp_path, monkeypatch)
    frozen = _frozen_records(root, monkeypatch)
    card = frozen[index]
    before = {path: path.read_bytes() for path in frozen}
    run_dir = delivery.RUNTIME_ROOT / "runs" / "forged"
    run_dir.mkdir(parents=True)
    delivery.write_json(run_dir / "run.json", {"card": delivery.repo_relative(card)})
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.setenv("CHRL_RECOVERY_OBJECTIVE", "forged old retry")
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    for name in ("write_json", "emit_event", "launch_codex", "require_legacy_history"):
        monkeypatch.setattr(
            delivery, name, lambda *a, **kw: pytest.fail("side effect/late gate")
        )
    calls = {
        "admission": lambda: delivery.admission_report(card),
        "doctor": lambda: delivery.doctor(str(card), check_remote=False),
        "run": lambda: delivery.run_delivery(str(card)),
        "recovery": lambda: delivery.run_delivery(str(card), recovery=True),
        "review": lambda: delivery.run_review(str(card)),
        "handoff": lambda: delivery.implementation_handoff(str(card)),
        "publish": lambda: delivery.publish(str(card)),
        "start": lambda: delivery.start_delivery_card(card, {}),
        "finalize": lambda: delivery.finalize_card(card),
        "manifest": lambda: delivery.capture_manifest(str(card)),
        "verdict": lambda: delivery.verdict_template(str(card)),
        "recovery-source": lambda: delivery.recovery_source(card, []),
    }
    with pytest.raises(delivery.DeliveryError, match="frozen.*non-deliverable"):
        calls[entry]()
    assert {path: path.read_bytes() for path in frozen} == before
    assert list(run_dir.iterdir()) == [run_dir / "run.json"]


def test_publish_links_preserve_frozen_sources_but_validate_live_links(
    tmp_path, monkeypatch
):
    root = _repository(tmp_path, monkeypatch)
    frozen = _frozen_records(root, monkeypatch)
    before = {path: path.read_bytes() for path in frozen}
    live = root / f"{FIXTURE_BOARD}/1.backlog/live.md"
    live.parent.mkdir(parents=True)
    live.write_text(f"{FIXTURE_BOARD}/2.todo/card.md\n")
    with pytest.raises(delivery.DeliveryError, match="dangling live board"):
        delivery.require_live_board_references([])
    destination = f"{FIXTURE_BOARD}/4.done/card.md"
    assert delivery.rewrite_active_board_references("card.md", destination) == [
        delivery.repo_relative(live)
    ]
    (root / destination).parent.mkdir(parents=True)
    (root / destination).write_text("done fixture\n")
    delivery.require_live_board_references([])
    assert {path: path.read_bytes() for path in frozen} == before
    live.write_text(f"openspec/board/2.todo/{frozen[0].name}\n")
    with pytest.raises(delivery.DeliveryError, match="dangling live board"):
        delivery.require_live_board_references([])


def test_doctor_distinguishes_history_start_recovery_and_dependencies(
    tmp_path, monkeypatch
):
    root = _repository(tmp_path, monkeypatch)
    frozen = _frozen_records(root, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/2.todo/card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text("2.todo"))
    (root / ".gitignore").write_text(".runtime/\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "accepted and historical fixture")

    def checks(target=card, recovery=False):
        return {
            item["name"]: item
            for item in delivery.doctor(
                str(target), check_remote=False, recovery=recovery
            )["checks"]
        }

    initial = checks()
    assert initial["clean-start"]["status"] == "pass"
    assert initial["single-active-card"]["status"] == "pass"
    for path in frozen[:3]:
        assert path.name in initial["superseded-no-go"]["detail"]
    assert frozen[3].name in initial["suspended-not-verifiable"]["detail"]
    card.write_text(
        card.read_text().replace("- none", f"- `{delivery.repo_relative(frozen[0])}`")
    )
    assert checks()["dependencies"]["status"] == "fail"
    card.write_text(_card_text("2.todo"))
    active = card.replace(frozen[0].parent / card.name)
    active.write_text(_card_text())
    assert checks(active)["single-active-card"]["status"] == "fail"
    monkeypatch.setenv("CHRL_RECOVERY_OBJECTIVE", "finish the fixture")
    assert checks(active, True)["recovery-payload"]["status"] == "fail"
    run_dir = delivery.RUNTIME_ROOT / "runs" / "retained"
    run_dir.mkdir(parents=True)
    delivery.retain_recovery_manifest(
        card_name=active.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": "retained",
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {"id": active.stem, "path": delivery.repo_relative(active)},
        },
    )
    recovered = checks(active, True)
    for name in ("single-active-card", "recovery-payload", "recovery-objective"):
        assert recovered[name]["status"] == "pass"
    monkeypatch.delenv("CHRL_RECOVERY_OBJECTIVE")
    assert checks(active, True)["recovery-objective"]["status"] == "fail"
    second = active.with_name("second.md")
    second.write_text(_card_text())
    assert checks(active, True)["single-active-card"]["status"] == "fail"
    assert checks(second, True)["recovery-payload"]["status"] == "fail"


def _card_text(status: str = "3.inprogress") -> str:
    return """# Test measured delivery

## Status
<status>

## Lifecycle
openspec-v1

## Acceptance
- [C1] observable result

## Design
- static fixture

## Verify
```json
{"schema":"changerail.card-evidence.v1","conditions":[{"condition":"C1","seam":"fixture","precondition":"card exists","action":"validate","expected":"static declaration","method":{"kind":"test","target":"tests/test_fixture.py"},"stage":"implementation"}],"risks":[{"kinds":["input_safety"],"applies":true,"decision":"closed schema","conditions":["C1"]},{"kinds":["mutation","restart"],"applies":false,"decision":"read-only fixture","conditions":[]},{"kinds":["concurrency","publication","external_effects"],"applies":false,"decision":"no side effects","conditions":[]}]}
```

## Delivery Budget
- primary_invariant: fixture admission
- expected_wall_minutes: 15
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 1

## Depends On
- none

## Result
implementation in progress

## Next
- verify

## Log
- 2026-09-02T00:00:00Z started
""".replace("<status>", status)


def test_admission_counts_structured_requirements_not_scenario_steps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = root / "structured-card.md"
    card.write_text(
        """# Structured acceptance

## Lifecycle
openspec-v1

## Acceptance

### Requirement: First obligation

#### Scenario: First case

- [C1] WHEN an input arrives
- [C2] THEN the first behavior is observable
- [C3] AND its evidence is retained

### Requirement: Second obligation

#### Scenario: Second case

- [C4] WHEN another input arrives
- [C5] THEN the second behavior is observable

## Design
- static fixture

## Verify
```json
{"schema":"changerail.card-evidence.v1","conditions":[{"condition":"C1","seam":"a","precondition":"a","action":"a","expected":"a","method":{"kind":"test","target":"tests/future.py"},"stage":"implementation"},{"condition":"C2","seam":"a","precondition":"a","action":"a","expected":"a","method":{"kind":"test","target":"tests/future.py"},"stage":"implementation"},{"condition":"C3","seam":"a","precondition":"a","action":"a","expected":"a","method":{"kind":"test","target":"tests/future.py"},"stage":"implementation"},{"condition":"C4","seam":"a","precondition":"a","action":"a","expected":"a","method":{"kind":"test","target":"tests/future.py"},"stage":"implementation"},{"condition":"C5","seam":"a","precondition":"a","action":"a","expected":"a","method":{"kind":"test","target":"tests/future.py"},"stage":"implementation"}],"risks":[{"kinds":["input_safety"],"applies":true,"decision":"closed","conditions":["C1"]},{"kinds":["mutation","restart"],"applies":false,"decision":"none","conditions":[]},{"kinds":["concurrency","publication","external_effects"],"applies":false,"decision":"none","conditions":[]}]}
```

## Delivery Budget
- primary_invariant: both obligation groups describe one bounded behavior
- expected_wall_minutes: 15
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 80

## Change 1: `structured-acceptance`

## Change 2: `structured-application`
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "admission": {
                "max_expected_wall_minutes": 15,
                "max_acceptance_criteria": 4,
                "max_production_owners": 1,
                "max_runtime_contours": 1,
                "max_estimated_product_files": 5,
                "max_estimated_production_loc": 300,
            }
        },
    )

    report = delivery.admission_report(card)

    assert report["status"] == "READY"
    assert report["change_count"] == 2
    assert report["acceptance_criteria"] == 2
    assert delivery.acceptance_criteria(card) == [
        "Requirement: First obligation / Scenario: First case",
        "Requirement: Second obligation / Scenario: Second case",
    ]


def test_change_checkpoints_are_ordered_and_required_before_preverify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    card.write_text(
        card.read_text(encoding="utf-8")
        + "\n## Change 1: `validate-projection`\n"
        + "\n## Change 2: `apply-projection`\n",
        encoding="utf-8",
    )
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": run_dir.name,
            "card": delivery.repo_relative(card),
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": [
                {"number": 1, "slug": "validate-projection"},
                {"number": 2, "slug": "apply-projection"},
            ],
        },
    )

    with pytest.raises(delivery.DeliveryError, match="order violation"):
        delivery.emit_event("change-2", "starting")

    delivery.emit_event("change-1", "starting")
    delivery.emit_event("change-1", "complete")
    with pytest.raises(delivery.DeliveryError, match="change-2.*starting"):
        delivery.preverify(str(card))
    assert observed == []

    delivery.emit_event("change-2", "starting")
    delivery.emit_event("change-2", "complete")
    assert delivery.preverify(str(card)) == 0
    assert observed == ["quick-one", "quick-two"]
    checkpoints = delivery.change_checkpoint_statuses(
        delivery.declared_change_plan(run_dir) or [],
        delivery.combined_change_events(run_dir),
    )
    assert [(item["slug"], item["status"]) for item in checkpoints] == [
        ("validate-projection", "complete"),
        ("apply-projection", "complete"),
    ]
    assert all(isinstance(item["duration_seconds"], float) for item in checkpoints)


def _verdict_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, dict[str, object]]:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(
        _card_text().replace(
            "- [C1] observable result", "- criterion one\n- criterion two"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        delivery,
        "VERDICT_SCHEMA_PATH",
        Path(__file__).parents[3]
        / "tools"
        / "changerail"
        / "schemas"
        / "review-verdict.schema.json",
    )
    template = delivery.verdict_template(str(card))["template"]
    for item in template["acceptance"]:
        item["evidence"] = ["focused evidence"]
    return card, template


def _review_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    root = _repository(tmp_path, monkeypatch)
    # A test's legacy fixture is not an implementation session.  Tests that
    # exercise role refusal set that role explicitly at their call boundary.
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    current_profile = delivery.profile()
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            **current_profile,
            "budgets": {**current_profile["budgets"], "enforce_limits": True},
            "verification": {
                **current_profile["verification"],
                "pre_review_commands": ["true"],
            },
        },
    )
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(
        _card_text().replace(
            "implementation in progress", "implemented observable result"
        ),
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("first\n", encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    # These receipt/finalizer fixtures exercise legacy consumer mechanics, not
    # v2 observed-proof adoption.  Keep that boundary explicit: a fixture-only
    # exact v1 identity and current recovery manifest are retained before any
    # legacy consumer is reached.  Missing metadata is never a test shortcut.
    _legacy_observed_anchor(run_dir, card)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    source_schema = (
        Path(__file__).parents[3]
        / "tools"
        / "changerail"
        / "schemas"
        / "review-verdict.schema.json"
    )
    schema_path = root / "tools" / "changerail" / "schemas" / source_schema.name
    schema_path.parent.mkdir(parents=True)
    schema_path.write_text(source_schema.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(delivery, "VERDICT_SCHEMA_PATH", schema_path)
    paths = delivery.changed_paths()
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": "run-1",
        "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "created_at": "2026-09-04T00:00:00Z",
        "card": {"id": "test-card", "path": delivery.repo_relative(card)},
        "paths": paths,
        "fingerprint": delivery.payload_fingerprint(paths),
        "path_fingerprints": delivery.path_fingerprints(paths),
    }
    delivery.write_json(delivery.manifest_path("test-card"), manifest)
    delivery.write_json(run_dir / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run_dir, card)
    delivery.capture_manifest(str(card))
    # capture_manifest updates its retained bytes, so renew only this isolated
    # fixture's independently declared v1 identity afterwards.
    _trust_legacy_observed_fixture(run_dir, card)
    return root, card, run_dir


def _write_verdict(card: Path, verdict: dict[str, object]) -> None:
    delivery.write_json(delivery.verdict_path(delivery.card_id(card)), verdict)


class _FakeCodexProcess:
    def __init__(self, events: list[dict[str, object]]) -> None:
        self._events = events
        self._streamed = threading.Event()
        self.stdout = self._stdout()
        self.stderr = iter(())
        self.terminated = False
        self.pid = 12345
        self.popen_kwargs: dict[str, object] = {}
        self.signals: list[int] = []

    def _stdout(self):
        for event in self._events:
            yield json.dumps(event) + "\n"
        self._streamed.set()

    def wait(self, timeout: float | None = None) -> int:
        assert self._streamed.wait(timeout=1)
        return -15 if self.terminated else 0

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.terminated = True


class _TimeoutCodexProcess(_FakeCodexProcess):
    def __init__(self) -> None:
        super().__init__([])
        self.wait_count = 0

    def wait(self, timeout: float | None = None) -> int:
        self.wait_count += 1
        if self.wait_count <= 2:
            raise subprocess.TimeoutExpired("codex", timeout)
        return -9


class _InterruptedCodexProcess(_FakeCodexProcess):
    def __init__(self) -> None:
        super().__init__([])
        self.wait_count = 0

    def wait(self, timeout: float | None = None) -> int:
        self.wait_count += 1
        if self.wait_count == 1:
            raise KeyboardInterrupt
        return -15


def _command_event(index: int) -> dict[str, object]:
    return {
        "type": "item.started",
        "item": {
            "id": f"command-{index}",
            "type": "command_execution",
            "command": f"command {index}",
            "aggregated_output": f"sensitive-output-{index}",
        },
    }


@pytest.mark.parametrize("role", ["implementation", "review"])
def test_budget_policy_observes_without_command_stops(role):
    budget = delivery._SessionCommandBudget(
        role,
        {
            "enforce_limits": False,
            "first_edit_discovery_commands": 1,
            "first_edit_hard_stop_commands": 2,
            "review_commands": 1,
            "review_verdict_only_commands": 2,
            "review_hard_stop_commands": 3,
        },
        inherited_investigative_commands=7,
    )
    for index in range(1, 41):
        assert budget.observe(_command_event(index)) is None
    snapshot = budget.snapshot()
    assert snapshot["enforced"] is False
    assert snapshot["observed"] == 47 and snapshot["session_observed"] == 40
    assert snapshot["inherited"] == 7 and snapshot["verdict_only_entered"] is False


def test_budget_policy_actual_child_survives_reference_timeout_and_count(
    tmp_path, monkeypatch
):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    marker = run / "completed"
    source = (
        "import json, subprocess, time; from pathlib import Path\n"
        "for i in range(30):\n"
        ' print(json.dumps({"type":"item.started","item":{"id":str(i),"type":"command_execution","command":"true"}}), flush=True)\n'
        ' subprocess.run(["true"], check=True)\n'
        "time.sleep(0.05)\n"
        f'Path({str(marker)!r}).write_text("completed")\n'
    )
    monkeypatch.setattr(
        delivery,
        "codex_session_command",
        lambda **kwargs: [sys.executable, "-c", source],
    )
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "budgets": {
                "enforce_limits": False,
                "review_commands": 1,
                "review_verdict_only_commands": 2,
                "review_hard_stop_commands": 3,
            }
        },
    )
    assert (
        delivery.launch_codex(
            role="review",
            prompt="fixture",
            model="fixture",
            reasoning="high",
            run_dir=run,
            timeout_minutes=0.0001,
            expected_artifact=marker,
        )
        == 0
    )
    metadata = delivery.load_json(run / "sessions/review-01/session.json")
    assert marker.read_text() == "completed"
    assert metadata["duration_seconds"] > 0.006 and metadata["timed_out"] is False
    assert metadata["command_budget"]["observed"] == 30
    assert metadata["command_budget"]["enforced"] is False
    assert metadata["budget_violation"] is None and metadata["completed"] is True
    assert not (run / "sessions/review-01/verdict-only.json").exists()


def test_budget_policy_admission_size_is_informational_but_structure_is_not(
    tmp_path, monkeypatch
):
    root = _repository(tmp_path, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/1.backlog/large.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        _card_text("1.backlog")
        .replace("expected_wall_minutes: 15", "expected_wall_minutes: 300")
        .replace("estimated_production_loc: 1", "estimated_production_loc: 1000")
        + "\n## Change 1: `large`\nImplement and verify.\n"
    )
    configured = delivery.profile()
    configured["admission"] = {key: 1 for key in configured["admission"]}
    configured["budgets"]["enforce_limits"] = False
    monkeypatch.setattr(delivery, "profile", lambda: configured)
    assert delivery.admission_report(card)["status"] == "READY"
    configured["budgets"]["enforce_limits"] = True
    assert delivery.admission_report(card)["status"] == "SPLIT_REQUIRED"
    configured["budgets"]["enforce_limits"] = False
    card.write_text(card.read_text().replace("changerail.card-evidence.v1", "unknown"))
    with pytest.raises(delivery.DeliveryError):
        delivery.admission_report(card)


def test_budget_policy_keeps_shared_two_review_limit(tmp_path, monkeypatch):
    root, card, run = _review_fixture(tmp_path, monkeypatch)
    configured = delivery.profile()
    configured["budgets"]["enforce_limits"] = False
    configured["max_review_cycles"] = 0
    monkeypatch.setattr(delivery, "profile", lambda: configured)

    def reviewer(**kwargs):
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["fixture semantic result"]
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", reviewer)  # Model boundary only.
    # This old budget-only unit deliberately mutates its synthetic payload
    # between cycles.  Exact v1 continuation is recovery-only and correctly
    # refuses that mutation; isolate only the unrelated observed-contract
    # selector so the real cycle accounting, manifests, pre-review receipts,
    # and verdict consumer remain under test.  C4 integration uses genuine
    # exact-v1 recovery and genuine v2 records elsewhere.
    contract = delivery._run_observed_contract
    with monkeypatch.context() as isolated:
        isolated.setattr(
            delivery,
            "_run_observed_contract",
            lambda selected_run: (
                None if selected_run == run else contract(selected_run)
            ),
        )
        for index in range(2):
            (root / "tracked.txt").write_text(str(index))
            delivery.capture_manifest(str(card))
            _write_matching_preverification(card, run)
            assert delivery.run_review(str(card)) == 0
    assert delivery.review_budget_usage(run)["semantic_cycles"] == 2
    assert len(list((run / "reviews").glob("cycle-??.json"))) == 2
    (root / "tracked.txt").write_text("third payload")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, run)
    with pytest.raises(delivery.DeliveryError, match="two-review budget"):
        delivery.run_review(str(card))
    # Numerical waiver does not permit stale prerequisite proof or another role.
    (root / "tracked.txt").write_text("unverified")
    with pytest.raises(delivery.DeliveryError):
        delivery.run_review(str(card))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    with pytest.raises(delivery.DeliveryError, match="must hand off"):
        delivery.run_review(str(card))


def test_budget_policy_runner_continues_repair_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    monkeypatch.setattr(delivery, "require_frozen_execution", lambda run: {})
    run = tmp_path / "run"
    run.mkdir()
    calls = {"review": 0, "floor": 0, "repair": 0, "publish": 0}

    def review(*args):
        calls["review"] += 1
        return 3 if calls["review"] <= 5 else 0

    def floor(*args):
        calls["floor"] += 1
        return 1 if calls["floor"] <= 3 else 0

    def repair(**kwargs):
        calls["repair"] += 1
        return run / "repair.json"

    def publish(*args):
        assert calls["review"] == 9 and calls["floor"] == 4
        calls["publish"] += 1
        return 0

    monkeypatch.setattr(
        delivery, "launch_implementation_stage", lambda **kwargs: "fixture-thread"
    )
    monkeypatch.setattr(delivery, "run_review", review)
    monkeypatch.setattr(delivery, "verify", floor)
    monkeypatch.setattr(delivery, "build_repair_context", repair)
    monkeypatch.setattr(delivery, "publish", publish)
    monkeypatch.setattr(delivery, "emit_event", lambda *args: None)
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    assert (
        delivery.orchestrate_delivery(
            card=tmp_path / "card.md",
            run_dir=run,
            current_profile={
                "budgets": {"enforce_limits": False},
                "max_review_cycles": 0,
                "max_terminal_semantic_repair_reviews": 0,
                "max_post_verification_repair_reviews": 0,
            },
            resume_thread_id=None,
            recovery_context=None,
            require_first_file_change=True,
            inherited_investigative_commands=0,
        )
        == 0
    )
    assert calls == {"review": 9, "floor": 4, "repair": 8, "publish": 1}


def test_review_budget_reserves_verdict_protocol_commands() -> None:
    budget = delivery._SessionCommandBudget(
        "review",
        {
            "review_commands": 12,
            "review_verdict_only_commands": 20,
            "review_hard_stop_commands": 24,
        },
    )

    for index in range(1, 13):
        assert budget.observe(_command_event(index)) is None
    for index, command in (
        (13, f"./bin/chrl verdict template {FIXTURE_BOARD}/3.inprogress/test.md"),
        (14, f"./bin/chrl verdict validate {FIXTURE_BOARD}/3.inprogress/test.md"),
    ):
        event = _command_event(index)
        event["item"]["command"] = command
        assert budget.observe(event) is None
        assert delivery._command_traits(command)["review_protocol"] is True

    for index in range(15, 23):
        assert budget.observe(_command_event(index)) is None
    assert budget.snapshot() == {
        "metric": "review_investigative_command_count",
        "enforced": True,
        "target": 12,
        "verdict_only_at": 20,
        "hard_stop": 24,
        "observed": 20,
        "inherited": 0,
        "session_observed": 20,
        "target_exceeded": True,
        "verdict_only_entered": True,
        "hard_stop_exceeded": False,
    }
    for index in range(23, 27):
        assert budget.observe(_command_event(index)) is None

    assert delivery.is_review_wrapper_command(
        f"./bin/chrl review {FIXTURE_BOARD}/3.inprogress/test.md"
    )
    assert not delivery.is_review_wrapper_command(
        f"./bin/chrl verdict validate {FIXTURE_BOARD}/3.inprogress/test.md"
    )
    violation = budget.observe(_command_event(27))

    assert violation is not None
    assert violation["metric"] == "review_investigative_command_count"
    assert violation["budget"] == 12
    assert violation["hard_stop_budget"] == 24
    assert violation["observed"] == 25


@pytest.mark.parametrize(
    "command",
    (
        f"./bin/chrl verdict template {FIXTURE_BOARD}/3.inprogress/test.md",
        f"./bin/chrl verdict validate {FIXTURE_BOARD}/3.inprogress/test.md",
        (
            "/bin/bash -lc './bin/chrl verdict template "
            f"{FIXTURE_BOARD}/3.inprogress/test.md'"
        ),
        (
            f"bash -lc './bin/chrl verdict validate {FIXTURE_BOARD}/3.inprogress/test.md'"
        ),
    ),
)
def test_review_protocol_recognizes_direct_and_shell_wrapped_commands(
    command: str,
) -> None:
    assert delivery.is_review_protocol_command(command) is True


def test_implementation_budget_excludes_exact_delivery_protocol_commands() -> None:
    budget = delivery._SessionCommandBudget(
        "implementation",
        {
            "first_edit_discovery_commands": 8,
            "first_edit_hard_stop_commands": 12,
        },
    )
    protocol_commands = (
        f"./bin/board-do {FIXTURE_BOARD}/2.todo/test.md",
        "./bin/chrl event do starting",
        "./bin/chrl event change-1 starting",
    )
    for index, command in enumerate(protocol_commands, start=1):
        event = _command_event(index)
        event["item"]["command"] = command
        assert budget.observe(event) is None
        assert delivery._command_traits(command)["delivery_protocol"] is True
    for index in range(1, 13):
        assert budget.observe(_command_event(index + 3)) is None
    violation = budget.observe(_command_event(16))

    assert violation is not None
    assert violation["observed"] == 13
    assert violation["metric"] == ("investigative_commands_before_first_file_change")


@pytest.mark.parametrize(
    "command",
    (
        "/bin/bash -lc './bin/chrl verdict fingerprint card.md'",
        "/bin/bash -lc './bin/chrl verdict template card.md && touch escaped'",
        "/bin/bash -lc './bin/chrl verdict template'",
        "/tmp/bash -lc './bin/chrl verdict template card.md'",
        "python ./bin/chrl verdict template card.md",
    ),
)
def test_review_protocol_rejects_non_protocol_or_composed_commands(
    command: str,
) -> None:
    assert delivery.is_review_protocol_command(command) is False


def _launch_with_command_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    role: str,
    command_count: int,
) -> tuple[Path, _FakeCodexProcess]:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run"
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": "run-1",
            "card": f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
            "started_at": "2026-09-03T00:00:00Z",
        },
    )
    events: list[dict[str, object]] = [
        {
            "type": "item.started",
            "item": {"id": "mcp-1", "type": "mcp_tool_call"},
        },
        *[_command_event(index) for index in range(1, command_count + 1)],
    ]
    if role == "implementation" and command_count == 8:
        events.extend(
            [
                {
                    "type": "item.started",
                    "item": {"id": "change-1", "type": "file_change"},
                },
                _command_event(9),
            ]
        )
    process = _FakeCodexProcess(events)

    def fake_popen(*args, **kwargs):
        del args
        process.popen_kwargs = kwargs
        return process

    def fake_killpg(pid: int, sent_signal: int) -> None:
        assert pid == process.pid
        if sent_signal == 0:
            # The observation after wait is not a termination signal.
            raise ProcessLookupError(pid)
        process.signals.append(sent_signal)
        process.terminated = True

    monkeypatch.setattr(delivery.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(delivery.os, "killpg", fake_killpg)
    monkeypatch.setattr(delivery, "execution_env", lambda extra=None: dict(extra or {}))
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "budgets": {
                "first_edit_discovery_commands": 8,
                "first_edit_hard_stop_commands": 12,
                "review_commands": 12,
                "review_verdict_only_commands": 20,
                "review_hard_stop_commands": 24,
            }
        },
    )
    return run_dir, process


def _verification_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path, dict[str, list[str]], list[str]]:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(
        _card_text().replace(
            "implementation in progress", "implemented observable result"
        ),
        encoding="utf-8",
    )
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    delivery.write_json(
        run_dir / "run.json",
        {
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "run_id": run_dir.name,
            "card": delivery.repo_relative(card),
            "change_plan": [],
        },
    )
    configured = {
        "pre_review_commands": ["quick-one", "quick-two"],
        "final_commands": ["check-one", "check-two"],
    }
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {"verification": configured},
    )
    observed: list[str] = []
    actual_run = delivery.run_shell_verification
    environment = delivery.execution_env
    monkeypatch.setattr(
        delivery,
        "execution_env",
        lambda extra=None: {
            **environment(extra),
            "BASH_FUNC_quick-one%%": "() { true; }",
            "BASH_FUNC_quick-two%%": "() { true; }",
            "BASH_FUNC_quick-three%%": "() { true; }",
            "BASH_FUNC_check-one%%": "() { true; }",
            "BASH_FUNC_check-two%%": "() { true; }",
        },
    )

    def observe_run(command: str, log: Path, **kwargs) -> dict[str, object]:
        observed.append(command)
        return actual_run(command, log, **kwargs)

    monkeypatch.setattr(delivery, "run_shell_verification", observe_run)
    return root, card, run_dir, configured, observed


def _allow_final_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    delivery.write_json(
        delivery.manifest_path("test-card"), {"paths": delivery.changed_paths()}
    )
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    monkeypatch.setattr(delivery, "validate_verdict", lambda value: {"result": "go"})


def _write_matching_preverification(card: Path, run_dir: Path) -> None:
    commands = delivery.verification_commands("pre_review")
    run_path = run_dir / "run.json"
    run = delivery._check_json(run_path) if run_path.exists() else {}
    run.update(
        {
            "run_id": run_dir.name,
            "card": delivery.repo_relative(card),
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": [],
            "started_at": delivery.utc_now(),
        }
    )
    delivery.write_json(run_path, run)
    if run.get("schema") == "changerail.delivery-run.v1" and False:
        # Fixture-only identity is renewed after this fixture deliberately
        # changes retained v1 metadata; production has no such identity entry.
        _trust_legacy_observed_fixture(run_dir, card)
    result = delivery._run_full_floor(
        card,
        commands=commands,
        root_name="preverification",
        result_name="preverification.json",
        schema="changerail.pre-review-verification.v1",
        event_stage="preverification",
        proof_lane="pre_review",
    )
    assert result["ok"]


def test_fingerprint_covers_staged_and_untracked_without_mutating_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    (root / "tracked.txt").write_text("staged\n", encoding="utf-8")
    (root / "new.txt").write_text("untracked\n", encoding="utf-8")
    _git(root, "add", "--", "tracked.txt")

    assert delivery.changed_paths() == ["new.txt", "tracked.txt"]
    staged_before = _git(root, "diff", "--cached", "--name-only").stdout
    first = delivery.payload_fingerprint()
    first_paths = delivery.path_fingerprints(["new.txt", "tracked.txt"])
    staged_after = _git(root, "diff", "--cached", "--name-only").stdout

    assert staged_after == staged_before == "tracked.txt\n"
    (root / "new.txt").write_text("changed untracked\n", encoding="utf-8")
    assert delivery.payload_fingerprint() != first
    changed_paths = delivery.path_fingerprints(["new.txt", "tracked.txt"])
    assert changed_paths["new.txt"] != first_paths["new.txt"]
    assert changed_paths["tracked.txt"] == first_paths["tracked.txt"]


def test_measured_codex_sessions_rely_on_launcher_mcp_filtering(tmp_path: Path) -> None:
    command = delivery.codex_session_command(
        model="gpt-6-astra",
        reasoning="high",
        last_message=tmp_path / "last-message.md",
        prompt="$chrl-review card.md",
    )

    overrides = [
        command[index + 1]
        for index, argument in enumerate(command[:-1])
        if argument == "-c"
    ]
    assert "mcp_servers.context7.enabled=false" not in overrides
    assert "mcp_servers.filesystem.enabled=false" not in overrides
    assert "tool_output_token_limit=4000" in overrides

    resumed = delivery.codex_session_command(
        model="gpt-6-astra",
        reasoning="high",
        last_message=tmp_path / "resumed-last-message.md",
        prompt="$chrl-ff specs card.md",
        resume_thread_id="thread-1",
    )
    assert resumed[1:3] == ["exec", "resume"]
    assert resumed[-2:] == ["thread-1", "$chrl-ff specs card.md"]


def test_profile_routes_atomic_implementation_to_terra_and_review_to_astra() -> None:
    current_profile = delivery.profile()

    assert delivery.model_route(current_profile, "implementation") == (
        "gpt-5.6-terra",
        "high",
    )
    assert delivery.model_route(current_profile, "review") == (
        "gpt-6-astra",
        "high",
    )


def test_recovery_source_refuses_same_path_byte_amendment_without_rewriting_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A retained manifest is proof of bytes, not merely a dirty path list."""
    root = _repository(tmp_path, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text())
    tracked = root / "tracked.txt"
    tracked.write_text("retained payload\n")

    run_dir = delivery.RUNTIME_ROOT / "runs" / "retained-exact"
    run_dir.mkdir(parents=True)
    counter = run_dir / "run.json"
    counter.write_text('{"counter": 1}\n')
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": "retained-exact",
        "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "card": {"id": card.stem, "path": delivery.repo_relative(card)},
    }
    delivery.retain_recovery_manifest(
        card_name=card.name, run_dir=run_dir, manifest=manifest
    )

    dirty_before = delivery.changed_paths()
    hashes_before = delivery.path_fingerprints(dirty_before)
    source = run_dir / "manifest.json"
    source_before = source.read_bytes()
    counter_before = counter.read_bytes()
    dirty_before = delivery.changed_paths()
    hashes_before = delivery.path_fingerprints(dirty_before)
    ok, _detail, _manifest = delivery.recovery_source(card, dirty_before)
    assert ok is True

    tracked.write_text("amended payload\n")
    dirty_after = delivery.changed_paths()
    assert dirty_after == dirty_before
    assert delivery.path_fingerprints(dirty_after) != hashes_before
    ok, detail, _manifest = delivery.recovery_source(card, dirty_after)
    assert ok is False
    assert "fingerprint" in detail
    assert source.read_bytes() == source_before
    assert counter.read_bytes() == counter_before


def _exact_recovery_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, run_id: str = "retained-exact"
) -> tuple[Path, Path, Path]:
    root = _repository(tmp_path, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text(), encoding="utf-8")
    (root / "tracked.txt").write_text("retained payload\n", encoding="utf-8")
    run_dir = delivery.RUNTIME_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True)
    delivery.retain_recovery_manifest(
        card_name=card.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run_id,
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        },
    )
    return root, card, run_dir


def _raw_duplicate_recovery_manifest(
    manifest: dict[str, object],
    target: str,
    value_mode: str,
    duplicate_first: bool,
    escaped_key: bool,
) -> str:
    """Encode one manifest with two JSON spellings of the same object key."""

    compact = lambda value: json.dumps(value, separators=(",", ":"))
    if target == "root":
        key = "fingerprint"
        actual = manifest[key]
    elif target == "nested-head":
        key = "head_commit"
        actual = manifest["fingerprint"][key]  # type: ignore[index]
    elif target == "nested-payload":
        key = "payload_fingerprint"
        actual = manifest["fingerprint"][key]  # type: ignore[index]
    else:
        key, actual = next(iter(manifest["path_fingerprints"].items()))  # type: ignore[index,union-attr]
    duplicate = actual if value_mode == "equal" else "sha256:stale"
    encoded_key = compact(key)
    duplicate_key = '"finger\\u0070rint"' if escaped_key else encoded_key
    original = f"{encoded_key}:{compact(actual)}"
    duplicate_entry = f"{duplicate_key}:{compact(duplicate)}"
    replacement = (
        f"{duplicate_entry},{original}"
        if duplicate_first
        else f"{original},{duplicate_entry}"
    )
    raw = compact(manifest)
    assert raw.count(original) == 1
    return raw.replace(original, replacement, 1)


@pytest.mark.parametrize(
    ("target", "value_mode", "duplicate_first", "escaped_key"),
    (
        ("root", "conflicting", True, True),
        ("root", "equal", False, False),
        ("nested-head", "conflicting", False, False),
        ("nested-payload", "equal", True, False),
        ("path", "conflicting", False, False),
        ("path", "equal", True, False),
    ),
)
def test_recovery_source_refuses_duplicate_json_keys_without_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    value_mode: str,
    duplicate_first: bool,
    escaped_key: bool,
) -> None:
    root, card, run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    source = run_dir / "manifest.json"
    counter = run_dir / "run.json"
    delivery.write_json(counter, {**delivery.load_json(counter), "counter": 3})
    paths = delivery.changed_paths()
    assert delivery.recovery_source(card, paths)[0] is True

    manifest = delivery.load_json(source)
    source.write_text(
        _raw_duplicate_recovery_manifest(
            manifest, target, value_mode, duplicate_first, escaped_key
        ),
        encoding="utf-8",
    )
    source_before = source.read_bytes()
    counter_before = counter.read_bytes()
    payload_before = {relative: (root / relative).read_bytes() for relative in paths}
    records_before = sorted(
        path.relative_to(delivery.RUNTIME_ROOT).as_posix()
        for path in delivery.RUNTIME_ROOT.rglob("*")
    )
    monkeypatch.setattr(
        delivery, "launch_codex", lambda **_kwargs: pytest.fail("model launch")
    )

    ok, detail, _manifest = delivery.recovery_source(card, paths)
    monkeypatch.setenv("CHRL_RECOVERY_OBJECTIVE", "check duplicate proof")
    checks = {
        item["name"]: item
        for item in delivery.doctor(str(card), check_remote=False, recovery=True)[
            "checks"
        ]
    }

    assert ok is False
    assert detail in {
        "previous delivery manifest is unavailable",
        "previous delivery manifest lacks exact fingerprint proof",
    }
    assert checks["recovery-payload"]["status"] == "fail"
    assert source.read_bytes() == source_before
    assert counter.read_bytes() == counter_before
    assert {
        relative: (root / relative).read_bytes() for relative in paths
    } == payload_before
    assert (
        sorted(
            path.relative_to(delivery.RUNTIME_ROOT).as_posix()
            for path in delivery.RUNTIME_ROOT.rglob("*")
        )
        == records_before
    )


def test_explicit_legacy_recovery_needs_exact_proof_but_not_fresh_admission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    fresh = root / f"{FIXTURE_BOARD}/2.todo/fresh-versionless.md"
    fresh.parent.mkdir(parents=True)
    fresh.write_text(
        "# Legacy card\n\n## Status\n\n2.todo\n\n## Lifecycle\nopenspec-v1\n\n"
        "## Acceptance\n\n- legacy\n",
        encoding="utf-8",
    )
    with pytest.raises(delivery.DeliveryError, match=r"requires a \[C<number>\]"):
        delivery.admission_report(fresh)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/legacy-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "# Legacy card\n\n## Status\n\n3.inprogress\n\n## Lifecycle\nopenspec-v1\n\n"
        "## Acceptance\n\n- legacy\n",
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("retained legacy payload\n", encoding="utf-8")
    run_dir = delivery.RUNTIME_ROOT / "runs" / "legacy-proof"
    run_dir.mkdir(parents=True)
    counter = run_dir / "run.json"
    counter.write_text('{"counter": 7}\n', encoding="utf-8")
    delivery.retain_recovery_manifest(
        card_name=card.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": "legacy-proof",
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        },
    )
    source = run_dir / "manifest.json"
    source_before = source.read_bytes()
    counter_before = counter.read_bytes()
    dirty_before = delivery.changed_paths()
    hashes_before = delivery.path_fingerprints(dirty_before)
    records_before = sorted(
        path.relative_to(delivery.RUNTIME_ROOT).as_posix()
        for path in delivery.RUNTIME_ROOT.rglob("*")
    )
    monkeypatch.setenv("CHRL_RECOVERY_OBJECTIVE", "finish legacy fixture")
    checks = {
        item["name"]: item
        for item in delivery.doctor(str(card), check_remote=False, recovery=True)[
            "checks"
        ]
    }
    assert checks["recovery-payload"]["status"] == "pass"
    assert source.read_bytes() == source_before
    assert counter.read_bytes() == counter_before
    assert (
        sorted(
            path.relative_to(delivery.RUNTIME_ROOT).as_posix()
            for path in delivery.RUNTIME_ROOT.rglob("*")
        )
        == records_before
    )

    (root / "tracked.txt").write_text("amended legacy payload\n", encoding="utf-8")
    dirty_after = delivery.changed_paths()
    assert dirty_after == dirty_before
    assert delivery.path_fingerprints(dirty_after) != hashes_before
    changed = {
        item["name"]: item
        for item in delivery.doctor(str(card), check_remote=False, recovery=True)[
            "checks"
        ]
    }
    assert changed["recovery-payload"]["status"] == "fail"
    assert source.read_bytes() == source_before
    assert counter.read_bytes() == counter_before
    assert (
        sorted(
            path.relative_to(delivery.RUNTIME_ROOT).as_posix()
            for path in delivery.RUNTIME_ROOT.rglob("*")
        )
        == records_before
    )


def test_recovery_source_refuses_forged_pointer_when_run_local_source_is_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    source = run_dir / "manifest.json"
    counter = run_dir / "run.json"
    delivery.write_json(counter, {**delivery.load_json(counter), "counter": 3})
    source_before = source.read_bytes()
    counter_before = counter.read_bytes()
    (root / "tracked.txt").write_text("forged pointer payload\n", encoding="utf-8")
    paths = delivery.changed_paths()
    pointer = delivery.load_json(source)
    pointer["paths"] = paths
    pointer["fingerprint"] = delivery.payload_fingerprint(paths)
    pointer["path_fingerprints"] = delivery.path_fingerprints(paths)
    delivery.write_json(delivery.manifest_path(card.stem), pointer)

    ok, detail, _manifest = delivery.recovery_source(card, paths)

    assert ok is False
    assert "exact fingerprint proof" in detail
    assert source.read_bytes() == source_before
    assert counter.read_bytes() == counter_before


@pytest.mark.parametrize(
    "corruption",
    (
        "missing-fingerprint",
        "missing-schema",
        "empty-fingerprint",
        "malformed-fingerprint",
        "malformed-path-fingerprints",
        "missing-path-digest",
        "extra-path-digest",
        "duplicate-path",
        "non-string-path-dict",
        "non-string-path-list",
        "wrong-run-id",
        "wrong-baseline",
        "unknown-schema",
        "non-object-json",
        "invalid-json",
        "invalid-encoding",
    ),
)
def test_recovery_source_refuses_incomplete_or_malformed_exact_proof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    _root, card, run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    source = run_dir / "manifest.json"
    manifest = delivery.load_json(source)
    if corruption == "missing-fingerprint":
        manifest.pop("fingerprint")
    elif corruption == "missing-schema":
        manifest.pop("schema")
    elif corruption == "empty-fingerprint":
        manifest["fingerprint"] = {}
    elif corruption == "malformed-fingerprint":
        manifest["fingerprint"] = "sha256:not-a-mapping"
    elif corruption == "malformed-path-fingerprints":
        manifest["path_fingerprints"] = []
    elif corruption == "missing-path-digest":
        manifest["path_fingerprints"].pop(manifest["paths"][0])
    elif corruption == "extra-path-digest":
        manifest["path_fingerprints"]["extra.txt"] = "sha256:forged"
    elif corruption == "duplicate-path":
        manifest["paths"].append(manifest["paths"][0])
    elif corruption == "non-string-path-dict":
        manifest["paths"] = [{}]
    elif corruption == "non-string-path-list":
        manifest["paths"] = [[]]
    elif corruption == "wrong-run-id":
        manifest["run_id"] = "other-run"
    elif corruption == "unknown-schema":
        manifest["schema"] = "unknown-schema.v100"
    elif corruption == "non-object-json":
        source.write_bytes(b"[]")
        manifest = None
    elif corruption == "invalid-json":
        source.write_bytes(b"{")
        manifest = None
    elif corruption == "invalid-encoding":
        source.write_bytes(b"\xff")
        manifest = None
    else:
        manifest["baseline_head"] = "0" * 40
    if manifest is not None:
        delivery.write_json(source, manifest)
    source_before = source.read_bytes()

    ok, detail, _manifest = delivery.recovery_source(card, delivery.changed_paths())

    assert ok is False
    assert detail in {
        "previous delivery manifest lacks exact fingerprint proof",
        "previous delivery manifest is unavailable",
    }
    assert source.read_bytes() == source_before


def test_recovery_source_uses_whole_tree_and_rejects_changed_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, _run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    dirty = delivery.changed_paths()
    assert delivery.recovery_source(card, dirty[:-1])[0] is False
    (root / "unlisted.txt").write_text("unlisted\n", encoding="utf-8")
    assert delivery.recovery_source(card, delivery.changed_paths())[0] is False
    (root / "unlisted.txt").unlink()
    (root / "head-change.txt").write_text("head change\n", encoding="utf-8")
    _git(root, "add", "head-change.txt")
    _git(root, "commit", "--only", "-m", "change baseline", "head-change.txt")
    ok, detail, _manifest = delivery.recovery_source(card, delivery.changed_paths())
    assert ok is False
    assert "exact fingerprint proof" in detail


@pytest.mark.parametrize("target_kind", ("missing", "external"))
def test_recovery_source_keeps_deletions_and_leaf_links_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target_kind: str
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text(), encoding="utf-8")
    (root / "tracked.txt").unlink()
    target = root.parent / f"{target_kind}-leaf-target"
    if target_kind == "external":
        target.write_text("do not read through leaf link\n", encoding="utf-8")
    link = root / "leaf-link"
    link.symlink_to(target)
    run_dir = delivery.RUNTIME_ROOT / "runs" / "retained-link"
    run_dir.mkdir(parents=True)
    delivery.retain_recovery_manifest(
        card_name=card.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": "retained-link",
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        },
    )
    original_open = Path.open
    original_read_text = Path.read_text

    def refuse_target_open(self: Path, *args: object, **kwargs: object):
        if self.resolve(strict=False) == target.resolve(strict=False):
            raise AssertionError("leaf symlink target was read")
        return original_open(self, *args, **kwargs)

    def refuse_target_read(self: Path, *args: object, **kwargs: object):
        if self.resolve(strict=False) == target.resolve(strict=False):
            raise AssertionError("leaf symlink target was read")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", refuse_target_open)
    monkeypatch.setattr(Path, "read_text", refuse_target_read)
    with pytest.raises(AssertionError, match="leaf symlink target"):
        link.open()
    with pytest.raises(AssertionError, match="leaf symlink target"):
        link.read_text()
    assert delivery.recovery_source(card, delivery.changed_paths())[0] is True
    link.unlink()
    link.symlink_to("different-target")
    ok, detail, _manifest = delivery.recovery_source(card, delivery.changed_paths())
    assert ok is False
    assert "exact fingerprint proof" in detail


@pytest.mark.parametrize("drift", ("chmod", "directory", "deletion", "card-rename"))
def test_recovery_source_refuses_path_type_mode_and_card_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, drift: str
) -> None:
    root, card, _run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    tracked = root / "tracked.txt"
    if drift == "chmod":
        tracked.chmod(0o755)
    elif drift == "directory":
        tracked.unlink()
        tracked.mkdir()
    elif drift == "deletion":
        tracked.unlink()
    else:
        card = card.rename(card.with_name("renamed-card.md"))

    assert delivery.recovery_source(card, delivery.changed_paths())[0] is False


@pytest.mark.parametrize(
    "unsafe", ("run-id", "payload-path", "manifest-link", "run-link")
)
def test_recovery_source_refuses_unsafe_retained_source_without_dereferencing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unsafe: str
) -> None:
    root, card, run_dir = _exact_recovery_fixture(tmp_path, monkeypatch)
    source = run_dir / "manifest.json"
    if unsafe == "run-id":
        source.unlink()
        unsafe_dir = delivery.RUNTIME_ROOT / "runs" / "unsafe run"
        unsafe_dir.mkdir()
        delivery.write_json(unsafe_dir / "manifest.json", {"run_id": "unsafe run"})
    elif unsafe == "payload-path":
        manifest = delivery.load_json(source)
        manifest["paths"] = ["../outside"]
        delivery.write_json(source, manifest)
    else:
        outside = root.parent / "outside-source"
        outside.mkdir()
        outside_manifest = outside / "manifest.json"
        outside_manifest.write_text('{"outside": true}\n', encoding="utf-8")
        source.unlink()
        original_read_text = Path.read_text
        original_open = Path.open

        def refuse_outside_read(self: Path, *args: object, **kwargs: object):
            if self.resolve(strict=False) == outside_manifest.resolve(strict=False):
                raise AssertionError("outside manifest was read")
            return original_read_text(self, *args, **kwargs)

        def refuse_outside_open(self: Path, *args: object, **kwargs: object):
            if self.resolve(strict=False) == outside_manifest.resolve(strict=False):
                raise AssertionError("outside manifest was read")
            return original_open(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", refuse_outside_read)
        monkeypatch.setattr(Path, "open", refuse_outside_open)
        if unsafe == "manifest-link":
            source.symlink_to(outside_manifest)
        else:
            (run_dir / "run.json").unlink()
            run_dir.rmdir()
            run_dir.symlink_to(outside, target_is_directory=True)
        with pytest.raises(AssertionError, match="outside manifest"):
            source.open()
        with pytest.raises(AssertionError, match="outside manifest"):
            source.read_text()

    assert delivery.recovery_source(card, delivery.changed_paths())[0] is False


def test_recovery_source_refuses_payload_ancestor_link_without_reading_outside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    nested = root / "nested"
    nested.mkdir()
    nested_file = nested / "payload.txt"
    nested_file.write_text("baseline nested\n", encoding="utf-8")
    _git(root, "add", "nested/payload.txt")
    _git(root, "commit", "-m", "add nested baseline")
    card = root / f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text(), encoding="utf-8")
    nested_file.write_text("retained nested\n", encoding="utf-8")
    run_dir = delivery.RUNTIME_ROOT / "runs" / "retained-nested"
    run_dir.mkdir(parents=True)
    delivery.retain_recovery_manifest(
        card_name=card.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": "retained-nested",
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        },
    )
    dirty_before = delivery.changed_paths()
    assert "nested/payload.txt" in dirty_before
    outside = root.parent / "outside-payload"
    outside.mkdir()
    outside_file = outside / "payload.txt"
    outside_file.write_text("outside\n", encoding="utf-8")
    nested_file.unlink()
    nested.rmdir()
    nested.symlink_to(outside, target_is_directory=True)
    actual_paths = delivery.changed_paths()
    assert "nested/payload.txt" in actual_paths
    assert actual_paths != dirty_before
    source = run_dir / "manifest.json"
    manifest = delivery.load_json(source)
    manifest["paths"] = actual_paths
    delivery.write_json(source, manifest)
    original_open = Path.open

    def refuse_outside_open(self: Path, *args: object, **kwargs: object):
        if self.resolve(strict=False) == outside_file.resolve(strict=False):
            raise AssertionError("payload ancestor symlink was followed")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", refuse_outside_open)
    with pytest.raises(AssertionError, match="payload ancestor"):
        (nested / "payload.txt").open()
    assert delivery.recovery_source(card, delivery.changed_paths())[0] is False


def test_recovery_source_requires_exact_previous_manifest_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(
        _card_text().replace(
            "implementation in progress", "implemented observable result"
        ),
        encoding="utf-8",
    )
    run_dir = root / ".runtime" / "changerail" / "runs" / "stopped-run"
    run_dir.mkdir(parents=True)
    (root / "tracked.txt").write_text("retained payload\n", encoding="utf-8")
    retained_manifest = delivery.retain_recovery_manifest(
        card_name=card.name,
        run_dir=run_dir,
        manifest={
            "schema": "changerail.delivery-manifest.v1",
            "run_id": "stopped-run",
            "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
            "card": {
                "id": "test-card",
                "path": f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
            },
        },
    )
    aborted_run = root / ".runtime" / "changerail" / "runs" / "zz-aborted-run"
    aborted_run.mkdir(parents=True)
    aborted_manifest = {
        "run_id": "zz-aborted-run",
        "card": retained_manifest["card"],
        "paths": [],
    }
    delivery.write_json(aborted_run / "manifest.json", aborted_manifest)
    delivery.write_json(delivery.manifest_path("test-card"), aborted_manifest)

    ok, detail, manifest = delivery.recovery_source(
        card,
        [f"{FIXTURE_BOARD}/3.inprogress/test-card.md", "tracked.txt"],
    )

    assert ok is True
    assert "stopped-run" in detail
    assert manifest is not None and manifest["run_id"] == "stopped-run"
    extra_ok, extra_detail, _manifest = delivery.recovery_source(
        card,
        [
            f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
            "tracked.txt",
            "unrelated.txt",
        ],
    )
    assert extra_ok is False
    assert "current worktree" in extra_detail


def test_recovery_context_ignores_incomplete_cycle_zero_and_indexes_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = _recovery_card_baseline(root)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    current_fingerprint = delivery.payload_fingerprint()
    previous_run = root / ".runtime" / "changerail" / "runs" / "previous"
    run_dir = root / ".runtime" / "changerail" / "runs" / "current"
    (previous_run / "focused-evidence").mkdir(parents=True)
    (previous_run / "reviews").mkdir()
    run_dir.mkdir(parents=True)
    change_plan = [
        {"number": 1, "slug": "validate-projection"},
        {"number": 2, "slug": "apply-projection"},
    ]
    _anchor_exact_legacy_recovery_source(previous_run, card)
    _copy_exact_legacy_recovery_source(previous_run, run_dir, card)
    for owner in (previous_run, run_dir):
        run = delivery.load_json(owner / "run.json")
        run["change_plan"] = change_plan
        delivery.write_json(owner / "run.json", run)
        # The plan is part of the retained v1 identity, so renew this explicit
        # fixture pin only after its complete source bytes are written.
        _trust_legacy_observed_fixture(owner, card)
    (previous_run / "phase-events.jsonl").write_text(
        "\n".join(
            json.dumps(event)
            for event in (
                {
                    "at": "2026-09-04T00:00:00Z",
                    "phase": "change-1",
                    "stage": "starting",
                },
                {
                    "at": "2026-09-04T00:01:00Z",
                    "phase": "change-1",
                    "stage": "complete",
                },
                {
                    "at": "2026-09-04T00:02:00Z",
                    "phase": "change-2",
                    "stage": "starting",
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )
    delivery.write_json(
        previous_run / "focused-evidence" / "01-green.json",
        {
            "label": "green",
            "command": "true",
            "exit_code": 0,
            "duration_seconds": 0.1,
            "fingerprint": current_fingerprint,
            "log": ".runtime/changerail/runs/previous/focused-evidence/01-green.log",
        },
    )
    delivery.write_json(
        previous_run / "reviews" / "cycle-00.json",
        {"workspace": current_fingerprint, "result": "go"},
    )
    delivery.write_json(
        previous_run / "reviews" / "cycle-00-manifest.json",
        {"fingerprint": current_fingerprint},
    )

    context_path = delivery.build_recovery_context(
        run_dir=run_dir, previous_run=previous_run, objective="resume exact payload"
    )
    context = delivery.load_json(context_path)

    assert context["previous_completed_review"] is None
    assert context["retained_focused_evidence"][0]["matches_current_payload"] is True
    assert context["payload_paths"] == ["tracked.txt"]
    assert [item["status"] for item in context["change_checkpoints"]] == [
        "complete",
        "started",
    ]
    assert context["next_change_event"] == {
        "phase": "change-2",
        "stage": "complete",
    }
    assert len(context["inherited_change_events"]) == 3
    assert context["resume_strategy"] == "resume_retained_thread"


def test_first_semantic_no_go_recovery_resumes_retained_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = _recovery_card_baseline(root)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    fingerprint = delivery.payload_fingerprint()
    previous_run = root / ".runtime" / "changerail" / "runs" / "previous"
    current_run = root / ".runtime" / "changerail" / "runs" / "current"
    reviews = previous_run / "reviews"
    session = previous_run / "sessions" / "implementation"
    reviews.mkdir(parents=True)
    session.mkdir(parents=True)
    current_run.mkdir(parents=True)
    _anchor_exact_legacy_recovery_source(previous_run, card)
    _copy_exact_legacy_recovery_source(previous_run, current_run, card)
    delivery.write_json(
        session / "session.json",
        {
            "role": "implementation",
            "started_at": "2026-09-04T00:00:00Z",
            "finished_at": "2026-09-04T00:01:00Z",
            "duration_seconds": 60,
            "exit_code": 0,
        },
    )
    (session / "events.jsonl").write_text(
        json.dumps(
            {
                "observed_at": "2026-09-04T00:00:00Z",
                "event": {"type": "thread.started", "thread_id": "thread-1"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = {
        "fingerprint": fingerprint,
        "path_fingerprints": delivery.path_fingerprints(["tracked.txt"]),
    }
    delivery.write_json(reviews / "cycle-01-manifest.json", manifest)
    delivery.write_json(
        reviews / "cycle-01.json", {"workspace": fingerprint, "result": "no-go"}
    )
    delivery.write_json(
        reviews / "cycle-01-context.json", {"review_reason": "semantic"}
    )

    context = delivery.load_json(
        delivery.build_recovery_context(
            run_dir=current_run,
            previous_run=previous_run,
            objective="repair the first semantic finding",
        )
    )

    assert context["resume_strategy"] == "resume_retained_thread"
    assert "terminal_review_pending" not in context
    assert context["resumed_thread_id"] == "thread-1"
    assert context["inherited_review_budget"]["semantic_cycles"] == 1


def test_review_budget_usage_accumulates_across_recovery_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    run_dir = root / ".runtime" / "changerail" / "runs" / "recovery"
    reviews = run_dir / "reviews"
    reviews.mkdir(parents=True)
    delivery.write_json(
        run_dir / "recovery-context.json",
        {
            "inherited_review_budget": {
                "semantic_cycles": 1,
                "terminal_semantic_repair_reviews": 0,
                "post_verification_repair_reviews": 0,
            }
        },
    )
    delivery.write_json(reviews / "cycle-01.json", {"result": "no-go"})
    delivery.write_json(
        reviews / "cycle-01-context.json", {"review_reason": "semantic"}
    )

    assert delivery.review_budget_usage(run_dir) == {
        "semantic_cycles": 2,
    }


def test_recovery_resumes_thread_and_inherits_only_investigative_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    previous_run = root / ".runtime" / "changerail" / "runs" / "previous"
    session = previous_run / "sessions" / "implementation"
    session.mkdir(parents=True)
    delivery.write_json(
        session / "session.json",
        {
            "session": "implementation",
            "role": "implementation",
            "started_at": "2026-09-04T00:00:00Z",
            "finished_at": "2026-09-04T00:01:00Z",
            "duration_seconds": 60,
            "exit_code": -9,
            "stop_reason": "command_safety_stop",
        },
    )
    events = [
        {
            "observed_at": "2026-09-04T00:00:00Z",
            "event": {"type": "thread.started", "thread_id": "thread-1"},
        }
    ]
    for index, command in enumerate(
        (
            "./bin/chrl event do starting",
            "./bin/chrl event change-1 starting",
            *(f"bounded read {number}" for number in range(1, 8)),
        ),
        start=1,
    ):
        traits = delivery._command_traits(command)
        events.append(
            {
                "observed_at": f"2026-09-04T00:00:{index:02d}Z",
                "event": {
                    "type": "item.started",
                    "item": {
                        "id": f"item-{index}",
                        "type": "command_execution",
                        "command_fingerprint": f"sha256:{index:064x}",
                        "command_traits": traits,
                    },
                },
            }
        )
    (session / "events.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in events), encoding="utf-8"
    )
    board_only = {
        "paths": [
            f"{FIXTURE_BOARD}/2.todo/test.md",
            f"{FIXTURE_BOARD}/3.inprogress/test.md",
        ]
    }

    assert delivery.recovery_implementation_state(previous_run, board_only) == (
        "thread-1",
        True,
        7,
    )
    assert delivery.recovery_implementation_state(
        previous_run, {"paths": [*board_only["paths"], "src/feature.py"]}
    ) == ("thread-1", False, 0)


def test_implementation_handoff_freezes_current_preverified_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(_card_text(), encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    _legacy_observed_anchor(run_dir, card)
    manifest_file = root / ".runtime" / "changerail" / "manifest.json"
    paths = delivery.changed_paths()
    fingerprint = delivery.payload_fingerprint(paths)
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": run_dir.name,
        "baseline_head": fingerprint["head_commit"],
        "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        "path_fingerprints": delivery.path_fingerprints(paths),
        "fingerprint": fingerprint,
        "paths": paths,
    }
    delivery.write_json(manifest_file, manifest)
    delivery.write_json(run_dir / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run_dir, card)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    monkeypatch.setattr(delivery, "preverify", lambda value: 0)
    monkeypatch.setattr(delivery, "capture_manifest", lambda value: manifest)
    monkeypatch.setattr(delivery, "manifest_path", lambda identifier: manifest_file)
    timestamps = iter(("2026-09-04T00:00:00Z", "2026-09-04T00:00:01Z"))
    monkeypatch.setattr(delivery, "utc_now", lambda: next(timestamps))
    monkeypatch.setattr(
        delivery,
        "require_current_successful_preverification",
        lambda *args, **kwargs: {},
    )

    assert delivery.implementation_handoff(str(card)) == 0
    payload = delivery.require_current_implementation_handoff(card, run_dir)

    assert payload["schema"] == "changerail.implementation-handoff.v1"
    assert payload["fingerprint"] == fingerprint
    assert payload["kind"] == "implementation"
    assert delivery.implementation_handoff(str(card)) == 0
    assert len(list((run_dir / "implementation-handoffs").glob("handoff-*.json"))) == 1


def test_implementation_handoff_retries_after_safe_deterministic_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = root / "openspec" / "board" / "3.inprogress" / "test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text(), encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    _legacy_observed_anchor(run_dir, card)
    manifest_file = root / ".runtime" / "changerail" / "manifest.json"
    paths = delivery.changed_paths()
    fingerprint = delivery.payload_fingerprint(paths)
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": run_dir.name,
        "baseline_head": fingerprint["head_commit"],
        "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        "path_fingerprints": delivery.path_fingerprints(paths),
        "fingerprint": fingerprint,
        "paths": paths,
    }
    delivery.write_json(manifest_file, manifest)
    delivery.write_json(run_dir / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run_dir, card)
    preverify_results = iter((1, 0, 0))
    observed_repairs: list[Path] = []

    def fake_safe_repair(value: Path) -> bool:
        observed_repairs.append(value)
        return True

    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    monkeypatch.setattr(delivery, "preverify", lambda value: next(preverify_results))
    monkeypatch.setattr(delivery, "run_safe_handoff_repair", fake_safe_repair)
    monkeypatch.setattr(delivery, "capture_manifest", lambda value: manifest)
    monkeypatch.setattr(delivery, "manifest_path", lambda identifier: manifest_file)

    assert delivery.implementation_handoff(str(card)) == 1
    assert not (run_dir / "implementation-handoff.json").exists()
    assert delivery.implementation_handoff(str(card)) == 0
    assert observed_repairs == [run_dir]
    assert (run_dir / "implementation-handoff.json").is_file()


def test_failed_handoff_reports_authoritative_retry_action(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repository(tmp_path, monkeypatch)
    card = root / "openspec" / "board" / "3.inprogress" / "test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text(), encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    _legacy_observed_anchor(run_dir, card)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    monkeypatch.setattr(delivery, "preverify", lambda value: 1)
    monkeypatch.setattr(delivery, "run_safe_handoff_repair", lambda value: False)

    assert delivery.implementation_handoff(str(card)) == 1
    failure = json.loads(capsys.readouterr().err)
    assert failure["status"] == "failed"
    assert failure["artifact_written"] is False
    assert "do not report success" in failure["action"]
    assert not (run_dir / "implementation-handoff.json").exists()


def test_safe_handoff_repair_is_scoped_to_changed_python_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    source = root / "src" / "sample.py"
    source.parent.mkdir(parents=True)
    source.write_text("import sys\nimport os\n", encoding="utf-8")
    (root / "notes.txt").write_text("not Python\n", encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    delivery.write_json(
        run_dir / "preverification.json",
        {
            "commands": [
                {"command": "git diff --check", "exit_code": 0},
                {"command": "uv run ruff check src tests", "exit_code": 1},
            ]
        },
    )
    observed: list[str] = []

    def fake_run(command: str, log: Path) -> dict[str, object]:
        observed.append(command)
        source.write_text("import os\nimport sys\n", encoding="utf-8")
        log.write_text("Found 1 error (1 fixed).\n", encoding="utf-8")
        return {
            "command": command,
            "exit_code": 0,
            "duration_seconds": 0.01,
            "log": delivery.repo_relative(log),
        }

    monkeypatch.setattr(delivery, "run_shell_verification", fake_run)

    assert delivery.run_safe_handoff_repair(run_dir) is True
    assert observed == ["uv run ruff check --fix --select I -- src/sample.py"]
    repair = delivery.load_json(run_dir / "deterministic-repair.json")
    assert repair["kind"] == "safe_import_sorting"
    assert repair["paths"] == ["src/sample.py"]
    assert repair["changed_payload"] is True
    assert delivery.deterministic_commands(run_dir)[0]["source"] == (
        "deterministic-handoff-repair"
    )


def test_finalize_card_moves_once_without_rewriting_result_or_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch
    )
    done = root / "openspec" / "board" / "4.done"
    done.mkdir(parents=True)
    # The finalizer assertions stay real; its receipt now needs real final proof.
    assert delivery.verify(str(card)) == 0
    verification = _final_check_set(card, run_dir, commands)
    original_result = delivery.section_body(card.read_text(), "Result")
    original_log = delivery.section_body(card.read_text(), "Log")
    receipt = delivery.delivery_receipt_lines(
        verdict={"reviewed_at": "2026-09-02T00:01:00Z"},
        verification=verification,
        run_dir=run_dir,
        finalized_at="2026-09-02T00:03:00Z",
    )

    destination = delivery.finalize_card(card, receipt=receipt)

    assert destination == done / "test-card.md"
    assert not card.exists()
    text = destination.read_text(encoding="utf-8")
    assert "## Status\n4.done" in text
    assert delivery.section_body(text, "Result") == original_result
    assert (
        "\n".join(delivery.section_body(text, "Log")).rstrip()
        == "\n".join(original_log).rstrip()
    )
    assert "## Delivery Receipt" in text
    assert "Final repository verification: `passed`" in text
    assert "Pytest:" not in text
    with pytest.raises(delivery.DeliveryError, match="current validated final"):
        delivery.delivery_receipt_lines(
            verdict={"reviewed_at": "2026-09-02T00:01:00Z"},
            verification=verification,
            run_dir=run_dir,
            finalized_at="2026-09-02T00:03:00Z",
        )


def test_final_verify_runs_final_floor_once_after_matching_preverification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )

    assert delivery.preverify(str(card)) == 0
    assert delivery.preverify(str(card)) == 0
    _allow_final_verification(monkeypatch)
    assert delivery.verify(str(card)) == 0

    assert observed == ["quick-one", "quick-two", "check-one", "check-two"]
    assert len(list((run_dir / "preverification").glob("cycle-*"))) == 1
    assert len(list((run_dir / "verification").glob("cycle-*"))) == 1
    final = delivery.load_json(run_dir / "verification.json")
    assert final["configured_commands"] == ["check-one", "check-two"]
    assert final["fingerprint"] == delivery.payload_fingerprint()


def test_final_verify_fails_closed_after_payload_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )

    assert delivery.preverify(str(card)) == 0
    preverified = delivery.load_json(run_dir / "preverification.json")
    (root / "tracked.txt").write_text("changed after preverify\n", encoding="utf-8")
    _allow_final_verification(monkeypatch)
    with pytest.raises(delivery.DeliveryError, match="current successful"):
        delivery.verify(str(card))

    assert observed == ["quick-one", "quick-two"]
    assert not (run_dir / "verification.json").exists()
    assert preverified["fingerprint"] != delivery.payload_fingerprint()


def test_final_verify_fails_closed_for_changed_verification_command_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, run_dir, configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )

    assert delivery.preverify(str(card)) == 0
    configured["pre_review_commands"] = ["quick-two", "quick-three"]
    _allow_final_verification(monkeypatch)
    with pytest.raises(delivery.DeliveryError, match="configured command set"):
        delivery.verify(str(card))

    assert observed == ["quick-one", "quick-two"]
    assert not (run_dir / "verification.json").exists()


def test_final_verify_fails_closed_without_preverification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    _allow_final_verification(monkeypatch)

    with pytest.raises(delivery.DeliveryError, match="successful preverification"):
        delivery.verify(str(card))

    assert observed == []
    assert not (run_dir / "verification.json").exists()


@pytest.mark.parametrize("placeholder", ("implementation in progress", "", "TBD"))
def test_preverify_rejects_provisional_result_without_running_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, placeholder: str
) -> None:
    _root, card, _run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    card.write_text(
        card.read_text(encoding="utf-8").replace(
            "implemented observable result", placeholder
        ),
        encoding="utf-8",
    )

    with pytest.raises(delivery.DeliveryError, match="substantive Result"):
        delivery.preverify(str(card))

    assert observed == []


def test_preverify_rejects_empty_log_without_running_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, _run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    card.write_text(
        card.read_text(encoding="utf-8").replace("- 2026-09-02T00:00:00Z started", ""),
        encoding="utf-8",
    )

    with pytest.raises(delivery.DeliveryError, match="substantive Log"):
        delivery.preverify(str(card))

    assert observed == []


def test_preverify_rejects_missing_next_section_without_running_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, _run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    card.write_text(
        card.read_text(encoding="utf-8").replace("\n## Next\n- verify\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(
        delivery.DeliveryError, match="preserved card sections: ## Next"
    ):
        delivery.preverify(str(card))

    assert observed == []


def test_preverify_rejects_future_card_log_timestamp_without_running_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, _run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    card.write_text(
        card.read_text(encoding="utf-8").replace(
            "2026-09-02T00:00:00Z", "2999-09-02T00:00:00Z"
        ),
        encoding="utf-8",
    )

    with pytest.raises(delivery.DeliveryError, match="future card Log timestamps"):
        delivery.preverify(str(card))

    assert observed == []


def test_preverify_cli_does_not_require_go(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, card, run_dir, _configured, observed = _verification_fixture(
        tmp_path, monkeypatch
    )
    monkeypatch.setattr(
        delivery,
        "validate_verdict",
        lambda value: pytest.fail("preverify must not validate a GO verdict"),
    )

    assert delivery.main(["preverify", str(card)]) == 0
    assert observed == ["quick-one", "quick-two"]
    assert (run_dir / "preverification.json").is_file()


def test_rewrite_active_board_references_updates_only_live_columns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    todo_source = f"{FIXTURE_BOARD}/2.todo/test-card.md"
    active_source = f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    destination = f"{FIXTURE_BOARD}/4.done/test-card.md"
    backlog = root / "openspec" / "board" / "1.backlog" / "epic.md"
    todo = root / "openspec" / "board" / "2.todo" / "next.md"
    canceled = root / "openspec" / "board" / "5.canceled" / "history.md"
    for path, source in (
        (backlog, todo_source),
        (todo, active_source),
        (canceled, todo_source),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"- `{source}`\n", encoding="utf-8")

    changed = delivery.rewrite_active_board_references("test-card.md", destination)

    assert changed == [
        f"{FIXTURE_BOARD}/1.backlog/epic.md",
        f"{FIXTURE_BOARD}/2.todo/next.md",
    ]
    assert destination in backlog.read_text(encoding="utf-8")
    assert destination in todo.read_text(encoding="utf-8")
    assert todo_source in canceled.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "relative", ["src/product.py", "tests/test_product.py", "docs/example.md"]
)
def test_live_board_reference_check_covers_product_paths_outside_openspec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    root = _repository(tmp_path, monkeypatch)
    source = root / relative
    source.parent.mkdir()
    source.write_text(
        f'CARD = "{FIXTURE_BOARD}/2.todo/missing-card.md"\n', encoding="utf-8"
    )

    before = source.read_bytes()
    with pytest.raises(delivery.DeliveryError, match="missing-card.md"):
        delivery.require_live_board_references([relative])
    # A real reference stays checked even inside tests; no tests/ exemption.
    target = root / FIXTURE_BOARD / "2.todo" / "missing-card.md"
    target.parent.mkdir(parents=True)
    target.write_text(_card_text(), encoding="utf-8")
    delivery.require_live_board_references([relative])
    target.unlink()
    with pytest.raises(delivery.DeliveryError, match="missing-card.md"):
        delivery.require_live_board_references([relative])
    assert source.read_bytes() == before


def test_live_board_reference_fixture_construction_does_not_hide_real_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    source = root / "tests" / "test_fixture.py"
    source.parent.mkdir()
    # The outer checkout sees construction, the isolated fixture sees the
    # original literal value. A real literal alongside it must still be checked.
    fixture_text = 'FIXTURE_BOARD = "openspec/board"\nCARD = f"{FIXTURE_BOARD}/2.todo/synthetic.md"\n'
    source.write_text(fixture_text, encoding="utf-8")
    delivery.require_live_board_references(["tests/test_fixture.py"])
    namespace: dict[str, object] = {}
    exec(compile(fixture_text, str(source), "exec"), namespace)
    assert namespace["CARD"] == f"{FIXTURE_BOARD}/2.todo/synthetic.md"
    real_reference = f"{FIXTURE_BOARD}/2.todo/real-link.md"
    source.write_text(
        fixture_text + f'REAL_CARD = "{real_reference}"\n', encoding="utf-8"
    )
    assert delivery.dangling_live_board_references(["tests/test_fixture.py"]) == [
        {"source": "tests/test_fixture.py", "reference": real_reference}
    ]
    with pytest.raises(delivery.DeliveryError, match="real-link.md"):
        delivery.require_live_board_references(["tests/test_fixture.py"])
    target = root / real_reference
    target.parent.mkdir(parents=True)
    target.write_text(_card_text(), encoding="utf-8")
    delivery.require_live_board_references(["tests/test_fixture.py"])


def test_live_board_reference_check_allows_current_todo_transition_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress" / "current-card.md"
    active.parent.mkdir(parents=True)
    active.write_text(_card_text(), encoding="utf-8")
    source = root / "src" / "product.py"
    source.parent.mkdir()
    source.write_text(
        f'CARD = "{FIXTURE_BOARD}/2.todo/current-card.md"\n', encoding="utf-8"
    )

    delivery.require_live_board_references(["src/product.py"])


def test_metrics_separate_agent_and_deterministic_commands(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run-1"
    card = tmp_path / f"{FIXTURE_BOARD}/2.todo/test.md"
    card.parent.mkdir(parents=True)
    card.write_text("legacy metric fixture")
    session = run_dir / "sessions" / "implementation"
    session.mkdir(parents=True)
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": "run-1",
            "card": f"{FIXTURE_BOARD}/2.todo/test.md",
            "started_at": "2026-09-02T00:00:00Z",
            "execution_contract": "changerail.native.v1",
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": [{"number": 1, "slug": "bounded-change"}],
        },
    )
    delivery.write_json(
        session / "session.json",
        {
            "session": "implementation",
            "role": "implementation",
            "model": "gpt-5.6-terra",
            "reasoning_effort": "high",
            "model_evidence": {
                "model": "gpt-5.6-terra",
                "reasoning_effort": "high",
                "source": "explicit_codex_cli_arguments",
            },
            "started_at": "2026-09-02T00:00:00Z",
            "finished_at": "2026-09-02T00:01:00Z",
            "duration_seconds": 60,
            "exit_code": 0,
        },
    )
    events = [
        {
            "observed_at": "2026-09-02T00:00:00Z",
            "event": {"type": "thread.started", "thread_id": "thread-1"},
        },
        {
            "observed_at": "2026-09-02T00:00:01Z",
            "event": {
                "type": "item.started",
                "item": {
                    "id": "command-1",
                    "type": "command_execution",
                    "command": "./bin/chrl preverify card.md",
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:02Z",
            "event": {
                "type": "item.completed",
                "item": {
                    "id": "command-1",
                    "type": "command_execution",
                    "command": "./bin/chrl preverify card.md",
                    "exit_code": 0,
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:03Z",
            "event": {
                "type": "item.started",
                "item": {
                    "id": "command-2",
                    "type": "command_execution",
                    "command": (
                        "./bin/chrl evidence --label focused -- "
                        "uv run pytest -q tests/test_feature.py"
                    ),
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:04Z",
            "event": {
                "type": "item.completed",
                "item": {
                    "id": "command-2",
                    "type": "command_execution",
                    "command": (
                        "./bin/chrl evidence --label focused -- "
                        "uv run pytest -q tests/test_feature.py"
                    ),
                    "exit_code": 0,
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:05Z",
            "event": {
                "type": "item.completed",
                "item": {"id": "change-1", "type": "file_change"},
            },
        },
        {
            "observed_at": "2026-09-02T00:01:00Z",
            "event": {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 80,
                    "output_tokens": 10,
                    "reasoning_output_tokens": 4,
                },
            },
        },
    ]
    (session / "events.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in events), encoding="utf-8"
    )
    (run_dir / "phase-events.jsonl").write_text(
        "\n".join(
            json.dumps(event)
            for event in (
                {
                    "at": "2026-09-02T00:00:10Z",
                    "phase": "change-1",
                    "stage": "starting",
                },
                {
                    "at": "2026-09-02T00:00:20Z",
                    "phase": "change-1",
                    "stage": "complete",
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )
    evidence = run_dir / "focused-evidence"
    evidence.mkdir()
    delivery.write_json(
        evidence / "01-focused.json",
        {
            "command": "uv run pytest -q tests/test_feature.py",
            "exit_code": 0,
            "duration_seconds": 1.5,
            "observed_at": "2026-09-02T00:00:30Z",
        },
    )
    preverification = run_dir / "preverification" / "cycle-01"
    preverification.mkdir(parents=True)
    delivery.write_json(
        preverification / "preverification.json",
        {
            "commands": [
                {
                    "command": "uv run ruff check src tests",
                    "exit_code": 0,
                    "duration_seconds": 0.5,
                    "log": "verification.log",
                }
            ]
        },
    )
    verification = run_dir / "verification" / "cycle-01"
    verification.mkdir(parents=True)
    delivery.write_json(
        verification / "verification.json",
        {
            "commands": [
                {
                    "command": "uv run pytest -q",
                    "exit_code": 0,
                    "duration_seconds": 12.0,
                    "log": "verification.log",
                }
            ],
        },
    )

    metrics = delivery.build_metrics(run_dir)

    assert metrics["usage"]["uncached_input_tokens"] == 20
    assert metrics["model_routes"] == [
        {
            "session": "implementation",
            "role": "implementation",
            "model": "gpt-5.6-terra",
            "reasoning_effort": "high",
            "review_reason": None,
            "source": "explicit_codex_cli_arguments",
        }
    ]
    assert metrics["command_count"] == 2
    assert metrics["agent_command_count"] == 2
    assert metrics["deterministic_command_count"] == 3
    assert metrics["command_observation_count"] == 5
    assert metrics["execution_command_count"] == 3
    assert metrics["pytest_command_count"] == 2
    assert metrics["full_pytest_command_count"] == 1
    assert metrics["review_attempt_count"] == 0
    assert metrics["review_cycle_count"] == 0
    assert metrics["change_checkpoints"] == [
        {
            "number": 1,
            "slug": "bounded-change",
            "status": "complete",
            "started_at": "2026-09-02T00:00:10Z",
            "completed_at": "2026-09-02T00:00:20Z",
            "duration_seconds": 10.0,
        }
    ]
    assert metrics["sessions"][0]["thread_id"] == "thread-1"
    assert metrics["sessions"][0]["commands_before_first_file_change"] == 2
    assert (
        metrics["sessions"][0]["investigative_commands_before_first_file_change"] == 2
    )
    assert metrics["usage_status"] == "complete"
    assert metrics["timing"] == {
        "run_wall_seconds": 60.0,
        "session_wall_seconds": 60.0,
        "raw_session_wall_seconds": 60.0,
        "overlapping_session_seconds": 0.0,
        "agent_shell_command_seconds": 2.0,
        "deterministic_check_seconds": 14.0,
        "model_api_non_command_seconds": 58.0,
        "review_wrapper_wait_seconds": 0,
        "orchestration_outside_sessions_seconds": 0.0,
        "deterministic_check_seconds_are_nested_in_session_wall": True,
    }
    assert metrics["duplicate_review_invocation_count"] == 0
    assert metrics["budget_observations"][0] == {
        "role": "implementation",
        "metric": "investigative_commands_before_first_file_change",
        "budget": 8,
        "observed": 2,
        "exceeded": False,
        "verdict_only_budget": None,
        "verdict_only_entered": False,
        "hard_stop_budget": 12,
        "hard_stop_exceeded": False,
    }


def test_metrics_union_nested_review_and_duplicate_wrapper_intervals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run"
    for name in ("implementation", "review-01"):
        (run_dir / "sessions" / name).mkdir(parents=True)
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": "run-1",
            "card": f"{FIXTURE_BOARD}/3.inprogress/test.md",
            "started_at": "2026-09-02T00:00:00Z",
            "finished_at": "2026-09-02T00:01:00Z",
            "duration_seconds": 60,
        },
    )
    review_command = f"./bin/chrl review {FIXTURE_BOARD}/3.inprogress/test.md"
    common = {
        "usage": {
            "input_tokens": None,
            "cached_input_tokens": None,
            "output_tokens": None,
            "reasoning_output_tokens": None,
            "uncached_input_tokens": None,
        },
        "usage_complete": False,
        "usage_status": "unknown",
        "stop_reason": "completed",
        "model_evidence": {},
    }
    sessions = {
        "implementation": {
            **common,
            "session": "implementation",
            "role": "implementation",
            "started_at": "2026-09-02T00:00:00Z",
            "timing": {"session_wall_seconds": 60.0},
            "commands": [
                {
                    "command": review_command,
                    "command_traits": {"review_wrapper": True},
                    "started_at": started,
                    "duration_seconds": duration,
                    "exit_code": 0,
                }
                for started, duration in (
                    ("2026-09-02T00:00:10Z", 20.0),
                    ("2026-09-02T00:00:15Z", 15.0),
                )
            ],
        },
        "review-01": {
            **common,
            "session": "review-01",
            "role": "review",
            "started_at": "2026-09-02T00:00:10Z",
            "timing": {"session_wall_seconds": 20.0},
            "commands": [
                {
                    "command": "bounded read",
                    "command_traits": {},
                    "started_at": "2026-09-02T00:00:11Z",
                    "duration_seconds": 2.0,
                    "exit_code": 0,
                }
            ],
        },
    }
    monkeypatch.setattr(
        delivery, "parse_session_metrics", lambda path: sessions[path.name]
    )

    metrics = delivery.build_metrics(run_dir)

    assert metrics["timing"]["raw_session_wall_seconds"] == 80.0
    assert metrics["timing"]["session_wall_seconds"] == 60.0
    assert metrics["timing"]["overlapping_session_seconds"] == 20.0
    assert metrics["timing"]["review_wrapper_wait_seconds"] == 20.0
    assert metrics["timing"]["agent_shell_command_seconds"] == 2.0
    assert metrics["timing"]["model_api_non_command_seconds"] == 58.0
    assert metrics["duplicate_review_invocation_count"] == 1


def test_metrics_do_not_double_count_failed_evidence_wrapper(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run"
    session = run_dir / "sessions" / "implementation"
    session.mkdir(parents=True)
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": "run-1",
            "card": f"{FIXTURE_BOARD}/2.todo/test.md",
            "started_at": "2026-09-02T00:00:00Z",
        },
    )
    delivery.write_json(
        session / "session.json",
        {
            "role": "implementation",
            "model": "gpt-6-astra",
            "reasoning_effort": "high",
            "started_at": "2026-09-02T00:00:00Z",
            "finished_at": "2026-09-02T00:01:00Z",
            "duration_seconds": 60,
            "exit_code": 0,
        },
    )
    command = (
        "./bin/chrl evidence --label focused -- uv run pytest -q tests/test_feature.py"
    )
    events = [
        {
            "observed_at": "2026-09-02T00:00:01Z",
            "event": {
                "type": "item.started",
                "item": {
                    "id": "command-1",
                    "type": "command_execution",
                    "command": command,
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:02Z",
            "event": {
                "type": "item.completed",
                "item": {
                    "id": "command-1",
                    "type": "command_execution",
                    "command": command,
                    "exit_code": 1,
                },
            },
        },
    ]
    (session / "events.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in events), encoding="utf-8"
    )
    evidence = run_dir / "focused-evidence"
    evidence.mkdir()
    delivery.write_json(
        evidence / "01-focused.json",
        {
            "command": "uv run pytest -q tests/test_feature.py",
            "exit_code": 1,
            "duration_seconds": 1.5,
            "observed_at": "2026-09-02T00:00:02Z",
        },
    )

    metrics = delivery.build_metrics(run_dir)

    assert metrics["failed_command_count"] == 1
    assert metrics["deterministic_failed_command_count"] == 1
    assert metrics["failed_command_observation_count"] == 2
    assert metrics["pytest_command_count"] == 1


def test_incomplete_session_retains_partial_usage_and_unfinished_command_time(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run"
    session = run_dir / "sessions" / "review-01"
    session.mkdir(parents=True)
    delivery.write_json(
        run_dir / "run.json",
        {
            "run_id": "run-1",
            "card": f"{FIXTURE_BOARD}/3.inprogress/test.md",
            "started_at": "2026-09-02T00:00:00Z",
            "finished_at": "2026-09-02T00:00:10Z",
        },
    )
    delivery.write_json(
        session / "session.json",
        {
            "role": "review",
            "started_at": "2026-09-02T00:00:00Z",
            "finished_at": "2026-09-02T00:00:10Z",
            "duration_seconds": 10,
            "exit_code": 1,
            "stop_reason": "nonzero_exit",
        },
    )
    events = [
        {
            "observed_at": "2026-09-02T00:00:02Z",
            "observed_elapsed_seconds": 2.0,
            "event": {
                "type": "item.started",
                "item": {
                    "id": "command-1",
                    "type": "command_execution",
                    "command": "bounded read",
                },
            },
        },
        {
            "observed_at": "2026-09-02T00:00:08Z",
            "observed_elapsed_seconds": 8.0,
            "event": {
                "type": "turn.failed",
                "usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 80,
                    "output_tokens": 10,
                    "reasoning_output_tokens": 4,
                },
            },
        },
    ]
    (session / "events.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in events), encoding="utf-8"
    )

    metrics = delivery.build_metrics(run_dir)

    assert metrics["usage_status"] == "partial"
    assert metrics["usage"]["input_tokens"] is None
    assert metrics["usage_observed_lower_bound"]["uncached_input_tokens"] == 20
    assert metrics["sessions"][0]["usage_status"] == "partial"
    assert metrics["sessions"][0]["commands"][0]["completed"] is False
    assert metrics["sessions"][0]["commands"][0]["duration_seconds"] == 8.0
    assert metrics["stop_reason_counts"] == {"nonzero_exit": 1}
    assert metrics["timing"]["model_api_non_command_seconds"] == 2.0


@pytest.mark.parametrize(("role", "budget"), (("implementation", 8), ("review", 12)))
def test_codex_session_allows_shell_command_budget_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    role: str,
    budget: int,
) -> None:
    run_dir, process = _launch_with_command_count(
        tmp_path, monkeypatch, role=role, command_count=budget
    )

    assert (
        delivery.launch_codex(
            role=role,
            prompt="test",
            model="gpt-test",
            reasoning="high",
            run_dir=run_dir,
            timeout_minutes=1,
        )
        == 0
    )

    session_name = "implementation" if role == "implementation" else "review-01"
    assert process.terminated is False
    assert process.popen_kwargs["start_new_session"] is True
    session = delivery.load_json(run_dir / "sessions" / session_name / "session.json")
    assert session["model_evidence"] == {
        "model": "gpt-test",
        "reasoning_effort": "high",
        "source": "explicit_codex_cli_arguments",
    }
    assert session["stop_reason"] == "completed"
    assert not (run_dir / "sessions" / session_name / "budget-violation.json").exists()


def test_review_enters_verdict_only_without_killing_a_useful_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir, process = _launch_with_command_count(
        tmp_path, monkeypatch, role="review", command_count=20
    )
    expected_verdict = tmp_path / "missing-verdict.json"

    assert (
        delivery.launch_codex(
            role="review",
            prompt="test",
            model="gpt-test",
            reasoning="high",
            run_dir=run_dir,
            timeout_minutes=1,
            expected_artifact=expected_verdict,
        )
        == 0
    )

    session_dir = run_dir / "sessions" / "review-01"
    session = delivery.load_json(session_dir / "session.json")
    notice = delivery.load_json(session_dir / "verdict-only.json")
    assert process.terminated is False
    assert notice["observed_investigative_commands"] == 20
    assert notice["hard_stop"] == 24
    assert session["command_budget"]["verdict_only_entered"] is True
    assert session["stop_reason"] == "incomplete_review_no_verdict"


def test_recovery_session_does_not_require_a_new_file_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir, process = _launch_with_command_count(
        tmp_path, monkeypatch, role="implementation", command_count=9
    )

    assert (
        delivery.launch_codex(
            role="implementation",
            prompt="recovery",
            model="gpt-test",
            reasoning="high",
            run_dir=run_dir,
            timeout_minutes=1,
            session_env={"CHRL_RECOVERY_RUN": "1"},
        )
        == 0
    )

    session_dir = run_dir / "sessions" / "implementation"
    assert process.terminated is False
    assert delivery.load_json(session_dir / "session.json")["recovery"] is True
    assert not (session_dir / "budget-violation.json").exists()
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    assert delivery.build_metrics(run_dir)["budget_observations"] == []


def test_technical_capacity_recovery_dispatches_one_pending_successor(
    project, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The worker is mocked; prepare/apply and retained recovery state are real."""
    from scripts.changerail import local_delivery as d
    from scripts.changerail import native_workflow as flow
    from scripts.changerail import technical_recovery as recovery
    from tools.changerail.tests.test_technical_recovery import _files, _origin

    _root, card, origin = _origin(project, monkeypatch)
    before = _files(origin)
    checkpoints = d.change_checkpoint_statuses(
        d.declared_change_plan(origin) or [], d.combined_change_events(origin)
    )
    session = origin / "sessions/failed-group-2"
    assert [row["status"] for row in checkpoints] == ["complete", "pending"]
    assert (origin / "focused-evidence/completed-group.json").is_file()
    assert recovery.classify_session(d, session)["failure_class"] == "model_capacity"
    calls: list[dict[str, object]] = []

    def launch(_delivery, **kwargs) -> None:
        calls.append(kwargs)

    def execute(**kwargs) -> int:
        kwargs["before_orchestrate"]()
        return 0

    monkeypatch.setattr(flow, "launch_groups", launch)
    monkeypatch.setattr(d, "execute_prepared_delivery", execute)
    prepared = recovery.prepare(d, origin)
    result = recovery.apply(d, origin, Path(prepared["proposal"]))
    successor = Path(result["successor"])

    assert result["state"] == "dispatched"
    assert _files(origin) == before
    assert d._check_json(successor / "run.json")["recovery_of"] == origin.name
    technical = d._check_json(successor / "run.json")["technical_recovery"]
    assert technical["schema"] == recovery.SCHEMA
    assert technical["proposal_sha256"].startswith("sha256:")
    assert technical["next_group"] == 2
    assert technical["fallback"] == {
        "model": "fallback-model",
        "reasoning_effort": "high",
    }
    assert len(calls) == 1
    assert calls[0]["only_group"] == 2
    assert calls[0]["model_route_name"] == "technical-recovery"
    assert recovery.apply(d, origin, Path(prepared["proposal"]))["successor"] == str(
        successor
    )
    assert len(calls) == 1


@pytest.mark.parametrize(
    ("role", "budget", "hard_stop"),
    (("implementation", 8, 12), ("review", 12, 24)),
)
def test_codex_session_terminates_on_next_shell_command_and_records_violation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    role: str,
    budget: int,
    hard_stop: int,
) -> None:
    run_dir, process = _launch_with_command_count(
        tmp_path, monkeypatch, role=role, command_count=hard_stop + 1
    )

    with pytest.raises(delivery.DeliveryError, match="shell command budget exceeded"):
        delivery.launch_codex(
            role=role,
            prompt="test",
            model="gpt-test",
            reasoning="high",
            run_dir=run_dir,
            timeout_minutes=1,
        )

    session_name = "implementation" if role == "implementation" else "review-01"
    session_dir = run_dir / "sessions" / session_name
    violation = delivery.load_json(session_dir / "budget-violation.json")
    assert process.terminated is True
    assert process.signals == [signal.SIGKILL]
    assert violation == {
        "schema": "changerail.command-budget-violation.v1",
        "role": role,
        "metric": (
            "investigative_commands_before_first_file_change"
            if role == "implementation"
            else "review_investigative_command_count"
        ),
        "budget": budget,
        "hard_stop_budget": hard_stop,
        "observed": hard_stop + 1,
        "command_id": f"command-{hard_stop + 1}",
        "item_type": "command_execution",
        "observed_at": violation["observed_at"],
    }
    assert delivery.load_json(session_dir / "session.json")["budget_violation"] == (
        violation
    )
    retained = (session_dir / "stdout.jsonl").read_text(encoding="utf-8") + (
        session_dir / "events.jsonl"
    ).read_text(encoding="utf-8")
    assert f"command {hard_stop + 1}" not in retained
    assert "sensitive-output" not in retained
    assert "command_fingerprint" in retained
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    assert delivery.build_metrics(run_dir)["budget_observations"] == [
        {
            "role": role,
            "metric": violation["metric"],
            "budget": budget,
            "observed": hard_stop + 1,
            "exceeded": True,
            "verdict_only_budget": 20 if role == "review" else None,
            "verdict_only_entered": role == "review",
            "hard_stop_budget": hard_stop,
            "hard_stop_exceeded": True,
        }
    ]
    metrics = delivery.build_metrics(run_dir)
    assert metrics["usage_complete"] is False
    assert metrics["usage_status"] == "unknown"
    assert metrics["usage"]["input_tokens"] is None
    assert delivery.load_json(session_dir / "session.json")["stop_reason"] == (
        "command_safety_stop"
    )


def test_codex_session_interrupt_is_finalized_as_delivery_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    run_dir = tmp_path / "run"
    delivery.write_json(
        run_dir / "run.json",
        {"run_id": "run-1", "card": "test-card.md", "started_at": "now"},
    )
    process = _InterruptedCodexProcess()

    def fake_popen(*args, **kwargs):
        del args
        process.popen_kwargs = kwargs
        return process

    def fake_killpg(pid: int, sent_signal: int) -> None:
        assert pid == process.pid
        if sent_signal == 0:
            # The observation after wait is not a termination signal.
            raise ProcessLookupError(pid)
        process.signals.append(sent_signal)

    monkeypatch.setattr(delivery.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(delivery.os, "killpg", fake_killpg)
    monkeypatch.setattr(delivery, "execution_env", lambda extra=None: dict(extra or {}))
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "budgets": {
                "first_edit_discovery_commands": 8,
                "review_commands": 12,
            }
        },
    )

    with pytest.raises(delivery.DeliveryError, match="interrupted"):
        delivery.launch_codex(
            role="implementation",
            prompt="test",
            model="gpt-test",
            reasoning="high",
            run_dir=run_dir,
            timeout_minutes=1,
        )

    session = delivery.load_json(
        run_dir / "sessions" / "implementation" / "session.json"
    )
    assert process.signals == [signal.SIGTERM]
    assert session["interrupted"] is True
    assert session["exit_code"] == -15
    assert session["stop_reason"] == "operator_interrupt"


def _configured_final_check_fixture(tmp_path, monkeypatch, commands=None):
    root, card, run = _review_fixture(tmp_path, monkeypatch)
    monkeypatch.setenv("CHRL_SESSION_ROLE", "outer")
    configured = ["printf stable", "true"] if commands is None else commands
    current = delivery.profile()
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            **current,
            "verification": {
                "pre_review_commands": ["true"],
                "final_commands": configured,
            },
        },
    )
    _write_matching_preverification(card, run)
    verdict = delivery.verdict_template(str(card))["template"]
    verdict["acceptance"][0]["evidence"] = ["owned fixture"]
    delivery.write_json(delivery.verdict_path(card.stem), verdict)
    return root, card, run, configured


def _refresh_exact_legacy_fixture(card: Path, run: Path) -> None:
    """Explicitly establish a new exact v1 source after fixture payload setup.

    The final-receipt tests below deliberately add a local pytest file before
    exercising the consumer.  This is setup for a new exact fixture source,
    not a production pin or an inference from absent version fields.
    """

    paths = delivery.changed_paths()
    manifest = delivery.load_json(delivery.manifest_path(card.stem))
    manifest.update(
        {
            "run_id": run.name,
            "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
            "card": {"id": card.stem, "path": delivery.repo_relative(card)},
            "paths": paths,
            "fingerprint": delivery.payload_fingerprint(paths),
            "path_fingerprints": delivery.path_fingerprints(paths),
        }
    )
    delivery.write_json(delivery.manifest_path(card.stem), manifest)
    delivery.write_json(run / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run, card)
    delivery.capture_manifest(str(card))
    _trust_legacy_observed_fixture(run, card)


@pytest.mark.parametrize("damage", ["missing-log", "drift"])
def test_configured_final_check_behavioral_regressions(tmp_path, monkeypatch, damage):
    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    counter = run / "count"
    commands[:] = (
        ["printf changed > tracked.txt", "printf 'first\\n' > tracked.txt"]
        if damage == "drift"
        else ["printf x >> " + str(counter), "true"]
    )
    code = delivery.verify(str(card))
    index = delivery.load_json(run / "verification.json")
    if damage == "drift":
        assert code == 1
        assert (root / "tracked.txt").read_bytes() == b"changed"
        assert len(index["commands"]) == 1
    else:
        assert code == 0 and counter.read_bytes() == b"x"
        (root / index["commands"][0]["log"]).unlink()
        assert delivery.verify(str(card)) == 0
        assert counter.read_bytes() == b"xx"


def _configured_pre_review_check_fixture(tmp_path, monkeypatch, commands=None):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    card.write_text(
        card.read_text().replace(
            "implementation in progress", "implemented observable result"
        )
    )
    configured = commands or ["printf stable", "true"]
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "verification": {
                "pre_review_commands": configured,
                "final_commands": configured,
            }
        },
    )
    return root, card, run, configured


def _singleflight_publication_gate(
    run: Path,
    result_name: str | None,
    gate: tuple[Path, Path, Path | None, Path | None] | None,
) -> str:
    """Inject observation-only fixture gates around real terminal publications."""
    if gate is None:
        return ""
    receipt_ready, receipt_release, index_ready, index_release = gate
    index = run / result_name if result_name is not None else None
    return (
        "original_finish=d.finish_check_result; original_write=d.write_json; "
        f"receipt_ready=Path({str(receipt_ready)!r}); receipt_release=Path({str(receipt_release)!r}); "
        f"index_ready={repr(str(index_ready))}; index_release={repr(str(index_release))}; "
        f"index_path={repr(str(index))}\n"
        "def pause(ready, release):\n"
        '    open(ready, "wb", buffering=0).write(b"P")\n'
        '    open(release, "rb", buffering=0).read(1)\n'
        "def gated_finish(path, item, output):\n"
        '    if os.environ.get("CHRL_FIXTURE_EARLY_UNLOCK") == "1":\n'
        "        active=next(iter(d._ACTIVE_VERIFICATION_LOCKS.values()))\n"
        "        d.fcntl.flock(active.fd, d.fcntl.LOCK_UN)\n"
        "    pause(receipt_ready, receipt_release)\n"
        "    return original_finish(path, item, output)\n"
        "def gated_write(path, value):\n"
        "    if index_path is not None and Path(path) == Path(index_path):\n"
        "        pause(Path(index_ready), Path(index_release))\n"
        "    return original_write(path, value)\n"
        "d.finish_check_result=gated_finish; d.write_json=gated_write; "
    )


def _delivery_child_bootstrap(root: Path, run: Path) -> str:
    """Load shared schemas and the generic profile before selecting fixture state.

    These component fixtures override project globals after import, just like
    the parent fixture. A fresh interpreter must not infer its import root from
    the temporary Git checkout or inherit a developer's CHRL environment.
    Preserve only the explicit fixture switch for the lock mutation probe.
    """
    source = MODULE_PATH.parents[2]
    profile = source / "tools/changerail/templates/profile.toml"
    return (
        "import importlib.util, os, sys; from pathlib import Path; "
        '[os.environ.pop(key) for key in list(os.environ) '
        'if key.startswith("CHRL_") and key != "CHRL_FIXTURE_EARLY_UNLOCK"]; '
        f'os.environ["CHRL_PROJECT_ROOT"]={str(source)!r}; '
        f's=importlib.util.spec_from_file_location("delivery", {str(MODULE_PATH)!r}); '
        "d=importlib.util.module_from_spec(s); s.loader.exec_module(d); "
        'os.environ.pop("CHRL_PROJECT_ROOT"); '
        f'd.PROFILE_PATH=Path({str(profile)!r}); '
        f'd.REPO_ROOT=Path({str(root)!r}); d.BOARD_ROOT=d.REPO_ROOT/"openspec/board"; '
        'd.RUNTIME_ROOT=d.REPO_ROOT/".runtime/changerail"; d.FROZEN_BOARD_RECORDS={}; '
        f'os.environ["CHRL_RUN_DIR"]={str(run)!r}; '
    )


def _singleflight_exact_legacy_identity(run: Path) -> str:
    """Pass a fixture's already-pinned v1 identity into its fresh test process.

    Each subprocess imports a new module, so it cannot see this module's
    fixture-only identity map.  This is deliberately a literal copy of the
    independently established fixture entry, never an environment switch or a
    production identity entry.
    """

    return "d.native.is_native = lambda card: False; d._run_observed_contract = lambda run: None; "


def _singleflight_verifier(
    root: Path,
    card: Path,
    run: Path,
    command: str,
    *,
    profile_path: Path | None = None,
    acquisition_gate: tuple[Path, Path] | None = None,
    publication_gate: tuple[Path, Path, Path | None, Path | None] | None = None,
) -> list[str]:
    """Run the real preverify entry point in an isolated verifier process."""
    profile = (
        f'import json; d.profile=lambda: {{"verification": json.loads('
        f"Path({str(profile_path)!r}).read_text())}}; "
        if profile_path is not None
        else f'd.profile=lambda: {{"verification": {{"pre_review_commands": [{command!r}], "final_commands": ["true"]}}}}; '
    )
    gate = ""
    if acquisition_gate is not None:
        ready, release = acquisition_gate
        gate = (
            "original_open=d._open_run_local_verification_lock; "
            "d._open_run_local_verification_lock=lambda run_dir: "
            f'(open({str(ready)!r}, "wb", buffering=0).write(b"A"), '
            f'open({str(release)!r}, "rb", buffering=0).read(1), original_open(run_dir))[-1]; '
        )
    code = (
        _delivery_child_bootstrap(root, run)
        + _singleflight_exact_legacy_identity(run)
        + profile
        + gate
        + _singleflight_publication_gate(run, "preverification.json", publication_gate)
        + "d.require_legacy_history=lambda: None; d.require_delivery_card_structure=lambda card: None; "
        "d.require_substantive_result_and_log=lambda card: None; d.require_non_future_log_timestamps=lambda card: None; "
        "d.require_live_board_references=lambda: None; d.emit_event=lambda phase, stage: None; "
        f"sys.exit(d.preverify({str(card)!r}))"
    )
    return [sys.executable, "-c", code]


def _singleflight_focused_verifier(
    root: Path,
    run: Path,
    command: list[str],
    *,
    publication_gate: tuple[Path, Path, Path | None, Path | None] | None = None,
) -> list[str]:
    """Run the real focused-evidence entry point in an isolated process."""
    code = (
        _delivery_child_bootstrap(root, run)
        + _singleflight_publication_gate(run, None, publication_gate)
        + f'sys.exit(d.run_evidence("singleflight", {command!r}))'
    )
    return [sys.executable, "-c", code]


def _singleflight_direct_verifier(
    root: Path,
    card: Path,
    run: Path,
    command: str,
    mode: str,
    *,
    profile_path: Path | None = None,
    acquisition_gate: tuple[Path, Path] | None = None,
) -> list[str]:
    """Exercise private floor/focused adapters from another verifier process."""
    direct_child = f'from pathlib import Path; Path({str(run / "direct-spawned")!r}).write_text("spawned")'
    profile = (
        f'import json; d.profile=lambda: {{"verification": json.loads('
        f"Path({str(profile_path)!r}).read_text())}}; "
        if profile_path is not None
        else f'd.profile=lambda: {{"verification": {{"pre_review_commands": [{command!r}], "final_commands": ["true"]}}}}; '
    )
    gate = ""
    if acquisition_gate is not None:
        ready, release = acquisition_gate
        gate = (
            "original_open=d._open_run_local_verification_lock; "
            "d._open_run_local_verification_lock=lambda run_dir: "
            f'(open({str(ready)!r}, "wb", buffering=0).write(b"A"), '
            f'open({str(release)!r}, "rb", buffering=0).read(1), original_open(run_dir))[-1]; '
        )
    code = (
        _delivery_child_bootstrap(root, run)
        + _singleflight_exact_legacy_identity(run)
        + profile
        + gate
        + "d.emit_event=lambda phase, stage: None; "
        f"mode={mode!r}; "
        f"card=Path({str(card)!r}); "
        f'identity={{"kind":"argv", "argv":[sys.executable,"-c",{direct_child!r}]}}; '
        'result=(d._run_evidence_locked(Path(os.environ["CHRL_RUN_DIR"]), "direct", identity) '
        'if mode == "focused-helper" else d._run_full_floor(card, commands=d.verification_commands("pre_review"), '
        'root_name="preverification", result_name="preverification.json", '
        'schema="changerail.pre-review-verification.v1", event_stage="preverification", proof_lane="pre_review")); '
        'sys.exit(result if isinstance(result, int) else (0 if result["ok"] else 1))'
    )
    return [sys.executable, "-c", code]


def _singleflight_final_verifier(
    root: Path,
    card: Path,
    run: Path,
    command: str,
    *,
    profile_path: Path | None = None,
    acquisition_gate: tuple[Path, Path] | None = None,
    publication_gate: tuple[Path, Path, Path | None, Path | None] | None = None,
) -> list[str]:
    """Run the actual final entrypoint with fixture-owned existing GO prerequisites."""
    profile = (
        f'import json; d.profile=lambda: {{"verification": json.loads('
        f"Path({str(profile_path)!r}).read_text())}}; "
        if profile_path is not None
        else f'd.profile=lambda: {{"verification": {{"pre_review_commands": ["true"], "final_commands": [{command!r}]}}}}; '
    )
    gate = ""
    if acquisition_gate is not None:
        ready, release = acquisition_gate
        gate = (
            "original_open=d._open_run_local_verification_lock; "
            "d._open_run_local_verification_lock=lambda run_dir: "
            f'(open({str(ready)!r}, "wb", buffering=0).write(b"A"), '
            f'open({str(release)!r}, "rb", buffering=0).read(1), original_open(run_dir))[-1]; '
        )
    code = (
        _delivery_child_bootstrap(root, run)
        + _singleflight_exact_legacy_identity(run)
        + profile
        + gate
        + _singleflight_publication_gate(run, "verification.json", publication_gate)
        + f"sys.exit(d.verify({str(card)!r}))"
    )
    return [sys.executable, "-c", code]


def test_check_singleflight_real_final_verifiers(tmp_path, monkeypatch):
    """Two real final callers share the same run lock and preserve fresh-GO gates."""
    import select
    import sys

    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "ready.fifo", root / "release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    child = [
        sys.executable,
        "-c",
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)',
    ]
    command = shlex.join(child)
    commands[:] = [command]
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(
            _singleflight_final_verifier(root, card, run, command), cwd=root
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        before = {path: path.read_bytes() for path in run.rglob("*.json")}
        contender = groups.start(
            _singleflight_final_verifier(root, card, run, command),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _, stderr = contender.communicate(timeout=5)
        assert contender.returncode != 0 and "already running" in stderr
        assert {path: path.read_bytes() for path in run.rglob("*.json")} == before
        os.write(release_fd, b"x")
        assert first.wait(timeout=5) == 0
        reuse = subprocess.run(
            _singleflight_final_verifier(root, card, run, command),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert (
            reuse.returncode == 0
            and len(list((run / "verification").glob("cycle-*"))) == 1
        )
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_fixture_group_cleanup_after_child_ready(
    tmp_path, monkeypatch
):
    """Injected fixture failure cleans its verifier descendants but not an outside sentinel."""
    import select
    import sys
    import time

    root, _card, _run, _commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    ready, release = root / "cleanup-ready.fifo", root / "cleanup-release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    child_pid = root / "fixture-child.pid"
    child_code = (
        "import os; from pathlib import Path; "
        f"Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)'
    )
    holder_code = (
        "import subprocess, sys; "
        f'child=subprocess.Popen([sys.executable, "-c", {child_code!r}]); child.wait()'
    )
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    sentinel = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
    )
    groups = _FixtureProcessGroups()
    try:
        groups.start([sys.executable, "-c", holder_code], cwd=root)
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        with pytest.raises(RuntimeError, match="injected after child-ready"):
            raise RuntimeError("injected after child-ready")
    finally:
        groups.close()
        os.close(ready_fd)
        os.close(release_fd)
    try:
        deadline = time.monotonic() + 5
        while True:
            try:
                os.kill(int(child_pid.read_text()), 0)
            except ProcessLookupError:
                break
            assert time.monotonic() < deadline, "fixture-owned child survived cleanup"
            time.sleep(0.05)
        assert sentinel.poll() is None
    finally:
        os.killpg(sentinel.pid, signal.SIGKILL)
        sentinel.wait(timeout=5)


@pytest.mark.parametrize("damage", ["corrupt", "missing"])
def test_check_singleflight_durable_intent_refuses_damaged_final_orphan(
    tmp_path, monkeypatch, damage
):
    """Final-lane receipt damage also cannot permit a focused cross-lane retry."""
    import select
    import sys

    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    ready, release, done = (
        root / "ready.fifo",
        root / "release.fifo",
        root / "done.fifo",
    )
    for fifo in (ready, release, done):
        os.mkfifo(fifo)
    child_pid = run / "child-pid"
    child = [
        sys.executable,
        "-c",
        f"import os; from pathlib import Path; Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1); '
        f'open({str(done)!r}, "wb", buffering=0).write(b"D")',
    ]
    command = shlex.join(child)
    commands[:] = [command]
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    done_fd = os.open(done, os.O_RDWR | os.O_NONBLOCK)
    parent = None
    groups = _FixtureProcessGroups()
    try:
        sentinel_process = groups.start(
            [sys.executable, "-c", "import time; time.sleep(30)"], cwd=root
        )
        parent = groups.start(
            _singleflight_final_verifier(root, card, run, command), cwd=root
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        pid = int(child_pid.read_text())
        record = next(
            path
            for path in (run / "verification").glob("cycle-*/*.json")
            if len(path.stem) == 32
        )
        intent = next((run / "verification-attempts").glob("*.json"))
        intent_bytes = intent.read_bytes()
        parent.kill()
        assert parent.wait(timeout=5) != 0
        os.kill(pid, 0)
        assert (
            sentinel_process.poll() is None
        )  # Separate fixture session is never touched.
        if damage == "corrupt":
            record.write_bytes(b'{"state":"running",')
        else:
            record.unlink()
        retry = subprocess.run(
            _singleflight_focused_verifier(root, run, ["true"]),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert retry.returncode != 0 and "remains unresolved" in retry.stderr
        assert intent.read_bytes() == intent_bytes
        os.write(release_fd, b"x")
        assert select.select([done_fd], [], [], 5)[0] and os.read(done_fd, 1) == b"D"
    finally:
        for fd in (ready_fd, release_fd, done_fd):
            os.close(fd)
        groups.close()


@pytest.mark.parametrize(
    "first_lane,contender_mode",
    [
        ("focused", "floor-helper"),
        ("configured", "focused-helper"),
    ],
)
def test_check_singleflight_direct_helpers_cannot_bypass_real_lock(
    tmp_path, monkeypatch, first_lane, contender_mode
):
    """Private adapters acquire the same lock; no boolean/caller convention bypasses it."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "ready.fifo", root / "release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    child = [
        sys.executable,
        "-c",
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)',
    ]
    shell = shlex.join(child)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        first_argv = (
            _singleflight_focused_verifier(root, run, child)
            if first_lane == "focused"
            else _singleflight_verifier(root, card, run, shell)
        )
        first = groups.start(first_argv, cwd=root)
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        before = {path: path.read_bytes() for path in run.rglob("*.json")}
        contender = groups.start(
            _singleflight_direct_verifier(root, card, run, shell, contender_mode),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _stdout, stderr = contender.communicate(timeout=5)
        assert contender.returncode != 0 and "already running" in stderr
        assert not (run / "direct-spawned").exists()
        assert {path: path.read_bytes() for path in run.rglob("*.json")} == before
        os.write(release_fd, b"x")
        assert first.wait(timeout=5) == 0
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_direct_floor_reuses_completion_after_delayed_acquisition(
    tmp_path, monkeypatch
):
    """A waiting direct caller rechecks the completed proof before allocating a cycle."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    child_ready, child_release = root / "child-ready.fifo", root / "child-release.fifo"
    acquire_ready, acquire_release = (
        root / "acquire-ready.fifo",
        root / "acquire-release.fifo",
    )
    for fifo in (child_ready, child_release, acquire_ready, acquire_release):
        os.mkfifo(fifo)
    counter = run / "direct-invocations"
    child = [
        sys.executable,
        "-c",
        f"from pathlib import Path; p=Path({str(counter)!r}); "
        'p.write_text(p.read_text()+"x" if p.exists() else "x"); '
        f'open({str(child_ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(child_release)!r}, "rb", buffering=0).read(1)',
    ]
    command = shlex.join(child)
    child_ready_fd = os.open(child_ready, os.O_RDWR | os.O_NONBLOCK)
    child_release_fd = os.open(child_release, os.O_RDWR | os.O_NONBLOCK)
    acquire_ready_fd = os.open(acquire_ready, os.O_RDWR | os.O_NONBLOCK)
    acquire_release_fd = os.open(acquire_release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(
            _singleflight_direct_verifier(root, card, run, command, "floor-helper"),
            cwd=root,
        )
        assert (
            select.select([child_ready_fd], [], [], 5)[0]
            and os.read(child_ready_fd, 1) == b"R"
        )
        busy = groups.start(
            _singleflight_direct_verifier(root, card, run, command, "floor-helper"),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _stdout, stderr = busy.communicate(timeout=5)
        assert busy.returncode != 0 and "already running" in stderr
        delayed = groups.start(
            _singleflight_direct_verifier(
                root,
                card,
                run,
                command,
                "floor-helper",
                acquisition_gate=(acquire_ready, acquire_release),
            ),
            cwd=root,
        )
        assert select.select([acquire_ready_fd], [], [], 5)[0]
        assert os.read(acquire_ready_fd, 1) == b"A"
        os.write(child_release_fd, b"x")
        assert first.wait(timeout=5) == 0
        before = {path: path.read_bytes() for path in run.rglob("*") if path.is_file()}
        assert counter.read_text() == "x"
        assert len(list((run / "preverification").glob("cycle-*"))) == 1
        os.write(acquire_release_fd, b"x")
        assert delayed.wait(timeout=5) == 0
        assert counter.read_text() == "x"
        assert len(list((run / "preverification").glob("cycle-*"))) == 1
        assert {
            path: path.read_bytes() for path in run.rglob("*") if path.is_file()
        } == before
        restarted = groups.start(
            _singleflight_direct_verifier(root, card, run, command, "floor-helper"),
            cwd=root,
        )
        assert restarted.wait(timeout=5) == 0
        assert counter.read_text() == "x"
        assert len(list((run / "preverification").glob("cycle-*"))) == 1
    finally:
        for fd in (
            child_ready_fd,
            child_release_fd,
            acquire_ready_fd,
            acquire_release_fd,
        ):
            os.close(fd)
        groups.close()


@pytest.mark.parametrize("entry", ["focused", "preverify", "final"])
def test_check_singleflight_retains_real_lock_through_publication_windows(
    tmp_path, monkeypatch, entry
):
    """A post-child contender stays busy until the real receipt/index publication finishes."""
    import select
    import sys

    if entry == "final":
        root, card, run, _ = _configured_final_check_fixture(tmp_path, monkeypatch)
    else:
        root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    receipt_ready, receipt_release = (
        root / "receipt-ready.fifo",
        root / "receipt-release.fifo",
    )
    index_ready, index_release = root / "index-ready.fifo", root / "index-release.fifo"
    for fifo in (receipt_ready, receipt_release, index_ready, index_release):
        os.mkfifo(fifo)
    counter = run / f"{entry}-publication-invocations"
    child = [
        sys.executable,
        "-c",
        f"from pathlib import Path; p=Path({str(counter)!r}); "
        'p.write_text(p.read_text()+"x" if p.exists() else "x")',
    ]
    command = shlex.join(child)
    gate = (
        receipt_ready,
        receipt_release,
        None if entry == "focused" else index_ready,
        None if entry == "focused" else index_release,
    )
    first_argv = (
        _singleflight_focused_verifier(root, run, child, publication_gate=gate)
        if entry == "focused"
        else _singleflight_final_verifier(
            root, card, run, command, publication_gate=gate
        )
        if entry == "final"
        else _singleflight_verifier(root, card, run, command, publication_gate=gate)
    )
    contender_argv = (
        _singleflight_focused_verifier(root, run, child)
        if entry == "focused"
        else _singleflight_final_verifier(root, card, run, command)
        if entry == "final"
        else _singleflight_verifier(root, card, run, command)
    )
    receipt_ready_fd = os.open(receipt_ready, os.O_RDWR | os.O_NONBLOCK)
    receipt_release_fd = os.open(receipt_release, os.O_RDWR | os.O_NONBLOCK)
    index_ready_fd = os.open(index_ready, os.O_RDWR | os.O_NONBLOCK)
    index_release_fd = os.open(index_release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(first_argv, cwd=root)
        assert select.select([receipt_ready_fd], [], [], 5)[0]
        assert os.read(receipt_ready_fd, 1) == b"P" and counter.read_text() == "x"
        before_receipt = {path: path.read_bytes() for path in run.rglob("*.json")}
        cycles_root = run / (
            "focused-evidence"
            if entry == "focused"
            else "verification"
            if entry == "final"
            else "preverification"
        )
        cycles = (
            len(list(cycles_root.glob("cycle-*")))
            if entry != "focused"
            else len(list(cycles_root.glob("*.json")))
        )
        contender = groups.start(
            contender_argv,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _stdout, stderr = contender.communicate(timeout=5)
        assert contender.returncode != 0 and "already running" in stderr
        assert {
            path: path.read_bytes() for path in run.rglob("*.json")
        } == before_receipt
        assert (
            len(list(cycles_root.glob("cycle-*")))
            if entry != "focused"
            else len(list(cycles_root.glob("*.json")))
        ) == cycles
        os.write(receipt_release_fd, b"x")
        if entry != "focused":
            assert select.select([index_ready_fd], [], [], 5)[0]
            assert os.read(index_ready_fd, 1) == b"P"
            before_index = {path: path.read_bytes() for path in run.rglob("*.json")}
            index_contender = groups.start(
                contender_argv,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            _stdout, stderr = index_contender.communicate(timeout=5)
            assert index_contender.returncode != 0 and "already running" in stderr
            assert {
                path: path.read_bytes() for path in run.rglob("*.json")
            } == before_index
            os.write(index_release_fd, b"x")
        assert first.wait(timeout=5) == 0 and counter.read_text() == "x"
        restarted = groups.start(
            contender_argv,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _stdout, stderr = restarted.communicate(timeout=5)
        if entry == "focused":
            assert restarted.returncode != 0 and "must not be repeated" in stderr
        else:
            assert restarted.returncode == 0
        assert counter.read_text() == "x"
    finally:
        for fd in (receipt_release_fd, index_release_fd):
            try:
                os.write(fd, b"x")
            except BlockingIOError:
                pass
        for fd in (
            receipt_ready_fd,
            receipt_release_fd,
            index_ready_fd,
            index_release_fd,
        ):
            os.close(fd)
        groups.close()


def test_check_singleflight_real_focused_evidence(tmp_path, monkeypatch):
    """Focused evidence uses the same run-local boundary, not a separate lock."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "ready.fifo", root / "release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    counter = run / "focused-invocations"
    child = [
        sys.executable,
        "-c",
        f"from pathlib import Path; p=Path({str(counter)!r}); "
        'p.write_text(p.read_text()+"x" if p.exists() else "x"); '
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)',
    ]
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    first = second = None
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(_singleflight_focused_verifier(root, run, child), cwd=root)
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        before = {path: path.read_bytes() for path in run.rglob("*.json")}
        cycles = len(list((run / "focused-evidence").glob("*.json")))
        second = groups.start(
            _singleflight_focused_verifier(root, run, child),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _, stderr = second.communicate(timeout=5)
        assert second.returncode != 0 and "already running" in stderr
        assert {path: path.read_bytes() for path in run.rglob("*.json")} == before
        assert len(list((run / "focused-evidence").glob("*.json"))) == cycles
        os.write(release_fd, b"x")
        assert first.wait(timeout=5) == 0
        assert counter.read_text() == "x"
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_real_processes(tmp_path, monkeypatch):
    """A contender must not launch a second FIFO-held configured child."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "ready.fifo", root / "release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    counter = run / "invocations"
    child = (
        f"import os; from pathlib import Path; "
        f'p=Path({str(counter)!r}); p.write_text(p.read_text()+"x" if p.exists() else "x"); '
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)'
    )
    command = shlex.join([sys.executable, "-c", child])
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    first = second = None
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(_singleflight_verifier(root, card, run, command), cwd=root)
        assert select.select([ready_fd], [], [], 5)[0]
        assert os.read(ready_fd, 1) == b"R"
        before = {path: path.read_bytes() for path in run.rglob("*.json")}
        cycles = len(list((run / "preverification").glob("cycle-*")))
        second = groups.start(
            _singleflight_verifier(root, card, run, command),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _, stderr = second.communicate(timeout=5)
        assert second.returncode != 0 and "already running" in stderr
        assert {path: path.read_bytes() for path in run.rglob("*.json")} == before
        assert len(list((run / "preverification").glob("cycle-*"))) == cycles
        os.write(release_fd, b"xx")
        assert first.wait(timeout=5) == 0
        assert counter.read_text() == "x"
        reused = subprocess.run(
            _singleflight_verifier(root, card, run, command),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert reused.returncode == 0 and counter.read_text() == "x"
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_cross_lane_different_command_refuses_before_publication(
    tmp_path, monkeypatch
):
    """A focused holder blocks a distinct configured command until terminal publication."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "ready.fifo", root / "release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    held = [
        sys.executable,
        "-c",
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1)',
    ]
    marker = run / "different-command-ran"
    contender_command = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("no")',
        ]
    )
    groups = _FixtureProcessGroups()
    try:
        first = groups.start(_singleflight_focused_verifier(root, run, held), cwd=root)
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        before = {path: path.read_bytes() for path in run.rglob("*.json")}
        cycles = len(list((run / "preverification").glob("cycle-*")))
        contender = subprocess.run(
            _singleflight_verifier(root, card, run, contender_command),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert contender.returncode != 0 and "already running" in contender.stderr
        assert not marker.exists()
        assert {path: path.read_bytes() for path in run.rglob("*.json")} == before
        assert len(list((run / "preverification").glob("cycle-*"))) == cycles
        os.write(release_fd, b"x")
        assert first.wait(timeout=5) == 0
        assert len(list((run / "focused-evidence").glob("*.json"))) == 1
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


@pytest.mark.parametrize(
    "first_lane,damage",
    [
        ("focused", "corrupt"),
        ("focused", "missing"),
        ("configured", "corrupt"),
        ("configured", "missing"),
    ],
)
def test_check_singleflight_durable_intent_refuses_damaged_orphan_cross_lane(
    tmp_path, monkeypatch, first_lane, damage
):
    """Receipt damage cannot erase start ownership while the fixture child survives."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release, done = (
        root / "ready.fifo",
        root / "release.fifo",
        root / "done.fifo",
    )
    for fifo in (ready, release, done):
        os.mkfifo(fifo)
    sentinel = root / "unrelated-sentinel"
    sentinel.write_bytes(b"preserve")
    child_pid = run / "child-pid"
    child = [
        sys.executable,
        "-c",
        f"import os; from pathlib import Path; Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1); '
        f'open({str(done)!r}, "wb", buffering=0).write(b"D")',
    ]
    shell = shlex.join(child)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    done_fd = os.open(done, os.O_RDWR | os.O_NONBLOCK)
    parent = None
    groups = _FixtureProcessGroups()
    try:
        sentinel_process = groups.start(
            [sys.executable, "-c", "import time; time.sleep(30)"], cwd=root
        )
        first = (
            _singleflight_focused_verifier(root, run, child)
            if first_lane == "focused"
            else _singleflight_verifier(root, card, run, shell)
        )
        parent = groups.start(first, cwd=root)
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        pid = int(child_pid.read_text())
        record = (
            next((run / "focused-evidence").glob("*.json"))
            if first_lane == "focused"
            else next((run / "preverification").glob("cycle-*/*.json"))
        )
        intent = next((run / "verification-attempts").glob("*.json"))
        intent_bytes = intent.read_bytes()
        parent.kill()
        assert parent.wait(timeout=5) != 0
        os.kill(pid, 0)
        assert sentinel_process.poll() is None  # Parent-group cleanup never reaches it.
        if damage == "corrupt":
            record.write_bytes(b'{"state":"running",')
        else:
            record.unlink()
        before = {
            path: path.read_bytes() for path in run.rglob("*.json") if path != record
        }
        contender = (
            _singleflight_verifier(root, card, run, "true")
            if first_lane == "focused"
            else _singleflight_focused_verifier(root, run, ["true"])
        )
        retry = subprocess.run(
            contender, cwd=root, capture_output=True, text=True, timeout=5
        )
        assert retry.returncode != 0 and "remains unresolved" in retry.stderr
        assert intent.read_bytes() == intent_bytes
        assert {
            path: path.read_bytes() for path in run.rglob("*.json") if path != record
        } == before
        assert sentinel.read_bytes() == b"preserve"
        os.write(release_fd, b"x")
        assert select.select([done_fd], [], [], 5)[0] and os.read(done_fd, 1) == b"D"
    finally:
        for fd in (ready_fd, release_fd, done_fd):
            os.close(fd)
        groups.close()


def test_check_singleflight_interrupted_terminal_remains_unresolved(
    tmp_path, monkeypatch
):
    """A terminal interrupted/null observation is not observed child completion."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release, done = (
        root / "ready.fifo",
        root / "release.fifo",
        root / "done.fifo",
    )
    for fifo in (ready, release, done):
        os.mkfifo(fifo)
    child_pid = run / "child-pid"
    child = [
        sys.executable,
        "-c",
        f"import os; from pathlib import Path; Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1); '
        f'open({str(done)!r}, "wb", buffering=0).write(b"D")',
    ]
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    done_fd = os.open(done, os.O_RDWR | os.O_NONBLOCK)
    parent = None
    groups = _FixtureProcessGroups()
    try:
        # Keep bash as the immediate subprocess so a parent-only SIGINT leaves the
        # FIFO-held Python worker independently observable.
        parent = groups.start(
            _singleflight_verifier(root, card, run, shlex.join(child) + "; :"), cwd=root
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        pid = int(child_pid.read_text())
        parent.send_signal(signal.SIGINT)
        assert parent.wait(timeout=5) != 0
        record_path = next(
            path
            for path in (run / "preverification").glob("cycle-*/*.json")
            if len(path.stem) == 32
        )
        record = delivery.load_json(record_path)
        assert record["state"] == "terminal" and record["outcome"] == "interrupted"
        assert record["exit_code"] is None and record["verdict"] == "unconfirmed"
        os.kill(pid, 0)
        retry = subprocess.run(
            _singleflight_focused_verifier(root, run, ["true"]),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert retry.returncode != 0 and "remains unresolved" in retry.stderr
        os.write(release_fd, b"x")
        assert select.select([done_fd], [], [], 5)[0] and os.read(done_fd, 1) == b"D"
    finally:
        for fd in (ready_fd, release_fd, done_fd):
            os.close(fd)
        groups.close()


def test_check_singleflight_unknown_terminal_remains_unresolved(tmp_path, monkeypatch):
    """Schema-allowed unknown/null is not an authorized child-completion outcome."""
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    identity = {"kind": "argv", "argv": ["true"]}
    path, item = delivery.start_check_result(run, "focused", "unknown", identity)
    item.update(
        state="terminal",
        observed_at=delivery.utc_now(),
        duration_seconds=0,
        fingerprint=delivery.payload_fingerprint(),
        outcome="unknown",
        exit_code=None,
        verdict="unconfirmed",
        reason="interrupted_owner",
    )
    delivery.finish_check_result(path, item, b"")
    with pytest.raises(delivery.DeliveryError, match="remains unresolved"):
        delivery.run_evidence("retry", ["true"])


def test_check_singleflight_revalidates_under_lock(tmp_path, monkeypatch):
    """A real preverify process decides only after its kernel-lock acquisition."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "acquire-ready.fifo", root / "acquire-release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    profile_path = tmp_path / "profile.json"
    marker = run / "in-lock-command"
    old = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("old")',
        ]
    )
    current = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("current")',
        ]
    )
    profile_path.write_text(
        json.dumps({"pre_review_commands": [old], "final_commands": ["true"]})
    )
    groups = _FixtureProcessGroups()
    try:
        verifier = groups.start(
            _singleflight_verifier(
                root,
                card,
                run,
                old,
                profile_path=profile_path,
                acquisition_gate=(ready, release),
            ),
            cwd=root,
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"A"
        # These are changed after the preliminary owner read but before real flock.
        (root / "tracked.txt").write_text("changed before acquisition\n")
        profile_path.write_text(
            json.dumps({"pre_review_commands": [current], "final_commands": ["true"]})
        )
        os.write(release_fd, b"x")
        assert verifier.wait(timeout=5) == 0
        assert marker.read_text() == "current"
        result = delivery.load_json(run / "preverification.json")
        assert result["configured_commands"] == [current]
        assert result["fingerprint"] == delivery.payload_fingerprint()
        assert len(list((run / "preverification").glob("cycle-*"))) == 1
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_final_and_direct_floor_revalidate_at_acquisition(
    tmp_path, monkeypatch
):
    """Final and direct adapters use the current configuration after real flock."""
    import select
    import sys

    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    ready, release = root / "acquire-ready.fifo", root / "acquire-release.fifo"
    os.mkfifo(ready)
    os.mkfifo(release)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    profile_path = tmp_path / "profile.json"
    marker = run / "final-current"
    old = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("old")',
        ]
    )
    current = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("current")',
        ]
    )
    profile_path.write_text(
        json.dumps({"pre_review_commands": ["true"], "final_commands": [old]})
    )
    groups = _FixtureProcessGroups()
    try:
        final = groups.start(
            _singleflight_final_verifier(
                root,
                card,
                run,
                old,
                profile_path=profile_path,
                acquisition_gate=(ready, release),
            ),
            cwd=root,
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"A"
        profile_path.write_text(
            json.dumps({"pre_review_commands": ["true"], "final_commands": [current]})
        )
        os.write(release_fd, b"x")
        assert final.wait(timeout=5) == 0 and marker.read_text() == "current"
        assert delivery.load_json(run / "verification.json")["configured_commands"] == [
            current
        ]

        # The direct floor receives its stale list before the barrier; after the
        # genuine flock it must reject the newly configured current list.
        direct_ready, direct_release = (
            root / "direct-ready.fifo",
            root / "direct-release.fifo",
        )
        os.mkfifo(direct_ready)
        os.mkfifo(direct_release)
        direct_ready_fd = os.open(direct_ready, os.O_RDWR | os.O_NONBLOCK)
        direct_release_fd = os.open(direct_release, os.O_RDWR | os.O_NONBLOCK)
        try:
            profile_path.write_text(
                json.dumps({"pre_review_commands": [old], "final_commands": ["true"]})
            )
            direct = groups.start(
                _singleflight_direct_verifier(
                    root,
                    card,
                    run,
                    old,
                    "floor-helper",
                    profile_path=profile_path,
                    acquisition_gate=(direct_ready, direct_release),
                ),
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            assert (
                select.select([direct_ready_fd], [], [], 5)[0]
                and os.read(direct_ready_fd, 1) == b"A"
            )
            (root / "tracked.txt").write_text(
                "direct payload changed before acquisition\n"
            )
            profile_path.write_text(
                json.dumps(
                    {"pre_review_commands": [current], "final_commands": ["true"]}
                )
            )
            os.write(direct_release_fd, b"x")
            _, stderr = direct.communicate(timeout=5)
            assert (
                direct.returncode != 0 and "commands changed before execution" in stderr
            )
            assert len(list((run / "preverification").glob("cycle-*"))) == 1
        finally:
            os.close(direct_ready_fd)
            os.close(direct_release_fd)
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_payload_only_changes_revalidate_final_and_direct_acquisition(
    tmp_path, monkeypatch
):
    """Payload-only acquisition drift neither reuses stale proof nor masks current decisions."""
    import select
    import sys

    final_tmp = tmp_path / "final-payload-only"
    final_tmp.mkdir()
    root, card, run, commands = _configured_final_check_fixture(final_tmp, monkeypatch)
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    final_counter = run / "final-payload-invocations"
    final_command = shlex.join(
        [
            sys.executable,
            "-c",
            f"from pathlib import Path; p=Path({str(final_counter)!r}); "
            'p.write_text(p.read_text()+"x" if p.exists() else "x")',
        ]
    )
    commands[:] = [final_command]
    assert delivery.verify(str(card)) == 0 and final_counter.read_text() == "x"
    receipt_ready, receipt_release = (
        root / "final-acquire-ready.fifo",
        root / "final-acquire-release.fifo",
    )
    os.mkfifo(receipt_ready)
    os.mkfifo(receipt_release)
    ready_fd = os.open(receipt_ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(receipt_release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        before_final = (run / "verification.json").read_bytes()
        final = groups.start(
            _singleflight_final_verifier(
                root,
                card,
                run,
                final_command,
                acquisition_gate=(receipt_ready, receipt_release),
            ),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"A"
        (root / "tracked.txt").write_text("payload-only final drift\n")
        os.write(release_fd, b"x")
        _stdout, stderr = final.communicate(timeout=5)
        assert final.returncode != 0 and "stale" in stderr
        assert (run / "verification.json").read_bytes() == before_final
        assert len(list((run / "verification").glob("cycle-*"))) == 1
        assert final_counter.read_text() == "x"
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()

    direct_tmp = tmp_path / "direct-payload-only"
    direct_tmp.mkdir()
    root, card, run, commands = _configured_pre_review_check_fixture(
        direct_tmp, monkeypatch
    )
    direct_counter = run / "direct-payload-invocations"
    direct_command = shlex.join(
        [
            sys.executable,
            "-c",
            f"from pathlib import Path; p=Path({str(direct_counter)!r}); "
            'p.write_text(p.read_text()+"x" if p.exists() else "x")',
        ]
    )
    commands[:] = [direct_command]
    assert (
        delivery._run_full_floor(
            card,
            commands=commands,
            root_name="preverification",
            result_name="preverification.json",
            schema="changerail.pre-review-verification.v1",
            event_stage="preverification",
            proof_lane="pre_review",
        )["ok"]
        and direct_counter.read_text() == "x"
    )
    ready, release = (
        root / "direct-acquire-ready.fifo",
        root / "direct-acquire-release.fifo",
    )
    os.mkfifo(ready)
    os.mkfifo(release)
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    groups = _FixtureProcessGroups()
    try:
        previous = delivery.load_json(run / "preverification.json")
        direct = groups.start(
            _singleflight_direct_verifier(
                root,
                card,
                run,
                direct_command,
                "floor-helper",
                acquisition_gate=(ready, release),
            ),
            cwd=root,
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"A"
        (root / "tracked.txt").write_text("payload-only direct drift\n")
        os.write(release_fd, b"x")
        assert direct.wait(timeout=5) == 0
        current = delivery.load_json(run / "preverification.json")
        assert (
            current["fingerprint"]
            == delivery.payload_fingerprint()
            != previous["fingerprint"]
        )
        assert direct_counter.read_text() == "xx"
        assert len(list((run / "preverification").glob("cycle-*"))) == 2
    finally:
        os.close(ready_fd)
        os.close(release_fd)
        groups.close()


def test_check_singleflight_orphan_refusal(tmp_path, monkeypatch):
    """A parent death cannot turn its still-live child into reusable completion."""
    import select
    import sys

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    ready, release, done = (
        root / "ready.fifo",
        root / "release.fifo",
        root / "done.fifo",
    )
    for fifo in (ready, release, done):
        os.mkfifo(fifo)
    sentinel = root / "unrelated-sentinel"
    sentinel.write_bytes(b"preserve")
    child_pid = run / "child-pid"
    child = (
        f"import os; from pathlib import Path; Path({str(child_pid)!r}).write_text(str(os.getpid())); "
        f'open({str(ready)!r}, "wb", buffering=0).write(b"R"); '
        f'open({str(release)!r}, "rb", buffering=0).read(1); '
        f'open({str(done)!r}, "wb", buffering=0).write(b"D")'
    )
    command = shlex.join([sys.executable, "-c", child])
    ready_fd = os.open(ready, os.O_RDWR | os.O_NONBLOCK)
    release_fd = os.open(release, os.O_RDWR | os.O_NONBLOCK)
    done_fd = os.open(done, os.O_RDWR | os.O_NONBLOCK)
    parent = None
    groups = _FixtureProcessGroups()
    try:
        parent = groups.start(
            _singleflight_verifier(root, card, run, command), cwd=root
        )
        assert select.select([ready_fd], [], [], 5)[0] and os.read(ready_fd, 1) == b"R"
        pid = int(child_pid.read_text())
        parent.kill()
        assert parent.wait(timeout=5) != 0
        os.kill(pid, 0)  # Observable child liveness, not a PID-only completion claim.
        retry = subprocess.run(
            _singleflight_verifier(root, card, run, command),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert retry.returncode != 0 and "remains unresolved" in retry.stderr
        os.write(release_fd, b"x")
        assert select.select([done_fd], [], [], 5)[0] and os.read(done_fd, 1) == b"D"
        again = subprocess.run(
            _singleflight_verifier(root, card, run, command),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert again.returncode != 0 and "remains unresolved" in again.stderr
        assert sentinel.read_bytes() == b"preserve"
    finally:
        for fd in (ready_fd, release_fd, done_fd):
            os.close(fd)
        groups.close()


def test_check_singleflight_shared_floor_releases_after_terminal_failure(
    tmp_path, monkeypatch
):
    """The direct shared-floor adapter takes the boundary and releases on failure."""
    root, card, run, configured = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    configured[:] = ["exit 7"]
    failed = delivery._run_full_floor(
        card,
        commands=configured,
        root_name="preverification",
        result_name="preverification.json",
        schema="changerail.pre-review-verification.v1",
        event_stage="preverification",
        proof_lane="pre_review",
    )
    configured[:] = ["true"]
    recovered = delivery._run_full_floor(
        card,
        commands=configured,
        root_name="preverification",
        result_name="preverification.json",
        schema="changerail.pre-review-verification.v1",
        event_stage="preverification",
        proof_lane="pre_review",
    )
    assert not failed["ok"] and recovered["ok"]
    assert len(list((run / "preverification").glob("cycle-*"))) == 2


def test_check_singleflight_completed_cycle_100_is_reusable(tmp_path, monkeypatch):
    """The real allocator's first three-digit cycle remains a completed attempt."""
    positive = (
        "cycle-01",
        "cycle-09",
        "cycle-10",
        "cycle-99",
        "cycle-100",
        "cycle-101",
    )
    negative = (
        "cycle-0",
        "cycle-00",
        "cycle-1",
        "cycle-9",
        "cycle-010",
        "cycle-+10",
        "cycle--10",
        "cycle-١٠",
        "cycle-10x",
        "cycle-10/child",
    )
    assert all(delivery._is_verification_cycle_name(name) for name in positive)
    assert not any(delivery._is_verification_cycle_name(name) for name in negative)

    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    cycles = run / "preverification"
    for number in range(1, 100):
        (cycles / f"cycle-{number:02d}").mkdir(parents=True, exist_ok=False)

    assert delivery.preverify(str(card)) == 0
    receipt = delivery.load_json(run / "preverification.json")
    intents = [
        delivery.load_json(path)
        for path in (run / "verification-attempts").glob("*.json")
    ]
    assert (cycles / "cycle-100").is_dir()
    assert all(
        intent["state"] == "observed_terminal" and intent["outcome"] == "exit"
        for intent in intents
    )
    assert {intent["record"] for intent in intents} == {
        command["record"] for command in receipt["commands"]
    }

    # This reaches the real ownership reader before cache reuse. A two-digit-only
    # cycle check incorrectly treats the completed cycle-100 intent as unresolved.
    assert delivery.preverify(str(card)) == 0
    assert len(list(cycles.glob("cycle-*"))) == 100

    # A large canonical name does not relax the typed ledger: started, malformed
    # terminal, foreign and noncanonical records still block before another cycle.
    path = next((run / "verification-attempts").glob("*.json"))
    before = path.read_bytes()
    for mutation in ("started", "missing-exit", "foreign-card", "noncanonical-cycle"):
        item = delivery.load_json(path)
        if mutation == "started":
            item = {
                key: value
                for key, value in item.items()
                if key not in {"outcome", "exit_code", "finished_at"}
            }
            item["state"] = "started"
        elif mutation == "missing-exit":
            item["exit_code"] = None
        elif mutation == "foreign-card":
            item["card"] = f"{FIXTURE_BOARD}/3.inprogress/foreign.md"
        else:
            item["record"] = item["record"].replace("cycle-100", "cycle-010")
        delivery.write_json(path, item)
        assert delivery._unresolved_verification_attempt(run) == delivery.repo_relative(
            path
        )
        with pytest.raises(delivery.DeliveryError, match="remains unresolved"):
            delivery.preverify(str(card))
        assert len(list(cycles.glob("cycle-*"))) == 100
        path.write_bytes(before)


def test_check_singleflight_direct_floor_revalidates_configured_commands(
    tmp_path, monkeypatch
):
    """A direct caller's pre-lock command text cannot execute after config changes."""
    import sys

    root, card, run, configured = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    marker = run / "stale-command-ran"
    stale = shlex.join(
        [
            sys.executable,
            "-c",
            f'from pathlib import Path; Path({str(marker)!r}).write_text("ran")',
        ]
    )
    configured[:] = ["true"]
    with pytest.raises(
        delivery.DeliveryError, match="commands changed before execution"
    ):
        delivery._run_full_floor(
            card,
            commands=[stale],
            root_name="preverification",
            result_name="preverification.json",
            schema="changerail.pre-review-verification.v1",
            event_stage="preverification",
            proof_lane="pre_review",
        )
    assert not marker.exists() and not (run / "preverification").exists()


def test_check_singleflight_capability_is_current_process_run_and_lifetime_bound(
    tmp_path, monkeypatch
):
    """Forged or expired helper capabilities cannot allocate a cycle or child."""
    root, card, run, configured = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    opened = 0
    original_open = delivery._open_run_local_verification_lock

    def counted_open(run_dir):
        nonlocal opened
        opened += 1
        return original_open(run_dir)

    monkeypatch.setattr(delivery, "_open_run_local_verification_lock", counted_open)
    with delivery.verification_attempt_lock(run, card, "pre_review") as ownership:
        forged = (
            ownership._replace(token="0" * 32),
            ownership._replace(pid=ownership.pid + 1),
            ownership._replace(run_dir=run / "foreign"),
            ownership._replace(card=card.with_name("foreign.md")),
            object(),
        )
        for capability in forged:
            with pytest.raises(delivery.DeliveryError, match="current lock ownership"):
                delivery._run_full_floor(
                    card,
                    commands=configured,
                    root_name="preverification",
                    result_name="preverification.json",
                    schema="changerail.pre-review-verification.v1",
                    event_stage="preverification",
                    proof_lane="pre_review",
                    ownership=capability,
                )
        assert not (run / "preverification").exists()
        # The genuine capability delegates without recursive acquisition.
        result = delivery._run_full_floor(
            card,
            commands=configured,
            root_name="preverification",
            result_name="preverification.json",
            schema="changerail.pre-review-verification.v1",
            event_stage="preverification",
            proof_lane="pre_review",
            ownership=ownership,
        )
        assert result["ok"] and opened == 1
    with pytest.raises(delivery.DeliveryError, match="current lock ownership"):
        delivery._require_verification_attempt_ownership(ownership, run, card)


def test_check_singleflight_wrappers_delegate_with_one_real_kernel_acquisition(
    tmp_path, monkeypatch
):
    """Configured wrappers pass the one live capability rather than reacquiring."""
    calls: list[int] = []
    original_flock = delivery.fcntl.flock

    def observed_flock(fd, operation):
        if operation & delivery.fcntl.LOCK_EX:
            calls.append(fd)
        return original_flock(fd, operation)

    monkeypatch.setattr(delivery.fcntl, "flock", observed_flock)
    original_profile = delivery.profile
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    assert delivery.preverify(str(card)) == 0 and len(calls) == 1

    final_tmp = tmp_path / "final-wrapper"
    final_tmp.mkdir()
    monkeypatch.setattr(delivery, "profile", original_profile)
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    root, card, run, _ = _configured_final_check_fixture(
        final_tmp, monkeypatch, ["true"]
    )
    calls.clear()
    assert delivery.verify(str(card)) == 0 and len(calls) == 1


@pytest.mark.parametrize("damage", ["leaf-link", "fifo", "ancestor-link"])
def test_check_singleflight_rejects_nonregular_or_link_lock_paths_before_spawn(
    tmp_path, monkeypatch, damage
):
    """The actual lock reader rejects every unsafe fixture path before receipts or children."""
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    if damage == "leaf-link":
        outside.write_text("preserve")
        (run / ".verification.lock").symlink_to(outside)
    elif damage == "fifo":
        os.mkfifo(run / ".verification.lock")
    else:
        parent = run.parent
        target = tmp_path / "real-runs"
        parent.rename(target)
        parent.symlink_to(target, target_is_directory=True)
        run = parent / run.name
        monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    with pytest.raises(
        delivery.DeliveryError,
        match="(unsafe verification lock|cannot start focused proof|unsafe current execution owner)",
    ):
        delivery.run_evidence("unsafe-lock", ["true"])
    assert not (run / "focused-evidence").exists()
    if damage == "leaf-link":
        assert outside.read_text() == "preserve"


def test_check_singleflight_validation_and_publication_failures_release_differently(
    tmp_path, monkeypatch
):
    """Observed validation failure releases; failed terminal publication remains unresolved."""
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    original_read = delivery.read_check_result
    monkeypatch.setattr(
        delivery,
        "read_check_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("fixture validation")),
    )
    assert delivery.run_evidence("validation-failure", ["true"]) == 1
    monkeypatch.setattr(delivery, "read_check_result", original_read)
    assert (
        delivery.run_evidence(
            "after-validation", [sys.executable, "-c", 'print("released")']
        )
        == 0
    )

    publication_tmp = tmp_path / "publication"
    publication_tmp.mkdir()
    root, card, run, _ = _configured_pre_review_check_fixture(
        publication_tmp, monkeypatch
    )
    original_finish = delivery.finish_check_result
    monkeypatch.setattr(
        delivery,
        "finish_check_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("fixture publication")),
    )
    assert delivery.run_evidence("publication-failure", ["true"]) == 1
    monkeypatch.setattr(delivery, "finish_check_result", original_finish)
    before = {path: path.read_bytes() for path in run.rglob("*.json")}
    with pytest.raises(delivery.DeliveryError, match="remains unresolved"):
        delivery.run_evidence("after-publication", ["printf must-not-run"])
    assert {path: path.read_bytes() for path in run.rglob("*.json")} == before


def test_check_singleflight_revalidates_owner_after_actual_lock_acquisition(
    tmp_path, monkeypatch
):
    """A controlled pre-lock owner change is caught after the real flock succeeds."""
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    other = card.with_name("other.md")
    other.write_bytes(card.read_bytes())
    original = delivery._open_run_local_verification_lock
    changed = False

    def acquire_after_owner_change(run_dir):
        nonlocal changed
        if not changed:
            changed = True
            owner = delivery.load_json(run / "run.json")
            owner["card"] = delivery.repo_relative(other)
            delivery.write_json(run / "run.json", owner)
        return original(run_dir)  # The real no-follow open and kernel flock still run.

    monkeypatch.setattr(
        delivery, "_open_run_local_verification_lock", acquire_after_owner_change
    )
    with pytest.raises(delivery.DeliveryError, match="foreign verification owner"):
        delivery.run_evidence("owner-race", ["true"])
    assert changed and not (run / "focused-evidence").exists()


def test_check_singleflight_rejects_unsafe_lock_path_before_spawn(
    tmp_path, monkeypatch
):
    """The regular/no-follow lock path refuses a symlink without starting proof."""
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    outside = root.parent / "outside-lock"
    outside.write_text("outside")
    (run / ".verification.lock").symlink_to(outside)
    with pytest.raises(delivery.DeliveryError, match="unsafe verification lock"):
        delivery.run_evidence("unsafe-lock", ["true"])
    assert not (run / "focused-evidence").exists() and outside.read_text() == "outside"


def _final_check_set(card, run, commands):
    return delivery._verified_command_set(
        run / "verification.json",
        run,
        card,
        delivery.payload_fingerprint(),
        commands,
        "final",
    )


@pytest.mark.parametrize(
    "command,code",
    [
        ("true", 0),
        ("printf stable", 0),
        ("exit 7", 7),
        ("kill -TERM $$", -15),
    ],
)
def test_configured_final_check_terminal_outcomes(tmp_path, monkeypatch, command, code):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, [command, "true"]
    )
    execute = subprocess.run
    running = []

    def observe(argv, *args, **kwargs):
        if argv[:2] == ["bash", "-lc"]:
            paths = list((run / "verification").glob("cycle-*/*.json"))
            records = [delivery.load_json(p) for p in paths]
            item = next(x for x in records if x["state"] == "running")
            assert item["lane"] == "final" and item["run_id"] == run.name
            assert item["card"] == delivery.repo_relative(card)
            assert item["command_identity"] == {
                "kind": "shell",
                "argv": argv,
                "shell_text": argv[-1],
            }
            assert item["before"] == delivery.payload_fingerprint() and item[
                "started_at"
            ].endswith("Z")
            running.append(item["attempt_id"])
        return execute(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", observe)
    assert delivery.verify(str(card)) == (0 if code == 0 else 1)
    index = delivery.load_json(run / "verification.json")
    assert len(index["commands"]) == len(set(running)) == (2 if code == 0 else 1)
    item, data, current = delivery.read_check_result(
        root / index["commands"][0]["record"], run, "final"
    )
    assert item["exit_code"] == code and item["outcome"] == "exit"
    assert current is (code == 0) and item["observed_at"] >= item["started_at"]
    assert item["duration_seconds"] >= 0
    assert data == (b"stable" if command == "printf stable" else b"")
    assert (
        item["log_size"] == len(data)
        and item["log_sha256"] == hashlib.sha256(data).hexdigest()
    )
    assert (_final_check_set(card, run, commands) is not None) is (code == 0)
    assert delivery.focused_evidence_summaries(run) == []


@pytest.mark.parametrize(
    "damage",
    [
        "control",
        "missing",
        "extra",
        "reordered",
        "duplicate",
        "absolute",
        "traversal",
        "unknown",
        "unknown-field",
        "bool-exit",
        "negative-duration",
        "date",
        "non-utc",
        "deep",
        "duplicate-key",
        "nested-duplicate",
        "nan",
        "running",
        "foreign-run",
        "foreign-card",
        "foreign-attempt",
        "foreign-lane",
        "argv",
        "shell",
        "stale",
        "missing-log",
        "tampered-log",
        "truncated-log",
        "legacy",
        "bad-index",
        "infinity",
        "overflow",
        "early-finish",
        "nested-unknown",
        "index-date",
        "index-schema",
        "index-bool-exit",
        "log-absolute",
        "log-traversal",
    ],
)
def test_configured_final_check_set_and_safe_summary(tmp_path, monkeypatch, damage):
    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    assert delivery.verify(str(card)) == 0
    _damage_configured_check(
        root, run / "verification.json", commands, damage, "pre_review"
    )
    valid = damage == "control"
    proof = _final_check_set(card, run, commands)
    assert (proof is not None) is valid
    assert (
        delivery._successful_verification_matches(
            run / "verification.json",
            run_dir=run,
            card=card,
            fingerprint=delivery.payload_fingerprint(),
            commands=commands,
            lane="final",
        )
        is valid
    )
    # Untrusted loaded mappings cannot certify summary or receipt, even if green.
    with pytest.raises(delivery.DeliveryError, match="validated final"):
        delivery.pytest_summary_from_verification(
            delivery.load_json(run / "verification.json"), run_dir=run
        )
    if valid:
        assert delivery.pytest_summary_from_verification(proof, run_dir=run) is None
    else:
        with pytest.raises(delivery.DeliveryError):
            delivery.pytest_summary_from_verification(proof, run_dir=run)
    rows = delivery.deterministic_commands(run)
    assert all(row["proof_status"] == "unconfirmed" for row in rows)
    delivery.build_metrics(run)
    children = []
    monkeypatch.setattr(
        delivery,
        "_run_full_floor",
        lambda *a, **kw: children.append(kw) or {"ok": False},
    )
    if damage == "running":
        with pytest.raises(delivery.DeliveryError, match="remains unresolved"):
            delivery.verify(str(card))
        assert children == []
    else:
        assert delivery.verify(str(card)) == (0 if valid else 1)
        assert len(children) == (0 if valid else 1)


def test_configured_final_check_exact_pytest_bytes(tmp_path, monkeypatch):
    import sys

    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    test = root / "test_owned.py"
    test.write_text("def test_owned():\n    assert 2 + 2 == 4\n")
    (root / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n")
    # Real installed pytest in the owned repository, never a printed fake summary.
    monkeypatch.setenv(
        "PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]
    )
    commands[:] = ["uv run pytest -q"]
    _refresh_exact_legacy_fixture(card, run)
    _write_matching_preverification(card, run)
    verdict = delivery.verdict_template(str(card))["template"]
    verdict["acceptance"][0]["evidence"] = ["owned fixture"]
    delivery.write_json(delivery.verdict_path(card.stem), verdict)
    assert delivery.verify(str(card)) == 0
    proof = _final_check_set(card, run, commands)
    summary = delivery.pytest_summary_from_verification(proof, run_dir=run)
    assert summary.startswith("1 passed in ")
    log = root / proof.receipts[0][0]["log"]
    info = log.stat()
    forbidden = {(info.st_dev, info.st_ino)}
    with monkeypatch.context() as watched:
        opened, reads = _focused_check_watch_reads(watched, forbidden)
        # Receipt must use the exact decision bytes even if storage changes afterwards.
        log.write_bytes(b"999 passed in 0.01s\n")
        assert delivery.pytest_summary_from_verification(proof, run_dir=run) == summary
        receipt = delivery.delivery_receipt_lines(
            verdict=verdict,
            verification=proof,
            run_dir=run,
            finalized_at=delivery.utc_now(),
        )
        assert f"- Pytest: `{summary}`." in receipt
        assert not (set(reads) & forbidden) and not (set(opened) & forbidden)
    assert _final_check_set(card, run, commands) is None
    log.write_bytes(proof.receipts[0][1])
    original_receipt = delivery.delivery_receipt_lines
    called = []

    def receipt_from_decision(**kwargs):
        incoming = kwargs["verification"]
        assert incoming.receipts == proof.receipts
        with monkeypatch.context() as watched:
            _, reads = _focused_check_watch_reads(watched, forbidden)
            log.write_bytes(b"888 passed in 0.01s\n")
            lines = original_receipt(**kwargs)
            assert f"- Pytest: `{summary}`." in lines and not (set(reads) & forbidden)
            called.append(lines)
            return lines

    class ReachedBoundary(Exception):
        pass

    def finalize(*a, **kw):
        raise ReachedBoundary

    monkeypatch.setattr(delivery, "delivery_receipt_lines", receipt_from_decision)
    monkeypatch.setattr(delivery, "finalize_card", finalize)
    with pytest.raises(ReachedBoundary):
        delivery.publish(str(card))
    assert len(called) == 1


@pytest.mark.parametrize("full_pytest", [False, True])
def test_configured_final_check_silent_summary(tmp_path, monkeypatch, full_pytest):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true"]
    )
    if full_pytest:
        # Genuine pytest with its terminal summary disabled by fixture configuration.
        (root / "test_owned.py").write_text("def test_owned():\n    pass\n")
        (root / "pytest.ini").write_text("[pytest]\naddopts = --no-summary -qq\n")
        (root / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n")
        commands[:] = ["uv run pytest -q"]
        _refresh_exact_legacy_fixture(card, run)
        _write_matching_preverification(card, run)
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["fixture"]
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
    assert delivery.verify(str(card)) == 0
    proof = _final_check_set(card, run, commands)
    assert delivery.pytest_summary_from_verification(proof, run_dir=run) is None
    kwargs = dict(
        verdict={"reviewed_at": delivery.utc_now()},
        verification=proof,
        run_dir=run,
        finalized_at=delivery.utc_now(),
    )
    if full_pytest:
        with pytest.raises(
            delivery.DeliveryError, match="cannot derive pytest summary"
        ):
            delivery.delivery_receipt_lines(**kwargs)
    else:
        assert not any(
            "Pytest:" in line for line in delivery.delivery_receipt_lines(**kwargs)
        )


@pytest.mark.parametrize(
    "damage",
    [
        "control",
        "missing-log",
        "stale",
        "legacy",
        "pre-review",
        "no-go",
        "manifest",
        "role",
    ],
)
def test_configured_final_check_composed_reuse_and_publish_gate(
    tmp_path, monkeypatch, damage
):
    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    counter = run / "count"
    commands[:] = ["printf x >> " + str(counter), "true"]
    assert delivery.verify(str(card)) == 0 and counter.read_bytes() == b"x"
    history = {
        p: p.read_bytes() for p in (run / "verification").rglob("*") if p.is_file()
    }
    assert delivery.verify(str(card)) == 0 and counter.read_bytes() == b"x"
    assert all(p.read_bytes() == data for p, data in history.items())
    proof = _final_check_set(card, run, commands)
    before_rows = delivery.deterministic_commands(run)
    if damage in {"missing-log", "stale", "legacy"}:
        _damage_configured_check(
            root, run / "verification.json", commands, damage, "pre_review"
        )
    elif damage == "pre-review":
        # Even equal configured lists cannot transfer pre_review authority into final.
        delivery.profile()["verification"]["pre_review_commands"] = commands
        _write_matching_preverification(card, run)
        (run / "verification.json").write_bytes(
            (run / "preverification.json").read_bytes()
        )
    elif damage == "no-go":
        verdict = delivery.load_json(delivery.verdict_path(card.stem))
        verdict["result"] = "no-go"
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
    elif damage == "manifest":
        path = delivery.manifest_path(card.stem)
        manifest = delivery.load_json(path)
        manifest["paths"] = []
        delivery.write_json(path, manifest)
    elif damage == "role":
        monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")
    before = (
        card.read_bytes(),
        _git(root, "write-tree").stdout,
        _git(root, "rev-parse", "HEAD").stdout,
    )
    boundary = []

    class ReachedBoundary(Exception):
        pass

    def finalize(value, *, receipt):
        boundary.append((value, receipt))
        raise ReachedBoundary

    monkeypatch.setattr(delivery, "finalize_card", finalize)
    real_git = delivery.git

    def read_only_git(*args, **kwargs):
        assert args[0] not in {"add", "commit", "push"}, (
            "external publication action reached"
        )
        return real_git(*args, **kwargs)

    monkeypatch.setattr(delivery, "git", read_only_git)
    with pytest.raises(
        ReachedBoundary if damage == "control" else delivery.DeliveryError
    ):
        delivery.publish(str(card))
    assert bool(boundary) is (damage == "control")
    assert before == (
        card.read_bytes(),
        _git(root, "write-tree").stdout,
        _git(root, "rev-parse", "HEAD").stdout,
    )
    assert not (root / "openspec/board/4.done" / card.name).exists()
    if damage == "missing-log":
        assert delivery.deterministic_commands(run) == before_rows
        history.pop(root / proof.receipts[0][0]["log"])
        assert delivery.verify(str(card)) == 0 and counter.read_bytes() == b"xx"
        assert all(p.read_bytes() == data for p, data in history.items())
        assert (
            delivery.build_metrics(run)["deterministic_command_count"] == 5
        )  # one pre, two per final cycle
        assert delivery.focused_evidence_summaries(run) == []


@pytest.mark.parametrize("change", [False, True])
def test_configured_final_check_independent_aggregate_drift(
    tmp_path, monkeypatch, change
):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true", "true"]
    )
    original = (root / "tracked.txt").read_bytes()
    before = delivery.payload_fingerprint()
    allocate = delivery._next_verification_cycle

    def between(path):
        cycle = allocate(path)
        if change:
            (root / "tracked.txt").write_bytes(b"between aggregate and child")
        return cycle

    monkeypatch.setattr(delivery, "_next_verification_cycle", between)
    assert delivery.verify(str(card)) == (1 if change else 0)
    index = delivery.load_json(run / "verification.json")
    assert len(index["commands"]) == 2 and index["ok"] is (not change)
    assert all(
        delivery.read_check_result(root / row["record"], run, "final")[2]
        for row in index["commands"]
    )
    assert (delivery.payload_fingerprint() != before) is change
    assert (root / "tracked.txt").read_bytes() == (
        b"between aggregate and child" if change else original
    )
    assert (_final_check_set(card, run, commands) is None) is change


@pytest.mark.parametrize("target", ["owner", "index", "history", "record", "log"])
@pytest.mark.parametrize("damage", ["control", "leaf", "ancestor", "fifo"])
def test_configured_final_check_nonregular_read_order(
    tmp_path, monkeypatch, target, damage
):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true"]
    )
    assert delivery.verify(str(card)) == 0
    index = run / "verification.json"
    record = root / delivery.load_json(index)["commands"][0]["record"]
    victim = {
        "owner": run / "run.json",
        "index": index,
        "history": run / "verification/cycle-01/verification.json",
        "record": record,
        "log": record.with_suffix(".log"),
    }[target]
    assert _final_check_set(card, run, commands) is not None
    if damage == "ancestor":
        moved = victim.parent.rename(
            victim.parent.with_name("saved-" + victim.parent.name)
        )
        victim.parent.symlink_to(moved, target_is_directory=True)
    elif damage != "control":
        moved = victim.rename(victim.with_name(victim.name + "-saved"))
        if damage == "leaf":
            victim.symlink_to(moved)
        else:
            os.mkfifo(victim)
    info = victim.stat()
    identity = (info.st_dev, info.st_ino)
    forbidden = set() if damage == "control" else {identity}
    opened, reads = _focused_check_watch_reads(monkeypatch, forbidden)
    before = card.read_bytes(), _git(root, "write-tree").stdout
    children, boundary = [], []
    monkeypatch.setattr(
        delivery,
        "_run_full_floor",
        lambda *a, **kw: children.append(kw) or {"ok": False},
    )

    class ReachedBoundary(Exception):
        pass

    def finalize(*a, **kw):
        boundary.append(kw)
        raise ReachedBoundary

    monkeypatch.setattr(delivery, "finalize_card", finalize)
    valid = damage == "control" or (target == "history" and damage != "ancestor")
    assert (_final_check_set(card, run, commands) is not None) is valid
    if (
        target == "owner"
        and damage != "control"
        or (target == "index" and damage == "ancestor")
    ):
        with pytest.raises((delivery.DeliveryError, OSError, ValueError)):
            delivery.verify(str(card))
        assert children == []
    else:
        assert delivery.verify(str(card)) == (0 if valid else 1)
        assert len(children) == (0 if valid else 1)
    with pytest.raises(
        ReachedBoundary if valid else (delivery.DeliveryError, OSError, ValueError)
    ):
        delivery.publish(str(card))
    assert bool(boundary) is valid
    delivery.deterministic_commands(run)
    assert not (set(reads) & forbidden)
    assert before == (card.read_bytes(), _git(root, "write-tree").stdout)
    if damage == "fifo":
        assert identity in opened  # fstat, never content, even for zero-byte logs.
        with monkeypatch.context() as mutant:
            mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
            with pytest.raises(AssertionError, match="forbidden content read"):
                if target == "history":
                    delivery.deterministic_commands(run)
                else:
                    delivery.publish(str(card))


@pytest.mark.parametrize("duration", [10**400, -1, True, "long", None])
def test_configured_final_check_legacy_and_lane_compatibility(
    tmp_path, monkeypatch, duration
):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true", "true"]
    )
    assert delivery.run_evidence("focused", ["true"]) == 0
    assert delivery.verify(str(card)) == 0
    pre = (run / "preverification.json").read_bytes()
    final = delivery.load_json(run / "verification.json")
    assert final["commands"][0]["record"] != final["commands"][1]["record"]
    final["commands"][1]["record"] = final["commands"][0]["record"].replace(
        "/cycle-", "/./cycle-"
    )
    delivery.write_json(run / "verification.json", final)
    assert _final_check_set(card, run, commands) is None
    legacy = {
        "commands": [
            {"command": "legacy", "exit_code": 0, "duration_seconds": duration},
            {"command": "valid", "exit_code": 0, "duration_seconds": 1.25},
            None,
            {"command": []},
        ]
    }
    index = run / "verification/cycle-02/verification.json"
    delivery.write_json(index, legacy)
    saved = index.read_bytes()
    rows = [
        row
        for row in delivery.deterministic_commands(run)
        if row["source"] == "final-verification"
    ]
    assert rows[-3]["command"] == "legacy" and rows[-3]["duration_seconds"] is None
    assert rows[-2]["command"] == "valid" and rows[-2]["duration_seconds"] == 1.25
    delivery.build_metrics(run)
    assert (
        index.read_bytes() == saved
        and (run / "preverification.json").read_bytes() == pre
    )
    delivery.require_current_successful_preverification(
        card, run, stage="compatibility"
    )
    assert len(delivery.focused_evidence_summaries(run)) == 1


def test_configured_final_check_missing_owner(tmp_path, monkeypatch):
    root, card, run, _ = _configured_final_check_fixture(tmp_path, monkeypatch)
    owner = run / "run.json"
    owner.unlink()
    with pytest.raises(delivery.DeliveryError):
        delivery.verify(str(card))
    assert not (run / "verification").exists()


@pytest.mark.parametrize(
    "foreign", ["pre_review", "focused", "run", "card", "attempt", "path"]
)
def test_configured_final_check_repair_foreign_metrics(tmp_path, monkeypatch, foreign):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true", "true"]
    )
    assert delivery.run_evidence("own-focus", ["true"]) == 0
    assert delivery.verify(str(card)) == 0
    original_final = delivery.load_json(run / "verification.json")
    # Two real identical shell texts are still two distinct final invocations.
    original_rows = delivery.deterministic_commands(run)
    original_metrics = delivery.build_metrics(run)
    assert original_metrics["deterministic_command_count"] == 4
    assert [row["source"] for row in original_rows].count("final-verification") == 2
    if foreign == "pre_review":
        record = (
            root
            / delivery.load_json(run / "preverification.json")["commands"][0]["record"]
        )
    elif foreign == "focused":
        record = next((run / "focused-evidence").glob("*.json"))
    else:
        actual = root / original_final["commands"][0]["record"]
        item = delivery.load_json(actual)
        parent = run.with_name("foreign-run") if foreign == "path" else run / "copied"
        parent.mkdir()
        record = parent / actual.name
        item["log"] = delivery.repo_relative(record.with_suffix(".log"))
        if foreign == "run":
            item["run_id"] = "foreign"
        elif foreign == "card":
            item["card"] = f"{FIXTURE_BOARD}/3.inprogress/foreign.md"
        elif foreign == "attempt":
            item["attempt_id"] = "0" * 32
        delivery.write_json(record, item)
        record.with_suffix(".log").write_bytes(actual.with_suffix(".log").read_bytes())
    copied = {
        **original_final,
        "commands": [
            {
                "command": "true",
                "exit_code": 0,
                "record": delivery.repo_relative(record),
            }
        ],
        "configured_commands": ["true"],
    }
    delivery.write_json(run / "verification/cycle-02/verification.json", copied)
    delivery.write_json(run / "verification.json", copied)
    # metrics.json is the explicitly regenerated report, not retained execution history.
    history = {
        p: p.read_bytes()
        for p in run.rglob("*")
        if p.is_file() and p != run / "metrics.json"
    }
    assert (
        delivery._verified_command_set(
            run / "verification.json",
            run,
            card,
            delivery.payload_fingerprint(),
            ["true"],
            "final",
        )
        is None
    )
    assert delivery.deterministic_commands(run) == original_rows
    metrics = delivery.build_metrics(run)
    assert (
        metrics["deterministic_command_count"]
        == original_metrics["deterministic_command_count"]
    )
    assert (
        metrics["timing"]["deterministic_check_seconds"]
        == original_metrics["timing"]["deterministic_check_seconds"]
    )
    assert all(p.read_bytes() == data for p, data in history.items())


@pytest.mark.parametrize("damage", ["missing", "tampered"])
def test_configured_final_check_repair_owned_metrics(tmp_path, monkeypatch, damage):
    root, card, run, commands = _configured_final_check_fixture(tmp_path, monkeypatch)
    assert delivery.verify(str(card)) == 0
    before = delivery.deterministic_commands(run)
    metrics = delivery.build_metrics(run)
    proof = _final_check_set(card, run, commands)
    log = root / proof.receipts[0][0]["log"]
    if damage == "missing":
        log.unlink()
    else:
        log.write_bytes(b"corrupt")
    history = {
        p: p.read_bytes()
        for p in run.rglob("*")
        if p.is_file() and p != run / "metrics.json"
    }
    assert _final_check_set(card, run, commands) is None
    assert (
        delivery.deterministic_commands(run) == before
    )  # Exact fields and intact sibling.
    after = delivery.build_metrics(run)
    assert (
        after["deterministic_command_count"]
        == metrics["deterministic_command_count"]
        == 3
    )
    assert (
        after["timing"]["deterministic_check_seconds"]
        == metrics["timing"]["deterministic_check_seconds"]
    )
    assert all(p.read_bytes() == data for p, data in history.items())


@pytest.mark.parametrize("damage", ["control", "leaf", "ancestor", "fifo"])
def test_configured_final_check_publisher_repeated_owner_read(
    tmp_path, monkeypatch, damage
):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true"]
    )
    assert delivery.verify(str(card)) == 0
    select = delivery._manifest_for_run
    forbidden, boundary = set(), []
    opened, reads = _focused_check_watch_reads(monkeypatch, forbidden)
    checkpoint = 0

    def repeated(*args):
        nonlocal checkpoint
        checkpoint = len(reads)
        owner = run / "run.json"
        if damage == "ancestor":
            moved = run.rename(run.with_name("saved-run"))
            run.symlink_to(moved, target_is_directory=True)
        elif damage != "control":
            moved = owner.rename(run / "saved-owner.json")
            if damage == "leaf":
                owner.symlink_to(moved)
            else:
                os.mkfifo(owner)
        if damage != "control":
            info = owner.stat()
            forbidden.add((info.st_dev, info.st_ino))
        return select(*args)

    class ReachedBoundary(Exception):
        pass

    def finalize(*a, **kw):
        boundary.append(kw)
        raise ReachedBoundary

    monkeypatch.setattr(delivery, "_manifest_for_run", repeated)
    monkeypatch.setattr(delivery, "finalize_card", finalize)
    before = card.read_bytes(), _git(root, "write-tree").stdout
    with pytest.raises(
        ReachedBoundary if damage == "control" else delivery.DeliveryError
    ):
        delivery.publish(str(card))
    assert bool(boundary) is (damage == "control")
    assert before == (card.read_bytes(), _git(root, "write-tree").stdout)
    assert not (set(reads[checkpoint:]) & forbidden)
    if damage == "fifo":
        assert set(opened) & forbidden
        with monkeypatch.context() as mutant:
            mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
            with pytest.raises(AssertionError, match="forbidden content read"):
                select(card, run)


@pytest.mark.parametrize("target", ["owner", "index", "history", "record"])
@pytest.mark.parametrize("damage", ["malformed", "deep", "duplicate", "nonfinite"])
def test_configured_final_check_bad_json_consumers(
    tmp_path, monkeypatch, target, damage
):
    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["true"]
    )
    assert delivery.verify(str(card)) == 0
    index = run / "verification.json"
    record = root / delivery.load_json(index)["commands"][0]["record"]
    victim = {
        "owner": run / "run.json",
        "index": index,
        "history": run / "verification/cycle-01/verification.json",
        "record": record,
    }[target]
    broken = {
        "malformed": b"\xff",
        "deep": ('{"x":' + "[" * 2000 + "0" + "]" * 2000 + "}").encode(),
        "duplicate": b'{"x":0,"\\u0078":1}',
        "nonfinite": b'{"x":1e400}',
    }[damage]
    victim.write_bytes(broken)
    assert (_final_check_set(card, run, commands) is not None) is (target == "history")
    delivery.deterministic_commands(run)
    assert victim.read_bytes() == broken
    if target != "history":
        before = card.read_bytes(), _git(root, "write-tree").stdout
        with pytest.raises(delivery.DeliveryError):
            delivery.publish(str(card))
        assert before == (card.read_bytes(), _git(root, "write-tree").stdout)


def test_configured_final_check_real_interruption(tmp_path, monkeypatch):
    import sys

    root, card, run, commands = _configured_final_check_fixture(
        tmp_path, monkeypatch, ["touch .runtime/floor-ready; sleep 5", "true"]
    )
    code = (
        _delivery_child_bootstrap(root, run)
        + "import signal, threading, time; "
        f'd.profile=lambda: {{"verification": {{"pre_review_commands": ["true"], "final_commands": {commands!r}}}}}; '
        "\ndef interrupt_when_ready():\n"
        "    deadline=time.monotonic()+5\n"
        "    while not Path('.runtime/floor-ready').exists():\n"
        "        if time.monotonic()>deadline: return\n"
        "        time.sleep(0.01)\n"
        "    os.kill(os.getpid(), signal.SIGINT)\n"
        "timer=threading.Thread(target=interrupt_when_ready); timer.start()\n"
        f"result=d._run_full_floor(Path({str(card)!r}), commands={commands!r}, "
        'root_name="verification", result_name="verification.json", '
        'schema="changerail.final-verification.v1", event_stage="verification", proof_lane="final"); '
        'timer.join(); sys.exit(0 if result["ok"] else 1)'
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, timeout=10
    )
    assert result.returncode == 1
    index = delivery.load_json(run / "verification.json")
    assert len(index["commands"]) == 1
    item = delivery.load_json(root / index["commands"][0]["record"])
    assert item["outcome"] == "interrupted" and item["exit_code"] is None
    assert (
        item["verdict"] == "unconfirmed"
        and _final_check_set(card, run, commands) is None
    )


@pytest.mark.parametrize("damage", ["missing-log", "drift"])
def test_configured_pre_review_check_behavioral_regressions(
    tmp_path, monkeypatch, damage
):
    commands = (
        ["printf changed > tracked.txt", "printf 'baseline\\n' > tracked.txt"]
        if damage == "drift"
        else None
    )
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, commands
    )
    code = delivery.preverify(str(card))
    payload = delivery.load_json(run / "preverification.json")
    if damage == "drift":
        assert code != 0
        assert (root / "tracked.txt").read_text() == "changed"
        assert len(payload["commands"]) == 1
    else:
        assert code == 0
        delivery.require_current_successful_preverification(card, run, stage="test")
        log = root / payload["commands"][0]["log"]
        assert log.read_bytes() == b"stable"
        before = delivery.payload_fingerprint()
        log.unlink()
        assert delivery.payload_fingerprint() == before
        with pytest.raises(delivery.DeliveryError):
            delivery.require_current_successful_preverification(card, run, stage="test")


@pytest.mark.parametrize(
    "command,code",
    [
        ("true", 0),
        ("printf stable", 0),
        ("exit 7", 7),
        ("kill -TERM $$", -15),
    ],
)
def test_configured_pre_review_check_terminal_outcomes(
    tmp_path, monkeypatch, command, code
):
    root, card, run, _ = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, [command, "true"]
    )
    assert delivery.preverify(str(card)) == (0 if code == 0 else 1)
    index = delivery.load_json(run / "preverification.json")
    assert len(index["commands"]) == (2 if code == 0 else 1)
    record = root / index["commands"][0]["record"]
    item, data, current = delivery.read_check_result(record, run, "pre_review")
    assert item["exit_code"] == code and item["outcome"] == "exit"
    assert current is (code == 0)
    assert data == (b"stable" if command == "printf stable" else b"")
    assert item["before"] == item["fingerprint"] == delivery.payload_fingerprint()
    assert delivery.focused_evidence_summaries(run) == []


@pytest.mark.parametrize(
    "damage",
    [
        "control",
        "missing",
        "extra",
        "reordered",
        "duplicate",
        "absolute",
        "traversal",
        "unknown",
        "unknown-field",
        "bool-exit",
        "negative-duration",
        "date",
        "non-utc",
        "deep",
        "duplicate-key",
        "nested-duplicate",
        "nan",
        "running",
        "foreign-run",
        "foreign-card",
        "foreign-attempt",
        "foreign-lane",
        "argv",
        "shell",
        "stale",
        "missing-log",
        "tampered-log",
        "truncated-log",
        "legacy",
        "bad-index",
    ],
)
def test_configured_pre_review_check_set_and_safe_reads(tmp_path, monkeypatch, damage):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    assert delivery.preverify(str(card)) == 0
    index_path = run / "preverification.json"
    _damage_configured_check(root, index_path, commands, damage, "final")
    assert delivery._successful_verification_matches(
        index_path,
        card=card,
        run_dir=run,
        lane="pre_review",
        fingerprint=delivery.payload_fingerprint(),
        commands=commands,
    ) is (damage == "control")
    if damage == "control":
        delivery.require_current_successful_preverification(card, run, stage="test")
    else:
        with pytest.raises(delivery.DeliveryError):
            delivery.require_current_successful_preverification(card, run, stage="test")
    assert all(
        row["proof_status"] == "unconfirmed"
        for row in delivery.deterministic_commands(run)
    )
    delivery.build_metrics(run)


def _damage_configured_check(root, index_path, commands, damage, foreign_lane):
    index = delivery.load_json(index_path)
    path = root / index["commands"][0]["record"]
    item = delivery.load_json(path)
    if damage == "missing":
        index["commands"].pop()
    elif damage == "extra":
        index["commands"].append(index["commands"][0])
    elif damage == "reordered":
        index["commands"].reverse()
    elif damage == "duplicate":
        index["commands"][1]["record"] = index["commands"][0]["record"]
    elif damage == "absolute":
        index["commands"][0]["record"] = str(path)
    elif damage == "traversal":
        index["commands"][0]["record"] = ".runtime/../" + index["commands"][0]["record"]
    elif damage == "unknown":
        item["schema"] = "future"
    elif damage == "unknown-field":
        item["arbitrary"] = True
    elif damage == "bool-exit":
        item["exit_code"] = False
    elif damage == "negative-duration":
        item["duration_seconds"] = -1
    elif damage == "date":
        item["observed_at"] = "tomorrow"
    elif damage == "non-utc":
        item["observed_at"] = "2026-09-06T00:00:00+03:00"
    elif damage == "running":
        item = {
            k: v
            for k, v in item.items()
            if k
            in {
                "schema",
                "state",
                "attempt_id",
                "run_id",
                "card",
                "lane",
                "command_identity",
                "label",
                "command",
                "started_at",
                "before",
            }
        }
        item["state"] = "running"
    elif damage.startswith("foreign-"):
        item[
            {
                "foreign-run": "run_id",
                "foreign-card": "card",
                "foreign-attempt": "attempt_id",
                "foreign-lane": "lane",
            }[damage]
        ] = foreign_lane if damage == "foreign-lane" else "foreign"
    elif damage == "argv":
        item["command_identity"]["argv"][-1] = "false"
    elif damage == "shell":
        item["command_identity"]["shell_text"] = "false"
    elif damage == "stale":
        item["fingerprint"]["payload_fingerprint"] = "sha256:" + "0" * 64
    elif damage == "legacy":
        index["commands"] = [{"command": c, "exit_code": 0} for c in commands]
    elif damage == "bad-index":
        index["commands"] = [None, 3, {"command": []}]
    elif damage == "index-date":
        index["verified_at"] = ["tomorrow"]
    elif damage == "index-schema":
        index["schema"] = "future"
    elif damage == "index-bool-exit":
        index["commands"][0]["exit_code"] = False
    elif damage == "early-finish":
        item["observed_at"] = "2000-01-01T00:00:00Z"
    elif damage == "nested-unknown":
        item["command_identity"]["untrusted"] = True
    elif damage == "log-absolute":
        item["log"] = str(path.with_suffix(".log"))
    elif damage == "log-traversal":
        item["log"] = ".runtime/../" + item["log"]
    delivery.write_json(index_path, index)
    delivery.write_json(path, item)
    if damage == "deep":
        path.write_text('{"x":' + "[" * 2000 + "0" + "]" * 2000 + "}")
    elif damage == "duplicate-key":
        path.write_text(
            path.read_text().replace(
                '"exit_code": 0', '"exit_code": 0, "exit_\\u0063ode": 0'
            )
        )
    elif damage == "nested-duplicate":
        path.write_text(
            path.read_text().replace(
                '"kind": "shell"', '"kind": "shell", "kind": "shell"'
            )
        )
    elif damage == "nan":
        path.write_text(path.read_text().replace('"exit_code": 0', '"exit_code": NaN'))
    elif damage in {"infinity", "overflow"}:
        item["duration_seconds"] = "NONFINITE"
        path.write_text(
            json.dumps(item).replace(
                '"NONFINITE"', "Infinity" if damage == "infinity" else "1e400"
            )
        )
    elif damage == "missing-log":
        path.with_suffix(".log").unlink()
    elif damage == "tampered-log":
        path.with_suffix(".log").write_bytes(b"STABLE")
    elif damage == "truncated-log":
        path.with_suffix(".log").write_bytes(b"stab")


@pytest.mark.parametrize("target", ["owner", "index", "record", "log"])
@pytest.mark.parametrize("damage", ["leaf", "ancestor", "fifo"])
def test_configured_pre_review_check_nonregular_read_order(
    tmp_path, monkeypatch, target, damage
):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, ["true"]
    )
    assert delivery.preverify(str(card)) == 0
    index = run / "preverification.json"
    record = root / delivery.load_json(index)["commands"][0]["record"]
    victim = {
        "owner": run / "run.json",
        "index": index,
        "record": record,
        "log": record.with_suffix(".log"),
    }[target]
    assert delivery._verified_command_set(
        index, run, card, delivery.payload_fingerprint(), commands, "pre_review"
    )
    if damage == "ancestor":
        old = victim.parent
        moved = old.rename(old.with_name(old.name + "-saved"))
        old.symlink_to(moved, target_is_directory=True)
    else:
        moved = victim.rename(victim.with_name(victim.name + "-saved"))
        if damage == "leaf":
            victim.symlink_to(moved)
        else:
            os.mkfifo(victim)
    info = victim.stat()
    identity = (info.st_dev, info.st_ino)
    opened, reads = _focused_check_watch_reads(monkeypatch, {identity})
    with pytest.raises(delivery.DeliveryError):
        delivery.require_current_successful_preverification(card, run, stage="test")
    delivery.deterministic_commands(run)
    assert identity not in reads
    if target == "owner":
        with pytest.raises(delivery.DeliveryError):
            delivery.preverify(str(card))
    if damage == "fifo":
        assert identity in opened
        with monkeypatch.context() as mutant:
            mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
            with pytest.raises(AssertionError, match="forbidden content read"):
                delivery.require_current_successful_preverification(
                    card, run, stage="test"
                )


def test_configured_pre_review_check_composed_reuse(tmp_path, monkeypatch):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    counter = run / "count"
    commands[:] = ["printf x >> " + str(counter), "true"]
    assert delivery.preverify(str(card)) == 0 and counter.read_bytes() == b"x"
    history = {
        p: p.read_bytes() for p in (run / "preverification").rglob("*") if p.is_file()
    }
    assert delivery.preverify(str(card)) == 0 and counter.read_bytes() == b"x"
    delivery.require_current_successful_preverification(card, run, stage="test")
    assert len(delivery.deterministic_commands(run)) == 2
    assert delivery.focused_evidence_summaries(run) == []
    assert all(p.read_bytes() == data for p, data in history.items())
    record = (
        root / delivery.load_json(run / "preverification.json")["commands"][0]["record"]
    )
    record.with_suffix(".log").unlink()
    history.pop(record.with_suffix(".log"))
    assert delivery.preverify(str(card)) == 0 and counter.read_bytes() == b"xx"
    assert len(list((run / "preverification").glob("cycle-*"))) == 2
    assert all(p.read_bytes() == data for p, data in history.items())


def test_configured_pre_review_check_legacy_and_deliberate_repair(
    tmp_path, monkeypatch
):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch
    )
    source = root / "src/sample.py"
    source.parent.mkdir()
    source.write_text("import sys\nimport os\n")
    excluded = root / "outside.py"
    excluded.write_bytes(source.read_bytes())
    tracked = root / "tests/unchanged.py"
    tracked.parent.mkdir()
    tracked.write_bytes(source.read_bytes())
    _git(root, "add", "--", "tests/unchanged.py")
    _git(root, "commit", "-m", "excluded unchanged source")
    commands[:] = ["uv run ruff check --select I src/sample.py"]
    before = delivery.payload_fingerprint()
    original = source.read_bytes()
    assert delivery.preverify(str(card)) != 0
    history = {
        p: p.read_bytes() for p in (run / "preverification").rglob("*") if p.is_file()
    }
    assert delivery.run_safe_handoff_repair(run) is True
    assert source.read_bytes() == b"import os\nimport sys\n" != original
    assert excluded.read_bytes() == tracked.read_bytes() == original
    assert delivery.payload_fingerprint() != before
    repair = delivery.load_json(run / "deterministic-repair.json")
    assert repair["command"]["exit_code"] == 0 and repair["changed_payload"] is True
    assert repair["paths"] == ["src/sample.py"]
    assert all(p.read_bytes() == data for p, data in history.items())
    with pytest.raises(delivery.DeliveryError):
        delivery.require_current_successful_preverification(card, run, stage="repair")
    assert delivery.preverify(str(card)) == 0


@pytest.mark.parametrize(
    "fault", ["spawn", "interruption", "log", "terminal", "terminal-interruption"]
)
def test_configured_pre_review_check_contract_and_retention(
    tmp_path, monkeypatch, capsys, fault
):
    _configured_check_retention(tmp_path, monkeypatch, capsys, fault, "pre_review")


@pytest.mark.parametrize(
    "fault", ["spawn", "interruption", "log", "terminal", "terminal-interruption"]
)
def test_configured_final_check_contract_and_retention(
    tmp_path, monkeypatch, capsys, fault
):
    _configured_check_retention(tmp_path, monkeypatch, capsys, fault, "final")


def _configured_check_retention(tmp_path, monkeypatch, capsys, fault, lane):
    fixture = (
        _configured_final_check_fixture
        if lane == "final"
        else _configured_pre_review_check_fixture
    )
    root, card, run, commands = fixture(tmp_path, monkeypatch, ["true", "true"])
    consume = delivery.verify if lane == "final" else delivery.preverify
    filename = "verification.json" if lane == "final" else "preverification.json"
    original_run, original_write, original_finish = (
        subprocess.run,
        delivery.write_json,
        delivery.finish_check_result,
    )
    children = []

    def run_child(argv, *args, **kwargs):
        if argv[:2] == ["bash", "-lc"]:
            children.append(argv)
            if fault == "spawn":
                raise OSError("controlled spawn fault")
            if fault == "interruption":
                raise KeyboardInterrupt
        return original_run(argv, *args, **kwargs)

    def write(path, value):
        if (
            path.parent.name.startswith("cycle-")
            and value.get("schema") == "changerail.check-result.v1"
        ):
            if fault == "terminal":
                raise OSError("controlled terminal fault")
            if fault == "terminal-interruption":
                raise KeyboardInterrupt
        return original_write(path, value)

    def finish(path, item, output):
        if fault == "log":
            path.with_suffix(".log").mkdir()
        return original_finish(path, item, output)

    monkeypatch.setattr(subprocess, "run", run_child)
    monkeypatch.setattr(delivery, "write_json", write)
    monkeypatch.setattr(delivery, "finish_check_result", finish)
    assert consume(str(card)) == 1
    index = delivery.load_json(run / filename)
    assert len(children) == len(index["commands"]) == 1 and index["ok"] is False
    expected_exit = None if fault in {"spawn", "interruption"} else 0
    assert index["commands"][0]["exit_code"] == expected_exit
    path = root / index["commands"][0]["record"]
    item = delivery.load_json(path)
    if fault in {"terminal", "terminal-interruption"}:
        assert item["state"] == "running"
        assert "observed exit=0" in capsys.readouterr().err
    else:
        assert item["exit_code"] == expected_exit and item["verdict"] == "unconfirmed"
        assert item["outcome"] == {
            "spawn": "spawn_failure",
            "interruption": "interrupted",
        }.get(fault, "exit")
    assert (
        delivery._verified_command_set(
            run / filename, run, card, delivery.payload_fingerprint(), commands, lane
        )
        is None
    )


def test_configured_pre_review_check_missing_owner_and_repeated_identity(
    tmp_path, monkeypatch
):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, ["true", "true"]
    )
    owner = (run / "run.json").read_bytes()
    (run / "run.json").unlink()
    with pytest.raises(delivery.DeliveryError):
        delivery.preverify(str(card))
    assert not (run / "preverification").exists()
    (run / "run.json").write_bytes(owner)
    assert delivery.preverify(str(card)) == 0
    index = run / "preverification.json"
    payload = delivery.load_json(index)
    first, second = [row["record"] for row in payload["commands"]]
    assert first != second
    payload["commands"][1]["record"] = first.replace("/cycle-", "/./cycle-")
    delivery.write_json(index, payload)
    assert (
        delivery._verified_command_set(
            index, run, card, delivery.payload_fingerprint(), commands, "pre_review"
        )
        is None
    )
    assert (
        delivery._verified_command_set(
            index, run, card, delivery.payload_fingerprint(), commands, "final"
        )
        is None
    )


def test_configured_pre_review_check_real_interruption(tmp_path, monkeypatch):
    import sys

    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, ["sleep 0.4", "true"]
    )
    code = (
        _delivery_child_bootstrap(root, run)
        + "import signal, threading; "
        f'd.profile=lambda: {{"verification": {{"pre_review_commands": {commands!r}, "final_commands": ["true"]}}}}; '
        "timer=threading.Timer(0.15, lambda: os.kill(os.getpid(), signal.SIGINT)); timer.start(); "
        f"result=d._run_full_floor(Path({str(card)!r}), commands={commands!r}, "
        'root_name="preverification", result_name="preverification.json", '
        'schema="changerail.pre-review-verification.v1", event_stage="preverification", proof_lane="pre_review"); '
        'timer.join(); sys.exit(0 if result["ok"] else 1)'
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, timeout=10
    )
    assert result.returncode == 1
    index = delivery.load_json(run / "preverification.json")
    assert len(index["commands"]) == 1
    item = delivery.load_json(root / index["commands"][0]["record"])
    assert item["outcome"] == "interrupted" and item["exit_code"] is None
    assert item["verdict"] == "unconfirmed"


@pytest.mark.parametrize("damage", ["missing-log", "tampered-log"])
def test_configured_pre_review_check_repair_metrics_keep_damaged_and_sibling(
    tmp_path, monkeypatch, damage
):
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    assert delivery.preverify(str(card)) == 0
    before = delivery.deterministic_commands(run)
    assert len(before) == 2
    index = delivery.load_json(run / "preverification.json")
    first = root / index["commands"][0]["record"]
    receipt = delivery.load_json(first)
    assert before[0]["finished_at"] == receipt["observed_at"]
    log = first.with_suffix(".log")
    if damage == "missing-log":
        log.unlink()
    else:
        log.write_bytes(b"corrupt")
    retained = {
        p: p.read_bytes() for p in (run / "preverification").rglob("*") if p.is_file()
    }
    after = delivery.deterministic_commands(run)
    assert after == before  # Includes exact command/exit/duration/time and sibling.
    assert all(row["proof_status"] == "unconfirmed" for row in after)
    assert delivery.build_metrics(run)["deterministic_command_count"] == 2
    assert delivery.focused_evidence_summaries(run) == []
    assert all(p.read_bytes() == data for p, data in retained.items())
    with pytest.raises(delivery.DeliveryError):
        delivery.require_current_successful_preverification(card, run, stage="damage")


@pytest.mark.parametrize("duration", [10**400, -1, True, "long", None])
def test_configured_pre_review_check_repair_legacy_numbers(
    tmp_path, monkeypatch, duration
):
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    cycle = run / "preverification/cycle-01/preverification.json"
    delivery.write_json(
        cycle,
        {
            "commands": [
                {"command": "old", "exit_code": 0, "duration_seconds": duration},
                {"command": "valid", "exit_code": 0, "duration_seconds": 1.25},
                None,
                {"command": []},
            ]
        },
    )
    original = cycle.read_bytes()
    rows = delivery.deterministic_commands(run)
    assert rows[0]["duration_seconds"] is None
    assert rows[1]["command"] == "valid" and rows[1]["duration_seconds"] == 1.25
    metrics = delivery.build_metrics(run)
    assert metrics["timing"]["deterministic_check_seconds"] == 1.25
    assert cycle.read_bytes() == original


@pytest.mark.parametrize("damage", ["leaf", "ancestor", "fifo"])
def test_configured_pre_review_check_repair_historical_index_read_order(
    tmp_path, monkeypatch, damage
):
    root, card, run, _ = _configured_pre_review_check_fixture(tmp_path, monkeypatch)
    assert delivery.preverify(str(card)) == 0
    victim = run / "preverification/cycle-01/preverification.json"
    assert len(delivery.deterministic_commands(run)) == 2
    if damage == "ancestor":
        old = victim.parent
        moved = old.rename(old.with_name("saved"))
        old.symlink_to(moved, target_is_directory=True)
    else:
        moved = victim.rename(victim.with_name("saved.json"))
        if damage == "leaf":
            victim.symlink_to(moved)
        else:
            os.mkfifo(victim)
    info = victim.stat()
    identity = (info.st_dev, info.st_ino)
    opened, reads = _focused_check_watch_reads(monkeypatch, {identity})
    assert delivery.deterministic_commands(run) == []
    assert identity not in reads
    if damage == "fifo":
        assert identity in opened
        with monkeypatch.context() as mutant:
            mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
            with pytest.raises(AssertionError, match="forbidden content read"):
                delivery.deterministic_commands(run)


@pytest.mark.parametrize("change", [False, True])
def test_configured_pre_review_check_repair_independent_aggregate_drift(
    tmp_path, monkeypatch, change
):
    root, card, run, commands = _configured_pre_review_check_fixture(
        tmp_path, monkeypatch, ["true", "true"]
    )
    original = (root / "tracked.txt").read_bytes()
    before = delivery.payload_fingerprint()
    allocate = delivery._next_verification_cycle

    def between_intervals(path):
        cycle = allocate(path)
        if change:
            (root / "tracked.txt").write_bytes(b"between aggregate and first child")
        return cycle

    monkeypatch.setattr(delivery, "_next_verification_cycle", between_intervals)
    code = delivery.preverify(str(card))
    index = delivery.load_json(run / "preverification.json")
    assert len(index["commands"]) == 2
    assert all(
        delivery.read_check_result(root / row["record"], run, "pre_review")[2]
        for row in index["commands"]
    )
    assert (delivery.payload_fingerprint() != before) is change
    assert (root / "tracked.txt").read_bytes() == (
        b"between aggregate and first child" if change else original
    )
    assert code == (
        1 if change else 0
    )  # Removing only aggregate equality makes this fail.
    assert index["ok"] is (not change)
    if change:
        with pytest.raises(delivery.DeliveryError):
            delivery.require_current_successful_preverification(
                card, run, stage="aggregate"
            )


@pytest.mark.parametrize("entry", ["verify", "review-reopen"])
@pytest.mark.parametrize("damage", ["control", "leaf", "ancestor", "fifo"])
def test_configured_pre_review_check_repair_actual_prerequisite_reads(
    tmp_path, monkeypatch, entry, damage
):
    root, card, run = _review_fixture(tmp_path, monkeypatch)
    # This test exercises receipt read ordering, not the dedicated
    # implementation-role refusal (covered below).  Keep its direct
    # runner-owned consumer call outside an inherited implementation session.
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    _write_matching_preverification(card, run)
    verdict = delivery.verdict_template(str(card))["template"]
    verdict["acceptance"][0]["evidence"] = ["fixture"]
    delivery.write_json(delivery.verdict_path(card.stem), verdict)
    # For review we force a new (otherwise legitimate) cycle at the model boundary.
    if entry == "review-reopen":
        delivery.verdict_path(card.stem).unlink()
    child_calls = []
    monkeypatch.setattr(
        delivery,
        "_run_full_floor",
        lambda *args, **kwargs: child_calls.append("floor") or {"ok": True},
    )

    def model(**kwargs):
        child_calls.append("model")
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", model)
    owner = run / "run.json"
    outside = root.parent / "owner-copy.json"
    outside.write_bytes(owner.read_bytes())
    forbidden = set()
    read_checkpoint = 0

    def damage_owner():
        nonlocal owner, read_checkpoint
        if entry == "review-reopen":
            read_checkpoint = len(
                reads
            )  # Earlier reads were of the still-regular owner.
        if damage == "leaf":
            owner.unlink()
            owner.symlink_to(outside)
        elif damage == "fifo":
            owner.unlink()
            os.mkfifo(owner)
        elif damage == "ancestor":
            moved = run.rename(run.with_name("saved-run"))
            run.symlink_to(moved, target_is_directory=True)
        if damage != "control":
            info = owner.stat()
            forbidden.add((info.st_dev, info.st_ino))

    if entry == "review-reopen":
        select_manifest = delivery._manifest_for_run

        def repeated_read(*args):
            damage_owner()
            return select_manifest(*args)

        monkeypatch.setattr(delivery, "_manifest_for_run", repeated_read)
    else:
        damage_owner()
    opened, reads = _focused_check_watch_reads(monkeypatch, forbidden)
    consume = delivery.verify if entry == "verify" else delivery.run_review
    if damage == "control":
        assert consume(str(card)) == 0 and len(child_calls) == 1
    else:
        with pytest.raises((delivery.DeliveryError, OSError, ValueError)):
            consume(str(card))
        assert not child_calls and not (set(reads[read_checkpoint:]) & forbidden)
        if damage == "fifo":
            assert set(opened) & forbidden
            with monkeypatch.context() as mutant:
                mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
                with pytest.raises(AssertionError, match="forbidden content read"):
                    consume(str(card))


def _focused_check_fixture(tmp_path, monkeypatch):
    root = _repository(tmp_path, monkeypatch)
    card = root / f"{FIXTURE_BOARD}/3.inprogress/focused.md"
    card.parent.mkdir(parents=True)
    card.write_text(_card_text())
    run = root / ".runtime/changerail/runs/focused-run"
    run.mkdir(parents=True)
    # These old receipt/owner tests intentionally exercise low-level consumer
    # behavior.  They still enter it through the real strict C4 reader: create
    # a complete, independently declared exact-v1 source rather than relying
    # on the historical unversioned fixture shortcut.
    _legacy_observed_anchor(run, card)
    monkeypatch.setenv("CHRL_RUN_DIR", str(run))
    schema = root / "tools/changerail/schemas/review-verdict.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_bytes(delivery.VERDICT_SCHEMA_PATH.read_bytes())
    monkeypatch.setattr(delivery, "VERDICT_SCHEMA_PATH", schema)
    paths = delivery.changed_paths()
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": run.name,
        "baseline_head": delivery.git("rev-parse", "HEAD").stdout.strip(),
        "created_at": "2026-09-04T00:00:00Z",
        "card": {"id": card.stem, "path": delivery.repo_relative(card)},
        "paths": paths,
        "fingerprint": delivery.payload_fingerprint(paths),
        "path_fingerprints": delivery.path_fingerprints(paths),
    }
    delivery.write_json(delivery.manifest_path(card.stem), manifest)
    delivery.write_json(run / "manifest.json", manifest)
    _trust_legacy_observed_fixture(run, card)
    delivery.capture_manifest(str(card))
    _trust_legacy_observed_fixture(run, card)
    return root, card, run


@pytest.mark.parametrize("change", [False, True])
def test_focused_check_terminal_outcomes(tmp_path, monkeypatch, change):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    before = delivery.payload_fingerprint()
    command = [
        sys.executable,
        "-c",
        "from pathlib import Path; Path('tracked.txt').write_text('changed')"
        if change
        else "pass",
    ]
    code = delivery.run_evidence("behavioral-red", command)
    assert (root / "tracked.txt").read_text() == ("changed" if change else "baseline\n")
    assert (delivery.payload_fingerprint() != before) is change
    assert (
        code != 0
    ) is change  # Behavioral assertion precedes any new-format assertion.


def _focused_check_core_record(tmp_path, monkeypatch, output=b""):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    command = {"kind": "argv", "argv": ["true"]}
    path, item = delivery.start_check_result(run, "focused", "core", command)
    assert delivery.read_check_result(path, run, "focused", command)[2] is False
    observed = subprocess.run(
        command["argv"], cwd=root, capture_output=True, check=False
    )
    item.update(
        state="terminal",
        observed_at=delivery.utc_now(),
        duration_seconds=0,
        fingerprint=delivery.payload_fingerprint(),
        outcome="exit",
        exit_code=observed.returncode,
        verdict="verified",
        reason="stable",
    )
    delivery.finish_check_result(path, item, observed.stdout + observed.stderr + output)
    assert delivery.read_check_result(path, run, "focused", command) == (
        item,
        output,
        True,
    )
    return root, run, path, item


@pytest.mark.parametrize(
    "corruption",
    [
        "control",
        "unknown-version",
        "unknown-field",
        "bool-exit",
        "negative-duration",
        "bad-date",
        "non-utc",
        "nan",
        "infinity",
        "overflow",
        "duplicate",
        "nested-duplicate",
        "missing-log",
        "tampered-log",
        "truncated-log",
        "running",
        "foreign-run",
        "foreign-card",
        "foreign-invocation",
        "foreign-lane",
        "foreign-command",
        "stale",
        "early-finish",
        "nested-unknown",
    ],
)
def test_focused_check_contract_and_retention(tmp_path, monkeypatch, corruption):
    from jsonschema import ValidationError

    root, run, path, item = _focused_check_core_record(
        tmp_path, monkeypatch, b"complete output"
    )
    log = path.with_suffix(".log")
    if corruption == "unknown-version":
        item["schema"] = "future"
    elif corruption == "unknown-field":
        item["extra"] = True
    elif corruption == "bool-exit":
        item["exit_code"] = False
    elif corruption == "negative-duration":
        item["duration_seconds"] = -1
    elif corruption == "bad-date":
        item["observed_at"] = "2026-02-31T10:00:00Z"
    elif corruption == "non-utc":
        item["observed_at"] = "2026-09-06T14:00:00+01:00"
    elif corruption == "early-finish":
        item["observed_at"] = "2000-01-01T00:00:00Z"
    elif corruption == "nested-unknown":
        item["command_identity"]["extra"] = "not allowed"
    elif corruption in {"nan", "infinity", "overflow"}:
        item["duration_seconds"] = float("nan") if corruption == "nan" else float("inf")
    elif corruption == "missing-log":
        log.unlink()
    elif corruption == "tampered-log":
        log.write_bytes(b"changed output!")
    elif corruption == "truncated-log":
        log.write_bytes(b"complete")
    elif corruption == "running":
        item["state"] = "running"
    elif corruption.startswith("foreign-"):
        key = {
            "foreign-run": "run_id",
            "foreign-card": "card",
            "foreign-invocation": "attempt_id",
            "foreign-lane": "lane",
            "foreign-command": "command",
        }[corruption]
        item[key] = "final" if key == "lane" else "f" * 32
    elif corruption == "stale":
        (root / "tracked.txt").write_text("stale")
    delivery.write_json(path, item)
    if corruption == "duplicate":
        path.write_text(
            path.read_text().replace(
                '"schema":', '"sch\\u0065ma": "duplicate", "schema":'
            )
        )
    elif corruption == "nested-duplicate":
        path.write_text(
            path.read_text().replace(
                '"head_commit":', '"head_commit": "duplicate", "head_commit":', 1
            )
        )
    elif corruption == "overflow":
        path.write_text(path.read_text().replace("Infinity", "1e9999"))
    if corruption in {"control", "stale"}:
        assert delivery.read_check_result(path, run, "focused")[2] is (
            corruption == "control"
        )
    else:
        with pytest.raises((ValueError, OSError, ValidationError)):
            delivery.read_check_result(path, run, "focused")


@pytest.mark.parametrize(
    "target", ["record", "log", "ancestor", "fifo", "absolute", "traversal"]
)
def test_focused_check_core_safe_reads(tmp_path, monkeypatch, target):
    root, run, path, item = _focused_check_core_record(tmp_path, monkeypatch)
    outside = root.parent / "outside"
    outside.write_bytes(b"never read")
    if target in {"record", "log"}:
        victim = path if target == "record" else path.with_suffix(".log")
        victim.unlink()
        victim.symlink_to(outside)
    elif target == "ancestor":
        directory = path.parent.rename(root.parent / "foreign-evidence")
        path.parent.symlink_to(directory, target_is_directory=True)
    elif target == "fifo":
        path.unlink()
        os.mkfifo(path)
    else:
        item["log"] = str(outside) if target == "absolute" else "../outside"
        delivery.write_json(path, item)
    original = os.fdopen

    def no_outside_content(fd, *args, **kwargs):
        info = os.fstat(fd)
        assert info.st_ino != outside.stat().st_ino
        return original(fd, *args, **kwargs)

    monkeypatch.setattr(os, "fdopen", no_outside_content)
    with pytest.raises((ValueError, OSError)):
        delivery.read_check_result(path, run, "focused")


@pytest.mark.parametrize("fault", ["log", "completion"])
def test_focused_check_core_storage_faults(tmp_path, monkeypatch, fault):
    root, run, path, item = _focused_check_core_record(tmp_path, monkeypatch)
    path2, running = delivery.start_check_result(
        run, "focused", "fault", item["command_identity"]
    )
    item.update(attempt_id=running["attempt_id"])
    if fault == "log":
        path2.with_suffix(".log").mkdir()
    else:
        original = delivery.write_json

        def fail_completion(dest, value):
            if dest == path2:
                raise OSError("injected terminal storage failure")
            return original(dest, value)

        monkeypatch.setattr(delivery, "write_json", fail_completion)
    with pytest.raises(OSError):
        delivery.finish_check_result(path2, item, b"")
    assert item["exit_code"] == 0
    assert delivery.read_check_result(path2, run, "focused")[2] is False


@pytest.mark.parametrize("drift", [False, True])
def test_focused_check_composed_reuse(tmp_path, monkeypatch, drift):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    counter = run / "counter"
    command = [
        sys.executable,
        "-c",
        "from pathlib import Path; p=Path(" + repr(str(counter)) + "); "
        "p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
        + ("Path('tracked.txt').write_text('drift')" if drift else "print('observed')"),
    ]
    assert delivery.run_evidence("compose", command) == (1 if drift else 0)
    path = next((run / "focused-evidence").glob("*.json"))
    receipt, log, current = delivery.read_check_result(path, run, "focused")
    assert receipt["exit_code"] == 0 and current is not drift
    original = {p: p.read_bytes() for p in (run / "focused-evidence").iterdir()}
    summary = delivery.focused_evidence_summaries(run)[0]
    assert summary["proof_status"] == ("unconfirmed" if drift else "current")
    assert delivery.deterministic_commands(run)[0]["command"] == summary["command"]
    metrics = delivery.build_metrics(run)
    assert metrics["run_id"] == run.name
    if not drift:
        with pytest.raises(delivery.DeliveryError, match=path.name):
            delivery.run_evidence("repeat", command)
        assert counter.read_text() == "x"
    # The recovery consumer must receive a real current source, including the
    # intentional payload-drift branch above, before it creates its next run.
    _refresh_exact_legacy_fixture(card, run)
    next_run = run.with_name("next")
    next_run.mkdir()
    _copy_exact_legacy_recovery_source(run, next_run, card)
    ctx = delivery.load_json(
        delivery.build_recovery_context(
            run_dir=next_run, previous_run=run, objective="fixture observation only"
        )
    )
    assert (
        ctx["retained_focused_evidence"][0]["proof_status"] == "historical/unconfirmed"
    )
    manifest = {
        "paths": delivery.changed_paths(),
        "fingerprint": delivery.payload_fingerprint(),
        "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "path_fingerprints": delivery.path_fingerprints(delivery.changed_paths()),
    }
    (run / "reviews").mkdir()
    (next_run / "reviews").mkdir()
    # Actual review context generation, not a model/review session or a GO verdict.
    review = delivery.load_json(
        delivery.build_review_context(
            card=card, run_dir=run, cycle=1, manifest=manifest
        )
    )
    assert review["focused_evidence"][0]["proof_status"] == summary["proof_status"]
    review = delivery.load_json(
        delivery.build_review_context(
            card=card, run_dir=next_run, cycle=1, manifest=manifest
        )
    )
    assert all(
        row["proof_status"] == "historical/unconfirmed"
        for row in review["carried_focused_evidence"]
    )
    assert len(review["carried_focused_evidence"]) == 1
    assert all(p.read_bytes() == data for p, data in original.items())
    if not drift:
        path.with_suffix(".log").write_bytes(b"corrupted")
        damaged = path.with_suffix(".log").read_bytes()
        assert delivery.run_evidence("new-attempt", command) == 0
        assert counter.read_text() == "xx"
        assert path.read_bytes() == original[path]
        assert path.with_suffix(".log").read_bytes() == damaged


@pytest.mark.parametrize(
    "fault",
    [
        "missing-owner",
        "unsafe-owner",
        "spawn",
        "signal",
        "log",
        "completion",
        "completion-interrupt",
        "nonzero-log",
    ],
)
def test_focused_check_producer_failures(tmp_path, monkeypatch, capsys, fault):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    command = [
        sys.executable,
        "-c",
        "print('output'); raise SystemExit(7)"
        if fault == "nonzero-log"
        else "print('output')",
    ]
    if fault in {"missing-owner", "unsafe-owner"}:
        owner = run / "run.json"
        if fault == "missing-owner":
            owner.unlink()
        else:
            outside = root.parent / "outside-owner.json"
            outside.write_bytes(owner.read_bytes())
            owner.unlink()
            owner.symlink_to(outside)
        with pytest.raises(
            delivery.DeliveryError,
            match="cannot start focused proof|unsafe current execution owner",
        ):
            delivery.run_evidence("failure", command)
        assert not (run / "focused-evidence").exists()
        return
    if fault == "spawn":
        command = [str(root / "nonexistent-executable")]
    elif fault == "signal":
        command = [
            sys.executable,
            "-c",
            "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
        ]
    elif fault in {"log", "nonzero-log"}:
        original = Path.open

        def fail_log(self, mode="r", *args, **kwargs):
            if self.suffix == ".log" and mode == "xb":
                raise OSError("injected log failure")
            return original(self, mode, *args, **kwargs)

        monkeypatch.setattr(Path, "open", fail_log)
    elif fault in {"completion", "completion-interrupt"}:

        def fail_terminal(path, value):
            if fault == "completion-interrupt":
                raise KeyboardInterrupt()
            raise OSError("injected completion failure")

        monkeypatch.setattr(delivery, "write_json", fail_terminal)
    assert delivery.run_evidence("failure", command) != 0
    path = next((run / "focused-evidence").glob("*.json"))
    item = delivery.load_json(path)
    if fault in {"completion", "completion-interrupt"}:
        assert item["state"] == "running"
        assert "observed exit=0" in capsys.readouterr().err
    else:
        expected = {"spawn": None, "signal": -15, "nonzero-log": 7}.get(fault, 0)
        assert item["exit_code"] == expected and item["verdict"] == "unconfirmed"
    assert delivery.focused_evidence_summaries(run)[0]["proof_status"] == "unconfirmed"


def test_focused_check_producer_validation_retention_failure(
    tmp_path, monkeypatch, capsys
):
    """The extracted locked helper retains its own validation-error boundary."""
    from jsonschema import ValidationError

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    del root, card
    monkeypatch.setattr(
        delivery,
        "read_check_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValidationError("injected")),
    )
    assert delivery.run_evidence("validation-retention", ["true"]) == 1
    item = delivery.load_json(next((run / "focused-evidence").glob("*.json")))
    assert item["state"] == "terminal" and item["verdict"] == "unconfirmed"
    assert "focused retention failed; observed exit=0" in capsys.readouterr().err


@pytest.mark.parametrize(
    "target", ["record", "log", "ancestor", "unknown", "nested-duplicate"]
)
def test_focused_check_consumers_and_safe_reads(tmp_path, monkeypatch, target):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    assert delivery.run_evidence("safe", ["true"]) == 0
    path = next((run / "focused-evidence").glob("*.json"))
    outside = root.parent / "outside"
    outside.write_bytes(b"never read")
    if target in {"record", "log"}:
        victim = path if target == "record" else path.with_suffix(".log")
        victim.unlink()
        victim.symlink_to(outside)
    elif target == "ancestor":
        moved = path.parent.rename(root.parent / "outside-directory")
        path.parent.symlink_to(moved, target_is_directory=True)
    elif target == "unknown":
        delivery.write_json(path, {"schema": "future", "command": {"unsafe": "type"}})
    else:
        path.write_text(
            path.read_text().replace(
                '"head_commit":', '"head_commit": "duplicate", "head_commit":'
            )
        )
    original = os.fdopen

    def reject_outside(fd, *args, **kwargs):
        assert os.fstat(fd).st_ino != outside.stat().st_ino
        return original(fd, *args, **kwargs)

    monkeypatch.setattr(os, "fdopen", reject_outside)
    assert delivery.focused_evidence_summaries(run)[0]["proof_status"] == "unconfirmed"
    assert delivery.deterministic_commands(run)[0]["proof_status"] == "unconfirmed"
    delivery.build_metrics(run)


def test_focused_check_legacy_and_lane_boundaries(tmp_path, monkeypatch):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    legacy = run / "focused-evidence/old.json"
    delivery.write_json(
        legacy,
        {
            "schema": "changerail.focused-evidence.v1",
            "command": "true",
            "exit_code": 0,
            "fingerprint": delivery.payload_fingerprint(),
        },
    )
    original = legacy.read_bytes()
    assert (
        delivery.focused_evidence_summaries(run)[0]["proof_status"]
        == "historical/unconfirmed"
    )
    assert delivery.run_evidence("current", ["true"]) == 0
    assert legacy.read_bytes() == original
    receipt = next(p for p in (run / "focused-evidence").glob("*.json") if p != legacy)
    receipt.with_suffix(".log").unlink()
    observed = next(
        row
        for row in delivery.deterministic_commands(run)
        if row["proof_status"] == "unconfirmed"
    )
    assert observed["command"] == "true" and observed["exit_code"] == 0
    delivery.build_metrics(run)
    # The general shell helper still permits intentional changed-payload success.
    before = delivery.payload_fingerprint()
    result = delivery.run_shell_verification(
        "printf changed > tracked.txt", run / "repair.log"
    )
    assert result["exit_code"] == 0 and delivery.payload_fingerprint() != before


def test_focused_check_real_interruption(tmp_path, monkeypatch):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    code = (
        _delivery_child_bootstrap(root, run)
        + "import signal, threading; "
        "timer=threading.Timer(0.15, lambda: os.kill(os.getpid(), signal.SIGINT)); timer.start(); "
        'result=d.run_evidence("interrupt", [sys.executable,"-c","import time; time.sleep(0.2)"]); '
        "timer.join(); sys.exit(result)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, timeout=10
    )
    assert result.returncode != 0
    item = delivery.load_json(next((run / "focused-evidence").glob("*.json")))
    assert item["outcome"] == "interrupted" and item["exit_code"] is None
    assert item["verdict"] == "unconfirmed"


@pytest.mark.parametrize("kind", ["recovery", "review", "owner"])
def test_focused_check_unsafe_indexes(tmp_path, monkeypatch, kind):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    assert delivery.run_evidence("indexed", ["true"]) == 0
    outside = root.parent / "outside-index.json"
    outside.write_text('{"retained_focused_evidence": []}')
    index = run / ("run.json" if kind == "owner" else "recovery-context.json")
    if index.exists():
        index.unlink()
    index.symlink_to(outside)
    original = Path.read_text

    def no_outside(self, *args, **kwargs):
        assert self.resolve() != outside.resolve()
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", no_outside)
    if kind == "owner":
        assert (
            delivery.focused_evidence_summaries(run)[0]["proof_status"] == "unconfirmed"
        )
    elif kind == "review":
        with pytest.raises(OSError):
            delivery.build_review_context(
                card=card,
                run_dir=run,
                cycle=1,
                manifest={"paths": [], "fingerprint": delivery.payload_fingerprint()},
            )
    else:
        current = run.with_name("next")
        current.mkdir()
        delivery.write_json(current / "run.json", {"change_plan": []})
        with pytest.raises(OSError):
            delivery.build_recovery_context(
                run_dir=current, previous_run=run, objective="fixture"
            )


def _focused_check_watch_reads(monkeypatch, forbidden):
    """Observe real stream reads, separately from open/fstat; never fake bytes."""
    opened, reads = [], []

    class Watched:
        def __init__(self, stream):
            self.stream = stream
            info = os.fstat(stream.fileno())
            self.identity = (info.st_dev, info.st_ino)
            opened.append(self.identity)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        def __getattr__(self, name):
            return getattr(self.stream, name)

        def read(self, *args):
            reads.append(self.identity)
            assert self.identity not in forbidden, "forbidden content read"
            return self.stream.read(*args)

    path_open, fdopen = Path.open, os.fdopen

    def watch_path(path, mode="r", *args, **kwargs):
        if "r" in mode and path.exists():
            assert not delivery.stat.S_ISFIFO(path.stat().st_mode), (
                "unsafe blocking FIFO open"
            )
        stream = path_open(path, mode, *args, **kwargs)
        return Watched(stream) if "r" in mode else stream

    monkeypatch.setattr(Path, "open", watch_path)
    monkeypatch.setattr(
        os, "fdopen", lambda *args, **kwargs: Watched(fdopen(*args, **kwargs))
    )
    return opened, reads


@pytest.mark.parametrize(
    "consumer", ["metrics", "recovery-current", "recovery-previous", "review"]
)
@pytest.mark.parametrize(
    "damage",
    ["control", "leaf", "ancestor", "fifo", "malformed", "incomplete", "missing"],
)
def test_focused_check_owner_consumers(tmp_path, monkeypatch, consumer, damage):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    assert delivery.run_evidence("owner-control", ["true"]) == 0
    next_run = run.with_name("next")
    next_run.mkdir()
    _copy_exact_legacy_recovery_source(run, next_run, card)
    (run / "reviews").mkdir()
    owner_run = next_run if consumer == "recovery-current" else run
    victim = owner_run / "run.json"
    original = victim.read_bytes()
    receipt = next((run / "focused-evidence").glob("*.json"))
    receipt_bytes = receipt.read_bytes()
    forbidden = set()
    if damage in {"leaf", "ancestor"}:
        if damage == "leaf":
            outside = root.parent / "outside-owner.json"
            outside.write_bytes(original)
            victim.unlink()
            victim.symlink_to(outside)
        else:
            directory = owner_run.rename(root.parent / "outside-run")
            owner_run.symlink_to(directory, target_is_directory=True)
            outside = directory / "run.json"
        info = outside.stat()
        forbidden.add((info.st_dev, info.st_ino))
    elif damage == "fifo":
        victim.unlink()
        os.mkfifo(victim)
        info = victim.stat()
        forbidden.add((info.st_dev, info.st_ino))
    elif damage == "malformed":
        victim.write_text("{broken")
    elif damage == "incomplete":
        victim.write_text("{}")
    elif damage == "missing":
        victim.unlink()
    _, reads = _focused_check_watch_reads(monkeypatch, forbidden)

    def consume():
        if consumer == "metrics":
            return delivery.build_metrics(run)
        if consumer == "review":
            return delivery.load_json(
                delivery.build_review_context(
                    card=card,
                    run_dir=run,
                    cycle=1,
                    manifest={
                        "paths": [],
                        "fingerprint": delivery.payload_fingerprint(),
                    },
                )
            )
        return delivery.load_json(
            delivery.build_recovery_context(
                run_dir=next_run, previous_run=run, objective="owner fixture"
            )
        )

    if damage in {"leaf", "ancestor", "fifo", "malformed"} or (
        consumer in {"metrics", "recovery-previous"}
        and damage in {"incomplete", "missing"}
    ):
        with pytest.raises((ValueError, OSError, delivery.DeliveryError)):
            consume()
    else:
        if damage in {"incomplete", "missing"} and consumer in {
            "recovery-current",
            "review",
        }:
            # Explicit old-unit boundary only: this parametrization feeds
            # malformed historical owner metadata to the receipt/context
            # reader.  C4 selection is separately covered by real exact-v1
            # and v2 integration tests, so isolate just that unrelated gate
            # for these two historical-data cases; no owner/evidence reader
            # under test is stubbed.
            actual_contract = delivery._run_observed_contract
            with monkeypatch.context() as isolated:
                isolated.setattr(
                    delivery,
                    "_run_observed_contract",
                    lambda selected_run: (
                        None
                        if selected_run == owner_run
                        else actual_contract(selected_run)
                    ),
                )
                result = consume()
        else:
            result = consume()
        if consumer == "metrics":
            assert (
                result["run_id"] == run.name
                and result["deterministic_command_count"] == 1
            )
            assert result["usage_status"] == "unknown"
        elif consumer == "review":
            assert result["focused_evidence"][0]["proof_status"] == (
                "current" if damage == "control" else "unconfirmed"
            )
        else:
            assert (
                result["inherited_review_budget"]
                == delivery._empty_review_budget_usage()
            )
            assert (
                result["retained_focused_evidence"][0]["proof_status"]
                == "historical/unconfirmed"
            )
    assert not forbidden.intersection(reads)
    if damage in {"incomplete", "missing"}:
        assert all(
            row["proof_status"] != "current"
            for row in delivery.focused_evidence_summaries(owner_run)
        )
    if damage != "ancestor":
        assert receipt.read_bytes() == receipt_bytes


def test_focused_check_deep_json_consumers(tmp_path, monkeypatch):
    import sys

    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    assert delivery.run_evidence("valid-control", ["true"]) == 0
    valid = next((run / "focused-evidence").glob("*.json"))
    valid_bytes = valid.read_bytes()
    marker = run / "loaded-command-must-not-run"
    bad = valid.with_name("deep.json")
    bad.write_text(
        '{"command": '
        + json.dumps("touch " + str(marker))
        + ', "nested": '
        + "[" * 2000
        + "0"
        + "]" * 2000
        + "}"
    )
    assert bad.stat().st_size < 262144
    for rows in (
        delivery.focused_evidence_summaries(run),
        delivery.deterministic_commands(run),
    ):
        assert len(rows) == 2
        assert [row["command"] for row in rows if row["proof_status"] == "current"] == [
            "true"
        ]
        # JSON nesting limits differ across supported Python versions. Whether
        # decoding refuses this input or recognizes untyped historical data,
        # the hostile record must never become valid current evidence.
        assert all(
            row["proof_status"] in {"current", "unconfirmed", "historical/unconfirmed"}
            for row in rows
        )
    metrics = delivery.build_metrics(run)
    assert metrics["deterministic_command_count"] == 2
    assert metrics["repeated_commands"] == []
    with pytest.raises(delivery.DeliveryError, match=valid.name):
        delivery.run_evidence("valid-repeat", ["true"])
    # Damaged proof is not reused; only this explicitly supplied new argv runs.
    counter = run / "authorized-count"
    command = [
        sys.executable,
        "-c",
        f'from pathlib import Path; Path({str(counter)!r}).write_text("x")',
    ]
    bad_bytes = bad.read_bytes()
    assert delivery.run_evidence("new-command", command) == 0
    assert counter.read_text() == "x" and not marker.exists()
    assert bad.read_bytes() == bad_bytes and valid.read_bytes() == valid_bytes


@pytest.mark.parametrize(
    "target", ["record", "log", "owner", "recovery-index", "review-index"]
)
def test_focused_check_nonregular_read_order(tmp_path, monkeypatch, target):
    root, card, run = _focused_check_fixture(tmp_path, monkeypatch)
    assert delivery.run_evidence("silent-control", ["true"]) == 0
    path = next((run / "focused-evidence").glob("*.json"))
    assert delivery.read_check_result(path, run, "focused")[1:] == (b"", True)
    next_run = run.with_name("next")
    next_run.mkdir()
    _copy_exact_legacy_recovery_source(run, next_run, card)
    (run / "reviews").mkdir()
    index = run / "recovery-context.json"
    delivery.write_json(
        index, {"retained_focused_evidence": delivery.focused_evidence_summaries(run)}
    )
    victim = {
        "record": path,
        "log": path.with_suffix(".log"),
        "owner": run / "run.json",
        "recovery-index": index,
        "review-index": index,
    }[target]

    def consume():
        if target in {"record", "log"}:
            return delivery.focused_evidence_summaries(run)
        if target == "owner":
            return delivery.build_metrics(run)
        if target == "recovery-index":
            return delivery.load_json(
                delivery.build_recovery_context(
                    run_dir=next_run, previous_run=run, objective="FIFO fixture"
                )
            )
        return delivery.load_json(
            delivery.build_review_context(
                card=card,
                run_dir=run,
                cycle=1,
                manifest={"paths": [], "fingerprint": delivery.payload_fingerprint()},
            )
        )

    control = consume()
    if target in {"record", "log"}:
        assert control[0]["proof_status"] == "current"
    elif target == "owner":
        assert control["run_id"] == run.name
    else:
        key = (
            "carried_focused_evidence"
            if target == "review-index"
            else "retained_focused_evidence"
        )
        assert control[key][0]["proof_status"] == "historical/unconfirmed"
    victim.unlink()
    os.mkfifo(victim)  # Real FIFO, O_NONBLOCK reader, no writer or background process.
    info = victim.stat()
    identity = (info.st_dev, info.st_ino)
    opened, reads = _focused_check_watch_reads(monkeypatch, {identity})
    if target in {"record", "log"}:
        assert consume()[0]["proof_status"] == "unconfirmed"
    else:
        with pytest.raises(ValueError, match="nonregular"):
            consume()
    assert identity in opened and identity not in reads
    # Narrow in-memory mutant: removing precisely S_ISREG must break read-order.
    # No product source edit, fake bytes, schema substitution or blocking read.
    with monkeypatch.context() as mutant:
        mutant.setattr(delivery.stat, "S_ISREG", lambda mode: True)
        with pytest.raises(AssertionError, match="forbidden content read"):
            consume()


def test_evidence_rejects_unchanged_successful_repeat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _focused_check_fixture(tmp_path, monkeypatch)

    assert delivery.run_evidence("first", ["true"]) == 0
    with pytest.raises(delivery.DeliveryError, match="must not be repeated"):
        delivery.run_evidence("duplicate", ["true"])

    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    assert delivery.run_evidence("after-change", ["true"]) == 0


def test_review_cycles_retain_path_hashes_and_expose_cycle_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _review_fixture(tmp_path, monkeypatch)
    cycles: list[int] = []
    contexts: list[dict[str, object]] = []

    def fake_launch_codex(**kwargs) -> int:
        cycle = int(kwargs["session_env"]["CHRL_REVIEW_CYCLE"])
        cycles.append(cycle)
        contexts.append(
            delivery.load_json(Path(kwargs["session_env"]["CHRL_REVIEW_CONTEXT"]))
        )
        (run_dir / "sessions" / f"review-{cycle:02d}").mkdir(parents=True)
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["focused evidence"]
        delivery.write_json(delivery.verdict_path("test-card"), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", fake_launch_codex)

    with pytest.raises(delivery.DeliveryError, match="review requires successful"):
        delivery.run_review(str(card))
    _write_matching_preverification(card, run_dir)
    assert delivery.run_review(str(card)) == 0
    assert delivery.run_review(str(card)) == 0
    assert cycles == [1]
    first = delivery.load_json(run_dir / "reviews" / "cycle-01-manifest.json")
    _isolate_legacy_review_cycle_unit(monkeypatch, run_dir)
    (root / "tracked.txt").write_text("second\n", encoding="utf-8")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, run_dir)
    assert delivery.run_review(str(card)) == 0
    second = delivery.load_json(run_dir / "reviews" / "cycle-02-manifest.json")

    assert cycles == [1, 2]
    assert contexts[0]["previous_cycle"] is None
    assert contexts[1]["previous_cycle"] == {
        "cycle": 1,
        "result": "go",
        "verdict": ".runtime/changerail/runs/run-1/reviews/cycle-01.json",
        "manifest": (".runtime/changerail/runs/run-1/reviews/cycle-01-manifest.json"),
        "changed_paths": ["tracked.txt"],
    }
    first_payloads = contexts[0]["payload_diffs"]
    assert isinstance(first_payloads, list)
    assert [item["path"] for item in first_payloads] == first["paths"]
    assert all((root / item["diff"]).is_file() for item in first_payloads)
    card_payload = next(
        item
        for item in first_payloads
        if item["path"] == f"{FIXTURE_BOARD}/3.inprogress/test-card.md"
    )
    assert "Test measured delivery" in (root / card_payload["diff"]).read_text(
        encoding="utf-8"
    )
    assert not (run_dir / "reviews" / "cycle-01-payload.diff").exists()
    assert (run_dir / "reviews" / "cycle-01.json").is_file()
    assert (run_dir / "reviews" / "cycle-02.json").is_file()
    assert (
        first["path_fingerprints"]["tracked.txt"]
        != second["path_fingerprints"]["tracked.txt"]
    )
    assert (
        first["path_fingerprints"][f"{FIXTURE_BOARD}/3.inprogress/test-card.md"]
        == second["path_fingerprints"][f"{FIXTURE_BOARD}/3.inprogress/test-card.md"]
    )


def test_recovery_review_uses_previous_run_hashes_for_delta_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _review_fixture(tmp_path, monkeypatch)
    current_manifest = delivery.load_json(delivery.manifest_path("test-card"))
    previous_run = root / ".runtime" / "changerail" / "runs" / "previous-run"
    previous_reviews = previous_run / "reviews"
    previous_reviews.mkdir(parents=True)
    previous_manifest_path = previous_reviews / "cycle-02-manifest.json"
    previous_verdict_path = previous_reviews / "cycle-02.json"
    delivery.write_json(previous_manifest_path, current_manifest)
    delivery.write_json(
        previous_verdict_path,
        {"workspace": current_manifest["fingerprint"], "result": "no-go"},
    )
    delivery.write_json(
        run_dir / "recovery-context.json",
        {
            "recovery_of": "previous-run",
            "previous_completed_review": {
                "cycle": 2,
                "result": "no-go",
                "verdict": delivery.repo_relative(previous_verdict_path),
                "manifest": delivery.repo_relative(previous_manifest_path),
            },
        },
    )
    _isolate_legacy_review_cycle_unit(monkeypatch, run_dir)
    (root / "tracked.txt").write_text("repaired\n", encoding="utf-8")
    repaired_manifest = delivery.capture_manifest(str(card))
    (run_dir / "reviews").mkdir()

    context_path = delivery.build_review_context(
        card=card,
        run_dir=run_dir,
        cycle=1,
        manifest=repaired_manifest,
        review_reason="terminal_semantic_recovery",
    )
    context = delivery.load_json(context_path)

    assert context["selected_paths"] == ["tracked.txt"]
    assert context["previous_cycle"] == {
        "cycle": 2,
        "run_id": "previous-run",
        "result": "no-go",
        "verdict": delivery.repo_relative(previous_verdict_path),
        "manifest": delivery.repo_relative(previous_manifest_path),
        "changed_paths": ["tracked.txt"],
        "cross_run": True,
    }
    assert context["payload_diffs"][0]["path"] == "tracked.txt"


def test_recovery_review_recomputes_carried_evidence_after_repair_edits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _review_fixture(tmp_path, monkeypatch)
    before_repair = delivery.payload_fingerprint()
    delivery.write_json(
        run_dir / "recovery-context.json",
        {
            "retained_focused_evidence": [
                {
                    "label": "stale-after-edit",
                    "command": "uv run pytest -q tests/test_old.py",
                    "exit_code": 0,
                    "fingerprint": before_repair,
                    "matches_current_payload": True,
                }
            ]
        },
    )
    _isolate_legacy_review_cycle_unit(monkeypatch, run_dir)
    (root / "tracked.txt").write_text("repaired\n", encoding="utf-8")
    repaired_manifest = delivery.capture_manifest(str(card))
    (run_dir / "reviews").mkdir()

    context = delivery.load_json(
        delivery.build_review_context(
            card=card,
            run_dir=run_dir,
            cycle=1,
            manifest=repaired_manifest,
        )
    )

    assert context["carried_focused_evidence"] == []


def test_failed_floor_cannot_add_a_third_independent_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, card, run_dir = _review_fixture(tmp_path, monkeypatch)
    cycles: list[int] = []
    reasons: list[str] = []

    def fake_launch_codex(**kwargs) -> int:
        cycle = int(kwargs["session_env"]["CHRL_REVIEW_CYCLE"])
        cycles.append(cycle)
        reasons.append(str(kwargs["session_env"]["CHRL_REVIEW_REASON"]))
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["focused evidence"]
        delivery.write_json(delivery.verdict_path("test-card"), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", fake_launch_codex)

    _write_matching_preverification(card, run_dir)
    assert delivery.run_review(str(card)) == 0
    _isolate_legacy_review_cycle_unit(monkeypatch, run_dir)
    (root / "tracked.txt").write_text("second\n", encoding="utf-8")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, run_dir)
    assert delivery.run_review(str(card)) == 0
    second_verdict = delivery.load_json(run_dir / "reviews" / "cycle-02.json")

    (root / "tracked.txt").write_text("third\n", encoding="utf-8")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, run_dir)
    with pytest.raises(delivery.DeliveryError, match="two-review budget exhausted"):
        delivery.run_review(str(card))

    delivery.write_json(
        run_dir / "verification.json",
        {
            "ok": False,
            "card": {
                "id": "test-card",
                "path": f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
            },
            "fingerprint": second_verdict["workspace"],
        },
    )
    before = sorted((run_dir / "reviews").glob("cycle-??.json"))
    with pytest.raises(delivery.DeliveryError, match="two-review budget exhausted"):
        delivery.run_review(str(card))
    assert cycles == [1, 2]
    assert sorted((run_dir / "reviews").glob("cycle-??.json")) == before


def test_review_retries_incomplete_attempt_as_the_same_semantic_cycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(
        _card_text().replace(
            "implementation in progress", "implemented observable result"
        ),
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("payload\n", encoding="utf-8")
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    (run_dir / "sessions" / "review-01").mkdir(parents=True)
    (run_dir / "reviews").mkdir()
    monkeypatch.setenv("CHRL_RUN_DIR", str(run_dir))
    monkeypatch.delenv("CHRL_SESSION_ROLE", raising=False)
    source_schema = (
        Path(__file__).parents[3]
        / "tools"
        / "changerail"
        / "schemas"
        / "review-verdict.schema.json"
    )
    schema_path = root / "tools" / "changerail" / "schemas" / source_schema.name
    schema_path.parent.mkdir(parents=True)
    schema_path.write_text(source_schema.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(delivery, "VERDICT_SCHEMA_PATH", schema_path)
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "max_wall_minutes": 1,
            "max_review_cycles": 2,
            "models": {"review": {"model": "gpt-test", "reasoning_effort": "high"}},
            "budgets": {"review_commands": 12},
            "verification": {
                "pre_review_commands": ["true"],
                "final_commands": ["check"],
            },
        },
    )
    _anchor_exact_legacy_recovery_source(run_dir, card)
    manifest = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": "run-1",
        "baseline_head": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "created_at": "2026-09-04T00:00:00Z",
        "card": {
            "id": "test-card",
            "path": f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
        },
        "paths": [],
    }
    delivery.write_json(delivery.manifest_path("test-card"), manifest)
    manifest = delivery.capture_manifest(str(card))
    delivery.write_json(run_dir / "reviews" / "cycle-01-manifest.json", manifest)
    _write_matching_preverification(card, run_dir)
    observed_cycles: list[int] = []

    def fake_launch_codex(**kwargs) -> int:
        observed_cycles.append(int(kwargs["session_env"]["CHRL_REVIEW_CYCLE"]))
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["focused evidence"]
        delivery.write_json(delivery.verdict_path("test-card"), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", fake_launch_codex)

    assert delivery.run_review(str(card)) == 0
    assert observed_cycles == [1]
    assert (run_dir / "reviews" / "cycle-01.json").is_file()


@pytest.mark.parametrize(
    "stage",
    (delivery.run_review, delivery.verify, delivery.publish),
)
def test_implementation_role_cannot_launch_runner_owned_stage(
    monkeypatch: pytest.MonkeyPatch, stage: Callable[..., int]
) -> None:
    monkeypatch.setenv("CHRL_SESSION_ROLE", "implementation")

    with pytest.raises(delivery.DeliveryError, match="must hand off"):
        stage("test-card.md")


def test_runner_owns_one_review_per_cycle_and_resumes_thread_for_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    monkeypatch.setattr(delivery, "require_frozen_execution", lambda run: {})
    run_dir = tmp_path / "run"
    reviews = run_dir / "reviews"
    reviews.mkdir(parents=True)
    card = tmp_path / "test-card.md"
    card.write_text("# Test\n\n## Lifecycle\nopenspec-v1\n", encoding="utf-8")
    implementation_calls: list[dict[str, object]] = []
    review_calls = 0
    verification_calls = 0
    publish_calls = 0

    def fake_implementation(**kwargs) -> str:
        implementation_calls.append(kwargs)
        return "thread-1"

    def fake_review(card_value: str) -> int:
        nonlocal review_calls
        del card_value
        review_calls += 1
        if review_calls == 1:
            delivery.write_json(reviews / "cycle-01.json", {"result": "no-go"})
            return 3
        return 0

    def fake_verify(card_value: str) -> int:
        nonlocal verification_calls
        del card_value
        verification_calls += 1
        return 0

    def fake_publish(card_value: str) -> int:
        nonlocal publish_calls
        del card_value
        publish_calls += 1
        return 0

    repair_context = run_dir / "repair-context.json"
    monkeypatch.setattr(delivery, "launch_implementation_stage", fake_implementation)
    monkeypatch.setattr(delivery, "run_review", fake_review)
    monkeypatch.setattr(delivery, "verify", fake_verify)
    monkeypatch.setattr(delivery, "publish", fake_publish)
    monkeypatch.setattr(
        delivery, "build_repair_context", lambda **kwargs: repair_context
    )
    monkeypatch.setattr(delivery, "emit_event", lambda *args: None)

    assert (
        delivery.orchestrate_delivery(
            card=card,
            run_dir=run_dir,
            current_profile={
                "max_review_cycles": 2,
                "max_post_verification_repair_reviews": 1,
            },
            resume_thread_id=None,
            recovery_context=None,
            require_first_file_change=True,
            inherited_investigative_commands=0,
        )
        == 0
    )
    assert review_calls == 2
    assert verification_calls == 1
    assert publish_calls == 1
    assert len(implementation_calls) == 2
    assert implementation_calls[1]["resume_thread_id"] == "thread-1"
    assert implementation_calls[1]["repair_context"] == repair_context
    assert implementation_calls[1]["require_first_file_change"] is False


def test_runner_stops_after_second_semantic_no_go(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    monkeypatch.setattr(delivery, "require_frozen_execution", lambda run: {})
    run_dir = tmp_path / "run"
    reviews = run_dir / "reviews"
    reviews.mkdir(parents=True)
    card = tmp_path / "test-card.md"
    card.write_text("# Test\n\n## Lifecycle\nopenspec-v1\n", encoding="utf-8")
    implementation_calls: list[dict[str, object]] = []
    review_calls = 0

    def fake_implementation(**kwargs) -> str:
        implementation_calls.append(kwargs)
        return "thread-1"

    def fake_review(card_value: str) -> int:
        nonlocal review_calls
        del card_value
        review_calls += 1
        delivery.write_json(
            reviews / f"cycle-{review_calls:02d}.json", {"result": "no-go"}
        )
        return 3

    monkeypatch.setattr(delivery, "launch_implementation_stage", fake_implementation)
    monkeypatch.setattr(delivery, "run_review", fake_review)
    monkeypatch.setattr(
        delivery,
        "build_repair_context",
        lambda **kwargs: run_dir / "repair-context.json",
    )
    monkeypatch.setattr(delivery, "verify", lambda card_value: pytest.fail(card_value))
    monkeypatch.setattr(delivery, "publish", lambda card_value: pytest.fail(card_value))
    monkeypatch.setattr(delivery, "emit_event", lambda *args: None)

    with pytest.raises(delivery.DeliveryError, match="two-review budget exhausted"):
        delivery.orchestrate_delivery(
            card=card,
            run_dir=run_dir,
            current_profile={
                "max_review_cycles": 2,
                "max_post_verification_repair_reviews": 1,
            },
            resume_thread_id=None,
            recovery_context=None,
            require_first_file_change=True,
            inherited_investigative_commands=0,
        )

    assert review_calls == 2
    assert len(implementation_calls) == 2


def test_implementation_stage_requires_handoff_and_passes_resume_thread(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    run_dir = root / ".runtime" / "changerail" / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    card = root / "openspec" / "board" / "3.inprogress" / "test-card.md"
    card.parent.mkdir(parents=True)
    card.write_text("# Test\n\n## Lifecycle\nopenspec-v1\n", encoding="utf-8")
    observed: dict[str, object] = {}

    monkeypatch.setattr(
        delivery,
        "model_route",
        lambda current_profile, role: ("gpt-test", "high"),
    )

    def fake_launch_codex(**kwargs) -> int:
        observed.update(kwargs)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", fake_launch_codex)

    with pytest.raises(delivery.DeliveryError, match="without a handoff"):
        delivery.launch_implementation_stage(
            card=card,
            run_dir=run_dir,
            current_profile={"max_wall_minutes": 1},
            resume_thread_id="thread-1",
            recovery_context=run_dir / "recovery-context.json",
            require_first_file_change=True,
            inherited_investigative_commands=7,
        )

    assert observed["resume_thread_id"] == "thread-1"
    assert observed["require_first_file_change"] is True
    assert observed["inherited_investigative_commands"] == 7
    assert observed["session_env"] == {
        "CHRL_RECOVERY_RUN": "1",
        "CHRL_RECOVERY_CONTEXT": str(run_dir / "recovery-context.json"),
    }


def test_runner_re_reviews_once_after_a_bounded_final_floor_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(delivery.native, "is_native", lambda card: False)
    monkeypatch.setattr(delivery, "require_frozen_execution", lambda run: {})
    run_dir = tmp_path / "run"
    (run_dir / "reviews").mkdir(parents=True)
    card = tmp_path / "test-card.md"
    card.write_text("# Test\n\n## Lifecycle\nopenspec-v1\n", encoding="utf-8")
    implementation_calls: list[dict[str, object]] = []
    review_calls = 0
    verification_results = iter((1, 0))
    verification_calls = 0

    def fake_implementation(**kwargs) -> str:
        implementation_calls.append(kwargs)
        return "thread-1"

    def fake_review(card_value: str) -> int:
        nonlocal review_calls
        del card_value
        review_calls += 1
        return 0

    def fake_verify(card_value: str) -> int:
        nonlocal verification_calls
        del card_value
        verification_calls += 1
        return next(verification_results)

    repair_context = run_dir / "floor-repair-context.json"
    monkeypatch.setattr(delivery, "launch_implementation_stage", fake_implementation)
    monkeypatch.setattr(delivery, "run_review", fake_review)
    monkeypatch.setattr(delivery, "verify", fake_verify)
    monkeypatch.setattr(delivery, "publish", lambda card_value: 0)
    monkeypatch.setattr(
        delivery, "build_repair_context", lambda **kwargs: repair_context
    )
    monkeypatch.setattr(delivery, "emit_event", lambda *args: None)

    assert (
        delivery.orchestrate_delivery(
            card=card,
            run_dir=run_dir,
            current_profile={
                "max_review_cycles": 2,
                "max_post_verification_repair_reviews": 1,
            },
            resume_thread_id=None,
            recovery_context=None,
            require_first_file_change=True,
            inherited_investigative_commands=0,
        )
        == 0
    )
    assert review_calls == 2
    assert verification_calls == 2
    assert len(implementation_calls) == 2
    assert implementation_calls[1]["repair_context"] == repair_context


def test_run_delivery_retains_metrics_and_manifest_after_session_hard_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    todo = root / "openspec" / "board" / "2.todo"
    in_progress = root / "openspec" / "board" / "3.inprogress"
    todo.mkdir(parents=True)
    in_progress.mkdir()
    card = todo / "test-card.md"
    card.write_text(_card_text("2.todo"), encoding="utf-8")
    _git(root, "add", "--", str(card.relative_to(root)))
    _git(root, "commit", "-m", "add card")
    monkeypatch.setattr(delivery, "PROFILE_PATH", root / ".changerail/profile.toml")
    monkeypatch.setattr(delivery, "doctor", lambda *args, **kwargs: {"ok": True})
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {
            "max_wall_minutes": 1,
            "models": {
                "implementation": {
                    "model": "gpt-test",
                    "reasoning_effort": "high",
                }
            },
            "budgets": {
                "first_edit_discovery_commands": 8,
                "review_commands": 12,
            },
        },
    )

    def fake_start_delivery_card(card_value: Path, manifest: dict[str, object]) -> Path:
        del manifest
        destination = in_progress / card_value.name
        card_value.replace(destination)
        return destination

    def fake_launch_codex(**kwargs) -> int:
        del kwargs
        raise delivery.DeliveryError(
            "implementation shell command budget exceeded: 9 > 8"
        )

    monkeypatch.setattr(delivery, "start_delivery_card", fake_start_delivery_card)
    monkeypatch.setattr(delivery, "launch_codex", fake_launch_codex)

    assert delivery.run_delivery(str(card)) == 2
    run_dir = next((root / ".runtime" / "changerail" / "runs").iterdir())
    run = delivery.load_json(run_dir / "run.json")
    retained = delivery.load_json(run_dir / "manifest.json")

    assert run["exit_code"] == 2
    assert isinstance(run["duration_seconds"], float)
    assert run["terminal_reason"].startswith("implementation shell command budget")
    assert "finished_at" in run
    assert (run_dir / "metrics.json").is_file()
    assert retained["card"]["path"] == (f"{FIXTURE_BOARD}/3.inprogress/test-card.md")
    assert retained["paths"] == [
        f"{FIXTURE_BOARD}/2.todo/test-card.md",
        f"{FIXTURE_BOARD}/3.inprogress/test-card.md",
    ]


def test_valid_verdict_becomes_stale_after_payload_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    active = root / "openspec" / "board" / "3.inprogress"
    active.mkdir(parents=True)
    card = active / "test-card.md"
    card.write_text(_card_text(), encoding="utf-8")
    monkeypatch.setattr(
        delivery,
        "VERDICT_SCHEMA_PATH",
        Path(__file__).parents[3]
        / "tools"
        / "changerail"
        / "schemas"
        / "review-verdict.schema.json",
    )
    template = delivery.verdict_template(str(card))["template"]
    template["acceptance"][0]["evidence"] = ["focused test passed"]
    delivery.write_json(delivery.verdict_path("test-card"), template)

    assert delivery.validate_verdict(str(card))["result"] == "go"
    card.write_text(_card_text() + "\nchanged\n", encoding="utf-8")
    with pytest.raises(delivery.DeliveryError, match="stale"):
        delivery.validate_verdict(str(card))


def test_verdict_acceptance_coverage_is_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    _write_verdict(card, verdict)

    assert delivery.validate_verdict(str(card))["acceptance"] == verdict["acceptance"]


def test_verdict_acceptance_coverage_rejects_empty_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    verdict["acceptance"][0]["evidence"] = []
    _write_verdict(card, verdict)

    from jsonschema.exceptions import ValidationError

    with pytest.raises(delivery.DeliveryError) as failure:
        delivery.validate_verdict(str(card))
    cause = failure.value.__cause__
    assert isinstance(cause, ValidationError)
    assert cause.validator == "minItems"
    assert list(cause.absolute_path) == ["acceptance", 0, "evidence"]


def test_verdict_acceptance_coverage_rejects_missing_criterion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    verdict["acceptance"] = verdict["acceptance"][:1]
    _write_verdict(card, verdict)

    with pytest.raises(delivery.DeliveryError, match=r"missing=\['criterion two'\]"):
        delivery.validate_verdict(str(card))


def test_verdict_acceptance_coverage_rejects_duplicate_criterion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    verdict["acceptance"].append(verdict["acceptance"][0].copy())
    _write_verdict(card, verdict)

    with pytest.raises(delivery.DeliveryError, match=r"duplicates=\['criterion one'\]"):
        delivery.validate_verdict(str(card))


def test_verdict_acceptance_coverage_rejects_foreign_criterion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    verdict["acceptance"][1]["criterion"] = "foreign criterion"
    _write_verdict(card, verdict)

    with pytest.raises(
        delivery.DeliveryError, match=r"foreign=\['foreign criterion'\]"
    ):
        delivery.validate_verdict(str(card))


def test_verdict_rejects_findings_without_operational_repair_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    card, verdict = _verdict_fixture(tmp_path, monkeypatch)
    verdict["result"] = "no-go"
    verdict["acceptance"][0]["result"] = "fail"
    verdict["findings"] = [
        {
            "id": "R1",
            "severity": "blocker",
            "summary": "The evidence is incomplete.",
            "paths": ["tests/test_feature.py"],
        }
    ]
    _write_verdict(card, verdict)

    with pytest.raises(delivery.DeliveryError, match="required property"):
        delivery.validate_verdict(str(card))

    verdict["findings"][0].update(
        {
            "preconditions": "An old selected-owner row exists.",
            "expected": "The old row is absent and the desired row is present.",
            "observed": "Only insertion into an empty key is asserted.",
            "repair_scope": "Seed the old row and assert both before and after hashes.",
        }
    )
    _write_verdict(card, verdict)
    assert delivery.validate_verdict(str(card))["result"] == "no-go"


def test_tracked_delivery_entrypoints_are_local_regular_files() -> None:
    root = Path(__file__).parents[3]
    for relative in ("bin/openspec", "bin/chrl", "bin/chrl-run"):
        path = root / relative
        assert path.is_file()
        assert not path.is_symlink()


def test_install_hooks_selects_project_owned_hook_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path, monkeypatch)
    configured = delivery.profile()
    monkeypatch.setattr(
        delivery,
        "profile",
        lambda: {**configured, "project": {"hooks_path": "scripts/git-hooks"}},
    )
    hooks = root / "scripts" / "git-hooks"
    hooks.mkdir(parents=True)
    pre_commit = hooks / "pre-commit"
    pre_commit.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    pre_commit.chmod(0o755)

    assert delivery.install_local_hooks()["status"] == "installed"
    assert _git(root, "config", "--get", "core.hooksPath").stdout.strip() == (
        "scripts/git-hooks"
    )
