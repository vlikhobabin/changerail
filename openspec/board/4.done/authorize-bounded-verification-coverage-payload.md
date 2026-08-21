# Авторизовать bounded verification-coverage payload

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- `investigate-bounded-field-validation-batch`

## Summary
Опубликовать exact authorization для successor
`define-verification-coverage-map`: ceiling 500 и только five-field map,
derived ledger и verification-admission protocol.

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
- `investigate-bounded-field-validation-batch`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/define-verification-coverage-map.md","successor_id":"define-verification-coverage-map","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Object exact, reciprocal и ограничен ceiling 500.
- Allowance покрывает five-field project map, references и derived ledger;
  acceptance/tasks/evidence не копируются во второй source of truth.
- Один canonical loader используется planning/delivery/verify/review.
- Exact-chain/mismatch evidence green; authorization source production delta
  zero.

## Non-Goals
- Реализация coverage map или global mandatory check catalog.

## Change Set
- `authorize-bounded-verification-coverage-payload`

## Verify
- GREEN: `bin/openspec validate authorize-bounded-verification-coverage-payload --strict`
  - passed before archive.
- GREEN: `bin/openspec validate changerail-contracts --strict` - passed after
  manual contract sync.
- GREEN: `bin/openspec validate --all --strict` - passed after archive, 34
  items.
- GREEN: `python3 scripts/smoke-review-preflight.py` - `review preflight smoke:
  PASS`.
- GREEN: `python3 scripts/public-surface-scan.py` - passed, 1201 files scanned,
  0 findings.
- GREEN: `bin/changerail-delivery-manifest scope-check .runtime/changerail/delivery-manifests/authorize-bounded-verification-coverage-payload.json --target working-tree --json`
  - passed, no missing/extra/mismatched paths.
- GREEN: `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-08-21-authorize-bounded-verification-coverage-payload/`

## Related
- `openspec/changes/archive/2026-08-21-authorize-bounded-verification-coverage-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/define-verification-coverage-map.md`
- `scripts/smoke-review-preflight.py`

## Result
Delivery завершен: exact authorization object сохранен, reciprocal successor
reference добавлен, `changerail-contracts` synced, coverage-specific
exact/mismatch preflight smoke добавлен, production behavior не менялось и
OpenSpec change archived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-verification-coverage-payload`

### Why
Coverage ledger меняет deterministic admission protocol.

### Goal
Опубликовать exact bounded source без реализации checks.

### Scope
- exact object/relations;
- single-loader and no-duplication constraints;
- exact/mismatch proof.

### Acceptance
- Только coverage successor получает protocol allowance/ceiling.
- Global catalog и второй acceptance source не разрешаются.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-verification-coverage-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
- 2026-08-21T11:06:12Z delivery started; exact authorization source moved to
  `3.inprogress` for verification, archive and review.
- 2026-08-21T11:11:15Z contract synced, coverage exact/mismatch smoke added,
  change archived and delivery verification passed; production delta remains
  zero.
- 2026-08-21T11:40:54Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
