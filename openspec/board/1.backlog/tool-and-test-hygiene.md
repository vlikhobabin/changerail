# Гигиена ядра и тестов: мёртвый код, дубли, маршруты прогона

## Status
1.backlog

## Lifecycle
openspec-v1

## Owner
unassigned

## Source
- Аудит мёртвого кода ядра 2026-09-12 (аудит A): 7 подтверждённых находок, 9 средних, 6 групп дублей.
- Аудит тестов 2026-09-12 (аудит B): 24 группы пересечений, 3 модуля без покрытия.
- Измерения прогона: 38 тестов >5 с дают 66% call-времени; setup был 42% воркер-времени.

## Summary
Накопившийся мелкий технический долг, не связанный с поведением доставки:
недостижимый код после удаления FF-маршрута, дублирующиеся помощники, тесты с
пересекающимся покрытием и отсутствие быстрого маршрута прогона.

Это заготовка: перед доставкой карточку нужно разделить по группам, потому что
сейчас в ней несколько независимых изменений.

## Acceptance
### Requirement: Убрать подтверждённо мёртвый код
#### Scenario: Подтверждённые находки удалены с регрессией
- [C1] Удалены `guarded_pump` (и осиротевший `stream_errors`), `_deleted_digest`, `acceptance_condition_ids`, `BOARD_COLUMNS`, `_LEGACY_OBSERVED_PROOF_CONTINUATION`, недостижимая ветка `else` на `legacy_observed_proof_continuation`, `engine_runtime.runner_python`. Каждое удаление подтверждено отсутствием ссылок и покрыто регрессией на прежнее поведение там, где оно наблюдаемо.

#### Scenario: Совместимость не задета
- [C2] Read-only чтение исторических runs, отклонение retired-профилей и совместимость установленных предшественников сохранены и покрыты существующими тестами.

### Requirement: Устранить дублирование в ядре
#### Scenario: Единые помощники
- [C3] Хеширование, чтение закрытого JSON и валидация формы ссылок сведены к одному каноническому помощнику каждый. Расхождение `ensure_ascii` между `evidence_dependencies` и `review_allowance` устранено и покрыто регрессией.

### Requirement: Быстрый маршрут прогона
#### Scenario: Маршруты по маркерам
- [C4] Тяжёлые real-e2e тесты помечены маркером и исключаются из быстрого маршрута; полный маршрут сохраняет их. Быстрый маршрут укладывается в согласованный бюджет и документирован в `CONTRIBUTING.md`.

### Requirement: Покрытие без пересечений
#### Scenario: Дубли и пробелы
- [C5] Пересекающиеся тесты сведены (в частности `test_distribution_execution_boundary` полностью покрыт `test_native_execution_contract`); для `installed_compatibility`, `openspec_board`, `source_install` добавлены выделенные модули либо зафиксировано осознанное решение не добавлять их.

### Requirement: Документация и публичный скан
#### Scenario: Осиротевшие и устаревшие места
- [C6] `DEV-CHECKOUT.md` слит с `docs/working-checkout.md` или удалён как осиротевший; `public-surface-scan.py` больше не перечисляет несуществующие корни, а `npm-logs` внесён в `SKIP_DIRS`, чтобы удалённый лог не ломал гейт повторно.

## Scope
- `scripts/changerail/local_delivery.py`, `engine_runtime.py`, `evidence_dependencies.py`, `review_allowance.py`, `native_workflow.py`, `scripts/public-surface-scan.py`.
- `tools/changerail/tests/*`, `tools/changerail/tests/conftest.py`, `pyproject.toml` (маркеры).
- `DEV-CHECKOUT.md`, `CONTRIBUTING.md`.

## Non-Goals
- Не менять наблюдаемое поведение доставки, полномочия и гейты.
- Не удалять read-only совместимость и намеренные отказы, перечисленные в аудите как «do not remove».
- Не заниматься здесь recovery-подсистемами и machine-гвардами — для них отдельные карточки.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
- none yet; the card is split into separate changes before admission.

## Design
- Реализация будет описана в связанном design.md; удаление кода и тестовые маршруты проверяются разными наборами.

## Delivery Budget
- primary_invariant: удалён только подтверждённо мёртвый код и дубли, наблюдаемое поведение и fail-closed отказы сохранены
- expected_wall_minutes: 240
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 8
- estimated_production_loc: 200

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
- Разделить на отдельные доставки перед реализацией: удаление кода, тестовые маршруты и документация проверяются разными наборами.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "dead code removal", "precondition": "Confirmed unreferenced names in the core", "action": "Remove each and run the full suite", "expected": "No test regresses and each removed name has no reference", "method": {"kind": "inspection", "target": "docs/operations.md"}, "stage": "implementation"},
    {"condition": "C2", "seam": "compatibility preserved", "precondition": "Historical runs and retired profiles", "action": "Run read-only history, retired-profile and installed-predecessor tests", "expected": "Same refusals and read-only behaviour as before", "method": {"kind": "inspection", "target": "docs/migration.md"}, "stage": "implementation"},
    {"condition": "C3", "seam": "single canonical helpers", "precondition": "Duplicate hash and JSON readers", "action": "Consolidate and cover with a regression on the JSON-digest flag", "expected": "One helper per concern; no identity divergence", "method": {"kind": "inspection", "target": "docs/runtime-repair.md"}, "stage": "implementation"},
    {"condition": "C4", "seam": "run routes", "precondition": "Full suite with per-test durations", "action": "Mark heavy real-e2e tests and measure the fast route", "expected": "Fast route within its budget; full route unchanged in coverage", "method": {"kind": "inspection", "target": "CONTRIBUTING.md"}, "stage": "final"},
    {"condition": "C5", "seam": "test overlap and gaps", "precondition": "Overlapping modules and uncovered modules", "action": "Consolidate duplicates and add or justify dedicated modules", "expected": "No lost assertion; gaps closed or explicitly accepted", "method": {"kind": "inspection", "target": "CONTRIBUTING.md"}, "stage": "final"},
    {"condition": "C6", "seam": "docs and public scan", "precondition": "Orphan doc and stale scan roots", "action": "Merge/remove the orphan doc and fix the scan roots and skips", "expected": "Scan passes with no stale root and npm-logs cannot break it again", "method": {"kind": "inspection", "target": "CONTRIBUTING.md"}, "stage": "final"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Removal only after reference proof; fail-closed refusals stay and keep their regressions", "conditions": ["C1", "C2"]},
    {"kinds": ["mutation"], "applies": false, "decision": "No state, receipt or lock semantics change", "conditions": []},
    {"kinds": ["concurrency", "restart"], "applies": false, "decision": "No runtime concurrency or recovery change", "conditions": []},
    {"kinds": ["publication", "external_effects"], "applies": false, "decision": "Local repository maintenance only", "conditions": []}
  ]
}
```
- `./bin/test-changerail`
- `./.venv/bin/python -m ruff check scripts tools/changerail/tests distribution.py`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Related
- `.runtime/planning/repo-cleanup/INVENTORY-AND-PLAN.md`
- `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md`
- `scripts/changerail/local_delivery.py`, `scripts/changerail/engine_runtime.py`, `scripts/public-surface-scan.py`

## Result
not started

## Next
- Разделить на отдельные доставки перед реализацией.

## Log
- 2026-09-12T18:00:00Z карточка создана как заготовка по итогам аудитов ядра и тестов.
