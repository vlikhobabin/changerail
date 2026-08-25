## MODIFIED Requirements

### Requirement: Expensive release smoke uses bounded isolated concurrency
After the bounded Windows scheduler is remote-reachable, ChangeRail MUST run
the review-preflight and delivery-runner release smoke commands so that every
registered mandatory case executes in a separate process/temp-root boundary
or in an explicitly declared dependent group. Concurrency and case runtime
MUST be bounded, and parallel completion order MUST NOT change the aggregated
result or diagnostic order. This successor MUST remain separate from A, B and
verify-project ownership.

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

#### Scenario: Release smoke waits for the Windows scheduler boundary
- **WHEN** `parallelize-isolated-release-smoke-cases` is prepared
- **THEN** exact published B and all prior A/scanner-v2 revisions are
  remote-reachable and recorded as immutable predecessors
- **AND** the smoke successor cannot absorb or redefine release registry,
  Windows scheduler or verify-project ownership

### Requirement: Tiered release verification MUST separate fast feedback from full authority
ChangeRail MUST provide a pre-admitted frozen `full-release` profile as the
only release-suite authority and a bounded `affected` profile solely for
non-authoritative inner-loop feedback. The frozen full inventory MUST contain
exactly 35 ordered leaf IDs with canonical newline-list SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`.
Requested `affected` MUST remain non-authoritative even when fail-closed
selection expands to the complete inventory. After publication of
`rescue-tiered-release-verification-split-boundary`, executable delivery MUST
use separate release-authority-core and Windows-scheduler lineages in the
specified order rather than the old broad successor.

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
- **WHEN** full-release and CI execute the local Windows matrix after the
  Windows-scheduler successor is published
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

#### Scenario: Release authority core has one exact owner
- **WHEN** maintainers publish
  `authorize-bounded-tiered-release-authority-core`
- **THEN** it contains only exact six-field authorization
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** the successor is limited to `<=499` production LOC against its exact
  published authorization HEAD and exclusively owns admission, the 35-ID
  registry/digest, profile selection/authority, atomic marker/lock/fsync,
  capture identity, fingerprint equality, receipt/manifest/schema/pub gates,
  canonical CI full-runner invocation and their parsed ownership oracles

#### Scenario: Authority core cannot absorb Windows topology
- **WHEN** the A successor is scoped or reviewed
- **THEN** it preserves existing Windows process scheduling and cannot add jobs,
  case schemas, process-group lifecycle, the six-ID matrix-owner transition or
  removal of the four redundant standalone processes
- **AND** a scope overlap, 500th production line, credential/mutation/live
  authority or broad protocol claim fails closed before terminal capture

#### Scenario: Windows scheduler has one exact owner
- **WHEN** published A and the independently authorized clean scanner-v2 are
  remote-reachable and maintainers publish
  `authorize-bounded-windows-release-matrix-scheduler`
- **THEN** it contains only exact six-field authorization
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-windows-release-matrix-scheduler.md","successor_id":"implement-bounded-windows-release-matrix-scheduler","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** the successor is limited to `<=499` production LOC against its exact
  published authorization HEAD and exclusively owns the six-case schema/
  registry, bounded jobs/isolation/order, central process-group cleanup,
  scheduler fault handling, six-ID owner transition, exact four-process removal
  and its narrow parsed-CI oracle extension

#### Scenario: Windows scheduler cannot redefine release authority
- **WHEN** the B successor is scoped or reviewed
- **THEN** it consumes A's exact registry, selector, capture and receipt
  contracts without redefining them or the general CI parser
- **AND** ownership overlap, scanner code, a 500th production line, live access
  or authority outside scheduling/cleanup/owner transition fails closed

#### Scenario: Ordered authorizations bound separate implementation scopes
- **WHEN** maintainers continue the release acceleration lineage
- **THEN** they publish A authorization and A implementation, then the separate
  clean scanner-v2 authorization and implementation, then B authorization and
  B implementation, with every predecessor remote-reachable before the next
  authorization is created
- **AND** only after B publication may they continue with the separate
  verify-project authorization/implementation and the separate review-preflight
  and delivery-runner release-smoke successor

#### Scenario: Executable successor receives one terminal full capture
- **WHEN** any ordered executable successor completes focused deterministic
  checks and requests final review
- **THEN** a fresh Sol/`xhigh` pre-capture audit verifies exact lineage, `<=499`
  comparison where applicable, authority/ownership scope, fault coverage and
  absence of forensic payload reuse before exactly one predeclared atomic
  `full-release` capture on the unchanged payload
- **AND** repair/retry/rescue budget is `0/0/0`; FAIL, timeout, malformed/stale
  receipt or fingerprint change is terminal without retry, while the sole GREEN
  capture may proceed to fresh formal Sol/`xhigh` review

#### Scenario: Fast-forward remains decision-only
- **WHEN** `$changerail-ff` prepares
  `rescue-tiered-release-verification-split-boundary`
- **THEN** it creates or updates only the target card and proposal, design,
  release-CI delta and tasks for this one same-slug change
- **AND** production/test/runtime LOC stay zero and no successor card, main-spec
  sync, history scan, full baseline, archive, review, commit or push occurs

### Requirement: Verify-project isolation MUST preserve complete semantic coverage
After the bounded Windows scheduler is published, ChangeRail MUST authorize
`parallelize-isolated-verify-project-cases` from that remote-reachable revision
separately before implementation. The authorization MUST set
`production_loc_ceiling` to `501`, disallow a new authority or wire protocol,
and bind
`openspec/board/4.done/investigate-tiered-release-verification-loop-boundary.md`
to `openspec/board/3.inprogress/parallelize-isolated-verify-project-cases.md`
with the exact reciprocal IDs. It MUST limit the successor to `<=500`
production LOC relative to exact published B HEAD. The successor MUST retain
exactly once semantic coverage for all current approximately 73 assertions and
45 run paths, without a cross-run cache.

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
  no retry after focused GREEN, while scanner-v2 and B remain independently
  bounded against their exact published predecessors

#### Scenario: Verify-project waits for the Windows scheduler boundary
- **WHEN** the separate verify-project authorization is prepared
- **THEN** exact published A, scanner-v2 and B revisions are remote-reachable,
  and exact B HEAD is the successor's immutable comparison base
- **AND** the successor cannot absorb release authority, scanner or Windows
  scheduler ownership

### Requirement: Published bounded tiered release verification authorization source
Published `authorize-bounded-tiered-release-verification-loop` MUST remain an
immutable historical authorization source for the original broad successor.
After publication of `rescue-tiered-release-verification-split-boundary`, it
MUST NOT authorize creation, implementation, review or publication of
`implement-tiered-release-verification-loop`; executable work MUST use the two
new exact split authorizations. The broad unpublished implementation and all
of its code, tests, diff, evidence, receipts and runtime state MUST remain
forensic-only and MUST NOT be reused by either clean successor.

#### Scenario: Authorization source publishes before successor creation
- **WHEN** maintainers inspect the previously published decision and
  authorization
- **THEN** their tracked objects and reciprocal historical relationship remain
  unchanged rather than being rewritten as accepted implementation evidence
- **AND** no new executable card may cite the broad authorization reference or
  create `implement-tiered-release-verification-loop`

#### Scenario: Exact reciprocal lineage is retained for the future successor
- **WHEN** A or B implementation is created after its authorization is
  published and remote-reachable
- **THEN** its `Published investigation authorization` contains only the exact
  two-field reference to its own A or B authorization card/id
- **AND** it depends on the split rescue, its own authorization and all ordered
  published predecessors without citing the broad authorization

#### Scenario: Tiered authorization mismatch fails closed
- **WHEN** an A/B candidate includes a cherry-pick, patch, copied code/test,
  old diff, receipt, report, evidence, runtime state or other implementation
  payload derived from the unpublished broad worktree
- **THEN** deterministic scope verification or the fresh pre-capture audit
  rejects the candidate before its sole terminal capture
- **AND** the old lineage is not declared accepted, repaired or published
  retroactively
