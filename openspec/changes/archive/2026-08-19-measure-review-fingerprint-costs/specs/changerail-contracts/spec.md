## ADDED Requirements

### Requirement: Review fingerprint cost measurement
ChangeRail MUST provide public-safe measurement for deterministic review
fingerprint and review preflight phases without changing the canonical
freshness values.

#### Scenario: Operator measures review fingerprint phases
- **WHEN** an operator runs the review fingerprint measurement surface for a
  workspace
- **THEN** the result lists separate durations for changed path discovery,
  reviewed-tree construction, untracked non-ignored content hashing and final
  fingerprint assembly
- **AND** the result includes the same `head_commit`, `tree_sha` and
  `diff_fingerprint` values as the canonical fingerprint command for the same
  workspace state

#### Scenario: Preflight measurement separates non-fingerprint gates
- **WHEN** review preflight runs with measurement enabled
- **THEN** the result lists fingerprint, OpenSpec validation, scoped whitespace
  check and public-surface scan durations as distinct phases
- **AND** failed checks continue to fail closed with their existing check ids

### Requirement: Synthetic large-repository fingerprint benchmark
ChangeRail MUST include focused benchmark coverage for review fingerprint cost
using synthetic public-safe repositories.

#### Scenario: Benchmark compares docs-only and source payloads
- **WHEN** the benchmark smoke runs
- **THEN** it creates a synthetic repository with many generic tracked files
- **AND** it records docs-only and source-payload timings before deleting the
  temporary repository
- **AND** it does not write private consumer paths, raw field-validation logs or
  generated repository contents to tracked files

#### Scenario: Benchmark threshold is derived from fixture behavior
- **WHEN** maintainers inspect the benchmark configuration
- **THEN** the threshold is based on the measured synthetic baseline and fixture
  size
- **AND** it does not depend on a specific consumer repository identity
