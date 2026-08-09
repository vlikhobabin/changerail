## ADDED Requirements

### Requirement: Verify-project detects maintenance opt-in
`verify-project` MUST treat tracked maintenance policy, maintenance helper
wiring or generated maintenance ownership declarations as explicit maintenance
opt-in signals.

#### Scenario: Consumer has no maintenance artifacts
- **WHEN** `bin/verify-project <path>` inspects a consumer with no tracked
  maintenance policy, helper wiring or generated ownership declaration
- **THEN** maintenance verification is skipped as not configured
- **AND** the absence of maintenance wiring is not a failure

#### Scenario: Consumer has maintenance policy
- **WHEN** `bin/verify-project <path>` finds a tracked
  `.changerail/maintenance.yaml`
- **THEN** it treats the consumer as opted in to maintenance verification
- **AND** missing required maintenance helper, schema, config or ignore wiring
  is reported as a blocking failure

### Requirement: Verify-project validates opted-in maintenance wiring
Opted-in consumers MUST have complete maintenance helper, schema, config and
ignore wiring, but verification MUST NOT run a full maintenance scan as part of
bootstrap verification.

#### Scenario: Opted-in consumer is complete
- **WHEN** `bin/verify-project <path>` inspects an opted-in consumer with valid
  maintenance policy, reachable maintenance helper wrappers, required schemas
  and ignored runtime paths
- **THEN** verification passes the maintenance wiring check
- **AND** it does not execute `bin/changerail-maintenance scan` as part of that
  check

#### Scenario: Maintenance runtime is not ignored
- **WHEN** an opted-in consumer would allow `.runtime/changerail/maintenance/`
  content to be tracked
- **THEN** `verify-project` reports a blocking failure
- **AND** it does not print raw runtime report contents

### Requirement: Verify-project validates maintenance generated copies
`verify-project` MUST include maintenance helper copies in generated Windows
wiring freshness checks when a consumer declares generated maintenance wiring.

#### Scenario: Generated maintenance helper is fresh
- **WHEN** `verify-project` inspects an opted-in generated Windows consumer
- **THEN** maintenance helper copies match recorded source identity and digest
- **AND** the generated wiring check passes

#### Scenario: Generated maintenance helper is stale or project-owned
- **WHEN** a generated maintenance helper is missing, stale or replaced by
  project-owned content
- **THEN** `verify-project` exits non-zero
- **AND** diagnostics distinguish stale generated-copy drift from
  project-owned divergence
