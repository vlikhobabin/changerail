## ADDED Requirements

### Requirement: Delivery skills preserve review-gated lifecycle
OPSX lifecycle skills MUST keep implementation, independent review and publish
as separate gates with explicit card-state responsibilities.

#### Scenario: Delivery hands off without done move
- **WHEN** `opsx-do` completes and archives all card-owned changes
- **THEN** it records verification and archive evidence but does not move the
  card to `4.done`

#### Scenario: Publish performs final board transition
- **WHEN** `opsx-pub` has a fresh valid `go` verdict and publishes the scoped
  payload
- **THEN** it performs only the documented board finalization needed to mark the
  story done
