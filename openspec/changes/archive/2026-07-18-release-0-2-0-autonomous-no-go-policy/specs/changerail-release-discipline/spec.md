## ADDED Requirements

### Requirement: Release publication bundle
ChangeRail release discipline MUST publish each public release as a coherent
versioned bundle that includes version source, changelog entries, migration
notes and compatibility notes.

#### Scenario: Maintainer publishes a pre-stable minor release
- **WHEN** a maintainer prepares a pre-stable minor release
- **THEN** `VERSION` MUST contain the target semantic version
- **AND** `CHANGELOG.md` MUST include a dated section for that version
- **AND** migration guide MUST include a version-to-version entry or explicitly
  say that no consumer action is required

#### Scenario: Release has no tool compatibility changes
- **WHEN** a release changes workflow policy without changing executable tool
  pins
- **THEN** compatibility notes MUST still identify the current ChangeRail
  version
- **AND** they MUST not imply that MCP, Codex, Claude or OpenSpec pins changed

## MODIFIED Requirements

### Requirement: Migration notes between versions
ChangeRail MUST maintain migration notes for version-to-version updates that affect
consumer projects or operator workflow.
Workflow contract changes MUST have migration notes even when symlink-based
consumer projects do not need tracked file rewiring.
Release discipline MUST describe how maintainers update executable dependency
pins in a reviewable way.
Release verification MUST include security disclosure policy and public-safety
checks for public ChangeRail releases.

#### Scenario: Consumer updates ChangeRail
- **WHEN** a consumer moves from one ChangeRail version to another
- **THEN** migration notes describe required update steps, verification gates
  and rollback considerations
- **AND** migration examples use public generic paths only

#### Scenario: Consumer updates workflow policy only
- **WHEN** a release changes lifecycle skill behavior, review/publish gates or
  autonomous agent policy without changing consumer tracked files
- **THEN** migration notes describe session restart, verification commands and
  local-copy refresh steps
- **AND** changelog marks breaking workflow contract changes with `BREAKING:`

#### Scenario: Maintainer updates executable dependency pins
- **WHEN** a release updates npm MCP package pins or CI action SHAs
- **THEN** release docs describe the update command, verification commands and
  review expectations

#### Scenario: Release checks security disclosure policy
- **WHEN** a maintainer prepares a public ChangeRail release
- **THEN** release verification confirms that tracked security disclosure
  policy exists and is linked from public docs
- **AND** public-safety scans pass for the final tracked payload
