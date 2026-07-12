## MODIFIED Requirements

### Requirement: Release CI workflow
Release CI MUST run the strengthened public-surface scan for current public
roots and reachable history.

#### Scenario: CI runs strengthened public-safety scan
- **WHEN** the ChangeRail CI workflow runs
- **THEN** it runs the public-surface scanner self-test
- **AND** it runs the scanner against current public roots and reachable
  history

### Requirement: CI workflow contract smoke
CI workflow contract smoke MUST require the strengthened scanner commands.

#### Scenario: CI smoke requires history scan command
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if the CI workflow no longer invokes the scanner history
  mode
