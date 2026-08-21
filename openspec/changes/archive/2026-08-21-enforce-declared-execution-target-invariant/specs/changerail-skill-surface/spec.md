## ADDED Requirements

### Requirement: Lifecycle skills MUST enforce target identity handoff
Canonical `ff`, `do`, `review`, `pub` и `deliver` skills MUST требовать
captured target identity и matching evidence при наличии project declaration и
MUST запрещать implicit substitution.

#### Scenario: Planning and delivery handoff target identity
- **WHEN** project объявил execution target
- **THEN** planning фиксирует identity в delivery scope
- **AND** delivery сохраняет matching evidence или structured blocker

#### Scenario: Reviewer видит mismatch
- **WHEN** manifest, current declaration и evidence target identities не
  совпадают
- **THEN** deterministic preflight блокирует semantic review/publish
- **AND** remediation не предлагает создать substitute target
