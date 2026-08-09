## Why

После появления catalog и policy contracts maintainers нужен deterministic
helper surface, чтобы валидировать их и держать readable generated index свежим
без agent invocation. CLI остается opt-in и read-only, пока operator явно не
передал write flag.

## What Changes

- Добавляются `bin/changerail-maintenance` и `bin/changerail-maintenance.cmd`
  wrappers через shared Python runtime.
- Добавляются catalog validation commands с configurable catalog/policy paths.
- Добавляется `render-index --check|--write` со stable ordering и idempotent
  output.
- Добавляется smoke coverage для validation, check-mode no-mutation,
  write-mode idempotence и POSIX/native Windows entrypoints.
- Добавляются minimal dogfood catalog и generated index для canonical docs
  ChangeRail.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: добавляются shared-runtime CLI entrypoints
  и deterministic generated index contract.

## Impact

- `bin/changerail-maintenance`
- `bin/changerail-maintenance.cmd`
- `scripts/changerail_maintenance.py`
- `scripts/changerail_repository_knowledge.py`
- `scripts/smoke-repository-knowledge.py`
- `scripts/smoke-windows-entrypoints.py`
- `.changerail/knowledge.yaml`
- `.changerail/maintenance.yaml`
- `.changerail/KNOWLEDGE.md`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-repository-knowledge/spec.md`
