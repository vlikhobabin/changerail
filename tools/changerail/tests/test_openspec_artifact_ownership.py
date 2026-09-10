"""Artifact ownership remains strict while unrelated backlog plans are incomplete."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.changerail import openspec_context as native
from scripts.changerail.contracts import DeliveryError


def card(root: Path, column: str, name: str, declaration: str) -> Path:
    path = root / "openspec/board" / column / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {name}\n\n## Lifecycle\nopenspec-v1\n\n{declaration}")
    return path


@pytest.mark.parametrize(
    "declaration",
    [
        "",
        "## OpenSpec Changes\n1. `archive`\n",
        "## OpenSpec Changes\n1. `one`\n2. `two`\n",
    ],
)
def test_incomplete_backlog_does_not_block_independent_owner(tmp_path, declaration):
    pending = card(tmp_path, "1.backlog", "planning", declaration)
    card(tmp_path, "2.todo", "accepted", "## OpenSpec Changes\n1. `owned-change`\n")
    before = pending.read_bytes()
    native.require_owned_artifacts(
        SimpleNamespace(REPO_ROOT=tmp_path),
        {"openspec/changes/owned-change/proposal.md"},
        {"openspec/changes/historical/tasks.md"},
    )
    assert pending.read_bytes() == before
    # Skipping the incomplete card in global inventory does not admit that card.
    with pytest.raises(DeliveryError, match="exactly one ordered entry"):
        native.change_id(pending)


def test_incomplete_backlog_cannot_claim_an_extra_tree(tmp_path):
    card(tmp_path, "1.backlog", "unowned-change", "")
    with pytest.raises(DeliveryError, match="unowned addition"):
        native.require_owned_artifacts(
            SimpleNamespace(REPO_ROOT=tmp_path),
            {"openspec/changes/unowned-change/proposal.md"},
            set(),
        )


@pytest.mark.parametrize("column", ["2.todo", "3.inprogress"])
def test_incomplete_accepted_card_still_blocks_ownership(tmp_path, column):
    card(tmp_path, column, "incomplete", "")
    card(tmp_path, "4.done", "completed", "## OpenSpec Changes\n1. `owned-change`\n")
    with pytest.raises(DeliveryError, match="exactly one ordered entry"):
        native.require_owned_artifacts(
            SimpleNamespace(REPO_ROOT=tmp_path),
            {"openspec/changes/archive/2026-09-09-owned-change/tasks.md"},
            set(),
        )


@pytest.mark.parametrize("column", ["1.backlog", "2.todo", "4.done"])
def test_duplicate_valid_owners_are_refused_including_backlog(tmp_path, column):
    declaration = "## OpenSpec Changes\n1. `owned-change`\n"
    card(tmp_path, column, "duplicate", declaration)
    card(tmp_path, "3.inprogress", "accepted", declaration)
    with pytest.raises(DeliveryError, match="multiple card owners"):
        native.require_owned_artifacts(
            SimpleNamespace(REPO_ROOT=tmp_path),
            {"openspec/changes/owned-change/tasks.md"},
            set(),
        )


def test_closed_valid_owner_can_own_new_archive_but_frozen_tree_cannot_grow(tmp_path):
    card(tmp_path, "1.backlog", "planning", "")
    card(tmp_path, "4.done", "completed", "## OpenSpec Changes\n1. `owned-change`\n")
    delivery = SimpleNamespace(REPO_ROOT=tmp_path)
    extra = {"openspec/changes/archive/2026-09-09-owned-change/tasks.md"}
    native.require_owned_artifacts(delivery, extra, set())
    with pytest.raises(DeliveryError, match="unowned addition"):
        native.require_owned_artifacts(
            delivery,
            extra,
            {"openspec/changes/archive/2026-09-09-owned-change/proposal.md"},
        )
