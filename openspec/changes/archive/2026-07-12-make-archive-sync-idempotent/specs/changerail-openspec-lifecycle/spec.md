## ADDED Requirements

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
