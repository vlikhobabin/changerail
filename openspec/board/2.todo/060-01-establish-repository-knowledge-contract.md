# Определить repository knowledge contract

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`01`

## Planning State
deliver-ready; OpenSpec artifacts are delegated to the internal `ff` phase of
`$chrl-deliver`

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Harness Engineering repository knowledge system-of-record pattern.
- Diataxis documentation classifications and C4 architecture guidance.

## Summary
Определить opt-in tracked catalog и maintenance policy, их public schemas,
классификации, ownership/freshness semantics и deterministic generated index.
Consumer выбирает собственную структуру repository и docs directories.

## Acceptance
- Опубликованы schemas с ids `changerail.repository-knowledge.v1` и
  `changerail.maintenance-policy.v1`.
- Default tracked paths равны `.changerail/knowledge.yaml` и
  `.changerail/maintenance.yaml`; consumer может переопределить их через CLI.
- Catalog record содержит `path`, `status`, `type`, `owner`, `source_globs`,
  `verify`, `review_after` и `supersedes` с документированными null/empty
  semantics.
- `status` различает как минимум `active`, `historical`, `superseded` и
  `generated`; active record не может ссылаться на отсутствующий path.
- `type` поддерживает `tutorial`, `how-to`, `reference`, `explanation`,
  `architecture`, `adr`, `runbook`, `historical` и `generated` без привязки к
  directory layout.
- Repository-relative paths нормализуются без выхода за repository root;
  absolute paths и traversal отклоняются fail-closed.
- YAML загружается через PyYAML и валидируется JSON Schema Draft 2020-12 с
  `additionalProperties: false` на contract-owned objects.
- CLI helper `bin/changerail-maintenance` и native Windows wrapper поддерживают
  catalog validation и `render-index --check|--write` через shared Python runtime.
- `render-index` имеет stable ordering и idempotent output; default/check mode
  не меняет файл, `--write` меняет только configured generated index path.
- ChangeRail содержит public-safe valid/invalid fixtures и минимальный dogfood
  catalog для собственных canonical docs.
- Existing consumers без `.changerail/maintenance.yaml` остаются unaffected.

## Depends On
- none

## Change Set
- none yet

## Verify
- Schema fixtures for valid/invalid catalog and policy documents.
- Catalog path traversal and unknown-field negative fixtures.
- `render-index` idempotence and `--check` no-mutation smoke.
- POSIX/native Windows entrypoint smoke.
- `./bin/openspec validate --all --strict`.
- `python3 scripts/public-surface-scan.py`.
- `git diff --check`.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `schemas/`
- `requirements-runtime.txt`
- `bin/changerail-python`
- `docs/changerail-contracts.md`

## Change 1: `establish-repository-knowledge-contract`

### Why
Knowledge checks cannot be portable until catalog records, classifications,
ownership and freshness fields have a versioned public shape.

### Goal
Add schema-backed catalog/policy loading, public docs and fixtures without
forcing a repository directory structure.

### Acceptance
- Catalog and policy schemas enforce the acceptance above.
- Loader produces structured diagnostics for schema and safe-path failures.
- Existing projects remain opt-in and backward compatible.

### Depends On
- none

### Related
- `openspec/changes/establish-repository-knowledge-contract/`

## Change 2: `add-knowledge-catalog-cli-and-index`

### Why
Consumers need a deterministic way to validate the catalog and keep a readable
index fresh without invoking an agent.

### Goal
Add shared-runtime CLI entrypoints and idempotent index check/write behavior.

### Acceptance
- POSIX and native Windows helpers validate catalogs consistently.
- Index output is stable and check mode is read-only.
- Dogfood and fixture coverage prove the generated index contract.

### Depends On
- `establish-repository-knowledge-contract`

### Related
- `openspec/changes/add-knowledge-catalog-cli-and-index/`

## Result
Not started.

## Next
- Run `$chrl-deliver openspec/board/2.todo/060-01-establish-repository-knowledge-contract.md`.

## Log
- `2026-08-09T12:35:25Z` — story extracted from broad maintenance harness card.
- `2026-08-09T13:16:00Z` — readiness review accepted; moved to `2.todo` for
  supervised single-card delivery.
