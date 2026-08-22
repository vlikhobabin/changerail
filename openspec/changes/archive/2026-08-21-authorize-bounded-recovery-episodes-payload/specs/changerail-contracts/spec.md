## ADDED Requirements

### Requirement: Recovery-episodes authorization MUST bind exact successor
ChangeRail MUST принимать episode/attempt protocol authorization только для
exact `report-recovery-aware-delivery-episodes` successor in `3.inprogress`,
bound к published batch investigation, с aggregate ceiling 500 и protocol
allowance true.

#### Scenario: Exact episode chain
- **WHEN** reciprocal links совпадают и aggregate production delta <=500
- **THEN** preflight применяет bounded exception

#### Scenario: Raw-log telemetry added
- **WHEN** payload добавляет content-bearing/raw-log reconstruction или другой
  successor ссылается на source
- **THEN** authorization неприменима
