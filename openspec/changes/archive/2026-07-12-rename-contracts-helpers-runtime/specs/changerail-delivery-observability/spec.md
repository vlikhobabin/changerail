## ADDED Requirements

### Requirement: ChangeRail delivery observability paths
Delivery metrics and review-cycle observability MUST read post-rename runtime
records from the ChangeRail runtime namespace by default.

#### Scenario: Metrics command runs with defaults
- **WHEN** the delivery metrics helper runs without explicit input paths
- **THEN** it reads delivery runs from `.runtime/changerail/delivery-runs`
- **AND** it reads review history from `.runtime/changerail/reviews`

#### Scenario: Historical OPSX evidence exists
- **WHEN** old ignored `.runtime/opsx` evidence exists on disk
- **THEN** the post-rename defaults do not mutate or migrate that evidence
