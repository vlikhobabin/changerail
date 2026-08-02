## ADDED Requirements

### Requirement: Release baseline includes one-command delivery regression
The local ChangeRail release baseline MUST include deterministic one-command
delivery regression coverage for the runner-supervised delivery path.

#### Scenario: Maintainer runs local release baseline
- **WHEN** a maintainer runs `python3 scripts/run-release-baseline.py`
- **THEN** the baseline executes the one-command delivery regression smoke or a
  delivery-runner smoke command that includes equivalent success, transient
  preflight resume and fail-closed review-gated scenarios
- **AND** release documentation lists that coverage in the focused smoke
  inventory
