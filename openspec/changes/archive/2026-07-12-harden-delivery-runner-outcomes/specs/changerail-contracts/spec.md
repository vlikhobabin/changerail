## ADDED Requirements

### Requirement: Release checks покрывают все contract schemas
ChangeRail release и verification documentation MUST описывать полный публичный
contract schema set: review verdict, review cycle history, delivery manifest,
delivery run и evidence index.

#### Scenario: Maintainer проверяет release checks
- **WHEN** maintainer читает release или contract documentation
- **THEN** documented schema coverage включает все пять публичных
  `changerail-*.schema.json` contract files
