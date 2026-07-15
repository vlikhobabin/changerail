## ADDED Requirements

### Requirement: Queue plan input contract
The delivery runner MUST accept queue plans only through the explicit
`changerail.delivery-plan.v1` contract and MUST preserve existing single-card
runner compatibility.

#### Scenario: Single-card runner remains compatible
- **WHEN** an operator invokes `bin/changerail-delivery-runner run <card>`
- **THEN** the positional card argument is still treated as one card path
- **AND** no queue semantics are inferred from that command

#### Scenario: Queue plan is schema-backed
- **WHEN** an operator invokes a plan-oriented command
- **THEN** the runner validates the plan against
  `schemas/changerail-delivery-plan.schema.json` before applying queue
  semantics

#### Scenario: Queue status is schema-backed
- **WHEN** the runner writes aggregate queue status
- **THEN** the JSON uses `changerail.delivery-plan-status.v1` and validates
  against `schemas/changerail-delivery-plan-status.schema.json`

### Requirement: Queue plan public-safety constraints
The delivery runner MUST fail closed on queue plan values that would put
credentials, secrets or machine-specific tracked state into public plans or
status.

#### Scenario: Workspace path is absolute
- **WHEN** a queue plan workspace path is an absolute machine path
- **THEN** plan validation fails before any child delivery can launch

#### Scenario: Runtime status references logs indirectly
- **WHEN** aggregate queue status includes child evidence
- **THEN** it references structured child status paths and does not inline raw
  stdout or stderr logs
