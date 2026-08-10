## Why

Greenfield consumer CI сейчас собирается вручную и не имеет machine-readable
exact ChangeRail revision contract. Из-за этого локальный PASS не доказывает,
что clean clone воспроизводится в runner path.

## What Changes

- Добавить explicit bootstrap opt-in для generated consumer CI.
- Требовать strict `changerail.consumer-lock.v1` для CI generation/execution.
- Checkout-ить exact declared ChangeRail revision в disposable runner path.
- Запускать тот же consumer verification baseline без Codex credentials.
- Добавить schema-aware CI template smoke и clean-clone fixture.
- Документировать lock refresh и CI failure remediation.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: bootstrap может сгенерировать lock-driven
  consumer CI только по explicit opt-in.
- `changerail-project-templates`: template set получает public-safe CI workflow.
- `changerail-release-ci`: release baseline проверяет generated consumer CI
  contract и clean-clone fixture.

## Impact

Затрагиваются bootstrap CLI, templates, bootstrap/release smoke, CI docs и
consumer adoption runbook. Workflow не получает publish authority и не требует
consumer credentials для baseline verification.
