## ADDED Requirements

### Requirement: Deliver accepts artifact-pending accepted cards
`changerail-deliver` MUST accept a scoped accepted card with an ordered change
plan as the normal start point even when card-owned OpenSpec artifacts do not
exist yet.

#### Scenario: Deliver starts from planned todo card
- **WHEN** an operator invokes `$changerail-deliver <card>` for a card in
  `2.todo` that has ordered `## Change N:` sections but no active
  `openspec/changes/<change>/` directory
- **THEN** the deliver workflow runs its fast-forward phase to create or
  complete apply-ready artifacts
- **AND** it does not stop solely because artifacts were absent before
  invocation

#### Scenario: Fast-forward remains planning-only
- **WHEN** the deliver workflow invokes or performs the fast-forward phase
- **THEN** that phase creates or updates board/card and OpenSpec artifacts only
- **AND** implementation, archive, review and publish remain responsibilities
  of the later lifecycle phases

### Requirement: Phase skills remain explicit recovery surfaces
ChangeRail lifecycle skill wording MUST distinguish the normal one-command
handoff from explicit phase command usage.

#### Scenario: Skill guidance names the normal path
- **WHEN** an agent reads `changerail-deliver` or `changerail-ff` guidance
- **THEN** the guidance identifies `$changerail-deliver <card>` as the normal
  operator handoff for an accepted ordered card
- **AND** it keeps `$changerail-ff`, `$changerail-do`, `$changerail-review` and
  `$changerail-pub` available for repair, debug or manual resume

#### Scenario: Fast-forward completes independently
- **WHEN** `$changerail-ff <card>` is invoked directly
- **THEN** its output hands off to `$changerail-do <card>` for explicit phase
  continuation
- **AND** it does not imply that direct fast-forward was required before
  `$changerail-deliver <card>` could have started
