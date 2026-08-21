## ADDED Requirements

### Requirement: Delivery episode and attempt lineage
ChangeRail runner MUST назначать stable episode id одному card execution и
unique typed attempt id каждому preflight, delivery или recovery process.
Resume MUST наследовать source episode и ссылаться на source attempt;
unrelated new execution той же карточки MUST начинать другой episode.

#### Scenario: Blocked child возобновляется
- **WHEN** schema-valid blocked attempt возобновляется через supported
  single-card или plan workflow
- **THEN** resumed status сохраняет source `episode_id`, использует новый
  recovery attempt id и связывает previous/source attempt
- **AND** card/workspace/episode identity проверяется до launch

#### Scenario: Та же карточка начинает unrelated execution
- **WHEN** оператор запускает new run без authorized source status
- **THEN** runner создает новый episode id
- **AND** prior attempts и review cycles не присоединяются только по card id

### Requirement: Complete aggregate performance with bounded samples
Runner MUST сохранять aggregate counts и durations всех observed commands,
tools и structured phases, даже когда detailed samples bounded. Он MUST
указывать observed count, retained count, sample limit и truncation state.

#### Scenario: Long run превышает detail limits
- **WHEN** command или timeline details превышают configured retained limits
- **THEN** aggregate counts и durations по-прежнему включают каждый observed
  item
- **AND** sample metadata сообщает truncation и effective limits

#### Scenario: Наблюдается structured operator wait
- **WHEN** lifecycle записывает value-free external/operator wait transition
- **THEN** performance totals классифицируют duration отдельно от active time
- **AND** entered value, screen content и external response не сохраняются
