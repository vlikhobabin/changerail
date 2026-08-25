## Why

Published tiered-loop investigation фиксирует executable authority boundary,
но future implementation не может consumировать decision вместо отдельного
clean tracked `4.done` authorization source. Этот source нужно опубликовать до
создания единственного successor.

## What Changes

- Опубликовать на authorization card ровно один recognized inline
  `Investigation authorization` object с шестью generic fields и exact
  investigation/successor ids и canonical paths.
- Зафиксировать ceiling `500`, protocol allowance `true` и независимый
  implementation limit `<=499` executable LOC от
  `45a2de98924c61bb9e944767013ea09918bba4b0`.
- Сохранить exact reciprocal lineage между published investigation,
  authorization и future successor, включая exact two-field inline reference.
- Ограничить payload board/OpenSpec/spec documentation: production, tests и
  runtime additions равны `0` LOC; successor card/code не создаются.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: опубликовать exact bounded authorization source для
  единственного future tiered release verification successor.

## Impact

Planning меняет только authorization board card и
`openspec/changes/authorize-bounded-tiered-release-verification-loop/`.
Delivery синхронизирует delta в
`openspec/specs/changerail-release-ci/spec.md`. Production, tests, workflows,
schemas, helpers, CLI, runtime state и future successor не меняются.
