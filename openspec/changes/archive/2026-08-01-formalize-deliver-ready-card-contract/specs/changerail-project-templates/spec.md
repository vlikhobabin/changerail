## ADDED Requirements

### Requirement: Board templates define deliver-ready cards
Project board templates MUST let generated consumer projects prepare
`deliver-ready` cards without creating premature OpenSpec change directories
and without adding another board column.

#### Scenario: Consumer board README is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the project
  board README
- **THEN** the generated file defines `deliver-ready` as an accepted `2.todo`
  card with owner, observable acceptance, ordered change plan, dependencies and
  handoff
- **AND** it states that OpenSpec artifacts are created by `$chrl-deliver` or
  the internal fast-forward phase rather than required before handoff

#### Scenario: Consumer card template is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the board card
  template
- **THEN** the template contains fields and notes sufficient to prepare a
  `deliver-ready` accepted card
- **AND** it does not instruct maintainers to create
  `openspec/changes/<change>/` directories while filling the template

#### Scenario: Board columns are reviewed
- **WHEN** generated board docs describe readiness
- **THEN** the standard board remains five columns from `1.backlog` through
  `5.canceled`
- **AND** no sixth `deliver-ready` column is introduced
