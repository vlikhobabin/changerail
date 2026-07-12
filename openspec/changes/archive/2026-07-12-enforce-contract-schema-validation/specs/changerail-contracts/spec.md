## ADDED Requirements

### Requirement: Canonical schema-backed validation для contracts
ChangeRail helper validation для delivery manifests и review verdicts MUST
валидировать указанный документ по tracked canonical Draft 2020-12 JSON Schema
до применения ChangeRail-specific semantic rules.

#### Scenario: Manifest нарушает canonical schema
- **WHEN** `scripts/changerail_delivery_manifest.py validate --json` получает
  manifest с unknown fields, invalid date-time formats, wrong nested types или
  missing conditional operation fields
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что manifest valid

#### Scenario: Verdict нарушает canonical schema
- **WHEN** `scripts/changerail_review_verdict.py validate --json` получает
  verdict с unknown fields, invalid date-time formats, wrong nested types или
  malformed nested reviewer/acceptance/finding data
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что verdict valid

#### Scenario: Publish freshness проверяет malformed go verdict
- **WHEN** publish валидирует malformed `go` verdict с `--check-fresh`
- **THEN** validation завершается fail до того, как freshness может разрешить
  staging

### Requirement: Contract schema validation общая для helpers и tests
Helper smoke tests для manifest и verdict validation MUST проверять тот же
schema-backed validation path, который используют CLI helpers, или включать
negative fixtures, которые падают при drift helper validation от tracked schemas.

#### Scenario: Negative fixture нарушает additionalProperties
- **WHEN** smoke fixture добавляет unknown nested field, запрещенный schema
- **THEN** соответствующий helper завершается non-zero

#### Scenario: Negative fixture нарушает date-time format
- **WHEN** smoke fixture использует non-date-time value в schema `format` field
- **THEN** соответствующий helper завершается non-zero
