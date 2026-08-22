## ADDED Requirements

### Requirement: Episode and attempt identity contract
Runtime owner schemas MUST использовать schema-valid episode ids и typed
attempt objects с unique ids и optional parent/previous links. Links MUST
разрешаться внутри одного workspace/card/episode и MUST отклонять cycles или
conflicting duplicate attempt ids.

#### Scenario: Cross-artifact lineage проходит валидацию
- **WHEN** delivery status, review history и manifest используют один episode id
  и distinct linked attempt ids
- **THEN** contract validation и episode materialization проходят
- **AND** каждый source остается authoritative для owned fields

#### Scenario: Cross-episode link fail closed
- **WHEN** attempt ссылается на parent/previous id другого episode либо duplicate
  id имеет другое content
- **THEN** episode refresh сообщает contract conflict
- **AND** не merge ambiguous attempts

### Requirement: Derived delivery episode record
`changerail.delivery-episode.v1` MUST быть ignored public-safe derived index
schema-valid attempt summaries и indirect owner-artifact references. Он MUST
NOT включать prompts, raw commands, MCP payloads, screenshots, source content
или raw logs.

#### Scenario: Episode refresh объединяет owner artifacts
- **WHEN** matching delivery, review и publish artifacts существуют для одного
  episode
- **THEN** refresh атомарно пишет ordered attempt summaries и final lifecycle
  state
- **AND** detailed evidence остается referenced через normalized ignored paths

#### Scenario: Legacy run не имеет explicit lineage
- **WHEN** reader встречает valid legacy delivery run без episode fields
- **THEN** он может показать isolated synthetic episode для этого run
- **AND** missing lineage и later review/publish data остаются `unknown`

### Requirement: Sampling and duration contract
Performance/episode schemas MUST отличать complete aggregate totals от bounded
detail samples и MUST явно представлять incomplete intervals.

#### Scenario: Detail sample усечен
- **WHEN** retained detail count меньше observed count
- **THEN** record объявляет truncation и sample limit
- **AND** aggregate totals остаются valid для complete observed set
