## Why

`investigation_required` останавливает delivery runner с сохраненным dirty
payload, но текущий status record не доказывает, что последующий resume видит
тот же самый payload. Без schema-backed identity оператор не может безопасно
отличить исходный retained review target от unrelated или измененной рабочей
директории.

## What Changes

- Добавить в `changerail.delivery-run.v1` bounded identity для retained payload
  при terminal outcome `BLOCKED` и reason `investigation_required`.
- Зафиксировать, какие значения входят в identity: card, workspace, prior
  status path, `HEAD`, tree SHA, diff fingerprint и целевой review state.
- Запретить использовать WIP commit, stash name, branch name или prose
  assertion как замену fingerprint proof.
- Сохранить public-safe contract: raw source, raw child logs и ignored runtime
  evidence не копируются в tracked artifacts.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: runner records retained-payload identity at an
  `investigation_required` safety stop.
- `changerail-contracts`: delivery-run status schema and fingerprint contracts
  describe the machine-verifiable retained-payload identity.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- Focused delivery-runner smoke fixtures for `investigation_required` stops
