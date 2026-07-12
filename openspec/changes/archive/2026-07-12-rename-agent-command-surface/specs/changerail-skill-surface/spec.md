## ADDED Requirements

### Requirement: ChangeRail lifecycle skill namespace
The generic lifecycle skill surface MUST use `changerail-*` skill names and
`/changerail:*` Claude commands as the canonical invocation namespace.

#### Scenario: Codex discovers lifecycle skills
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `changerail-explore`, `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver`
- **AND** it does not require `opsx-*` lifecycle skill names for new defaults

#### Scenario: Claude discovers lifecycle commands
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/changerail:explore`, `/changerail:ff`,
  `/changerail:do`, `/changerail:review`, `/changerail:pub` and
  `/changerail:deliver`
- **AND** new generated projects do not install `/opsx:*` command defaults

### Requirement: OpenSpec lifecycle namespace is preserved
ChangeRail MUST keep OpenSpec lifecycle skills under the `openspec-*`
namespace.

#### Scenario: OpenSpec skills are discovered after rename
- **WHEN** Codex or Claude loads ChangeRail project skills
- **THEN** OpenSpec artifact lifecycle skills remain named `openspec-*`
- **AND** `bin/openspec` remains the pinned OpenSpec CLI wrapper
