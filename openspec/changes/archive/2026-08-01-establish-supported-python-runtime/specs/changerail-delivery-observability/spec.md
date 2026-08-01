## ADDED Requirements

### Requirement: Delivery metrics uses shared Python runtime
`bin/changerail-delivery-metrics` MUST execute through the shared ChangeRail
Python runtime selector before reading structured runtime records.

#### Scenario: Metrics starts with supported runtime
- **WHEN** an operator invokes `bin/changerail-delivery-metrics`
- **THEN** the shared selector validates the interpreter and required modules
- **AND** metrics output behavior proceeds normally

#### Scenario: Metrics selected runtime is unsupported
- **WHEN** the selected interpreter is older than Python 3.11 or lacks required
  runtime modules
- **THEN** metrics exits non-zero before reading delivery records
- **AND** the diagnostic describes the runtime remediation
