# Добавить manifest scope reconciliation и handoff summary

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`010-core-release-contracts`

## Series Index
`04`

## Source
- Consumer publish потребовал ручного rename-aware сравнения manifest и staged
  diff; review/verification/card final state не сохранились в handoff ledger.

## Summary
Добавить machine-readable `scope-check` для delivery manifest и расширить
ignored handoff summary данными review, verification и окончательного состояния
карточки.

## Acceptance
- `scope-check` сравнивает manifest с working tree и отдельно со staged diff.
- Проверка NUL-safe и корректно обрабатывает add/modify/delete/rename.
- Результат явно перечисляет missing, extra и mismatched paths.
- Ignored runtime paths не считаются committable scope.
- Manifest хранит concise review и verification summaries и final card state.
- Schema и negative smoke отклоняют ложный green при extra staged path.

## Scope
- Delivery manifest schema/helper и documentation.
- Review/publish handoff integration.
- Rename и staged-scope fixtures.

## Non-Goals
- Хранение raw command logs в manifest.
- Generic command evidence capture: карточка `020-02`.

## Depends On
- `010-03-fix-publish-finalization-ledger`

## Implementation Notes
- Строить сравнение из structured Git status/index data, а не из
  `--name-only` text parsing.
- Summary должна оставаться малой; raw evidence остается ignored и ссылочной.

## Change Set
- `add-manifest-scope-and-handoff` (planned)

## Change 1: `add-manifest-scope-and-handoff`

### Why
Review/publish handoff сейчас требует ручного rename-aware сравнения manifest и
staged diff, а итоговые review/verification/card summaries не закреплены в
машиночитаемом ignored ledger.

### Goal
Добавить manifest scope reconciliation и concise handoff summary, которые
проверяют tracked payload без включения raw runtime logs в commit scope.

### Scope
- Delivery manifest schema/helper и documentation.
- Review/publish handoff integration.
- Rename и staged-scope fixtures.

### Acceptance
- `scope-check` сравнивает manifest с working tree и отдельно со staged diff.
- Проверка NUL-safe и корректно обрабатывает add/modify/delete/rename.
- Результат явно перечисляет missing, extra и mismatched paths.
- Ignored runtime paths не считаются committable scope.
- Manifest хранит concise review и verification summaries и final card state.
- Schema и negative smoke отклоняют ложный green при extra staged path.

### Depends On
- `fix-publish-finalization-ledger`

### Related
- `openspec/changes/add-manifest-scope-and-handoff/`

## Verify
- Scope-check smoke для add/modify/delete/rename и non-UTF-8 path.
- Negative staged extra/missing cases.
- Contract schema smoke, release baseline и `git diff --check`.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `scripts/changerail_delivery_manifest.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `docs/changerail-contracts.md`

## Result
not started

## Next
- Выполнить через series `010` runner plan после `010-03`.

## Log
- 2026-08-01T15:07:29Z карточка выделена из E1 delivery feedback.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
