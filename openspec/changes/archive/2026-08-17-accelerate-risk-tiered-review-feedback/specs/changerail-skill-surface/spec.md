## ADDED Requirements

### Requirement: Review skill runs deterministic preflight first
The canonical review and deliver skills MUST run deterministic review preflight
before launching an independent LLM payload reviewer.

#### Scenario: Preflight returns a process blocker
- **WHEN** preflight reports a manifest, board, archive, scope, freshness or
  locally available strict-check defect
- **THEN** the lifecycle returns the machine blocker to delivery
- **AND** it does not launch an LLM or consume implementation review budget

#### Scenario: Preflight routes semantic review
- **WHEN** machine gates pass and semantic payload review is required
- **THEN** the lifecycle uses `high` for ordinary risk or `xhigh` for critical
  risk
- **AND** no generic model-launch layer is required

## MODIFIED Requirements

### Requirement: Publish skill requires review gate by default
`changerail-pub` MUST fail closed for review-gated cards when a fresh
risk-appropriate payload gate is absent or stale. Deterministic/process payloads
may use a fresh `machine-reviewed` preflight receipt; ordinary and critical
payloads require a fresh valid `go` verdict.

#### Scenario: Publish runs without a valid review gate
- **WHEN** publish is invoked for a delivered card without its risk-appropriate
  fresh machine receipt or `go` verdict
- **THEN** publish stops before staging, committing or pushing files

### Requirement: Deliver skill orchestrates the lifecycle
`changerail-deliver` MUST orchestrate the card-level flow `ff -> do -> review -> pub`
while preserving phase safety stops, scoped publish behavior and autonomous
repeated-`NO-GO` escalation.

#### Scenario: Deliver reaches an external review stop
- **WHEN** an operator requires external review instead of self-launched review
- **THEN** `changerail-deliver` stops at the review gate and prints the review and
  resume commands without publishing

#### Scenario: Deliver uses the default review rescue budget
- **WHEN** `changerail-deliver` receives consecutive `no-go` review verdicts
- **THEN** the default autonomous policy allows two bounded same-card rescue
  attempts after the first `no-go`
- **AND** each rescue attempt still requires a fresh independent re-review
  before publish

#### Scenario: Deliver exhausts the same-card rescue budget
- **WHEN** the default same-card rescue budget is exhausted and review still
  returns `no-go`
- **THEN** `changerail-deliver` MUST stop publishing that payload
- **AND** the lifecycle instructions MUST direct the orchestrator to create a
  linked rescue/replacement card with prior cycle history instead of requesting
  manual exceptional authorization

#### Scenario: Deliver detects repeated lineage blockers
- **WHEN** linked replacement/rescue cards repeatedly return the same blocker
  class or unresolved invariant
- **THEN** lifecycle instructions MUST direct the orchestrator to create an
  investigation/design card before further implementation rescue work
