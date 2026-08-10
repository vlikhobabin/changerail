## Why

После initial bootstrap auth setup, POSIX repair, README и Git handoff требуют
ручных команд, а повторный bootstrap небезопасен для project-owned content.
Нужен bounded idempotent configure surface без скрытой публикации.

## What Changes

- Добавить explicit existing-project configure mode.
- Разрешить auth-only setup и manifest-owned POSIX wiring repair без
  перегенерации project-owned templates.
- Сделать auth remediation self-contained и не печатать credential contents.
- Добавить optional generated README для empty consumer.
- Добавить optional `git init`, default branch и remote setup.
- Запретить commit, push, PR/publish и external mutation.
- Добавить idempotency, dirty-state, credential-redaction и Git no-publish
  fixtures.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: helper получает bounded configure и explicit
  README/Git initialization modes.
- `changerail-project-templates`: минимальный consumer README становится
  opt-in generated artifact.
- `changerail-project-verification`: auth/wiring diagnostics дают executable
  remediation и различают project-owned conflicts.

## Impact

Затрагиваются bootstrap/verify helpers, README template routing, smoke fixtures
и adoption/migration docs. Existing default bootstrap по-прежнему не создает
auth marker, Git commit или remote без explicit flags.
