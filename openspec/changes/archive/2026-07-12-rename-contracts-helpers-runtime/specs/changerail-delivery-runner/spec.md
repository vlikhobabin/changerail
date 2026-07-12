## ADDED Requirements

### Requirement: ChangeRail delivery runner namespace
The non-interactive delivery runner MUST use ChangeRail command, schema and
runtime names after the rename.

#### Scenario: Runner starts a delivery
- **WHEN** the post-rename runner is invoked for a board card
- **THEN** it launches the ChangeRail delivery skill through
  `$changerail-deliver <card-path>`
- **AND** it writes status records using the `changerail.delivery-run.v1`
  schema id

#### Scenario: Runtime root is defaulted
- **WHEN** the runner is invoked without an explicit runtime root
- **THEN** status and logs are written under `.runtime/changerail/delivery-runs`
