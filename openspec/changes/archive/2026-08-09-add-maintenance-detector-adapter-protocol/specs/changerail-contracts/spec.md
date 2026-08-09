## ADDED Requirements

### Requirement: Maintenance adapter detector-result contract
ChangeRail detector-result contracts MUST represent adapter-produced findings
and adapter execution errors without language-specific fields.

#### Scenario: Adapter finding validates
- **WHEN** an adapter emits a generic finding with detector id, severity, code,
  message and repository-relative path evidence
- **THEN** the detector-result schema accepts the mapped finding

#### Scenario: Adapter execution error validates separately
- **WHEN** an adapter times out, exits non-zero or emits invalid JSON
- **THEN** the scan report can represent that outcome as a detector error
- **AND** schema validation keeps it separate from ordinary detector findings
