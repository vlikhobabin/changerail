## ADDED Requirements

### Requirement: Semantic version source

OPSX MUST publish the current project version in a root `VERSION` file using
semantic version format `MAJOR.MINOR.PATCH`.

#### Scenario: Maintainer checks current version
- **WHEN** a maintainer reads `VERSION`
- **THEN** the file contains exactly one semantic version string
- **AND** release docs explain how pre-1.0 and stable releases use semver

### Requirement: Changelog with breaking markers

OPSX MUST maintain a root `CHANGELOG.md` that records public changes by
version and marks breaking changes explicitly.

#### Scenario: Consumer checks whether an update is breaking
- **WHEN** a consumer reads changelog entries for a target OPSX version
- **THEN** any breaking workflow, schema, template, skill, command or helper
  change is marked with a `BREAKING:` prefix
- **AND** non-breaking additions and fixes are grouped separately from breaking
  entries

### Requirement: Tool compatibility notes

OPSX MUST document compatibility expectations for Codex CLI, Claude Code and
OpenSpec CLI.

#### Scenario: Operator prepares to update local tools
- **WHEN** an operator reviews OPSX compatibility notes
- **THEN** the notes identify Codex CLI, Claude Code and OpenSpec CLI support
  status
- **AND** the OpenSpec CLI compatibility note references the pin used by
  `bin/openspec`

### Requirement: Migration notes between versions

OPSX MUST maintain migration notes for version-to-version updates that affect
consumer projects or operator workflow.

#### Scenario: Consumer updates OPSX
- **WHEN** a consumer moves from one OPSX version to another
- **THEN** migration notes describe required update steps, verification gates
  and rollback considerations
- **AND** migration examples use public generic paths only
