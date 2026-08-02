## ADDED Requirements

### Requirement: Release baseline covers Windows wiring Git safety
The local release baseline and tracked CI smoke inventory MUST include focused
coverage for Windows wiring Git safety gates.

#### Scenario: Local baseline runs Windows wiring Git safety smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes the focused smoke command that validates generated,
  symlink and junction Git safety fixtures
- **AND** the baseline fails if the smoke reports unsafe status, dry-run add or
  index behavior

#### Scenario: CI workflow runs Windows wiring Git safety smoke
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs the same focused Windows wiring Git safety smoke command
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory
