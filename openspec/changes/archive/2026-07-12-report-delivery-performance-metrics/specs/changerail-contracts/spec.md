## ADDED Requirements

### Requirement: Delivery run schema fixtures cover performance fields
ChangeRail contract schema validation MUST cover delivery run performance and
usage breakdown fields used by runner and metrics helpers.

#### Scenario: Positive fixture includes performance data
- **WHEN** release schema smoke validates a delivery run fixture with
  performance summary and usage breakdown fields
- **THEN** `schemas/changerail-delivery-run.schema.json` accepts the fixture

#### Scenario: Optional timing fields are absent
- **WHEN** release schema smoke validates a delivery run fixture without
  optional performance fields
- **THEN** the fixture remains valid when required base status fields are present
