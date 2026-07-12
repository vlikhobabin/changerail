## ADDED Requirements

### Requirement: Delivery run safety-stop fallback evidence
The public delivery-run contract MUST state that `DELIVERED` is not a valid
fallback outcome when structured review-gated evidence shows publish is blocked.

#### Scenario: Maintainer reads runner contract docs
- **WHEN** maintainer reads delivery-run contract documentation
- **THEN** the documentation says structured JSONL terminal events are the
  preferred terminal outcome source
- **AND** it says runner fallback MUST check canonical review-gated evidence
  before treating child exit `0` as `DELIVERED`

#### Scenario: Supervisor observes no-go fallback
- **WHEN** a delivery run status is written for child exit `0` without a
  terminal JSONL event but with a fresh canonical `no-go` verdict for an
  unpublished card
- **THEN** `status.json`, printed `terminal_outcome` and wrapper exit code are
  consistent with `NO-GO`
