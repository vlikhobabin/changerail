## ADDED Requirements

### Requirement: Queue resume after investigation-required child
The delivery runner MUST allow `resume-plan` to represent recovery from a prior
child with `terminal_reason: investigation_required` only when the prior child
status is schema-valid, belongs to the same workspace/card source and contains
matching retained-payload identity.

#### Scenario: Queue resumes original retained payload
- **WHEN** aggregate status contains a child `BLOCKED` with
  `terminal_reason: investigation_required`
- **AND** the child status contains matching retained-payload identity
- **AND** the current plan fingerprint is unchanged
- **THEN** `resume-plan` may launch single-card
  `resume --status-path <prior-child-status>` for that original card
- **AND** downstream cards remain blocked until that child publishes
  successfully

#### Scenario: Queue accepts one replacement recovery card
- **WHEN** the current plan adds one recovery card for a prior
  `investigation_required` source
- **AND** all previous card identity, workspace, card reference, wave and
  dependencies are preserved
- **AND** the recovery card is same-workspace, same-wave and inherits the source
  dependencies
- **THEN** `resume-plan` accepts the recovery augmentation
- **AND** it launches the recovery before dependants of the source

#### Scenario: Queue blocks unsafe investigation recovery
- **WHEN** prior child status is missing, schema-invalid, from another
  workspace/card, lacks retained-payload identity or no longer matches the
  current retained payload
- **THEN** `resume-plan` records `BLOCKED`
- **AND** it exits non-zero before launching the source or downstream cards

### Requirement: Queue recovery keeps downstream blocked
Queue recovery from `investigation_required` MUST NOT satisfy downstream
dependencies until the original retained payload or its explicit replacement
has passed the risk-appropriate independent review and publish checks.

#### Scenario: Original retained payload publishes successfully
- **WHEN** retained-payload resume returns `DELIVERED` and normal queue
  publish-state checks pass
- **THEN** aggregate status may mark the source delivered
- **AND** only then may downstream dependencies treat that source as satisfied

#### Scenario: Replacement recovery publishes successfully
- **WHEN** a valid recovery card returns `DELIVERED` and normal queue
  publish-state checks pass
- **THEN** aggregate status marks the source `recovered` and records
  `recovered_by`
- **AND** only then may downstream dependencies treat that source as satisfied

#### Scenario: Recovery fails closed
- **WHEN** retained-payload resume or replacement recovery returns `NO-GO`,
  `BLOCKED` or inconsistent publish state
- **THEN** aggregate queue status remains fail-fast
- **AND** no source dependants are launched

### Requirement: Queue retained recovery smoke coverage
ChangeRail MUST include focused synthetic smoke coverage for
`investigation_required` queue recovery.

#### Scenario: Smokes cover success and adversarial cases
- **WHEN** the queue recovery smoke suite runs
- **THEN** it covers successful retained recovery
- **AND** it covers dirty state, stale authorization, wrong card, wrong
  workspace and fingerprint drift failures
