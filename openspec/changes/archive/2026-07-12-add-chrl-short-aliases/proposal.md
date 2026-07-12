## Why

Ежедневные ChangeRail команды слишком длинные для частого ручного
использования. Нужен официальный короткий invocation surface, который не
заменяет canonical namespace и не дробит source-of-truth contracts.

## What Changes

- Добавить публичные короткие Codex aliases `$chrl-*` для существующих
  ChangeRail lifecycle skills.
- Добавить Claude command aliases `/chrl:*`, которые делегируют canonical
  `/changerail:*` wrappers.
- Обновить repo-local и generated consumer wiring так, чтобы новые проекты
  получали обе семьи aliases.
- Расширить `verify-project` и smoke checks fail-closed проверками short
  aliases.
- Обновить durable docs: `chrl-*` описывается как recommended daily shorthand,
  `changerail-*` остается canonical/reference form.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-skill-surface`: official short aliases for Codex skills and
  Claude command wrappers.
- `changerail-project-bootstrap`: generated consumer projects include both
  canonical and short alias wiring.
- `changerail-project-verification`: verification gate checks required short
  alias wiring.
- `changerail-wiring-discovery`: smoke/discovery contracts include short alias
  surfaces.
- `changerail-agent-methodology`: user-facing lifecycle guidance can recommend
  short daily aliases while preserving canonical names.

## Impact

- `skills/`, `.codex/skills/`, `claude/commands/`
- `templates/project/`, `bin/bootstrap-project`, `bin/verify-project`
- smoke scripts under `scripts/`
- public docs and OpenSpec specs under `docs/`, `AGENTS.shared.md` and
  `openspec/specs/`
