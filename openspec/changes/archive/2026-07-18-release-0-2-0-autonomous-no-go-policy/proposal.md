## Why

Autonomous repeated `NO-GO` policy меняет публичный ChangeRail workflow
contract и требует понятного upgrade path для consumer projects. Вместо
оставления изменения в `Unreleased` нужно оформить минорный pre-stable release
`0.2.0` с changelog, migration notes и совместимостью.

## What Changes

- Подготовить release docs для `0.2.0`: `VERSION`, `CHANGELOG.md`,
  `docs/migration-guide.md` и compatibility notes.
- Зафиксировать, что `0.2.0` включает накопленные `Unreleased` изменения после
  `0.1.0` и новую autonomous repeated `NO-GO` escalation policy.
- Добавить migration instructions для проектов, уже использующих прежнюю
  two-cycle/manual exceptional authorization схему.
- Уточнить release discipline: workflow contract changes требуют migration
  notes даже когда consumer project не меняет tracked files.

## Capabilities

### New Capabilities

### Modified Capabilities

- `changerail-release-discipline`: release publication bundle и migration notes
  для workflow contract changes.

## Impact

- `VERSION`, `CHANGELOG.md`, `docs/migration-guide.md`,
  `docs/compatibility.md`, `docs/release-discipline.md`.
- OpenSpec release discipline spec.
- Consumer projects need verification and active agent session restart; local
  copied skills/instructions need manual refresh.
- No executable dependency pins or schema ids change in this release-prep card.
