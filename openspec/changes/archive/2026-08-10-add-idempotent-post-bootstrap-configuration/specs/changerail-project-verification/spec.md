## MODIFIED Requirements

### Requirement: Delivery runner auth readiness advisory
`verify-project` MUST report delivery runner Codex auth readiness as a
non-fatal advisory while preserving existing mandatory verification gates.
Missing-auth output MUST identify a real ChangeRail source runbook and provide a
generic executable remediation command for existing-project configuration.

#### Scenario: Consumer has project-local auth marker
- **WHEN** `bin/verify-project /opt/example-project` finds a supported auth
  marker under `/opt/example-project/.codex`
- **THEN** verification reports a passing delivery runner auth readiness
  advisory
- **AND** it does not read or print credential contents

#### Scenario: Consumer relies on auth environment variable
- **WHEN** verification runs with a supported Codex auth environment variable
  set
- **THEN** verification reports a passing delivery runner auth readiness
  advisory
- **AND** it identifies the environment variable name without printing the
  value

#### Scenario: Consumer is missing delivery auth
- **WHEN** required ChangeRail wiring passes but no supported auth marker or
  environment variable is present
- **THEN** `verify-project` exits `0`
- **AND** it reports a warning advisory with a ChangeRail source runbook path
- **AND** it prints a generic `--configure-existing --link-codex-auth` command
  without embedding a local auth source path or credential value

## ADDED Requirements

### Requirement: Existing-project configuration diagnostics
Verification MUST classify whether an auth or wiring remediation is safe for
bounded existing-project configuration and MUST not recommend automatic repair
for project-owned conflicts or unrelated dirty state.

#### Scenario: Missing allowlisted auth marker is repairable
- **WHEN** the ignored auth destination is absent and parent scope is valid
- **THEN** the diagnostic may recommend the configure command

#### Scenario: Destination is project-owned
- **WHEN** the auth or wiring destination contains non-owned content
- **THEN** the diagnostic reports manual owner review
- **AND** it does not recommend automatic overwrite
