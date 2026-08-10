## ADDED Requirements

### Requirement: Verify-project requires complete maintenance schema inventory
`verify-project` MUST require every tracked public maintenance schema for
consumers that have opted in to maintenance wiring.

#### Scenario: Opted-in consumer has complete maintenance schemas
- **WHEN** `bin/verify-project <path>` inspects an opted-in consumer
- **THEN** it checks reachability of `changerail-maintenance-quality-rollup.schema.json`
- **AND** it checks reachability of `changerail-maintenance-proposal-decision.schema.json`
- **AND** those checks are reported alongside the other required maintenance schemas

#### Scenario: Maintenance quality schema is missing
- **WHEN** an opted-in consumer cannot reach `changerail-maintenance-quality-rollup.schema.json`
- **THEN** `verify-project` exits non-zero with a blocking schema failure
- **AND** it does not run a full maintenance scan while diagnosing the missing schema

#### Scenario: Maintenance proposal-decision schema is missing
- **WHEN** an opted-in consumer cannot reach `changerail-maintenance-proposal-decision.schema.json`
- **THEN** `verify-project` exits non-zero with a blocking schema failure
- **AND** it does not report the maintenance opt-in as complete

### Requirement: Generated-copy maintenance contracts fail closed
Generated-copy verification MUST include the full maintenance contract surface
when generated ownership metadata declares maintenance helper or schema wiring.

#### Scenario: Generated-copy maintenance wiring is fresh
- **WHEN** `verify-project` inspects an opted-in generated-copy consumer with fresh maintenance helpers and schemas
- **THEN** the generated-copy verification passes for maintenance helper and schema artifacts
- **AND** the quality-rollup and proposal-decision schema checks pass

#### Scenario: Generated-copy maintenance schema is stale
- **WHEN** a generated-copy maintenance contract artifact is stale or replaced by project-owned content
- **THEN** `verify-project` exits non-zero
- **AND** diagnostics distinguish stale generated-copy drift from project-owned divergence without printing secret-like file contents
