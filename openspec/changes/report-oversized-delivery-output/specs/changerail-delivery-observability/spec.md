## ADDED Requirements

### Requirement: Delivery metrics reports oversized command output
The delivery metrics helper MUST report structured oversized command output
metadata from delivery run records without scraping raw logs.

#### Scenario: Oversized output metadata is available
- **WHEN** a delivery run record includes command output threshold metadata
- **THEN** metrics output reports oversized command count, largest observed
  command output, threshold and available top command label
- **AND** CSV and JSON output expose stable fields for those values

#### Scenario: Output metadata is unavailable
- **WHEN** a delivery run record lacks command output metadata
- **THEN** metrics renders the output amplification fields as `unknown`

### Requirement: Output size and token usage semantics are documented
ChangeRail observability documentation MUST distinguish command output byte
metadata from model-reported token usage fields.

#### Scenario: Token usage is available
- **WHEN** metrics has cached input, uncached input, output, reasoning or total
  token counts
- **THEN** documentation explains that those fields come from structured model
  usage reporting and are separate from command output byte counts

#### Scenario: Token usage is unavailable
- **WHEN** token usage fields are unavailable but output metadata is present
- **THEN** metrics reports token usage as `unknown` while still reporting
  command output metadata
