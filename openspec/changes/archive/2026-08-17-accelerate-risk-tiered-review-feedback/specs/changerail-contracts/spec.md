## ADDED Requirements

### Requirement: Deterministic review preflight result
The ChangeRail review helper MUST produce a schema-valid deterministic preflight
result before any LLM payload review is launched.

#### Scenario: Machine gates pass for ordinary code
- **WHEN** a review-ready ordinary card has a valid manifest, exact scope,
  archived changes and all available strict deterministic checks pass
- **THEN** preflight returns `ready-for-llm-review`
- **AND** the result recommends reasoning effort `high`

#### Scenario: Manifest operation metadata is stale
- **WHEN** expected and actual comparable path sets are identical but manifest
  operation metadata differs from Git state
- **THEN** explicit normalization may refresh operation metadata
- **AND** normalization MUST NOT add a missing or extra path to the manifest

#### Scenario: Process gate fails
- **WHEN** manifest, board, archive, scope or an available strict deterministic
  check fails
- **THEN** preflight returns a structured blocker before LLM launch
- **AND** no implementation review cycle is consumed

### Requirement: Review history phase counters
Review-cycle history MUST support independent optional counters for planning,
delivery-fix, implementation-review and live-admission phases.

#### Scenario: Planning is repeated before implementation review
- **WHEN** a card needs multiple planning corrections before its first semantic
  implementation payload review
- **THEN** planning cycles increase independently
- **AND** implementation review/rescue counters remain unchanged
