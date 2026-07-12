## ADDED Requirements

### Requirement: Batch guidance separates deliver and runner responsibilities
ChangeRail methodology MUST distinguish between the lifecycle skill that can
process an ordered card queue and the tracked runner that supervises one
non-interactive card invocation.

#### Scenario: Operator plans a bounded batch
- **WHEN** an operator wants to process multiple cards
- **THEN** methodology explains that `$changerail-deliver <board-column>` owns
  one-card-at-a-time queue ordering
- **AND** `bin/changerail-delivery-runner run <card>` is documented as the
  single-card structured-status launcher
