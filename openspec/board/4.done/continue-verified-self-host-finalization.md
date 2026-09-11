# Продолжить проверенную self-host финализацию

## Status
4.done

## Lifecycle
openspec-v1

## OpenSpec Stage
proposal

## Summary
Исправить обнаруженные реальной доставкой границы empty resume, bound identity и test fixture ownership.

## Acceptance
- [C1] Explicit rebind is atomic and rejects drift/live ownership.
- [C2] Empty and bound self-host continuations retain exact history and gates.
- [C3] Shared regression fixtures pass under the real bound environment.

## Scope
- Engine bootstrap/binding, recovery admission и общие regression fixtures.

## Non-Goals
- Изменение старых runs, checkpoints, review allowance или frozen snapshots.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `continue-verified-self-host-finalization`

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Design
- Explicit receipt и exact identity; bootstrap отдельно от действующей delivery.

## Delivery Budget
- primary_invariant: exact continuation of a stopped bound finalization
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 4
- estimated_production_loc: 300

## Verify
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "self-host continuation",
      "precondition": "retained terminal self-host run",
      "action": "execute the matching regression",
      "expected": "Explicit rebind is atomic and rejects drift/live ownership",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "self-host continuation",
      "precondition": "retained terminal self-host run",
      "action": "execute the matching regression",
      "expected": "Empty and bound self-host continuations retain exact history and gates",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "self-host continuation",
      "precondition": "retained terminal self-host run",
      "action": "execute the matching regression",
      "expected": "Shared regression fixtures pass under the real bound environment",
      "method": {
        "kind": "test",
        "target": "tools/changerail/tests/test_self_host_recovery.py"
      },
      "stage": "implementation"
    }
  ],
  "risks": [
    {
      "kinds": [
        "input_safety",
        "mutation",
        "restart",
        "concurrency",
        "publication",
        "external_effects"
      ],
      "applies": true,
      "decision": "explicit exact receipts, locks, no live owners and ordinary gates",
      "conditions": [
        "C1",
        "C2",
        "C3"
      ]
    }
  ]
}
```

## Result
Реализованы explicit engine rebind с before/after receipts и crash reconciliation, подтверждение прежней bound identity, точное продолжение пустого payload через ordinary ancestry. Неизменность source history, completed groups и review allowance сохраняется.

C1: `test_engine_snapshot.py` — 49 passed, включая race, drift, живого владельца и сбои между rename и fsync intent/binding. C2: `test_self_host_recovery.py` — 51 passed; сквозной сценарий с двумя остановками/resume, реальными snapshots и локальной публикацией — 1 passed. В E2E модель контролируется fixture; archive, final verification и Git publication выполняются штатно.

C3: полный локальный `./bin/test-changerail` под binding и Python 3.14.4 дал 1001 passed и один отказ crash-unit из-за постороннего непрозрачного процесса. Исправлена только изоляция списка процессов в test fixture; весь затронутый модуль повторно прошёл (51 passed), остальные 951 проверки и production source не менялись. Ruff, strict OpenSpec validation и публичная Git/distribution-выборка прошли проверку. Evidence сохранены локально в `.runtime/changerail/self-host-work/`.

Один независимый review завершён GO после исправлений. Canonical spec синхронизирован; stock archive: `openspec/changes/archive/2026-09-11-continue-verified-self-host-finalization/`. Полный CI точного коммита обязателен до операционного rebind и перехода сохранённого run.

## Next
- Принять план, исправить подтверждённые дефекты и проверить переход до применения.

## Log
- 2026-09-11 Коррекция по реальному self-host successor, без повторного apply origin.
- 2026-09-11T08:05:10Z accepted native OpenSpec plan
- 2026-09-11 Корректирующая инфраструктура проверена и архивирована; source runtime и тестовая обвязка получили GO. Frozen Next сохранён.
