## Why

OPSX нужен reusable methodology artifact до bootstrap consumer projects, чтобы
не дублировать и не drift-ить agent instructions. Репозиторию также нужна
собственная OpenSpec-доска, чтобы dogfood-ить workflow, который он описывает.

## What Changes

- Добавить `AGENTS.shared.md` как generic OPSX methodology block для agents.
- Оставить root `AGENTS.md` как repo-specific public-safety и verification
  policy.
- Создать первую self-hosted OpenSpec board card и change для OPSX.
- Зафиксировать generated-section и drift expectations для будущего bootstrap и
  verify tooling.

## Capabilities

### New Capabilities
- `opsx-agent-methodology`: shared agent methodology для OPSX maintainers и
  bootstrapped consumer projects.

### Modified Capabilities
- none

## Impact

- Affected files: `AGENTS.shared.md`, root `AGENTS.md`, `openspec/board/**`,
  `openspec/changes/add-shared-agents-methodology/**`.
- Runtime, network, secret или machine-local state не добавляются.
- Будущие `templates/project` и `bin/verify-project` будут использовать shared
  methodology.
