## Why

POSIX bootstrap всегда записывает relative symlink targets, поэтому tracked
consumer wiring зависит от topology bootstrap-машины. Кроме того, consumer не
хранит public-safe intended ChangeRail version/revision и не может отделить
валидность wiring от source drift.

## What Changes

- Добавить POSIX path modes `absolute` и explicit `relative`.
- Сделать absolute resolved ChangeRail root default для independent consumers.
- Ввести public schema `changerail.consumer-lock.v1` и generated tracked lock.
- Зафиксировать version, revision, backend, path mode и выбранные profiles без
  machine-local paths.
- Добавить `advisory` и `strict` source-drift enforcement.
- Расширить refresh/repair и verifier на manifest-owned POSIX symlink wiring.
- Добавить non-sibling clean-clone и ownership/scope negative fixtures.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: bootstrap создает portable POSIX wiring и
  tracked consumer lock.
- `changerail-project-verification`: verifier различает wiring validity, source
  match и advisory/strict source drift.
- `changerail-wiring-discovery`: discovery классифицирует POSIX path mode,
  ownership и lock state.
- `changerail-contracts`: public schema inventory получает
  `changerail.consumer-lock.v1`.

## Impact

Затрагиваются bootstrap/verify helpers, wiring discovery, JSON Schemas,
contract smoke, POSIX fixtures и consumer wiring/adoption/compatibility docs.
Windows `changerail.generated-wiring.v1` остается совместимым и не меняет
default backend.
