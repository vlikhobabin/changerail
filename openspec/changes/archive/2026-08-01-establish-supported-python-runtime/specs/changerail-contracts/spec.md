## ADDED Requirements

### Requirement: Contract helpers use shared Python runtime
Delivery manifest and review verdict helper entrypoints MUST execute through
the shared ChangeRail Python runtime selector before schema-backed helper code
imports runtime dependencies.

#### Scenario: Review verdict helper starts on supported runtime
- **WHEN** an operator invokes the review verdict helper through the ChangeRail
  runtime entrypoint
- **THEN** the shared selector validates the interpreter and required modules
- **AND** verdict validation or fingerprint behavior proceeds normally

#### Scenario: Delivery manifest helper starts on supported runtime
- **WHEN** delivery, review or publish invokes the delivery manifest helper
  through the ChangeRail runtime entrypoint
- **THEN** the shared selector validates the interpreter and required modules
- **AND** manifest derive, validate, staging-plan, finalize-card or
  publish-update behavior proceeds normally

#### Scenario: Contract helper dependency is missing
- **WHEN** the selected interpreter lacks `jsonschema`
- **THEN** contract helper invocation exits non-zero before schema-backed code
  imports
- **AND** the diagnostic names `jsonschema` as the missing runtime dependency
