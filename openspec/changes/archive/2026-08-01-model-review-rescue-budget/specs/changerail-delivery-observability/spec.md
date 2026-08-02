## ADDED Requirements

### Requirement: Rescue budget metrics
The ChangeRail delivery metrics helper MUST report structured same-card review
rescue budget counters without scraping free-text logs or prose.

#### Scenario: History contains rescue budget state
- **WHEN** metrics reads review-cycle history containing `rescue_budget.limit`,
  `rescue_budget.used`, `rescue_budget.remaining` and
  `rescue_budget.exhausted`
- **THEN** text, JSON and CSV metrics expose those values for the corresponding
  run
- **AND** existing first-pass GO output remains based on structured review cycle
  results

#### Scenario: History is absent but run summary has budget state
- **WHEN** metrics has no review-cycle history for a run but the delivery-run
  status includes `performance.review.rescue_budget`
- **THEN** metrics exposes the run summary budget counters as best-effort values

#### Scenario: History and run summary disagree
- **WHEN** both review-cycle history and delivery-run status provide rescue
  budget counters
- **THEN** metrics uses the review-cycle history counters as the canonical
  source for that run

#### Scenario: Legacy records have no budget fields
- **WHEN** metrics reads legacy review history or delivery-run status without
  rescue budget fields
- **THEN** it renders budget limit, used, remaining and exhausted values as
  `unknown`

### Requirement: Stable rescue budget CSV columns
The delivery metrics CSV output MUST include stable columns for rescue budget
state.

#### Scenario: Operator exports metrics CSV
- **WHEN** the operator passes `--csv`
- **THEN** the header includes `rescue_budget_limit`,
  `rescue_budget_used`, `rescue_budget_remaining` and
  `rescue_budget_exhausted`
- **AND** each row renders unavailable values as `unknown`
