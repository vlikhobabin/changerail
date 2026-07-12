## ADDED Requirements

### Requirement: Bootstrap installs short ChangeRail aliases
Bootstrap MUST generate new consumer projects with both canonical
`changerail-*` wiring and short `chrl-*` wiring for ChangeRail lifecycle
commands.

#### Scenario: Operator bootstraps a project with alias wiring
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives `.codex/skills/chrl-*` entries for all generic
  ChangeRail lifecycle skills
- **AND** the target receives `.claude/commands/chrl` for all generic
  ChangeRail lifecycle commands
- **AND** canonical `changerail-*` wiring remains present

#### Scenario: Bootstrap dry-run reports alias wiring
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** the planned operations include the short `chrl-*` Codex skill
  entries and `/chrl:*` Claude command directory
