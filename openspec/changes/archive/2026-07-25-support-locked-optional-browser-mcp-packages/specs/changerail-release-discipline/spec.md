## MODIFIED Requirements

### Requirement: Tool compatibility notes
ChangeRail MUST document compatibility expectations for Codex CLI, Claude Code and
OpenSpec CLI.
Compatibility notes MUST document executable MCP dependency pins and their
tracked integrity source and trusted setup verification.
Compatibility notes MUST identify approved optional browser MCP package pins
without presenting them as default bootstrap or root ChangeRail dependencies.

#### Scenario: Operator prepares to update local tools
- **WHEN** an operator reviews ChangeRail compatibility notes
- **THEN** the notes identify Codex CLI, Claude Code and OpenSpec CLI support
  status
- **AND** the OpenSpec CLI compatibility note references the pin used by
  `bin/openspec`

#### Scenario: Maintainer reviews MCP supply-chain pins
- **WHEN** a maintainer reads ChangeRail compatibility notes
- **THEN** the notes identify the exact npm MCP package pins and the tracked
  integrity lock used to audit them
- **AND** the notes identify approved optional browser MCP package pins
- **AND** the notes identify the `verify-project`/`npm view` trusted setup
  check that compares tracked integrity with npm registry metadata

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
- **WHEN** a release updates default or approved optional npm MCP package pins
  or CI action SHAs
- **THEN** release docs describe the update command, verification commands and
  review expectations
- **AND** optional browser MCP package upgrades are documented as explicit
  release work rather than silent consumer adoption changes

#### Scenario: Release checks security disclosure policy
- **WHEN** a maintainer prepares a public ChangeRail release
- **THEN** release verification confirms that tracked security disclosure
  policy exists and is linked from public docs
- **AND** public-safety scans pass for the final tracked payload
