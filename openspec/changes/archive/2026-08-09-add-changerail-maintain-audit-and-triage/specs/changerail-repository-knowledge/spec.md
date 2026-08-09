## ADDED Requirements

### Requirement: Maintenance audit agent workflow
The repository knowledge maintenance workflow MUST support an agent-facing
read-only audit mode that consumes deterministic scan and lifecycle report
contracts without changing repository state.

#### Scenario: Audit runs deterministic commands
- **WHEN** an agent runs maintenance audit without a supplied report
- **THEN** it uses `bin/changerail-maintenance scan --json` and/or
  `bin/changerail-maintenance report --json` as deterministic inputs
- **AND** it does not pass state-write, baseline-write or card-write flags

#### Scenario: Audit consumes retained report
- **WHEN** an agent receives an existing schema-valid maintenance report path
- **THEN** it may explain findings and ambiguity in prose
- **AND** it treats unsupported or invalid report data as an audit finding
  instead of silently normalizing it outside the deterministic CLI

### Requirement: Maintenance triage agent workflow
The repository knowledge maintenance workflow MUST support bounded agent triage
that produces schema-valid annotations and card previews under ignored runtime
state before any tracked board mutation is requested.

#### Scenario: Triage writes ignored annotations
- **WHEN** maintenance triage records agent annotations
- **THEN** the annotations validate against `changerail.maintenance-triage.v1`
- **AND** the files are written below `.runtime/changerail/maintenance/`

#### Scenario: Triage previews cards before write
- **WHEN** maintenance triage prepares board-card output
- **THEN** it runs or consumes the preview-first card bridge without `--write`
- **AND** no tracked board card is created or updated unless the operator
  separately requested explicit card writes
