# Определить repository knowledge contract

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`060-repository-knowledge-maintenance`

## Series Index
`01`

## Planning State
published; archived OpenSpec changes, retained verification evidence and fresh
review gate are complete

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
- `establish-repository-knowledge-contract`
- `add-knowledge-catalog-cli-and-index`

## Verify
- Fast-forward artifacts validated:
  `./bin/openspec validate establish-repository-knowledge-contract --strict`;
  `./bin/openspec validate add-knowledge-catalog-cli-and-index --strict`;
  `git diff --check`.
- Delivery verification passed. Retained evidence index:
  `.runtime/changerail/evidence/060-01-establish-repository-knowledge-contract/index.json`.
- `python3 scripts/smoke-repository-knowledge.py` -> passed.
- `python3 scripts/smoke-contract-schemas.py` -> passed.
- `bin/changerail-maintenance validate-catalog` -> passed.
- `bin/changerail-maintenance render-index --check` -> passed.
- `python3 scripts/smoke-windows-entrypoints.py` -> passed.
- `./bin/openspec validate establish-repository-knowledge-contract --strict` -> passed.
- `./bin/openspec validate add-knowledge-catalog-cli-and-index --strict` -> passed.
- `./bin/openspec validate --all --strict` -> passed.
- `python3 scripts/public-surface-scan.py` -> passed.
- `git diff --check` -> passed.
- Post-review rescue attempt 1 fixed `R1` from review cycle 1:
  invalid `bin/changerail-maintenance validate-catalog --json` failure output
  now emits exactly one parseable JSON object with `ok: false` and diagnostics.
  Retained evidence ids:
  `rescue-invalid-json-diagnostic`, `rescue-repository-knowledge-smoke`,
  `rescue-contract-schemas-smoke`, `rescue-windows-entrypoints-smoke`,
  `rescue-openspec-all-strict`, `rescue-public-surface-scan`,
  `rescue-render-index-check`, `rescue-diff-check`.

## Archive
- `openspec/changes/archive/2026-08-09-establish-repository-knowledge-contract/`
- `openspec/changes/archive/2026-08-09-add-knowledge-catalog-cli-and-index/`

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
- `openspec/changes/archive/2026-08-09-establish-repository-knowledge-contract/`

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
- `openspec/changes/archive/2026-08-09-add-knowledge-catalog-cli-and-index/`

## Result
Delivered: repository knowledge and maintenance policy schemas, YAML loader,
public-safe fixtures, dogfood catalog/index, CLI wrappers, deterministic
`render-index`, docs and smoke coverage are implemented and published through
the review-gated ChangeRail flow.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and
published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- `2026-08-09T12:35:25Z` — story extracted from broad maintenance harness card.
- `2026-08-09T13:16:00Z` — readiness review accepted; moved to `2.todo` for
  supervised single-card delivery.
- `2026-08-09T13:21:08Z` — internal `ff` phase created apply-ready OpenSpec
  artifacts for both card-owned changes; moving to `3.inprogress` for delivery.
- `2026-08-09T13:33:05Z` — implemented both changes, synced main specs,
  archived OpenSpec changes and captured delivery verification evidence; ready
  for independent review.
- `2026-08-09T13:39:11Z` — independent review cycle 1 returned `no-go` with
  blocker `R1`: invalid `validate-catalog --json` failure output emitted two
  JSON objects.
- `2026-08-09T13:43:04Z` — same-card rescue attempt 1 fixed `R1`, added smoke
  assertion for invalid JSON-mode diagnostics and recaptured verification
  evidence; fresh re-review required.
- 2026-08-09T13:51:15Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
