# Drift gate (Фаза 3)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 3 (`docs/opsx-source-of-truth-architecture.md`).
- Раздел 11 (Verification и drift).

## Summary
Реализовать `scripts/smoke-drift.py`, который проходит по configured workspace
roots и показывает, какие проекты подключены к OPSX, какие используют legacy
source, где сломан wiring и какие явно исключены — с machine-readable output для
CI и без публикации machine-local inventory в репозитории.

## Acceptance
- `scripts/smoke-drift.py` проходит по configured workspace roots и
  переиспользует verify-проверки для классификации.
- Есть механизм include/exclude списка проектов; machine-local inventory хранится
  в `internal/`, а не в tracked файлах.
- Machine-readable (JSON) output для CI, красно-зеленый по exit-коду.
- Отчет показывает consumer-классы: OPSX source, legacy source, broken wiring,
  disconnected и explicitly excluded.
- Public safety: в репозиторий не попадают реальные имена проектов и пути.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `docs/wiring-discovery.md`
- `scripts/smoke-wiring-discovery.py`

## Result
not started

## Next
- triage: после `verify-project` (Фаза 2). Через `opsx-ff` разложить на changes.

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.).

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 3 remaining scope.
