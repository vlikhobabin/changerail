## ADDED Requirements

### Requirement: Runner captures delivery performance summary
The delivery runner MUST record best-effort performance data from child JSONL
events and workspace runtime evidence in the delivery run status record.

#### Scenario: Child emits command lifecycle events
- **WHEN** a fake child JSONL stream contains command start and completion
  events for multiple commands
- **THEN** the runner status includes command execution count
- **AND** it includes command duration summaries with runner-observed durations

#### Scenario: Child emits agent messages
- **WHEN** a child JSONL stream contains agent message events
- **THEN** the runner status includes an agent message count when that event
  class is observed

#### Scenario: Child reaches terminal outcome
- **WHEN** a child JSONL stream or fallback evidence determines a terminal
  outcome
- **THEN** the runner status includes the terminal outcome and available timing
  summary without changing the existing `DELIVERED`, `NO-GO` or `BLOCKED`
  semantics

### Requirement: Runner timestamps observed JSONL events
The delivery runner MUST preserve runner-observed timing for child JSONL events
used in performance summaries.

#### Scenario: Timeline is retained
- **WHEN** the runner records a timeline entry or equivalent command summary
- **THEN** each retained event has a runner-observed timestamp or duration
  derived from runner observation order
- **AND** raw child stdout remains ignored runtime evidence
