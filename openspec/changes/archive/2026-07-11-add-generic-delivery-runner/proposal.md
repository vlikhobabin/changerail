## Why

OPSX имеет repo-scoped Codex launcher, но не имеет tracked generic runner для
повторяемого non-interactive delivery. Supervisor-ы вынуждены наблюдать процесс
через свободный текст, `pgrep` или локальные скрипты.

## What Changes

- Добавить public-safe runner helper для non-interactive OPSX delivery.
- Закрывать stdin child-процесса и поддерживать per-run `model` и
  `reasoning_effort` через штатные Codex CLI overrides.
- Атомарно писать runtime status/run record с card, phase, result, timestamps,
  commit при наличии, model/effort и базовой usage-информацией, если она
  доступна.
- Явно представлять terminal outcomes `DELIVERED`, `NO-GO` и `BLOCKED`.
- Описать preflight/runbook для launcher, auth/permissions, proxy connectivity,
  symlinks, binary lookup и диагностики по status record.

## Capabilities

### New Capabilities
- `opsx-delivery-runner`: generic non-interactive delivery runner, status/run
  record and operational preflight behavior.

### Modified Capabilities
- `opsx-contracts`: добавить публичный run record/status contract namespace.

## Impact

- new runner helper under `bin/` or `scripts/`
- new JSON schema for run records/status
- smoke tests for runner command construction, closed stdin and terminal status
- `docs/opsx-contracts.md`
- `docs/how-it-works.md`
- `AGENTS.shared.md`
