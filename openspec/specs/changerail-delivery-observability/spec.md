# changerail-delivery-observability Specification

## Purpose
Зафиксировать ChangeRail observability для delivery run records, review-cycle
history, metrics и CSV reporting без скрейпинга свободного текста логов.
## Requirements
### Requirement: Review cycle history
ChangeRail MUST support retained review-cycle evidence without replacing the latest
canonical verdict required by publish.

#### Scenario: No-go is followed by re-review
- **WHEN** a first review cycle returns `no-go` and a later cycle returns `go`
- **THEN** metrics can still read the earlier `no-go` findings from runtime
  review-cycle evidence
- **AND** the historical cycle retains finding ids, severities and summaries or
  an immutable per-cycle verdict snapshot path

### Requirement: Delivery metrics tool
ChangeRail MUST provide a tracked metrics tool that reads structured delivery run
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

### Requirement: ChangeRail delivery observability paths
Delivery metrics and review-cycle observability MUST read post-rename runtime
records from the ChangeRail runtime namespace by default.

#### Scenario: Metrics command runs with defaults
- **WHEN** the delivery metrics helper runs without explicit input paths
- **THEN** it reads delivery runs from `.runtime/changerail/delivery-runs`
- **AND** it reads review history from `.runtime/changerail/reviews`

#### Scenario: Historical OPSX evidence exists
- **WHEN** old ignored `.runtime/opsx` evidence exists on disk
- **THEN** the post-rename defaults do not mutate or migrate that evidence

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

### Requirement: Runtime performance evidence comes from structured events
ChangeRail performance observability MUST derive delivery timing summaries from
structured runtime events and status records instead of free-text stdout/stderr
scraping.

#### Scenario: Runner summarizes command performance
- **WHEN** command lifecycle events are present in the child JSONL stream
- **THEN** the performance summary exposes command counts and slowest commands
  from structured event data

#### Scenario: Structured events are incomplete
- **WHEN** child JSONL events do not expose a timing dimension
- **THEN** observability output reports that optional dimension as unknown
  instead of parsing free-text logs

### Requirement: Delivery metrics reports performance summary
The delivery metrics helper MUST report structured performance details from
delivery run records and review-cycle evidence without scraping raw logs.

#### Scenario: Performance summary is available
- **WHEN** a delivery run record includes slow-command and review timing data
- **THEN** text metrics output includes a per-run slow-command summary and
  review-cycle timeline
- **AND** CSV output includes stable columns for those values

#### Scenario: Performance summary is unavailable
- **WHEN** a delivery run record lacks optional performance fields
- **THEN** metrics output renders the missing values as `unknown`

### Requirement: Delivery metrics reports token breakdown
The delivery metrics helper MUST report available token usage breakdowns and
derive display totals when enough structured usage data exists.

#### Scenario: Explicit total is absent
- **WHEN** a run record has `input_tokens` and `output_tokens` but no
  `total_tokens`
- **THEN** metrics output displays `total_tokens` as their sum

#### Scenario: Breakdown fields are available
- **WHEN** a run record has cached input, uncached input, output or reasoning
  token counts
- **THEN** metrics output displays those counts in text and CSV output

### Requirement: Queue observability records
ChangeRail delivery observability MUST treat aggregate queue status as a
structured metrics input alongside existing delivery run records and review
history.

#### Scenario: Queue status is available
- **WHEN** metrics read a `changerail.delivery-plan-status.v1` record
- **THEN** they can report queue result, card counts, child run references,
  terminal outcome and push/no-push mode without scraping raw logs

#### Scenario: Queue status is unavailable
- **WHEN** only existing child delivery run records are available
- **THEN** existing delivery metrics behavior remains compatible
- **AND** missing queue-level values are rendered as `unknown`

### Requirement: Queue metrics from structured records
The delivery metrics helper MUST read aggregate queue status and child delivery
run records to report queue outcomes without parsing arbitrary text.

#### Scenario: Queue status is present
- **WHEN** metrics receive a queue status directory or default queue runtime
  path containing `changerail.delivery-plan-status.v1` records
- **THEN** metrics report queue id, result, terminal outcome, completed cards,
  blocked/no-go cards, child run ids and push/no-push mode

#### Scenario: Child records provide details
- **WHEN** a queue status references child delivery run records
- **THEN** metrics use the existing child record and review-cycle fields for
  token usage, timing, findings and acceptance details

#### Scenario: Queue details are missing
- **WHEN** queue status is missing optional timing or child references
- **THEN** metrics render those values as `unknown`

### Requirement: Queue runtime paths
ChangeRail observability MUST use ignored queue runtime paths for aggregate
status, locks and logs.

#### Scenario: Queue runner writes runtime state
- **WHEN** a plan command writes aggregate status or locks
- **THEN** the default path is under `.runtime/changerail/delivery-plans/`
- **AND** raw logs and locks remain ignored runtime state
