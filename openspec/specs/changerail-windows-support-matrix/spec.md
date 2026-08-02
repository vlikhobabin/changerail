# changerail-windows-support-matrix Specification

## Purpose
Зафиксировать sanitized two-host native Windows capability matrix и evidence
contract для readiness перед deeper Windows wiring/runtime probes.

## Requirements

### Requirement: Two-host capability matrix
ChangeRail MUST publish a sanitized two-host native Windows support matrix
before running deeper Windows wiring probes.

#### Scenario: Matrix includes baseline capabilities
- **WHEN** `030-01` is delivered
- **THEN** the tracked report includes one row each for `windows-host-a` and
  `windows-host-b`
- **AND** each row records sanitized OS, filesystem, Git, Python, shell and
  privilege capability outcomes

#### Scenario: Host identity remains private
- **WHEN** the support matrix is committed
- **THEN** it excludes raw hostnames, usernames, private Windows paths,
  credentials and SSH command strings

### Requirement: SSH execution and fixture transfer proof
The Windows support matrix MUST prove that each lab host can execute
non-interactive commands and receive deterministic test fixtures safely.

#### Scenario: Host probe completes
- **WHEN** a host is marked ready in the support matrix
- **THEN** SSH access, non-interactive PowerShell execution, disposable root
  setup, fixture write/read and cleanup have passed

#### Scenario: Host cannot complete a mandatory readiness check
- **WHEN** SSH execution, disposable root setup or fixture transfer fails for a
  host
- **THEN** the matrix records the host as not ready with a concise sanitized
  reason
- **AND** downstream Windows wiring probes do not treat that host as ready

### Requirement: Evidence-backed tracked summary
The tracked Windows support matrix MUST cite retained ignored evidence for the
live probe that produced it.

#### Scenario: Matrix cites runtime evidence
- **WHEN** a maintainer reads the tracked matrix
- **THEN** it identifies the harness command class, aggregate outcome and
  ignored runtime report/evidence path
- **AND** it does not embed raw command output

#### Scenario: Public-surface scan checks sanitized output
- **WHEN** `030-01` delivery verifies the support matrix
- **THEN** public-surface scan covers the tracked report and fails on private
  host identity, credentials or machine-local paths
