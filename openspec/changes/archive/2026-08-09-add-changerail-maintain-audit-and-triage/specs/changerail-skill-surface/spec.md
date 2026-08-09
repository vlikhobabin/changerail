## ADDED Requirements

### Requirement: Maintain skill surface
ChangeRail MUST provide tracked generic source skills for canonical
`changerail-maintain` and short alias `chrl-maintain`, plus Claude command
wrappers for `/changerail:maintain` and `/chrl:maintain`.

#### Scenario: Codex discovers maintain skills
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `changerail-maintain` and `chrl-maintain`
- **AND** `chrl-maintain` delegates to the canonical `changerail-maintain`
  contract without introducing a separate runtime namespace

#### Scenario: Claude discovers maintain commands
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/changerail:maintain` and `/chrl:maintain`
- **AND** the short wrapper delegates to the canonical maintain command

### Requirement: Maintain modes preserve lifecycle boundaries
`changerail-maintain` MUST expose only `audit` and `triage` modes, and MUST NOT
perform delivery, publish or fix work.

#### Scenario: Audit mode is invoked
- **WHEN** an agent follows `changerail-maintain audit`
- **THEN** it runs or consumes deterministic repository maintenance scan/report
  output
- **AND** it does not write tracked files, board cards, baseline files,
  delivery manifests, publish records or external systems

#### Scenario: Triage mode is invoked
- **WHEN** an agent follows `changerail-maintain triage`
- **THEN** it may write only schema-valid annotations and previews below ignored
  maintenance runtime state
- **AND** it does not commit, push, publish or mutate tracked board cards by
  default

### Requirement: Maintain mutation requests route through card flow
`changerail-maintain` MUST treat requests to fix findings, publish changes or
perform tracked repository mutation as a handoff to normal ChangeRail card
delivery until an explicit fix mode is delivered.

#### Scenario: User requests fix through maintain
- **WHEN** a user asks `changerail-maintain` to fix a maintenance finding
- **THEN** the skill states that fix mode is not available yet
- **AND** it routes the work to a normal ChangeRail board card and
  `$changerail-deliver` handoff

#### Scenario: User requests card writes during triage
- **WHEN** a user explicitly supplies a tracked card-write intent such as
  `--write-cards`
- **THEN** the skill may delegate only to `bin/changerail-maintenance cards
  --write`
- **AND** it still does not commit, push or publish the resulting board change
  without the normal delivery/review/publish flow
