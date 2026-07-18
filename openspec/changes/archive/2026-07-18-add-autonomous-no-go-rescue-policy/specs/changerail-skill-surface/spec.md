## MODIFIED Requirements

### Requirement: Deliver skill orchestrates the lifecycle
`changerail-deliver` MUST orchestrate the card-level flow `ff -> do -> review -> pub`
while preserving phase safety stops, scoped publish behavior and autonomous
repeated-`NO-GO` escalation.

#### Scenario: Deliver reaches an external review stop
- **WHEN** an operator requires external review instead of self-launched review
- **THEN** `changerail-deliver` stops at the review gate and prints the review and
  resume commands without publishing

#### Scenario: Deliver uses the default review rescue budget
- **WHEN** `changerail-deliver` receives consecutive `no-go` review verdicts
- **THEN** the default autonomous policy allows five bounded same-card rescue
  attempts after the first `no-go`
- **AND** each rescue attempt still requires a fresh independent re-review
  before publish

#### Scenario: Deliver exhausts the same-card rescue budget
- **WHEN** the default same-card rescue budget is exhausted and review still
  returns `no-go`
- **THEN** `changerail-deliver` MUST stop publishing that payload
- **AND** the lifecycle instructions MUST direct the orchestrator to create a
  linked rescue/replacement card with prior cycle history instead of requesting
  manual exceptional authorization

#### Scenario: Deliver detects repeated lineage blockers
- **WHEN** linked replacement/rescue cards repeatedly return the same blocker
  class or unresolved invariant
- **THEN** lifecycle instructions MUST direct the orchestrator to create an
  investigation/design card before further implementation rescue work
