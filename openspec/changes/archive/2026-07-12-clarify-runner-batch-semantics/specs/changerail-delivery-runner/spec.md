## ADDED Requirements

### Requirement: Runner remains a single-card launcher
The tracked non-interactive delivery runner MUST treat its positional `card`
argument as one card path and MUST NOT imply that it owns multi-card queue
semantics unless explicit queue support is implemented.

#### Scenario: Operator reads runner help
- **WHEN** an operator runs `bin/changerail-delivery-runner run --help`
- **THEN** the help text describes the positional argument as a single
  repository-relative board card path

#### Scenario: Supervisor reads run status
- **WHEN** the runner writes
  `.runtime/changerail/delivery-runs/<run-id>/status.json`
- **THEN** the status record represents the single card passed to that runner
  invocation

### Requirement: Queue semantics belong to deliver or future queue runner
Documentation MUST state that directory or ordered-card queue handling belongs
to `$changerail-deliver` itself, or to a future queue-aware runner with
per-card records.

#### Scenario: Batch delivery is documented
- **WHEN** docs describe bounded batch delivery
- **THEN** they distinguish `$changerail-deliver <board-column>` from
  `bin/changerail-delivery-runner run <single-card>`
