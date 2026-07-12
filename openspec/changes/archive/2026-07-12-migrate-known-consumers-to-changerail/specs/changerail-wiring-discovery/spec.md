## ADDED Requirements

### Requirement: Migrated consumers remove stale OPSX wiring
Known consumers migrated to ChangeRail MUST remove stale OPSX generic lifecycle
wiring from project-local discovery paths.

#### Scenario: Consumer is inspected after migration
- **WHEN** a migrated consumer's `.claude`, `.codex` and `bin` wiring is
  inspected
- **THEN** generic lifecycle wiring points to `/opt/changerail`
- **AND** stale `.claude/commands/opsx`, `.codex/skills/opsx-*` and
  `bin/opsx-*` defaults are absent unless explicitly retained as
  project-local legacy notes outside the generated ChangeRail surface

#### Scenario: Agent sessions resume
- **WHEN** migration verification passes for a consumer project
- **THEN** Claude/Codex sessions for that project are restarted, or an explicit
  follow-up card is recorded, before using `/changerail:*` or `$changerail-*`
