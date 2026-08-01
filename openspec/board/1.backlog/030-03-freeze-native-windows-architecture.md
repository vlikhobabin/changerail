# Зафиксировать native Windows architecture и test plan

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`030-native-windows-discovery`

## Series Index
`03`

## Source
- Результаты двух-host исследования `030-02`.

## Summary
Выбрать default/fallback native Windows runtime и wiring architecture,
зафиксировать tracked/untracked ownership, upgrade/drift model и обязательную
test matrix, затем полностью перепланировать серию `040`.

## Acceptance
- Architecture decision выбирает один default path и bounded fallbacks.
- Явно определены prerequisites: shell, Python, Git, Developer Mode/elevation.
- Определено, какие wiring artifacts tracked, generated ignored или copied.
- Описаны bootstrap, verify, drift, upgrade и cleanup semantics.
- Threat model покрывает junction traversal, accidental staging, credentials,
  command quoting и untrusted repository content.
- Test matrix включает оба Windows hosts и deterministic local fixtures.
- Все cards серии `040` обновлены против решения до delivery.

## Scope
- Architecture/design docs, compatibility contract и implementation backlog.
- Изменение состава/порядка серии `040`.

## Non-Goals
- Реализация выбранной architecture.
- Обещание unsupported Windows editions без evidence.

## Depends On
- `030-02-reproduce-windows-runtime-wiring-and-git-behavior`

## Implementation Notes
- Не сохранять несколько равноправных default strategies.
- Если host results расходятся, support matrix должна объяснять branching rule,
  а не скрывать несовместимость.

## Change Set
- none yet

## Verify
- Architecture review против probe evidence.
- Cross-link и board series consistency checks.
- Public-surface scan current/history.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `docs/compatibility.md`

## Result
not started

## Next
- Провести mandatory refresh серии `040`; только затем принимать `040-01`.

## Log
- 2026-08-01T15:07:29Z карточка создана как research exit gate.
