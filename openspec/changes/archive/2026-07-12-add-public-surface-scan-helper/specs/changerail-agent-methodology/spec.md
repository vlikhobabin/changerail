## ADDED Requirements

### Requirement: Public-surface scan helper
ChangeRail MUST provide a reusable helper for public-surface scans required by
repository policy.

#### Scenario: Maintainer scans touched public files
- **WHEN** `scripts/public-surface-scan.py` is run against explicit tracked
  paths
- **THEN** it fails on disallowed machine-local `/opt/*` paths
- **AND** it allows documented generic examples such as `/opt/changerail` and
  `/opt/example-project`

#### Scenario: Historical rename references are scanned
- **WHEN** a line contains a documented historical or migration reference to
  `/opt/opsx`
- **THEN** the scanner treats it as allowed
- **AND** non-historical `/opt/opsx` examples remain reviewable findings

#### Scenario: Default public scan covers archived OpenSpec artifacts
- **WHEN** `scripts/public-surface-scan.py` runs without explicit path arguments
- **THEN** it scans the tracked OpenSpec surface including `openspec/changes/archive`
- **AND** a disallowed `/opt/*` path inside an archived change is reported as a
  finding
