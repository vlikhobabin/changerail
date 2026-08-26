## Why

Опубликованное integration decision требует отдельную docs-only authorization
после публикации scheduler v1 и до появления affected-profile successor. Это
отделяет selection/activation authority от уже проверенного execution primitive.

## What Changes

- Публикуется exact six-field affected-profile authorization object и future
  two-field implementation reference.
- Фиксируются clean start, `<=499` production LOC, canonical inventory,
  bounded Git selection, sole scheduler activation и full-only authority.
- Successor, executable activation и expensive evidence остаются отсутствующими.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: добавить exact bounded affected-profile-v1
  authorization contract из опубликованного integration decision.

## Impact

Меняются только эта карточка, same-slug OpenSpec artifacts, синхронизированный
release-CI spec и archive metadata. Production code, tests, dependencies,
schemas, CI, baseline и runtime behavior остаются неизменными.
