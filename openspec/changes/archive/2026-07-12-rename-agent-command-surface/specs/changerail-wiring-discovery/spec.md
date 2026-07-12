## ADDED Requirements

### Requirement: ChangeRail command discovery wiring
Wiring discovery MUST verify ChangeRail lifecycle skills and Claude command
wrappers instead of OPSX lifecycle names.

#### Scenario: Repo-local wiring is checked
- **WHEN** wiring smoke validates the ChangeRail repository
- **THEN** `.claude/commands/changerail` resolves to the tracked ChangeRail
  command wrapper directory
- **AND** `.codex/skills/changerail-*` resolves to tracked ChangeRail lifecycle
  skill directories

#### Scenario: Consumer wiring is checked
- **WHEN** wiring smoke validates a generated consumer example
- **THEN** the consumer exposes `/changerail:*` Claude commands
- **AND** the consumer exposes `changerail-*` Codex skills through symlinks to
  the ChangeRail source of truth
