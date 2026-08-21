## ADDED Requirements

### Requirement: Live-progress authorization MUST bind exact successor
ChangeRail MUST принимать live-progress protocol authorization только для exact
`expose-structured-live-delivery-progress` successor in `3.inprogress`, bound к
published batch investigation, с ceiling 500 и protocol allowance true.

#### Scenario: Exact live-progress chain
- **WHEN** source, investigation и successor reciprocal links совпадают
- **THEN** preflight принимает bounded protocol exception

#### Scenario: Mismatched telemetry payload
- **WHEN** другая card/path или broader authority ссылается на source
- **THEN** preflight сохраняет `investigation-required`
