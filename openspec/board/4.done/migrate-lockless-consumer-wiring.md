# Добавить безопасную миграцию lockless consumer wiring

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `python3 -m py_compile bin/bootstrap-project bin/verify-project scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py scripts/smoke-windows-wiring-git-safety.py` - passed
- `python3 scripts/smoke-bootstrap-project.py` - passed, 23/23 checks
- `python3 scripts/smoke-verify-project.py` - passed, 60/60 checks
- `python3 scripts/smoke-windows-wiring-git-safety.py` - passed, 6/6 checks
- `./bin/openspec validate "adopt-lockless-consumer-wiring" --strict` - passed
- `./bin/openspec validate "changerail-project-bootstrap" --strict` - passed
- `./bin/openspec validate "changerail-project-templates" --strict` - passed
- `./bin/openspec validate "changerail-project-verification" --strict` - passed
- `./bin/openspec archive "adopt-lockless-consumer-wiring" --yes --skip-specs` - passed after already-synced duplicate guard aborted the plain archive without changes
- `./bin/openspec validate --all --strict` - passed, 26 items
- `git diff --check` - passed
- `python3 scripts/public-surface-scan.py` - passed, 1050 files scanned, 0 findings
- `python3 scripts/public-surface-scan.py --history` - passed, 1050 files scanned, 0 findings
- `python3 scripts/run-release-baseline.py` - passed, 36/36 steps; Windows matrix recorded live two-host smoke as not-run, so no live two-host coverage is claimed

## Archive
- `openspec/changes/archive/2026-08-19-adopt-lockless-consumer-wiring/`

## Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `schemas/changerail-consumer-lock.schema.json`
- `docs/consumer-adoption-runbook.md`
- `scripts/smoke-bootstrap-project.py`
- `openspec/changes/archive/2026-08-19-adopt-lockless-consumer-wiring/`

## Result
implemented, reviewed and finalized through ChangeRail scoped publish; exact
payload and published commit ledger is retained in the ignored delivery
manifest.

## Next
- done

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
- `openspec/changes/archive/2026-08-19-adopt-lockless-consumer-wiring/`

## Log
- 2026-08-18T17:39:30Z создана после fail-closed ответа refresh-wiring на
  корректно работающем, но созданном до consumer-lock legacy wiring.
- 2026-08-19T06:29:33Z decomposed by `$chrl-ff` into one OpenSpec change and
  moved to `2.todo`.
- 2026-08-19T10:49:06Z `$changerail-do` implemented lockless adoption,
  synced specs, archived `adopt-lockless-consumer-wiring` and prepared
  review handoff.
- 2026-08-19T11:16:10Z publish baseline found and corrected the generated-copy
  Windows Git-safety smoke expectation for lock-owned refresh; release
  baseline passed after correction.
- 2026-08-19T11:40:09Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
