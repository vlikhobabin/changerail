## ADDED Requirements

### Requirement: Generated wiring freshness diagnostics
Wiring discovery diagnostics consumed by verification and drift gates MUST
distinguish fresh, stale, missing and project-owned generated Windows wiring.

#### Scenario: Generated wiring diagnostics are fresh
- **WHEN** a generated Windows consumer has manifest-owned artifacts that match
  the ChangeRail source identity and digest
- **THEN** diagnostics identify the generated-copy mode as fresh

#### Scenario: Generated wiring diagnostics are stale or missing
- **WHEN** a generated Windows consumer has stale or missing manifest-owned
  artifacts
- **THEN** diagnostics identify the affected project-relative path
- **AND** diagnostics include a refresh remediation without copying raw source
  content into tracked output

#### Scenario: Generated wiring diagnostics see project-owned content
- **WHEN** a generated Windows wiring destination contains project-owned content
  or lacks generated ownership metadata
- **THEN** diagnostics identify project-owned divergence separately from stale
  generated-copy drift
