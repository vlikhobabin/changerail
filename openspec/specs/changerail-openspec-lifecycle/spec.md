# changerail-openspec-lifecycle Specification

## Purpose
Зафиксировать публичную ChangeRail surface для OpenSpec lifecycle skills и wrapper
`bin/openspec`, включая provenance, pin версии CLI и правила будущего sync.

## Requirements
### Requirement: OpenSpec lifecycle skills
ChangeRail MUST provide tracked OpenSpec lifecycle skills under `skills/openspec-*`
for the OpenSpec actions used by ChangeRail delivery flows.

#### Scenario: Consumer project links OpenSpec skills
- **WHEN** a consumer project exposes ChangeRail skills through documented wiring
- **THEN** OpenSpec action skills are available from `skills/openspec-*`

### Requirement: OpenSpec skill provenance
ChangeRail MUST document the source, license and generated CLI version for imported
OpenSpec lifecycle skills.

#### Scenario: Maintainer reviews OpenSpec skill origin
- **WHEN** a maintainer inspects the OpenSpec lifecycle documentation
- **THEN** the documentation identifies the OpenSpec CLI source, MIT license
  and generated version used for the tracked skill files

### Requirement: Pinned OpenSpec wrapper
ChangeRail MUST provide `bin/openspec` as a tracked wrapper that executes a pinned
OpenSpec CLI version and supports an explicit version override.

#### Scenario: Consumer invokes the OpenSpec wrapper
- **WHEN** `/opt/changerail/bin/openspec validate --all` is run from an ChangeRail project
- **THEN** the wrapper executes the pinned OpenSpec CLI package unless
  `OPENSPEC_VERSION` overrides the pin

### Requirement: OpenSpec compatibility notes
ChangeRail MUST document the OpenSpec CLI pin and the update policy for generated
OpenSpec lifecycle skills.

#### Scenario: Maintainer updates OpenSpec CLI
- **WHEN** the pinned OpenSpec CLI version changes
- **THEN** compatibility notes and skill provenance are updated in the same
  delivery scope

### Requirement: Archive duplicate sync diagnostics
The ChangeRail OpenSpec wrapper MUST make already-synced archive conflicts
diagnostic instead of silently looking successful.

#### Scenario: Archive sees duplicate already-synced requirement
- **WHEN** `bin/openspec archive <change> --yes` prints that an `ADDED`
  requirement already exists and aborts without changing files
- **THEN** the wrapper exits non-zero
- **AND** the diagnostic tells the operator to rerun with `--skip-specs` only
  after confirming the main specs were already synced intentionally

#### Scenario: Archive is explicitly told to skip specs
- **WHEN** the operator runs `bin/openspec archive <change> --yes --skip-specs`
- **THEN** the wrapper does not add duplicate-sync diagnostics
- **AND** the command result is delegated to the pinned OpenSpec CLI
