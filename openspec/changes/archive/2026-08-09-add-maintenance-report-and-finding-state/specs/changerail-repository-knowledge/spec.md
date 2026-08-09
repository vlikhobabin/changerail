## ADDED Requirements

### Requirement: Maintenance lifecycle report contract
ChangeRail MUST publish a JSON Schema Draft 2020-12 lifecycle report contract
with schema id `changerail.maintenance-report.v1`. The report MUST be
normalized from a complete schema-valid `changerail.maintenance-scan-report.v1`
source and MUST contain run metadata, source scan metadata, detector summary
and normalized lifecycle findings.

#### Scenario: Complete scan normalizes to lifecycle report
- **WHEN** `bin/changerail-maintenance report --json` runs against valid
  repository knowledge maintenance configuration
- **THEN** stdout contains exactly one `changerail.maintenance-report.v1` JSON
  document
- **AND** every normalized finding contains `fingerprint`,
  `evidence_fingerprint`, `detector`, `rule`, `severity`, `confidence`, `path`,
  `evidence_refs`, `remediation`, `first_seen`, `owner`, `risk_class` and
  lifecycle `status`

#### Scenario: Invalid source scan is rejected
- **WHEN** lifecycle normalization receives an incomplete or schema-invalid
  `changerail.maintenance-scan-report.v1` source
- **THEN** the command exits non-zero
- **AND** the emitted lifecycle report is marked incomplete with a blocker
  diagnostic instead of silently accepting partial detector output

### Requirement: Maintenance finding identity
ChangeRail MUST compute each lifecycle finding identity from canonical JSON over
`identity_version`, detector result id, finding rule/code and normalized
repository-relative subject. The public fingerprint form MUST be
`sha256:<lowercase-hex>`.

#### Scenario: Volatile finding fields do not change identity
- **WHEN** a repeated scan observes the same detector, rule and normalized
  subject with a different message, severity, timestamp or workspace root
- **THEN** the lifecycle finding keeps the same `fingerprint`
- **AND** identity material does not include the volatile field values

#### Scenario: Subject change changes identity
- **WHEN** a repeated scan observes the same detector and rule for a different
  normalized repository-relative subject
- **THEN** the lifecycle finding has a different `fingerprint`

### Requirement: Maintenance evidence fingerprint
ChangeRail MUST compute `evidence_fingerprint` separately from finding identity
using canonical JSON over sanitized material evidence. Evidence, raw message
text and timestamps MUST NOT be copied into identity material.

#### Scenario: Evidence change preserves identity
- **WHEN** a repeated scan observes the same finding identity with changed
  material evidence
- **THEN** the lifecycle finding keeps the same `fingerprint`
- **AND** `evidence_fingerprint` changes

#### Scenario: Unsafe evidence fails closed
- **WHEN** detector evidence contains an absolute path, traversal path, unknown
  local path shape or secret-like raw value
- **THEN** lifecycle normalization rejects that evidence with a blocker
  diagnostic
- **AND** the unsafe value is not copied into lifecycle output

### Requirement: Maintenance runtime state continuity
ChangeRail MUST keep maintenance lifecycle runtime state atomically below
`.runtime/changerail/maintenance/state.json`. Lifecycle normalization MUST be
read-only by default, and durable state updates MUST require explicit
`--write-state`.

#### Scenario: State write is explicit and atomic
- **WHEN** `bin/changerail-maintenance report --json --write-state` completes
  successfully
- **THEN** `.runtime/changerail/maintenance/state.json` is written atomically
- **AND** repeated runs with the restored state preserve `first_seen` for the
  same finding identity

#### Scenario: Custom state path stays in runtime root
- **WHEN** `bin/changerail-maintenance report --json --write-state --state <path>`
  receives a custom state path outside `.runtime/changerail/maintenance/`
- **THEN** lifecycle normalization exits non-zero
- **AND** the custom path is not written

#### Scenario: Default report does not claim continuity
- **WHEN** `bin/changerail-maintenance report --json` runs without restored
  state and without `--write-state`
- **THEN** repository tracked files are not modified
- **AND** each finding `first_seen` is the current observation
- **AND** the report metadata states that cross-run continuity was not restored

#### Scenario: Corrupt state fails closed
- **WHEN** `.runtime/changerail/maintenance/state.json` is corrupt or has an
  unsupported schema version
- **THEN** lifecycle normalization exits non-zero
- **AND** the existing state file is not replaced implicitly
