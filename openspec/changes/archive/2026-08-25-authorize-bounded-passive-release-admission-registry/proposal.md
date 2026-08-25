## Why

Published rescue `rescue-tiered-release-authority-two-stage-boundary` отделяет
dormant passive A1 от terminal authority A2, но deterministic preflight может
допустить будущую реализацию A1 только через отдельный clean tracked
authorization source. Этот source нужно подготовить и опубликовать до создания
successor-карточки.

## What Changes

- Опубликовать на authorization card ровно один recognized inline
  `Investigation authorization` object с шестью generic fields, exact rescue и
  future A1 identities, ceiling `500` и protocol allowance `false`.
- Зафиксировать reciprocal lineage для будущего
  `implement-passive-release-admission-registry` и exact two-field reference на
  опубликованную authorization-карточку.
- Ограничить A1 passive ownership literal 35-record registry, bounded offline
  admission, effective-PATH/pin/Ruff checks, bounded Git selector, closed map и
  AST/fault oracles; до exact published A2 A1 остаётся structurally dormant.
- Разрешить authorization и будущей A1 delivery только focused, static,
  offline и current-only proof; history scan, full baseline, authority receipt
  и terminal capture не являются допустимым evidence.
- Сохранить payload docs-only: production, test и runtime additions равны `0`
  LOC; successor card/code не создаются.

## Capabilities

### New Capabilities

- Нет.

### Modified Capabilities

- `changerail-release-ci`: опубликовать exact bounded authorization source для
  dormant A1 и закрепить его ownership, dormancy и focused-only proof boundary.

## Impact

Planning меняет только authorization board card и
`openspec/changes/authorize-bounded-passive-release-admission-registry/`.
Delivery синхронизирует delta в
`openspec/specs/changerail-release-ci/spec.md`. Production code, tests,
workflows, schemas, CLI, runtime state, terminal authority и future successor
не меняются.
