# Добавить безопасную миграцию lockless consumer wiring

## Status
2.todo

## Owner
ChangeRail

## OpenSpec Stage
artifacts

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
- `adopt-lockless-consumer-wiring`

## Verify
- `./bin/openspec validate "adopt-lockless-consumer-wiring" --strict`
- focused bootstrap and verify smoke commands for lockless adoption fixtures
- `./bin/openspec validate --all --strict`
- `git diff --check`
- `python3 scripts/public-surface-scan.py`

## Archive
- not started

## Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `schemas/changerail-consumer-lock.schema.json`
- `docs/consumer-adoption-runbook.md`
- `scripts/smoke-bootstrap-project.py`
- `openspec/changes/adopt-lockless-consumer-wiring/`

## Result
not started

## Next
- `$changerail-do openspec/board/2.todo/migrate-lockless-consumer-wiring.md`

## Change 1: `adopt-lockless-consumer-wiring`

### Why
Legacy consumers without `openspec/changerail-consumer-lock.json` need a safe
opt-in path from lockless compatibility to lock-owned refresh without treating
project-owned files as ChangeRail-owned.

### Goal
Add explicit lockless wiring adoption that inventories existing ChangeRail
surface, blocks ambiguous ownership, creates schema-valid lock/manifest data and
adds missing helpers through the inferred owned backend.

### Scope
- Extend `bin/bootstrap-project --configure-existing` with an explicit
  lockless adoption mode and dry-run inventory.
- Preserve normal `--refresh-wiring` fail-closed behavior when no consumer lock
  exists.
- Update `bin/verify-project` diagnostics for lockless, adoptable, unsafe and
  adopted consumers.
- Add focused smoke fixtures for success, negative ownership gates, missing
  helper addition and idempotency.
- Update consumer adoption migration and rollback docs.

### Acceptance
- Plain `--refresh-wiring` without consumer lock still stops before mutation and
  points to explicit adoption.
- Dry-run reports keep/add/reject decisions for allowlisted ChangeRail-owned
  wiring only.
- Adoption writes schema-valid lock/manifest only after single-root ownership,
  backend/path mode and clean source revision are proven.
- Dangling, mixed-root, regular-file, project-owned, unsupported Windows and
  dirty unrelated states block without partial mutation.
- Successful adoption can be verified as lock-backed and a second adoption run
  is idempotent.

### Depends On
- none

### Related
- `openspec/changes/adopt-lockless-consumer-wiring/`

## Log
- 2026-08-18T17:39:30Z создана после fail-closed ответа refresh-wiring на
  корректно работающем, но созданном до consumer-lock legacy wiring.
- 2026-08-19T06:29:33Z decomposed by `$chrl-ff` into one OpenSpec change and
  moved to `2.todo`.
