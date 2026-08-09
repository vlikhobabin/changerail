## Why

Repository knowledge нельзя безопасно поддерживать в consumer projects, пока
catalog records, classifications, ownership и freshness поля не имеют stable
public shape. Этот change фиксирует opt-in contract до добавления
deterministic maintenance checks и agent triage.

## What Changes

- Добавляются public JSON Schemas для repository knowledge catalog и
  maintenance policy contracts.
- Добавляется shared Python loading/validation logic: YAML читается через
  PyYAML, затем валидируется JSON Schema Draft 2020-12 и возвращает structured
  diagnostics.
- Фиксируется safe repository-relative path semantics для catalog records и
  policy configuration.
- Добавляются public-safe valid/invalid fixtures для catalog/policy validation.
- Документируются tracked default paths, null/empty semantics,
  classifications и backward-compatible opt-in behavior.

## Capabilities

### New Capabilities
- `changerail-repository-knowledge`: opt-in repository knowledge catalog и
  maintenance policy contracts, validation и public-safe fixtures.

### Modified Capabilities
- `changerail-contracts`: published schema ids для repository knowledge и
  maintenance policy входят в ChangeRail public contracts.

## Impact

- `schemas/changerail-repository-knowledge.schema.json`
- `schemas/changerail-maintenance-policy.schema.json`
- `scripts/changerail_repository_knowledge.py`
- `scripts/smoke-repository-knowledge.py`
- `scripts/smoke-contract-schemas.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-repository-knowledge/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `.changerail/knowledge.yaml`
- `.changerail/maintenance.yaml`
