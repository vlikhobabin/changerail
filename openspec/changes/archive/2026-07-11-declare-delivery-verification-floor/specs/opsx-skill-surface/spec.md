## ADDED Requirements

### Requirement: Delivery and review audit mandatory verification
`opsx-do` MUST collect mandatory verification from local rules and artifacts,
and `opsx-review` MUST audit whether mandatory verification claims are backed by
concrete evidence.

#### Scenario: Delivery hands off evidence
- **WHEN** `opsx-do` completes a change with mandatory checks
- **THEN** the card, tasks or delivery manifest contains command/outcome
  evidence for those checks

#### Scenario: Review finds an unbacked mandatory claim
- **WHEN** `opsx-review` sees a mandatory verification claim without concrete
  command/outcome evidence
- **THEN** it records a finding instead of treating the claim as proven
