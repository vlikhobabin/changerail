## ADDED Requirements

### Requirement: Delivery progress wire contract
`changerail.delivery-run.v1` и `changerail.delivery-plan-status.v1` MUST
поддерживать один optional объект `changerail.delivery-progress.v1` с bounded
phase/stage enums, date-time heartbeat и non-negative monotonic event counter.
Объект MUST отклонять undeclared content-bearing fields.

#### Scenario: Safe progress проходит валидацию
- **WHEN** status содержит известные phase/stage, valid heartbeat timestamp и
  non-negative event counter
- **THEN** применимая public schema валидирует record
- **AND** aggregate status может mirror объект без semantic conversion

#### Scenario: Content-bearing progress не проходит валидацию
- **WHEN** progress содержит prompts, command bodies, environment values,
  response bodies, raw log excerpts или unknown phase/stage
- **THEN** schema validation fail closed
- **AND** invalid object не публикуется как trusted live progress

### Requirement: Bounded progress health contract
Status contracts MUST представлять progress health через bounded state,
non-negative heartbeat age и process-alive observation, не выдавая diagnostic
terminal или mutation authority.

#### Scenario: Stale health совместим с running result
- **WHEN** schema-valid running record сообщает stale progress health и живой
  process
- **THEN** schema validation проходит
- **AND** `result` остается `RUNNING`, а не выводится только из health
