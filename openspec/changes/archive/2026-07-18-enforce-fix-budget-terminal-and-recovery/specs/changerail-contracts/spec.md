## MODIFIED Requirements

### Requirement: Delivery run record contract
ChangeRail MUST define a public `changerail.delivery-run.v1` contract for
machine-readable delivery run status, terminal outcomes and an optional stable
terminal reason.

#### Scenario: Runner writes status
- **WHEN** the delivery runner writes
  `<workspace>/.runtime/changerail/delivery-runs/<run-id>/status.json` by default
- **THEN** the JSON uses `changerail.delivery-run.v1` and includes card, phase,
  result, timestamps and command metadata
- **AND** the record includes `commit` when workspace `HEAD` is available

#### Scenario: Runner writes a safety-stop reason
- **WHEN** delivery terminates without publication because the pre-review fix
  budget is exhausted
- **THEN** the record contains terminal outcome `BLOCKED` and
  `terminal_reason: fix_budget_exhausted`
- **AND** aggregate queue status can preserve the same reason without parsing
  raw logs

#### Scenario: Usage is unavailable
- **WHEN** the runner cannot observe token usage from the provider output
- **THEN** the run record explicitly reports usage as unavailable instead of
  guessing values

### Requirement: Delivery run safety-stop fallback evidence
The public delivery-run contract MUST state that `DELIVERED` is not a valid
fallback outcome when structured review-gated evidence or an unpublished card
shows that publish did not complete.

#### Scenario: Maintainer reads runner contract docs
- **WHEN** maintainer reads delivery-run contract documentation
- **THEN** the documentation says structured JSONL terminal signals are the
  preferred terminal outcome and reason source
- **AND** it says runner fallback MUST check canonical review-gated evidence
  and published card state before treating child exit `0` as `DELIVERED`

#### Scenario: Supervisor observes no-go fallback
- **WHEN** a delivery run status is written for child exit `0` without a
  terminal JSONL event but with a fresh canonical `no-go` verdict for an
  unpublished card
- **THEN** `status.json`, printed `terminal_outcome` and wrapper exit code are
  consistent with `NO-GO`

#### Scenario: Supervisor observes fix-budget safety stop
- **WHEN** a completed agent-message event contains exact terminal marker lines
  for `BLOCKED` and `fix_budget_exhausted`
- **THEN** `status.json` preserves both values and the wrapper exits non-zero
- **AND** arbitrary prose containing similar words is not authoritative

#### Scenario: Successful process leaves card unpublished
- **WHEN** child exit is `0`, no authoritative terminal signal or canonical
  review fallback exists, and the card is not uniquely published under
  `4.done`
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: unpublished_card`
