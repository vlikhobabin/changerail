# Добавить безопасную миграцию lockless consumer wiring

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Field-validation consumer, подключенный до появления
  `openspec/changerail-consumer-lock.json`.
- `bin/bootstrap-project --configure-existing --refresh-wiring`
- `docs/consumer-adoption-runbook.md`

## Summary
Legacy consumer может иметь корректные ChangeRail symlinks, ignored local
Codex config и рабочие skills, но не иметь consumer lock. Текущий
`--configure-existing --refresh-wiring` fail-closed останавливается на missing
lock и не предлагает безопасного способа добавить новый обязательный helper.
Оператор вынужден создавать точечный symlink вручную, а дальнейшая проверка
wiring остается lockless compatibility path.

Нужен явный migration flow, который инвентаризирует существующую поверхность,
не переписывает project-owned files и создает проверяемый lock только после
подтверждения однозначного ChangeRail ownership.

## Acceptance
- `bootstrap-project` предоставляет explicit migration/adopt mode для
  существующего lockless consumer; обычный `--refresh-wiring` остается
  fail-closed без opt-in.
- Dry-run перечисляет только allowlisted ChangeRail-owned skills, commands и
  helper wrappers, которые будут сохранены, добавлены или отклонены.
- Existing correct symlinks на один ChangeRail root принимаются; dangling,
  mixed-root, regular-file и project-owned conflicts блокируют migration без
  частичных изменений.
- Migration не изменяет `AGENTS.md`, `.codex/config.toml`, `.mcp.json`, auth,
  application source, board cards или unrelated Git state.
- При успешной миграции создаются schema-valid wiring manifest/consumer lock с
  explicit source revision, profile inference/evidence и выбранным enforcement.
- Missing newly supported helper добавляется через тот же backend/path mode,
  что и доказанная существующая wiring surface.
- POSIX symlink и Windows generated-copy/junction policies имеют явное решение;
  неподдержанный inference блокируется с remediation.
- Smoke покрывает successful legacy adoption, mixed roots, missing helper,
  dirty unrelated file, regular-file conflict и idempotent second run.
- Consumer adoption runbook документирует migration и rollback.

## Non-Goals
- Автоматическое принятие произвольных `.codex` или `.claude` файлов как
  ChangeRail-owned.
- Перезапись project-specific instructions/config.
- Неявное повышение Codex authority profile.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `schemas/changerail-consumer-lock.schema.json`
- `docs/consumer-adoption-runbook.md`
- `scripts/smoke-bootstrap-project.py`

## Result
not started

## Next
- triage

## Log
- 2026-08-18T17:39:30Z создана после fail-closed ответа refresh-wiring на
  корректно работающем, но созданном до consumer-lock legacy wiring.
