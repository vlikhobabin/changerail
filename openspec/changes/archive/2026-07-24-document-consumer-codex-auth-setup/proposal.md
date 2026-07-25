## Why

Consumer setup сейчас может выглядеть завершенным после bootstrap и
`verify-project`, но delivery-plan automation падает на первом runner preflight,
если нет effective Codex auth. Оператору нужен один canonical public-safe путь
настройки до unattended delivery runner use.

## What Changes

- Документировать Codex auth prerequisite для
  `changerail-delivery-runner run`, `preflight-plan`, `run-plan` и
  `resume-plan`.
- Объяснить effective `CODEX_HOME`, поддерживаемые project-local auth marker и
  auth environment variable формы.
- Добавить безопасные remediation examples только с `/opt/example-project` и
  `$HOME`.
- Зафиксировать, что `.codex/auth.json` является ignored local state и
  credentials нельзя копировать или коммитить по умолчанию.

## Capabilities

### New Capabilities

### Modified Capabilities
- `changerail-delivery-runner`: consumer-facing docs описывают auth readiness
  для runner commands.
- `changerail-project-bootstrap`: bootstrap guidance описывает безопасный
  handoff для ignored local Codex auth state.

## Impact

- Затрагивает public docs и consumer adoption guidance.
- Не копирует credentials, не добавляет tracked auth files и не меняет default
  bootstrap behavior.
