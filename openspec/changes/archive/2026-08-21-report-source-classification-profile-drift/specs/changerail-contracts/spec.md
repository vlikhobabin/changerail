## ADDED Requirements

### Requirement: Source classification profile check report
ChangeRail MUST выдавать schema-valid
`changerail.source-classification-check.v1` с selected profile identities,
source/checksum state, declared project overrides, effective rule summary,
bounded covered/excluded/uncovered counts и diagnostics. Report MUST NOT
включать source contents или machine-absolute paths.

#### Scenario: Final file совпадает с profile и declared overrides
- **WHEN** profile baseline available и все final differences находятся только
  в exact declared override paths
- **THEN** check сообщает matching provenance и named project overrides
- **AND** effective rules берутся из final project classification

#### Scenario: Profile divergence не объявлен
- **WHEN** final rule отличается от confirmed selected profile вне declared
  override paths либо same profile id/version имеет другой checksum
- **THEN** check сообщает blocking `confirmed_profile_drift`
- **AND** не rewrite и не silently merge file

### Requirement: Detection-only drift has no risk authority
Unaccepted candidate и uncovered-source diagnostics MUST оставаться value-free
и advisory, пока не доказывают divergence от explicitly selected schema-valid
profile. Advisory detection MUST NOT менять current source classification или
risk calculation.

#### Scenario: Unknown suffix указывает на candidate
- **WHEN** tracked HEAD содержит path signals для unaccepted profile, не covered
  built-in/final rules
- **THEN** check сообщает bounded confidence, counts и capped normalized path
  examples как advisory
- **AND** `added_production_loc` и review route используют final classification

#### Scenario: Selected profile rule больше не покрывает matching source
- **WHEN** confirmed selected profile требует source rule, но final project
  classification omits его без declared override
- **THEN** check сообщает blocking drift
- **AND** preflight не может считать omission lower-risk payload
