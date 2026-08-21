## ADDED Requirements

### Requirement: Optional verification coverage configuration
Bootstrapped project guidance MUST показывать verification coverage как explicit
optional tracked config reference и MUST описывать map как project-owned policy,
а не ChangeRail global test catalog.

#### Scenario: Новый consumer не включает coverage map
- **WHEN** project bootstrapped без project-specific map
- **THEN** existing strict verification profile и mandatory targeted OpenSpec
  validation не меняются
- **AND** placeholder coverage rule не считается mandatory

#### Scenario: Consumer включает coverage map
- **WHEN** maintainers добавляют tracked map reference и schema-valid entries
- **THEN** guidance объясняет planning/evidence/review flow и namespaced
  extension ownership
- **AND** examples используют только generic project paths и synthetic data
