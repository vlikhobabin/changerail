## ADDED Requirements

### Requirement: Episode-aware delivery metrics
`changerail-delivery-metrics` MUST агрегировать explicitly linked attempts по
episode, исключать preflight-only records из delivery success и first-pass
review rates и присоединять review/publish data только через matching episode и
attempt lineage.

#### Scenario: Preflight-only plan попадает в отчет
- **WHEN** runtime содержит plan preflight без delivery/recovery attempt
- **THEN** metrics сообщает его в preflight diagnostics/counts
- **AND** он отсутствует в delivery success и first-pass-review denominators

#### Scenario: Blocked episode возобновляется и публикуется
- **WHEN** один episode содержит initial blocked delivery, linked recovery,
  review rescue и successful publish attempts
- **THEN** metrics выдает одну episode row с attempt/recovery counts, summed
  usage/durations и delivered final outcome
- **AND** first-pass review использует только первый linked review cycle

#### Scenario: Later review принадлежит другому episode
- **WHEN** одна card имеет earlier preflight/run и later unrelated delivery с
  review history
- **THEN** metrics не присоединяет later review к earlier record
- **AND** отсутствующая legacy lineage сообщается как `unknown`

### Requirement: Complete totals and explicit unknowns
Episode metrics MUST использовать complete aggregate counters при truncated
bounded samples и MUST отличать unavailable values от numeric zero.

#### Scenario: Long run усекает command samples
- **WHEN** attempt сообщает 455 observed commands, но сохраняет 50 details
- **THEN** episode command totals включают 455, а output сообщает sampling limits
- **AND** detail truncation не уменьшает duration или tool totals

#### Scenario: Token usage недоступен
- **WHEN** один attempt не имеет schema-valid usage data
- **THEN** text/CSV сообщает `unknown`, а JSON — unavailable/null
- **AND** aggregate не считает missing value нулем
