"""Installed recovery through actual CLI gates and a disposable Git publication.

Only the model launcher is replaced with controlled implementation/reviewer
sessions. Archive, checks, proof validation, accounting and publication are real.
The generic historical archive receives an explicit test-only compatibility
pin; genuine upstream pins are tested separately in test_installed_restoration.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import distribution as dist
import pytest

from scripts.changerail import local_delivery as d
from scripts.changerail import native_workflow as flow
from scripts.changerail import openspec_board as board
from scripts.changerail import openspec_context as native
from tools.changerail.tests.test_native_openspec_integration import project as project
from tools.changerail.tests.test_installed_restoration import admit_synthetic_payload

SOURCE = Path(__file__).resolve().parents[3]


def snapshot(run):
    return {
        p.relative_to(run).as_posix(): p.read_bytes()
        for p in run.rglob("*")
        if p.is_file()
    }


def observed_contract(run, card):
    selection = {
        "schema": "changerail.observed-proof-selection.v1",
        "root": d.repo_relative(run),
        "owner": {"run_id": run.name, "card": d.repo_relative(card)},
        "required_stages": ["implementation", "review", "final"],
    }
    path = run / "observed-proof-selection.json"
    d.write_json(path, selection)
    return {
        "schema": "changerail.observed-proof.v1",
        "required_stages": selection["required_stages"],
        "selection": {
            "path": d.repo_relative(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        },
    }


def _reference(path):
    data = path.read_bytes()
    return {
        "path": d.repo_relative(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _fragments(run):
    path = run / "observed-bytes.txt"
    data = b"before: return 1\naction: implement return 2\nafter: pytest confirms return 2\n"
    path.write_bytes(data)
    bounds = [
        0,
        data.index(b"\n") + 1,
        data.index(b"\n", data.index(b"\n") + 1) + 1,
        len(data),
    ]
    return {
        name: {
            **_reference(path),
            "start": bounds[index],
            "end": bounds[index + 1],
            "fragment_sha256": hashlib.sha256(
                data[bounds[index] : bounds[index + 1]]
            ).hexdigest(),
        }
        for index, name in enumerate(("before", "action", "after"))
    }


def inspect_behavior(root, card, run):
    row = d.derive_proof_inventory(card)["conditions"][0]
    fragments = _fragments(run)
    artifact = run / "inspection.json"
    d.write_json(
        artifact,
        {
            "schema": "changerail.inspection-observation.v1",
            "observer": "controlled implementation fixture",
            "role": "implementation",
            "observed_at": d.utc_now(),
            "condition": row["identity"],
            "inspected_sources": [_reference(root / "source.py")],
            "fragments": fragments,
            "conclusion": "The source returns 2 and retained real pytest checks assert that result.",
            "mocked_seams": ["model launcher only"],
            "residual_risks": ["disposable offline fixture"],
        },
    )
    proof = {
        "schema": "changerail.card-proof.v1",
        "run": {"run_id": run.name, "card": d.repo_relative(card)},
        "inventory_digest": d.derive_proof_inventory(card)["digest"],
        "payload": d.payload_fingerprint(),
        "condition": row["identity"],
        "method": row["method"],
        "stage": row["stage"],
        "observation_id": "implementation-C1",
        "recorder_role": "implementation",
        "kind": "inspection",
        "outcome": "pass",
        "artifact": _reference(artifact),
        "fragments": fragments,
    }
    return d.record_observed_proof(run, proof)


def retained_manifest(run, card, baseline):
    paths = d.changed_paths()
    value = {
        "schema": "changerail.delivery-manifest.v1",
        "run_id": run.name,
        "baseline_head": baseline,
        "card": {"id": card.stem, "path": d.repo_relative(card)},
        "paths": paths,
        "fingerprint": d.payload_fingerprint(paths),
        "path_fingerprints": d.path_fingerprints(paths),
        "path_states": {p: d._path_state(p) for p in paths},
    }
    d.write_json(run / "manifest.json", value)
    d.write_json(d.manifest_path(card.stem), value)
    return value


def test_installed_restore_public_cli_reaches_local_publication(
    project, tmp_path, monkeypatch, capsys
):
    root, card, _client = project
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    (root / ".gitignore").write_text(
        ".runtime/\n__pycache__/\n.pytest_cache/\ntools/openspec/node_modules/\n"
    )
    for column in ("4.done", "5.canceled"):
        location = root / "openspec/board" / column
        location.mkdir(parents=True)
        (location / ".gitkeep").write_text("")
    old_source = tmp_path / "old-source"
    config, payload = dist.source_payload(SOURCE)
    config["version"] = "2.0.0-candidate.5"
    payload["distribution.json"] = (dist.encoded(config), 0o644)
    for name, (data, mode) in payload.items():
        dist.write_atomic(old_source / name, data, mode)
    old_archive = tmp_path / "old.tar.gz"
    dist.build(old_source, old_archive)
    dist.install(root, old_archive)
    admit_synthetic_payload(monkeypatch, root)
    profile = (SOURCE / "tools/changerail/templates/profile.toml").read_text()
    command = (
        f"{sys.executable} -m pytest -p no:cacheprovider -v tests/test_behavior.py"
    )
    profile = profile.replace(
        'final_commands = ["python3 -m pytest -v", "./bin/openspec validate --specs --strict --no-interactive"]',
        "final_commands = "
        + json.dumps(
            [command, "./bin/openspec validate --specs --strict --no-interactive"]
        ),
    )
    dist.write_atomic(root / ".changerail/profile.toml", profile.encode())
    dist.write_atomic(root / "bin/codex", b"#!/bin/sh\nexit 99\n", 0o755)
    monkeypatch.setattr(d, "PROFILE_PATH", root / ".changerail/profile.toml")
    # Public --project initializes these paths at import; this in-process CLI
    # fixture performs the same binding without replacing any validation gate.
    for name, value in list(vars(d).items()):
        if (
            name.endswith("SCHEMA_PATH")
            and isinstance(value, Path)
            and value.is_relative_to(SOURCE)
        ):
            monkeypatch.setattr(d, name, root / value.relative_to(SOURCE))
    (root / "source.py").write_text("def value():\n    return 1\n")
    dist.write_atomic(
        root / "tests/test_behavior.py",
        b"from source import value\n\ndef test_value():\n    assert value() == 2\n",
    )
    assert d.main(["native-accept", str(card)]) == 0
    card = card.parent.parent / "2.todo" / card.name
    d.git("add", ".")
    d.git("commit", "-m", "accepted installed fixture")
    baseline = d.git("rev-parse", "HEAD").stdout.strip()
    remote = tmp_path / "remote.git"
    d.git("init", "--bare", str(remote))
    d.git("remote", "add", "origin", str(remote))
    d.git("push", "-u", "origin", "main")
    plan = d._check_json(d.RUNTIME_ROOT / "native-plans/example/native-plan.json")
    origin = d.RUNTIME_ROOT / "runs/original"
    origin.mkdir(parents=True)
    board.import_accepted(d, card, origin)
    target = card.parent.parent / "3.inprogress" / card.name
    target.parent.mkdir()
    card.rename(target)
    card = target
    card.write_text(d.replace_section(card.read_text(), "Status", ["3.inprogress"]))
    metadata = {
        "schema": "changerail.delivery-run.v2",
        "run_id": origin.name,
        "card": d.repo_relative(card),
        "execution_contract": "changerail.native.v1",
        "mode": "delivery",
        "lifecycle_mode": "openspec-v1",
        "started_at": d.utc_now(),
        "baseline_head": baseline,
        "change_plan": [{"number": n, "slug": slug} for n, slug in plan["groups"]],
        "process_identity": d.execution_identity(),
        "observed_proof_contract": observed_contract(origin, card),
    }
    d.write_json(origin / "run.json", metadata)
    tasks = root / "openspec/changes/example-change/tasks.md"
    (root / "source.py").write_text("def value():\n    return 2\n")
    with monkeypatch.context() as env:
        env.setenv("CHRL_RUN_DIR", str(origin))
        env.setenv("CHRL_SESSION_ROLE", "implementation")
        env.setenv("CHRL_DELIVERY_STAGE", "change")
        for n, _slug in plan["groups"]:
            env.setenv("CHRL_CHANGE_NUMBER", str(n))
            d.emit_event(f"change-{n}", "starting")
            tasks.write_text(tasks.read_text().replace(f"[ ] {n}.1", f"[x] {n}.1"))
            assert (
                d.run_evidence(
                    f"group-{n}",
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-p",
                        "no:cacheprovider",
                        "-v",
                        "tests/test_behavior.py",
                    ],
                )
                == 0
            )
            inspect_behavior(root, card, origin)
            d.emit_event(f"change-{n}", "complete")
    card.write_text(
        d.replace_section(
            card.read_text(), "Next", ["- accidentally changed accepted Next"]
        )
    )
    with pytest.raises(d.DeliveryError, match="plan changed"):
        native.require_plan(d, card, origin / "native-plan.json")
    old_identity = {
        key: value
        for key, value in metadata["process_identity"].items()
        if key != "scripts/__init__.py" and not key.startswith("tools/openspec/")
    }
    metadata.update(
        process_identity=old_identity,
        finished_at=d.utc_now(),
        exit_code=2,
        terminal_reason="accepted native OpenSpec plan changed; explicit replan required",
    )
    d.write_json(origin / "run.json", metadata)
    retained_manifest(origin, card, baseline)
    child = origin.with_name("failed-child")
    child.mkdir()
    events = d.read_phase_events(origin)
    child_meta = {
        **metadata,
        "run_id": child.name,
        "recovery_of": origin.name,
        "inherited_change_events": events,
        "observed_proof_contract": observed_contract(child, card),
    }
    d.write_json(child / "run.json", child_meta)
    d.write_json(
        child / "recovery-context.json",
        {"inherited_review_budget": {"semantic_cycles": 0}},
    )
    with pytest.raises(d.DeliveryError, match="plan changed"):
        board.import_accepted(d, card, child)
    assert not (child / "native-plan.json").exists()
    retained_manifest(child, card, baseline)
    history = {origin.name: snapshot(origin), child.name: snapshot(child)}
    archive = tmp_path / "target.tar.gz"
    dist.build(SOURCE, archive)
    capsys.readouterr()
    assert (
        d.main(
            [
                "plan-restore-prepare",
                str(child),
                "--runtime-archive",
                str(archive),
                "--reason",
                "restore exact accepted fixture Next",
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert (
        d.main(
            [
                "plan-restore-apply",
                str(child),
                "--proposal",
                report["proposal"],
                "--authorize",
                report["proposal_sha256"],
            ]
        )
        == 0
    )
    capsys.readouterr()
    allocations = []

    def controlled_session(**kwargs):
        role, run = kwargs["role"], kwargs["run_dir"]
        stage = kwargs.get("session_env", {}).get("CHRL_DELIVERY_STAGE")
        assert stage != "change", "completed groups must never be replayed"
        allocations.append((role, stage))
        session = run / "sessions" / f"controlled-{len(allocations)}"
        session.mkdir(parents=True)
        d.write_json(
            session / "session.json",
            {
                "role": role,
                "started_at": d.utc_now(),
                "finished_at": d.utc_now(),
                "completed": True,
                "returncode": 0,
                "stop_reason": "completed",
            },
        )
        (session / "events.jsonl").write_text(
            json.dumps(
                {
                    "observed_at": d.utc_now(),
                    "event": {
                        "type": "thread.started",
                        "thread_id": "controlled-independent-review"
                        if role == "review"
                        else f"controlled-implementation-{len(allocations)}",
                    },
                }
            )
            + "\n"
        )
        if kwargs.get("on_session_started"):
            kwargs["on_session_started"](session)
        with monkeypatch.context() as env:
            env.setenv("CHRL_SESSION_ROLE", role)
            env.setenv("CHRL_RUN_DIR", str(run))
            for key, value in kwargs.get("session_env", {}).items():
                env.setenv(key, value)
            if role == "implementation":
                with pytest.raises(d.DeliveryError, match="handoff"):
                    d.require_current_implementation_handoff(card, run)
                if stage == "finalize":
                    canonical = root / "openspec/specs/example/spec.md"
                    delta = (
                        root / "openspec/changes/example-change/specs/example/spec.md"
                    )
                    canonical.write_text(
                        canonical.read_text()
                        + "\n"
                        + delta.read_text().split("\n", 1)[1]
                    )
                    report_path = run / "sync-report.md"
                    report_path.write_text(
                        "Added Added behavior; preserved Preserve old behavior.\n"
                    )
                    flow.record_sync(d, card, run, report_path)
                card.write_text(
                    d.replace_section(
                        card.read_text(),
                        "Result",
                        [
                            "Implemented and checked deterministic fixture behavior; current evidence retained."
                        ],
                    )
                )
                card.write_text(
                    d.replace_section(
                        card.read_text(),
                        "Log",
                        [
                            "- Completed both task groups; refreshed evidence for the current payload."
                        ],
                    )
                )
                assert (
                    d.run_evidence(
                        f"fresh-{len(allocations)}",
                        [
                            sys.executable,
                            "-m",
                            "pytest",
                            "-p",
                            "no:cacheprovider",
                            "-v",
                            "tests/test_behavior.py",
                        ],
                    )
                    == 0
                )
                inspect_behavior(root, card, run)
                assert d.implementation_handoff(str(card)) == 0
            else:
                proofs = d.require_current_stage_proofs(card, run, ["implementation"])
                template = d.verdict_template(str(card))["template"]
                for decision in template["decisions"]:
                    decision["assessment"] = (
                        "The inspected implementation and real pytest receipt prove fixture behavior; only the model launcher is simulated."
                    )
                    for ref in decision["condition_refs"]:
                        ref["observation_ids"] = [
                            p["observation_id"]
                            for p in proofs
                            if p["condition"] == ref["condition"]
                        ]
                    decision["observation_ids"] = [
                        p["observation_id"]
                        for p in proofs
                        if p["condition"] in decision["conditions"]
                    ]
                d.write_json(d.verdict_path(card.stem), template)
                assert d.validate_verdict(str(card))["result"] == "go"
        return 0

    monkeypatch.setattr(d, "launch_codex", controlled_session)
    result = d.main(["resume", str(child)])
    captured = capsys.readouterr()
    assert result == 0, captured.out + captured.err
    assert allocations == [
        ("implementation", "finalize"),
        ("review", None),
        ("implementation", "archive-refresh"),
        ("review", None),
    ]
    assert history == {origin.name: snapshot(origin), child.name: snapshot(child)}
    assert not d.changed_paths()
    assert (root / "openspec/board/4.done/example.md").is_file()
    assert d.git("rev-parse", "HEAD").stdout.strip() != baseline
    assert d.git("rev-parse", "origin/main").stdout == d.git("rev-parse", "HEAD").stdout
    assert (
        d.git("--git-dir", str(remote), "rev-parse", "refs/heads/main").stdout
        == d.git("rev-parse", "HEAD").stdout
    )
    successor = next(
        p for p in (d.RUNTIME_ROOT / "runs").iterdir() if p not in (origin, child)
    )
    assert d.review_budget_usage(successor) == {"semantic_cycles": 1}
    assert d._check_json(successor / "publication.json")["state"] == "pushed"
    assert d._check_json(successor / "verification.json")["ok"] is True
    assert d._check_json(successor / "run.json")["recovery_of"] == child.name
