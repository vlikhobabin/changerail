# Подключение новых проектов (Фаза 5)

## Status
4.done

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
- Adopted projects: `verify-project` зелёный для каждого. Workspace-drift
  smoke зелёный: каждый workspace-root либо `opsx_source`, либо
  `explicitly_excluded` (0 `broken_wiring`/`disconnected`).

## Archive
- Операционная карточка (adoption/exclude в чужих репо и machine-local
  инвентаре); OpenSpec-архивации не требует. Инвентарь и причины exclude — в
  `internal/`.

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `internal/local-migration-context.md` (machine-local, не в git)

## Result
Workspace roots проинвентаризированы (инвентарь в `internal/`). Проекты,
которым нужен OPSX, подключены через adoption flow (verify-project зелёный);
проекты вне OPSX (доменный агрегатор как source-layer, machine-ops scratch)
добавлены в явный `exclude` drift-gate с причинами. Итог: drift-smoke зелёный
на 100% — либо `opsx_source`, либо `explicitly_excluded`.

## Next
- Поддерживать инвентарь `internal/` при появлении новых workspace-проектов:
  каждый новый root — либо adopt, либо explicit exclude.

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.). Реальный список проектов держите в
`internal/`, а не в карточке.

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 5 scope.
- 2026-07-09 done: workspace roots inventoried; adopted the projects that
  need OPSX (verify green) and added explicit drift excludes for the rest;
  drift-smoke 100% green. Moved to 4.done.
