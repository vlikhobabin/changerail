## Why

Published investigation выбрала exact phase-routed aggregate/child authority
boundary и bounded successor, но deterministic preflight не может принять
investigation decision как authorization source. Нужна отдельная clean tracked
`4.done` карточка, которая связывает решение только с выбранным successor.

## What Changes

- Опубликовать один machine-readable authorization object для exact
  investigation, successor и canonical board paths.
- Ограничить successor ceiling 500 production-counted LOC и разрешить новый
  authority/wire protocol только для принятой aggregate/child authority,
  resume и status boundary.
- Зафиксировать fail-closed exact-chain contract: любая подмена card id/path,
  investigation, ceiling или protocol flag отклоняет authorization.
- Сохранить production delta равным нулю и не изменять runner, schemas или
  runtime behavior.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: exact bounded phase-routed authorization source и
  условия его одноразового применения к выбранному successor.

## Impact

- Planning создает target card metadata и
  `openspec/changes/authorize-bounded-phase-routed-delivery-payload/`; delivery
  синхронизирует delta в `openspec/specs/changerail-contracts/spec.md`.
- Exact successor уже содержит existing reciprocal contract: authorization
  source depends on investigation, investigation blocks exact successor, а
  successor depends on investigation и ссылается на будущий published
  authorization source. Его можно менять только для восстановления этой
  metadata при обнаруженном drift.
- `scripts/smoke-review-preflight.py` меняется только если существующая
  non-production coverage не доказывает exact-chain acceptance и mismatch
  rejection.
- Consumer-project behavior, provider authority, credentials, production code,
  schemas и runtime state не меняются.
