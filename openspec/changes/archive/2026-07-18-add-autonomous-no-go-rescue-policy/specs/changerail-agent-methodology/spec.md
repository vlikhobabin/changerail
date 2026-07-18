## ADDED Requirements

### Requirement: Autonomous repeated no-go escalation
ChangeRail methodology MUST define an autonomous escalation path for repeated
`NO-GO` review cycles that preserves independent review and fail-closed publish
semantics without waiting for operator authorization.

#### Scenario: Same-card rescue budget remains available
- **WHEN** a review returns `NO-GO` with a scoped blocker
- **THEN** the implementing session may perform bounded same-card rescue work
  within the configured rescue budget
- **AND** it MUST request a fresh independent re-review before publish

#### Scenario: Same-card rescue budget is exhausted
- **WHEN** the same-card rescue budget is exhausted and the latest review still
  returns `NO-GO`
- **THEN** the orchestrating agent MUST NOT publish the dirty payload
- **AND** it MUST create or request a linked rescue/replacement card instead of
  self-authorizing another same-card rescue

#### Scenario: Replacement card carries prior history
- **WHEN** a linked rescue/replacement card is created after repeated `NO-GO`
- **THEN** the card MUST include the source card, latest safe published
  reference, prior blocker findings, rescue attempts, evidence summaries,
  current hypothesis and required verification floor

#### Scenario: Repeated blocker class escalates to investigation
- **WHEN** two linked rescue/replacement cards in the same lineage return the
  same blocker class or unresolved invariant
- **THEN** the next autonomous card MUST be an investigation/design card rather
  than another implementation rescue

#### Scenario: Goal is externally blocked or unverifiable
- **WHEN** investigation shows that the goal needs unavailable credentials,
  network, license, stand access, required software, or cannot be reproduced
- **THEN** the card MUST record `BLOCKED`, `SUPERSEDED` or `NOT-VERIFIABLE`
  with concrete evidence instead of publishing unreviewed implementation
