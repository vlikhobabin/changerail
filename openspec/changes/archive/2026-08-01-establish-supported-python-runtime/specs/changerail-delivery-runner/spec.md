## ADDED Requirements

### Requirement: Delivery runner uses shared Python runtime
`bin/changerail-delivery-runner` MUST execute every subcommand through the
shared ChangeRail Python runtime selector.

#### Scenario: Runner starts with supported runtime
- **WHEN** an operator invokes `bin/changerail-delivery-runner run <card>`
- **THEN** the shared selector validates the interpreter and required modules
- **AND** runner preflight or delivery launch behavior proceeds normally

#### Scenario: Runner override is invalid
- **WHEN** `CHANGERAIL_PYTHON` points to an invalid interpreter and an operator
  invokes any delivery runner subcommand
- **THEN** the runner exits non-zero before preflight or delivery child launch
- **AND** the diagnostic identifies the invalid override
