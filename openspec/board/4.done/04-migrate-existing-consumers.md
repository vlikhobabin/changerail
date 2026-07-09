# Миграция существующих потребителей (Фаза 4)

## Status
4.done

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
- `verify-project` зелёный для каждого переведённого потребителя; suite
  drift-gate агрегатора остаётся зелёным после де-дупа generic-скиллов.

## Archive
- Операционная карточка (перевод чужих репозиториев); OpenSpec-архивации не
  требует. Детали выполнения — в `internal/`.

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `internal/local-migration-context.md` (machine-local, не в git)

## Result
Существующие потребители переведены на OPSX точечно (по одному проекту, каждый
как прямой потребитель `/opt/opsx`, generic-only). Доменный агрегатор обработан
по слоеной модели: generic `openspec-*` де-дуплены в OPSX, специализированные
`opsx-*` и доменные скиллы оставлены локально; его drift-gate правок не
потребовал. Практический playbook и краевые случаи занесены в раздел 13.3.

## Next
- Опциональный follow-up: полная генерализация специализированных `opsx-*`
  агрегатора в domain-overlay поверх generic-базы из OPSX (Option B) — отдельной
  OpenSpec-change внутри доменного репозитория.
- Фаза 5 (adoption новых проектов + явные exclude для проектов вне OPSX) —
  отдельная карточка `05`.

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...` и т.д.). Реальный список проектов и порядок
миграции держите в `internal/`, а не в карточке.

Принцип порядка (обобщённо, без реальных имён):
- миграция идёт по одному проекту, точечно; проект переводится только после
  приостановки активной работы в нём (грязное дерево / WIP — сначала пауза);
- aggregator-flip не обязан быть первым: если он транзитивно перецепляет
  потребителей, находящихся в активной работе, предпочтительнее сначала
  перевести отдельные проекты как прямые потребители OPSX (раздел 8, вариант 1),
  а флип агрегатора отложить на конец, когда останутся только доменные
  потребители;
- каждый шаг требует поштучного подтверждения оператора; migration diff
  коммитится в репозитории проекта, не в `/opt/opsx`.

Подтверждённый ordered-инвентарь и наблюдаемое состояние целей — в
`internal/local-migration-context.md` и `internal/opsx-migration-inventory.json`.

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 4 scope.
- 2026-07-09 migration order principle recorded (one-at-a-time, pause-before,
  aggregator-flip deferred); real list + first target pinned in `internal/`.
- 2026-07-09 done: all confirmed consumers migrated (generic-only) and the
  domain aggregator de-duped (openspec-* -> OPSX, opsx-*/domain kept local);
  moved to `4.done`. Validated playbook folded into architecture section 13.3.
