## ADDED Requirements

### Requirement: Queue no-go recovery remains explicit
The delivery runner MUST keep aggregate `NO-GO` handling fail-fast while
documenting that autonomous recovery occurs through a linked card before
dependent downstream cards resume.

#### Scenario: Child no-go blocks downstream cards
- **WHEN** a child delivery run returns `NO-GO`
- **THEN** aggregate queue status records `NO-GO`
- **AND** no new downstream cards are launched from the same plan run

#### Scenario: Autonomous recovery is represented as a card
- **WHEN** an autonomous agent continues after a terminal child `NO-GO`
- **THEN** it MUST create or run a linked rescue/replacement or investigation
  card rather than pushing the failed child payload
- **AND** the original aggregate plan may resume only after the recovery card
  publishes with a fresh independent `GO`
