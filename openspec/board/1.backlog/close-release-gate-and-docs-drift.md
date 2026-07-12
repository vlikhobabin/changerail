# Закрыть пробелы release gate и drift публичной документации

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

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
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `.github/workflows/changerail-ci.yml`
- `AGENTS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/release-discipline.md`
- `scripts/smoke-release-ci.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `scripts/smoke-review-fingerprint.py`
- `scripts/smoke-drift.py`
- `openspec/board/1.backlog/protect-public-data-and-supply-chain.md`
- `openspec/board/1.backlog/harden-machine-readable-contracts-and-publish-scope.md`

## Result
not started

## Next
- Triage the required release floor and split the story into CI coverage,
  lint/schema gates and documentation/release-note changes.

## Log
- 2026-07-12T15:05:13Z card created from repository review findings about CI
  coverage, lint gaps, release reproducibility and stale public documentation.
