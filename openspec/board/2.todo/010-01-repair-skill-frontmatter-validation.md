# Исправить YAML frontmatter ChangeRail skills

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`010-core-release-contracts`

## Series Index
`01`

## Source
- Воспроизводимый Codex skill discovery failure от 2026-08-01.

## Summary
Исправить невалидные YAML `description` в `changerail-deliver`,
`changerail-do` и `changerail-pub` и добавить детерминированную проверку
frontmatter всех bundled skills в release baseline.

## Acceptance
- Все `skills/*/SKILL.md` имеют YAML-valid frontmatter.
- Canonical и alias skills загружаются без `Skipped loading` diagnostics.
- Release baseline парсит полный frontmatter, а не только извлекает `name`
  строковым разбором.
- Negative fixture доказывает, что unquoted scalar с `: ` отклоняется.
- Проверка не зависит от сетевого `codex exec` или наличия credentials.

## Scope
- `skills/*/SKILL.md` frontmatter.
- Wiring/skill discovery smoke и release baseline inventory.
- Contract/spec update для валидируемого skill metadata.

## Non-Goals
- Изменение поведения delivery phases.
- Массовое редактирование skill prose.

## Depends On
- none

## Implementation Notes
- Использовать настоящий YAML parser с pinned dependency или минимальный
  deterministic parser contract, который соответствует Codex loader behavior.
- Actual Codex discovery можно оставить дополнительным smoke, но не единственным
  CI gate.

## Change Set
- `repair-skill-frontmatter-validation` (planned)

## Change 1: `repair-skill-frontmatter-validation`

### Why
Текущие canonical ChangeRail skill frontmatter содержат YAML scalar с `: `,
из-за чего Codex может пропустить загрузку skill и сделать runner bootstrap
недетерминированным.

### Goal
Сделать skill metadata YAML-valid и добавить release gate, который проверяет
полный bundled skill frontmatter тем же классом парсинга, на который опирается
agent discovery.

### Scope
- `skills/*/SKILL.md` frontmatter для canonical ChangeRail skills.
- Детерминированный skill metadata smoke в release baseline.
- Contract/spec update для валидируемой skill metadata.

### Acceptance
- Все `skills/*/SKILL.md` имеют YAML-valid frontmatter.
- Canonical и alias skills загружаются без `Skipped loading` diagnostics.
- Release baseline парсит полный frontmatter, а не только извлекает `name`
  строковым разбором.
- Negative fixture доказывает, что unquoted scalar с `: ` отклоняется.
- Проверка не зависит от сетевого `codex exec` или наличия credentials.

### Depends On
- none

### Related
- `openspec/changes/repair-skill-frontmatter-validation/`

## Verify
- YAML parse всех `skills/*/SKILL.md`.
- `python3 scripts/smoke-wiring-discovery.py`.
- `python3 scripts/run-release-baseline.py`.
- `git diff --check`.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `skills/changerail-deliver/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-pub/SKILL.md`

## Result
not started

## Next
- Bootstrap delivery: `$chrl-deliver openspec/board/2.todo/010-01-repair-skill-frontmatter-validation.md`

## Log
- 2026-08-01T15:07:29Z карточка пересобрана из исходного bug report.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для bootstrap delivery.
