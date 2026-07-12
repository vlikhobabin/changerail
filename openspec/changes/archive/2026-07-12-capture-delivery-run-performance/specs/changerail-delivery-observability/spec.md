## ADDED Requirements

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
