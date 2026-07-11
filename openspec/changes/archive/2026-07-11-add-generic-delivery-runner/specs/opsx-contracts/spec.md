## ADDED Requirements

### Requirement: Delivery run record contract
OPSX MUST define a public `opsx.delivery-run.v1` contract for machine-readable
delivery run status and terminal outcomes.

#### Scenario: Runner writes status
- **WHEN** the delivery runner writes
  `<workspace>/.runtime/opsx/delivery-runs/<run-id>/status.json` by default
- **THEN** the JSON uses `opsx.delivery-run.v1` and includes card, phase,
  result, timestamps and command metadata
- **AND** the record includes `commit` when workspace `HEAD` is available

#### Scenario: Usage is unavailable
- **WHEN** the runner cannot observe token usage from the provider output
- **THEN** the run record explicitly reports usage as unavailable instead of
  guessing values
