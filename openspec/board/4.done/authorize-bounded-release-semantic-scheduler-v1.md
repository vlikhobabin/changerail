# Авторизовать bounded release semantic scheduler v1

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 04

## Source
- Published integration decision
  `decide-accelerated-release-loop-integration-boundary`, commit
  `0de81cf7e578335c728466b81c1c60b6d447dab7`.

## Summary
Опубликовать ровно одну docs-only authorization для dormant bounded semantic
scheduler v1 поверх опубликованного connected broker supervisor v5, не создавая
successor или production activation.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `decide-accelerated-release-loop-integration-boundary`

## Blocks
- `implement-bounded-release-semantic-scheduler-v1`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- The card contains exactly one ordered six-field object equal to the published
  decision and blocks only exact scheduler v1.
- Future implementation depends on the published decision and this
  authorization and uses only:
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}`
- Scheduler starts from the future published authorization HEAD, adds at most
  `499` production LOC and imports only published connected broker v5.
- It prevalidates 1..64 unique tasks and roots before launch, accepts jobs 1..4,
  executes each task exactly once, cancels outstanding work on terminal failure
  and emits one deterministic ordered bounded result per task.
- Each child retains v5's 8192-byte output cap; summary is at most 64 KiB and
  contains no raw output. Malformed, duplicate, missing, unknown, over-bound or
  incomplete state fails closed.
- Scheduler owns no selector, semantic inventory, release profile, runner/CI
  activation, receipt or publication authority and remains dormant outside
  focused tests.
- Successor card/code remain absent; authorization changes docs only, adds
  production/test/runtime LOC `0` and runs no history/full/live work.

## Change Set
- `authorize-bounded-release-semantic-scheduler-v1`

## Verify
- GREEN: FF strict target/all OpenSpec, exact object/reference/decision equality,
  sole-block/successor-absence, JSON/TOML, classification, current public scan
  `1470/0` and whitespace checks.
- GREEN: DO synchronized capability/all strict OpenSpec, exact archive/main
  sync, production/test/runtime LOC `0`, manifest scope and normalized
  ordinary/high preflight.
- NOT RUN by contract: reachable history, full release baseline, live matrix or
  successor execution.

## Archive
- `openspec/changes/archive/2026-08-26-authorize-bounded-release-semantic-scheduler-v1/`

## Related
- `openspec/changes/authorize-bounded-release-semantic-scheduler-v1/`
- `openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md`
- `openspec/board/4.done/deliver-connected-broker-supervisor-v5.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: exact scheduler authorization is synchronized and archived;
successor and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-release-semantic-scheduler-v1`

### Why
Published integration decision requires a separate exact authorization before
the scheduler successor can be created.

### Goal
Publish one bounded docs-only scheduler authorization without creating or
activating scheduler code.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source, object, reference, LOC, scheduler bounds, dormancy and review
  contracts pass while successor stays absent.

### Depends On
- `decide-accelerated-release-loop-integration-boundary`

### Related
- `openspec/changes/authorize-bounded-release-semantic-scheduler-v1/`

## Log
- 2026-08-26 created from exact published integration-decision HEAD; successor
  absent and no executable or runtime evidence imported.
- 2026-08-26 FF created one apply-ready same-slug change; strict target/all,
  exact object/reference/decision equality, JSON/TOML, classification, current
  public scan and whitespace checks passed. No history/full/live work ran.
- 2026-08-26 DO synchronized three release-CI requirements, archived the
  same-slug change and retained production/test/runtime LOC `0`. No history,
  full baseline, live matrix, successor, review, commit or push ran.
- 2026-08-26T10:05:32Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
