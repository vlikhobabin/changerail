## ADDED Requirements

### Requirement: Queue metrics from structured records
The delivery metrics helper MUST read aggregate queue status and child delivery
run records to report queue outcomes without parsing arbitrary text.

#### Scenario: Queue status is present
- **WHEN** metrics receive a queue status directory or default queue runtime
  path containing `changerail.delivery-plan-status.v1` records
- **THEN** metrics report queue id, result, terminal outcome, completed cards,
  blocked/no-go cards, child run ids and push/no-push mode

#### Scenario: Child records provide details
- **WHEN** a queue status references child delivery run records
- **THEN** metrics use the existing child record and review-cycle fields for
  token usage, timing, findings and acceptance details

#### Scenario: Queue details are missing
- **WHEN** queue status is missing optional timing or child references
- **THEN** metrics render those values as `unknown`

### Requirement: Queue runtime paths
ChangeRail observability MUST use ignored queue runtime paths for aggregate
status, locks and logs.

#### Scenario: Queue runner writes runtime state
- **WHEN** a plan command writes aggregate status or locks
- **THEN** the default path is under `.runtime/changerail/delivery-plans/`
- **AND** raw logs and locks remain ignored runtime state
