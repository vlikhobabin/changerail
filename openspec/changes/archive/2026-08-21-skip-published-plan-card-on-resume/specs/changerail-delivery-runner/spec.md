## ADDED Requirements

### Requirement: Published-card resume reconciliation
The delivery runner MUST reconcile a plan card that was published outside a
previous failed aggregate run before dispatching another delivery child.

#### Scenario: Resume skips a safely published prior blocker
- **WHEN** `resume-plan` re-resolves a prior non-delivered card to exactly one
  path under `openspec/board/4.done/`
- **AND** the owning repository is clean and `HEAD == upstream`
- **AND** the plan runs in push mode
- **THEN** aggregate status marks the card `skipped` with result `DELIVERED`
- **AND** no delivery child is launched for that card
- **AND** its dependants may continue in dependency order

#### Scenario: Published-card proof is incomplete
- **WHEN** the current card path, clean-tree proof or upstream equality does not
  satisfy normal push-mode queue success criteria
- **THEN** resume MUST NOT infer delivered status from retained state or a
  partial board-path signal
