## ADDED Requirements

### Requirement: Verify short ChangeRail aliases
`verify-project` MUST validate short `chrl-*` ChangeRail alias wiring for
generated or migrated consumer projects.

#### Scenario: Consumer has complete short alias wiring
- **WHEN** `verify-project` runs for a correctly wired ChangeRail consumer
- **THEN** `.claude/commands/chrl` resolves to the ChangeRail source of truth
- **AND** `.codex/skills/chrl-*` resolves to tracked ChangeRail alias skill
  directories
- **AND** the consumer passes verification

#### Scenario: Consumer is missing a short alias
- **WHEN** a generated ChangeRail consumer is missing `.codex/skills/chrl-do`
  or `.claude/commands/chrl`
- **THEN** `verify-project` exits non-zero
- **AND** the output identifies the missing short alias wiring
