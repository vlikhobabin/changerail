# Реализовать connected broker supervisor v5

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R13-S5I

## Source
- Published decision `decide-connected-broker-supervisor-proof-boundary`,
  commit `a94bd4e2907a1c216e7456cf1a9da643d283b796`.
- Published authorization `authorize-bounded-connected-broker-supervisor-v5`,
  commit `888f2aaeb5a5b352474c100c63c68f1de612a7a1`.
- Terminal v4 findings R8/R9 are requirements only; no v4 code, card, verdict,
  history, manifest, logs or evidence are reused.

## Summary
Реализовать clean Linux broker/controller и доказать outer cleanup и pidfd
signaling через public `supervise` с эффективными source mutations.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization:
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}`
- Independent review: exactly one fresh `gpt-5.6-sol`/`high`
- Same-card repair/retry/rescue budget: `0/0/0`

## Depends On
- `decide-connected-broker-supervisor-proof-boundary`
- `authorize-bounded-connected-broker-supervisor-v5`

## Blocks
- downstream release-loop activation pending exact v5 publication and a later
  tracked refresh.

## Acceptance
- Implementation starts from exact authorization HEAD `888f2aa...`, adds no
  dependency and at most `499` production LOC.
- One Linux broker subprocess becomes subreaper before target launch; caller
  never scans caller-global children and broker owns only its target tree.
- Closed bounded protocol orders ready, started and one terminal report; EOF,
  malformed/duplicate/overflow/timeout/fatal loss fail closed.
- Recoverable faults clean exact broker descendants with TERM/KILL/reap and two
  empty scans; fatal parent path retains bounded same-group cleanup.
- R8 canonical test invokes public `supervise` for fatal/timeout cleanup and
  proves no survivor. Removing exact public `_stop_group(proc)` wiring in a
  disposable source copy makes the same scenario fail.
- R9 canonical test invokes public `supervise`, passes identity validation and
  observes `pidfd_send_signal` with no PID-only signal. Replacing it with
  `os.kill(pid, sig)` in a disposable copy makes the same scenario fail.
- Both mutations assert effective unique source changes; direct helper calls,
  pre-signal mismatch and no-op mutations cannot satisfy proof.
- Fresh bounded canonical/counterfactual evidence is retained. Full baseline,
  history scan, live matrix and downstream activation are not run or accepted.

## Change Set
- `deliver-connected-broker-supervisor-v5`

## Verify
- RED: focused test failed with `FileNotFoundError` before the production module
  existed.
- GREEN: focused canonical and effective R8/R9 mutation suite 6/6,
  py_compile/inventory, pinned Ruff, schema smoke, strict OpenSpec,
  classification, current public scan `1458/0`, JSON/TOML and whitespace.
- Production LOC `460/499`; no dependency; exact authorization and dormant
  baseline/CI wiring oracles pass.
- GREEN: eight retained mandatory evidence records validate; manifest scope and
  normalized ordinary/high preflight are `ready-for-llm-review`.

## Archive
- `openspec/changes/archive/2026-08-26-deliver-connected-broker-supervisor-v5/`

## Related
- `openspec/changes/deliver-connected-broker-supervisor-v5/`
- `openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md`
- `openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: clean v5 production and connected counterfactual proof are
synchronized and archived. Final retained evidence and manifest/preflight pass;
one fresh Sol/high review remains. Publication requires GO and permits no
repair.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `deliver-connected-broker-supervisor-v5`

### Why
The published v5 authorization permits one clean implementation attempt that
must close the two final connected-proof gaps without another repair cycle.

### Goal
Deliver one dormant bounded broker/controller and mutation-sensitive proof.

### Scope
- `scripts/changerail_release_child_broker.py`
- `tests/smoke-release-child-broker-v5.py`
- this card, same-slug OpenSpec artifacts, synchronized release-CI spec and
  archive metadata.

### Acceptance
- Exact authorization, `<=499` production LOC, broker/protocol/cleanup,
  public-path R8/R9 counterfactuals, evidence and dormancy pass.

### Depends On
- `decide-connected-broker-supervisor-proof-boundary`
- `authorize-bounded-connected-broker-supervisor-v5`

### Related
- `openspec/changes/deliver-connected-broker-supervisor-v5/`

## Log
- 2026-08-26 clean worktree created from exact published authorization HEAD;
  terminal v4 payload and runtime evidence were not read or imported.
- 2026-08-26 FF created one apply-ready same-slug change; strict target/all
  OpenSpec and whitespace passed. No implementation/history/full/live ran.
- 2026-08-26 DO captured RED for the missing module, then implemented the clean
  broker/controller. Focused public-`supervise` canonical and effective R8/R9
  mutation proof, py_compile and pinned Ruff passed; no history/full/live ran.
- 2026-08-26 DO synchronized two v5 requirements and archived the same-slug
  change. Focused/static/current verification passed at production LOC
  `460/499`; no dependency, activation, history/full/live/review/commit/push.
- 2026-08-26 final DO handoff retained eight mandatory command records;
  manifest scope and ordinary/high preflight passed with exact published
  authorization. No history/full/live/review/commit/push ran.
- 2026-08-26T08:50:20Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
