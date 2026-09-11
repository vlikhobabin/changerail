## Why

Изменение ядра ChangeRail во время собственной доставки смешивает identity engine
с изменяемым продуктом и блокирует штатное продолжение перед review.

## What Changes

- Добавляется immutable engine snapshot с отдельной execution identity.
- Self-host prepare/apply/reconcile создают ровно одного successor из остановленного run.
- Successor наследует историю completed groups и review accounting, начинает finalize
  и проходит обычные review, archive, final verification и publication gates.
- Старый run и его receipts остаются неизменными; drift engine, launcher, profile,
  payload или live process отклоняется fail-closed.

## Capabilities

### Modified Capabilities

- `native-delivery`

## Impact

Затрагиваются runtime routing, recovery receipts, lifecycle integration, launchers,
schemas, tests и русская операторская документация. Consumer-проекты не изменяются
до отдельной операции development attach.
