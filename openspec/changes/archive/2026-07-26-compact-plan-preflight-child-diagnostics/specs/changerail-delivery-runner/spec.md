## MODIFIED Requirements

### Requirement: Queue preflight aggregate status
The delivery runner MUST write schema-backed aggregate status for plan preflight
and status inspection, and MUST surface child preflight failures as compact
operator diagnostics without embedding raw child logs.

#### Scenario: Preflight succeeds
- **WHEN** `preflight-plan` validates every workspace, card and dependency
- **THEN** aggregate status records `DELIVERED` as the preflight result, the
  plan fingerprint and all resolved card states without child run references

#### Scenario: Operator reads status
- **WHEN** an operator invokes `status-plan` for a prior queue run or preflight
- **THEN** the command reads the aggregate status record and reports structured
  queue state without parsing raw child stdout or stderr

#### Scenario: Child preflight failure summary is compact
- **WHEN** `preflight-plan` observes a child preflight check failure
- **THEN** aggregate operator output reports the card id, failing check name,
  `fail` status and a short reason
- **AND** the output does not rely on a truncated child JSON blob

#### Scenario: Child preflight evidence remains referenced
- **WHEN** aggregate status records a child preflight failure
- **THEN** the corresponding card entry includes a concise `reason` and a
  `run_status_path` reference to the child `changerail.delivery-run.v1` status
  record
- **AND** aggregate status does not inline raw stdout or stderr logs

#### Scenario: JSON status remains schema-compatible
- **WHEN** `status-plan --json` reads aggregate status with compact child
  diagnostics
- **THEN** the emitted JSON still validates against
  `schemas/changerail-delivery-plan-status.schema.json`
