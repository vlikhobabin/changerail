## ADDED Requirements

### Requirement: Delivery performance observability contract
ChangeRail delivery observability MUST describe machine-readable performance
summary fields that explain long delivery runs without scraping free-text logs.

#### Scenario: Maintainer reads delivery status
- **WHEN** `status.json` contains performance summary fields
- **THEN** those fields identify available wall time, command execution count,
  agent message count, file change count, slowest commands, review cycle timing
  and publish latency
- **AND** missing optional timing fields are treated as unknown rather than zero

#### Scenario: Contract docs describe timing semantics
- **WHEN** maintainers read delivery-run contract documentation
- **THEN** the docs distinguish required status fields from best-effort timing
  and usage breakdown fields
- **AND** the docs state that raw runtime logs remain ignored state
