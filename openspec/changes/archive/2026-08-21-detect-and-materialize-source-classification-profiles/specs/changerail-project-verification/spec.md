## ADDED Requirements

### Requirement: Materialized source classification verification
Project verification MUST валидировать materialized source classification и
optional profile provenance через public schemas, сохраняя legacy files без
provenance.

#### Scenario: Materialized classification valid
- **WHEN** helper создает project file из selected profiles
- **THEN** project verification и review preflight принимают schema/final rules
- **AND** report показывает profile id/version/checksum без source content

#### Scenario: Provenance malformed
- **WHEN** profile checksum, source kind или override path invalid
- **THEN** project verification сообщает blocking policy error
- **AND** review preflight не игнорирует malformed provenance
