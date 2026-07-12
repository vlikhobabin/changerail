## ADDED Requirements

### Requirement: Consumer-example smoke uses ChangeRail
Wiring discovery smoke MUST create and validate generated consumer examples
with ChangeRail command and skill names.

#### Scenario: Consumer example is created
- **WHEN** wiring discovery smoke runs in consumer-example mode
- **THEN** the temporary consumer exposes `.claude/commands/changerail`
- **AND** it exposes `.codex/skills/changerail-*` for generic lifecycle skills

#### Scenario: Stale command wrapper is present
- **WHEN** the generated consumer contains `.claude/commands/opsx`
- **THEN** wiring discovery smoke fails
