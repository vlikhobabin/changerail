## ADDED Requirements

### Requirement: Orchestrator, worker and reviewer role model
Shared methodology MUST define the operational roles used by supervised
ChangeRail delivery: orchestrator, delivery worker and independent reviewer.

#### Scenario: Agent reads shared methodology
- **WHEN** an agent reads `AGENTS.shared.md`
- **THEN** it can identify which context is responsible for choosing cards,
  running or supervising delivery, fixing scoped blockers and requesting
  review
- **AND** it can identify that the reviewer context is separate from the
  planning and implementation context

### Requirement: Role co-location boundaries
Shared methodology MUST state when orchestrator and delivery worker may be the
same session and when they should be separate, while preserving independent
review as a mandatory separate context.

#### Scenario: Small single-card task is delivered
- **WHEN** a card is small enough for the active supervised session to run
  delivery directly
- **THEN** the methodology permits orchestrator and delivery worker to be the
  same session
- **AND** still requires a fresh reviewer context before publish

#### Scenario: Fresh reviewer is unavailable
- **WHEN** delivery reaches review and no fresh reviewer context is available
- **THEN** the workflow stops at the review gate instead of publishing
