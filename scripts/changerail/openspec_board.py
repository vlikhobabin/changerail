"""Structural admission for one-card/one-change native OpenSpec delivery."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError
from scripts.changerail import openspec_context as native


def _receipt_root(delivery: Any, card: Path) -> Path:
    return Path(delivery.REPO_ROOT) / ".runtime/changerail/native-plans" / card.stem


def require_accepted(delivery: Any, card: Path) -> Path:
    """Require the immutable admission receipt for a todo/in-progress card."""

    if card.parent.name not in {"2.todo", "3.inprogress", "4.done"}:
        raise DeliveryError("native accepted card must be todo, inprogress, or done")
    receipt = _receipt_root(delivery, card)
    native.require_plan(delivery, card, receipt)
    return receipt


def _exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def accept_card(delivery: Any, card: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Accept complete stock artifacts and move a backlog card to todo."""

    card = card.absolute()
    if (
        card.resolve(strict=True) != card
        or card.parent.parent != Path(delivery.REPO_ROOT) / "openspec/board"
    ):
        raise DeliveryError(
            "native card must belong to the local board without symlinks"
        )
    if card.parent.name not in {"1.backlog", "2.todo"}:
        raise DeliveryError("native-accept expects an exact backlog or todo card")
    if not native.is_native(card):
        raise DeliveryError("native-accept requires ## Lifecycle openspec-v1")
    delivery.require_delivery_card_structure(card)
    text = card.read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
    if len(headings) != len(set(headings)):
        raise DeliveryError("native card contains duplicate sections")
    if native._section(card, "Status") != card.parent.name:
        raise DeliveryError("native card Status differs from its board column")
    if any(path != card for path in card.parent.parent.glob(f"*/{card.name}")):
        raise DeliveryError("native card exists in multiple board columns")
    report = delivery.admission_report(card)
    if report.get("status") != "READY":
        raise DeliveryError(
            "native admission failed: " + "; ".join(report.get("reasons", []))
        )
    identity = native.plan_identity(delivery, card)
    receipt_root = _receipt_root(delivery, card)
    receipt = receipt_root / "native-plan.json"
    if receipt.exists():
        native.require_plan(delivery, card, receipt_root)
    if dry_run:
        return {
            "schema": "changerail.openspec-admission.v1",
            "status": "READY",
            "dry_run": True,
            "card": delivery.repo_relative(card),
            "change_id": native.change_id(card),
            "receipt": delivery.repo_relative(receipt),
            "moved": False,
        }
    if not receipt.exists():
        _exclusive_json(receipt, identity)
    target = card.parent.parent / "2.todo" / card.name
    moved = target != card
    if moved:
        if target.exists():
            raise DeliveryError(f"native todo destination already exists: {target}")
        before = card.read_text(encoding="utf-8")
        text = delivery.replace_section(before, "Status", ["2.todo"])
        text = delivery.replace_section(
            text,
            "Result",
            ["accepted native OpenSpec plan; structural admission only"],
        )
        log = delivery.section_body(text, "Log")
        text = delivery.replace_section(
            text,
            "Log",
            [*log, f"- {delivery.utc_now()} accepted native OpenSpec plan"],
        )
        try:
            with target.open("x", encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            native.require_plan(delivery, target, receipt_root)
            if card.read_text(encoding="utf-8") != before:
                raise DeliveryError("native source card changed during admission")
            card.unlink()
        except OSError as exc:
            raise DeliveryError(
                "native admission move is incomplete; preserve both paths for reconciliation"
            ) from exc
    delivery.rewrite_active_board_references(card.name, delivery.repo_relative(target))
    return {
        "schema": "changerail.openspec-admission.v1",
        "status": "READY",
        "dry_run": False,
        "card": delivery.repo_relative(target),
        "change_id": native.change_id(target),
        "receipt": delivery.repo_relative(receipt),
        "moved": moved,
    }


def import_accepted(delivery: Any, card: Path, run_dir: Path) -> None:
    """Copy the accepted identity into a new run without regenerating artifacts."""

    source = require_accepted(delivery, card) / "native-plan.json"
    target = run_dir / "native-plan.json"
    payload = source.read_bytes()
    if target.exists():
        if target.read_bytes() != payload:
            raise DeliveryError("run contains a different native plan")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    native.require_plan(delivery, card, target)
