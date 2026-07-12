## ADDED Requirements

### Requirement: Short ChangeRail lifecycle aliases
ChangeRail MUST provide official short `chrl-*` Codex skill aliases and
`/chrl:*` Claude command aliases for every canonical generic ChangeRail
lifecycle command.

#### Scenario: Codex discovers short lifecycle aliases
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `chrl-explore`, `chrl-ff`, `chrl-do`, `chrl-review`,
  `chrl-pub` and `chrl-deliver`
- **AND** canonical `changerail-explore`, `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver` remain
  available

#### Scenario: Claude discovers short lifecycle aliases
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/chrl:explore`, `/chrl:ff`, `/chrl:do`,
  `/chrl:review`, `/chrl:pub` and `/chrl:deliver`
- **AND** canonical `/changerail:explore`, `/changerail:ff`,
  `/changerail:do`, `/changerail:review`, `/changerail:pub` and
  `/changerail:deliver` remain available

### Requirement: Short aliases delegate to canonical contracts
Short `chrl-*` and `/chrl:*` aliases MUST delegate to the matching canonical
`changerail-*` lifecycle contract without duplicating lifecycle logic or
introducing a separate runtime namespace.

#### Scenario: Agent opens a short alias skill
- **WHEN** an agent reads `skills/chrl-do/SKILL.md`
- **THEN** the file identifies `chrl-do` as an alias for `changerail-do`
- **AND** it directs the agent to follow the canonical `changerail-do` contract

#### Scenario: User invokes a short Claude command
- **WHEN** a Claude user invokes `/chrl:review`
- **THEN** the wrapper delegates to the canonical `/changerail:review`
  contract
- **AND** review verdict schema ids and runtime paths remain under the
  `changerail` namespace
