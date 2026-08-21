## Why

Шесть связанных protocol-bearing payloads имеют apply-ready планы, но не могут
пройти deterministic review без опубликованного bounded investigation; четыре
также происходят из repeated field defect. Нужен один public-safe decision,
который задает exact per-successor scope и не повышает global limits.

## What Changes

- Зафиксировать exact successor ids и authorization-time `3.inprogress` paths.
- Ограничить каждый payload ceiling `500` production-counted LOC и отдельной
  protocol authorization.
- Выбрать shared-helper/single-source границы, исключающие duplicate expansion.
- Завершить repeated-defect analysis для bounded successors без выдачи нового
  rescue budget.
- Сохранить обязательные verification floors и stop/split behavior при drift.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: published bounded decision для exact field-validation
  successors и будущих authorization sources.

## Impact

Изменение затрагивает только board/OpenSpec contract artifacts и main
`changerail-contracts` spec. Production code, schemas и global review limits не
меняются.
