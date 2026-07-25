## Why

Codex auth setup является install-time contract, который проходит через docs,
bootstrap, verification и runner preflight. Focused smoke coverage должен
ловить regressions без чтения или печати real credential contents.

## What Changes

- Расширить generic smoke coverage для project-local auth marker readiness.
- Покрыть explicit `CODEX_HOME`, missing auth и stale symlink diagnostics.
- Покрыть bootstrap opt-in auth link и verification advisory behavior.
- Держать все generated credentials fake, empty или temporary под ignored
  runtime space.

## Capabilities

### New Capabilities

### Modified Capabilities
- `changerail-release-ci`: release baseline включает focused smoke coverage для
  consumer auth setup contract.

## Impact

- Затрагивает smoke scripts и release baseline expectations.
- Не добавляет real secrets, runtime logs или machine-local auth state в
  tracked payload.
