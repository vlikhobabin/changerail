## ADDED Requirements

### Requirement: Structured live delivery progress
Delivery runner MUST публиковать optional
`changerail.delivery-progress.v1` для работающего single-card child на основе
валидированных lifecycle events и bounded activity heartbeat. Runner MUST NOT
выводить lifecycle transition из свободного prose, текста command или output.

#### Scenario: Lifecycle transition обновляет running status
- **WHEN** matching child отправляет schema-valid progress event для major
  transition `ff`, `do`, `review` или `publish`
- **THEN** runner атомарно обновляет `progress.phase`, `progress.stage`,
  `heartbeat_at` и monotonic `event_counter`
- **AND** существующие semantics `phase: delivery` и `result: RUNNING` не
  меняются

#### Scenario: Недоверенный content не является progress
- **WHEN** child prose, shell command или command output содержит текст,
  похожий на lifecycle phase или secret-bearing value
- **THEN** runner не копирует это значение в progress
- **AND** phase/stage может изменить только validated value-free lifecycle event

### Requirement: Stale heartbeat is a non-terminal diagnostic
Delivery runner MUST оценивать heartbeat age вместе с observed process state и
MUST NOT завершать или классифицировать живой child только из-за одного
пропущенного heartbeat interval.

#### Scenario: Живой child пропускает heartbeat interval
- **WHEN** heartbeat age превышает documented stale threshold, а child process
  остается живым
- **THEN** status сообщает bounded health `stale` и heartbeat age
- **AND** terminal outcome остается unset до появления существующего terminal
  evidence

#### Scenario: Child завершается после stale heartbeat
- **WHEN** process завершается после перехода heartbeat в stale
- **THEN** runner определяет terminal result через существующий terminal
  protocol
- **AND** progress health может сообщить termination, не заменяя result
