## ADDED Requirements

### Requirement: Release baseline covers Windows smoke matrix
The local release baseline and tracked CI smoke inventory MUST include the
platform-neutral Windows smoke matrix contract.

#### Scenario: Local baseline runs Windows smoke matrix
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes `python3 scripts/smoke-windows-matrix.py` as a mandatory
  step
- **AND** the baseline fails if the smoke matrix reports a failed mandatory
  local matrix item

#### Scenario: CI workflow runs Windows smoke matrix
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-matrix.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory
