## ADDED Requirements

### Requirement: Полное покрытие ChangeRail contract schemas
`verify-project` и его smoke checks MUST валидировать reachability для каждой
public ChangeRail contract schema, tracked в source repository.

#### Scenario: Все public schemas существуют
- **WHEN** `bin/verify-project <path>` запускается для consumer project
- **THEN** он проверяет review verdict, review cycle history, delivery manifest,
  delivery run и evidence index schema files

#### Scenario: Public schema отсутствует
- **WHEN** любой public ChangeRail contract schema file отсутствует в
  ChangeRail source root
- **THEN** verification завершается non-zero и указывает missing schema
