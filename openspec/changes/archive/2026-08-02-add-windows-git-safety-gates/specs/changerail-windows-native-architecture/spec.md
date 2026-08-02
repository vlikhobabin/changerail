## ADDED Requirements

### Requirement: Windows wiring Git safety fixture matrix
The native Windows support model MUST include deterministic Git safety fixture
coverage for generated, symlink and junction wiring modes before those modes
are treated as safe to publish.

#### Scenario: Git safety matrix runs locally
- **WHEN** release baseline runs focused Windows wiring safety smoke
- **THEN** fixtures cover generated-copy, symlink fallback and junction fallback
  path classes
- **AND** each fixture records porcelain status, dry-run add and index
  inspection evidence

#### Scenario: Unsafe staging fails closed
- **WHEN** a fixture shows that Git would stage ChangeRail source, ignored
  runtime state, credentials or out-of-scope files
- **THEN** the smoke fails closed and reports the unsafe path class without
  exposing secret values

#### Scenario: Rename and uninstall remain bounded
- **WHEN** Windows wiring is renamed, refreshed, uninstalled or partially
  cleaned up in a fixture
- **THEN** only manifest-owned generated artifacts or current-run-owned link
  paths are modified
- **AND** project-owned files remain untouched and visible to Git safety checks
