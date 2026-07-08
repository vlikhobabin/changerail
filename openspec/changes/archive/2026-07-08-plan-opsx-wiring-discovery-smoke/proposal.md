## Why

OPSX уже поставляет минимальный source surface для `opsx-explore` и `opsx-ff`,
но способ подключения этих skills/commands еще не закреплен как проверяемый
contract. Без discovery smoke легко получить wrappers, которые ссылаются на
несуществующие пути, или symlink-и, раскрывающие machine-local workspace.

## What Changes

- Добавить capability delta `opsx-wiring-discovery`.
- Зафиксировать expected wiring для consumer projects:
  `.claude/skills`, `.claude/commands/opsx`, `.codex/skills/opsx-*`.
- Зафиксировать repo-local dogfooding constraints для `/opt/opsx`.
- Определить smoke evidence для Claude command discovery и Codex skill
  discovery.
- Добавить `docs/wiring-discovery.md` и
  `scripts/smoke-wiring-discovery.py`.
- Добавить repo-local relative symlink-и для dogfooding discovery:
  `.claude/skills`, `.claude/commands/opsx`,
  `.codex/skills/opsx-explore`, `.codex/skills/opsx-ff`.
- Запускать repo-local и consumer-example smoke с JSON report в ignored
  runtime space.
- Не создавать local settings, secrets, machine-local links или tracked
  runtime state.

## Capabilities

### New Capabilities
- `opsx-wiring-discovery`: discovery and smoke contract for OPSX skill/command
  wiring.

### Modified Capabilities
- none

## Impact

- Affected files: `openspec/changes/plan-opsx-wiring-discovery-smoke/**`,
  board card, `docs/wiring-discovery.md`,
  `scripts/smoke-wiring-discovery.py`, `.claude/skills`,
  `.claude/commands/opsx`, `.codex/skills/opsx-explore`,
  `.codex/skills/opsx-ff`.
- Runtime report output stays under ignored `.runtime/`.
- Repo-local symlink-и are relative and stay inside `/opt/opsx`.
