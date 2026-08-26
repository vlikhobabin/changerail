# Авторизовать bounded affected release profile v3

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 10

## Source
- Published decision `rescue-affected-release-profile-exact-target-proof-boundary`,
  commit `8772376bc3b3bbb5d9aa2dd96c5a47c9430a863d`.
- Published integration decision `decide-accelerated-release-loop-integration-boundary`.
- Published semantic scheduler v1 implementation.
- Published affected v2 authorization; its unpublished implementation successor
  is exhausted by the source decision and remains forensic-only.

## Summary
Авторизовать ровно один clean implementation successor для affected profile v3
в пределах exact target/proof boundary и `<=499` production LOC.

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
- `rescue-affected-release-profile-exact-target-proof-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v2`

## Blocks
- `implement-bounded-affected-release-profile-v3`

## Authorization
- Investigation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-target-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v3.md","successor_id":"implement-bounded-affected-release-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Authorization публикуется docs-only от exact decision HEAD `8772376…` и
  содержит ровно один six-field object выше без дополнительных полей/объектов.
- `Depends On` содержит ровно decision, integration decision, scheduler v1 и
  affected v2 authorization; `Blocks` содержит только exact v3 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md","authorization_id":"authorize-bounded-affected-release-profile-v3"}`,
  начинается от authorization-publishing HEAD и добавляет не более 499
  production LOC.
- Future implementation зависит ровно от четырех published predecessors выше
  плюс эту published authorization и блокирует только
  `certify-accelerated-release-loop-v1`.
- Authorization сохраняет exact 35→30 inventory, three-digit R/C grammar,
  closed target descriptor inventory, aggregate admission ordering, exact
  integer scheduler jobs/row tuples, full-only authority и four-step CI.
- Connected proof остается конечным и exhaustive для selector streams/bounds,
  target kinds/access/root, scheduler typed cross-fields/jobs и всех exact CI
  field/trigger/action/with/run/gating/indirect surfaces.
- Future v3 строится clean из published sources; terminal unpublished v2 code,
  cards, manifests, verdicts, logs и evidence запрещены.
- Authorization добавляет production/test/runtime LOC 0, не создает successor,
  code, dependency, schema, CI или runtime authority.
- History/full/affected benchmark/live/certification/prototype evidence не
  запускается и не принимается; требуется один fresh Sol/high review.

## Change Set
- `authorize-bounded-affected-release-profile-v3`

## Verify
- GREEN required: exact object/reference/dependencies/sole block/LOC, published
  decision reachability, successor absence, strict OpenSpec, JSON/TOML,
  classification, current public scan, archive/main sync, whitespace, manifest
  scope and preflight.
- Retained mandatory publication evidence:
  `.runtime/changerail/evidence/authorize-bounded-affected-release-profile-v3/index.json`
  binds exact source commit to the expected rescue branch.
- RED: not applicable; docs-only authorization adds no executable behavior.
- Prohibited: history, full baseline, affected benchmark, live matrix,
  successor creation/implementation, certification, commit or push before review.

## Archive
- `openspec/changes/archive/2026-08-26-authorize-bounded-affected-release-profile-v3/`

## Related
- `openspec/changes/authorize-bounded-affected-release-profile-v3/`
- `openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO complete: exact docs-only v3 authorization is synchronized and archived.
Successor and executable payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-affected-release-profile-v3`

### Why
Published rescue requires a separately reviewed and published authorization
before any v3 implementation card or executable work may exist.

### Goal
Publish one exact bounded authorization for the sole clean v3 implementation.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact source object, future reference, dependencies, sole block, trust
  boundary, LOC and dormancy contracts above are machine-checkable.

### Depends On
- `rescue-affected-release-profile-exact-target-proof-boundary`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v2`

### Related
- `openspec/changes/authorize-bounded-affected-release-profile-v3/`

## Log
- 2026-08-26 created in a clean worktree from exact published rescue HEAD;
  successor and unpublished v2 payload/evidence were not created or imported.
- 2026-08-26 FF produced one exact apply-ready docs-only authorization change.
- 2026-08-26 DO retained exact source publication evidence, synchronized
  release-CI, archived the change and prepared ordinary/high preflight.
- 2026-08-26T17:36:30Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
