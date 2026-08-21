# Авторизовать bounded external-blocker resume payload

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
Опубликовать exact authorization для critical successor
`resume-retained-payload-after-external-blocker`: ceiling 500 и только
investigated dirty-resume/blocker/evidence wire boundary.

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/resume-retained-payload-after-external-blocker.md","successor_id":"resume-retained-payload-after-external-blocker","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Object bound к exact investigation/successor path и ceiling 500.
- Allowance покрывает closed blocker enum, scoped evidence и exact retained
  resume; generic dirty bypass, credential handling и target rebind исключены.
- Exact-chain/mismatch evidence green; production delta zero.

## Non-Goals
- Реализация resume или расширение credential/mutation authority.

## Change Set
- `authorize-bounded-external-blocker-resume-payload`

## Verify
- `bin/openspec validate authorize-bounded-external-blocker-resume-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-external-blocker-resume-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-external-blocker-resume-payload.md`.

## Change 1: `authorize-bounded-external-blocker-resume-payload`

### Why
Critical retained-payload launch authority требует exact published source.

### Goal
Опубликовать bounded source без реализации dirty resume.

### Scope
- exact authorization object/relations;
- exact acceptance and mismatch proof.

### Acceptance
- Только external-blocker resume successor получает allowance.
- Generic dirty/credential/target authority не разрешается.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-external-blocker-resume-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
