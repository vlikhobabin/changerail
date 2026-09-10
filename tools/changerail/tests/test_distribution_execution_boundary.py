"""An installed source update cannot thaw a previously retained run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.changerail import local_delivery as delivery


def _run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(delivery, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(delivery, "RUNTIME_ROOT", tmp_path / ".runtime/changerail")
    profile = tmp_path / ".changerail/profile.toml"
    profile.parent.mkdir()
    profile.write_text(
        'schema = "changerail.local-delivery.v1"\nmax_review_cycles = 2\n'
    )
    monkeypatch.setattr(delivery, "PROFILE_PATH", profile)
    run = tmp_path / ".runtime/changerail/runs/retained"
    run.mkdir(parents=True)
    (run / "run.json").write_text(
        json.dumps(
            {
                "schema": "changerail.delivery-run.v2",
                "run_id": run.name,
                "card": "openspec/board/3.inprogress/example.md",
                "execution_contract": "changerail.native.v1",
                "mode": "delivery",
                "lifecycle_mode": "openspec-v1",
                "started_at": "2026-09-09T00:00:00Z",
                "change_plan": [],
                "process_identity": delivery.execution_identity(),
            }
        )
    )
    return run


def test_distribution_retirement_overrides_matching_contract(tmp_path, monkeypatch):
    run = _run(tmp_path, monkeypatch)
    before = (run / "run.json").read_bytes()
    entry = {
        "sha256": hashlib.sha256(before).hexdigest(),
        "size": len(before),
        "mode": 0o644,
        "execution_contract": "changerail.native.v1",
    }
    (tmp_path / ".changerail/distribution-lock.json").write_text(
        json.dumps(
            {
                "schema": "changerail.installation.v1",
                "retained_read_only_runs": {
                    str((run / "run.json").relative_to(tmp_path)): entry
                },
            }
        )
    )
    with pytest.raises(delivery.DeliveryError, match="histor|read-only"):
        delivery.require_current_execution(run)
    assert (run / "run.json").read_bytes() == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("execution_contract", None),
        ("mode", "recovery"),
        ("lifecycle_mode", "board-only"),
    ],
)
def test_historical_execution_refusal_preserves_bytes(
    tmp_path, monkeypatch, field, value
):
    run = _run(tmp_path, monkeypatch)
    metadata = json.loads((run / "run.json").read_bytes())
    metadata[field] = value
    (run / "run.json").write_text(json.dumps(metadata))
    before = (run / "run.json").read_bytes()
    with pytest.raises(delivery.DeliveryError):
        delivery.require_current_execution(run)
    assert (run / "run.json").read_bytes() == before


def test_changed_profile_does_not_adopt_frozen_execution(tmp_path, monkeypatch):
    run = _run(tmp_path, monkeypatch)
    delivery.require_frozen_execution(run)
    delivery.PROFILE_PATH.write_text(
        delivery.PROFILE_PATH.read_text() + "require_push = false\n"
    )
    with pytest.raises(delivery.DeliveryError, match="process changed"):
        delivery.require_frozen_execution(run)


def test_metrics_and_status_leave_historical_files_untouched(tmp_path, monkeypatch):
    run = _run(tmp_path, monkeypatch)
    old = json.loads((run / "run.json").read_bytes())
    old.pop("execution_contract")
    old["schema"] = "prior.delivery-run.v1"
    (run / "run.json").write_text(json.dumps(old))
    (run / "metrics.json").write_text('{"historical":true}\n')
    before = {p.relative_to(run): p.read_bytes() for p in run.rglob("*") if p.is_file()}
    assert delivery.main(["status", str(run)]) == 0
    assert delivery.main(["metrics", str(run)]) == 0
    assert {
        p.relative_to(run): p.read_bytes() for p in run.rglob("*") if p.is_file()
    } == before
