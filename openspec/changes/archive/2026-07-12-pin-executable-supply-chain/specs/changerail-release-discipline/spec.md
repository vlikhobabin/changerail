## MODIFIED Requirements

### Requirement: Tool compatibility notes
Compatibility notes MUST document executable MCP dependency pins and their
tracked integrity source and trusted setup verification.

#### Scenario: Maintainer reviews MCP supply-chain pins
- **WHEN** a maintainer reads ChangeRail compatibility notes
- **THEN** the notes identify the exact npm MCP package pins and the tracked
  integrity lock used to audit them
- **AND** the notes identify the `verify-project`/`npm view` trusted setup
  check that compares tracked integrity with npm registry metadata

### Requirement: Migration notes between versions
Release discipline MUST describe how maintainers update executable dependency
pins in a reviewable way.

#### Scenario: Maintainer updates executable dependency pins
- **WHEN** a release updates npm MCP package pins or CI action SHAs
- **THEN** release docs describe the update command, verification commands and
  review expectations
