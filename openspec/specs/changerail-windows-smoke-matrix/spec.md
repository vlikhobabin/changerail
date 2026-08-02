# changerail-windows-smoke-matrix Specification

## Purpose
Зафиксировать aggregate native Windows smoke matrix runner, deterministic local
fixture coverage, optional live two-host evidence and public-safe report
retention.
## Requirements
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

### Requirement: Windows smoke operations documentation
ChangeRail MUST document how maintainers run, interpret and retain evidence
from the Windows smoke matrix without exposing private Windows lab inventory.

#### Scenario: Maintainer runs local matrix
- **WHEN** a maintainer reads the Windows compatibility or release guidance
- **THEN** it shows the local deterministic matrix command
- **AND** it explains that local matrix success covers platform-neutral
  fixtures but does not by itself prove live host coverage

#### Scenario: Maintainer runs live matrix
- **WHEN** a maintainer reads the Windows live smoke guidance
- **THEN** it shows the live two-host command using ignored
  `internal/windows-lab-inventory.json`
- **AND** it identifies `windows-host-a` and `windows-host-b` as the only
  tracked host ids
- **AND** it explains repeat-after-cleanup expectations

#### Scenario: Maintainer interprets caveats
- **WHEN** a live host is unavailable or a matrix item fails
- **THEN** the documentation instructs maintainers to record a sanitized
  blocker or caveat before claiming host coverage
- **AND** it points to ignored `.runtime/changerail/windows-smoke/` reports as
  retained evidence

### Requirement: Windows smoke CI integration path
ChangeRail MUST document the boundary between current Linux release-baseline
matrix checks and future live Windows CI execution.

#### Scenario: Linux release baseline is documented
- **WHEN** release guidance describes local baseline checks
- **THEN** it includes the platform-neutral Windows smoke matrix command
- **AND** it states that this command does not require private Windows hosts

#### Scenario: Future Windows CI is documented
- **WHEN** Windows CI integration guidance is read
- **THEN** it describes runner-local secure inventory injection as future work
- **AND** it forbids committing SSH targets, usernames, credentials, private
  disposable roots or raw host output

### Requirement: Clean-clone Windows lifecycle proof
The Windows smoke matrix MUST include an explicit live clean-clone lifecycle
proof before ChangeRail claims full native Windows support.

#### Scenario: Live matrix runs clean-clone proof
- **WHEN** a maintainer runs `python3 scripts/smoke-windows-matrix.py --live`
- **THEN** the matrix runs a clean-clone lifecycle proof against
  `windows-host-a` and `windows-host-b`
- **AND** the proof starts each host from a disposable clone of the ChangeRail
  source ref under the ignored Windows lab root
- **AND** tracked summaries identify only generic host ids, command class,
  outcome and ignored runtime report paths

#### Scenario: Clean-clone proof exercises consumer lifecycle
- **WHEN** the clean-clone lifecycle proof runs on a host
- **THEN** it launches required native `.cmd` helpers from the cloned source
- **AND** it creates a generated-copy consumer project through
  `bootstrap-project.cmd`
- **AND** it runs `verify-project.cmd` against that consumer
- **AND** it confirms required ChangeRail skills, Claude commands and helper
  wiring are discoverable through project-local generated paths
- **AND** it refreshes generated wiring without modifying project-owned files
- **AND** it proves an explicit no-push staging fixture excludes ignored runtime
  files from the Git index

#### Scenario: Clean-clone proof cannot complete
- **WHEN** clone, bootstrap, verification, discovery, refresh or scoped staging
  fails on either host
- **THEN** the matrix reports the item as failed
- **AND** ChangeRail MUST record a sanitized blocker or caveat instead of
  claiming full native Windows support from that run
