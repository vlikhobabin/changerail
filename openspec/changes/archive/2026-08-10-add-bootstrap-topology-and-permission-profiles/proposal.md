## Why

Greenfield bootstrap принимает `--kind`, но использует его только как label и
неявно генерирует максимальную Codex authority. Новый public consumer должен
получать observable topology/surface policy и безопасный interactive default,
не ломая существующий all-surfaces contract.

## What Changes

- Добавить project profiles `generic`, `workspace-root` и `service`.
- Добавить surface profiles `all-surfaces` и `codex-only`.
- Добавить Codex policies `safe-interactive` и `trusted-automation`.
- Сделать safe-interactive public default; полный доступ оставить explicit.
- Сохранить `--kind` как проверяемый compatibility alias и fail closed на
  неизвестные или конфликтующие combinations.
- Добавить profile matrix в bootstrap/verify smoke и синхронизировать docs.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: bootstrap начинает применять выбранные
  topology, surface и Codex authority profiles.
- `changerail-project-templates`: templates рендерят различимый profile policy
  и безопасный Codex default.
- `changerail-project-verification`: verifier проверяет declared profile и
  несовместимые/ослабляющие combinations.

## Impact

Затрагиваются `bin/bootstrap-project`, `bin/verify-project`, templates,
bootstrap/verify smoke, compatibility/adoption docs и generated consumer
configuration. Existing consumers без новых fields остаются на legacy
all-surfaces verification path.
