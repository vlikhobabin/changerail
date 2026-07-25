## ADDED Requirements

### Requirement: Delivery runner auth readiness advisory
`verify-project` MUST report delivery runner Codex auth readiness as a
non-fatal advisory while preserving existing mandatory verification gates.

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
- **AND** it reports a warning advisory with the next remediation step for
  delivery runner readiness
