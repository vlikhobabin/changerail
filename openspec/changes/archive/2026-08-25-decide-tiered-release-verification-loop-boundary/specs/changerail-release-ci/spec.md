## MODIFIED Requirements

### Requirement: Baseline acceleration preserves mandatory command coverage
The local ChangeRail release baseline MUST preserve every frozen mandatory
semantic check ID with exactly one declared owner. Optimization MAY regroup or
remove duplicate process invocations only when the same semantic leaf remains
owned and executed exactly once in `full-release`. The baseline MUST NOT use an
`affected` result or reusable whole-baseline pass cache as review, publish or CI
authority.

#### Scenario: Semantic orchestration replaces duplicate process invocation
- **WHEN** a maintainer runs `full-release` after tiered orchestration is
  published
- **THEN** every ID in the frozen inventory receives exactly one terminal
  result from its declared owner in deterministic registry order
- **AND** missing, duplicate, unknown, corrupt or timed-out ownership returns
  the baseline non-zero even when the corresponding process command appeared
  elsewhere

#### Scenario: Optimized behavior is compared with sequential oracle
- **WHEN** focused acceptance runs fresh real-Git structural history cases or
  jobs-1 and default-job Windows/smoke fixtures
- **THEN** normalized findings, case coverage, exit status and diagnostics have
  semantic parity
- **AND** structural history and concurrency timing evidence remains
  observational and cannot alter the correctness verdict

#### Scenario: Structural history performance metadata is observational
- **WHEN** the structural history successor records timing or memory metadata
- **THEN** it records `/usr/bin/time -v` elapsed-time and max-RSS values only
  alongside the required correctness evidence
- **AND** no warm sample, ratio, CV, wall-clock or RSS threshold can select,
  retry or change the verdict

#### Scenario: Maintainer attributes baseline duration
- **WHEN** the local release baseline executes its selected semantic inventory
- **THEN** human-readable output reports monotonic duration for every owned ID
  without changing that ID's pass/fail result
- **AND** timing output is observational data, not a reusable pass receipt or
  publish authority

### Requirement: Release baseline covers Windows entrypoints
ChangeRail release baseline MUST retain deterministic smoke coverage for native
Windows entrypoint wrapper contracts as semantic ID `windows.entrypoints`,
owned exactly once by the local Windows matrix.

#### Scenario: Local baseline runs Windows entrypoint semantics
- **WHEN** `python3 scripts/run-release-baseline.py --profile full-release` runs
- **THEN** the mandatory Windows matrix executes `windows.entrypoints` exactly
  once in its six-item local registry
- **AND** the baseline fails if the case reports a wrapper inventory, argv,
  cwd, environment, exit-code or unsupported-launch finding

#### Scenario: Release CI workflow retains Windows entrypoint semantics
- **WHEN** the ChangeRail CI workflow executes the canonical full-release
  runner
- **THEN** the runner reaches `windows.entrypoints` through the mandatory local
  Windows matrix
- **AND** `scripts/smoke-release-ci.py` rejects missing or multiply-owned
  semantic coverage without requiring a standalone duplicate process

### Requirement: Release baseline covers Windows wiring Git safety
The local release baseline and tracked CI MUST retain focused generated,
symlink and junction Git safety coverage as semantic ID
`windows.wiring-git-safety`, owned exactly once by the local Windows matrix.

#### Scenario: Local baseline runs Windows wiring Git safety semantics
- **WHEN** `python3 scripts/run-release-baseline.py --profile full-release` runs
- **THEN** the mandatory Windows matrix executes
  `windows.wiring-git-safety` exactly once
- **AND** the baseline fails if that case reports unsafe status, dry-run add or
  index behavior

#### Scenario: CI retains Windows wiring Git safety semantics
- **WHEN** the tracked ChangeRail CI workflow invokes canonical full-release
- **THEN** the local Windows matrix owns the same wiring Git safety ID
- **AND** CI contract smoke rejects missing or duplicate ownership without
  requiring another standalone invocation

### Requirement: Release baseline covers Windows smoke matrix
The local release baseline and tracked CI MUST execute the platform-neutral
local Windows smoke matrix once as the sole owner of its six frozen leaf IDs.
The matrix MUST use bounded isolated concurrency and MUST NOT enter live mode or
read live inventory unless an operator invokes the separate explicit live gate.

#### Scenario: Local baseline runs bounded Windows matrix
- **WHEN** `python3 scripts/run-release-baseline.py --profile full-release` runs
- **THEN** it executes one local matrix owning exactly
  `windows.entrypoints`, `project.bootstrap`, `project.verify-drift`,
  `windows.wiring-git-safety`, `windows.lab-dry-run` and
  `windows.runtime-wiring-dry-run`
- **AND** the baseline fails on missing, duplicate, failed, crashed, timed-out
  or malformed terminal result for any of the six IDs

#### Scenario: Release CI workflow runs local matrix only
- **WHEN** the tracked ChangeRail CI workflow invokes canonical full-release
- **THEN** `scripts/smoke-release-ci.py` proves one matrix owner for all six
  IDs and absence of the four duplicate standalone processes
- **AND** default CI does not supply `--live`, read a host inventory or contact
  a Windows host

## ADDED Requirements

### Requirement: Tiered release verification MUST separate fast feedback from full authority
ChangeRail MUST provide a pre-admitted frozen `full-release` profile as the
only release-suite authority and a bounded `affected` profile solely for
non-authoritative inner-loop feedback. The frozen full inventory MUST contain
exactly 35 ordered leaf IDs with canonical newline-list SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`.
Requested `affected` MUST remain non-authoritative even when fail-closed
selection expands to the complete inventory.

#### Scenario: Toolchain admission fails before semantic execution
- **WHEN** child Python is older than 3.11, an exact runtime/dev distribution
  pin is missing or mismatched, `ruff 0.6.9` is not usable from the release
  environment, Git/repository identity is invalid, Node/npm/npx is unusable,
  pinned OpenSpec `1.3.1` cannot run, or a registry target is unavailable
- **THEN** startup reports bounded aggregate admission failures and exits
  non-zero with `semantic_started: 0`
- **AND** no OpenSpec validation, smoke, scanner, matrix or other semantic
  child has run

#### Scenario: Full inventory ownership is exact
- **WHEN** full-release registry admission checks the frozen inventory
- **THEN** every one of the 35 ordered IDs has one owner and one direct command
  or explicit sequential group
- **AND** duplicate/missing/unknown IDs, owner/result mismatch, inventory digest
  drift or absent terminal result fails closed

#### Scenario: Windows local cases execute with bounded parallelism
- **WHEN** the six-item local Windows registry runs with jobs 1 or default jobs
- **THEN** `--jobs` is bounded to `1..8`, default is
  `min(4,max(1,cpu),6)`, every case has isolated temp/report/output/process-group
  state and finite timeout/output bounds
- **AND** completion races preserve registry-order diagnostics while crash,
  timeout, oversized or malformed output is reaped and makes the matrix red

#### Scenario: Four duplicate processes are removed without semantic loss
- **WHEN** full-release and CI execute the local Windows matrix
- **THEN** entrypoints, wiring Git safety, bootstrap and verify-project each run
  exactly once as matrix-owned leaf IDs
- **AND** no standalone duplicate invocation remains while jobs-1/default
  parity and fault injection prove all prior semantic assertions remain live

#### Scenario: Local profile cannot consume live Windows state
- **WHEN** full-release or affected verification runs without an explicit
  operator live command
- **THEN** Windows local mode does not open inventory, resolve host credentials
  or start network/SSH/WinRM access
- **AND** live host proof remains a separate `--live --inventory` gate that is
  absent from CI and cannot be enabled through a release profile or environment
  override

#### Scenario: Affected selector handles every Git path transition
- **WHEN** a valid base-to-workspace change contains added, modified, deleted,
  renamed, copied, untracked or multi-area paths within declared bounds
- **THEN** the closed path map selects the deterministic ordered union of all
  mapped semantic IDs using both old and new rename/copy paths
- **AND** it always includes the minimum OpenSpec/current-public/whitespace/
  ignored-status floor and Python syntax/lint for Python paths

#### Scenario: Selector uncertainty expands to full inventory
- **WHEN** base resolution/ancestry, Git framing, path decoding, map ownership
  or selection is unknown or ambiguous; a path/count/output bound is exceeded;
  a path is unknown; or selector, registry, toolchain, CI or normative profile
  sources change
- **THEN** effective selection expands to all 35 IDs rather than omitting a
  plausible check or returning an empty pass
- **AND** the report records a bounded deterministic fallback reason

#### Scenario: Affected evidence cannot authorize review or publish
- **WHEN** review, publish or CI is offered evidence requested with
  `--profile affected`
- **THEN** it rejects that evidence as a full-suite claim even if effective
  fallback executed all 35 IDs successfully
- **AND** no affected result, cache, timing or selector output can become a
  reusable whole-baseline authority

#### Scenario: Full-release evidence is complete and payload-bound
- **WHEN** review or publish accepts a release-suite claim, or tracked CI runs
- **THEN** evidence comes from exact `--profile full-release`, has admitted
  toolchain, current frozen digest, one PASS for all 35 IDs and the same payload
  fingerprint under existing manifest/evidence freshness rules
- **AND** missing, stale, changed-payload, incomplete or malformed evidence
  fails closed; CI invokes only the canonical full-release runner

#### Scenario: Ordered authorizations bound separate implementation scopes
- **WHEN** maintainers continue after publication of this decision
- **THEN** they first publish tiered authorization with ceiling `500`, protocol
  allowance `true` and exact successor `implement-tiered-release-verification-loop`,
  whose implementation is `<=499` production LOC relative to
  `45a2de98924c61bb9e944767013ea09918bba4b0`
- **AND** after that implementation is remote-reachable they may separately
  publish `verify-project` authorization with ceiling `501`, protocol allowance
  `false` and exact successor `parallelize-isolated-verify-project-cases`,
  limited to `<=500` LOC against exact published tiered HEAD; scanner-v2 remains
  independent and uses a separate authorization with ceiling `301`, protocol
  allowance `false` and exact successor
  `deliver-clean-git-compatible-structural-history-scan-v2`, limited to
  `<=300` production LOC relative to exact published tiered HEAD

#### Scenario: Executable successor receives one terminal full capture
- **WHEN** either authorized implementation finishes all focused deterministic
  checks and requests final review
- **THEN** its predeclared full-release capture runs exactly once without retry,
  and PASS may proceed to fresh critical Sol/`xhigh` review
- **AND** FAIL or TIMEOUT stops that lineage for a clean repair/replacement
  rather than selecting a second result after observing the first

#### Scenario: Fast-forward remains decision-only
- **WHEN** `$changerail-ff` prepares
  `decide-tiered-release-verification-loop-boundary`
- **THEN** it creates or updates only the target card and proposal, design,
  release-CI delta and tasks for this one change
- **AND** production/test/runtime LOC stay zero and no successor card, main-spec
  sync, history scan, full baseline, archive, review, commit or push occurs

### Requirement: Verify-project isolation MUST preserve complete semantic coverage
After tiered orchestration is published, ChangeRail MUST authorize
`parallelize-isolated-verify-project-cases` separately before implementation.
The authorization MUST set `production_loc_ceiling` to `501`, disallow a new
authority or wire protocol, and bind
`openspec/board/4.done/investigate-tiered-release-verification-loop-boundary.md`
to `openspec/board/3.inprogress/parallelize-isolated-verify-project-cases.md`
with the exact reciprocal IDs. It MUST limit the successor to `<=500`
production LOC relative to exact published tiered HEAD. The successor MUST
retain exactly once semantic coverage for all current approximately 73
assertions and 45 run paths, without a cross-run cache.

#### Scenario: Static registry proves complete current coverage
- **WHEN** the isolated `verify-project` successor builds its case registry
- **THEN** every current assertion and run path has exactly one frozen semantic
  ID and source-span/hash entry in a machine-checkable completeness oracle
- **AND** missing, duplicate, unknown or changed source-span ownership fails
  closed before the parallel scheduler reports success

#### Scenario: External cases use immutable isolated fixtures
- **WHEN** a registry case requires a CLI or filesystem boundary
- **THEN** it starts from one immutable base fixture and receives a separate
  copy-on-write, reflink-or-copy child with isolated runtime/report/output roots
- **AND** one case cannot observe or mutate another case's fixture, environment,
  report, output or process-group state

#### Scenario: Pure validators and CLI sentinels have exact owners
- **WHEN** a check observes a pure in-process validator rather than a CLI
  boundary
- **THEN** it remains in-process with an exact semantic owner
- **AND** minimal end-to-end CLI sentinels own only their declared boundary
  assertions so removal of duplicate processes cannot remove semantic coverage

#### Scenario: Bounded concurrency retains deterministic parity
- **WHEN** the registry runs with jobs `1` or default jobs
- **THEN** jobs accept only `1..8`, default is at most `4`, results and
  diagnostics remain in static registry order, and normalized status/exit
  results have jobs-1/default parity
- **AND** crash, timeout, malformed or oversized output terminates and reaps the
  child process group and makes the run non-zero

#### Scenario: Affected selection and authorization remain fail-closed
- **WHEN** an affected run selects `verify-project` coverage or a path is
  unknown, ambiguous or belongs to selector/self-change authority
- **THEN** the closed path map selects the owned IDs or expands to full inventory
  without treating an affected receipt as publish authority
- **AND** the successor has one predeclared terminal full-release capture with
  no retry after focused GREEN, while scanner-v2 remains independently bounded
  against the same published tiered HEAD
