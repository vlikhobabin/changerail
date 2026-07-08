## Why

OPSX уже содержит bootstrap, verification и drift gates, но пока не имеет
публичного release contract. Без semver, changelog, compatibility и migration
notes потребители не могут безопасно обновлять `/opt/opsx` или оценивать
breaking changes.

## What Changes

- Добавить canonical version marker для текущей версии OPSX.
- Добавить changelog с явными `BREAKING:` marker-ами.
- Добавить release discipline doc с правилами semver и release checklist.
- Добавить compatibility notes для Codex CLI, Claude Code и OpenSpec CLI.
- Добавить migration guide между версиями OPSX.
- Обновить публичные README/architecture ссылки на release discipline.

## Capabilities

### New Capabilities
- `opsx-release-discipline`: public OPSX versioning, changelog,
  compatibility and migration contract.

### Modified Capabilities
- none

## Impact

- Public docs: `README.md`, `docs/opsx-source-of-truth-architecture.md`.
- New release docs: `VERSION`, `CHANGELOG.md`, `docs/release-discipline.md`,
  `docs/compatibility.md`, `docs/migration-guide.md`.
- Consumer impact: maintainers and consumer projects get a documented update
  ritual and compatibility source of truth.
