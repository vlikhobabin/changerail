# Авторизовать bounded recovery-episodes payload

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
`report-recovery-aware-delivery-episodes`: ceiling 500 и только owner-generated
episode/attempt lineage плюс bounded metrics rollup.

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/report-recovery-aware-delivery-episodes.md","successor_id":"report-recovery-aware-delivery-episodes","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Exact source/path/ceiling валидны и reciprocal.
- Allowance покрывает owner lineage и derived metrics schemas, не raw-log
  reconstruction или prompts/tool payload retention.
- Runner production budget не выше 300, metrics budget не выше 200; aggregate
  exact payload остается не выше 500.
- Exact-chain/mismatch preflight evidence green; production delta source zero.

## Non-Goals
- Реализация episode/metrics behavior или authorization raw telemetry.

## Change Set
- `authorize-bounded-recovery-episodes-payload`

## Verify
- `bin/openspec validate authorize-bounded-recovery-episodes-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-recovery-episodes-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/report-recovery-aware-delivery-episodes.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-recovery-episodes-payload.md`.

## Change 1: `authorize-bounded-recovery-episodes-payload`

### Why
Episode/attempt schemas и owner linkage меняют wire contract.

### Goal
Опубликовать exact source с aggregate ceiling 500.

### Scope
- exact object/relations;
- runner 300 + metrics 200 boundary;
- exact/mismatch proof.

### Acceptance
- Source действует только для recovery-episodes successor.
- Raw logs и broader telemetry authority исключены.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-recovery-episodes-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
