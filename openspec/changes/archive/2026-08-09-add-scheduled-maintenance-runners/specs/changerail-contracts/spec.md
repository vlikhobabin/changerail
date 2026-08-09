## ADDED Requirements

### Requirement: Maintenance run status contract
ChangeRail MUST define a public `changerail.maintenance-run.v1` contract for
machine-readable maintenance runner status, phases, results, timestamps,
report references, annotation references and bounded execution diagnostics.

#### Scenario: Runner writes maintenance status
- **WHEN** the maintenance runner writes
  `.runtime/changerail/maintenance/runs/<run-id>/status.json`
- **THEN** the JSON uses `changerail.maintenance-run.v1`
- **AND** it includes workspace metadata, mode, phase, result, timestamps,
  command metadata, lock diagnostics, timeout diagnostics and optional usage
  availability

#### Scenario: Status references reports indirectly
- **WHEN** scan mode completes and report output is retained
- **THEN** the status references repository-relative ignored runtime paths for
  scan/report artifacts
- **AND** it does not inline raw command logs, credentials or local runtime
  traces

### Requirement: Maintenance run schema validation
ChangeRail MUST publish a Draft 2020-12 JSON Schema for
`changerail.maintenance-run.v1` and include fixture-backed validation in the
public contract smoke suite.

#### Scenario: Maintainer lists maintenance run schema
- **WHEN** the tracked `schemas/` directory is listed
- **THEN** `schemas/changerail-maintenance-run.schema.json` exists

#### Scenario: Contract smoke validates maintenance run fixture
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** it validates a representative successful scan-mode
  `changerail.maintenance-run.v1` fixture
- **AND** it rejects a malformed fixture with unknown contract-owned fields or
  invalid timestamp values

### Requirement: Maintenance runner control flow uses structured status
Maintenance runner supervisors MUST determine terminal state from
`changerail.maintenance-run.v1` fields, not from scraped human prose.

#### Scenario: Scan command exits successfully
- **WHEN** deterministic scan/report command exits zero and produces
  schema-valid output
- **THEN** runner status records a successful result from structured command
  outcome and artifact validation

#### Scenario: Human prose conflicts with structured output
- **WHEN** child output contains human text that resembles success but required
  schema-valid artifacts are missing
- **THEN** runner status records failure or blocked diagnostics
- **AND** the supervisor does not treat the run as successful
