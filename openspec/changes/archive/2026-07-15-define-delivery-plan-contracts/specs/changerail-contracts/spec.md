## ADDED Requirements

### Requirement: Delivery plan contract
ChangeRail MUST define a public schema-backed `changerail.delivery-plan.v1`
contract for declarative multi-workspace delivery queue plans.

#### Scenario: Maintainer lists contract schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.delivery-plan.v1` and
  `changerail.delivery-plan-status.v1`

#### Scenario: Plan uses public-safe workspace references
- **WHEN** a delivery plan declares workspaces
- **THEN** each workspace uses a stable alias and a consumer-root-relative path
- **AND** the plan schema rejects machine-specific absolute workspace paths

#### Scenario: Plan rejects credential-bearing values
- **WHEN** a delivery plan contains URL userinfo, password-like fields,
  token-like fields or secret-bearing runtime state
- **THEN** schema-backed validation fails before runner semantic validation

#### Scenario: Plan declares cards and dependencies
- **WHEN** a delivery plan is valid
- **THEN** every card has a stable id, workspace alias, card path or filename,
  optional dependencies, optional wave and optional per-card model or reasoning
  override

### Requirement: Delivery plan status contract
ChangeRail MUST define a public schema-backed
`changerail.delivery-plan-status.v1` contract for aggregate queue status.

#### Scenario: Queue status references child records
- **WHEN** a queue run starts or updates aggregate state
- **THEN** the status record includes the plan fingerprint, per-card states and
  references to child `changerail.delivery-run.v1` status records when those
  child records exist

#### Scenario: Queue status records terminal outcome
- **WHEN** a queue run reaches a terminal state
- **THEN** the status record records terminal outcome `DELIVERED`, `NO-GO` or
  `BLOCKED`
- **AND** it records whether the run used push-enabled or explicit `--no-push`
  success criteria

#### Scenario: Queue runtime remains ignored
- **WHEN** a queue status record is written
- **THEN** the default path is under ignored `.runtime/changerail/`
- **AND** the status schema does not require raw logs or secrets

### Requirement: Delivery plan schema fixtures
ChangeRail contract schema validation MUST cover delivery plan and delivery
plan status schemas in the public schema smoke suite.

#### Scenario: Positive fixtures validate
- **WHEN** release schema smoke validates representative delivery plan and plan
  status fixtures
- **THEN** both fixtures validate against their tracked schemas

#### Scenario: Negative fixture violates plan safety
- **WHEN** release schema smoke validates a delivery plan with an absolute
  workspace path or duplicate identifier
- **THEN** the fixture fails schema or semantic validation
