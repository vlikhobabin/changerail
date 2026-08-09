## ADDED Requirements

### Requirement: Maintenance scan report contract schemas
ChangeRail MUST publish Draft 2020-12 JSON Schemas for maintenance scan reports
and detector results using canonical ids `changerail.maintenance-scan-report.v1`
and `changerail.maintenance-detector-result.v1`.

#### Scenario: Maintainer lists maintenance scan schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.maintenance-scan-report.v1`
- **AND** schemas exist for `changerail.maintenance-detector-result.v1`

#### Scenario: Scan report separates diagnostics
- **WHEN** a maintenance scan report contains raw detector findings, detector
  execution errors and configuration diagnostics
- **THEN** schema validation preserves those as distinct fields
- **AND** rejects unknown contract-owned fields

#### Scenario: Contract schema smoke covers scan schemas
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** the smoke validates representative positive and negative documents
  for maintenance scan report and detector result schemas
