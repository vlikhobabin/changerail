## ADDED Requirements

### Requirement: Release docs name reproducible local baseline
ChangeRail release discipline documentation MUST name the local release baseline
command and describe its relationship to CI.

#### Scenario: Maintainer prepares a release
- **WHEN** a maintainer reads release discipline docs before publish
- **THEN** the docs identify the single local baseline command to run
- **AND** the docs identify any separate trusted-network checks that remain
  outside the generated public-safe baseline
