# Changelog

Все публичные изменения ChangeRail фиксируются в этом файле.

Формат следует release discipline ChangeRail: версии используют semver, а breaking
changes помечаются префиксом `BREAKING:`.

## Unreleased

### Added
- Added release discipline docs: semver policy, compatibility notes and
  migration guide.
- Added initial release CI plan through OpenSpec change
  `add-release-ci-gate`.
- Added `bin/changerail-delivery-runner` for supervised single-card
  non-interactive delivery with structured runtime status records.
- Added `bin/changerail-delivery-metrics` for aggregate metrics from delivery
  run records and review-cycle history.
- Added public contract schemas for delivery run records and review-cycle
  history, plus schema-backed validation for review verdict and delivery
  manifest helpers.
- Added delivery manifest derivation/finalization helpers and review freshness
  fingerprint coverage.
- Added short daily aliases `$chrl-*` and `/chrl:*` while preserving canonical
  `changerail` runtime names.
- Added public-surface scan helper coverage for current files and reachable
  history.
- Added local release baseline command `scripts/run-release-baseline.py`,
  inventory-based Python compile checks, contract schema smoke, pinned
  `ruff`/`jsonschema` release tooling and focused runner/metrics/fingerprint
  CI smokes.

### Changed
- Renamed the public product/toolchain identity from OPSX to ChangeRail across
  docs, lifecycle skills, Claude commands, helpers, schemas, templates and
  smoke checks.
- Bumped pinned OpenSpec CLI `1.3.0` -> `1.3.1` in `bin/openspec` and refreshed
  `skills/openspec-*` via `openspec update` (sharper `contextFiles` guidance in
  apply-change/verify-change). Updated compatibility and lifecycle docs.
- Clarified review-gated publish finalization: delivery leaves reviewed cards in
  `3.inprogress`, and publish records deterministic board metadata after a
  fresh `go` verdict and scoped commit.
- Documented `scripts/smoke-drift.py` as an inventory-driven gate; release CI
  and the local baseline use generated public-safe fixtures.

### Fixed
- Fixed release CI drift where runner, metrics, review fingerprint, schema
  validation and lint coverage were not all part of the mandatory gate.
- Fixed stale public documentation that still treated tracked bootstrap,
  verify, template and script surfaces as planned work.

### Breaking
- BREAKING: OPSX source path, command namespace, skill namespace, helper names,
  runtime namespace and schema ids are renamed to ChangeRail. Consumers must
  migrate `/opt/opsx`, `/opsx:*`, `$opsx-*`, `bin/opsx-*`,
  `.runtime/opsx` and `opsx.*.v1` wiring to the ChangeRail equivalents.

## 0.1.0 - 2026-07-08

### Added
- Initial public ChangeRail baseline: shared methodology, lifecycle skills, Claude
  command wrappers, OpenSpec lifecycle helpers, contract schemas, project
  templates, bootstrap, verify-project, drift gate and wiring smoke.

### Changed
- none

### Fixed
- none

### Breaking
- none
