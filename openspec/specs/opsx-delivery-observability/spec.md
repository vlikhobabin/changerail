# opsx-delivery-observability Specification

## Purpose
Зафиксировать OPSX observability для delivery run records, review-cycle
history, metrics и CSV reporting без скрейпинга свободного текста логов.

## Requirements
### Requirement: Review cycle history
OPSX MUST support retained review-cycle evidence without replacing the latest
canonical verdict required by publish.

#### Scenario: No-go is followed by re-review
- **WHEN** a first review cycle returns `no-go` and a later cycle returns `go`
- **THEN** metrics can still read the earlier `no-go` findings from runtime
  review-cycle evidence
- **AND** the historical cycle retains finding ids, severities and summaries or
  an immutable per-cycle verdict snapshot path

### Requirement: Delivery metrics tool
OPSX MUST provide a tracked metrics tool that reads structured delivery run
records and review-cycle evidence instead of scraping free-text logs.

#### Scenario: Operator requests aggregate metrics
- **WHEN** the metrics tool reads a directory of run records and review evidence
- **THEN** it prints per-run and aggregate results including first-pass go rate,
  finding counts by severity, acceptance outcomes, wall-time and available token
  usage

### Requirement: CSV metrics output
The metrics tool MUST support CSV output for per-run delivery metrics.

#### Scenario: Operator requests CSV
- **WHEN** the operator passes the CSV output option
- **THEN** the tool emits a stable header and one row per run with missing
  optional fields rendered explicitly as `unknown`

### Requirement: Unknown optional metrics
Metrics output MUST represent unavailable optional fields explicitly.

#### Scenario: Usage is missing
- **WHEN** a run record does not contain token usage
- **THEN** the metrics output reports token usage as `unknown`
