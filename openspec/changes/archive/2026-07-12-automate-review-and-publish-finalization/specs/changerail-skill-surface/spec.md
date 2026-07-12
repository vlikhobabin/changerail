## ADDED Requirements

### Requirement: Deliver provides fresh-review launch contract
`changerail-deliver` MUST provide a standard fresh-review launch contract for
the independent review phase.

#### Scenario: Deliver reaches review gate
- **WHEN** `changerail-deliver` reaches a card's review phase without an
  existing fresh verdict
- **THEN** the skill provides a ready-to-run reviewer prompt or invocation
  contract that includes scope, forbidden writes, verdict path and
  `reviewer.independence` requirements
- **AND** the orchestrator validates the resulting verdict with `--check-fresh`
  before continuing to publish

### Requirement: Publish finalizes board metadata deterministically
`changerail-pub` MUST define deterministic board finalization behavior for
review-gated cards after the reviewed payload commit succeeds.

#### Scenario: Publish commits reviewed payload
- **WHEN** `changerail-pub` commits a reviewed card payload
- **THEN** it finalizes the board card into `4.done`, records commit/push
  metadata, and amends only card metadata when required by board protocol
- **AND** it does not make substantive code, docs, specs, schema, script or
  test edits after the fresh `go` verdict
