# Реализовать bounded release semantic scheduler v1

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 05

## Source
- Published decision `decide-accelerated-release-loop-integration-boundary`.
- Published authorization `authorize-bounded-release-semantic-scheduler-v1`,
  commit `ad6fa60cd641838cbef31059245e8cee9cbaa601`.

## Summary
Реализовать dormant scheduler для bounded parallel execution независимых
semantic tasks через опубликованный connected broker v5, не активируя его в
release runner, CI или authority surfaces.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `decide-accelerated-release-loop-integration-boundary`
- `authorize-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v1`

## Acceptance
- Implementation uses only the exact two-field authorization reference above,
  starts from published authorization HEAD and adds at most `499` production
  LOC.
- One dormant module imports only published connected broker v5, validates one
  immutable plan of 1..64 unique IDs/commands/timeouts/roots before launch and
  reserves every isolated root atomically before semantic work.
- `jobs` accepts integers 1..4; jobs 1 and default parallel execution produce
  identical exact-once deterministic registry-ordered results.
- Every task uses v5 `supervise`; child output remains capped at 8192 bytes,
  summary stays at most 64 KiB and contains no raw output.
- First terminal failure prevents unstarted tasks from launching; running tasks
  complete through v5 cleanup and every plan entry receives exactly one pass,
  fail or cancelled result.
- Malformed/duplicate/missing/unknown/over-bound inputs, root collisions,
  supervisor exceptions and malformed results fail closed without partial
  prelaunch execution or owned survivors.
- Connected focused proof covers validation, roots, jobs parity, exact once,
  ordered aggregation, failure cancellation, output/timeout/protocol failures
  and descendant cleanup.
- Repository-wide dormancy proof rejects imports or activation in baseline,
  CI, receipts, review/publish and other production entrypoints.
- No selector, semantic inventory, profile, runner/CI activation, receipt or
  publication authority is added; history/full/live work is not run.

## Change Set
- `implement-bounded-release-semantic-scheduler-v1`

## Verify
- GREEN: FF strict target/all OpenSpec, exact authorization/reference,
  published-base and future-successor absence checks, whitespace.
- RED: focused smoke initially failed with `ModuleNotFoundError` because the
  authorized scheduler module did not exist.
- GREEN: focused scheduler smoke covers validation/root bounds, exact 64 tasks,
  jobs 1/4 parity/order/exact-once, cancellation, injected faults and real v5
  normal/jobs4/output/timeout/protocol/descendant cleanup.
- GREEN: compile inventory, Python runtime, contract schemas `28`, release CI
  `49/49`, pinned Ruff, source classification, current public scan `1477/0`,
  JSON/TOML, strict OpenSpec and whitespace.
- Cycle-1 Sol/high review: `NO-GO`; R1 shared-event timing, R2 closed failure
  states, R3 executor lifecycle totality and R4 production spawn design required
  the sole same-card repair.
- GREEN after repair: jobs=4 queued-wrapper cancellation, closed malformed
  failure table, constructor/submit/wait/shutdown total results and explicit
  spawn-process/cross-process-event contract.
- Production LOC is remeasured by final preflight; structural activation paths
  remain `0`.
- NOT RUN by contract: reachable history, full release baseline, live matrix or
  affected successor.

## Archive
- `openspec/changes/archive/2026-08-26-implement-bounded-release-semantic-scheduler-v1/`

## Related
- `openspec/changes/implement-bounded-release-semantic-scheduler-v1/`
- `openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md`
- `scripts/changerail_release_child_broker.py`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: dormant bounded scheduler and connected proof are implemented,
synchronized and archived without production activation.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `implement-bounded-release-semantic-scheduler-v1`

### Why
Published authorization permits one dormant scheduler primitive before the
separate affected-profile activation can be authorized.

### Goal
Deliver bounded deterministic scheduler execution and connected proof without
production activation.

### Scope
- scheduler module under `scripts/`;
- focused scheduler smoke under `tests/`;
- this card, same-slug OpenSpec artifacts, synchronized release-CI spec,
  archive and necessary source-classification metadata only.

### Acceptance
- Exact authorization, LOC, execution, cancellation, result, root, dormancy and
  verification contracts pass.

### Depends On
- `decide-accelerated-release-loop-integration-boundary`
- `authorize-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/implement-bounded-release-semantic-scheduler-v1/`

## Log
- 2026-08-26 created from exact published scheduler authorization HEAD;
  affected authorization/successor absent and no prototype payload imported.
- 2026-08-26 FF created one apply-ready change; strict target/all, exact
  authorization/reference, scope and successor-absence checks passed.
- 2026-08-26 DO captured absent-module RED, implemented a 306-LOC dormant
  scheduler, passed focused/static/current gates, synchronized three release-CI
  requirements and archived the change. No history/full/live, affected
  successor, review, commit or push ran.
- 2026-08-26 cycle-1 fresh Sol/high review returned NO-GO with R1-R4. The sole
  same-card repair moved terminal-event publication inside workers, closed all
  broker failure cross-fields, totalized executor lifecycle faults and synced
  the actual spawn-process production design. Repair budget is exhausted;
  cycle-2 requires a fresh targeted Sol/high review.
- 2026-08-26T11:12:35Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
