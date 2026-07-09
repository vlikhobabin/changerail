# Changelog

Все публичные изменения OPSX фиксируются в этом файле.

Формат следует release discipline OPSX: версии используют semver, а breaking
changes помечаются префиксом `BREAKING:`.

## Unreleased

### Added
- Added release discipline docs: semver policy, compatibility notes and
  migration guide.
- Added initial release CI plan through OpenSpec change
  `add-release-ci-gate`.

### Changed
- Bumped pinned OpenSpec CLI `1.3.0` -> `1.3.1` in `bin/openspec` and refreshed
  `skills/openspec-*` via `openspec update` (sharper `contextFiles` guidance in
  apply-change/verify-change). Updated compatibility and lifecycle docs.

### Fixed
- none

### Breaking
- none

## 0.1.0 - 2026-07-08

### Added
- Initial public OPSX baseline: shared methodology, lifecycle skills, Claude
  command wrappers, OpenSpec lifecycle helpers, contract schemas, project
  templates, bootstrap, verify-project, drift gate and wiring smoke.

### Changed
- none

### Fixed
- none

### Breaking
- none
