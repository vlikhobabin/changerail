# Закрыть пробелы release gate и drift публичной документации

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Комплексное ревью кода, документации и public-safety controls ChangeRail от
  2026-07-12.
- `.github/workflows/changerail-ci.yml`
- `docs/release-discipline.md`
- `CHANGELOG.md`

## Summary
Привести release CI и публичную документацию в соответствие с фактической
исполняемой поверхностью ChangeRail. Каждый tracked helper, schema и smoke test
должен находиться под понятным автоматическим gate, а README, repository
instructions, changelog и compatibility/migration docs должны описывать уже
реализованный продукт без устаревших planned-status утверждений.

Текущий CI успешно проверяет OpenSpec, bootstrap, wiring, verify, manifest и
drift fixture, но не компилирует и не запускает часть новых runner, metrics и
fingerprint surfaces. JSON step не проверяет все schemas, lint gate отсутствует,
поэтому два unused imports уже остаются незамеченными. Одновременно `AGENTS.md`
считает templates/bootstrap/scripts planned surface, README называет
runner/metrics следующим направлением, а `CHANGELOG.md` не перечисляет ряд
существенных Unreleased возможностей.

## Findings
- CI syntax list не включает `bin/changerail-delivery-runner`,
  `bin/changerail-delivery-metrics`, часть smoke scripts и все executable Python
  files как автоматически обнаруживаемую поверхность.
- CI не запускает `smoke-delivery-runner.py`, `smoke-delivery-metrics.py` и
  `smoke-review-fingerprint.py`.
- JSON/config baseline не выполняет schema meta-validation и fixture validation
  для всех пяти ChangeRail schemas.
- `ruff check bin scripts` находит unused imports в
  `scripts/smoke-delivery-runner.py` и `scripts/smoke-drift.py`, но lint не входит
  в release gate.
- `scripts/smoke-drift.py` является inventory-driven command и без `--config`,
  `--workspace-root` или `--project` закономерно завершается fail; документация и
  naming должны исключать ожидание самодостаточного no-argument smoke.
- `AGENTS.md`, `README.md` и `CHANGELOG.md` отстают от tracked runner, metrics,
  review history, manifest derivation, public scan и finalization surface.
- В репозитории нет единой локальной команды, которая воспроизводит полный CI
  baseline без ручного выбора измененной поверхности.

## Acceptance
- CI автоматически компилирует или импортирует каждый tracked Python helper и
  smoke script под `bin/` и `scripts/`, не полагаясь на вручную устаревающий
  неполный список.
- CI запускает focused smoke coverage для delivery runner, delivery metrics,
  review fingerprint, verdict validation, manifest derivation, bootstrap,
  verify, wiring, archive diagnostics, release contract и drift fixture.
- Все JSON schemas проходят parse, Draft 2020-12 meta-schema check и positive/
  negative fixture validation; helper/schema drift приводит к red CI.
- В release gate добавлен согласованный lint/format check. Текущие два unused
  imports устранены, а правила и версии инструмента закреплены воспроизводимо.
- Drift command явно документирован как inventory-driven gate. CI продолжает
  использовать generated public-safe fixture; при необходимости добавлен
  отдельный `--self-test` или wrapper для удобного локального полного smoke.
- Добавлена одна документированная локальная команда или script, которая
  воспроизводит полный release baseline и возвращает non-zero при любом
  обязательном failure.
- `scripts/smoke-release-ci.py` проверяет не только наличие строк, но и полный
  обязательный command inventory либо заменен более надежной структурированной
  проверкой workflow.
- `AGENTS.md` перечисляет фактическую public surface и не называет реализованные
  templates/bootstrap/verify/scripts planned work.
- `README.md` включает delivery runner, metrics, новые schemas и public-safety
  helper в текущий статус; следующие направления не повторяют уже завершенные
  функции.
- `CHANGELOG.md`, compatibility notes и migration guide отражают все
  user-facing Unreleased изменения после `0.1.0`, включая operational runner,
  metrics, manifest/review contracts, aliases и finalization behavior.
- Markdown links, OpenSpec strict validation, config parsing, public-safety
  scans и `git diff --check` входят в финальную verification evidence.

## Change Set
- `harden-release-ci-inventory`
- `add-local-release-baseline`
- `sync-release-public-docs`

## Verify
- `openspec validate harden-release-ci-inventory --strict` -> pass
- `openspec validate add-local-release-baseline --strict` -> pass
- `openspec validate sync-release-public-docs --strict` -> pass
- `openspec validate --all --strict` -> pass
- `python3 scripts/smoke-release-ci.py` -> pass, `summary: pass (39/39 passed, 0 failed)`
- `python3 scripts/smoke-contract-schemas.py` -> pass, `SMOKE_CONTRACT_SCHEMAS_OK (5 schemas)`
- `python3 scripts/compile-python-inventory.py` -> pass, 21 tracked Python files compiled
- `.runtime/changerail/ci-venv/bin/ruff check bin scripts` -> pass
- `python3 scripts/public-surface-scan.py` -> pass, 416 files scanned, 0 findings
- `python3 scripts/run-release-baseline.py` -> pass, 25/25 baseline steps passed
- `rg -n "Begin Patch|Add File|End Patch|\\*\\*\\*" openspec/changes/archive/2026-07-12-*` -> pass, no matches after review fix
- `python3 scripts/run-release-baseline.py` -> pass after review fix, 25/25 baseline steps passed
- `git diff --check` -> pass

## Archive
- `openspec/changes/archive/2026-07-12-harden-release-ci-inventory/`
- `openspec/changes/archive/2026-07-12-add-local-release-baseline/`
- `openspec/changes/archive/2026-07-12-sync-release-public-docs/`

## Related
- `openspec/changes/archive/2026-07-12-harden-release-ci-inventory/`
- `openspec/changes/archive/2026-07-12-add-local-release-baseline/`
- `openspec/changes/archive/2026-07-12-sync-release-public-docs/`
- `.github/workflows/changerail-ci.yml`
- `AGENTS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/release-discipline.md`
- `requirements-dev.txt`
- `ruff.toml`
- `scripts/compile-python-inventory.py`
- `scripts/run-release-baseline.py`
- `scripts/smoke-contract-schemas.py`
- `scripts/smoke-release-ci.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `scripts/smoke-review-fingerprint.py`
- `scripts/smoke-drift.py`
- `openspec/board/1.backlog/protect-public-data-and-supply-chain.md`
- `openspec/board/1.backlog/harden-machine-readable-contracts-and-publish-scope.md`

## Result
implemented, verified, specs synced and OpenSpec changes archived

Published reviewed payload as `77e59e9`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `harden-release-ci-inventory`

### Why
Tracked runner, metrics, fingerprint and schema validation surfaces are part of
the release surface but are not fully covered by the current CI gate.

### Goal
Make release CI inventory-driven for Python syntax coverage, add pinned lint,
run the focused smoke inventory and validate all public schemas.

### Scope
- CI workflow and release workflow smoke.
- Python syntax inventory and lint configuration.
- Contract schema validation smoke.

### Acceptance
- CI compiles tracked Python helpers and smoke scripts from repository
  inventory.
- CI runs `ruff check bin scripts` with pinned tooling.
- CI runs required focused smoke checks for runner, metrics, fingerprint,
  verdict, manifest, bootstrap, verify, wiring, archive, release and drift
  behavior.
- Schema validation smoke covers all five public `changerail-*.schema.json`
  contracts.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-harden-release-ci-inventory/`

## Change 2: `add-local-release-baseline`

### Why
Maintainers currently need to reconstruct the full release baseline manually
from CI and docs.

### Goal
Add one local command that reproduces the mandatory release baseline and
documents generated public-safe drift fixture behavior.

### Scope
- Local release baseline script.
- CI invocation or CI inventory alignment.
- Release docs and README references.

### Acceptance
- One documented command runs the full release baseline and returns non-zero on
  mandatory failure.
- The command uses generated `.runtime/` fixtures for drift coverage.
- Docs explain that direct `scripts/smoke-drift.py` use remains
  inventory-driven.

### Depends On
- `harden-release-ci-inventory`

### Related
- `openspec/changes/archive/2026-07-12-add-local-release-baseline/`

## Change 3: `sync-release-public-docs`

### Why
Public docs and release notes lag behind the current tracked ChangeRail
surface.

### Goal
Update README, repository instructions, changelog, compatibility notes,
migration guide and release discipline so they describe the implemented
surface and current verification gates.

### Scope
- Public docs and release notes only.
- Generic public-safe examples only.

### Acceptance
- `AGENTS.md` and `README.md` describe current templates, bootstrap, verify,
  runner, metrics, schemas, public-safety helper, scripts and finalization
  surface.
- `CHANGELOG.md`, compatibility notes and migration guide include user-facing
  Unreleased changes after `0.1.0`.
- Drift docs identify inventory-driven manual use and generated fixture release
  use.

### Depends On
- `harden-release-ci-inventory`
- `add-local-release-baseline`

### Related
- `openspec/changes/archive/2026-07-12-sync-release-public-docs/`

## Log
- 2026-07-12T15:05:13Z card created from repository review findings about CI
  coverage, lint gaps, release reproducibility and stale public documentation.
- 2026-07-12T18:52:43Z decomposed into three OpenSpec changes, created
  apply-ready artifacts, validated each change with `openspec validate
  <change> --strict`, and moved card to `3.inprogress`.
- 2026-07-12T19:06:25Z implemented CI inventory/lint/schema gates, local release
  baseline and public docs sync; synced specs; archived all three changes; ran
  `python3 scripts/run-release-baseline.py` with 25/25 steps passing.
- 2026-07-12T19:17:10Z independent review cycle 1 returned `no-go` for
  archived OpenSpec files containing literal patch transcript text; removed the
  stray transcript blocks from archive docs, confirmed no patch markers remain,
  and reran `python3 scripts/run-release-baseline.py` with 25/25 steps passing.
- 2026-07-12T19:27:06Z publish finalized card into `4.done` with commit `77e59e9` and push status `pending`.
