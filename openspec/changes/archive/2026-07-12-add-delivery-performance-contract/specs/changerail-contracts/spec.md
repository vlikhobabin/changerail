## ADDED Requirements

### Requirement: Delivery run performance summary contract
ChangeRail MUST define schema-backed optional performance fields for
`changerail.delivery-run.v1` status records without weakening the required base
status contract.

#### Scenario: Runner writes performance fields
- **WHEN** a delivery runner status record includes performance data
- **THEN** the JSON remains valid against `schemas/changerail-delivery-run.schema.json`
- **AND** the record can include wall time, event counts, command counts,
  slow-command details, file-change counts, review timing and publish timing

#### Scenario: Performance data is unavailable
- **WHEN** a delivery runner cannot observe optional performance data
- **THEN** the status record remains valid without guessing those values
- **AND** the required base fields still include schema, card, phase, result,
  timestamps, command and usage availability

### Requirement: Delivery run usage breakdown contract
ChangeRail MUST allow delivery run records to expose available token usage
breakdowns while preserving explicit unknown semantics for unavailable usage.

#### Scenario: Usage breakdown is available
- **WHEN** provider output exposes cached input, uncached input, output or
  reasoning token counts
- **THEN** `changerail.delivery-run.v1` can represent those counts as
  non-negative integers under `usage`

#### Scenario: Usage total is derived downstream
- **WHEN** a status record contains input and output token counts but no
  explicit total
- **THEN** the contract allows metrics consumers to derive the display total
  without mutating the runtime record
