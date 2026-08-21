## ADDED Requirements

### Requirement: Agents SHALL preserve declared execution target
Planning, delivery и review agents SHALL переносить exact project-declared
target identity и SHALL NOT создавать, клонировать, восстанавливать,
регистрировать или выбирать substitute target для обхода unavailable external
gate.

#### Scenario: Declared target недоступна
- **WHEN** обязательная target verification не может быть выполнена на exact
  declared identity
- **THEN** agent записывает structured blocker
- **AND** не получает green evidence на новой или альтернативной среде

#### Scenario: Проект не объявил target
- **WHEN** `.changerail/execution-target.json` отсутствует и acceptance не
  требует target-bound evidence
- **THEN** existing generic workflow остается доступным
