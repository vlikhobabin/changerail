## ADDED Requirements

### Requirement: Maintenance baseline and waiver contract
ChangeRail MUST publish a JSON Schema Draft 2020-12 baseline contract for
`.changerail/maintenance-baseline.yaml` with separate `accepted` and `waivers`
collections. Acceptance MUST be keyed by lifecycle finding identity
fingerprint. Each waiver MUST include `owner`, `reason` and either an
ISO-8601 `expires_at` or `review_after` boundary.

#### Scenario: Baseline acceptance is schema backed
- **WHEN** `.changerail/maintenance-baseline.yaml` contains accepted finding
  identities
- **THEN** `bin/changerail-maintenance accept-baseline --write` writes only the
  baseline file
- **AND** the resulting file validates against the maintenance baseline schema

#### Scenario: Expired waiver does not suppress finding
- **WHEN** a lifecycle finding matches a waiver whose `expires_at` or
  `review_after` boundary is in the past
- **THEN** the lifecycle output keeps the finding open
- **AND** the expired waiver is reported as not suppressing the finding

#### Scenario: Active date-only waiver remains report-valid
- **WHEN** a lifecycle finding matches a waiver with a future date-only
  `expires_at` or `review_after` boundary
- **THEN** the lifecycle output marks the finding waived
- **AND** `suppressed_until` is normalized to a report-valid UTC date-time

### Requirement: Maintenance baseline preview defaults
ChangeRail maintenance baseline operations MUST be read-only by default and
MUST mutate tracked baseline content only when explicit `--write` is supplied.

#### Scenario: Accept baseline preview does not mutate files
- **WHEN** `bin/changerail-maintenance accept-baseline --json` runs without
  `--write`
- **THEN** it emits a schema-valid preview artifact or JSON summary
- **AND** the repository working tree content is not modified

#### Scenario: Accept baseline write is scoped
- **WHEN** `bin/changerail-maintenance accept-baseline --write` runs
- **THEN** the only tracked file it creates or updates is
  `.changerail/maintenance-baseline.yaml`

### Requirement: Maintenance triage annotations
ChangeRail MUST accept schema-bound maintenance triage annotations and MUST NOT
invoke an LLM as part of `triage` command execution.

#### Scenario: Triage validates supplied annotations
- **WHEN** `bin/changerail-maintenance triage --annotations <path> --json`
  receives valid annotation JSON
- **THEN** the command emits normalized schema-valid annotations
- **AND** no LLM or external model process is invoked

#### Scenario: Invalid triage fails closed
- **WHEN** supplied triage annotations violate the schema
- **THEN** the command exits non-zero
- **AND** it emits one machine-readable diagnostic document

### Requirement: Maintenance board card bridge
ChangeRail MUST provide a preview-first board-card bridge from lifecycle
findings to ChangeRail board cards. Written cards MUST carry exactly one
machine-readable line `Maintenance Origin: <sha256 fingerprint>`.

#### Scenario: Card bridge preview does not mutate board
- **WHEN** `bin/changerail-maintenance cards --json` runs without `--write`
- **THEN** preview artifacts are retained under ignored
  `.runtime/changerail/maintenance/`
- **AND** no tracked board card is created or updated

#### Scenario: Card bridge writes exact origin marker
- **WHEN** `bin/changerail-maintenance cards --write` creates a board card for
  a lifecycle finding
- **THEN** the tracked card contains exactly one line
  `Maintenance Origin: <sha256 fingerprint>`
- **AND** the card title, summary and evidence references contain only
  sanitized repository-relative metadata

#### Scenario: Card bridge rejects unsafe report material
- **WHEN** `bin/changerail-maintenance cards --write` receives a lifecycle
  report whose open finding contains an absolute path, unsafe local path shape,
  secret-like `finding.path` or other secret-like card material
- **THEN** the command exits non-zero
- **AND** no tracked board card is created or updated for that finding

#### Scenario: Card bridge deduplicates across board lanes
- **WHEN** a lifecycle finding has the same fingerprint as a card already
  present under `openspec/board/1.backlog`, `2.todo`, `3.inprogress`, `4.done`
  or `5.canceled`
- **THEN** `bin/changerail-maintenance cards --write` updates that existing
  card evidence summary
- **AND** it does not create another card for the same identity
