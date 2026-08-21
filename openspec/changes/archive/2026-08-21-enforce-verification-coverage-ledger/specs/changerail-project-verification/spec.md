## ADDED Requirements

### Requirement: Deterministic verification coverage preflight
Review preflight MUST fail closed до model launch, когда configured coverage map,
per-change plan или runtime ledger invalid, stale, scope-incomplete либо не
содержит required observed evidence.

#### Scenario: Ledger fresh и complete
- **WHEN** map/plan/card/manifest/review fingerprints совпадают и каждая
  applicable entry имеет schema-valid fresh evidence required kinds
- **THEN** coverage process check проходит
- **AND** deterministic check не расходует semantic review budget

#### Scenario: Evidence направлен на internal disconnected path
- **WHEN** process contract complete, но linked test/oracle не exercise
  published boundary или connected integration route
- **THEN** deterministic identity check не придумывает semantic pass
- **AND** independent reviewer MUST оценить и может block test adequacy

#### Scenario: Coverage map не настроена
- **WHEN** project не имеет reference `verification.coverage_map`
- **THEN** preflight использует current project-declared verification floor
- **AND** не требует generated coverage artifacts
