## Why

Maintainers сейчас должны вручную собирать локальный release baseline из
нескольких docs и CI steps. Это легко рассинхронизируется с workflow и делает
перед-release проверку менее воспроизводимой, чем сам CI gate.

## What Changes

- Добавить одну documented local command/script, которая запускает полный
  обязательный release baseline и возвращает non-zero при любом failure.
- Согласовать локальный baseline с tracked CI inventory: OpenSpec validation,
  config parsing, schema validation, lint, syntax compile, smoke checks,
  generated drift fixture, public-surface scans и whitespace checks.
- Задокументировать, что `scripts/smoke-drift.py` остается inventory-driven
  command, а локальный baseline вызывает его через generated public-safe
  fixture.
- Включить baseline command в release docs and card verification evidence.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-release-ci`: release verification must expose a single local
  command that reproduces the mandatory CI baseline.
- `changerail-release-discipline`: release docs must describe the local release
  baseline and drift fixture behavior.

## Impact

- New or updated release baseline script under `scripts/` or `bin/`
- `.github/workflows/changerail-ci.yml`
- `scripts/smoke-release-ci.py`
- `docs/release-discipline.md`
- `README.md`
- `AGENTS.md`
