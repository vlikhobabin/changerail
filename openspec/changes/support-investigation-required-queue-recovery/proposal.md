## Why

`resume-plan` умеет представлять linked recovery для `NO-GO` и
`fix_budget_exhausted`, но prior child с `investigation_required` остается
нерезюмируемым в queue flow. Downstream cards должны оставаться blocked, пока
исходный retained payload или явная replacement ветка не пройдет независимый
review и publish.

## What Changes

- Расширить queue status/recovery contract для prior child с
  `terminal_reason: investigation_required`.
- Разрешить только constrained same-workspace recovery, связанный с prior
  status и retained-payload identity.
- Сохранить fail-fast semantics: downstream cards не запускаются до успешной
  independent review/publish оригинального или replacement payload.
- Добавить synthetic smokes для successful recovery и fail-closed случаев:
  dirty state, stale authorization, wrong card, wrong workspace и fingerprint
  drift.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: queue `resume-plan` represents authorized
  `investigation_required` recovery without weakening downstream dependency
  gates.
- `changerail-contracts`: aggregate plan status schema captures retained
  recovery metadata and stable blocking reasons.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-plan-status.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- Queue runner smoke fixtures and adversarial recovery cases
