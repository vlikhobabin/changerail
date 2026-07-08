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
- Не создавать symlink-и, scripts или local settings в этом planning change.

## Capabilities

### New Capabilities
- `opsx-wiring-discovery`: discovery and smoke contract for OPSX skill/command
  wiring.

### Modified Capabilities
- none

## Impact

- Affected files: `openspec/changes/plan-opsx-wiring-discovery-smoke/**`,
  board card and future docs/scripts to be implemented by the next delivery
  pass.
- No runtime state, local settings, symlinks or scripts are added by this
  planning change.
- The follow-up implementation can safely test wiring without private path
  leaks.
