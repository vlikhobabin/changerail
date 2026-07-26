## Why

Оператору нужен быстрый ответ, почему `preflight-plan` заблокировал queue run.
Сейчас actionable child failure может теряться внутри усеченного JSON, хотя
полная child status запись уже существует отдельно.

## What Changes

- Сделать aggregate output для child preflight failures компактным:
  card id, failing check name, `fail` и короткая причина.
- Сохранить ссылку на полную `changerail.delivery-run.v1` child status запись
  как runtime evidence.
- Не добавлять raw stdout/stderr logs или усеченные JSON blobs в aggregate
  status.
- Сохранить совместимость `status-plan --json` с текущей
  `changerail.delivery-plan-status.v1` schema.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: aggregate plan preflight/status выводит
  компактные child diagnostics без изменения wire schema.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
