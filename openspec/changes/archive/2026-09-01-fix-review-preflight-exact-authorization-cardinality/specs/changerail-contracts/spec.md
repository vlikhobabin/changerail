## MODIFIED Requirements

### Requirement: Published investigation authorization for deterministic preflight
Deterministic preflight SHALL принимать inline JSON
`Published investigation authorization` только как однозначную bounded chain.
Legacy absence field или ровно одно значение `none` означает
`not-declared`; non-default authorization MUST находиться в единственном
`## Review` section и единственном exact field. Reference MUST быть одним JSON
object с ровно двумя уникальными decoded keys `authorization_card` и
`authorization_id`, значения которых являются non-empty strings и указывают на
clean unchanged tracked `HEAD` artifact в `4.done` с exact path/id/status.

Published source MUST иметь единственный `## Authorization` section и
единственный exact `Investigation authorization` field. Source JSON MUST быть
одним object с ровно шестью уникальными decoded keys `investigation_card`,
`investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` и `allow_new_authority_or_wire_protocol`. Identity
values MUST быть non-empty strings, ceiling MUST быть integer-not-boolean от
301 до 500, protocol allowance MUST быть boolean, а exact current successor и
published investigation path/id/status/tracked state MUST совпадать до выдачи
authority.

Каждый проверяемый `## Depends On`/`## Blocks` MUST существовать ровно в одном
second-level section. Authorization source `Depends On` MUST содержать ровно
одну dependency — exact investigation. Successor `Depends On` и investigation
`Blocks` MUST содержать expected edge ровно один раз, но MAY сохранять другие
legitimate dependencies/targets. Relation reference совпадает только как exact
bare `<id>`, `<id>.md` или canonical
`openspec/board/<lane>/<id>.md`; duplicate equivalent expected forms, missing,
mismatch, foreign stem и non-board path не удовлетворяют edge.

Duplicate field/section/decoded key, missing/extra JSON key, invalid type,
duplicate expected edge и extra authorization-source dependency MUST вернуть
authorization `invalid`, outcome `investigation-required` и запретить semantic
review eligibility. Этот active exact-cardinality contract supersedes прежнюю
multi-candidate tolerance для нескольких exact source fields: clean published
authorization source содержит ровно один object; JSON вне exact field не
является candidate. Все остальные production LOC, ceiling, protocol,
repeated-defect, scope, freshness и risk gates остаются независимыми и
fail-closed.

#### Scenario: Exact published chain допускает bounded successor
- **WHEN** successor содержит ровно один schema-valid two-field reference,
  source содержит ровно один schema-valid six-field object и три required
  relation edges однозначно связывают clean published cards
- **THEN** preflight применяет только declared LOC, repeated-defect и protocol
  decisions к exact successor
- **AND** ordinary payload в пределах ceiling получает
  `ready-for-llm-review` с route `high`

#### Scenario: Duplicate или extra authorization structure отклоняется
- **WHEN** successor reference или source field/section повторяется, JSON
  содержит duplicate decoded key, missing/extra key либо value неверного type
- **THEN** authorization имеет `status: invalid`
- **AND** preflight возвращает exit `1`, outcome `investigation-required` и
  `llm_review.required: false` до semantic review

#### Scenario: Authorization source имеет ambiguous dependency
- **WHEN** source `Depends On` отсутствует, повторен, ссылается не на exact
  investigation либо содержит второй dependency item/reference
- **THEN** source не выдает bounded authority
- **AND** preflight возвращает `investigation-required` без semantic review

#### Scenario: Shared board relations сохраняют совместимость
- **WHEN** exact successor dependency встречается ровно один раз рядом с
  unrelated successor dependencies либо exact investigation `Blocks` edge
  встречается ровно один раз рядом с другими blocked targets
- **THEN** unrelated relations не делают exact authorization invalid
- **AND** duplicate equivalent form самого required edge остается invalid

#### Scenario: Published card использует filename reference
- **WHEN** required relation использует exact `<id>.md` или canonical board path
  с этим filename
- **THEN** preflight нормализует его в exact card id
- **AND** другой stem или noncanonical path не совпадает с required edge

#### Scenario: Repeated defect не имеет valid authorization
- **WHEN** successor объявляет repeated defect, а authorization отсутствует,
  unreadable, stale, unpublished, ambiguous или не связывает exact successor
- **THEN** preflight возвращает `investigation-required`
- **AND** LLM не запускается и authority не выводится из prose

#### Scenario: Successor превышает published ceiling
- **WHEN** valid authorization объявляет ceiling 500, но successor добавляет
  больше 500 production LOC
- **THEN** preflight возвращает `investigation-required`
- **AND** result называет превышенный explicit ceiling

#### Scenario: Successor не имеет protocol allowance
- **WHEN** valid authorization связывает exact successor, но boolean protocol
  allowance равен false, а successor объявляет новый authority/wire protocol
- **THEN** preflight возвращает `investigation-required`
- **AND** valid relation/repeated authorization не переопределяет protocol
  decision

#### Scenario: Ранее допускавшийся второй exact source field больше не выбирается
- **WHEN** clean source содержит canonical matching object и второй exact
  `Investigation authorization` field, включая unrelated object
- **THEN** preflight отклоняет source по field cardinality вместо target
  selection
- **AND** JSON examples вне exact field остаются ignored и не влияют на
  authorization cardinality
