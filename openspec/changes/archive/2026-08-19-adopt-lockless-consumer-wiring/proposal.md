## Why

Legacy ChangeRail consumer может иметь корректную wiring-поверхность, созданную
до появления `openspec/changerail-consumer-lock.json`. Сейчас
`bootstrap-project --configure-existing --refresh-wiring` правильно
останавливается на missing lock, но не дает оператору безопасного opt-in пути
для принятия существующей wiring, добавления новых helpers и создания
schema-valid lock.

## What Changes

- Добавить explicit existing-project migration/adoption mode для lockless
  consumers. Обычный `--refresh-wiring` остается fail-closed без opt-in.
- Требовать, чтобы dry-run и apply flows инвентаризировали только allowlisted
  ChangeRail-owned commands, skills и helper wrappers до записи lock.
- Принимать существующую wiring только когда все accepted artifacts указывают
  на один ChangeRail source root и один совместимый backend/path-mode policy.
- Блокировать adoption на dangling links, mixed roots, project-owned regular
  files, undeclared conflicts, unsupported Windows inference или unrelated dirty
  state без partial mutation.
- Создавать schema-valid wiring metadata и
  `openspec/changerail-consumer-lock.json` с source revision, profile evidence и
  выбранным enforcement только после доказанного ownership.
- Добавлять missing newly supported helper через тот же inferred owned wiring
  backend/path mode.
- Документировать migration и rollback в consumer adoption runbook.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: explicit lockless consumer adoption behavior
  для existing-project configuration.
- `changerail-project-verification`: verifier различает legacy lockless
  compatibility и adopted lock-backed wiring после migration.
- `changerail-project-templates`: generated/runbook guidance описывает
  existing consumer migration и rollback.

## Impact

- Affected code: `bin/bootstrap-project`, `bin/verify-project`.
- Affected docs/templates: `docs/consumer-adoption-runbook.md` и generated
  consumer guidance, где упоминается existing-project wiring configuration.
- Affected schemas: переиспользуются существующие
  `changerail.consumer-lock.v1` и generated wiring manifest schemas; новый
  schema id не планируется.
- Public-surface impact: migration examples должны оставаться generic и не
  должны сохранять private consumer paths, raw field-validation logs или
  credentials.
