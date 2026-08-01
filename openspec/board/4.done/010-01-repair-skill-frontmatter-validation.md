# Исправить YAML frontmatter ChangeRail skills

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `repair-skill-frontmatter-validation` (archived)

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
- `openspec validate "repair-skill-frontmatter-validation" --strict` passed.
- `git diff --check` passed for planning artifacts.
- `python3 - <<'PY' ...` YAML-parsed all `skills/*/SKILL.md`, checked parsed
  `name` values, and rejected the unquoted `: ` negative fixture:
  `YAML_FRONTMATTER_OK`.
- `python3 scripts/smoke-wiring-discovery.py` passed: `172/172` checks.
- `python3 scripts/run-release-baseline.py` passed: `25/25` release baseline
  steps.
- `openspec validate --all --strict` passed after archive: `13` specs, `0`
  failed.
- `git diff --check` passed after archive.

## Archive
- `openspec/changes/archive/2026-08-01-repair-skill-frontmatter-validation/`

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `openspec/changes/repair-skill-frontmatter-validation/`
- `skills/changerail-deliver/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-pub/SKILL.md`

## Result
Published reviewed payload as `64100218514e03b18963122282d15310f09f7893`;
push status `pending` on `main`/`origin`.

## Next
- done

## Log
- 2026-08-01T15:07:29Z карточка пересобрана из исходного bug report.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для bootstrap delivery.
- 2026-08-01T16:00:18Z `$chrl-deliver` выполнил `ff`: создан active change
  `repair-skill-frontmatter-validation`, apply-required artifacts готовы,
  planning checks passed.
- 2026-08-01T16:09:35Z `$chrl-deliver` выполнил `do`: исправлен skill
  frontmatter, усилен deterministic wiring smoke, обновлены specs/docs/release
  dependency, выполнен release baseline, change archived.
- 2026-08-01T16:19:57Z publish finalized card into `4.done` with commit `64100218514e03b18963122282d15310f09f7893` and push status `pending`.
