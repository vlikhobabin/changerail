## ADDED Requirements

### Requirement: Native Windows support claim release gate
ChangeRail release-facing documentation MUST require final Windows proof,
public-surface scans and the Linux release baseline before publishing a native
Windows support claim.

#### Scenario: Maintainer prepares Windows support claim
- **WHEN** maintainer documentation describes native Windows support readiness
- **THEN** it names the live clean-clone lifecycle proof command or aggregate
  live matrix command
- **AND** it names `python3 scripts/run-release-baseline.py`
- **AND** it names current and history public-surface scans

#### Scenario: Final proof is missing or blocked
- **WHEN** the final clean-clone proof is missing, stale or blocked
- **THEN** release-facing docs require an explicit blocker/caveat before any
  support claim is published
