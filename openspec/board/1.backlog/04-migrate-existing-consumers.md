# Миграция существующих потребителей (Фаза 4)

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- OPSX roadmap, раздел 12, Фаза 4 (`docs/opsx-source-of-truth-architecture.md`).
- Разделы 8 (Symlink-модель, слоеная модель) и 13 (миграция).

## Summary
Перевести существующие проекты с частично настроенным локальным workflow на
OPSX как единый source of truth. Для workspace с развернутой сетью потребителей
предпочтителен агрегатор: одно изменение в доменном источнике вместо правки
каждого потребителя.

## Acceptance
- Первый legacy aggregator переключен на `/opt/opsx`; транзитивные consumers
  проверены зеленым discovery/drift smoke.
- Канонические проверки legacy drift-gate указывают на OPSX либо проверяют
  aggregator-симлинки на OPSX.
- Решено владение OpenSpec-спеками и тестами generic skills: перенос в OPSX или
  зафиксированное переходное двойное владение с явным сроком.
- Локальные docs ссылаются на OPSX как внешний workflow layer; legacy
  bootstrap-runbook помечен superseded ссылкой на `bootstrap-project`.
- Старые локальные копии убраны, если больше не нужны.
- Public safety: migration diffs коммитятся в проектных репозиториях; в OPSX
  репозиторий не попадают реальные имена проектов и пути (детали в `internal/`).

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
- triage: после зеленого drift gate (Фаза 3) и готового bootstrap/adoption (Фаза 2).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.). Реальный список проектов и порядок
миграции держите в `internal/`, а не в карточке.

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 4 scope.
