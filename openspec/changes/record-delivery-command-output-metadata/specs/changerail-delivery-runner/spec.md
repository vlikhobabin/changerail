## ADDED Requirements

### Requirement: Runner records bounded command output metadata
The delivery runner MUST record bounded per-command output metadata in delivery
run status when structured child events provide sufficient data.

#### Scenario: Command event reports output bytes
- **WHEN** child JSONL exposes command completion data with stdout or stderr
  byte counts
- **THEN** `status.json` records bounded command output-byte metadata for that
  command
- **AND** the record does not copy raw stdout or stderr payload text into the
  structured status

#### Scenario: Command exceeds output threshold
- **WHEN** a command's observed output bytes exceed the documented
  per-command threshold
- **THEN** `status.json` marks that command as threshold-exceeded
- **AND** the status retains only bounded metadata and references to ignored raw
  evidence when such references are available

### Requirement: Runner distinguishes command result and truncation states
The delivery runner MUST distinguish command process failure, runner-observed
truncation and successful bounded result when structured child events provide
enough fields.

#### Scenario: Command fails without truncation
- **WHEN** a command completion event reports a non-zero exit code without a
  truncation indicator
- **THEN** the command metadata records a process-failure classification

#### Scenario: Command output is runner-truncated
- **WHEN** a command event or runner observation reports output truncation
- **THEN** the command metadata records a truncation classification separate
  from process failure

#### Scenario: Command succeeds within budget
- **WHEN** a command completion event reports success and output bytes within
  the threshold
- **THEN** the command metadata records a successful bounded result

#### Scenario: Structured output fields are unavailable
- **WHEN** child JSONL lacks sufficient fields to classify command output
- **THEN** the runner reports the optional output classification as unknown or
  absent instead of scraping arbitrary stdout/stderr text
