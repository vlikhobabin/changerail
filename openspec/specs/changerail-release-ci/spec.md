# changerail-release-ci Specification

## Purpose

Зафиксировать release-facing CI gate для ChangeRail: OpenSpec validation,
docs/config checks, Python smoke checks, templates/bootstrap/verify/drift and
wiring discovery.
## Requirements
### Requirement: Published bounded passive release admission authorization source
ChangeRail MUST publish
`authorize-bounded-passive-release-admission-registry` as one clean tracked
`4.done` board card before creating successor
`implement-passive-release-admission-registry`. The source MUST contain exactly
one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`rescue-tiered-release-authority-two-stage-boundary` to exact future successor
`implement-passive-release-admission-registry` through canonical `4.done` and
`3.inprogress` paths, ceiling `500` and protocol allowance `false`. Future A1
MUST remain at no more than 499 added production LOC relative to the exact
remote-reachable HEAD that publishes this authorization source.

#### Scenario: Authorization source publishes before A1 creation
- **WHEN** maintainers deliver the bounded passive admission authorization
  after publication of its rescue investigation
- **THEN** the payload contains only the authorization board card, its OpenSpec
  artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, successor card or
  code remains absent, and no history scan or full baseline is run

#### Scenario: Exact reciprocal lineage is retained for future A1
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-passive-release-admission-registry`
- **THEN** the published rescue investigation blocks both authorization and
  future A1, while authorization depends on the rescue and blocks that A1
- **AND** future A1 depends on
  `rescue-tiered-release-authority-two-stage-boundary` and its
  `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-passive-release-admission-registry.md","authorization_id":"authorize-bounded-passive-release-admission-registry"}`

#### Scenario: A1 authorization limits passive ownership
- **WHEN** future `implement-passive-release-admission-registry` is scoped or
  reviewed against this source
- **THEN** it owns only the literal 35-record registry, canonical digest,
  owners, direct commands and sequential groups; total bounded injected
  admission; effective-PATH Python and parsed distribution-pin/Ruff-origin
  checks; offline OpenSpec admission; bounded Git A/M/D/R/C/untracked
  selection; closed path map; parsed Python-AST ownership oracle and connected
  faults
- **AND** it cannot own authority receipts, terminal capture, credentials,
  mutation, live access, A2 activation or another release entrypoint

#### Scenario: A1 remains structurally dormant through A2 publication
- **WHEN** this authorization or future A1 is delivered, reviewed or published
  before separately published `implement-terminal-release-authority-activation`
- **THEN** no release baseline, CI workflow, manifest/review/publish preflight,
  receipt schema or production entrypoint imports, invokes or activates A1
- **AND WHEN** that exact A2 is published
- **THEN** only exact published A2 may import, invoke or activate published A1
- **AND** a structural negative-wiring oracle fails every pre-A2 activation
  path and every post-A2 activation path outside exact A2

#### Scenario: Authorization and dormant A1 use current focused proof
- **WHEN** publication eligibility is assessed for this source or future A1
- **THEN** this docs-only source uses strict exact-object, relation, absence,
  ownership, current public-safety and source-classification checks, while A1
  uses real offline admission plus focused, static, current and connected fault
  proof
- **AND** neither payload executes, requires or accepts a reachable-history
  scan, full release baseline, authority receipt or terminal capture as its
  publication evidence
- **AND** prohibited evidence cannot be cited as reusable full-release authority
  for A2

#### Scenario: Passive admission authorization mismatch fails closed
- **WHEN** a card changes any rescue, authorization or successor id/path, adds
  a seventh source field, changes ceiling `500` or protocol `false`, creates A1
  before authorization publication, exceeds 499 added production LOC against
  the published authorization HEAD, expands A1 ownership or wires it before A2
- **THEN** deterministic verification rejects the source or candidate
- **AND** no malformed, partial or over-broad payload can authorize A1

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

### Requirement: Git-compatible commit headers MUST иметь bounded semantic tree boundary
ChangeRail MUST считать exhausted
`deliver-structurally-bounded-public-history-scan` payload и его evidence
forensic-only и MUST определять raw commit parser clean replacement через
одну exact bounded grammar. Batch-validated commit body MUST быть не
больше `64 MiB`, header block MUST быть не больше `64 MiB - 2` bytes
и содержать не больше `1,000,000` physical lines. Первая physical line
MUST точно равняться `tree SP` плюс 40 lowercase hexadecimal bytes.
Каждая later initial line MUST содержать `1..255` byte key из printable
non-space ASCII, required first `SP` и opaque possibly-empty value без NUL,
ASCII control или DEL. Continuation MUST начинаться с `SP`, MAY быть
exact `b" "` и MUST следовать за later non-`tree` logical header. Только
first tree OID MUST интерпретироваться; все later headers, включая
parent, identity, signature, mergetag и unknown keys, MUST оставаться opaque.

#### Scenario: Pinned source ancestry и planning snapshot моделируются read-only
- **WHEN** maintainers применяют minimal parser model к exact source ancestry
  `git rev-list 644e9e1bf03fa444d603652b17d7262846149978` и separately pinned
  planning `git rev-list --all` snapshot
- **THEN** source ancestry имеет `95/95` accepted/rejected `0`, ordered
  `sha256:8576a6f652fa2d168d0956ff225471c92b5190fc46cef707bdae2472584b86ba`
  и sorted
  `sha256:0771d6bc5ad5f121ac630d58805eba30185e84f53595c6ec117f5138ca597eb7`
- **AND** planning snapshot имеет `98/98` accepted/rejected `0`, extra-ref
  OIDs `e0ec75135e8a35be5283a9d6de556dc63f43e260`,
  `e2a39bec92a165a63ede6e3835dc03807fd6ff8f` и
  `e7f5542d91aad1c79545f6a2239f87d3761e9180`, ordered
  `sha256:31c8ae5d7a32a748e5efd371c63d2ae622949d1c8c7c8241c730dd3678c0460e`,
  sorted `sha256:f0545cd40fb856e5153821988a9156941c519c8738abdc11088362b0f58c425d`
  и sorted ref snapshot
  `sha256:5b53eac521b1d0618949bbbc2b89b86c5adb4b208c307ca53bd78baac180fad5`
- **AND** каждая population содержит три signed commits, 48 continuation lines и
  шесть exact blank folds, а commit
  `4fb01e7a12c43ab5c5ff06b1388743433846b54d` остаётся named regression
  без превращения raw objects и forensic runtime output в tracked authority

#### Scenario: Traversal получает ровно один semantic tree
- **WHEN** raw commit начинается с exact `tree <40 lowercase hex>`, имеет
  bounded header block и только valid later opaque logical headers
- **THEN** traversal получает только этот first tree OID
- **AND** `parent`, `author`, `committer`, `gpgsig`, `mergetag`, `encoding` и
  unknown later values не whitelist, не декодируются и не используются

#### Scenario: Blank и unknown folds valid
- **WHEN** later unknown, signature или mergetag logical header имеет один или
  несколько `SP`-prefixed continuations, включая exact physical line `b" "`
- **THEN** commit framing остаётся valid, а каждый continuation остаётся opaque
- **AND** empty initial value, additional leading value spaces и non-ASCII
  value bytes valid, если не содержат NUL, ASCII control или DEL

#### Scenario: Commit header framing malformed
- **WHEN** tree missing, late, duplicated, continued, uppercase, short, long или
  non-hex; continuation не имеет preceding non-tree logical header; required
  first `SP` или `LF LF` отсутствует; tab/control/DEL/non-ASCII byte находится
  до first `SP`; value нарушает byte class; либо body, header, key или
  physical-line count превышает exact bound
- **THEN** history scanning fails closed до traversal tuples, cache reuse, partial
  findings или successful text/JSON output
- **AND** arbitrary message bytes после first `LF LF` не считаются commit headers,
  а further `SP` после first `SP` является opaque value

#### Scenario: Replacement tests проверяют raw objects и все bounds
- **WHEN** future replacement проверяет commit-header parser
- **THEN** он создаёт real raw commit objects для blank и unknown folded
  headers и проверяет key lengths `1/255/256`, injected-small exact/one-over
  body/header/line bounds, missing first `SP`, bad key bytes, orphan continuation и
  every malformed tree/value/fold transition
- **AND** он сохраняет full batch framing, fault injection, exact child count,
  independent tuples, legacy parity, no-partial-output и byte-identical
  refs/worktree/index no-mutation matrix

#### Scenario: Clean authorization и replacement выполняются по порядку
- **WHEN** maintainers продолжают после independent review и publication этого
  rescue investigation
- **THEN** они сначала создают и публикуют
  `authorize-bounded-git-commit-header-compatible-history-scan` с exact object
  `{"investigation_card":"openspec/board/4.done/rescue-git-commit-header-compatibility-decision.md","investigation_id":"rescue-git-commit-header-compatibility-decision","successor_card":"openspec/board/3.inprogress/deliver-git-compatible-structural-public-history-scan-replacement.md","successor_id":"deliver-git-compatible-structural-public-history-scan-replacement","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`
- **AND** только после remote reachability clean tracked source можно создать
  exact replacement с единственной reference
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-git-commit-header-compatible-history-scan.md","authorization_id":"authorize-bounded-git-commit-header-compatible-history-scan"}`

#### Scenario: Replacement scope или review contract drift
- **WHEN** replacement не использует exact reciprocal ids/paths, начинается
  до publication clean authorization, превышает 300 added production LOC
  относительно `ccccb62562e1646b595119edd3326763860f14a7`, объявляет новый
  authority/protocol, не использует `critical`/`xhigh` repeated-defect
  review или даёт same-card rescue сверх exact `limit/used/remaining 0/0/0`
- **THEN** deterministic verification отклоняет replacement до semantic review
  или publication
- **AND** authorization ceiling `301` не разрешает production line 301,
  repair, другой successor или protocol waiver

#### Scenario: Fast-forward завершает только rescue decision
- **WHEN** `$changerail-ff` подготавливает
  `rescue-git-commit-header-compatibility-decision`
- **THEN** создаются или обновляются только rescue card и proposal, design,
  release-CI delta и tasks этого change
- **AND** production/test/runtime additions остаются zero и не выполняются
  authorization, replacement, implementation, history scan, full baseline, archive,
  review, commit или push

### Requirement: Published bounded Git-compatible structural history authorization source
ChangeRail MUST publish
`authorize-bounded-git-commit-header-compatible-history-scan` as one clean
tracked `4.done` board card before creating successor
`deliver-git-compatible-structural-public-history-scan-replacement`. The
authorization source MUST contain exactly one schema-valid
`Investigation authorization` object with only `investigation_card`,
`investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`rescue-git-commit-header-compatibility-decision` to exact future successor
`deliver-git-compatible-structural-public-history-scan-replacement` through
canonical `4.done` and `3.inprogress` paths, ceiling `301` and protocol
allowance `false`. The authorization MUST NOT raise the successor's independent
limit of 300 added production LOC relative to
`ccccb62562e1646b595119edd3326763860f14a7`.

#### Scenario: Authorization source publishes before replacement creation
- **WHEN** maintainers deliver the bounded Git-compatible structural-history
  authorization after publication of its rescue investigation
- **THEN** the payload contains only the authorization board card, its
  OpenSpec artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, no successor
  card or code is created, and no history scan, benchmark or full baseline is
  run

#### Scenario: Exact reciprocal lineage is retained for the future replacement
- **WHEN** the authorization source is published and a later separate flow
  creates `deliver-git-compatible-structural-public-history-scan-replacement`
- **THEN** the published rescue investigation blocks both
  `authorize-bounded-git-commit-header-compatible-history-scan` and
  `deliver-git-compatible-structural-public-history-scan-replacement`, while
  the authorization source depends on the investigation and blocks that exact
  successor
- **AND** the future successor depends on
  `rescue-git-commit-header-compatibility-decision` and its
  `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-git-commit-header-compatible-history-scan.md","authorization_id":"authorize-bounded-git-commit-header-compatible-history-scan"}`

#### Scenario: Git-compatible structural authorization mismatch fails closed
- **WHEN** a future card changes any investigation, authorization or successor
  id/path, omits a reciprocal relation, uses an authorization reference with
  fields other than exact `authorization_card` and `authorization_id`, exceeds
  300 added production LOC against `ccccb625`, or declares new authority or
  wire protocol
- **THEN** deterministic verification rejects the source for that candidate
- **AND** ceiling `301` cannot authorize a 301st production line, another
  successor or a reusable authority/protocol waiver

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

### Requirement: Published bounded structural public-history authorization source
ChangeRail MUST publish
`authorize-bounded-structural-public-history-scan` as one clean tracked
`4.done` board card before creating successor
`deliver-structurally-bounded-public-history-scan`. The authorization source
MUST contain exactly one schema-valid `Investigation authorization` object
with only `investigation_card`, `investigation_id`, `successor_card`,
`successor_id`, `production_loc_ceiling` and
`allow_new_authority_or_wire_protocol`. Those fields MUST bind exact published
investigation `investigate-structural-public-history-scan-proof` to exact future
successor `deliver-structurally-bounded-public-history-scan` through canonical
`4.done` and `3.inprogress` paths, ceiling `301` and protocol allowance
`false`. The authorization MUST NOT raise the successor's independent limit of
300 added production LOC relative to
`ccccb62562e1646b595119edd3326763860f14a7`.

#### Scenario: Authorization source publishes before successor creation
- **WHEN** maintainers deliver the bounded structural public-history
  authorization after publication of its investigation
- **THEN** the payload contains only the authorization board card, its
  OpenSpec artifacts and the exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, no successor
  card or code is created, and no history scan, benchmark or full baseline is
  run

#### Scenario: Exact reciprocal lineage is retained for the future successor
- **WHEN** the authorization source is published and a later separate flow
  creates `deliver-structurally-bounded-public-history-scan`
- **THEN** the published investigation blocks both
  `authorize-bounded-structural-public-history-scan` and
  `deliver-structurally-bounded-public-history-scan`, while the authorization
  source depends on the investigation and blocks that exact successor
- **AND** the future successor depends on
  `investigate-structural-public-history-scan-proof` and its
  `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}`

#### Scenario: Structural authorization mismatch fails closed
- **WHEN** a future card changes any investigation, authorization or successor
  id/path, omits a reciprocal relation, uses an authorization reference with
  fields other than exact `authorization_card` and `authorization_id`, exceeds
  300 added production LOC against `ccccb625`, or declares new authority or
  wire protocol
- **THEN** deterministic verification rejects the source for that candidate
- **AND** ceiling `301` cannot authorize a 301st production line, another
  successor or a reusable authority/protocol waiver

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

### Requirement: Published bounded release authority core authorization source
ChangeRail MUST publish
`authorize-bounded-tiered-release-authority-core` as one clean tracked `4.done`
board card before creating successor `implement-tiered-release-authority-core`.
The source MUST contain exactly one schema-valid `Investigation authorization`
object with only `investigation_card`, `investigation_id`, `successor_card`,
`successor_id`, `production_loc_ceiling` and
`allow_new_authority_or_wire_protocol`. Those fields MUST bind exact published
rescue `rescue-tiered-release-verification-split-boundary` to that exact future
successor through canonical `4.done` and `3.inprogress` paths, ceiling `500`
and protocol allowance `true`. The authorization MUST NOT raise the independent
successor limit of `<=499` production LOC against
`25f756ebf2aa90c58e01eab3703b291dbdde257f` or authorize credential, mutation
or live authority.

#### Scenario: Scope A authorization publishes before successor creation
- **WHEN** maintainers deliver the authority-core authorization after the split
  rescue is published and remote-reachable
- **THEN** the source object is exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** the payload contains only the authorization board card, its OpenSpec
  artifacts and this release-CI relationship requirement; production, test and
  runtime additions remain zero and successor card/code stay absent

#### Scenario: Exact reciprocal lineage is retained for Scope A
- **WHEN** this source is published and a later separate flow creates
  `implement-tiered-release-authority-core`
- **THEN** the split rescue blocks both the authorization and exact successor,
  while the authorization depends on the rescue and blocks that successor
- **AND** the successor depends on both sources and its `Published investigation
  authorization` contains only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-authority-core.md","authorization_id":"authorize-bounded-tiered-release-authority-core"}`

#### Scenario: Scope A ownership is exclusive
- **WHEN** the authorization or its future successor is scoped
- **THEN** it owns only aggregate toolchain admission, the exact 35-ID registry
  and digest, affected/full selection and authority, atomic marker/lock/fsync,
  generic capture identity and fingerprint equality, receipt/manifest/schema/
  preflight/publish gates, canonical CI full-runner invocation and their parsed
  YAML/Python-AST ownership oracles
- **AND** Scope B Windows schemas, jobs, isolation/order, process-group
  lifecycle, deduplication and owner transition plus verify-project, history
  scanner and review/delivery smoke internals remain excluded

#### Scenario: Authority mismatch fails closed
- **WHEN** a candidate changes any bound id/path/relation, uses more than the
  exact two reference fields, claims excluded ownership or credential/mutation/
  live authority, or adds a 500th production line against the exact base
- **THEN** deterministic verification rejects that candidate
- **AND** ceiling `500` and allowance `true` cannot authorize another successor,
  a broad waiver or reuse of forensic implementation payload

### Requirement: Clean release-loop acceleration MUST use bounded H/I/R/A lineage
After publication of `rescue-release-process-supervisor-boundary`, ChangeRail MUST
supersede the active clean H/I/R/A future lineage with the exact ordered
S -> (H4, I3, W1) -> R3 -> A3 -> measured optimization/final certification
lineage. Historical cards, archives and published authorization objects remain
immutable. The exhausted H/I implementation episodes, including code, tests,
diffs, reports, receipts, runtime state and local identity, MUST remain
forensic-only and MUST NOT become implementation, review or publication
authority.

#### Scenario: Supersession replaces only future work
- **WHEN** maintainers continue release-loop acceleration after this rescue is
  published and remote-reachable
- **THEN** they use S first, then H4/I3/W1 in parallel, then R3, then A3, then
  separately authorized measured optimization and final certification
- **AND** the old published H/I one-successor authorization objects cannot
  authorize creation, implementation, review or publication of any replacement
  successor
- **AND** generic forensic summaries may record only the boundary lessons of
  incomplete containment, validation and connected ownership proof, without
  accepting implementation payload or local identity as authority

#### Scenario: Predecessor wave remains structurally dormant before A3
- **WHEN** exact A3 is not yet published and remote-reachable
- **THEN** S/H4/I3/W1/R3 production MUST NOT be imported or invoked by
  `run-release-baseline`, workflow, review/publish gates or receipt schema
- **AND** no full-release/CI authority or evidence can come from the
  predecessor wave
- **AND** after A3 publication only exact A3 integration paths may activate
  those published components

#### Scenario: S is the sole POSIX child-supervisor foundation
- **WHEN** maintainers publish `authorize-bounded-release-child-supervisor-v1`
- **THEN** it contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-child-supervisor-v1.md","successor_id":"implement-bounded-release-child-supervisor-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** its successor remains `<=499` production LOC against its exact
  published authorization HEAD and exclusively owns the platform-neutral child
  protocol plus POSIX hard IO/time/process-group/subreaper cleanup
- **AND** semantic parsing, scheduling policy, Windows behavior, registry,
  receipt and CI authority are excluded and fail closed on scope overlap

#### Scenario: H4, I3 and W1 have exact disjoint authorization objects
- **WHEN** S is published and remote-reachable and maintainers prepare the
  parallel foundation wave in separate clean worktrees
- **THEN** `authorize-bounded-structural-history-engine-v4` contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/deliver-bounded-structural-history-engine-v4.md","successor_id":"deliver-bounded-structural-history-engine-v4","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}`
- **AND** `authorize-bounded-isolated-case-scheduler-v3` contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-isolated-case-scheduler-v3.md","successor_id":"implement-bounded-isolated-case-scheduler-v3","production_loc_ceiling":400,"allow_new_authority_or_wire_protocol":true}`
- **AND** `authorize-native-windows-job-supervisor-v1` contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-native-windows-job-supervisor-v1.md","successor_id":"implement-native-windows-job-supervisor-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

#### Scenario: Parallel foundation ownership stays disjoint
- **WHEN** H4, I3 and W1 are scoped, implemented or independently reviewed
- **THEN** H4 remains `<=349` production LOC as a pure Git traversal/framing/
  memo client of S and owns neither process cleanup nor canonical CI authority
- **AND** I3 remains `<=399` production LOC and owns prelaunch path/root/env/
  jobs validation, deterministic scheduling/order/report schema and focused
  scheduler fixtures over S, but not low-level supervision, Windows behavior
  or canonical CI policy/oracles
- **AND** W1 remains `<=499` production LOC and owns native Windows
  `CREATE_SUSPENDED`, Job Object, correct `ctypes` signatures, handle lifecycle
  and connected native tests, but not POSIX cleanup or scheduler semantics
- **AND** production paths, contracts, tests and authority ownership do not
  overlap, so the three implementation heads may publish independently

#### Scenario: R3 follows every published foundation
- **WHEN** S, H4, I3 and W1 implementation heads are all published and
  remote-reachable
- **THEN** `authorize-bounded-public-release-registry-profile-v3` contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-public-release-registry-profile-v3.md","successor_id":"implement-public-release-registry-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** R3 remains `<=499` production LOC and owns only public registry,
  profile/affected selection and fail-closed diagnostics, excluding supervision,
  history framing, scheduler control, Windows handling, receipt and CI authority

#### Scenario: A3 is the only payload-bound authority owner
- **WHEN** R3 is published and remote-reachable
- **THEN** `authorize-bounded-payload-release-authority-v3` contains exactly `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-payload-bound-release-authority-v3.md","successor_id":"implement-payload-bound-release-authority-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- **AND** A3 remains `<=499` production LOC and exclusively owns bounded
  semantic execution through the published supervisors, per-step telemetry,
  atomic receipt, canonical baseline/CI activation, parsed YAML ownership and
  exact receipt/manifest/review/publish/CI fingerprint equality
- **AND** requested `affected` remains non-authoritative, including any
  fail-closed expansion to a complete profile

#### Scenario: Bounded successor review and terminal failure stay constrained
- **WHEN** an S, H4, I3, W1, R3 or A3 authorization or implementation is
  prepared, reviewed or repaired
- **THEN** it is `ordinary` with a fresh Sol/`high` independent review, at most
  one scoped repair, no credential, mutation, live-admission or
  final-certification authority, and no retry after repeated terminal failure
- **AND** repeated terminal failure creates a separate design decision rather
  than another implementation attempt in that lineage
- **AND** only a separate final-certification card is `critical` and receives a
  fresh Sol/`xhigh` review after measured optimization and all focused, static,
  receipt and native Windows gates are green

#### Scenario: Rescue planning and delivery remain docs-only
- **WHEN** `$changerail-ff` and `$changerail-do` prepare
  `rescue-release-process-supervisor-boundary`
- **THEN** they create/update only this card, one same-slug proposal, design,
  release-CI delta, tasks, synchronized main spec and archive metadata
- **AND** production, test and runtime LOC remain zero and no successor card,
  implementation, history scan, full-release, live Windows run, review, commit
  or push occurs

### Requirement: Published bounded release child supervisor authorization source
ChangeRail MUST publish
`authorize-bounded-release-child-supervisor-v1` as one clean tracked `4.done`
board card before creating successor
`implement-bounded-release-child-supervisor-v1`. The source MUST contain
exactly one schema-valid `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`. Those
fields MUST bind exact published investigation
`rescue-release-process-supervisor-boundary` to the exact future successor
through canonical `4.done` and `3.inprogress` paths, ceiling `500` and protocol
allowance `true`. Future S MUST remain at no more than 499 added production LOC
relative to the exact remote-reachable HEAD that publishes this authorization
source.

#### Scenario: Authorization source publishes before future S creation
- **WHEN** maintainers deliver the bounded child-supervisor authorization after
  the rescue investigation is published
- **THEN** the payload contains only the authorization card, its OpenSpec
  artifacts and this exact release-CI relationship requirement
- **AND** production, test and runtime additions remain zero, future S
  card/code remain absent, and no history scan, full-release baseline or live
  execution is run

#### Scenario: Exact reciprocal lineage is retained for future S
- **WHEN** the authorization source is published and a later separate flow
  creates `implement-bounded-release-child-supervisor-v1`
- **THEN** the published rescue blocks both authorization and future S, while
  this authorization depends on the rescue and blocks only future S
- **AND** future S depends on `rescue-release-process-supervisor-boundary` and
  its `Published investigation authorization` field contains only exact inline
  JSON `{"authorization_card":"openspec/board/4.done/authorize-bounded-release-child-supervisor-v1.md","authorization_id":"authorize-bounded-release-child-supervisor-v1"}`

#### Scenario: S authorization limits protocol and POSIX ownership
- **WHEN** future `implement-bounded-release-child-supervisor-v1` is scoped or
  reviewed against this source
- **THEN** it owns only the platform-neutral child protocol and POSIX hard
  stdout/stderr/report framing, process-group containment, finite deadline,
  TERM-then-KILL escalation, reaping and subreaper cleanup
- **AND** Git parsing, scheduler policy, Windows Job behavior, registry,
  baseline/CI activation, receipt ownership, credential authority, mutation
  authority and live admission are excluded and scope overlap fails closed

#### Scenario: S remains structurally dormant through A3 publication
- **WHEN** this authorization or future S is delivered, reviewed or published
  before exact `implement-payload-bound-release-authority-v3` is published and
  remote-reachable
- **THEN** `run-release-baseline`, the CI workflow, review/publish gates and
  receipt schema do not import or invoke S
- **AND WHEN** exact A3 is published and remote-reachable
- **THEN** only exact A3 integration paths may activate published S

#### Scenario: Authorization and dormant S use focused current proof
- **WHEN** publication eligibility is assessed for this source or future S
- **THEN** this docs-only source uses strict exact-object, reciprocal-relation,
  absence, ownership, JSON, TOML, current public-safety, source-classification,
  whitespace and manifest-scope checks, while future S uses focused static and
  connected POSIX proof
- **AND** neither payload executes, requires or accepts reachable-history,
  full-release, live execution, receipt, review, commit or push activity as
  publication evidence

#### Scenario: Child-supervisor authorization mismatch fails closed
- **WHEN** a card changes any rescue, authorization or successor id/path,
  adds a seventh source field, changes ceiling `500` or protocol `true`,
  creates future S before authorization publication, exceeds 499 added
  production LOC against the published authorization HEAD, expands S ownership
  or wires S before A3
- **THEN** deterministic verification rejects the source or candidate
- **AND** no malformed, partial or over-broad payload can authorize future S
