## ADDED Requirements

### Requirement: Actionable auth remediation diagnostics
Delivery runner preflight MUST keep missing-auth and stale-symlink checks
fail-closed while reporting concise remediation guidance that does not expose
credential contents.

#### Scenario: Auth marker is missing
- **WHEN** delivery runner preflight finds no supported auth marker and no
  supported auth environment variable
- **THEN** the `CODEX auth` check fails
- **AND** its message points to the project-local auth marker, explicit
  `CODEX_HOME` or supported auth environment variable remediation path

#### Scenario: Auth symlink is stale
- **WHEN** delivery runner preflight finds a broken symlink under effective
  `CODEX_HOME`
- **THEN** the `CODEX_HOME symlinks` check fails
- **AND** its message identifies stale symlink diagnostics and points to the
  auth setup remediation path

#### Scenario: Diagnostics stay sanitized
- **WHEN** runner preflight records auth remediation diagnostics
- **THEN** structured status does not include credential file contents,
  environment variable values or token-like secret values
