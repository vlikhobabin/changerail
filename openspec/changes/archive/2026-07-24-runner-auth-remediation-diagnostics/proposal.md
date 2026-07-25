## Why

Delivery runner preflight уже fail-closed при missing auth или stale symlinks,
но diagnostic должен сразу показывать следующий remediation step. Сейчас
оператору приходится выводить setup details из общего failure text.

## What Changes

- Улучшить `CODEX auth: fail` и stale `CODEX_HOME` symlink diagnostics.
- Направить сообщение к canonical consumer auth setup section.
- Сохранить fail-closed preflight behavior для missing auth и stale symlinks.
- Не раскрывать credential contents или unsafe machine-local secrets в status
  output.

## Capabilities

### New Capabilities

### Modified Capabilities
- `changerail-delivery-runner`: auth remediation diagnostics становятся
  actionable, сохраняя preflight failure semantics.

## Impact

- Затрагивает `bin/changerail-delivery-runner`, delivery runner docs и focused
  smoke coverage.
- Не меняет status schema.
