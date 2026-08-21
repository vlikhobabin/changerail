# Авторизовать bounded live-progress payload

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
`expose-structured-live-delivery-progress`: ceiling 500 и только bounded
value-free progress event/status wire boundary.

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/expose-structured-live-delivery-progress.md","successor_id":"expose-structured-live-delivery-progress","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Object bound к exact investigation/successor path и ceiling 500.
- Allowance покрывает только bounded progress/heartbeat/status protocol.
- Raw logs, prose parsing и другой telemetry authority не authorizes.
- Exact-chain/mismatch preflight evidence green; production delta zero.

## Non-Goals
- Реализация progress protocol или authorization другой card.

## Change Set
- `authorize-bounded-live-progress-payload`

## Verify
- `bin/openspec validate authorize-bounded-live-progress-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-live-progress-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/expose-structured-live-delivery-progress.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-live-progress-payload.md`.

## Change 1: `authorize-bounded-live-progress-payload`

### Why
Новый progress wire contract требует exact source после investigation.

### Goal
Опубликовать bounded source без реализации telemetry behavior.

### Scope
- exact authorization object и reciprocal links;
- exact acceptance/mismatch preflight proof.

### Acceptance
- Только live-progress successor получает ceiling/protocol allowance.
- Source не меняет production code или global limits.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-live-progress-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
