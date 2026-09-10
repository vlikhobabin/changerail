from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.changerail import runtime_repair as repair
from scripts.changerail.contracts import DeliveryError


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project, source = tmp_path / "project", tmp_path / "source"
    run = project / ".runtime/changerail/runs/one"
    run.mkdir(parents=True)
    code = source / "scripts/changerail/core.py"
    code.parent.mkdir(parents=True)
    code.write_text("answer = 2\n")
    test = source / "tools/changerail/tests/test_core.py"
    test.parent.mkdir(parents=True)
    test.write_text(
        "import runpy\ndef test_actual_answer():\n    assert runpy.run_path('scripts/changerail/core.py')['answer'] == 2\n"
    )
    original = {
        "scripts/changerail/core.py": hashlib.sha256(b"answer = 1\n").hexdigest(),
        ".changerail/profile.toml": "profile",
    }
    metadata = {
        "process_identity": original,
        "finished_at": "stopped",
        "card": "card.md",
        "execution_contract": "changerail.native.v1",
    }
    manifest = {"run_id": "one", "path_fingerprints": {"product.py": "retained"}}
    (run / "run.json").write_text(json.dumps(metadata))
    (run / "manifest.json").write_text(json.dumps(manifest))
    state = {"payload": "unchanged", "events": [], "historical": False, "locked": False}

    def read(path: Path, limit=262144):
        if path.resolve() != path or not path.is_file():
            raise ValueError("unsafe path")
        data = path.read_bytes()
        if len(data) > limit:
            raise ValueError("oversized")
        return data

    def current(run):
        if state["historical"]:
            raise DeliveryError("historical adopted run is read-only")
        return json.loads(read(run / "run.json"))

    @contextmanager
    def lock():
        if state["locked"]:
            raise DeliveryError("another delivery runner holds the checkout")
        state["locked"] = True
        try:
            yield
        finally:
            state["locked"] = False

    def safe(value):
        if (
            not isinstance(value, str)
            or value.startswith("/")
            or ".." in Path(value).parts
        ):
            raise DeliveryError("unsafe path")
        return value

    delivery = SimpleNamespace(
        REPO_ROOT=project,
        RUNTIME_ROOT=project / ".runtime/changerail",
        _check_bytes=read,
        _check_json=lambda path: json.loads(read(path)),
        _safe_path=safe,
        require_current_execution=current,
        review_budget_usage=lambda run: {"semantic_cycles": 0},
        combined_change_events=lambda run: state["events"],
        resolve_deliverable_card=lambda card: project / card,
        recovery_source=lambda card, paths: (True, "retained", manifest),
        changed_paths=lambda: ["product.py"],
        payload_fingerprint=lambda: state["payload"],
        delivery_lock=lock,
        utc_now=lambda: "now",
        execution_identity=lambda: {
            **original,
            "scripts/changerail/core.py": hashlib.sha256(code.read_bytes()).hexdigest(),
        },
    )
    monkeypatch.setattr(
        repair.source_binding, "binding", lambda root: {"source_root": str(source)}
    )
    monkeypatch.setattr(
        repair.source_binding,
        "read_runtime",
        lambda root, path, fallback: (source / path.relative_to(root)).read_bytes(),
    )
    monkeypatch.setattr(
        repair.source_binding,
        "trusted_path",
        lambda root, path: source / path.relative_to(root),
    )
    return delivery, run, code, test, state


def prepare(workspace):
    delivery, run, *_ = workspace
    return Path(
        repair.prepare(
            delivery,
            run,
            tests=["tools/changerail/tests/test_core.py"],
            reason="Correct core answer regression",
        )["proposal"]
    )


def test_success_retains_real_assertions_without_rewriting_accounting(workspace):
    delivery, run, *_ = workspace
    original = (run / "run.json").read_bytes()
    proposal = prepare(workspace)
    assert "1 passed" in (proposal.parent / "check.log").read_text()
    assert (
        repair.effective_identity(
            delivery, run, delivery.require_current_execution(run)
        )
        != delivery.execution_identity()
    )
    repair.apply(delivery, run, proposal)
    assert (
        repair.effective_identity(
            delivery, run, delivery.require_current_execution(run)
        )
        == delivery.execution_identity()
    )
    assert (run / "run.json").read_bytes() == original
    assert delivery.review_budget_usage(run) == {"semantic_cycles": 0}


def test_failed_assertion_cannot_produce_adoption(workspace):
    _, run, code, *_ = workspace
    code.write_text("answer = 3\n")
    with pytest.raises(DeliveryError, match="focused tests did not pass"):
        prepare(workspace)
    assert not list((run / "runtime-repairs").glob("*/proposal.json"))
    assert "1 failed" in next((run / "runtime-repairs").glob("*/check.log")).read_text()


@pytest.mark.parametrize(
    "path",
    [
        "reviews",
        "verification-attempts",
        "proof-index.json",
        "focused-evidence",
        "preverification.json",
        "implementation-handoff.json",
        "native-archive.json",
        "publication.json",
    ],
)
def test_prior_proof_or_later_stage_is_never_thawed(workspace, path):
    _, run, *_ = workspace
    (run / path).write_text("{}")
    with pytest.raises(DeliveryError, match="before evidence"):
        prepare(workspace)
    assert not (run / "runtime-repairs").exists()


def test_completed_change_is_not_silently_reused(workspace):
    *_, state = workspace
    state["events"] = [{"phase": "change-1", "stage": "complete"}]
    with pytest.raises(DeliveryError, match="accepted checkpoints"):
        prepare(workspace)


@pytest.mark.parametrize("key", ["historical", "locked"])
def test_history_and_writer_guards_apply_before_verification(workspace, key):
    *_, state = workspace
    state[key] = True
    with pytest.raises(DeliveryError):
        prepare(workspace)


def test_project_configuration_cannot_be_rebound(workspace):
    delivery, *_ = workspace
    current = delivery.execution_identity
    delivery.execution_identity = lambda: {
        **current(),
        ".changerail/profile.toml": "changed",
    }
    with pytest.raises(
        DeliveryError, match="project, launcher, schemas and skills remain frozen"
    ):
        prepare(workspace)


@pytest.mark.parametrize("drift", ["source", "payload", "run", "log", "snapshot"])
def test_apply_refuses_changed_source_payload_or_proof(workspace, drift):
    delivery, run, code, _, state = workspace
    proposal = prepare(workspace)
    if drift == "source":
        code.write_text("answer = 4\n")
    elif drift == "payload":
        state["payload"] = "changed"
    elif drift == "run":
        (run / "manifest.json").write_text(
            '{"run_id":"one", "path_fingerprints":{"different":"yes"}}'
        )
    elif drift == "log":
        (proposal.parent / "check.log").write_text("1 passed, forged\n")
    else:
        (proposal.parent / "source/scripts/changerail/core.py").write_text(
            "answer = 9\n"
        )
    with pytest.raises(DeliveryError):
        repair.apply(delivery, run, proposal)
    assert not (run / "runtime-repairs/applied").exists()


def test_applied_receipt_chain_detects_tampering(workspace):
    delivery, run, *_ = workspace
    proposal = prepare(workspace)
    receipt = Path(repair.apply(delivery, run, proposal)["receipt"])
    value = json.loads(receipt.read_text())
    value["previous_sha256"] = "invented predecessor"
    receipt.write_text(json.dumps(value))
    with pytest.raises(DeliveryError, match="receipt chain changed"):
        repair.effective_identity(
            delivery, run, delivery.require_current_execution(run)
        )


def test_resume_dispatch_uses_applied_repair_and_preserves_original_run(
    workspace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Exercise real resume dispatch; replace only the external delivery launch."""
    from scripts.changerail import local_delivery

    delivery, run, *_ = workspace
    for name, value in vars(delivery).items():
        monkeypatch.setattr(local_delivery, name, value)
    monkeypatch.setattr(local_delivery, "runner_module", lambda: local_delivery)
    launched = []
    monkeypatch.setattr(
        local_delivery,
        "run_delivery",
        lambda card, *, recovery=False: launched.append((card, recovery)) or 0,
    )
    original = (run / "run.json").read_bytes()
    assert local_delivery.main(["resume", str(run)]) == 2
    assert launched == []
    capsys.readouterr()
    assert (
        local_delivery.main(
            [
                "runtime-repair-prepare",
                str(run),
                "--reason",
                "Repair reproduced answer bug",
                "--test",
                "tools/changerail/tests/test_core.py",
            ]
        )
        == 0
    )
    proposal = json.loads(capsys.readouterr().out)["proposal"]
    assert (
        local_delivery.main(
            [
                "runtime-repair-apply",
                str(run),
                "--proposal",
                proposal,
            ]
        )
        == 0
    )
    receipt = json.loads(capsys.readouterr().out)["receipt"]
    assert Path(receipt).is_file()
    assert local_delivery.main(["resume", str(run)]) == 0
    assert launched == [(str(delivery.REPO_ROOT / "card.md"), True)]
    assert (run / "run.json").read_bytes() == original
