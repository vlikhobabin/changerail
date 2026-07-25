## Why

Типовой локальный remediation для runner auth readiness - связать project
`.codex/auth.json` с уже authenticated Codex home, но bootstrap не должен
молчаливо копировать или раскрывать credentials. Явный opt-in режим делает
безопасный путь discoverable без ослабления public-surface safety.

## What Changes

- Добавить явный bootstrap option для создания project-local ignored
  `.codex/auth.json` symlink.
- Отказывать при missing auth source и не читать/не печатать credential
  contents.
- Сохранить default bootstrap credential-free и public-safe.
- Убедиться, что generated ignore policy продолжает держать `.codex/auth.json`
  untracked.

## Capabilities

### New Capabilities

### Modified Capabilities
- `changerail-project-bootstrap`: bootstrap поддерживает explicit opt-in local
  Codex auth link для generated consumer projects.

## Impact

- Затрагивает `bin/bootstrap-project`, bootstrap docs и bootstrap smoke
  coverage.
- Не вводит credential copying или tracked machine-local auth state.
