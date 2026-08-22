# Авторизовать bounded source-profile payload

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
- GREEN: `bin/openspec validate authorize-bounded-source-profile-payload --strict`
  - passed before archive.
- GREEN: `bin/openspec validate changerail-contracts --strict` - passed after
  manual contract sync.
- GREEN: `python3 scripts/smoke-review-preflight.py` - `review preflight smoke:
  PASS`; exact source-profile authorization acceptance and mismatched-card
  rejection covered.
- GREEN: `bin/openspec archive authorize-bounded-source-profile-payload --yes --skip-specs`
  - passed after manual spec sync.
- GREEN: `bin/openspec validate --all --strict` - passed before archive, 34
  items.
- GREEN: `python3 scripts/public-surface-scan.py` - passed, 1202 files scanned,
  0 findings.
- GREEN: `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-08-21-authorize-bounded-source-profile-payload/`

## Related
- `openspec/changes/authorize-bounded-source-profile-payload/`
- `openspec/changes/archive/2026-08-21-authorize-bounded-source-profile-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/materialize-versioned-source-classification-profiles.md`
- `scripts/smoke-review-preflight.py`

## Result
Delivery завершен: exact source-profile authorization source сохранен, single
effective rules constraint synced, exact/mismatch preflight smoke покрывает
source-profile chain, production behavior не менялось и OpenSpec change
archived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- 2026-08-21T11:49:49Z `$chrl-ff` confirmed apply-ready artifacts and moved
  the card to `3.inprogress`.
- 2026-08-21T11:54:13Z `$chrl-do` synced `changerail-contracts`, added
  source-profile exact/mismatch preflight smoke coverage and archived
  `authorize-bounded-source-profile-payload`; production delta remains zero.
- 2026-08-21T12:31:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
