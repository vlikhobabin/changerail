## ADDED Requirements

### Requirement: Generated Windows wiring verification matrix
The native Windows generated-copy default MUST have deterministic verification
coverage for fresh, stale, missing, diverged and refreshed generated artifacts
before ChangeRail claims the generated wiring model is enforced.

#### Scenario: Generated wiring enforcement is verified locally
- **WHEN** the local release baseline runs generated wiring verifier smoke
- **THEN** deterministic fixtures cover valid generated content, stale copies,
  missing generated files, project-owned divergence and successful refresh

#### Scenario: Generated wiring diagnostics are sanitized
- **WHEN** verifier or drift diagnostics report generated Windows wiring
  failures
- **THEN** they avoid credential values, private hostnames and private Windows
  absolute paths
