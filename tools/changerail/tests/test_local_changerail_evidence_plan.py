from __future__ import annotations

import copy
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(REPO_ROOT))
delivery = importlib.import_module("scripts.changerail.local_delivery")
sys.path.pop(0)
SCHEMA = json.loads(
    (REPO_ROOT / "tools/changerail/schemas/card-evidence.schema.json").read_text()
)


def _plan(ids: tuple[str, ...] = ("C1",)) -> dict[str, object]:
    return {
        "schema": "changerail.card-evidence.v1",
        "conditions": [
            {
                "condition": condition,
                "seam": "parser",
                "precondition": "a card",
                "action": "validate",
                "expected": "a declaration",
                "stage": "final" if index else "implementation",
                "method": {
                    "kind": "runtime" if index else "test",
                    "target": "src/example/core/future.py::test_plan",
                },
            }
            for index, condition in enumerate(ids)
        ],
        "risks": [
            {
                "kinds": ["input_safety"],
                "applies": True,
                "decision": "closed input",
                "conditions": list(ids),
            },
            {
                "kinds": ["mutation", "restart"],
                "applies": True,
                "decision": "read-only gate",
                "conditions": [ids[0]],
            },
            {
                "kinds": ["concurrency", "publication", "external_effects"],
                "applies": False,
                "decision": "not applicable",
                "conditions": [],
            },
        ],
    }


def _text(
    acceptance: str, plan: dict[str, object] | str, *, extra_verify: str = ""
) -> str:
    rendered = plan if isinstance(plan, str) else json.dumps(plan, indent=2)
    return (
        "# Evidence card\n\n## Acceptance\n" + acceptance + "\n\n"
        "## Design\n- static declaration\n\n## Verify\n"
        "A future target remains inert.\n\n```json\n"
        + rendered
        + "\n```\n"
        + extra_verify
    )


@pytest.mark.parametrize(
    ("acceptance", "ids"),
    [
        ("- [C1] compact acceptance\n  wrapped continuation", ("C1",)),
        (
            "### Requirement: structured\n#### Scenario: plan\n- [C1] WHEN one fact\n- [C2] THEN another fact\n  wrapped continuation",
            ("C1", "C2"),
        ),
    ],
)
def test_complete_plan_shapes(acceptance: str, ids: tuple[str, ...]) -> None:
    text = _text(
        acceptance, _plan(ids), extra_verify="\n- shell checks may be listed here\n"
    )
    assert delivery.validate_evidence_plan_text(text, SCHEMA)["conditions"]
    assert delivery.validate_evidence_plan_text(text, SCHEMA, phase="specs") == {
        "conditions": list(ids)
    }
    design_plan = _plan(ids)
    design_plan["conditions"] = []
    assert (
        delivery.validate_evidence_plan_text(
            _text(acceptance, design_plan), SCHEMA, phase="design"
        )["conditions"]
        == []
    )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda plan: plan.pop("schema"), "required property"),
        (
            lambda plan: plan.__setitem__("schema", "unknown.v1"),
            "changerail.card-evidence.v1",
        ),
        (lambda plan: plan.__setitem__("unknown", True), "Additional properties"),
        (lambda plan: plan["conditions"][0].pop("expected"), "required property"),  # type: ignore[index]
        (
            lambda plan: plan["conditions"][0].__setitem__("seam", "   "),
            "does not match",
        ),  # type: ignore[index]
        (
            lambda plan: plan["conditions"][0].__setitem__("stage", "later"),
            "not one of",
        ),  # type: ignore[index]
        (
            lambda plan: plan["conditions"][0]["method"].__setitem__("kind", "shell"),
            "not one of",
        ),  # type: ignore[index]
        (
            lambda plan: plan["conditions"][0]["method"].__setitem__(
                "target", "https://future.example/test"
            ),
            "inert relative locator",
        ),  # type: ignore[index]
        (
            lambda plan: plan["risks"][0].__setitem__("applies", "true"),
            "is not of type 'boolean'",
        ),  # type: ignore[index]
        (
            lambda plan: plan["risks"][0].__setitem__("conditions", ["C2"]),
            "foreign conditions",
        ),  # type: ignore[index]
        (
            lambda plan: plan["risks"][0].__setitem__(
                "kinds", ["input_safety", "input_safety"]
            ),
            "non-unique",
        ),  # type: ignore[index]
    ],
)
def test_plan_validation_boundaries(mutate, message: str) -> None:
    plan = _plan()
    mutate(plan)
    with pytest.raises(delivery.DeliveryError, match=message):
        delivery.validate_evidence_plan_text(_text("- [C1] a condition", plan), SCHEMA)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (_text("- a condition", _plan()), r"requires a \[C<number>\]"),
        (_text("- [C1] one\n- [C1] two", _plan()), "duplicate Acceptance"),
        (_text("- [C1] one", _plan(("C2",))), "foreign Acceptance"),
        (
            _text("- [C1] one", _plan(), extra_verify="```json\n{}\n```"),
            "exactly one fenced",
        ),
        (_text("- [C1] one", '{"schema": ').removesuffix("```\n"), "unclosed"),
        (
            _text(
                "- [C1] one", '{"schema":"changerail.card-evidence.v1","schema":"x"}'
            ),
            "duplicate JSON key",
        ),
        (
            _text("- [C1] one", _plan()).replace(
                "## Design", "## Design\n- again\n\n## Design"
            ),
            "exactly one ## Design",
        ),
        (
            _text("- [C1] one", _plan()).replace(
                "## Acceptance", "## Acceptance\n- [C2] second\n\n## Acceptance"
            ),
            "exactly one ## Acceptance",
        ),
    ],
)
def test_plan_parser_refusals(text: str, message: str) -> None:
    with pytest.raises(delivery.DeliveryError, match=message):
        delivery.validate_evidence_plan_text(text, SCHEMA)


def test_card_and_future_target_are_read_only(tmp_path: Path) -> None:
    card = tmp_path / "card.md"
    card.write_text(_text("- [C1] inert", _plan()))
    before = card.read_bytes()
    assert delivery.validate_evidence_plan(card)["conditions"][0]["condition"] == "C1"
    assert card.read_bytes() == before
    future = copy.deepcopy(_plan())
    future["conditions"][0]["method"]["target"] = (
        "docs/development/future-proof.md::planned_case"
    )
    assert delivery.validate_evidence_plan_text(_text("- [C1] inert", future), SCHEMA)[
        "conditions"
    ]


@pytest.mark.parametrize(
    ("target", "valid"),
    [
        ("AGENTS.md", True),
        ("src/example/core/application.py", True),
        ("docs/development/example.md::future_case", True),
        ("/tmp/x", False),
        ("../x", False),
        ("..::selector", False),
        (".::selector", False),
        ("tests/x.py;echo nope", False),
    ],
)
def test_target_locators_are_inert_and_segment_safe(target: str, valid: bool) -> None:
    plan = _plan()
    plan["conditions"][0]["method"]["target"] = target  # type: ignore[index]
    text = _text("- [C1] locator", plan)
    if valid:
        assert delivery.validate_evidence_plan_text(text, SCHEMA)["conditions"]
    else:
        with pytest.raises(delivery.DeliveryError, match="inert relative locator"):
            delivery.validate_evidence_plan_text(text, SCHEMA)


@pytest.mark.parametrize(
    "bullet",
    ["* untagged", "+ untagged", "- [C0] zero", "- [C1] one\n- [C1] duplicate"],
)
def test_all_top_level_acceptance_bullets_are_restricted(bullet: str) -> None:
    with pytest.raises(delivery.DeliveryError):
        delivery.validate_evidence_plan_text(_text(bullet, _plan()), SCHEMA)


def test_design_allows_only_known_partial_rows_and_tasks_requires_all_rows() -> None:
    plan = _plan(("C1", "C2"))
    _text("- [C1] first\n- [C2] second", plan)
    partial = copy.deepcopy(plan)
    partial["conditions"] = partial["conditions"][:1]
    assert delivery.validate_evidence_plan_text(
        _text("- [C1] first\n- [C2] second", partial), SCHEMA, phase="design"
    )
    with pytest.raises(delivery.DeliveryError, match="exactly match"):
        delivery.validate_evidence_plan_text(
            _text("- [C1] first\n- [C2] second", partial), SCHEMA
        )
    partial["conditions"][0]["condition"] = "C9"  # type: ignore[index]
    with pytest.raises(delivery.DeliveryError, match="foreign Acceptance"):
        delivery.validate_evidence_plan_text(
            _text("- [C1] first\n- [C2] second", partial), SCHEMA, phase="design"
        )


def test_native_card_declares_static_evidence_before_artifact_creation(
    tmp_path: Path,
) -> None:
    card = tmp_path / "card.md"
    card.write_text(
        "# Native fixture\n\n## Lifecycle\nopenspec-v1\n\n"
        + _text("- [C1] inert", _plan()).replace("# Evidence card\n", "")
    )
    assert (
        delivery.validate_evidence_plan(card)["schema"] == "changerail.card-evidence.v1"
    )
    assert delivery.native.lifecycle_mode(card) == "openspec-v1"
    with pytest.raises(delivery.DeliveryError, match="exactly one ordered"):
        delivery.native.change_id(card)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda plan: plan.__setitem__("observed_result", "pass"),
            "Additional properties",
        ),
        (
            lambda plan: plan["conditions"].append(
                copy.deepcopy(plan["conditions"][0])
            ),
            "duplicate evidence-plan condition rows",
        ),  # type: ignore[index]
        (lambda plan: plan["risks"].pop(), "cover exactly"),
        (
            lambda plan: plan["risks"][1].__setitem__(
                "kinds", ["mutation", "input_safety"]
            ),
            "duplicate evidence-plan risk kinds",
        ),  # type: ignore[index]
        (lambda plan: plan["risks"][0].__setitem__("decision", " "), "does not match"),  # type: ignore[index]
        (
            lambda plan: plan["risks"][0].__setitem__("conditions", []),
            "applicable evidence-plan risk",
        ),  # type: ignore[index]
        (
            lambda plan: plan["risks"][2].__setitem__("conditions", ["C1"]),
            "non-applicable evidence-plan risk",
        ),  # type: ignore[index]
    ],
)
def test_remaining_closed_plan_matrix(mutate, message: str) -> None:
    plan = _plan()
    mutate(plan)
    with pytest.raises(delivery.DeliveryError, match=message):
        delivery.validate_evidence_plan_text(_text("- [C1] a condition", plan), SCHEMA)
