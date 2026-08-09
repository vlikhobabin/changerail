## Why

Repository knowledge catalog уже фиксирует source of truth, но пока не дает
детерминированного gate-а, который показывает drift, stale generated output или
опасные active references до передачи ambiguous findings агенту.

## What Changes

- Добавить read-only `bin/changerail-maintenance scan`, который генерирует один
  schema-bound JSON report без LLM и без mutation.
- Расширить `changerail.maintenance-policy.v1` optional `scan` configuration:
  include/exclude globs, enabled detectors, severity threshold, timeout и
  per-detector options.
- Добавить core detectors для configured documentation universe, orphan records,
  local Markdown links/anchors, generated index freshness и forbidden active
  references.
- Опубликовать public schemas `changerail.maintenance-scan-report.v1` и
  `changerail.maintenance-detector-result.v1`.
- Добавить focused fixtures и smoke coverage для drift, stale generated output,
  orphan records, forbidden references и no-mutation behavior.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: adds deterministic maintenance scan
  behavior over catalog, policy and generated index contracts.
- `changerail-contracts`: adds public scan report and detector-result schema
  contracts and schema smoke coverage.

## Impact

- Affected code: `scripts/changerail_maintenance.py`,
  `scripts/changerail_repository_knowledge.py`, `bin/changerail-maintenance`,
  Windows wrapper smoke where relevant.
- Affected contracts: `schemas/changerail-maintenance-policy.schema.json`,
  new scan report/result schemas, `docs/changerail-contracts.md`.
- Affected tests/fixtures: `scripts/smoke-repository-knowledge.py`,
  `scripts/smoke-contract-schemas.py`, repository knowledge fixtures and
  focused scan fixtures.
