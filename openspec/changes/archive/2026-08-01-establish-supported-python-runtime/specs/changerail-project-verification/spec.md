## ADDED Requirements

### Requirement: Verify-project uses shared Python runtime
`bin/verify-project` MUST execute through the shared ChangeRail Python runtime
selector before project verification imports or checks run.

#### Scenario: Verify-project starts on supported runtime
- **WHEN** an operator runs `bin/verify-project /opt/example-project` with a
  supported Python runtime and required runtime modules
- **THEN** the shared selector starts the verifier
- **AND** project wiring verification proceeds normally

#### Scenario: Verify-project sees unsupported runtime
- **WHEN** an operator runs `bin/verify-project /opt/example-project` with an
  unsupported selected interpreter
- **THEN** verification exits non-zero before project checks run
- **AND** the diagnostic describes the supported Python runtime and remediation
