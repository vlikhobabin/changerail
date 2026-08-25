## MODIFIED Requirements

### Requirement: Exhausted path-sensitive history acceleration is replaced fail-closed
ChangeRail MUST preserve unpublished
`accelerate-path-sensitive-public-history-scan`,
`deliver-path-sensitive-public-history-scan-replacement` and fixture-v2
implementation payloads plus their negative verdicts as forensic-only, and
MUST NOT copy or publish them as implementation evidence. Future delivery MUST
use only `deliver-structurally-bounded-public-history-scan` after exact
`authorize-bounded-structural-public-history-scan` publication. Production
behavior MUST start from exact safe commit
`ccccb62562e1646b595119edd3326763860f14a7`, MUST add at most 300 production
LOC relative to that commit and MUST NOT introduce new authority or wire
protocol. Each history invocation MUST freshly execute exactly one
`git rev-list --all` and exactly one persistent `git cat-file --batch`, with no
cross-run cache, recipe, transcript or benchmark authority. The scanner MUST
use only invocation-local memoization and MUST NOT mutate repository refs,
worktree contents or Git index state.

#### Scenario: Fresh traversal uses invocation-local memoization
- **WHEN** the structural successor scans reachable history
- **THEN** it strictly parses a fresh ordered `rev-list --all` stream and
  obtains all required commit, tree and blob objects through its sole
  persistent `cat-file --batch` child
- **AND** each object OID is requested at most once per invocation, each exact
  `(blob OID, repository-relative path)` is scanned at most once, and findings
  expand deterministically to every ordered reachable `(commit,path,blob)`
  occurrence
- **AND** all memoized state is process-local and is neither loaded nor saved
  across invocations

#### Scenario: Connected state oracle proves scanner non-mutation
- **WHEN** a connected test independently captures, before and after every
  successful and fault-injected candidate run, the complete ref namespace
  (refname, direct or symbolic target and peeled target), an exhaustive
  worktree mapping of repository-relative path, file type/mode and raw bytes,
  and the exact raw bytes of the Git index
- **THEN** the before and after snapshots are byte-for-byte identical for each
  observed component
- **AND** the oracle runs outside the counted candidate PATH and derives none
  of its expected state from candidate output, memo counters or a persistent
  cache

#### Scenario: Reachability, batch or path framing is unsafe
- **WHEN** `rev-list` or batch data is malformed, truncated, missing,
  mistyped, unexpectedly duplicated, size-inconsistent or unsuccessful, or a
  raw tree name is empty, undecodable, non-round-tripping, slash/backslash
  bearing, control-bearing, absolute, `.` or `..`
- **THEN** history scanning exits nonzero before any terminal partial findings
  or successful report
- **AND** every commit has one valid tree, every raw object has its expected
  type and complete framing, and every path is validated before prefixing

#### Scenario: Git child count remains constant across real history scale
- **WHEN** a connected test runs the candidate against small and enlarged
  temporary real-Git histories with a PATH-first Git argv recorder
- **THEN** each candidate run records exact Git child-launch count `2`, one
  `rev-list --all` and one `cat-file --batch`, regardless of commit, tree, blob,
  ref or occurrence count
- **AND** no production `ls-tree`, `show`, per-object Git process or extra Git
  discovery child is launched

#### Scenario: Independent verifier proves actual ordered coverage
- **WHEN** a verifier outside the counted candidate PATH independently runs
  real `git rev-list --all` and `git ls-tree -r -z --full-tree` per commit
- **THEN** its strict actual ordered `(commit,path,blob)` tuple list equals the
  candidate test observer list exactly
- **AND** expected coverage is not derived from candidate findings, synthetic
  cardinalities, recipe, realization transcript, cache counters or a tracked
  fixture authority

#### Scenario: Small real repositories preserve semantics and reject faults
- **WHEN** focused temporary real-Git cases cover allowed content, leaks,
  secret redaction, rename/exact path identity, binary/NUL content, non-UTF8
  blob content and malformed/truncated/mistyped/missing/unsafe injected Git data
- **THEN** valid cases have normalized finding parity with exact legacy scanner
  `ccccb625:scripts/public-surface-scan.py`
- **AND** every fault case exits nonzero without partial success, while the
  ephemeral repositories and injectors do not become benchmark authority

#### Scenario: Exact successor preflight evaluates bounded authorization
- **WHEN** deterministic preflight evaluates
  `deliver-structurally-bounded-public-history-scan`
- **THEN** its exact authorization reference resolves to unchanged clean
  tracked `openspec/board/4.done/authorize-bounded-structural-public-history-scan.md`
  with status `valid`, reciprocal investigation/successor IDs and paths,
  production ceiling `301` and protocol allowance `false`
- **AND** absent, stale or mismatched authorization, a baseline other than
  `ccccb625`, more than 300 added production LOC, or new authority/wire behavior
  stops delivery

#### Scenario: Final evidence uses correctness gates without timing thresholds
- **WHEN** the exact candidate has passed focused structural tests and enters
  final verification
- **THEN** delivery runs exactly one standalone current-history scan and
  exactly one full release baseline on the unchanged payload, and both MUST
  pass their correctness oracles
- **AND** `/usr/bin/time -v` elapsed-time and max-RSS values are retained only
  as observational metadata; wall, ratio, CV and process/descendant-RSS
  thresholds cannot select, retry or change the verdict

#### Scenario: Release CI claims complete all-ref history
- **WHEN** release CI runs the public-history scan or full release baseline
- **THEN** checkout uses `fetch-depth: 0` before the scan
- **AND** shallow or single-ref history cannot satisfy the complete
  `rev-list --all` proof

### Requirement: Materialized public-history fixture authority MUST precede a scanner candidate
ChangeRail MUST preserve published fixture-v2 decisions and certification as
historical forensic records for their original stopped lineage, but MUST treat
their recipe, transcript, authority, warm-ratio/CV rule and descendant-RSS
oracle as superseded for future delivery. The structural successor MUST NOT
depend on, reconstruct, copy or publish the exhausted fixture-v2 implementation
or either `NO-GO` payload. Its authority MUST instead be the published
structural decision plus exact bounded authorization, real-Git structural tests
and final correctness runs.

#### Scenario: Historical fixture-v2 lineage is inspected
- **WHEN** maintainers inspect published decisions
  `ccccb62562e1646b595119edd3326763860f14a7`,
  `c2c145ce4d107a8dfcd30603f46e46641c2009c0`,
  `f6b56f11593e56fddbd6a718f6abe5418ade9129` or certification
  `3915f54f017e3bf7b9af785f62519a87b75f9b9c`
- **THEN** their tracked content and retained forensic evidence remain
  unchanged
- **AND** none is claimed as accepted implementation evidence for the
  structural successor

#### Scenario: Future candidate proposes fixture or persistent-state authority
- **WHEN** a successor proposes cross-run cache, fixture recipe/materializer,
  realization transcript, detached fixture authority, warm sample/CV
  replacement, wall threshold or descendant-RSS threshold
- **THEN** deterministic verification rejects the candidate as outside this
  decision and authorization
- **AND** observational `time -v` metadata cannot be promoted into such an
  authority

#### Scenario: Ordered structural authorization and implementation lineage runs
- **WHEN** maintainers proceed after
  `investigate-structural-public-history-scan-proof` is reviewed and published
- **THEN** they create and publish
  `authorize-bounded-structural-public-history-scan` before creating
  `deliver-structurally-bounded-public-history-scan`
- **AND** the authorization source contains exact object
  `{"investigation_card":"openspec/board/4.done/investigate-structural-public-history-scan-proof.md","investigation_id":"investigate-structural-public-history-scan-proof","successor_card":"openspec/board/3.inprogress/deliver-structurally-bounded-public-history-scan.md","successor_id":"deliver-structurally-bounded-public-history-scan","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`
- **AND** the implementation card uses only exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}`

#### Scenario: Structural implementation publishes GREEN
- **WHEN** the exact authorized implementation passes structural, semantic,
  fault, history, full-baseline, manifest, preflight and independent-review
  gates within 300 production LOC relative to `ccccb625`
- **THEN** it may publish without a fixture benchmark, timing threshold or
  descendant-RSS oracle
- **AND** only after that publication may maintainers deliver
  `parallelize-isolated-release-smoke-cases` and then resume the phase-routed
  runner series

#### Scenario: Fast-forward completes this structural decision
- **WHEN** `$changerail-ff` prepares
  `decide-structural-public-history-scan-proof`
- **THEN** only the source card and this change's proposal, design, release-CI
  delta and tasks are created or updated
- **AND** production/test/runtime LOC remains zero and no successor card,
  history scan, benchmark, full baseline, archive, review, commit or push
  occurs
