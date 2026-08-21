## ADDED Requirements

### Requirement: Verification coverage lifecycle
Когда project настраивает verification coverage map, ChangeRail planning MUST
объявить selected coverage, delivery MUST reconcile его с actual scope и
observed evidence, а review MUST проверить каждый applicable invariant против
card acceptance. Projects без map MUST сохранять existing verification floor.

#### Scenario: Planned scope получает applicable path
- **WHEN** actual delivery manifest содержит path/operation или namespaced
  surface, делающий unplanned coverage rule applicable
- **THEN** delivery блокируется и возвращает change в planning
- **AND** не продолжает работу с silently incomplete ledger

#### Scenario: Applicable rule имеет complete evidence
- **WHEN** plan и actual scope совпадают, а все required evidence references
  valid/fresh
- **THEN** deterministic preflight может передать payload в independent review
- **AND** reviewer по-прежнему оценивает oracle/test adequacy до acceptance pass
