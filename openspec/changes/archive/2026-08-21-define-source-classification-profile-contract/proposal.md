## Why

Consumer-owned `.changerail/source-classification.yaml` решает подсчет
предметных исходников, но новый проект не может воспроизводимо выбрать правила
без ручного копирования YAML. Нужен data-only versioned profile contract,
который интеграции могут поставлять без расширения trusted executable surface.

## What Changes

- Добавить schema `changerail.source-classification-profile.v1` с stable id,
  version, source metadata и совместимым classification payload.
- Определить canonical serialization/checksum, repository-relative paths и
  запрет executable/network content.
- Разрешить built-in generic profiles и explicit local integration profile,
  валидируемые одной схемой.
- Зафиксировать deterministic merge rules и fail-closed conflicts для
  пересекающихся source kinds с несовместимыми measurement strategies.
- Сохранить `.changerail/source-classification.yaml` единственным runtime
  source of truth для review preflight.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: versioned profile schema, checksum и merge semantics
  дополняют существующий source-classification contract.

## Impact

- новая profile schema и schema inventory
- generic built-in profile data
- contract validation and conflict fixtures
- existing `changerail.source-classification.v1` remains compatible
