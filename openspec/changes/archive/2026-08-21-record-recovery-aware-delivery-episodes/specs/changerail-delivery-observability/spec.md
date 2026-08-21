## ADDED Requirements

### Requirement: Recovery-aware episode telemetry
ChangeRail MUST публиковать canonical structured episode, связывающий initial
delivery, blocked/recovery attempts, review/rescue cycles и publish через
explicit ids, а не log parsing, timestamp inference или один card id.

#### Scenario: Оператор проверяет completed recovered delivery
- **WHEN** card блокируется, возобновляется, получает no-go/rescue/re-review и
  затем publish
- **THEN** episode показывает ordered typed attempts, links, durations, usage и
  final outcome
- **AND** report строится без чтения raw child logs

#### Scenario: Attempt оставлен
- **WHEN** recovery attempt не достигает publish и ни один successor attempt его
  не supersede
- **THEN** episode остается terminal/incomplete с explicit last known outcome
- **AND** не считается delivered по inference
