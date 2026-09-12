# Пересмотр recovery-подсистем

## Status
1.backlog

## Lifecycle
openspec-v1

## Owner
unassigned

## Source
- Разбор неопубликованной работы и стоимости тестов: `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md`.
- Измерения полного набора: 2367 воркер-секунд, из них ~1900 приходятся на recovery и release e2e.
- Карточка `4.done/restore-accepted-plan-after-implementation-drift.md` — предшественник части этого кода.

## Summary
Recovery-подсистемы — `plan_restoration`, `self_host_recovery`, `technical_recovery`,
`runtime_repair`, `installed_compatibility`, `installed_restoration` — это ~3 826
строк (19% ядра) и самая дорогая по тестам часть: они проверяются full-fidelity
(реальный git, реальный CLI, bare remote, дочерние процессы). При этом по факту
эксплуатации они применялись единицы раз: self-host recovery — 3 прогона,
plan restoration — 5.

Нужно решить, оправдана ли текущая глубина: это не «легаси» (код достижим,
защищает реальные инварианты и покрыт тестами), а вопрос цены и модели.

## Acceptance
### Requirement: Обосновать глубину recovery или упростить её
#### Scenario: Решение по каждой подсистеме
- [C1] Для каждой из шести подсистем зафиксировано: какой реальный отказ она предотвращает, как часто требуется, что произойдёт при её удалении. Итог по каждой — «оставить как есть», «упростить» или «удалить» с обоснованием.

#### Scenario: Стоимость доказана измерением
- [C2] Стоимость каждой подсистемы в коде и в тестах измерена (LOC, воркер-секунды, число тестов >5 с), а не оценена на глаз. Решение опирается на эти числа.

### Requirement: Дешёвая проверка состояния вместо полного e2e
#### Scenario: State-machine тесты
- [C3] Для сохраняемых подсистем переходы проверяются как состояния (append-only receipts, ancestry, crash-точки, отказы) без реального remote и полного CLI; real-e2e остаётся малым набором smoke.

## Scope
- `scripts/changerail/plan_restoration.py`, `self_host_recovery.py`, `technical_recovery.py`, `runtime_repair.py`, `installed_restoration.py`, `installed_compatibility.py`.
- Соответствующие `tools/changerail/tests/test_{plan_restore*,self_host*,technical_recovery,runtime_repair,installed_restoration}*.py`.
- `docs/self-host-recovery.md`, `docs/runtime-repair.md`, `docs/operations.md` — при изменении контракта.

## Non-Goals
- Не удалять read-only совместимость установленных предшественников без отдельного решения.
- Не менять контракт recovery в рамках этой карточки: только анализ и, при согласии оператора, упрощение с регрессией.
- Не трогать `close-exhausted-native-delivery` и `add-operator-review-allowance`.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
- none yet; a change is created before admission, once the keep/simplify/remove decision is made.

## Design
- Реализация будет описана в связанном design.md, если по итогам анализа потребуется изменение кода.

## Delivery Budget
- primary_invariant: по каждой recovery-подсистеме есть доказанное измерением решение — оставить, упростить или удалить
- expected_wall_minutes: 240
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 6
- estimated_production_loc: 0

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
- Анализ и измерения; изменение кода — только если принято решение «упростить» и оно оформлено отдельным scope.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "per-subsystem justification", "precondition": "Recovery modules and their tests as committed", "action": "For each subsystem record the prevented failure, observed usage and removal impact", "expected": "Each subsystem has a written keep/simplify/remove decision with rationale", "method": {"kind": "inspection", "target": "docs/self-host-recovery.md"}, "stage": "implementation"},
    {"condition": "C2", "seam": "measured cost", "precondition": "A full suite run with per-test durations", "action": "Attribute production LOC and worker-seconds to each subsystem", "expected": "Decisions cite measured numbers, not estimates", "method": {"kind": "inspection", "target": "docs/operations.md"}, "stage": "implementation"},
    {"condition": "C3", "seam": "cheap state-machine coverage", "precondition": "A subsystem selected for simplification", "action": "Replace full-fidelity e2e with transition-level checks plus a small smoke set", "expected": "Coverage of the same refusals is retained at materially lower test cost", "method": {"kind": "inspection", "target": "docs/runtime-repair.md"}, "stage": "final"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Any simplification keeps the existing fail-closed refusals and their regressions", "conditions": ["C1", "C3"]},
    {"kinds": ["mutation", "restart"], "applies": true, "decision": "Append-only receipts, ancestry and crash boundaries are preserved or explicitly retired with operator sign-off", "conditions": ["C1"]},
    {"kinds": ["concurrency"], "applies": false, "decision": "Analysis only; no runtime concurrency change in this card", "conditions": []},
    {"kinds": ["publication", "external_effects"], "applies": false, "decision": "Local synthetic projects only; no network publication", "conditions": []}
  ]
}
```
- `git diff --check`

## Related
- `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md`
- `.runtime/planning/repo-cleanup/INVENTORY-AND-PLAN.md`
- `scripts/changerail/self_host_recovery.py`, `plan_restoration.py`, `technical_recovery.py`

## Result
not started

## Next
- triage

## Log
- 2026-09-12T18:00:00Z карточка создана, чтобы вернуться к вопросу позже; решение по глубине recovery не принято.
