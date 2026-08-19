## ADDED Requirements

### Requirement: Delivery run schema bounds command output metadata
The `changerail.delivery-run.v1` schema MUST allow structured command output
metadata while forbidding raw command payload copies in status records.

#### Scenario: Status contains command output metadata
- **WHEN** a delivery run record includes per-command output metadata
- **THEN** schema validation accepts non-negative stdout/stderr byte counts,
  result classification, threshold flags and truncation indicators
- **AND** the schema does not allow raw stdout or stderr payload text inside
  per-command metadata

#### Scenario: Legacy status lacks output metadata
- **WHEN** a delivery run record was produced before command output metadata
  existed
- **THEN** schema validation continues to accept the record if all pre-existing
  required fields are valid

### Requirement: Delivery run output metadata remains compact
The delivery-run contract MUST keep output amplification diagnostics bounded so
`status.json` remains a supervisor-friendly summary.

#### Scenario: Many commands exceed threshold
- **WHEN** a delivery run contains many oversized command events
- **THEN** the status record includes aggregate counts and bounded top-command
  metadata rather than every raw output payload
- **AND** ignored raw evidence paths remain outside committable scope
