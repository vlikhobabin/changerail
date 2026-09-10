"""Targeted checks select additive regression commands from changed paths."""

from __future__ import annotations

import copy

import pytest

from scripts.changerail.contracts import DeliveryError
from scripts.changerail.targeted_checks import select_targeted_commands


@pytest.fixture
def profile():
    return {
        "verification": {"commands": ["run full floor"]},
        "targeted": [
            {
                "paths": ["src/indexing/source_unit*.py", "src/postgres/refresh.py"],
                "commands": ["run source-unit regression", "run shared regression"],
            },
            {
                "paths": ["src/indexing/lifecycle.py", "src/indexing/*staging.py"],
                "commands": ["run readiness regression", "run shared regression"],
            },
            {"paths": ["frontend/*.js"], "commands": ["npm test -- --runInBand"]},
        ],
    }


def test_matching_rule_adds_all_commands_without_replacing_floor(profile):
    before = copy.deepcopy(profile)
    assert select_targeted_commands(profile, ["src/indexing/source_unit_ir.py"]) == [
        "run source-unit regression",
        "run shared regression",
    ]
    assert profile == before
    assert profile["verification"]["commands"] == ["run full floor"]


def test_changes_to_another_area_add_its_regressions(profile):
    assert select_targeted_commands(
        profile, ["src/indexing/source_unit_ir.py", "src/indexing/lifecycle.py"]
    ) == [
        "run source-unit regression",
        "run shared regression",
        "run readiness regression",
    ]
    assert select_targeted_commands(profile, ["src/indexing/lifecycle.py"]) == [
        "run readiness regression",
        "run shared regression",
    ]


def test_deleted_path_still_selects_its_regression_without_filesystem_access(profile):
    # The removed file need not exist; Git's changed path remains a selector.
    assert select_targeted_commands(profile, ["src/postgres/refresh.py"]) == [
        "run source-unit regression",
        "run shared regression",
    ]


def test_rename_endpoints_select_both_affected_domains(profile):
    assert select_targeted_commands(
        profile, ["src/postgres/refresh.py", "frontend/refresh.js"]
    ) == [
        "run source-unit regression",
        "run shared regression",
        "npm test -- --runInBand",
    ]


def test_command_order_is_stable_for_duplicate_and_reordered_paths(profile):
    paths = [
        "frontend/app.js",
        "src/indexing/lifecycle.py",
        "src/indexing/source_unit.py",
    ]
    expected = [
        "run source-unit regression",
        "run shared regression",
        "run readiness regression",
        "npm test -- --runInBand",
    ]
    assert select_targeted_commands(profile, paths) == expected
    assert select_targeted_commands(profile, list(reversed(paths)) + paths) == expected


def test_matching_is_case_sensitive_fnmatch_including_nested_paths(profile):
    assert select_targeted_commands(profile, ["Frontend/app.js"]) == []
    assert select_targeted_commands(profile, ["frontend/widgets/app.js"]) == [
        "npm test -- --runInBand"
    ]


def test_absent_or_unmatched_rules_add_nothing(profile):
    assert select_targeted_commands({}, ["src/file.py"]) == []
    assert select_targeted_commands(profile, []) == []
    assert select_targeted_commands(profile, ["docs/guide.md"]) == []


@pytest.mark.parametrize(
    "rule",
    [
        {},
        {"paths": ["src/*"]},
        {"paths": ["src/*"], "commands": ["run tests"], "replace": True},
        {"paths": "src/*", "commands": ["run tests"]},
        {"paths": [], "commands": ["run tests"]},
        {"paths": ["../src/*"], "commands": ["run tests"]},
        {"paths": ["/src/*"], "commands": ["run tests"]},
        {"paths": ["src/*"], "commands": "run tests"},
        {"paths": ["src/*"], "commands": []},
        {"paths": ["src/*"], "commands": [""]},
        {"paths": ["src/*"], "commands": [" "]},
        {"paths": ["src/*"], "commands": [12]},
        {"paths": ["src/*"], "commands": ["run\x00tests"]},
        {"paths": [None], "commands": ["run tests"]},
    ],
)
def test_invalid_rules_fail_even_when_no_path_matches(rule):
    with pytest.raises(DeliveryError):
        select_targeted_commands({"targeted": [rule]}, ["docs/guide.md"])


@pytest.mark.parametrize(
    "paths",
    [
        "src/file.py",
        ["../src/file.py"],
        ["/src/file.py"],
        ["src/./file.py"],
        ["src//file.py"],
        [None],
        [""],
    ],
)
def test_invalid_changed_path_input_fails(paths):
    with pytest.raises(DeliveryError):
        select_targeted_commands({}, paths)


@pytest.mark.parametrize("rules", [None, {}, "src/*"])
def test_invalid_targeted_container_fails(rules):
    with pytest.raises(DeliveryError):
        select_targeted_commands({"targeted": rules}, [])
