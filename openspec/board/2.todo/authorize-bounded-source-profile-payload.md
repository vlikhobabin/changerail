# Авторизовать bounded source-profile payload

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
`materialize-versioned-source-classification-profiles`: ceiling 500 и только
profile provenance/materialization/check protocol при одном effective rules
source.

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-bounded-field-validation-batch.md","investigation_id":"investigate-bounded-field-validation-batch","successor_card":"openspec/board/3.inprogress/materialize-versioned-source-classification-profiles.md","successor_id":"materialize-versioned-source-classification-profiles","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Object exact, reciprocal и ограничен ceiling 500.
- Allowance покрывает profile/check/provenance contract; existing
  `.changerail/source-classification.yaml` остается единственным effective
  rules input.
- Detection, materialization и drift report используют один canonical
  normalization path.
- Exact-chain/mismatch evidence green; source production delta zero.

## Non-Goals
- Реализация profiles или изменение global complexity limits.

## Change Set
- `authorize-bounded-source-profile-payload`

## Verify
- `bin/openspec validate authorize-bounded-source-profile-payload --strict`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/authorize-bounded-source-profile-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/materialize-versioned-source-classification-profiles.md`

## Result
Проработка завершена; apply-ready authorization artifacts созданы.

## Next
- Выполнить
  `$chrl-deliver openspec/board/2.todo/authorize-bounded-source-profile-payload.md`.

## Change 1: `authorize-bounded-source-profile-payload`

### Why
Profile/check contracts влияют на production complexity classification.

### Goal
Опубликовать exact bounded source без реализации profiles.

### Scope
- exact object/relations;
- effective-rules single-source constraint;
- exact/mismatch proof.

### Acceptance
- Только source-profile successor получает allowance/ceiling.
- Второй effective rules source не разрешается.

### Depends On
- `investigate-bounded-field-validation-batch`

### Related
- `openspec/changes/authorize-bounded-source-profile-payload/`

## Log
- 2026-08-21T09:04:00Z created from published bounded batch investigation.
