# changerail-release-ci Specification

## Purpose

Зафиксировать release-facing CI gate для ChangeRail: OpenSpec validation,
docs/config checks, Python smoke checks, templates/bootstrap/verify/drift and
wiring discovery.
## Requirements
### Requirement: Release CI workflow
ChangeRail MUST provide a tracked CI workflow that runs the release verification
baseline on pushes, pull requests and manual dispatch.
Release CI MUST run the strengthened public-surface scan for current public
roots and reachable history.

#### Scenario: CI runs for repository changes
- **WHEN** the ChangeRail CI workflow is triggered by `push`, `pull_request` or
  `workflow_dispatch`
- **THEN** it runs OpenSpec validation, docs/config parsing checks and Python
  syntax checks
- **AND** it exits non-zero when any required command fails

#### Scenario: CI runs strengthened public-safety scan
- **WHEN** the ChangeRail CI workflow runs
- **THEN** it runs the public-surface scanner self-test
- **AND** it runs the scanner against current public roots and reachable
  history

### Requirement: Template and bootstrap smoke in CI

ChangeRail CI MUST exercise project templates and bootstrap/verify behavior through
red/green smoke commands.

#### Scenario: Template or bootstrap drift breaks generated projects
- **WHEN** template, bootstrap or verification wiring is broken
- **THEN** the CI workflow runs `scripts/smoke-verify-project.py` and
  `scripts/smoke-bootstrap-project.py`
- **AND** the workflow fails before release-facing changes can be accepted

### Requirement: Drift and wiring smoke in CI

ChangeRail CI MUST run drift and wiring discovery checks without requiring private
workspace inventory.

#### Scenario: CI checks drift and wiring safely
- **WHEN** CI reaches smoke verification
- **THEN** it runs `scripts/smoke-wiring-discovery.py`
- **AND** it runs `scripts/smoke-drift.py` against a generated generic runtime
  project
- **AND** committed workflow content contains no private workspace inventory

### Requirement: CI workflow contract smoke
ChangeRail MUST provide a local smoke check that validates the tracked CI workflow
contains the required release gates.
CI workflow contract smoke MUST require the strengthened scanner commands.

#### Scenario: Maintainer edits the workflow
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if the CI workflow is missing required triggers or command
  strings
- **AND** it passes only when all required release gates are present

#### Scenario: CI smoke requires history scan command
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if the CI workflow no longer invokes the scanner history
  mode

### Requirement: Release CI validates ChangeRail fixtures
Release CI MUST run bootstrap, verify, wiring and drift smoke against generated
ChangeRail fixtures after the rename.

#### Scenario: Release CI runs
- **WHEN** the release CI workflow executes after the rename
- **THEN** generated fixture paths and reports use the ChangeRail runtime
  namespace
- **AND** release smoke fails if generated defaults still use OPSX wiring

### Requirement: CI covers generated workflow guidance
Release CI MUST run bootstrap smoke coverage that fails when generated workflow
guidance drifts from the current ChangeRail process.

#### Scenario: Template workflow guidance regresses
- **WHEN** release CI runs `scripts/smoke-bootstrap-project.py`
- **THEN** missing lifecycle, role model, fresh review or board finalization
  guidance in generated files fails the CI smoke

### Requirement: Release CI inventory coverage
ChangeRail release CI MUST discover and compile tracked Python helper and smoke
files under `bin/` and `scripts/` from repository inventory instead of relying
on a manually maintained incomplete file list.

#### Scenario: New Python helper is tracked
- **WHEN** a Python helper or smoke script is tracked under `bin/` or `scripts/`
- **THEN** release CI includes that file in the syntax compile gate
- **AND** a syntax error in that file fails the release workflow

### Requirement: Release CI focused smoke inventory
ChangeRail release CI MUST run the focused smoke scripts that protect delivery
runner, delivery metrics, review fingerprint, review verdict validation,
review preflight,
manifest derivation, bootstrap, verify, wiring discovery, archive diagnostics,
release workflow contract and drift fixture behavior.

#### Scenario: Focused smoke coverage regresses
- **WHEN** the tracked CI workflow no longer invokes a required focused smoke
  command
- **THEN** `scripts/smoke-release-ci.py` fails before the workflow change can
  be accepted

### Requirement: Release CI lint gate
ChangeRail release CI MUST run a pinned lint gate for tracked Python helpers and
scripts.

#### Scenario: Unused import reaches release gate
- **WHEN** `ruff check bin scripts` reports an unused import or equivalent
  lint failure
- **THEN** release CI exits non-zero before publish

### Requirement: Local release baseline command
ChangeRail MUST provide a single local command that reproduces the mandatory
release CI baseline from the repository checkout and exits non-zero when any
mandatory check fails.

#### Scenario: Maintainer runs local release baseline
- **WHEN** a maintainer runs the documented local release baseline command
- **THEN** it executes OpenSpec validation, config parsing, schema validation,
  Python syntax inventory, lint, focused smoke checks, generated drift fixture,
  public-surface scans and whitespace checks
- **AND** the command returns non-zero if any required check fails

#### Scenario: Drift smoke needs inventory
- **WHEN** the local release baseline checks drift
- **THEN** it invokes `scripts/smoke-drift.py` with a generated public-safe
  project fixture rather than requiring no-argument drift behavior

### Requirement: Release baseline history scan uses only invocation-local memoization
The ChangeRail release history scanner MUST freshly enumerate all reachable Git
inputs on every invocation. It MUST use only process-local object and exact
path-sensitive `(blob OID, repository-relative path)` memoization for that
invocation, and MUST NOT load, save, validate or otherwise depend on a
persistent cross-run cache or other retained scanner state. Scanner execution
MUST NOT mutate repository refs, worktree contents or Git index state.

#### Scenario: Unchanged blob is reachable from many commits
- **WHEN** the same Git blob is reachable at the same selected path from many
  commits
- **THEN** the scanner reads its content through batch object I/O and evaluates
  that `(blob, path)` identity at most once during that invocation
- **AND** it materializes the same ordered per-commit findings as a fresh
  traversal without retained state

#### Scenario: Same blob appears under two current-policy paths
- **WHEN** one blob is reachable under two repository-relative paths
- **THEN** the scanner evaluates the two exact path identities independently
- **AND** rename and exact path identity remain distinct only within the
  invocation-local memo

#### Scenario: Policy or Git input changes
- **WHEN** scanner policy, object format, blob content, exact path or reachable
  refs change between invocations
- **THEN** no retained result can authorize reuse for the changed input
- **AND** the scanner freshly enumerates reachable inputs before producing its
  result

#### Scenario: Retained scanner state is proposed
- **WHEN** a candidate proposes a cache file, cache directory, cache
  key/version, cache environment or CLI control, daemon, transcript, receipt or
  any other cross-run scanner state
- **THEN** deterministic verification rejects it before successful history
  output
- **AND** a missing, malformed or unreadable required Git object makes the
  history command exit non-zero rather than produce a false pass

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

#### Scenario: Invocation-local optimization or parallel smoke capacity exists
- **WHEN** a maintainer runs the complete release baseline with
  invocation-local history memoization or parallel smoke capacity
- **THEN** the baseline still invokes each mandatory command in its tracked
  inventory
- **AND** any failed, missing, corrupt or timed-out command returns the baseline
  non-zero

#### Scenario: Optimized behavior is compared with sequential oracle
- **WHEN** focused acceptance runs fresh real-Git structural history cases or
  sequential and parallel smoke fixtures
- **THEN** normalized findings, case coverage, exit status and diagnostics have
  semantic parity
- **AND** structural history timing evidence remains observational and cannot
  alter the correctness verdict

#### Scenario: Structural history performance metadata is observational
- **WHEN** the structural history successor records timing or memory metadata
- **THEN** it records `/usr/bin/time -v` elapsed-time and max-RSS values only
  alongside the required correctness evidence
- **AND** no warm sample, ratio, CV, wall-clock or RSS threshold can select,
  retry or change the verdict

#### Scenario: Maintainer attributes baseline duration
- **WHEN** the local release baseline executes its mandatory inventory
- **THEN** human-readable output reports monotonic duration for every invoked
  step without changing that step's pass/fail result
- **AND** timing output is observational data, not a reusable pass receipt or
  publish authority

### Requirement: Consumer Codex auth setup smoke coverage
ChangeRail release baseline MUST include focused smoke coverage for the
consumer Codex auth setup contract across bootstrap, verification and delivery
runner preflight surfaces.

#### Scenario: Release baseline checks auth setup contract
- **WHEN** the local release baseline or release CI focused smoke set runs
- **THEN** it covers bootstrap opt-in auth link behavior, verification readiness
  advisory behavior and delivery runner auth remediation diagnostics
- **AND** it does not require real Codex credentials

#### Scenario: Smoke keeps credentials out of output
- **WHEN** smoke tests create temporary fake auth marker contents
- **THEN** tracked test output and structured status assertions do not include
  credential contents or token-like values

### Requirement: Release baseline validates skill frontmatter
The local release baseline and release CI MUST include deterministic validation
for complete bundled skill YAML frontmatter.

#### Scenario: Maintainer runs local release baseline after skill edits
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** the mandatory focused smoke set parses all `skills/*/SKILL.md`
  frontmatter as YAML
- **AND** the command returns non-zero if any bundled skill frontmatter is
  invalid

#### Scenario: Release CI runs without Codex credentials
- **WHEN** the ChangeRail CI workflow executes the release baseline checks
- **THEN** skill frontmatter validation uses repository-local parser behavior
- **AND** it does not require a networked `codex exec` call or real Codex
  credentials

#### Scenario: String-only frontmatter parsing regresses
- **WHEN** the release baseline executes the wiring discovery smoke
- **THEN** the smoke includes a negative fixture for an unquoted `: ` scalar
- **AND** the baseline fails if the parser path accepts that fixture

### Requirement: Release baseline covers Python runtime selection
ChangeRail release baseline MUST include focused smoke coverage for shared
Python runtime selection and diagnostics.

#### Scenario: Runtime smoke covers supported and failing selectors
- **WHEN** `python3 scripts/smoke-python-runtime.py` runs
- **THEN** it verifies successful helper startup through a supported runtime
- **AND** it verifies old-version simulation, missing dependency simulation and
  invalid override diagnostics

#### Scenario: Local release baseline runs runtime smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it includes the focused Python runtime smoke in the mandatory step
  list

### Requirement: Release baseline covers Windows entrypoints
ChangeRail release baseline MUST include deterministic smoke coverage for
native Windows entrypoint wrapper contracts.

#### Scenario: Local release baseline runs Windows entrypoint smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it includes `python3 scripts/smoke-windows-entrypoints.py` in the
  mandatory step list
- **AND** the baseline fails if the focused smoke reports a wrapper inventory,
  argv, cwd, environment, exit-code or unsupported-launch finding

#### Scenario: Release CI workflow runs Windows entrypoint smoke
- **WHEN** the ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-entrypoints.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Release baseline covers Windows wiring Git safety
The local release baseline and tracked CI smoke inventory MUST include focused
coverage for Windows wiring Git safety gates.

#### Scenario: Local baseline runs Windows wiring Git safety smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes the focused smoke command that validates generated,
  symlink and junction Git safety fixtures
- **AND** the baseline fails if the smoke reports unsafe status, dry-run add or
  index behavior

#### Scenario: CI workflow runs Windows wiring Git safety smoke
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs the same focused Windows wiring Git safety smoke command
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Release baseline covers Windows smoke matrix
The local release baseline and tracked CI smoke inventory MUST include the
platform-neutral Windows smoke matrix contract.

#### Scenario: Local baseline runs Windows smoke matrix
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes `python3 scripts/smoke-windows-matrix.py` as a mandatory
  step
- **AND** the baseline fails if the smoke matrix reports a failed mandatory
  local matrix item

#### Scenario: CI workflow runs Windows smoke matrix
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-matrix.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Generated consumer CI regression gate
The ChangeRail release baseline and tracked CI MUST validate the generated
consumer workflow contract and execute a local clean-clone fixture against an
exact strict consumer lock.

#### Scenario: Release baseline runs consumer CI smoke
- **WHEN** `python3 scripts/run-release-baseline.py` executes
- **THEN** it includes structured validation of the generated workflow
- **AND** it includes the local strict-lock clean-clone consumer fixture

#### Scenario: Workflow uses a floating ChangeRail reference
- **WHEN** the template no longer reads an exact lock revision
- **THEN** release CI smoke fails

#### Scenario: Workflow gains write authority
- **WHEN** the template adds repository write, commit, push or publish behavior
- **THEN** release CI smoke fails before release publication

### Requirement: Consumer CI failure fixtures
Release smoke MUST cover absent/malformed/advisory locks, unavailable revision,
owned wiring conflict and successful exact-revision verification.

#### Scenario: CI negative matrix runs
- **WHEN** focused consumer CI smoke executes
- **THEN** every unsafe or non-reproducible fixture exits non-zero
- **AND** the successful fixture proves the same local and CI verification path

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

### Requirement: Repaired fixture history certification MUST be one-shot and precommitted
ChangeRail MUST permit exactly one separate reachable-history certification
attempt for repaired `history-fixture-v2` only after the tracked certification
policy is finalized and precommitted, and MUST treat every observed outcome as
terminal. The precommitment MUST NOT claim that the governed capture was
already reviewed or published; one fresh critical final-certification review
MUST occur after capture and before publication.

#### Scenario: Certification policy is finalized before capture
- **WHEN** DO prepares the certification payload for its only history capture
- **THEN** the board/OpenSpec/spec policy already fixes capture id
  `public-history-certification`, timeout 1200 seconds, source identities,
  before/after byte hashes, output oracle and no-retry rule
- **AND** the exact tracked policy fingerprint is retained before execution
- **AND** independent Sol/`xhigh` review and publication remain pending until
  terminal capture evidence exists

#### Scenario: Exact repaired source enters the capture
- **WHEN** certification checks the source immediately before and after
  `python3 scripts/public-surface-scan.py --history --json`
- **THEN** both review fingerprints are
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`
- **AND** both fixture fingerprints are
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`
- **AND** both exact-byte SHA-256 values for `authority.json` are
  `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`
- **AND** the seven authority paths match their predeclared exact SHA-256 values
  before and after execution

#### Scenario: Sole capture produces PASS
- **WHEN** the absent capture id is used once with timeout 1200 and the command
  completes with exit 0 before timeout
- **THEN** stdout is exactly one complete `changerail.public-surface-scan.v1`
  JSON report with `history: true`, `summary.status: pass`,
  `summary.findings: 0` and `findings: []`
- **AND** all pre/post source identities are unchanged
- **AND** the `changerail.evidence-index.v1` entry and ignored manifest retain
  the command identity, timing, exit, timeout, output and findings metadata

#### Scenario: Sole capture does not produce PASS
- **WHEN** the command reports findings, exits nonzero, times out, cannot start,
  emits incomplete or schema-invalid output, contradicts its exit status or the
  source identity changes
- **THEN** the observed FAIL or TIMEOUT is terminal and source review/publish is
  forbidden
- **AND** no retry, replacement id, upsert, diagnostic promotion, benchmark
  sample-selection rule or same-card repair/rescue is allowed

#### Scenario: Prior source timeout is retained independently
- **WHEN** certification evidence is evaluated
- **THEN** source evidence `public-history-final` remains a separate 300-second
  timeout with empty output, no exit code and no PASS claim
- **AND** the authentic 627.163-second prior duration is calibration only and
  cannot count as this certification attempt or outcome

#### Scenario: Published certification permits source review-only continuation
- **WHEN** the certification capture passed, its fresh critical Sol/`xhigh`
  review returned GO and the certification revision is remote-reachable
- **THEN** the unchanged source may receive exactly one fresh cycle-2
  Sol/`xhigh` review without another source scan or implementation edit
- **AND** the link remains one-way from certification to source with no source
  card edit
- **AND** source GO may proceed to publish while source NO-GO is terminal with
  no repair

#### Scenario: Fast-forward prepares certification policy
- **WHEN** `$changerail-ff` prepares
  `certify-materialized-public-history-fixture-v2-history-evidence`
- **THEN** it creates exactly one apply-ready board/OpenSpec/spec
  documentation/evidence-policy change with zero production/test/runtime LOC
- **AND** no evidence capture, reachable-history scan, fixture materialization,
  benchmark, full baseline, archive, review, commit or push occurs
