## ADDED Requirements

### Requirement: Review rescue budget contract
ChangeRail review-cycle history schemas MUST represent post-review same-card
rescue budget state separately from review cycle numbering.

#### Scenario: Initial review consumes no rescue attempt
- **WHEN** a review-cycle history record includes the first independent review
  cycle and the writer knows the rescue budget state
- **THEN** the record can store `rescue_budget.limit`,
  `rescue_budget.used`, `rescue_budget.remaining` and
  `rescue_budget.exhausted`
- **AND** the first cycle can store `same_card_rescue_attempt: 0`

#### Scenario: Re-review records consumed rescue attempts
- **WHEN** a same-card fix follows an independent `no-go` and a fresh re-review
  is recorded
- **THEN** the re-review cycle can store the consumed
  `same_card_rescue_attempt`
- **AND** the top-level `rescue_budget.used` and
  `rescue_budget.remaining` counters reflect the same post-review rescue budget

#### Scenario: Legacy review history remains readable
- **WHEN** an existing review-cycle history record omits rescue budget fields
- **THEN** schema validation still accepts the record
- **AND** consumers treat the absent budget fields as unknown instead of
  deriving a configured limit from prose

### Requirement: Delivery run review rescue budget summary
ChangeRail delivery-run schemas MUST allow a best-effort review rescue budget
summary without making it the canonical source when review-cycle history exists.

#### Scenario: Run record summarizes review budget
- **WHEN** a delivery-run status record includes review performance summary
  data
- **THEN** `performance.review.rescue_budget` can store `limit`, `used`,
  `remaining` and `exhausted`

#### Scenario: Legacy run record omits review budget
- **WHEN** a delivery-run status record lacks `performance.review.rescue_budget`
- **THEN** schema validation still accepts the record
- **AND** observability consumers report budget values as unknown unless
  review-cycle history provides them
