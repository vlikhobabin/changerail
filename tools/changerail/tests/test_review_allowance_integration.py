"""Review launch/recovery integration with isolated artifact/proof adapters.

Real CLI resume, locks, initial contexts, verdict consumer and accounting run;
the existing review fixture isolates native artifact and typed-proof adapters.
The companion API tests exercise real accepted native plan/frozen proof identity.
"""

from __future__ import annotations

import json
import multiprocessing
import sys
from pathlib import Path

import pytest

from scripts.changerail import engine_snapshot, native_workflow, review_allowance as policy
from tools.changerail.tests.test_local_changerail_delivery import (
    delivery, _review_fixture, _write_matching_preverification,
)

REAL_LAUNCH = delivery.launch_codex


def snapshot(run):
    return {p.relative_to(run).as_posix(): p.read_bytes() for p in run.rglob("*") if p.is_file()}


@pytest.fixture
def lineage(tmp_path, monkeypatch):
    root, card, run = _review_fixture(tmp_path, monkeypatch)
    profile = root / ".changerail/profile.toml"
    profile.parent.mkdir(exist_ok=True)
    profile.write_bytes(delivery.PROFILE_PATH.read_bytes())
    monkeypatch.setattr(delivery, "PROFILE_PATH", profile)
    monkeypatch.setattr(engine_snapshot, "_no_live_delivery", lambda _root: None)
    # Artifact/proof adapters are covered by the companion native eligibility tests.
    monkeypatch.setattr(delivery.native, "require_plan", lambda *args: None)
    monkeypatch.setattr(delivery, "_run_observed_contract", lambda _run: None)
    plan = {"groups": [], "change_id": "fixture-change"}
    delivery.write_json(run / "native-plan.json", plan)
    delivery.write_json(delivery.RUNTIME_ROOT / "native-plans" / card.stem / "native-plan.json", plan)
    launches = []

    def reviewer(**kwargs):
        selected = kwargs["run_dir"]
        context = delivery._check_json(Path(kwargs["session_env"]["CHRL_REVIEW_CONTEXT"]))
        ordinal = int(kwargs["session_env"]["CHRL_LINEAGE_REVIEW_NUMBER"])
        assert context["lineage_review_number"] == ordinal
        assert delivery.review_budget_usage(selected)["semantic_cycles"] == ordinal - 1
        if ordinal > 2:
            claim = delivery._check_json(selected / "recovery-context.json")
            assert claim["review_authorization"] == context["review_authorization"]
            assert claim["current_fingerprint"] != delivery.payload_fingerprint()
        launches.append((selected.name, context["cycle"], ordinal))
        session = selected / "sessions" / f"review-{context['cycle']:02d}"
        delivery.write_json(session / "session.json", {
            "session": session.name, "role": "review", "started_at": delivery.utc_now(),
            "finished_at": delivery.utc_now(), "duration_seconds": 0, "exit_code": 0,
            "completed": True, "stop_reason": "completed", "lineage_review_number": ordinal,
        })
        (session / "events.jsonl").write_text(json.dumps({"observed_at": delivery.utc_now(),
            "event": {"type": "thread.started", "thread_id": f"review-thread-{ordinal}"}}) + "\n")
        kwargs["on_session_started"](session)
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["result"] = "no-go"
        verdict["acceptance"][0].update(result="fail", evidence=["remaining behavior failure"])
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", reviewer)
    for number in (1, 2):
        (root / "tracked.txt").write_text(f"payload {number}\n")
        delivery.capture_manifest(str(card))
        _write_matching_preverification(card, run)
        assert delivery.run_review(str(card)) == 3
    metadata = delivery._check_json(run / "run.json")
    metadata.update(process_identity=delivery.execution_identity(), finished_at=delivery.utc_now(),
                    exit_code=2, terminal_reason="shared two-review budget exhausted after NO-GO")
    delivery.write_json(run / "run.json", metadata)
    monkeypatch.delenv("CHRL_RUN_DIR")

    def doctor(_card, **kwargs):
        return {"ok": True, "recovery_of": kwargs["required_run_id"]}

    monkeypatch.setattr(delivery, "doctor", doctor)  # Installation/remote checks only.

    def implementation(**kwargs):
        child = kwargs["run_dir"]
        context = delivery._check_json(child / "recovery-context.json")
        assert context["review_authorization"]["review_number"] == len(launches) + 1
        # This is the first writer: INITIAL authorization must already be durable.
        assert context["current_fingerprint"] == delivery.payload_fingerprint()
        (root / "tracked.txt").write_text(f"legitimate repair for ordinal {len(launches) + 1}\n")
        delivery.write_json(child / "native-plan.json", plan)
        delivery.capture_manifest(str(card))
        _write_matching_preverification(card, child)
        assert policy.allowance(delivery, child)["remaining"] == 1
        return "implementation-thread"

    monkeypatch.setattr(delivery, "launch_implementation_stage", implementation)
    return root, card, run, launches


def authorize(run, reason):
    proposal = policy.review_allow(delivery, run, reason=reason)
    return policy.review_allow(delivery, run, reason=reason, authorize=proposal["proposal_sha256"])


def test_public_resume_grants_third_then_fourth_without_reset_or_history_edits(lineage):
    _root, card, original, launches = lineage
    histories = {original: snapshot(original)}
    # Two autonomous NO-GO exhaust the shared allowance: resume reports the
    # retained decision point (3) without touching the frozen predecessor.
    assert delivery.main(["resume", str(original)]) == 3
    assert snapshot(original) == histories[original]
    assert launches == [(original.name, 1, 1), (original.name, 2, 2)]
    for ordinal in (3, 4):
        predecessor = list(histories)[-1]
        receipt = authorize(predecessor, f"repair remaining failure before review {ordinal}")
        child = delivery.RUNTIME_ROOT / "runs" / receipt["proposal"]["successor_run_id"]
        assert not child.exists()
        assert delivery.main(["resume", str(predecessor)]) == 3  # NO-GO after granted review.
        assert launches[-1] == (child.name, 1, ordinal)
        assert delivery.review_budget_usage(child) == {"semantic_cycles": ordinal}
        stopped = delivery._check_json(child / "run.json")
        assert f"spent={ordinal}, remaining=0" in stopped["terminal_reason"]
        assert stopped["stop_state"] == "awaiting-operator-decision"
        # The fixture profile configures no diagnosis model route, so the
        # deterministic analysis and the operator menu are what the run reports.
        decision = stopped["awaiting_decision"]
        assert decision["schema"] == "changerail.awaiting-operator-decision.v1"
        assert decision["primary_class"] is None
        assert decision["recommendation"] is None
        assert "amend-criterion" in decision["options"]
        assert (delivery.REPO_ROOT / decision["diagnosis"]).is_file()

        assert "amend-criterion" in stopped["awaiting_decision"]["options"]
        assert stopped["exit_code"] == 3
        status = policy.allowance(delivery, child)
        assert (status["operator_granted_slots"], status["spent_reviews"], status["remaining"]) == (ordinal - 2, ordinal, 0)
        assert status["in_flight"] is False
        for origin, before in histories.items():
            assert snapshot(origin) == before
        before_children = set((delivery.RUNTIME_ROOT / "runs").iterdir())
        assert delivery.main(["resume", str(child)]) == 3
        assert set((delivery.RUNTIME_ROOT / "runs").iterdir()) == before_children
        assert len(launches) == ordinal
        histories[child] = snapshot(child)
    assert len(list((delivery.RUNTIME_ROOT / "review-authorizations" / original.name).glob("*.json"))) == 2
    assert delivery.main(["status", str(child)]) == 0
    assert card.exists()


@pytest.mark.parametrize("boundary", ["mkdir", "context", "dispatch"])
def test_partial_claim_never_creates_another_child_or_reviewer(lineage, monkeypatch, boundary):
    _root, _card, origin, launches = lineage
    before = snapshot(origin)
    receipt = authorize(origin, "repair only after explicit review allowance")
    child = delivery.RUNTIME_ROOT / "runs" / receipt["proposal"]["successor_run_id"]
    if boundary == "mkdir":
        child.mkdir()
    elif boundary == "context":
        original_build = delivery.build_recovery_context

        def stop(**kwargs):
            original_build(**kwargs)
            raise delivery.DeliveryError("fixture crash after INITIAL context")

        monkeypatch.setattr(delivery, "build_recovery_context", stop)
        assert delivery.main(["resume", str(origin)]) == 2
    else:
        def stop(**kwargs):
            assert (kwargs["run_dir"] / "recovery-context.json").exists()
            raise delivery.DeliveryError("fixture crash before first writer")

        monkeypatch.setattr(delivery, "execute_prepared_delivery", stop)
        assert delivery.main(["resume", str(origin)]) == 2
    partial = snapshot(child)
    assert delivery.main(["resume", str(origin)]) == 2
    assert snapshot(child) == partial
    if (child / "manifest.json").exists():
        assert delivery.main(["resume", str(child)]) == 2
    assert len(launches) == 2
    assert sorted((delivery.RUNTIME_ROOT / "runs").iterdir()) == sorted([origin, child])
    assert snapshot(origin) == before


def test_granted_review_context_without_verdict_never_relaunches(lineage, monkeypatch):
    root, card, origin, launches = lineage
    receipt = authorize(origin, "repair with one reviewer only")
    child = delivery.RUNTIME_ROOT / "runs" / receipt["proposal"]["successor_run_id"]

    def interrupted(**kwargs):
        context = delivery._check_json(Path(kwargs["session_env"]["CHRL_REVIEW_CONTEXT"]))
        launches.append((child.name, context["cycle"], context["lineage_review_number"]))
        return 1

    monkeypatch.setattr(delivery, "launch_codex", interrupted)
    assert delivery.main(["resume", str(origin)]) == 2
    assert policy.allowance(delivery, child)["in_flight"] is True
    monkeypatch.setenv("CHRL_RUN_DIR", str(child))
    with pytest.raises(delivery.DeliveryError, match="allocation is unresolved"):
        delivery.run_review(str(card))
    assert len(launches) == 3
    monkeypatch.delenv("CHRL_RUN_DIR")
    with pytest.raises(delivery.DeliveryError, match="unresolved review"):
        authorize(child, "must not turn interrupted allocation into another grant")
    assert (root / "tracked.txt").read_text().startswith("legitimate repair")


def claim_only(lineage, monkeypatch):
    root, card, origin, _launches = lineage
    receipt = authorize(origin, "one review with preserved native continuation")
    child = delivery.RUNTIME_ROOT / "runs" / receipt["proposal"]["successor_run_id"]
    monkeypatch.setattr(delivery, "execute_prepared_delivery", lambda **kwargs: 0)
    assert delivery.main(["resume", str(origin)]) == 0
    monkeypatch.setenv("CHRL_RUN_DIR", str(child))
    (root / "tracked.txt").write_text("repaired payload\n")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, child)
    return card, child, receipt


def test_granted_native_provisional_and_final_share_ordinal_thread_and_one_slot(lineage, monkeypatch):
    card, child, receipt = claim_only(lineage, monkeypatch)
    monkeypatch.setattr(delivery.native, "is_native", lambda _card: True)
    monkeypatch.setattr(native_workflow, "require_sync", lambda *args: None)
    monkeypatch.setattr(delivery.native, "delivery_context", lambda *args: {})
    calls = []

    def reviewer(**kwargs):
        context = delivery._check_json(Path(kwargs["session_env"]["CHRL_REVIEW_CONTEXT"]))
        assert context["lineage_review_number"] == 3
        assert context["review_authorization"] == receipt["authorization"]
        calls.append(kwargs)
        session = child / "sessions" / f"review-{len(calls):02d}"
        delivery.write_json(session / "session.json", {
            "role": "review", "started_at": delivery.utc_now(), "finished_at": delivery.utc_now(),
            "duration_seconds": 0, "exit_code": 0, "completed": True,
        })
        (session / "events.jsonl").write_text(json.dumps({"observed_at": delivery.utc_now(),
            "event": {"type": "thread.started", "thread_id": "granted-independent-thread"}}) + "\n")
        kwargs["on_session_started"](session)
        verdict = delivery.verdict_template(str(card))["template"]
        verdict["acceptance"][0]["evidence"] = ["native phase reviewed"]
        delivery.write_json(delivery.verdict_path(card.stem), verdict)
        return 0

    monkeypatch.setattr(delivery, "launch_codex", reviewer)
    assert delivery.run_review(str(card)) == 0
    status = policy.allowance(delivery, child)
    assert (status["spent_reviews"], status["remaining"], status["in_flight"]) == (2, 1, True)
    assert delivery.run_review(str(card)) == 0
    assert len(calls) == 1
    # Stock archive/sync are adapter seams here; native continuation remains real.
    delivery.write_json(child / "native-archive.json", {})
    card.write_text(card.read_text() + "\nPost-archive Result/Log evidence refresh.\n")
    delivery.capture_manifest(str(card))
    _write_matching_preverification(card, child)
    assert delivery.run_review(str(card)) == 0
    assert len(calls) == 2
    assert calls[0]["resume_thread_id"] is None
    assert calls[1]["resume_thread_id"] == "granted-independent-thread"
    assert calls[1]["session_env"]["CHRL_NATIVE_REVIEW_PHASE"] == "final"
    assert delivery.review_budget_usage(child) == {"semantic_cycles": 3}
    assert policy.allowance(delivery, child)["remaining"] == 0
    assert len(delivery._completed_review_verdicts(child / "reviews")) == 1
    assert len(list((child / "sessions").glob("review-*/session.json"))) == 2


def test_grant_does_not_bypass_failed_floor_handoff_or_publication(lineage, monkeypatch):
    card, child, _receipt = claim_only(lineage, monkeypatch)
    assert policy.allowance(delivery, child)["remaining"] == 1
    with pytest.raises(delivery.DeliveryError, match="without a handoff"):
        delivery.require_current_implementation_handoff(card, child)
    delivery.write_json(child / "verification.json", {"ok": False, "fingerprint": delivery.payload_fingerprint()})
    with pytest.raises(delivery.DeliveryError, match="unchanged failed final floor"):
        delivery.run_review(str(card))
    with pytest.raises(delivery.DeliveryError, match="unchanged failed final floor"):
        delivery.require_repaired_final_payload(child)
    assert not (child / "reviews").exists() or not list((child / "reviews").glob("cycle-*.json"))
    assert delivery.main(["resume", str(child)]) == 2
    assert not (child / "publication.json").exists()


def test_granted_review_real_subprocess_receipt_retains_ordinal_and_context(lineage, monkeypatch):
    card, child, receipt = claim_only(lineage, monkeypatch)
    verdict = delivery.verdict_template(str(card))["template"]
    verdict["acceptance"][0]["evidence"] = ["synthetic reviewer subprocess"]
    artifact = delivery.verdict_path(card.stem)
    script = (
        "import json,os,pathlib,sys; "
        "assert os.environ['CHRL_LINEAGE_REVIEW_NUMBER']=='3'; "
        "context=json.loads(pathlib.Path(os.environ['CHRL_REVIEW_CONTEXT']).read_text()); "
        "assert context['lineage_review_number']==3; "
        "pathlib.Path(sys.argv[1]).write_text(sys.argv[2]); "
        "print(json.dumps({'type':'thread.started','thread_id':'actual-synthetic-review'}))"
    )
    monkeypatch.setattr(delivery, "codex_session_command",
                        lambda **kwargs: [sys.executable, "-c", script, str(artifact), json.dumps(verdict)])
    monkeypatch.setattr(delivery, "launch_codex", REAL_LAUNCH)
    assert delivery.run_review(str(card)) == 0
    session = delivery._check_json(child / "sessions/review-01/session.json")
    assert session["completed"] is True
    assert session["lineage_review_number"] == 3 and session["review_cycle"] == 1
    context = delivery._check_json(Path(session["review_context"]))
    assert context["review_authorization"] == receipt["authorization"]
    assert delivery.review_budget_usage(child) == {"semantic_cycles": 3}
    assert len(list((child / "sessions").iterdir())) == 1


def test_racing_operator_processes_publish_one_slot_and_preserve_history(lineage):
    _root, _card, origin, _launches = lineage
    before = snapshot(origin)
    reason = "same explicit concurrent decision"
    preview = policy.review_allow(delivery, origin, reason=reason)
    context = multiprocessing.get_context("fork")
    start = context.Event()

    def contender(connection):
        start.wait(10)
        try:
            result = policy.review_allow(delivery, origin, reason=reason, authorize=preview["proposal_sha256"])
            connection.send(("authorized", result["authorization"]))
        except delivery.DeliveryError as exc:
            connection.send(("refused", str(exc)))
        finally:
            connection.close()

    pipes = [context.Pipe(duplex=False) for _ in range(2)]
    processes = [context.Process(target=contender, args=(send,)) for _receive, send in pipes]
    try:
        for process in processes:
            process.start()
        start.set()
        results = []
        for receive, _send in pipes:
            assert receive.poll(15), "synthetic concurrent operator did not finish"
            results.append(receive.recv())
        for process in processes:
            process.join(5)
            assert process.exitcode == 0
        allowed = [value for state, value in results if state == "authorized"]
        assert allowed and all(value == allowed[0] for value in allowed)
        assert all(state == "authorized" or "another delivery runner" in value for state, value in results)
        assert len(list((delivery.RUNTIME_ROOT / "review-authorizations" / origin.name).glob("*.json"))) == 1
        assert policy.allowance(delivery, origin)["operator_granted_slots"] == 1
        assert snapshot(origin) == before
    finally:
        for process in processes:
            if process.is_alive():
                process.kill()
            process.join(5)
        for pair in pipes:
            for connection in pair:
                connection.close()


def test_lost_authorize_response_reuses_the_published_record(lineage, monkeypatch):
    _root, _card, origin, _launches = lineage
    before = snapshot(origin)
    reason = "repair with durable one-slot decision"
    preview = policy.review_allow(delivery, origin, reason=reason)
    original_write = policy.retained._write

    def lost_response(path, value):
        original_write(path, value)
        raise OSError("fixture crash after durable record publication")

    with monkeypatch.context() as interrupted:
        interrupted.setattr(policy.retained, "_write", lost_response)
        with pytest.raises(OSError, match="after durable"):
            policy.review_allow(delivery, origin, reason=reason, authorize=preview["proposal_sha256"])
    receipt = policy.review_allow(delivery, origin, reason=reason, authorize=preview["proposal_sha256"])
    assert receipt["reused"] is True
    assert policy.allowance(delivery, origin)["operator_granted_slots"] == 1
    assert not (delivery.RUNTIME_ROOT / "runs" / receipt["proposal"]["successor_run_id"]).exists()
    assert snapshot(origin) == before
