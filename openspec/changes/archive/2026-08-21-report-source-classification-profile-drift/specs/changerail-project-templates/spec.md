## ADDED Requirements

### Requirement: Explicit source classification profile lifecycle guidance
Generated project guidance MUST документировать `detect -> review ->
materialize -> check`, preview-before-write, tracked classification authority,
local profile ownership и explicit migration без hidden stack activation.

#### Scenario: Consumer добавляет specialized source
- **WHEN** project или domain integration добавляет profile для specialized
  language/structured source
- **THEN** guidance направляет maintainers проверить candidate signals и preview
  final rules до записи project policy
- **AND** ordinary review/delivery никогда не auto-accept detected profile

#### Scenario: Existing classification отличается
- **WHEN** materialize/check находит existing divergent project file
- **THEN** guidance требует separate explicit reviewed migration decision
- **AND** не предлагает force overwrite или automatic Git commit
