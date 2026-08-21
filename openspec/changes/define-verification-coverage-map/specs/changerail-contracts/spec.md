## ADDED Requirements

### Requirement: Project-owned verification coverage map
ChangeRail MUST валидировать optional tracked map
`changerail.verification-coverage.v1`, entries которой содержат только `id`,
`applies_to`, `invariant`, `oracle` и `required_evidence`. Invalid configured
map MUST fail closed; отсутствующая map MUST сохранять current project-declared
verification floor.

#### Scenario: Minimal generic Python rule проходит валидацию
- **WHEN** project rule использует normalized Python path selectors, stable
  invariant, bounded project oracle ref и required command/runtime evidence
- **THEN** schema validation проходит
- **AND** rule не делает formatter, typing или environment matrix checks
  mandatory вне explicit project policy

#### Scenario: Настроено unsafe или incomplete rule
- **WHEN** entry имеет duplicate id, absolute/traversing glob, не имеет selector,
  содержит unknown oracle kind, unbound evidence ref или undeclared extra policy
  field
- **THEN** map validation fail closed
- **AND** ни один coverage ledger этой map не считается trusted

### Requirement: Verification coverage plan and ledger contracts
ChangeRail MUST предоставлять tracked per-change plan-reference contract и
ignored runtime ledger contract. Оба MUST быть fingerprint-bound и ссылаться на
coverage ids/card acceptance hashes без дублирования invariant, oracle,
commands, acceptance text или final verdict authority.

#### Scenario: Planning ссылается на selected coverage
- **WHEN** `ff` оценивает configured map для change
- **THEN** tracked plan записывает map fingerprint, selected rule ids и exact
  card acceptance hashes
- **AND** map и card остаются sources referenced content

#### Scenario: Runtime ledger записывает observed evidence
- **WHEN** delivery reconciles actual manifest scope и записывает evidence
- **THEN** ignored ledger связывает map/plan/manifest/review fingerprints и
  evidence-index refs для каждого applicable rule
- **AND** не объявляет business acceptance и не включает raw outputs

### Requirement: Domain verification surface extension boundary
Coverage selectors MUST принимать schema-valid namespaced surface kinds от
project/domain extension, не назначая domain semantics или execution tools
generic ChangeRail core.

#### Scenario: Domain extension различает specialized surfaces
- **WHEN** extension выдает namespaced kinds для language modules, metadata,
  forms, roles, posting, reports, migrations или runtime UI
- **THEN** generic coverage matching может выбрать project-owned rules по ids
- **AND** domain classification/oracle behavior остается owned by extension
