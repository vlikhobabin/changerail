## Why

После фиксации clean release scope и distribution contract необходимо собрать
один final-certification payload для `1.0.0`, который согласует version,
changelog, compatibility, migration и publication gates на exact candidate.

## What Changes

- Установить root `VERSION` в `1.0.0` и добавить датированный release section
  при сохранении нового пустого `Unreleased`.
- Зафиксировать compatibility и migration contract перехода `0.5.0 -> 1.0.0`,
  включая required actions, rollback и честный native Windows caveat.
- Обновить release discipline и публичные status/roadmap references с
  final-certification и publication порядком.
- Подготовить exact sequential isolated-clone verification floor, trusted
  dependency integrity checks и public GitHub Release asset contract.
- Не включать deferred phase-routed/retention payloads и не менять dependency
  pins или runtime behavior.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: определить observable metadata,
  certification и post-review publication contract первого stable release.

## Impact

Затрагиваются `VERSION`, `CHANGELOG.md`, release/compatibility/migration docs,
README status, release verification metadata и OpenSpec release-discipline
spec. Annotated tag и GitHub Release создаются только после fresh independent
`GO`, scoped commit/push и повторной проверки remote reachability.
