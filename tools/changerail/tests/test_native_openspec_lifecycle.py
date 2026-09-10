from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.changerail.contracts import DeliveryError
from scripts.changerail import openspec_context as native
from scripts.changerail import local_delivery as delivery
from scripts.changerail import native_workflow as flow
from scripts.changerail.openspec_adapter import ApplyContext, Task


def _card(tmp_path: Path, column: str, extra: str = "") -> Path:
    root = tmp_path / "openspec/board" / column
    root.mkdir(parents=True)
    card = root / "card.md"
    card.write_text(f"# Card\n\n{extra}", encoding="utf-8")
    return card


def test_unmarked_executable_cards_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(DeliveryError, match="explicit ## Lifecycle"):
        native.lifecycle_mode(_card(tmp_path, "1.backlog"))


def test_unmarked_closed_cards_remain_history(tmp_path: Path) -> None:
    assert native.lifecycle_mode(_card(tmp_path, "4.done")) == "board-only-history"


def test_explicit_legacy_and_native_modes_are_distinct(tmp_path: Path) -> None:
    legacy = _card(tmp_path / "legacy", "2.todo", "## Lifecycle\nboard-only\n")
    current = _card(
        tmp_path / "current",
        "2.todo",
        "## Lifecycle\nopenspec-v1\n\n## OpenSpec Changes\n1. `add-route`\n",
    )
    assert native.lifecycle_mode(legacy) == "board-only"
    assert native.is_native(current)
    assert native.change_id(current) == "add-route"


def test_native_card_requires_exactly_one_change(tmp_path: Path) -> None:
    card = _card(
        tmp_path,
        "2.todo",
        "## Lifecycle\nopenspec-v1\n\n## OpenSpec Changes\n1. `one`\n2. `two`\n",
    )
    with pytest.raises(DeliveryError, match="exactly one ordered entry"):
        native.change_id(card)


def test_task_groups_are_contiguous_lowercase_slugs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    change = tmp_path / "change"
    change.mkdir()
    (change / "tasks.md").write_text(
        "## 1. implement-route\n- [ ] 1.1 work\n\n"
        "## 2. verify-route\n- [ ] 2.1 verify\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(native, "change_root", lambda _delivery, _card: change)
    assert native.task_groups(SimpleNamespace(), tmp_path / "unused.md") == [
        (1, "implement-route"),
        (2, "verify-route"),
    ]


def test_native_delivery_archives_between_provisional_and_final_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    card = tmp_path / "card.md"
    card.write_text("# Card\n", encoding="utf-8")
    events: list[str] = []
    reviews = iter((0, 0))

    def launch(**_kwargs: object) -> str:
        events.append("implementation")
        return "thread"

    def archive(_delivery: object, _card: Path, _run: Path) -> dict[str, object]:
        events.append("archive")
        (run_dir / "native-archive.json").write_text("{}", encoding="utf-8")
        return {"change_id": "change"}

    monkeypatch.setattr(delivery, "launch_implementation_stage", launch)
    # This unit test owns orchestration order; frozen ownership has contract tests.
    monkeypatch.setattr(delivery, "require_frozen_execution", lambda _run: {})
    monkeypatch.setattr(
        delivery, "run_review", lambda _card: events.append("review") or next(reviews)
    )
    monkeypatch.setattr(
        delivery, "verify_as_outer_dispatch", lambda _card: events.append("verify") or 0
    )
    monkeypatch.setattr(
        delivery, "publish", lambda _card: events.append("publish") or 0
    )
    monkeypatch.setattr(delivery, "emit_event", lambda *_args: None)
    monkeypatch.setattr(delivery, "changed_paths", lambda: [])
    monkeypatch.setattr(
        delivery, "write_json", lambda path, _value: path.write_text("{}")
    )
    monkeypatch.setattr(delivery.native, "is_native", lambda _card: True)
    monkeypatch.setattr(delivery.native, "archive", archive)
    from scripts.changerail import native_workflow

    monkeypatch.setattr(
        native_workflow,
        "launch_groups",
        lambda *_args, **_kwargs: events.append("groups"),
    )

    assert (
        delivery.orchestrate_delivery(
            card=card,
            run_dir=run_dir,
            current_profile={
                "max_review_cycles": 2,
            },
            resume_thread_id=None,
            recovery_context=None,
            require_first_file_change=True,
            inherited_investigative_commands=0,
        )
        == 0
    )
    assert events == [
        "groups",
        "implementation",
        "review",
        "archive",
        "implementation",
        "review",
        "verify",
        "publish",
    ]


def test_native_recovery_carries_exact_archive_receipt(tmp_path: Path) -> None:
    runs = tmp_path / ".runtime/changerail/runs"
    previous = runs / "previous"
    current = runs / "current"
    previous.mkdir(parents=True)
    current.mkdir()
    raw = b'{"schema":"changerail.openspec-archive.v1","change_id":"route"}\n'
    (previous / "native-archive.json").write_bytes(raw)

    assert native.carry_archive_receipt(
        SimpleNamespace(REPO_ROOT=tmp_path), previous, current
    )
    assert (current / "native-archive.json").read_bytes() == raw
    with pytest.raises(FileExistsError):
        native.carry_archive_receipt(
            SimpleNamespace(REPO_ROOT=tmp_path), previous, current
        )


@pytest.mark.parametrize("cross_group", [False, True])
def test_native_sessions_are_assigned_one_unfinished_group(
    tmp_path, monkeypatch, cross_group
):
    progress = {1: False, 2: False}
    events = []
    assignments = []
    client = SimpleNamespace(
        apply_context=lambda _id: ApplyContext(
            "ready",
            tuple(
                Task(str(n), f"{n}.1 Execute group {n}", progress[n]) for n in (1, 2)
            ),
            (),
            "stock fixture",
        )
    )
    monkeypatch.setattr(native, "adapter", lambda _d: client)
    monkeypatch.setattr(native, "require_plan", lambda *a: None)
    monkeypatch.setattr(native, "change_id", lambda _c: "fixture")
    monkeypatch.setattr(native, "delivery_context", lambda *a: {"fixture": True})

    def model(**kwargs):
        env = kwargs["session_env"]
        number = int(env["CHRL_CHANGE_NUMBER"])
        assignments.append(number)
        assert kwargs["resume_thread_id"] is None
        assert env["CHRL_DELIVERY_STAGE"] == "change"
        assert env["CHRL_CHANGE_NEXT_EVENT"] == "starting"
        progress[number] = True
        if cross_group:
            progress[2] = True
        for stage in ("starting", "complete"):
            events.append(
                {
                    "phase": f"change-{number}",
                    "stage": stage,
                    "at": "2026-09-09T00:00:00Z",
                }
            )
        return 0

    adapter = SimpleNamespace(
        declared_change_plan=lambda _r: [(1, "first"), (2, "second")],
        combined_change_events=lambda _r: events,
        change_checkpoint_statuses=delivery.change_checkpoint_statuses,
        write_json=delivery.write_json,
        repo_relative=lambda p: p.name,
        model_route=lambda *_a: ("fixture", "high"),
        launch_codex=model,
    )
    kwargs = dict(
        card=tmp_path / "card.md",
        run_dir=tmp_path,
        current_profile={"max_wall_minutes": 30},
        recovery_context=None,
    )
    if cross_group:
        with pytest.raises(DeliveryError, match="another task group"):
            flow.launch_groups(adapter, **kwargs)
        assert assignments == [1]
    else:
        flow.launch_groups(adapter, **kwargs)
        assert assignments == [1, 2]
        # Receipt-proven completed groups do not spawn again on continuation.
        flow.launch_groups(adapter, **kwargs)
        assert assignments == [1, 2]


def test_native_checkpoint_needs_tasks_and_current_evidence(tmp_path, monkeypatch):
    done = False
    client = SimpleNamespace(
        apply_context=lambda _id: ApplyContext(
            "ready", (Task("1", "1.1 Execute", done),), (), "fixture"
        )
    )
    monkeypatch.setattr(native, "adapter", lambda _d: client)
    monkeypatch.setattr(native, "change_id", lambda _c: "fixture")
    monkeypatch.setenv("CHRL_DELIVERY_STAGE", "change")
    monkeypatch.setenv("CHRL_CHANGE_NUMBER", "1")
    adapter = SimpleNamespace(focused_evidence_summaries=lambda _r: [])
    with pytest.raises(DeliveryError, match="another task group"):
        flow.checkpoint(adapter, tmp_path, tmp_path, "change-2", "starting")
    with pytest.raises(DeliveryError, match="not complete"):
        flow.checkpoint(adapter, tmp_path, tmp_path, "change-1", "complete")
    done = True
    with pytest.raises(DeliveryError, match="current focused evidence"):
        flow.checkpoint(adapter, tmp_path, tmp_path, "change-1", "complete")
