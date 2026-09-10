"""Keep shared harness fixtures independent of the consumer's delivery policy.

Project-owned adapter checks belong in .changerail/tests and deliberately sit
outside this fixture's scope. Tests of profiles can still select their own file.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import pytest

from scripts.changerail import local_delivery


@pytest.fixture(autouse=True)
def shared_test_profile(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile = Path(__file__).parents[1] / "templates/profile.toml"
    modules = {local_delivery}
    # Receipt tests retain independently loaded instances to isolate mutations.
    for name in ("delivery", "d"):
        instance = getattr(request.module, name, None)
        if isinstance(instance, ModuleType) and hasattr(instance, "PROFILE_PATH"):
            modules.add(instance)
    for module in modules:
        monkeypatch.setattr(module, "PROFILE_PATH", profile)
