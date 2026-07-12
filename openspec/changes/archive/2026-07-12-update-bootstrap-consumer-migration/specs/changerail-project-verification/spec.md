## ADDED Requirements

### Requirement: Verify ChangeRail consumer wiring
`verify-project` MUST validate ChangeRail consumer wiring after the rename.

#### Scenario: Consumer is correctly wired
- **WHEN** `verify-project` runs for a generated ChangeRail consumer
- **THEN** `.claude/commands/changerail`, `.claude/skills`,
  `.codex/skills/changerail-*`, `bin/changerail-*` and `bin/openspec` resolve
  to the ChangeRail source of truth

#### Scenario: Consumer still uses stale OPSX wiring
- **WHEN** `verify-project` finds stale `.claude/commands/opsx`,
  `.codex/skills/opsx-*` or `bin/opsx-*` defaults
- **THEN** verification fails with a message identifying the stale wiring
