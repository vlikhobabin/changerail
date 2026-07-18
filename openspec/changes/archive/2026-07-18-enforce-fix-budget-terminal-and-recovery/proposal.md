## Why

Даже корректная agent guidance недостаточна, если supervisor считает exit code
`0` доказательством delivery. Fix-budget safety stop без опубликованной
карточки уже может получить ложный `DELIVERED`, а queue не имеет проверяемого
recovery ordering для такой остановки.

## What Changes

- Классифицировать exit code `0` без structured terminal outcome и без
  published card как `BLOCKED`, а не `DELIVERED`.
- Распознавать structured fix-budget exhaustion как non-delivered child outcome
  и останавливать downstream queue.
- Представить linked recovery ordering в plan/status так, чтобы recovery card
  выполнялась перед blocked downstream work, а original plan возобновлялся
  только после её reviewed publish.
- Добавить focused smoke/negative coverage для exit-0 safety stop, bounded
  micro-fix handoff, linked recovery, external blocker и resume barrier.
- Обновить runner/contracts docs и main specs.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-delivery-runner`: усилить single-card terminal classification,
  queue fail-fast и recovery ordering/resume behavior.
- `changerail-contracts`: закрепить machine-readable fix-budget reason и
  non-delivered outcome evidence без разбора произвольного свободного текста.

## Impact

Затрагиваются `bin/changerail-delivery-runner`, delivery status/plan handling,
runner smoke fixtures, contract docs и соответствующие OpenSpec main specs.
Публичные schema ids остаются совместимыми; новые optional fields или reason
values должны быть backward-compatible.
