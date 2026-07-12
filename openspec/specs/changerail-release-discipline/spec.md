# changerail-release-discipline Specification

## Purpose

Зафиксировать release discipline для ChangeRail как самостоятельной публичной
технологии: semver, changelog, compatibility notes и migration notes.
## Requirements
### Requirement: Semantic version source

ChangeRail MUST publish the current project version in a root `VERSION` file using
semantic version format `MAJOR.MINOR.PATCH`.

#### Scenario: Maintainer checks current version
- **WHEN** a maintainer reads `VERSION`
- **THEN** the file contains exactly one semantic version string
- **AND** release docs explain how pre-1.0 and stable releases use semver

### Requirement: Changelog with breaking markers

ChangeRail MUST maintain a root `CHANGELOG.md` that records public changes by
version and marks breaking changes explicitly.

#### Scenario: Consumer checks whether an update is breaking
- **WHEN** a consumer reads changelog entries for a target ChangeRail version
- **THEN** any breaking workflow, schema, template, skill, command or helper
  change is marked with a `BREAKING:` prefix
- **AND** non-breaking additions and fixes are grouped separately from breaking
  entries

### Requirement: Tool compatibility notes
ChangeRail MUST document compatibility expectations for Codex CLI, Claude Code and
OpenSpec CLI.
Compatibility notes MUST document executable MCP dependency pins and their
tracked integrity source and trusted setup verification.

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
- **AND** the notes identify the `verify-project`/`npm view` trusted setup
  check that compares tracked integrity with npm registry metadata

### Requirement: Migration notes between versions
ChangeRail MUST maintain migration notes for version-to-version updates that affect
consumer projects or operator workflow.
Release discipline MUST describe how maintainers update executable dependency
pins in a reviewable way.
Release verification MUST include security disclosure policy and public-safety
checks for public ChangeRail releases.

#### Scenario: Consumer updates ChangeRail
- **WHEN** a consumer moves from one ChangeRail version to another
- **THEN** migration notes describe required update steps, verification gates
  and rollback considerations
- **AND** migration examples use public generic paths only

#### Scenario: Maintainer updates executable dependency pins
- **WHEN** a release updates npm MCP package pins or CI action SHAs
- **THEN** release docs describe the update command, verification commands and
  review expectations

#### Scenario: Release checks security disclosure policy
- **WHEN** a maintainer prepares a public ChangeRail release
- **THEN** release verification confirms that tracked security disclosure
  policy exists and is linked from public docs
- **AND** public-safety scans pass for the final tracked payload

### Requirement: Security disclosure policy
ChangeRail MUST maintain a tracked public security disclosure policy for
reporting vulnerabilities without publishing sensitive details.

#### Scenario: Public user reports a vulnerability
- **WHEN** a public user reads `SECURITY.md`
- **THEN** the policy identifies supported versions, preferred private
  disclosure channel and report content guidelines
- **AND** it tells reporters not to include secrets, credentials, exploit
  payloads or private workspace details in public issues

### Requirement: Product rename migration notes
ChangeRail release discipline MUST treat the OPSX to ChangeRail rename as a
breaking migration for consumers.

#### Scenario: Consumer reads rename release notes
- **WHEN** a consumer reads the release notes for the rename version
- **THEN** the notes mark source path, command namespace, skill namespace,
  helper and schema namespace changes as breaking where applicable
- **AND** the notes describe `/opt/changerail` as the canonical source-of-truth
  path

#### Scenario: Operator renames the GitHub repository
- **WHEN** the GitHub repository is renamed from `opsx` to `changerail`
- **THEN** migration docs describe updating local `origin` to the new
  repository URL
- **AND** old repository URLs are treated as compatibility redirects, not
  canonical documentation targets
