# Зафиксировать integration boundary ускоренного release loop

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 03

## Source
- Published connected broker supervisor v5,
  `deliver-connected-broker-supervisor-v5`, commit
  `9872d4edd5c35eb51d64d1199000c029f11bd92d`.
- Historical private integration timings and terminal unpublished candidates are
  hypotheses only; their code, cards, verdicts, manifests, logs and evidence
  are not accepted or reused.

## Summary
Разделить следующую интеграционную волну на dormant bounded semantic scheduler,
отдельный affected release profile и финальную certification-карточку. Это
сохраняет опубликованный v5 как единственный supervisor primitive, не смешивает
execution authority с планированием и оставляет дорогие history/full измерения
только финальной сертификации.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Future protocol scope: only the two later exact authorizations may permit
  their bounded scheduler and affected-profile authority surfaces.
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`
- Published investigation authorization: `none`

## Depends On
- `deliver-connected-broker-supervisor-v5`

## Blocks
- `authorize-bounded-release-semantic-scheduler-v1`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v1`
- `implement-bounded-affected-release-profile-v1`
- `certify-accelerated-release-loop-v1`

## Acceptance
- The decision freezes exact scheduler and affected-profile authorization
  objects and their exact future two-field references.

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

- Scheduler v1 starts from its future published authorization HEAD, imports
  only published v5 as its child-supervision primitive, adds at most `499`
  production LOC and remains dormant outside focused tests.
- Scheduler owns bounded prevalidation, at most four concurrent semantic jobs,
  deterministic ordered aggregation, exact-once execution, fail-fast
  cancellation and bounded result/output handling. It does not own selection,
  runner/CI activation, receipts or publication authority.
- Affected profile v1 starts only after published scheduler v1, adds at most
  `499` production LOC and owns selector/registry resolution plus the sole
  runner activation of scheduler. It does not redefine supervisor or scheduler
  internals.
- Requested `affected` is always non-authoritative, including fail-closed full
  fallback. Unknown, ambiguous, self-authority, malformed or over-bound Git
  input selects full fallback; only requested `full-release` may become
  authoritative after exact successful completion.
- Canonical CI remains one explicit `full-release` entrypoint. Affected mode is
  developer feedback only and cannot satisfy review, publish, receipt or final
  certification gates.
- Final `certify-accelerated-release-loop-v1` starts only after both published
  implementations, changes no production code, runs one fresh critical
  pre-capture audit and then at most one reachable-history scan and one full
  release baseline with no retry. It measures affected docs, Python and unknown
  fallback scenarios against frozen correctness and authority assertions.
- Publication order is decision -> scheduler authorization -> scheduler
  implementation -> affected authorization -> affected implementation ->
  certification. No successor may be created early.
- This decision remains docs-only with production/test/runtime LOC `0`; it
  runs or accepts no history, full baseline, live matrix or prototype evidence.

## Change Set
- `decide-accelerated-release-loop-integration-boundary`

## Verify
- GREEN: FF strict target/all OpenSpec validation, exact
  object/reference/order/future-absence oracle, JSON/TOML parse, current public
  scan `1464/0` and whitespace check.
- GREEN: DO source classification, synchronized capability/all strict OpenSpec,
  archive/main exact-sync, production/test/runtime LOC `0`, manifest scope and
  normalized ordinary/high preflight.
- NOT RUN by contract: reachable history, full release baseline, live matrix
  and successor execution.

## Archive
- `openspec/changes/archive/2026-08-26-decide-accelerated-release-loop-integration-boundary/`

## Related
- `openspec/changes/decide-accelerated-release-loop-integration-boundary/`
- `openspec/board/4.done/deliver-connected-broker-supervisor-v5.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: one docs-only decision freezes disjoint scheduler,
affected-profile and certification boundaries. The synchronized change is
archived; no successor or executable payload was created.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-accelerated-release-loop-integration-boundary`

### Why
Опубликованный v5 закрывает безопасное владение child process tree, но не
определяет scheduler, affected selection, activation authority или финальный
measurement gate. Их объединение в одну implementation-карточку снова создало
бы широкий непроверяемый payload.

### Goal
Опубликовать одно docs-only решение с disjoint ownership, точной lineage и
последовательным verification path для ускоренного release loop.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact future objects, references, ownership, ordering, authority,
  certification and dormancy boundaries are machine-checkable.

### Depends On
- `deliver-connected-broker-supervisor-v5`

### Related
- `openspec/changes/decide-accelerated-release-loop-integration-boundary/`

## Log
- 2026-08-26 operator authorized the next separate integration decision after
  published connected broker supervisor v5.
- 2026-08-26 FF created one apply-ready same-slug change; strict target/all
  OpenSpec, exact lineage/order/absence, JSON/TOML, current public scan and
  whitespace checks passed. No history/full/live or successor work ran.
- 2026-08-26 DO synchronized six release-CI requirements, archived the
  same-slug change and retained production/test/runtime LOC `0`. No history,
  full baseline, live matrix, successor, review, commit or push ran.
- 2026-08-26T09:45:48Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
