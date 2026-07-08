## Why

OPSX уже имеет shared methodology и собственную OpenSpec-доску, но еще не
поставляет reusable skills/commands как source of truth. Для bootstrap и
consumer symlink-модели нужен первый минимальный generic surface без
machine-local и domain-specific хвостов.

## What Changes

- Добавить `skills/opsx-explore/SKILL.md`.
- Добавить `skills/opsx-ff/SKILL.md`.
- Добавить Claude wrappers `claude/commands/opsx/explore.md` и
  `claude/commands/opsx/ff.md`.
- Обновить публичный статус в `README.md`, `AGENTS.md` и `CLAUDE.md`.
- Не добавлять repo-local `.claude`/`.codex` symlink wiring в этом change.

## Capabilities

### New Capabilities
- `opsx-skill-surface`: public, path-neutral generic OPSX skill and command
  source files.

### Modified Capabilities
- none

## Impact

- Affected files: `skills/opsx-explore/**`, `skills/opsx-ff/**`,
  `claude/commands/opsx/**`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
  `openspec/board/**`, `openspec/changes/add-minimal-opsx-skills/**`.
- No runtime state, secrets, local traces or machine-specific paths are added.
- Consumer projects can later symlink to these source files through bootstrap
  or adoption tooling.
