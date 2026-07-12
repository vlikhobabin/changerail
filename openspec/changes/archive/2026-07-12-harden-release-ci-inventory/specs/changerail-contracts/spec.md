## ADDED Requirements

### Requirement: Release schema validation gate
ChangeRail release verification MUST validate every public contract schema with
Draft 2020-12 meta-schema checks and fixture-backed document validation.

#### Scenario: Public schema is malformed
- **WHEN** a tracked `schemas/changerail-*.schema.json` file is not a valid
  Draft 2020-12 schema
- **THEN** the release schema validation smoke exits non-zero

#### Scenario: Helper and schema drift apart
- **WHEN** a positive or negative fixture no longer matches the helper-backed
  validation contract for review verdict, review cycle history, delivery
  manifest, delivery run or evidence index
- **THEN** the release schema validation smoke exits non-zero
