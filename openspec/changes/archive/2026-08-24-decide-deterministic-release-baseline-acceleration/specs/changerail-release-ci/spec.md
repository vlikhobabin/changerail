## ADDED Requirements

### Requirement: Release baseline history scan reuses only verified path-sensitive content
The ChangeRail release history scanner MUST freshly enumerate all reachable Git
inputs on every invocation and MUST scan every selected path-sensitive content
identity that is not covered by a valid matching content cache entry. Reuse
MUST be scoped to scanner policy, Git object format, blob identity and exact
repository-relative path, and MUST NOT act as a receipt for the history step or
the whole release baseline.

#### Scenario: Unchanged blob is reachable from many commits
- **WHEN** the same Git blob is reachable at the same selected path from many
  commits
- **THEN** the scanner reads its content through batch object I/O and evaluates
  that `(blob, path)` identity a bounded number of times
- **AND** it materializes the same ordered per-commit findings as an uncached
  scan

#### Scenario: Same blob appears under two current-policy paths
- **WHEN** one blob is reachable under two repository-relative paths
- **THEN** the scanner evaluates the two exact path identities independently
- **AND** a fixture for current historical `/opt/opsx` expects the same allowed
  result at both paths while proving distinct cache identities and rename
  invalidation

#### Scenario: Policy or Git input changes
- **WHEN** scanner policy, object format, blob content, exact path or reachable
  refs change
- **THEN** stale cache identity cannot authorize reuse for the changed input
- **AND** the scanner freshly enumerates reachable inputs before producing its
  result

#### Scenario: Cache or Git object data is invalid
- **WHEN** a cache entry is absent, truncated, malformed, mismatched, oversized
  or corrupt
- **THEN** the scanner treats it as a miss and evaluates the authentic Git
  object
- **AND** a missing, malformed or unreadable required Git object makes the
  history command exit non-zero rather than produce a false pass

### Requirement: Expensive release smoke uses bounded isolated concurrency
The review-preflight and delivery-runner release smoke commands MUST execute
every registered mandatory case in a separate process/temp-root isolation
boundary or in an explicitly declared dependent group. Concurrency and case
runtime MUST be bounded, and parallel completion order MUST NOT change the
aggregated result or diagnostic order.

#### Scenario: Independent smoke cases finish out of order
- **WHEN** registered smoke cases execute concurrently and complete in a
  different order on repeated runs
- **THEN** the parent reports results and diagnostics in stable registry order
- **AND** it exits zero only after receiving one successful terminal result for
  every registered case ID

#### Scenario: Smoke child crashes or times out
- **WHEN** a case crashes, exceeds its finite timeout, returns malformed output
  or produces oversized diagnostic output
- **THEN** the parent terminates and reaps the isolated process group
- **AND** the smoke exits non-zero with a bounded diagnostic at that case's
  deterministic registry position

#### Scenario: Worker configuration exceeds bounds
- **WHEN** requested jobs are zero, negative or above the declared hard ceiling
- **THEN** the smoke exits non-zero before launching cases
- **AND** no case is silently omitted or treated as passed

#### Scenario: Frozen legacy completeness oracle rejects an omitted case
- **WHEN** the successor extracts either smoke registry from its published
  parent blob
- **THEN** a machine-checkable AST/source-span inventory covers every top-level
  review `main()` scenario/assert block and every delivery `check_*` definition
  and `main()` invocation with immutable source/span hashes
- **AND** registry ownership is exact one-to-one with that inventory, and a
  fault injection for every registered oracle makes the parent red at its stable
  registry position

### Requirement: Baseline acceleration preserves mandatory command coverage
The local ChangeRail release baseline MUST continue to invoke every mandatory
step, including history scan, review-preflight smoke and delivery-runner smoke.
Optimization MUST remain internal to those commands and MUST NOT introduce a
reusable whole-baseline pass receipt or new publish authority.

#### Scenario: Warm optimization data exists
- **WHEN** a maintainer runs the complete release baseline with valid warm
  per-content cache data or parallel smoke capacity
- **THEN** the baseline still invokes each mandatory command in its tracked
  inventory
- **AND** any failed, missing, corrupt or timed-out command returns the baseline
  non-zero

#### Scenario: Optimized behavior is compared with sequential oracle
- **WHEN** focused acceptance runs cold/warm history fixtures or sequential and
  parallel smoke fixtures
- **THEN** normalized findings, case coverage, exit status and diagnostics have
  semantic parity
- **AND** timing evidence demonstrates the bounded thresholds declared by the
  reviewed implementation change

#### Scenario: Performance evidence is reproducible and memory-bounded
- **WHEN** an acceleration successor records its acceptance benchmark
- **THEN** it records frozen fixture version/scale/hash, checkout, Python/Git,
  OS/kernel, CPU, RAM, jobs, two discarded warmups and five monotonic samples
  per mode with coefficient of variation at most 15 percent
- **AND** every child VmHWM is at most 256 MiB and 100 ms aggregate RSS sampling
  is at most 128 MiB plus 256 MiB per active job ceiling; missing data or an
  exceeded bound is non-zero

#### Scenario: Maintainer attributes baseline duration
- **WHEN** the local release baseline executes its mandatory inventory
- **THEN** human-readable output reports monotonic duration for every invoked
  step without changing that step's pass/fail result
- **AND** timing output is observational data, not a reusable pass receipt or
  publish authority
