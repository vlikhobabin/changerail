## ADDED Requirements

### Requirement: Native Windows smoke matrix runner
ChangeRail MUST provide a non-interactive Windows smoke matrix runner that
aggregates deterministic local fixtures and optional live host checks for the
native Windows support contract.

#### Scenario: Local matrix runs without live hosts
- **WHEN** a maintainer runs `python3 scripts/smoke-windows-matrix.py`
- **THEN** the command executes the mandatory platform-neutral Windows fixture
  checks without contacting Windows lab hosts
- **AND** it exits non-zero when any mandatory local matrix item fails
- **AND** it writes or prints a structured summary using schema
  `changerail.windows-smoke-matrix.v1`

#### Scenario: Matrix includes focused fixture commands
- **WHEN** the local matrix runs
- **THEN** it covers `.cmd` wrapper inventory and process semantics
- **AND** it covers generated-copy bootstrap, ownership, stale copy detection,
  refresh and project-owned divergence fixtures
- **AND** it covers verifier, drift and Git safety behavior for generated,
  symlink and junction path classes

### Requirement: Live two-host smoke contract
The Windows smoke matrix MUST support explicit live execution against both
generic Windows lab hosts while keeping private connection data ignored.

#### Scenario: Live matrix uses ignored inventory
- **WHEN** a maintainer runs the matrix with live host execution enabled
- **THEN** it reads Windows host connection data from an ignored inventory path
- **AND** it requires exactly `windows-host-a` and `windows-host-b` as tracked
  host ids
- **AND** it refuses to run when the inventory path is not ignored by Git

#### Scenario: Host coverage is incomplete
- **WHEN** live matrix execution cannot complete for one or both generic hosts
- **THEN** the matrix report records a sanitized blocker or caveat for each
  missing or failed host
- **AND** ChangeRail MUST NOT claim full live host coverage from that run

### Requirement: Disposable workspace and cleanup coverage
The Windows smoke matrix MUST use disposable workspaces and prove idempotent
cleanup for deterministic and live host fixtures.

#### Scenario: Local fixtures create disposable projects
- **WHEN** the local matrix creates consumer or wiring fixtures
- **THEN** it creates them under ignored `.runtime/changerail/` paths
- **AND** repeated cleanup removes only current-run-owned or generated-owned
  artifacts
- **AND** project-owned files remain visible to Git safety checks

#### Scenario: Repeat run follows cleanup
- **WHEN** the matrix is run in repeat mode
- **THEN** it executes the same matrix after cleanup
- **AND** it reports any status mismatch instead of presenting the result as
  repeatable

### Requirement: Windows fallback matrix coverage
The Windows smoke matrix MUST cover generated-copy default behavior and bounded
symlink and junction fallback conditions.

#### Scenario: Generated default remains least privilege
- **WHEN** the local matrix checks generated-copy wiring
- **THEN** it verifies that native Windows default wiring does not require
  Developer Mode, administrator elevation, symlink privilege or junction
  traversal
- **AND** generated-owned artifacts have source identity and digest evidence

#### Scenario: Fallback proof is fail closed
- **WHEN** the matrix checks symlink or junction fallback behavior
- **THEN** positive fixtures include concrete source metadata and per-check
  evidence
- **AND** negative fixtures fail when privilege, Developer Mode, cleanup, Git
  status, dry-run add or index evidence is missing or unsafe

### Requirement: Public-safe smoke reports
The Windows smoke matrix MUST retain raw command output only in ignored runtime
state and keep tracked summaries sanitized.

#### Scenario: Matrix writes retained report
- **WHEN** a matrix run completes
- **THEN** the retained report is written under ignored
  `.runtime/changerail/windows-smoke/`
- **AND** tracked cards, docs or specs cite only command class, generic host id,
  outcome and ignored evidence path

#### Scenario: Sanitizer protects public surface
- **WHEN** matrix diagnostics include private hostnames, SSH targets,
  credential-like values or machine-local Windows paths
- **THEN** the public summary redacts those values
- **AND** public-surface scan fails if private host identity or credential
  content reaches tracked files
