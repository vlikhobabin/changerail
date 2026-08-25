## Why

Published structural investigation фиксирует exact bounded successor,
но deterministic preflight не может использовать investigation decision
вместо отдельного clean tracked `4.done` authorization source. Нужно
опубликовать только этот narrow source до создания implementation
successor.

## What Changes

- Опубликовать на source card ровно один recognized inline
  `Investigation authorization` object с шестью generic fields и exact
  investigation/successor ids и canonical paths.
- Зафиксировать ceiling `301`, protocol allowance `false` и
  независимый implementation limit `<=300` added production LOC от
  `ccccb62562e1646b595119edd3326763860f14a7`.
- Сохранить exact reciprocal lineage: published investigation blocks
  authorization и future successor, authorization depends on investigation и
  blocks future successor, а future successor depends on investigation и
  содержит только exact two-field inline authorization reference.
- Ограничить payload board/OpenSpec/spec documentation: production, tests и
  runtime additions равны `0` LOC; successor card/code не создаются.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: опубликовать exact bounded authorization source
  и обязательную inline-reference policy для единственного future
  structural public-history successor.

## Impact

Planning меняет только authorization board card и
`openspec/changes/authorize-bounded-structural-public-history-scan/`. Delivery
синхронизирует delta в `openspec/specs/changerail-release-ci/spec.md` и
может дополнить relation docs только exact successor link. Production
scanner, tests, workflows, schemas, helpers, CLI, runtime state и future
successor не меняются.
