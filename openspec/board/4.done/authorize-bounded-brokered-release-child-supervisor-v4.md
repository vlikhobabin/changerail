# Авторизовать bounded brokered release child supervisor v4

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S4A

## Source
- Published decision `decide-brokered-release-child-supervision-boundary`,
  commit `163db9b0d77e3c5ba3a348901f45a69f02a6bbc6`.

## Summary
Опубликовать единственный exact authorization source для будущего brokered v4
supervisor, сохранив clean start, `<=499` production LOC, bounded protocol,
ownership proof, one-repair review budget и полную dormancy до публикации v4.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Implementation: docs-only deterministic
- Independent review: one fresh `gpt-5.6-sol`/`high` pending
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `decide-brokered-release-child-supervision-boundary` (published
  `163db9b0d77e3c5ba3a348901f45a69f02a6bbc6`)

## Blocks
- `deliver-brokered-release-child-supervisor-v4`
- downstream release-loop activation remains blocked until exact v4
  publication and a later tracked refresh.

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- This authorization depends on the exact published decision and blocks only
  `deliver-brokered-release-child-supervisor-v4`; the decision blocks both.
- The future successor depends on both sources and uses only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}`.
- The successor starts from the exact HEAD that publishes this authorization,
  adds at most 499 production LOC and adds no external dependency beyond the
  already published psutil pin.
- Scope is closed to one broker/controller production module plus its existing
  runtime-selector entrypoint, focused tests and necessary source-classification
  metadata. It does not activate baseline, CI, receipt, review/publish or
  downstream work.
- Broker readiness before target launch, broker-only subreaper ownership,
  caller-global child-scan prohibition, bounded protocol, total cleanup,
  fatal-death honesty and the full decision proof matrix are mandatory.
- The successor gets one initial Sol/high review, at most one bounded same-card
  repair and one final Sol/high re-review; no third review/rescue/retry or
  terminal evidence reuse is permitted.
- The earlier v3 executable path remains exhausted. Published v3 sources are
  immutable history and cannot authorize implementation work.
- This payload adds production/test/runtime LOC `0`, creates no successor and
  runs no history, full baseline or live matrix.

## Change Set
- `authorize-bounded-brokered-release-child-supervisor-v4`

## Verify
- GREEN: strict target/all OpenSpec, exact object/order/lineage, successor
  absence, v3 exhaustion, dormancy and production LOC `0` oracles.
- GREEN: JSON/TOML, current public scan `1439/0`, source classification,
  tracked/untracked whitespace and diff check.
- GREEN: ignored manifest validation/scope and normalized ordinary/high
  preflight `ready-for-llm-review`; production/test/runtime LOC `0`.

## Archive
- `openspec/changes/archive/2026-08-26-authorize-bounded-brokered-release-child-supervisor-v4/`

## Related
- `openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: the same-slug authorization is synchronized and archived,
scope/preflight are green, and successor card/code remains absent. The payload
awaits one fresh review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-brokered-release-child-supervisor-v4`

### Why
The published broker decision defines the replacement boundary but is not the
six-field authorization source required by the future implementation.

### Goal
Publish the exact bounded v4 authorization without creating or activating its
successor.

### Scope
- This card, same-slug artifacts, synchronized release-CI spec and archive
  metadata only; production/test/runtime LOC `0`.

### Acceptance
- Exact object, reciprocal lineage, clean-start/LOC/proof/budget contract,
  v3 exhaustion, future-card absence and dormancy remain machine-checkable.

### Depends On
- `decide-brokered-release-child-supervision-boundary`

### Related
- `openspec/changes/authorize-bounded-brokered-release-child-supervisor-v4/`

## Log
- 2026-08-26 FF created one docs-only authorization from published decision
  `163db9b`; no successor, code, history/full/live evidence, review or push.
- 2026-08-26 DO validated exact authority, lineage, dormancy and public scope;
  no history, full baseline, live matrix, successor, review, commit or push.
- 2026-08-26 DO archived the same-slug change; ignored manifest scope and
  normalized ordinary/high preflight passed with production LOC `0`.
- 2026-08-26T06:55:58Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
