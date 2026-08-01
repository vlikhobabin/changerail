## ADDED Requirements

### Requirement: Deliver-ready accepted card contract
ChangeRail methodology MUST define `deliver-ready` as an accepted-card property
for normal one-command delivery handoff, not as a separate board lane or
independent tracked status field.

#### Scenario: Agent evaluates an accepted card
- **WHEN** an agent reads a board card in `2.todo` with accepted scope, known
  ownership, observable acceptance criteria, ordered `## Change N:` sections,
  explicit dependencies or `none`, and a `$chrl-deliver` or
  `$changerail-deliver` next handoff
- **THEN** the methodology treats the card as `deliver-ready`
- **AND** it does not require a sixth board column or a second readiness status
  field

#### Scenario: Artifacts are not created yet
- **WHEN** a `deliver-ready` card has no active `openspec/changes/<change>/`
  artifacts yet
- **THEN** `$changerail-deliver <card>` remains a valid normal handoff
- **AND** the internal fast-forward phase creates or completes the OpenSpec
  artifacts before delivery implementation starts

#### Scenario: Readiness criteria are missing
- **WHEN** a card is not yet `deliver-ready`
- **THEN** methodology directs agents and diagnostics to name the missing
  acceptance, scope, owner, ordered plan, dependency or handoff criteria
  instead of returning only a boolean result

### Requirement: One-command delivery is the normal operator handoff
ChangeRail methodology MUST present `$chrl-deliver <card>` as the everyday
operator handoff for a `deliver-ready` card while preserving canonical
`$changerail-deliver <card>` naming and phase commands for repair,
debugging and manual resume.

#### Scenario: Operator reads single-card guidance
- **WHEN** docs describe the normal accepted-card delivery path
- **THEN** they show `$chrl-deliver <card>` or `$changerail-deliver <card>` as
  the primary operator command
- **AND** they describe `ff`, `do`, `review` and `pub` as internal lifecycle
  phases or explicit repair/debug/manual-resume commands

#### Scenario: Manual recovery is needed
- **WHEN** a safety stop leaves a card partway through the lifecycle
- **THEN** phase commands remain documented as valid explicit resume or repair
  surfaces for the stopped phase
