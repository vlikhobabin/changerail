# Авторизовать bounded isolated release case executor v2

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R9-I

## Source
- Published decision `rescue-private-release-loop-acceleration-publication-boundary`,
  commit `25c76e7b4ae60d87598077935f829f43a5808330`.

## Summary
Опубликовать единственный docs-only authorization source для будущего I
implementation: bounded isolated release case executor v2.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- `rescue-private-release-loop-acceleration-publication-boundary`

## Blocks
- `implement-bounded-isolated-release-case-executor-v2`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-isolated-release-case-executor-v2.md","successor_id":"implement-bounded-isolated-release-case-executor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Ровно один schema-valid six-field authorization object имеет exact published
  investigation и exact future successor path/id.
- Decision `Blocks`, authorization `Depends On`/`Blocks` и future successor
  `Depends On` образуют exact reciprocal lineage.
- Future successor создается только после publication этого authorization source
  в `4.done`; его `Published investigation authorization` содержит ровно
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-isolated-release-case-executor-v2.md","authorization_id":"authorize-bounded-isolated-release-case-executor-v2"}`.
- `production_loc_ceiling` равен `500`; будущая implementation ограничена
  `<=499` executable LOC относительно ее exact published authorization HEAD.
- Этот authorization payload не добавляет новую authority или wire protocol;
  `true` разрешает только future I scope и не разрешает credential, mutation,
  live или terminal authority.
- Payload имеет production/test/runtime/executable LOC `0`; future successor,
  production code, tests и runtime state отсутствуют.
- I владеет только isolated case schemas, jobs/order, hard output и timeout
  bounds, process containment, cleanup и parsed-CI ownership proof; registry
  selection, history parsing, receipts и terminal authority вне scope.

## Change Set
- `authorize-bounded-isolated-release-case-executor-v2`

## Verify
- Strict target/capability/all OpenSpec, exact authorization parser и reciprocal
  lineage, JSON/TOML/current public scan, classification, whitespace/scope,
  manifest и preflight.
- No history scan, full release baseline, live run, successor, review, commit
  or push.

## Archive
- `openspec/changes/archive/2026-08-25-authorize-bounded-isolated-release-case-executor-v2/`

## Related
- `openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md`
- `openspec/changes/archive/2026-08-25-authorize-bounded-isolated-release-case-executor-v2/`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: один docs-only authorization change синхронизирован в canonical
release-CI spec и archived. Exact source binding, reciprocal lineage, future
two-field reference, zero executable LOC и I-only ownership готовы к fresh
independent ordinary/high review; successor отсутствует.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-isolated-release-case-executor-v2`

### Why
Future I implementation needs a separately published bounded authorization
source rather than consuming the decision directly.

### Goal
Bind the exact published investigation to one future I successor.

### Scope
- Board/OpenSpec/release-CI relationship documentation only.
- Production/test/runtime/executable LOC: `0`.

### Acceptance
- Exact six fields, ceiling `500`, protocol allowance `true`.
- Exact reciprocal relations and future exact two-field source reference.
- Future implementation is `<=499` executable LOC versus its exact published
  authorization HEAD and owns only I scope.
- No successor, executable implementation, history scan or full baseline.

### Depends On
- `rescue-private-release-loop-acceleration-publication-boundary`

### Related
- `openspec/changes/archive/2026-08-25-authorize-bounded-isolated-release-case-executor-v2/`

## Log
- 2026-08-25 card created from exact published decision base `25c76e7b4ae60d87598077935f829f43a5808330`; successor remains absent.
- 2026-08-25 FF created exactly one same-slug proposal, design, release-CI
  delta and tasks set; strict target/all validation passed without successor,
  history scan, full-release, live run, review, commit or push.
- 2026-08-25 DO synchronized `changerail-release-ci`, archived the sole
  docs-only change and prepared an ordinary/high preflight handoff. Exact
  authorization/lineage, JSON/TOML, current public scan, classification,
  whitespace and manifest scope are recorded in ignored runtime state; no
  successor, history/full-release/live run, review, commit or push ran.
- 2026-08-25T19:19:07Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
