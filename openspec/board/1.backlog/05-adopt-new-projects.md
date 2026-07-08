# Подключение новых проектов (Фаза 5)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 5 (`docs/opsx-source-of-truth-architecture.md`).
- Раздел 13.2 (классы миграции B и D).

## Summary
Подключить нужные проекты workspace к OPSX через adoption/bootstrap flow и явно
исключить те, что не должны использовать OPSX, чтобы drift gate не считал их
disconnected.

## Acceptance
- Workspace roots проинвентаризированы (инвентарь в `internal/`, не в git).
- Выбранные проекты подключены через adoption/bootstrap flow; `verify-project`
  зеленый для каждого.
- Для проектов, которые не должны использовать OPSX, добавлен явный exclude в
  drift-gate.
- Public safety: в OPSX репозиторий не попадают реальные имена проектов и пути.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `internal/local-migration-context.md` (machine-local, не в git)

## Result
not started

## Next
- triage: после готового bootstrap (Фаза 2) и зеленого drift gate (Фаза 3),
  следом за первой волной миграции (Фаза 4).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.). Реальный список проектов держите в
`internal/`, а не в карточке.

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 5 scope.
