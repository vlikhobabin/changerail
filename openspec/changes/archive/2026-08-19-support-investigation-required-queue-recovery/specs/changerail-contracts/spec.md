## ADDED Requirements

### Requirement: Queue retained recovery status metadata
`changerail.delivery-plan-status.v1` MUST represent
`investigation_required` recovery with bounded structured metadata. Aggregate
card status MUST be able to identify the recovery kind, source run status path,
source terminal reason and retained-payload fingerprint summary without
embedding raw child logs or raw source payload.

#### Scenario: Aggregate status records retained recovery context
- **WHEN** `resume-plan` evaluates a prior `investigation_required` child
- **THEN** aggregate status records a bounded reference to the prior child
  status and retained-payload fingerprint summary
- **AND** schema validation succeeds without raw child stdout/stderr content

#### Scenario: Duplicate recovery paths fail closed
- **WHEN** aggregate status or current plan would attach more than one active
  recovery path to the same `investigation_required` source
- **THEN** queue validation records `BLOCKED`
- **AND** it identifies the duplicate recovery as a stable machine reason

### Requirement: Queue recovery terminal reasons are stable
Queue retained recovery MUST use stable lowercase machine reasons for rejected
resume or recovery augmentation. The contract MUST cover missing prior status,
invalid prior status, wrong card, wrong workspace, missing retained identity,
fingerprint drift, stale authorization and duplicate recovery path.

#### Scenario: Failed queue recovery is machine-readable
- **WHEN** `resume-plan` rejects an `investigation_required` recovery
- **THEN** aggregate status contains `result: BLOCKED`
- **AND** the affected card status contains a stable terminal reason or reason
  detail that identifies the rejected class

#### Scenario: Downstream blocked state is explicit
- **WHEN** a downstream card depends on an `investigation_required` source that
  is not delivered or recovered
- **THEN** aggregate status keeps the downstream card pending or blocked
- **AND** it does not infer success from the presence of an authorization card
  alone
