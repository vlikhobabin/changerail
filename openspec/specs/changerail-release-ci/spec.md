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

### Requirement: Exhausted path-sensitive history acceleration is replaced fail-closed
ChangeRail MUST treat both unpublished
`accelerate-path-sensitive-public-history-scan` and stopped
`deliver-path-sensitive-public-history-scan-replacement` payloads as
forensic-only. Only `deliver-path-sensitive-public-history-scan-replacement-v2`
may reimplement the capability after its fixture and exact authorization
predecessors are published. Production behavior MUST start from exact safe
commit `ccccb62562e1646b595119edd3326763860f14a7`, MUST use fresh persistent
raw-tree batch traversal, and MUST add at most 300 production LOC relative to
that commit even though the exact preflight authorization ceiling is 301. New
authority or wire protocol and same-card repair/rescue are forbidden. Each
raw-tree `raw_name` MUST be exactly one non-empty Git tree path component:
strict UTF-8 bytes that round-trip unchanged, contain no NUL, slash, ASCII
control/DEL or backslash, and are neither `.` nor `..`; it MUST be validated
before prefixing, without splitting or normalization.

#### Scenario: Non-empty ls-tree framing is malformed
- **WHEN** an `ls-tree -r -z` compatibility or enumeration stream is non-empty
  but lacks exactly one terminal NUL, contains an empty interior record, has a
  malformed mode/type/OID header, or contains an undecodable or unsafe path
- **THEN** history scanning fails closed before cache lookup, cache reuse,
  partial findings or a successful history result
- **AND** only `b""` represents a valid empty tree

#### Scenario: Raw-tree name is malformed
- **WHEN** persistent raw-tree traversal receives an empty, undecodable,
  unsafe or slash-bearing `raw_name`
- **THEN** a connected successor negative fixture proves that history scanning
  fails closed before traversal output, cache lookup, cache reuse, partial
  findings or a successful history result

#### Scenario: Clean v2 replacement enumerates reachable objects
- **WHEN** the exact authorized v2 replacement performs a current cold or warm
  history scan
- **THEN** it freshly enumerates every reachable commit and traverses strict
  commit/tree/blob framing through one persistent batch object reader without a
  production `ls-tree` process per commit
- **AND** it preserves ordered per-commit findings and exact `(blob,path)` cache
  identity while treating every malformed, missing or mistyped object as a hard
  history failure

#### Scenario: Preflight evaluates the exact v2 authorization
- **WHEN** deterministic preflight evaluates the implementation card
- **THEN** the investigation and authorization sources are unchanged tracked
  `4.done` artifacts with reciprocal exact IDs/paths, the reference resolves to
  authorization status `valid`, ceiling 301 and protocol allowance false
- **AND** absence, staleness, mismatch, a changed fixture-authority source, more
  than 300 added production LOC or new authority/wire behavior stops delivery

#### Scenario: Initial v2 replacement review is not successful
- **WHEN** the exact successor receives `NO-GO`, misses a frozen performance or
  memory threshold, exceeds 300 added production LOC, modifies fixture
  authority, or lacks mandatory focused, history, benchmark, baseline,
  manifest, preflight or independent-review proof
- **THEN** same-card repair, favorable benchmark rerun and re-review are
  forbidden because repair/rescue limit/used/remaining is `0/0/0`
- **AND** both earlier payloads remain unpublished and downstream
  `parallelize-isolated-release-smoke-cases` remains blocked pending a new
  published decision and replacement

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
ChangeRail MUST treat `history-fixture-v1` as historical-only because its
published fingerprint and counts do not define a materializable preimage.
Before a new public-history scanner candidate is created, ChangeRail MUST
publish `history-fixture-v2` as an immutable tracked recipe, deterministic Git
materializer, root-independent realization transcript, detached component
authority, independent published-parent legacy oracle, benchmark harness and
self-tests.

#### Scenario: v1 digest and counts are the only available source
- **WHEN** a successor cannot resolve exact ordered recipe bytes, object graph,
  paths, parents and ref operations from tracked published sources
- **THEN** `history-fixture-v1` cannot authorize benchmark GREEN or candidate
  publication
- **AND** no implementation may reconstruct, guess or select a preimage for its
  historical fingerprint

#### Scenario: Recipe v2 is materialized in two fresh roots
- **WHEN** the pinned materializer validates and realizes the pinned recipe in
  two different new absolute roots under the sanitized deterministic Git
  environment
- **THEN** both runs produce byte-identical canonical transcripts, ordered
  object/ref/path records, counts, normalized legacy output digest and
  domain-separated fixture fingerprint
- **AND** the exact scale is 48 commits, 1152 selected occurrences, 96 unique
  `(blob,path)` identities and 72 unique blobs

#### Scenario: Fixture component is missing or modified
- **WHEN** the recipe schema, recipe, materializer, realization transcript,
  benchmark harness or self-test is absent, untracked, at another path or does
  not match its separate lowercase SHA-256 in the detached authority record
- **THEN** fixture validation fails before candidate execution or benchmark
- **AND** no component or authority file may validate itself through a digest
  embedded in its own bytes

#### Scenario: Published-parent legacy oracle runs
- **WHEN** fixture realization or benchmark computes the legacy result
- **THEN** it executes exact scanner blob
  `74b218d8d92274d73ffaea129404749a330e8320` from published commit
  `ccccb62562e1646b595119edd3326763860f14a7`, whose raw bytes have SHA-256
  `bd353167a9a3460047c4b25ef41827709bd2304b5b72945d244ffac01094bd6d`
- **AND** the oracle runs in a separate sanitized process without importing
  candidate or stopped-successor code, tests, cache, normalizer or evidence

#### Scenario: Frozen v2 benchmark evaluates a candidate
- **WHEN** the pre-candidate pinned harness runs its canonical benchmark
- **THEN** every fresh-root trial runs legacy uncached, candidate empty-cache
  cold and its immediate unchanged warm rerun in that order, with two complete
  discarded warmups and five complete measured trials
- **AND** unrounded monotonic medians require cold/legacy `<=0.20` and
  warm/legacy `<=0.05`; population CV `<=0.15` forbids rerun, while higher CV
  permits exactly one whole-set replacement and a second instability is
  `NOT-VERIFIABLE`
- **AND** every scanner/Git child VmHWM is `<=256 MiB`, 100 ms aggregate RSS for
  active job ceiling 1 is `<=384 MiB`, and missing samples or any bound breach
  is red

#### Scenario: Harness or evidence attempts favorable selection
- **WHEN** a payload changes fixture bytes, semantic cases, scale, oracle,
  normalization, workload, process timer boundary, trial order/count, cache
  state, threshold, unrounded arithmetic, CV replacement rule, RSS accounting
  or selects/deletes samples by outcome
- **THEN** pinned authority verification or connected harness self-tests fail
- **AND** runtime samples and host metadata remain evidence only and cannot
  define fixture bytes or authorize a different verdict

#### Scenario: Ordered fixture, authorization and implementation lineage runs
- **WHEN** maintainers proceed after this investigation is published
- **THEN** they publish `materialize-public-history-benchmark-fixture-v2`, then
  `authorize-bounded-public-history-scan-replacement-v2`, and only then create
  `deliver-path-sensitive-public-history-scan-replacement-v2`
- **AND** the authorization source contains exact object
  `{"investigation_card":"openspec/board/4.done/investigate-materialized-public-history-benchmark-v2.md","investigation_id":"investigate-materialized-public-history-benchmark-v2","successor_card":"openspec/board/3.inprogress/deliver-path-sensitive-public-history-scan-replacement-v2.md","successor_id":"deliver-path-sensitive-public-history-scan-replacement-v2","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`
- **AND** the implementation card uses only exact reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-public-history-scan-replacement-v2.md","authorization_id":"authorize-bounded-public-history-scan-replacement-v2"}`

#### Scenario: Fast-forward completes this decision
- **WHEN** `$changerail-ff` prepares
  `decide-materialized-public-history-benchmark-v2`
- **THEN** only the source card and this change's proposal, design, delta spec
  and tasks are created or updated
- **AND** production/test/runtime LOC remains zero and no successor card,
  history scan, benchmark, full baseline, archive, review, commit or push occurs

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
