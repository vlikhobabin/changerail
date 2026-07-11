## ADDED Requirements

### Requirement: Review cycle evidence contract
OPSX MUST define runtime review-cycle evidence that can retain previous review
results while leaving `.runtime/opsx/reviews/<card-id>.json` as the latest
canonical publish gate verdict.

#### Scenario: Latest verdict remains canonical
- **WHEN** publish validates a review verdict
- **THEN** it continues to validate `.runtime/opsx/reviews/<card-id>.json`
  against `opsx.review-verdict.v1`

#### Scenario: Metrics reads historical cycles
- **WHEN** review-cycle evidence exists for prior cycles
- **THEN** metrics can count historical findings without modifying the latest
  canonical verdict
- **AND** each historical cycle retains finding details or an immutable
  per-cycle verdict snapshot path
