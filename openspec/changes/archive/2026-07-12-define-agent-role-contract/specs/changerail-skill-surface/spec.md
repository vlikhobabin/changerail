## ADDED Requirements

### Requirement: Lifecycle skills expose role boundaries
ChangeRail lifecycle skills MUST make the orchestrator, delivery worker and
reviewer boundaries visible in the phase where they matter.

#### Scenario: Deliver orchestrates a card
- **WHEN** an agent follows `changerail-deliver`
- **THEN** the skill describes itself as the supervised orchestrator for the
  card pipeline
- **AND** it states that implementation may run in the same active context
  while review must run in a fresh context

#### Scenario: Delivery hands off to review
- **WHEN** `changerail-do` completes a review-gated card
- **THEN** the skill output and handoff instructions send the card to
  `changerail-review` rather than self-review or publish

#### Scenario: Review is invoked
- **WHEN** an agent follows `changerail-review`
- **THEN** the skill requires a fresh reviewer context and stops on
  self-review
