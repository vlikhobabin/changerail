## ADDED Requirements

### Requirement: Release baseline covers Windows entrypoints
ChangeRail release baseline MUST include deterministic smoke coverage for
native Windows entrypoint wrapper contracts.

#### Scenario: Local release baseline runs Windows entrypoint smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it includes `python3 scripts/smoke-windows-entrypoints.py` in the
  mandatory step list
- **AND** the baseline fails if the focused smoke reports a wrapper inventory,
  argv, cwd, environment, exit-code or unsupported-launch finding

#### Scenario: Release CI workflow runs Windows entrypoint smoke
- **WHEN** the ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-entrypoints.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory
