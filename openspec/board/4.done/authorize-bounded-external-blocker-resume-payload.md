# Авторизовать bounded external-blocker resume payload

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
- GREEN: `bin/openspec validate authorize-bounded-external-blocker-resume-payload --strict`
  - passed; evidence id `openspec-validate-change`.
- GREEN: `bin/openspec validate changerail-contracts --strict` - passed;
  evidence id `openspec-validate-changerail-contracts-post-archive`.
- GREEN: `bin/openspec validate --all --strict` - passed; evidence id
  `openspec-validate-all-post-archive-cleanup`.
- GREEN: `python3 scripts/smoke-review-preflight.py` - passed; exact
  external-blocker authorization acceptance and mismatched-card rejection
  covered; evidence id `smoke-review-preflight`.
- GREEN: `python3 scripts/public-surface-scan.py` - passed; evidence id
  `public-surface-scan`.
- GREEN: `git diff --check` - passed; evidence id
  `git-diff-check-post-archive-cleanup`.
- GREEN: `bin/openspec archive authorize-bounded-external-blocker-resume-payload --yes`
  - passed; evidence id `openspec-archive-change`.

## Archive
- `openspec/changes/archive/2026-08-21-authorize-bounded-external-blocker-resume-payload/`

## Related
- `openspec/changes/archive/2026-08-21-authorize-bounded-external-blocker-resume-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/resume-retained-payload-after-external-blocker.md`

## Result
Delivery завершен: exact authorization object сохранен, reciprocal successor
reference добавлен, `changerail-contracts` synced, focused preflight proof
added, production behavior не менялось и OpenSpec change archived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- 2026-08-21T09:20:00Z fast-forward phase validated existing apply-ready
  artifacts and moved card to `3.inprogress`.
- 2026-08-21T10:31:01Z `$chrl-do` added exact external-blocker resume
  preflight smoke coverage, synced `changerail-contracts`, linked successor
  authorization and archived `authorize-bounded-external-blocker-resume-payload`.
- 2026-08-21T10:40:34Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
