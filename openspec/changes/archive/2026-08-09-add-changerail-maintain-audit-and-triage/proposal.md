## Why

Maintenance scan/report/card helpers уже дают deterministic input, но agents
нуждаются в отдельном workflow surface, который безопасно объясняет findings и
проводит triage без неявного перехода к delivery, publish или fix. Без
`changerail-maintain` оператору приходится вызывать низкоуровневый CLI и
самостоятельно удерживать read-only boundary.

## What Changes

- Добавить canonical Codex skill `changerail-maintain` и short alias
  `chrl-maintain`.
- Добавить Claude wrapper `/changerail:maintain` и short alias `/chrl:maintain`.
- Определить agent-facing modes `audit` и `triage`.
- Зафиксировать, что `audit` только запускает/читает deterministic scan/report
  output и не меняет tracked files, baseline, board, runtime state или external
  systems.
- Зафиксировать, что `triage` пишет только schema-valid ignored annotations и
  card previews, а tracked card write требует отдельного explicit
  `--write-cards` operator intent.
- Явно отложить mutation/fix mode до отдельной карточки `060-06`.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-skill-surface`: добавить maintain skill/alias/wrapper discovery,
  modes и mutation boundary.
- `changerail-repository-knowledge`: добавить agent workflow expectations для
  audit/triage поверх существующих maintenance report, triage и card-preview
  contracts.

## Impact

- `skills/`, `.codex/skills/` и `claude/commands/changerail/` получают новые
  maintain surfaces.
- `claude/commands/chrl/` получает short wrapper.
- Skill/wrapper validation и public-surface scan должны покрывать новый
  agent-facing surface.
- Existing delivery, review, publish и fix workflows не меняются.
