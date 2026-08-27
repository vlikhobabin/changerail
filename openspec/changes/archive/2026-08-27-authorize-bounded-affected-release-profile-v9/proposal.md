## Why

Published rescue v9 устранил dependency/preflight contradiction и требует
отдельной docs-only authorization до появления clean implementation v9.
Authorization должна связать один exact successor с rescue investigation id,
ceiling и accumulated affected-profile contract.

## What Changes

- Публикуется exact six-field investigation authorization object для единственного
  `implement-bounded-affected-release-profile-v9` successor.
- Authorization получает exact dependency set и sole block, а future
  implementation — прямую rescue dependency и отдельную two-field reference.
- Закрепляются retained pre-production RED, 499 production LOC ceiling и весь
  accumulated affected fail-closed floor.
- Implementation v9, executable payload и certification остаются отсутствующими.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: добавляет exact v9 authorization, clean successor
  binding и direct-investigation implementation boundary.

## Impact

Change docs-only: board card, same-slug OpenSpec artifacts и main
`changerail-release-ci` specification. Production, tests, CI, schemas,
dependencies, runtime authority, implementation v9 и certification не
изменяются и не создаются.
