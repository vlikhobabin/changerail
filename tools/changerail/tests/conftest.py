"""Keep shared harness fixtures independent of the consumer's delivery policy.

Project-owned adapter checks belong in .changerail/tests and deliberately sit
outside this fixture's scope. Tests of profiles can still select their own file.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
from types import ModuleType

import pytest

from scripts.changerail import local_delivery


@pytest.fixture(scope="session", autouse=True)
def _tmp_basetemp_stays_removable(request: pytest.FixtureRequest) -> None:
    """Let the suite clean up after itself on a small ``/tmp``.

    Engine snapshots are genuinely immutable while they exist - directories
    ``0555``, files ``0444`` - so a fixture that builds one leaves a tree pytest
    itself cannot delete. Because ``/tmp`` here is a RAM-backed tmpfs, those
    leftovers accumulate across runs until a toolchain copy fails with ENOSPC
    and the run reports a mass of unrelated errors. Restoring write permission
    once the session is over changes nothing the tests observe and keeps the
    next run's cleanup, and this run's retention, working.
    """
    yield
    factory = getattr(request.config, "_tmp_path_factory", None)
    if factory is None:
        return
    for root, directories, files in os.walk(factory.getbasetemp()):
        for name in (*directories, *files):
            path = Path(root) / name
            try:
                if not path.is_symlink():
                    path.chmod(path.lstat().st_mode | stat.S_IWUSR)
            except OSError:
                # A vanished or unreadable entry is not this hook's problem.
                continue


@pytest.fixture(autouse=True)
def shared_test_profile(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A suite invoked by the final floor inherits a real delivery owner.
    # Fixtures create independent projects and install their own authority;
    # carrying the caller's run/engine environment into them is cross-project drift.
    for key in tuple(os.environ):
        if key.startswith("CHRL_"):
            monkeypatch.delenv(key)
    profile = Path(__file__).parents[1] / "templates/profile.toml"
    modules = {local_delivery}
    # Receipt tests retain independently loaded instances to isolate mutations.
    for name in ("delivery", "d"):
        instance = getattr(request.module, name, None)
        if isinstance(instance, ModuleType) and hasattr(instance, "PROFILE_PATH"):
            modules.add(instance)
    for module in modules:
        monkeypatch.setattr(module, "PROFILE_PATH", profile)
