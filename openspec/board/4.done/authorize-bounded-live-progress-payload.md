# Авторизовать bounded live-progress payload

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
- `bin/openspec validate authorize-bounded-live-progress-payload --strict` -
  passed.
- `bin/openspec validate changerail-contracts --strict` - passed.
- `python3 scripts/smoke-review-preflight.py` - passed; exact
  live-progress authorization acceptance and mismatched-card rejection covered.
- `bin/openspec archive authorize-bounded-live-progress-payload --yes` -
  passed.
- `bin/openspec validate --all --strict` - passed, 38 items before archive.
- `python3 scripts/public-surface-scan.py` - passed, 1201 files scanned, 0
  findings.
- `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-08-21-authorize-bounded-live-progress-payload/`

## Related
- `openspec/changes/authorize-bounded-live-progress-payload/`
- `openspec/changes/archive/2026-08-21-authorize-bounded-live-progress-payload/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`
- `openspec/board/2.todo/expose-structured-live-delivery-progress.md`

## Result
published; bounded live-progress authorization source complete

Reviewed payload finalized through ChangeRail scoped publish; exact payload and
published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- 2026-08-21T09:16:00Z `$chrl-ff` confirmed apply-ready artifacts and moved
  the card to `3.inprogress`.
- 2026-08-21T09:48:54Z `$chrl-do` added exact live-progress preflight smoke
  coverage, synced `changerail-contracts` and archived
  `authorize-bounded-live-progress-payload`.
- 2026-08-21T10:19:51Z publish finalized card into `4.done`; exact ledger
  retained in ignored manifest.
