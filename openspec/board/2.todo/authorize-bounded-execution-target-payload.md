# Авторизовать bounded execution-target payload

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
Опубликовать machine-readable authorization для exact bounded successor
`enforce-declared-execution-target-invariant`: ceiling 500 и только
target-identity project/delivery/evidence protocol boundary, принятую
investigation.

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/enforce-declared-execution-target-invariant.md","successor_id":"enforce-declared-execution-target-invariant","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Source содержит ровно один schema-valid object, bound к published
  investigation и exact successor id/path.
- Ceiling равен 500, protocol allowance относится только к optional
  target-identity contract и shared validator boundary.
- Source не меняет production code, global limits или provider authority.
- Deterministic preflight принимает exact chain и отклоняет mismatched card.

## Non-Goals
- Реализация target invariant.
- Authorization другого card или payload выше 500 LOC.

## Change Set
- `authorize-bounded-execution-target-payload`

## Verify
- `bin/openspec validate authorize-bounded-execution-target-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-execution-target-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/enforce-declared-execution-target-invariant.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-execution-target-payload.md`.

## Change 1: `authorize-bounded-execution-target-payload`

### Why
Investigation decision не является authorization source для protocol-bearing
successor.

### Goal
Опубликовать exact bounded source без production behavior changes.

### Scope
- authorization card/object;
- reciprocal relation update exact successor;
- focused preflight acceptance/mismatch proof.

### Acceptance
- Exact chain проходит, другая card/path отклоняется.
- Ceiling 500 и protocol allowance не расширяются.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-execution-target-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
