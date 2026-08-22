# Авторизовать bounded phase-routed delivery payload

## Status
2.todo

## Owner
unassigned

## OpenSpec Stage
not-started

## Series
- none

## Series Index
- none

## Source
- `investigate-phase-routed-delivery-authorization-boundary`

## Summary
Опубликовать machine-readable authorization для exact successor
`implement-phase-routed-delivery-authorization-boundary`. Authorization
разрешает только принятую investigation границу aggregate/child
authority/status protocol, ограничивает production payload 500 добавленными
строками и не меняет production behavior сама по себе.

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
- `investigate-phase-routed-delivery-authorization-boundary`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md","investigation_id":"investigate-phase-routed-delivery-authorization-boundary","successor_card":"openspec/board/3.inprogress/implement-phase-routed-delivery-authorization-boundary.md","successor_id":"implement-phase-routed-delivery-authorization-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Completed `4.done` source содержит ровно один schema-valid authorization
  object, bound к published investigation и exact successor id/path.
- `production_loc_ceiling` равен 500, а protocol allowance относится только к
  принятой aggregate/child authority, resume и status boundary.
- Authorization не разрешает третий repair исходной карточки, другой successor,
  alternate aggregate runtime root или ослабление global review policy.
- Exact successor содержит reciprocal dependency и точную ссылку на эту
  published authorization.
- Focused deterministic preflight принимает exact chain после перехода
  successor в `3.inprogress` и отклоняет mismatched card id/path, investigation,
  ceiling и protocol flag.
- Карточка не изменяет production runner, schemas или runtime behavior.

## Non-Goals
- Реализовывать phase-routed delivery fixes.
- Публиковать отклонённый payload `add-phase-routed-delivery-plan-execution`.
- Авторизовывать payload больше 500 production-counted LOC.
- Давать reusable authorization будущим runner protocol changes.

## Change Set
- `authorize-bounded-phase-routed-delivery-payload`

## Verify
- `bin/openspec validate authorize-bounded-phase-routed-delivery-payload --strict`
- `bin/openspec validate changerail-contracts --strict`
- `python3 scripts/smoke-review-preflight.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- pending

## Related
- `openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`

## Result
pending

## Next
- Run `$changerail-ff` for this card.

## Change 1: `authorize-bounded-phase-routed-delivery-payload`

### Why
Published investigation выбирает новую authority/wire boundary, но сама не
является authorization source, которую deterministic preflight может принять
для exact successor.

### Goal
Опубликовать один bounded authorization object и deterministic proof exact
reciprocal chain без production behavior changes.

### Scope
- Зафиксировать exact investigation, successor, canonical paths, ceiling и
  protocol permission в authorization source.
- Синхронизировать reusable authorization contract только в объёме, нужном для
  этого exact source.
- Проверить acceptance exact successor и fail-closed rejection несовпадающей
  цепочки.

### Acceptance
- Authorization object содержит только шесть обязательных полей и exact values
  из investigation decision.
- Exact reciprocal chain проходит deterministic preflight; изменения любого
  связующего id/path или bounded parameter отклоняются.
- Production delta равен нулю.

### Depends On
- none

### Related
- `openspec/changes/authorize-bounded-phase-routed-delivery-payload/`

## Log
- 2026-08-22T00:00:00Z created from the published phase-routed authorization
  boundary investigation.
