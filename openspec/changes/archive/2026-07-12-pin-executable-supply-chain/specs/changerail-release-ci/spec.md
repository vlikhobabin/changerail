## MODIFIED Requirements

### Requirement: Release CI workflow
Release CI MUST use immutable third-party action references.

#### Scenario: CI actions are immutable
- **WHEN** the ChangeRail CI workflow is reviewed
- **THEN** third-party actions are referenced by immutable commit SHA
- **AND** the workflow includes readable comments identifying the intended
  action version tag

### Requirement: CI workflow contract smoke
The CI workflow contract smoke MUST reject mutable third-party action tags.

#### Scenario: CI smoke rejects mutable action tags
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if required third-party actions are referenced only by
  mutable major tags such as `@v4`
