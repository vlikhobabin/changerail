# Авторизовать bounded verification-coverage payload

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
artifacts

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
- `bin/openspec validate authorize-bounded-verification-coverage-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-verification-coverage-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/define-verification-coverage-map.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-verification-coverage-payload.md`.

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
