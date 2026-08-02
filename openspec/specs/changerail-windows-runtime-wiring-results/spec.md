# changerail-windows-runtime-wiring-results Specification

## Purpose
Зафиксировать evidence contract для sanitized two-host native Windows runtime,
wiring и Git behavior comparison перед architecture decision.

## Requirements

### Requirement: Two-host runtime wiring comparison
ChangeRail MUST publish a sanitized two-host comparison for native Windows
runtime, wiring and Git behavior before selecting a Windows architecture.

#### Scenario: Comparison covers both lab hosts
- **WHEN** `030-02` is delivered
- **THEN** the tracked comparison includes one result each for
  `windows-host-a` and `windows-host-b`
- **AND** any missing host result has an explicit sanitized not-applicable or
  blocked reason

#### Scenario: Comparison covers required strategy classes
- **WHEN** the tracked comparison is published
- **THEN** it covers direct directory symlink, junction, direct file link,
  generated copy, extensionless wrapper launch, `.cmd` launch, PowerShell
  launch, Python launch, explicit Bash launch, Git traversal and drift/update
  behavior
- **AND** it summarizes security, portability, Git and operator trade-offs

### Requirement: Evidence-backed repeatability
The Windows runtime/wiring comparison MUST cite ignored runtime evidence and
prove repeatability after cleanup.

#### Scenario: Primary and repeatability reports are cited
- **WHEN** a maintainer reads the tracked comparison
- **THEN** it names the live probe command class
- **AND** it cites the ignored primary report path and repeatability report path

#### Scenario: Repeatability mismatch blocks conclusion
- **WHEN** the repeatability run changes a strategy conclusion from the primary
  run
- **THEN** the tracked comparison records the mismatch instead of presenting the
  strategy as stable

### Requirement: Public-safe result surface
The Windows runtime/wiring comparison MUST exclude private host identity,
private paths, credentials and raw runtime output from tracked files.

#### Scenario: Tracked result is sanitized
- **WHEN** `030-02` verification runs the public-surface scan
- **THEN** tracked docs, cards and OpenSpec artifacts contain only generic host
  ids and repository-relative ignored evidence paths
- **AND** raw stdout, stderr, SSH commands and disposable root values are not
  committed
