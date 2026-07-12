## ADDED Requirements

### Requirement: Discovery smoke covers short aliases
Wiring discovery smoke MUST validate short `chrl-*` Codex skill aliases and
`/chrl:*` Claude command aliases alongside canonical ChangeRail lifecycle
names.

#### Scenario: Repo-local alias wiring is checked
- **WHEN** wiring smoke validates the ChangeRail repository
- **THEN** `.codex/skills/chrl-*` resolves to tracked ChangeRail alias skill
  directories
- **AND** `.claude/commands/chrl` resolves to the tracked short command wrapper
  directory

#### Scenario: Consumer-example alias wiring is checked
- **WHEN** wiring discovery smoke validates a generated consumer example
- **THEN** the consumer exposes `/chrl:*` Claude command aliases
- **AND** the consumer exposes `chrl-*` Codex skill aliases through symlinks to
  the ChangeRail source of truth

#### Scenario: Short alias is missing from smoke target
- **WHEN** a smoke target is missing a required `chrl-*` skill or `/chrl:*`
  command wrapper
- **THEN** wiring discovery smoke fails with a report entry identifying the
  missing alias
