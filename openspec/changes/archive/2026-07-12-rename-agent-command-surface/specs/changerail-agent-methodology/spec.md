## ADDED Requirements

### Requirement: ChangeRail delivery handoff examples
Shared methodology MUST use ChangeRail lifecycle invocations in delivery
handoff examples.

#### Scenario: Agent completes fast-forward planning
- **WHEN** a card reaches apply-ready OpenSpec artifacts
- **THEN** the handoff example uses `$changerail-do <card-path>` when the
  ChangeRail delivery surface is installed

#### Scenario: Claude user follows the workflow
- **WHEN** a Claude Code user invokes the documented lifecycle
- **THEN** the documented command namespace is `/changerail:*`
