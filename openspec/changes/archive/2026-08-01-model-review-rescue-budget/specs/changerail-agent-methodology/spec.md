## ADDED Requirements

### Requirement: Review rescue terminology
ChangeRail methodology MUST define initial review, same-card rescue attempt and
re-review cycle as separate review-gated delivery concepts.

#### Scenario: Initial review is recorded
- **WHEN** a delivered card reaches its first independent review
- **THEN** methodology treats that review as `review_cycle: 1`
- **AND** it does not count the initial review as a consumed same-card rescue
  attempt

#### Scenario: No-go is followed by same-card rescue
- **WHEN** an independent review returns `no-go` and the implementing session
  fixes only scoped blocker findings in the same card
- **THEN** methodology counts that bounded fix as one same-card rescue attempt
- **AND** the following fresh review is a re-review cycle

#### Scenario: Rescue budget is exhausted
- **WHEN** the configured same-card rescue budget is exhausted and the latest
  review still returns `no-go`
- **THEN** autonomous delivery follows the linked rescue, replacement or
  investigation-card policy
- **AND** it does not publish the dirty payload or count the first review as a
  rescue attempt
