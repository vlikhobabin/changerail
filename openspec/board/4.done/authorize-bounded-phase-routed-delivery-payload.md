# Авторизовать bounded phase-routed delivery payload

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
- Existing reciprocal contract сохраняется: authorization source Depends On
  investigation, investigation Blocks exact successor, а successor Depends On
  investigation и содержит точную ссылку на эту published authorization.
- Focused non-production smoke принимает exact phase-routed chain после
  перехода successor в `3.inprogress` и fail-closed отклоняет mismatched card
  id/path, investigation relation, ceiling и protocol flag в пределах этого
  existing reciprocal contract.
- Карточка не изменяет production runner, schemas или runtime behavior.

## Non-Goals
- Реализовывать phase-routed delivery fixes.
- Публиковать отклонённый payload `add-phase-routed-delivery-plan-execution`.
- Авторизовывать payload больше 500 production-counted LOC.
- Давать reusable authorization будущим runner protocol changes.

## Change Set
- `authorize-bounded-phase-routed-delivery-payload`

## Verify
- PASS — `bin/openspec validate authorize-bounded-phase-routed-delivery-payload --strict`
- PASS — `bin/openspec validate changerail-contracts --strict`
- PASS — `python3 scripts/smoke-review-preflight.py` (exact phase-routed
  acceptance under the existing reciprocal contract; id/path, source
  investigation relation, ceiling and protocol-flag fail-closed rejection)
- PASS — `bin/openspec validate --all --strict` before and after archive
- PASS — `python3 scripts/public-surface-scan.py` (0 findings)
- PASS — `python3 -m json.tool .mcp.json` and TOML parse of
  `.codex/config.toml`
- PASS — `git diff --check` and explicit `git diff --no-index --check` scan of
  OpenSpec artifacts before archive
- PASS — `bin/changerail-delivery-manifest scope-check <manifest> --workspace .
  --target working-tree --json` (no missing, extra or mismatched paths)
- PASS — `bin/changerail-review-verdict preflight
  openspec/board/3.inprogress/authorize-bounded-phase-routed-delivery-payload.md
  --workspace . --normalize ... --json` (`ready-for-llm-review`, production
  LOC `0`)

## Archive
- `openspec/changes/archive/2026-08-22-authorize-bounded-phase-routed-delivery-payload/`

## Related
- `openspec/board/4.done/investigate-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`

## Result
Delivery repair R1 сузил synchronized contract до уже enforced reciprocal
relations и добавил exact non-production phase-routed smoke coverage; repair
R2 обновил successor Related path. Production runner, schemas, CLI и runtime
behavior не менялись.
RED evidence неприменим: payload содержит только board/OpenSpec contract
artifacts и не меняет testable production behavior.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- Проверить existing reciprocal contract exact successor и fail-closed
  rejection несовпадающей цепочки.

### Acceptance
- Authorization object содержит только шесть обязательных полей и exact values
  из investigation decision.
- Existing reciprocal chain проходит deterministic preflight; изменения card
  id/path, investigation relation или bounded parameter отклоняются.
- Production delta равен нулю.

### Depends On
- `investigate-phase-routed-delivery-authorization-boundary`

### Related
- `openspec/changes/authorize-bounded-phase-routed-delivery-payload/`

## Log
- 2026-08-22T00:00:00Z created from the published phase-routed authorization
  boundary investigation.
- 2026-08-22T18:33:30Z `$changerail-ff` создал apply-ready proposal, design,
  `changerail-contracts` delta spec и tasks; successor reciprocal metadata уже
  была exact, поэтому blocked successor не изменялся.
- 2026-08-22T18:43:00Z `$changerail-do` синхронизировал contract requirement,
  выполнил deterministic verification и архивировал change; карточка остается
  в `3.inprogress` для независимого review.
- 2026-08-22T19:06:31Z fresh same-card repair attempt 1 after cycle-1 `NO-GO`:
  R1 narrowed the requirement to the existing enforced reciprocal contract and
  added exact non-production smoke coverage; R2 repaired the successor Related
  path. Card remains in `3.inprogress` for review cycle 2.
- 2026-08-22T20:11:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
