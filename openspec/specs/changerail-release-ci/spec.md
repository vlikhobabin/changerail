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

### Requirement: Published psutil-backed release child supervisor v2 decision
ChangeRail MUST publish
`rescue-psutil-release-child-supervisor-boundary` as a clean tracked `4.done`
decision after published `rescue-release-process-supervisor-boundary` and
`authorize-bounded-release-child-supervisor-v1`, before creating either
`authorize-psutil-backed-release-child-supervisor-v2` or
`implement-psutil-backed-release-child-supervisor-v2`. The decision MUST block
both future cards and retain exactly this future authorization object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The later authorization MUST depend on this decision and block only the exact
successor. The future implementation MUST depend on both the decision and the
authorization, use only exact inline JSON
`{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}`
as its published authorization reference, and remain at no more than 499 added
production LOC relative to the exact remote-reachable HEAD that publishes its
authorization.

#### Scenario: S2 lineage starts only from the new published decision
- **WHEN** maintainers prepare the psutil-backed S2 lineage
- **THEN** this decision blocks both future cards, the future authorization
  depends on the decision and blocks only the exact future implementation
- **AND** the future implementation depends on both cards and uses the exact
  two-field authorization reference
- **AND** the published S v1 authorization cannot authorize v2, while the
  failed unpublished S2 authorization attempt is not reusable.

### Requirement: Psutil-backed S2 uses bounded portable cleanup
Future `implement-psutil-backed-release-child-supervisor-v2` MUST pin
`psutil==7.1.0` in runtime, development, bootstrap and admission dependency
surfaces. It MUST use a bounded stdlib `selectors`/`prctl` adapter and MUST NOT
assume, require, write or derive authority from a writable cgroup. It MUST
accept distinct positive `execution_timeout` and `cleanup_timeout` values, and
its total elapsed budget MUST be at most
`execution_timeout + cleanup_timeout + 1.0s`; `1.0s` is fixed setup/report
overhead only. Cleanup failure is terminal.

Every psutil error MUST fail closed. The implementation MUST identify a process
by exact `(pid, create_time)`. The `128` unique-identity, `128` descendant-per-
`children(recursive=True)`-scan and `32` cleanup-scan caps are inclusive allowed
maxima: exactly 128/128/32 MUST remain permitted, and only a value greater than
the applicable cap is terminal. It MUST require exactly two consecutive
`children(recursive=True)` scans with empty identity sets before declaring
recursive cleanup successful; the second empty scan is the success threshold,
not a failure cap. Identity mismatch, strict cap excess, timeout or cleanup
error MUST be terminal.

#### Scenario: S2 cleanup rejects unbounded or ambiguous containment
- **WHEN** S2 observes a psutil error, `(pid, create_time)` mismatch, timeout,
  cleanup failure, more than 128 identities, more than 128 descendants in one
  scan or more than 32 scans
- **THEN** it terminates fail-closed and does not report successful cleanup
- **AND** it does not compensate by assuming a writable cgroup or extending the
  exact total timeout budget.

#### Scenario: Stable-empty success requires its second empty scan
- **WHEN** focused negative proof observes zero or one consecutive empty
  `children(recursive=True)` identity set, or observes more than 128 identities,
  more than 128 descendants in one scan or more than 32 cleanup scans
- **THEN** it rejects premature cleanup success for fewer than two empty scans
  and rejects only the strict `>128`/`>128`/`>32` cap excesses
- **AND** exactly 128 identities, 128 descendants in one scan and 32 cleanup
  scans remain allowed, while the second consecutive empty scan reports success.

### Requirement: S2 remains dormant pending publication and downstream refresh
Before exact S2 publication, ChangeRail MUST keep its release baseline, CI workflow, review/publish gate, receipt schema and production entrypoint from importing, invoking or activating S2.
H4, I3, W1, R3 and A3 authorization and implementation work MUST remain
blocked until exact S2 publication and a later tracked refresh explicitly
re-establishes their downstream authorization and dependency relations.

The future S2 proof matrix MUST connect static assertions for: exact
decision/authorization/successor lineage; pin presence in runtime, development,
bootstrap and admission; bounded selector/prctl scope and writable-cgroup
absence; separate timeout arithmetic; psutil error, identity, cap and
stable-empty cleanup; and dormant wiring plus downstream refresh blocking.
Neither this decision nor future S2 may use live execution, reachable history,
full release baseline, review, commit or push as required proof.

#### Scenario: No stale lineage activates S2 or downstream work
- **WHEN** S2 has not been published and a later H4/I3/W1/R3/A3 card is
  planned, implemented, reviewed or activated
- **THEN** deterministic checks reject the attempt until S2 publication and a
  later explicit refresh have established its exact dependency
- **AND** baseline and CI wiring remain absent throughout the dormant period.

### Requirement: Psutil-backed S2 decision delivery remains docs-only
`$changerail-ff` and `$changerail-do` for `rescue-psutil-release-child-supervisor-boundary` MUST create or update only
the same decision card, proposal, design, release-CI delta, tasks, synchronized
main specification and archive metadata. Production, test and runtime LOC MUST
remain zero; future authorization and successor cards/code MUST remain absent;
and only generic forensic summaries of unpublished paths may be tracked.

#### Scenario: Decision does not create authority payloads
- **WHEN** maintainers fast-forward or deliver this decision
- **THEN** no future authorization or implementation card, code, diff,
  evidence, local identifier, history scan, full baseline, live execution,
  review, commit or push is created or accepted as decision evidence.

### Requirement: Published psutil-backed release child supervisor v2 authorization source
ChangeRail MUST publish `authorize-psutil-backed-release-child-supervisor-v2`
as one clean tracked `4.done` board card after published
`rescue-psutil-release-child-supervisor-boundary` and before creating
`implement-psutil-backed-release-child-supervisor-v2`. The source MUST contain
exactly one `Investigation authorization` object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The authorization MUST depend on the published decision and block only the
exact future implementation. The decision MUST block both the authorization
and the implementation. The future implementation MUST depend on both sources,
use only exact inline JSON
`{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}`
as its published authorization reference, and remain at no more than 499 added
production LOC relative to the exact HEAD that publishes this authorization.

#### Scenario: S2 authorization binds only the exact future implementation
- **WHEN** maintainers publish the S2 authorization source
- **THEN** it contains only the exact six-field object, depends on the
  published S2 decision and blocks only the exact future implementation
- **AND** the decision blocks both future cards, while the future implementation
  depends on both and uses only its exact two-field published reference
- **AND** the published S v1 authorization and failed unpublished S2 material
  cannot authorize the replacement.

### Requirement: Authorized S2 keeps the bounded portable cleanup contract
Future `implement-psutil-backed-release-child-supervisor-v2` MUST pin
`psutil==7.1.0` in runtime, development, bootstrap and admission dependency
surfaces. It MUST use a bounded stdlib `selectors`/`prctl` adapter and MUST NOT
assume, require, write or derive authority from a writable cgroup. It MUST
accept distinct positive `execution_timeout` and `cleanup_timeout`; total
elapsed time MUST be at most
`execution_timeout + cleanup_timeout + 1.0s`, where `1.0s` is fixed setup and
report overhead only. Cleanup failure is terminal.

Every psutil error MUST fail closed. The implementation MUST identify every
process by exact `(pid, create_time)`. The inclusive maxima are 128 unique
identities, 128 descendants in each `children(recursive=True)` scan and 32
cleanup scans: exactly each maximum MUST remain permitted and only strict
`>128`, `>128` or `>32` excess is terminal. Recursive cleanup MUST report
success only at the second consecutive empty identity scan; zero or one empty
scan is not successful cleanup. Identity mismatch, timeout or cleanup error is
terminal.

#### Scenario: S2 rejects ambiguous, unbounded or premature cleanup
- **WHEN** S2 observes a psutil error, `(pid, create_time)` mismatch, timeout,
  cleanup failure, strict cap excess or fewer than two consecutive empty scans
- **THEN** it fails closed and does not report successful cleanup
- **AND** exactly 128 identities, 128 descendants and 32 scans remain allowed,
  while the second consecutive empty scan is the success threshold
- **AND** it does not compensate through writable cgroup authority or an
  extended total timeout budget.

### Requirement: Authorized S2 remains dormant pending downstream refresh
Before exact S2 publication, ChangeRail MUST keep the release baseline, CI
workflow, review/publish gate, receipt schema and production entrypoint from
importing, invoking or activating S2. H4, I3, W1, R3 and A3 authorization and
implementation work MUST remain blocked until exact S2 publication and a later
tracked refresh explicitly establishes their downstream authorization and
dependency relations.

The future proof matrix MUST connect static assertions for exact lineage,
four-surface pin, bounded selector/prctl and writable-cgroup absence, timeout
arithmetic, psutil error/identity/cap/stable-empty cleanup and dormant wiring
with downstream refresh blocking. This authorization and future S2 MUST NOT
use live execution, reachable history, full release baseline, review, commit
or push as required proof.

#### Scenario: Authorization does not activate S2 or downstream work
- **WHEN** this authorization is delivered before S2 publication
- **THEN** its payload contains only documentation authority artifacts,
  production, test and runtime additions remain zero, and the future successor
  card/code remain absent
- **AND** baseline and CI wiring stay absent, while downstream H4/I3/W1/R3/A3
  work remains blocked pending later publication and refresh.

### Requirement: Published bounded terminal micro-fix decision MUST precede v3 authorization
ChangeRail MUST publish
`decide-bounded-unpublished-terminal-micro-fix-boundary` as one clean tracked
`4.done` board card after the published psutil S2 decision and authorization,
and before creating either
`authorize-bounded-psutil-supervisor-micro-fix-v3` or
`deliver-psutil-backed-release-child-supervisor-v3`.

The decision MUST block both future cards. Its later authorization MUST depend
on this decision and block only the exact v3 successor. The v3 successor MUST
depend on both sources and use only this exact two-field inline JSON reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The future authorization MUST contain exactly one object with only
`investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

#### Scenario: Decision retains exact v3 lineage without creating it
- **WHEN** maintainers deliver this decision before v3 publication
- **THEN** it blocks the exact authorization and successor, while the future
  authorization depends on the decision and blocks only the successor
- **AND** the successor depends on both cards and uses only its exact two-field
  authorization reference
- **AND** neither future card or executable payload exists in the decision
  delivery.

### Requirement: v3 micro-fix MUST be a clean bounded reconstruction
ChangeRail MUST permit the sole future v3 micro-fix only when its candidate is
unpublished, the exact published authorization is valid, all prior findings
are independently closed, and the latest cycle introduces exactly one new
isolated blocker. It MUST start from the clean HEAD that publishes its own
authorization, remain within the same authorized production paths and at most
499 added production LOC against that HEAD, and MUST NOT expand scope,
dependencies, schema or ownership.

The candidate may mechanically reconstruct executable code and tests from a
frozen failed candidate solely as source material. It MUST NOT reuse terminal
verdict, review history, log, receipt, manifest or evidence, and MUST rerun
every connected R1-R7 proof. It MUST receive exactly one implementation attempt
and one fresh Sol/high review; repair/retry/rescue budget is `0/0/0`. It MUST
NOT gain credential, mutation, live-admission or final authority.

#### Scenario: Reused terminal material cannot admit v3
- **WHEN** a proposed v3 candidate lacks a clean authorization start, exact
  authorization, independently closed prior findings, one isolated new latest
  blocker, fresh R1-R7 proof, unchanged authorized paths/scope or its LOC
  limit
- **THEN** ChangeRail rejects the candidate before review or publication
- **AND** verdict, history, log, receipt, manifest and other terminal evidence
  cannot substitute for the missing fresh proof.

### Requirement: R7 MUST distinguish pipe EOF from execution completion
The v3 micro-fix MUST treat pipe EOF only as stream state. It MUST NOT report
completion while the leader is live. Completion requires observing a terminal
leader state or reaching `execution_timeout`; cleanup MUST run only after that
completion condition. The connected R1-R7 proof MUST freshly cover EOF with a
live leader, observed terminal leader state, execution timeout and cleanup
order.

#### Scenario: Live leader after EOF remains incomplete
- **WHEN** the supervised pipe reaches EOF while the leader remains live
- **THEN** the v3 candidate does not report completion or successful cleanup
- **AND** it waits for a terminal leader observation or execution timeout,
  then performs cleanup under its existing bounded cleanup contract.

### Requirement: v3 and downstream refresh MUST remain dormant before publication
Before v3 publication, ChangeRail MUST keep S3 structurally dormant and MUST
block downstream refresh. The decision, future authorization and successor
MUST NOT create credential, mutation, live or final authority, or activate
release baseline, CI, review/publish gate, receipt schema or production
entrypoint outside the exact existing authorized scope.

#### Scenario: Decision delivery cannot activate S3
- **WHEN** maintainers fast-forward or deliver this docs-only decision
- **THEN** production, test and runtime LOC remain zero, the future
  authorization and successor cards/code remain absent, and downstream refresh
  stays blocked pending S3 publication
- **AND** history, full release baseline, live execution, review, commit and
  push are neither run nor accepted as decision evidence.

### Requirement: Published bounded v3 micro-fix authorization MUST preserve the exact reconstruction boundary
ChangeRail MUST publish `authorize-bounded-psutil-supervisor-micro-fix-v3` as
one clean tracked `4.done` authorization card only after
`decide-bounded-unpublished-terminal-micro-fix-boundary`. The authorization
MUST contain exactly one object with only `investigation_card`,
`investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` and `allow_new_authority_or_wire_protocol`, in this
exact order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The authorization MUST depend on that decision and block only the exact v3
successor. The future successor MUST depend on both sources and use only this
exact two-field inline JSON reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The successor MUST remain absent while this authorization is delivered. If it
is later created, it MUST be eligible only for an unpublished candidate with
this exact valid published authorization, independently closed prior findings
and exactly one new isolated latest blocker. It MUST start from the clean HEAD
that publishes this authorization, remain in the exact authorized production
paths, add at most 499 production LOC relative to that HEAD, and MUST NOT
expand scope, dependencies, schema or ownership.

The successor MAY mechanically reconstruct executable code and tests from the
frozen failed candidate solely as source material. It MUST NOT reuse terminal
verdict, review history, log, receipt, manifest or other evidence, and MUST
rerun every connected R1-R7 proof. It MUST treat pipe EOF as stream state only:
while the leader is live, EOF MUST NOT report completion. Completion requires a
terminal leader observation or `execution_timeout`, followed by cleanup under
the existing bounded cleanup contract.

The successor MUST receive exactly one implementation attempt and one fresh
Sol/high review, with repair/retry/rescue budget `0/0/0`; it MUST NOT gain
credential, mutation, live-admission or final authority. S3 and downstream
refresh MUST remain dormant until S3 publication. This authorization delivery
MUST add production, test and runtime LOC `0`, and MUST NOT create successor
card/code or run or accept history, full release baseline, live execution,
review, commit or push evidence.

#### Scenario: Exact authorization leaves the S3 successor dormant
- **WHEN** maintainers fast-forward or deliver the exact v3 authorization
- **THEN** the one ordered six-field object, reciprocal decision/authorization/
  future-successor lineage and exact two-field future reference are retained
- **AND** successor card/code remains absent, production, test and runtime LOC
  remain zero, and downstream refresh remains blocked pending S3 publication.

#### Scenario: Terminal material cannot substitute for a fresh v3 proof
- **WHEN** a proposed S3 successor lacks clean authorization provenance, exact
  eligibility, unchanged authorized scope, fresh connected R1-R7 proof or the
  required EOF/leader completion behavior
- **THEN** ChangeRail MUST reject it before review or publication
- **AND** frozen terminal verdicts, histories, logs, receipts, manifests and
  evidence MUST NOT substitute for the missing fresh proof.

### Requirement: Published brokered supervision decision MUST precede v4 authorization
ChangeRail MUST publish `decide-brokered-release-child-supervision-boundary` as
one clean tracked `4.done` docs-only card after the published terminal v3
decision and authorization, and before creating either
`authorize-bounded-brokered-release-child-supervisor-v4` or
`deliver-brokered-release-child-supervisor-v4`.

The decision MUST block both future cards. The future authorization MUST depend
on this decision and block only the exact implementation. The future
implementation MUST depend on both and use only this exact inline reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}
```

The future authorization alone MUST contain exactly one object with only the
following six fields in this order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Publication of this decision MUST exhaust and supersede the earlier future
`deliver-psutil-backed-release-child-supervisor-v3` path. The published v3
decision and authorization MUST remain immutable historical sources, but MUST
NOT authorize creation, continuation, repair, rescue, reuse or publication of
v3 after this decision. Exact v4 MUST be the sole conforming future release
child supervisor implementation path.

#### Scenario: Decision creates no future authority or implementation
- **WHEN** maintainers deliver this decision
- **THEN** it retains the exact future six-field and two-field objects plus
  reciprocal blocks/dependencies without creating either future card or code
- **AND** terminal v3 material remains forensic-only and supplies no authority,
  evidence, verdict, history, log, receipt or manifest
- **AND** any attempt to create, continue, repair, rescue, reuse or publish v3,
  or to introduce a supervisor successor other than exact v4, is rejected.

### Requirement: Broker subprocess MUST own the supervised process tree by construction
The future v4 controller MUST launch one dedicated broker in a new session or
equivalent platform containment unit. Before target launch the broker MUST
enable its child-supervision role and emit a bounded readiness message. Only
the broker may launch the target, discover its descendants or perform target
cleanup.

The application caller MUST NOT enable child-subreaper mode, scan caller-global
children, infer ownership from a caller before/after snapshot or claim a
pre-existing bystander and descendants that the bystander creates later. On
Linux the broker MUST become subreaper before target launch and start with no
application workload child other than the target.

#### Scenario: Later bystander descendant remains outside broker ownership
- **WHEN** a pre-existing caller child creates a new descendant after broker
  readiness while the target also forks, creates a session or exits
- **THEN** broker discovery and cleanup include only broker-owned target
  identities, every owned target identity is gone before success, and the
  bystander identities remain alive and unmodified.

### Requirement: Broker protocol and cleanup MUST be bounded and fail closed
The future v4 parent-broker protocol MUST use one closed version, monotonically
increasing sequence numbers, bounded message bytes, bounded total bytes and
bounded message count. It MUST permit exactly one `ready`, exactly one
`started`, bounded observations and exactly one terminal report after cleanup.
Pipe EOF MUST be stream state only.

Malformed UTF-8 or JSON, unknown/duplicate fields or messages, sequence drift,
truncation, premature EOF, multiple terminal reports, broker exception, target
identity error, execution timeout, cleanup timeout, identity/cap error or
missing cleanup proof MUST be terminal and MUST NOT report success. Every
recoverable post-launch broker exception MUST enter bounded broker-owned
cleanup. Successful cleanup MUST require two consecutive empty owned-identity
scans and no live or zombie owned identity.

The parent MUST keep a bounded outer process-group or platform containment path
for an unresponsive broker and MUST report terminal failure without claiming
that a process group contains detached sessions. The future implementation
MUST state and prove its fatal broker-death guarantee precisely.

#### Scenario: Protocol or broker fault cannot manufacture success
- **WHEN** the protocol is malformed, truncated, out of sequence, reaches EOF
  early, exceeds a bound, the broker raises after target launch, or cleanup
  proof is absent
- **THEN** the controller returns one bounded terminal failure and never a
  successful completion
- **AND** recoverable post-launch faults clean the broker-owned tree before the
  terminal report, while fatal broker-death coverage is not overstated.

### Requirement: Brokered v4 MUST use a clean bounded delivery and proof cycle
Future `deliver-brokered-release-child-supervisor-v4` MUST start from the exact
HEAD that publishes its authorization, use only the exact two-field reference,
add at most 499 production LOC and add no external dependency beyond the
already published psutil pin. It MUST NOT reuse terminal v3 code, verdict,
history, logs, receipts, manifests or evidence; generic forensic findings may
inform a fresh implementation and proof only.

The connected proof MUST cover pre-existing bystander plus later descendant,
pre-ready launch rejection, immediate post-launch identity fault, live-leader
pipe EOF, normal/signal/crash/timeout completion, setsid/double-fork, inherited
pipe, TERM-ignore/fork-during-cleanup, output and protocol N/N+1 bounds,
malformed/truncated/duplicate protocol, broker exception, timeout arithmetic,
two-empty cleanup and no-live/no-zombie results. V4 MUST remain dormant outside
focused tests until exact publication, and downstream activation MUST remain
blocked pending a later tracked refresh.

V4 receives one implementation attempt and one fresh Sol/high review. A first
NO-GO permits at most one bounded same-card repair and one final Sol/high
re-review; a third review, rescue, retry or terminal evidence reuse is
forbidden.

#### Scenario: One bounded repair replaces repeated rescue lineages
- **WHEN** the first fresh v4 review returns NO-GO for an in-scope defect
- **THEN** maintainers may perform exactly one bounded same-card repair and one
  final Sol/high re-review
- **AND** any surviving blocker after that re-review is terminal and cannot
  create another repair, rescue, publication or evidence-reuse path.

### Requirement: Brokered decision delivery MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC `0`, MUST NOT
create either future card or code, and MUST NOT activate release baseline, CI,
review/publish, receipt or downstream work. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Decision cannot activate brokered supervision
- **WHEN** the decision is planned, delivered, reviewed or published
- **THEN** only its card, same-slug artifacts, synchronized main spec and
  archive metadata change
- **AND** all executable and downstream activation surfaces remain unchanged.

### Requirement: Published brokered v4 authorization MUST bind only exact v4
ChangeRail MUST publish
`authorize-bounded-brokered-release-child-supervisor-v4` as one clean tracked
`4.done` docs-only card after published
`decide-brokered-release-child-supervision-boundary` and before creating
`deliver-brokered-release-child-supervisor-v4`.

The authorization MUST depend on the exact decision and block only exact v4.
It MUST contain exactly one object with only the following six fields in this
order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}
```

It MUST start from the exact HEAD that publishes this authorization, add at
most 499 production LOC, add no external dependency beyond the published
psutil pin, and implement the complete broker ownership, protocol, cleanup,
fatal-death honesty and proof boundary from the decision. It receives one
initial Sol/high review, at most one bounded same-card repair and one final
Sol/high re-review. Any surviving blocker is terminal.

The earlier v3 executable path MUST remain exhausted. Published v3 sources are
immutable history but MUST NOT authorize implementation work. Exact v4 and all
downstream activation MUST remain dormant until v4 publication and a later
tracked refresh.

#### Scenario: Authorization leaves exact v4 absent and dormant
- **WHEN** maintainers deliver this authorization
- **THEN** its exact six-field object, reciprocal lineage, future two-field
  reference, clean-start/LOC/proof/review boundaries and v3 exhaustion remain
  machine-checkable
- **AND** future v4 card/code, executable activation, downstream refresh,
  history, full baseline and live matrix evidence remain absent.

### Requirement: Brokered v4 authorization delivery MUST remain docs-only
The authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` specification and archive
metadata. Production, test and runtime LOC MUST remain zero. It MUST NOT create
the successor, dependency changes, protocol schema, executable code, CI,
baseline, receipt, review/publish activation or retained runtime evidence.

#### Scenario: Docs-only authority does not execute the future protocol
- **WHEN** the authorization is planned, delivered, reviewed or published
- **THEN** no broker process, target process, history scan, full baseline or
  live matrix is started or accepted as authorization evidence.

### Requirement: Connected broker proof decision MUST precede v5 authorization
ChangeRail MUST publish `decide-connected-broker-supervisor-proof-boundary` as
one clean tracked `4.done` docs-only card after the published broker v4 decision
and authorization, and before creating either
`authorize-bounded-connected-broker-supervisor-v5` or
`deliver-connected-broker-supervisor-v5`.

The decision MUST block both future cards. The future authorization MUST depend
on this decision and block only the exact implementation. The future
implementation MUST depend on both and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

The future authorization alone MUST contain exactly one object with only these
six fields in this order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Publication of this decision MUST exhaust the unpublished v4 implementation
path. Published v4 sources remain immutable history but MUST NOT authorize v4
creation, continuation, repair, rescue, reuse or publication after this
decision. Exact v5 MUST be the sole conforming future broker-supervisor path.

#### Scenario: Decision creates no future authority or implementation
- **WHEN** maintainers deliver this decision
- **THEN** it retains the exact future objects and reciprocal lineage without
  creating either future card or executable payload
- **AND** v4 code, verdict, history, manifest, logs and evidence remain
  forensic-only and cannot authorize or satisfy v5.

### Requirement: V5 MUST prove outer cleanup through public supervise
The future v5 focused proof MUST invoke public `supervise` for fatal broker-loss
and outer-timeout scenarios. It MUST observe bounded terminal failure and prove
that no same-process-group target survives. It MUST NOT call `_stop_group`
directly as a substitute for the production connection.

The proof MUST execute the same scenario against a disposable source mutation
that removes the exact public-path `_stop_group(proc)` exception or timeout
wiring. It MUST verify that the mutation changed the intended construct and
that the connected scenario fails. A no-op, ambiguous or unexecuted mutation
MUST fail the proof.

#### Scenario: Removed supervise cleanup wiring turns proof red
- **WHEN** the disposable candidate removes the outer cleanup call used by
  public `supervise`
- **THEN** the identical public scenario detects the missing cleanup connection
  and fails
- **AND** direct helper invocation cannot make the counterfactual pass.

### Requirement: V5 MUST prove pidfd signaling after identity validation
The future v5 focused proof MUST invoke public `supervise`, pass exact identity
validation, reach the signaling operation and observe use of
`pidfd_send_signal`. PID-only `os.kill(pid, sig)` MUST NOT substitute for this
operation.

The proof MUST execute the same scenario against a disposable source mutation
that replaces the pidfd signal operation with PID-only signaling. It MUST
verify the intended mutation occurred and that the connected scenario fails on
the forbidden backend observation. Rejection before any signal is attempted is
insufficient.

#### Scenario: PID-only signaling turns proof red
- **WHEN** the disposable candidate replaces post-identity pidfd signaling with
  `os.kill(pid, sig)`
- **THEN** the public connected scenario reaches signaling, observes the
  forbidden backend and fails
- **AND** an earlier identity mismatch cannot satisfy this proof.

### Requirement: V5 MUST be a clean bounded one-review delivery
Future `deliver-connected-broker-supervisor-v5` MUST start from the exact HEAD
that publishes its authorization, use only the exact two-field reference, add
at most 499 production LOC and add no dependency. It MUST reconstruct code and
tests from published requirements and generic findings only; terminal v4 code,
card, verdict, history, logs, manifest and evidence MUST NOT be copied or
accepted.

V5 MUST retain bounded canonical and counterfactual command evidence for R8 and
R9, preserve the published broker ownership/protocol/cleanup contract and stay
dormant outside focused tests. It receives exactly one implementation attempt
and one fresh Sol/high review with repair/retry/rescue budget `0/0/0`.

#### Scenario: Missing connected counterfactual blocks v5
- **WHEN** a proposed v5 lacks clean authorization provenance, exact scope,
  canonical public-path proof, either effective counterfactual mutation,
  retained fresh evidence or the LOC/dependency boundary
- **THEN** ChangeRail rejects it before publication
- **AND** no repair, retry, rescue or terminal v4 evidence reuse is permitted.

### Requirement: Connected proof decision MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC `0`, MUST NOT
create either future card or code, and MUST NOT activate release baseline, CI,
receipt, review/publish or downstream work. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Decision cannot execute v5 proof
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only its card, same-slug artifacts, synchronized main spec and
  archive metadata change
- **AND** all executable and downstream surfaces remain unchanged.

### Requirement: Published connected broker v5 authorization MUST bind exact proof
ChangeRail MUST publish `authorize-bounded-connected-broker-supervisor-v5` as
one clean tracked `4.done` docs-only card after published
`decide-connected-broker-supervisor-proof-boundary` and before creating
`deliver-connected-broker-supervisor-v5`.

The authorization MUST depend on the decision and block only exact v5. It MUST
contain exactly one object with only these six fields in this order and with
these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future v5 implementation MUST depend on both published sources and use
only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

It MUST start from the exact HEAD that publishes this authorization, add at
most 499 production LOC and add no dependency. It MUST reconstruct code and
tests from published requirements and generic findings only; terminal v4 code,
card, verdict, history, logs, manifest and evidence MUST NOT be copied or
accepted.

V5 MUST execute R8 fatal/timeout cleanup and R9 post-identity pidfd signaling
through public `supervise`. Disposable effective source mutations MUST remove
the public outer cleanup wiring and replace pidfd signaling with PID-only
signaling; each identical connected scenario MUST turn red. Direct private
helper calls, rejection before signaling and no-op/ambiguous mutations MUST NOT
satisfy the proof. Fresh bounded canonical and counterfactual evidence MUST be
retained for the v5 payload.

V5 receives exactly one implementation attempt and one fresh Sol/high review
with repair/retry/rescue budget `0/0/0`. It remains dormant outside focused
tests and cannot activate release baseline, CI, receipts, review/publish or
downstream work.

#### Scenario: Exact authorization leaves v5 absent
- **WHEN** maintainers deliver this authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start,
  LOC, proof and review boundaries remain machine-checkable
- **AND** successor card/code, executable activation, history, full baseline
  and live matrix evidence remain absent.

#### Scenario: Disconnected proof cannot satisfy authorization
- **WHEN** a future candidate calls private cleanup directly, rejects before
  signaling, omits either effective mutation or reuses v4 evidence
- **THEN** ChangeRail rejects it before publication
- **AND** the zero-repair budget does not authorize retry or rescue.

### Requirement: Connected broker v5 authorization MUST remain docs-only
This authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized release-CI specification and archive metadata.
Production, test and runtime LOC MUST remain zero. It MUST NOT create the
successor, dependency changes, schema, executable code, CI, baseline, receipt,
review/publish activation or retained runtime evidence.

#### Scenario: Authorization cannot execute v5
- **WHEN** maintainers plan, deliver, review or publish this authorization
- **THEN** no broker, target, history scan, full baseline or live matrix is
  started or accepted as authorization evidence.

### Requirement: Connected broker supervisor v5 MUST satisfy its public-path proof
ChangeRail MUST allow `deliver-connected-broker-supervisor-v5` only from exact
published authorization HEAD `888f2aaeb5a5b352474c100c63c68f1de612a7a1`,
with this sole authorization reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

The implementation MUST add no dependency and at most 499 production LOC. It
MUST use one dedicated Linux broker subprocess that becomes subreaper before
target launch, owns only its target tree and communicates through a closed,
versioned, bounded ready/started/terminal protocol. Protocol faults, EOF,
overflow, timeout, broker loss and incomplete cleanup MUST fail closed.

Recoverable broker faults MUST clean exact owned descendants through bounded
TERM/KILL/reap and two empty scans. Identity-bound signals MUST use pidfds after
identity validation. Fatal controller paths MUST perform bounded outer broker
process-group cleanup without claiming coverage of detached sessions.

The focused proof MUST call public `supervise` for R8 fatal/timeout cleanup and
R9 post-identity pidfd signaling. It MUST execute identical scenarios against
effective disposable source mutations that remove public outer cleanup wiring
and replace pidfd signaling with PID-only signaling. Each mutation MUST be
unique, asserted and turn its connected scenario red. Direct private cleanup
calls, rejection before signaling, no-op/ambiguous mutations and terminal v4
evidence MUST NOT satisfy the proof.

V5 MUST retain fresh bounded canonical/counterfactual evidence, remain dormant
outside focused tests and receive exactly one Sol/high review with `0/0/0`
repair/retry/rescue budget.

#### Scenario: Canonical public path passes and counterfactuals fail
- **WHEN** maintainers execute the focused v5 proof
- **THEN** canonical public `supervise` proves outer cleanup and pidfd signaling
  with no owned survivor
- **AND** each exact disposable mutation demonstrably changes source and makes
  the identical public scenario fail for its intended missing connection.

#### Scenario: Disconnected or reused proof blocks publication
- **WHEN** either connected mutation is absent, ineffective or bypasses public
  `supervise`, or any v4 runtime evidence is reused
- **THEN** review returns NO-GO and the zero-repair v5 lineage terminates.

### Requirement: Connected broker v5 MUST remain dormant after delivery
The v5 delivery MUST NOT wire its module into release baseline, CI, receipts,
review/publish or downstream activation. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Focused delivery creates no activation
- **WHEN** maintainers implement, verify, review or publish v5
- **THEN** only its dormant module, focused test, card, OpenSpec artifacts and
  necessary metadata change
- **AND** production entrypoints and canonical release execution stay unchanged.

### Requirement: Accelerated loop decision MUST split scheduler and activation
ChangeRail MUST publish
`decide-accelerated-release-loop-integration-boundary` as one clean tracked
`4.done` docs-only card after published
`deliver-connected-broker-supervisor-v5` commit
`9872d4edd5c35eb51d64d1199000c029f11bd92d` and before creating any future
scheduler, affected-profile or certification card.

The decision MUST block exact scheduler authorization and implementation,
affected-profile authorization and implementation, and final certification.
The only conforming publication order MUST be decision, scheduler
authorization, scheduler implementation, affected authorization, affected
implementation and certification. Every predecessor MUST be published and
remotely reachable before the next card is created.

#### Scenario: Decision leaves all successors absent
- **WHEN** maintainers deliver this decision
- **THEN** exact lineage and ordering are retained without creating a future
  card or executable payload
- **AND** private prototypes and terminal unpublished candidates remain
  forensic-only and cannot satisfy any dependency or evidence gate.

### Requirement: Scheduler authorization MUST bind dormant bounded execution
Future `authorize-bounded-release-semantic-scheduler-v1` MUST depend on this
published decision and block only exact
`implement-bounded-release-semantic-scheduler-v1`. The authorization alone MUST
contain exactly one object with only these six fields in this order and exact
values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

It MUST start from the exact authorization-publishing HEAD, add at most 499
production LOC and import only published connected broker v5 for child process
ownership. It MUST prevalidate one immutable plan of 1..64 unique task IDs,
commands, timeouts and isolated roots before launch; accept jobs 1..4; execute
each task exactly once; cancel outstanding work after terminal failure; and
emit one deterministic registry-ordered result per task.

Every child MUST retain v5's 8192-byte combined-output cap. Scheduler summary
MUST be at most 64 KiB and MUST NOT contain raw child output. Malformed,
duplicate, unknown, missing, over-bound or incomplete task/result state MUST
fail closed.

Scheduler v1 MUST NOT own Git selection, release profiles, semantic inventory,
runner/CI activation, receipts, review/publish or authority. It MUST remain
dormant outside focused tests until exact affected-profile implementation.

#### Scenario: Dormant scheduler proves bounded ordered execution
- **WHEN** future scheduler v1 receives valid independent tasks with jobs 1 and
  default jobs up to 4
- **THEN** it executes each task exactly once through v5 and returns identical
  deterministic ordered results
- **AND** connected fault fixtures prove prelaunch rejection, failure
  cancellation, timeout/output bounds and no owned survivor.

#### Scenario: Scheduler cannot activate itself
- **WHEN** scheduler authorization or implementation is delivered
- **THEN** repository-wide wiring proof finds no baseline, CI, receipt,
  review/publish or other production activation
- **AND** history, full baseline and live matrix evidence are not run or
  accepted.

### Requirement: Affected authorization MUST own selection and sole activation
Future `authorize-bounded-affected-release-profile-v1` MUST be created only
after published scheduler v1, depend on this decision and that implementation,
and block only exact `implement-bounded-affected-release-profile-v1`. The
authorization alone MUST contain exactly one object with only these six fields
in this order and exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation MUST depend on all published predecessors and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

It MUST start from the exact authorization-publishing HEAD and add at most 499
production LOC. It MUST own the canonical semantic inventory, exact physical
resolution, bounded NUL Git selector and the sole runner import/activation of
scheduler v1. It MUST NOT redefine v5 or scheduler supervision, cleanup or
result contracts.

Zero arguments MUST remain the compatibility alias for requested
`full-release`; explicit `--profile full-release` MUST be identical. Requested
`affected` MUST require exactly one `--base`; invalid or repeated combinations
MUST fail before admission or semantic launch.

Selection MUST aggregate committed, staged, unstaged and untracked paths and
retain rename/copy old and new operands. Invalid or non-ancestor base, unknown
status, malformed framing, absolute/traversal/control path, unknown or
ambiguous ownership, selector/authority self-change, Git nonzero/stderr/timeout
or any declared path/count/byte bound breach MUST deterministically select the
full semantic inventory with a fallback reason.

#### Scenario: Known paths select bounded required semantics
- **WHEN** affected mode receives valid docs-only or owned-Python changes
- **THEN** selection includes the invariant safety floor and every exact
  functional owner with deterministic deduplication and order
- **AND** scheduler executes only that resolved plan once.

#### Scenario: Uncertainty falls back without authority
- **WHEN** selector input is unknown, ambiguous, self-referential, malformed or
  over bound
- **THEN** affected mode selects the exact full semantic inventory and records
  its deterministic fallback reason
- **AND** requested affected remains non-authoritative.

### Requirement: Full release MUST remain the only authoritative profile
Requested profile MUST determine authority. Every requested `affected` result
MUST report `authoritative:false`, including exact full fallback and successful
execution. Only an admitted requested `full-release` that executes and passes
the exact full semantic inventory MAY report `authoritative:true`.

Canonical CI MUST contain exactly one active explicit full runner and MUST NOT
invoke affected mode, scheduler, broker or individual semantic commands
directly. Parsed YAML and Python AST ownership proof MUST reject inactive,
duplicate, chained, wrapped, indirect, reordered or additional execution
surfaces.

Review, publish, receipt and certification gates MUST reject affected output,
timing, fallback or selected-result JSON as full-release evidence.

#### Scenario: Affected success cannot authorize publish
- **WHEN** requested affected execution passes a subset or its full fallback
- **THEN** the result remains diagnostic and non-authoritative
- **AND** review, publish and receipt gates cannot accept it as full evidence.

#### Scenario: Canonical CI executes only full release
- **WHEN** maintainers validate the release workflow
- **THEN** one active exact full-release runner owns all semantic execution
- **AND** any affected or alternate direct execution path makes the parsed
  ownership oracle fail.

### Requirement: Final certification MUST be single-shot and evidence-only
`certify-accelerated-release-loop-v1` MUST be created only after both exact
implementations are published and remotely reachable. It MUST change
production, test and runtime LOC 0 and MUST be the sole card in this lineage
that may run reachable-history or full-release evidence.

Certification MUST first obtain one fresh critical Sol/xhigh pre-capture audit.
On GO it MUST run exactly one reachable-history scan and exactly one requested
full-release baseline with retry/repair/rescue budget `0/0/0`. It MUST also run
one disposable clean docs-only affected scenario, one owned-Python affected
scenario and one unknown-path full fallback.

Docs-only MUST finish within 15 seconds and select at most 15 semantic IDs.
Owned Python MUST finish within 120 seconds. Unknown input MUST select the
exact full semantic inventory and remain non-authoritative. Timing MUST be
monotonic diagnostic evidence and MUST NOT affect selection, pass/fail,
authority, ordering, retry or receipt eligibility.

#### Scenario: Single-shot acceleration certification passes
- **WHEN** pre-capture audit is GO and the one allowed evidence sequence
  satisfies correctness, authority, parity and performance contracts
- **THEN** certification retains fingerprint-bound bounded evidence and may be
  published
- **AND** no second history or full execution is permitted.

#### Scenario: Failed measurement cannot be repaired in certification
- **WHEN** any history, full, affected, fallback, timing, RSS, freshness or
  authority assertion fails
- **THEN** certification terminates without production repair or evidence retry
- **AND** any redesign requires a new investigation.

### Requirement: Integration decision MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC 0 and modify
only its card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata. It MUST NOT create
future cards, code, dependencies, schemas, runner/CI wiring, receipts or
review/publish activation.

It MUST NOT run or accept reachable-history, full release baseline, live matrix
or private prototype evidence. It receives one fresh Sol/high review with one
same-card docs repair available.

#### Scenario: Decision cannot claim implementation acceleration
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only exact lineage, ownership, order, limits and certification
  contracts change
- **AND** current release execution behavior remains unchanged.

### Requirement: Published scheduler authorization MUST bind exact dormant scope
ChangeRail MUST publish `authorize-bounded-release-semantic-scheduler-v1` as
one clean tracked `4.done` docs-only card after published
`decide-accelerated-release-loop-integration-boundary` commit
`0de81cf7e578335c728466b81c1c60b6d447dab7` and before creating
`implement-bounded-release-semantic-scheduler-v1`.

The authorization MUST depend on the decision, block only exact scheduler v1
and contain exactly one object with only these six fields in this order and
exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future implementation MUST depend on both published sources and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

It MUST start from the exact authorization-publishing HEAD, add at most 499
production LOC and import only published connected broker supervisor v5 for
child ownership. Terminal unpublished prototypes, cards, verdicts, manifests,
logs and evidence MUST NOT satisfy its implementation or review.

#### Scenario: Exact authorization leaves successor absent
- **WHEN** maintainers deliver this authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start and
  LOC boundaries remain machine-checkable
- **AND** successor card/code, executable activation and expensive evidence
  remain absent.

### Requirement: Scheduler authorization MUST freeze bounded execution contract
Future scheduler v1 MUST prevalidate one immutable plan of 1..64 unique task
IDs, commands, timeouts and isolated roots before launching any child. It MUST
accept jobs 1..4, execute each task exactly once through published v5, cancel
outstanding tasks on terminal failure and emit exactly one deterministic
registry-ordered result per task.

Every child MUST retain v5's 8192-byte combined-output cap. The scheduler
summary MUST be at most 64 KiB and MUST contain no raw child output. Malformed,
duplicate, missing, unknown, incomplete or over-bound task/result state MUST
fail closed.

Scheduler MUST NOT own Git selection, semantic inventory, release profiles,
runner/CI activation, receipts, review/publish or authority. It MUST remain
structurally dormant outside focused tests until exact later affected-profile
implementation activates it.

#### Scenario: Future scheduler proves jobs parity and cancellation
- **WHEN** focused scheduler proof executes independent tasks with jobs 1 and
  default jobs up to 4
- **THEN** results have identical exact-once registry order and bounded schema
- **AND** prelaunch, failure, timeout, output, malformed-result and descendant
  fixtures fail closed without an owned survivor.

#### Scenario: Unauthorized activation blocks successor
- **WHEN** a future scheduler candidate imports into baseline, CI, receipt,
  review/publish or another production entrypoint
- **THEN** structural dormancy proof and review fail
- **AND** the authorization cannot be used to widen that scope.

### Requirement: Scheduler authorization MUST remain docs-only
This authorization delivery MUST modify only its card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` specification and archive
metadata. Production, test and runtime LOC MUST remain 0. It MUST NOT create
the successor, dependency changes, schemas, executable code, CI, baseline,
receipt, review/publish activation or retained runtime evidence.

It MUST NOT run or accept reachable-history, full release baseline or live
matrix evidence. It receives one fresh Sol/high review with one same-card docs
repair available.

#### Scenario: Authorization cannot execute scheduler work
- **WHEN** maintainers plan, deliver, review or publish this authorization
- **THEN** only exact authorization and bounded future contracts change
- **AND** no scheduler, semantic task, history scan, full baseline or live
  matrix is started or accepted.

### Requirement: Scheduler v1 MUST execute bounded plans deterministically
`implement-bounded-release-semantic-scheduler-v1` MUST start from published
authorization HEAD `ad6fa60cd641838cbef31059245e8cee9cbaa601`, use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

and add at most 499 production LOC with no dependency. It MUST import only
published connected broker v5 for child ownership.

The scheduler MUST validate one closed immutable plan of 1..64 unique bounded
task IDs, commands, execution/cleanup timeouts and direct-child root names. It
MUST reserve all unique isolated roots before semantic launch and MUST launch
zero tasks on any validation or allocation failure.

Jobs MUST be an integer 1..4. Each started task MUST invoke public v5
`supervise` exactly once. Jobs 1 and default parallel execution MUST return the
same exact-once deterministic registry-ordered result sequence for equivalent
task outcomes.

The production path MUST use a `ProcessPoolExecutor` with explicit
multiprocessing `spawn`, never fork, and one manager-backed process-safe
terminal event shared by every worker wrapper. Each wrapper MUST set the event
after normalizing a failure and before returning it. A later activating
entrypoint MUST call the scheduler only under a guarded `__main__` path.
Focused deterministic proof MAY use a bounded thread executor only with an
injected supervisor. Constructor, submit, wait and shutdown faults MUST become
one complete ordered fail/cancelled result sequence and MUST NOT escape as a
partial result.

#### Scenario: Prevalidation reserves all roots before execution
- **WHEN** a plan contains malformed, duplicate, over-bound or colliding input
- **THEN** scheduler returns or raises a bounded validation failure before any
  supervisor call
- **AND** it removes only empty roots created by the failed reservation attempt.

#### Scenario: Parallel completion retains registry order
- **WHEN** valid independent tasks complete in different orders under jobs 1
  and jobs 4
- **THEN** every task executes exactly once and both summaries retain original
  plan order
- **AND** each result has the exact closed bounded field set.

### Requirement: Scheduler v1 MUST fail fast without bypassing v5 cleanup
Scheduler MUST set one shared terminal event after the first terminal task
failure, supervisor exception or malformed supervisor result. Tasks not yet
started MUST NOT call
the supervisor and MUST receive one deterministic cancelled result. Already
running tasks MUST finish through public v5 bounded cleanup before scheduler
returns.

Every child MUST retain the v5 8192-byte combined-output cap. Scheduler summary
MUST be canonical JSON serializable, at most 64 KiB and contain no raw output.
Malformed, duplicate, missing, unknown, incomplete or cross-field-invalid
result state MUST fail closed.

#### Scenario: First failure cancels unstarted tasks
- **WHEN** one task fails while more tasks remain pending than available jobs
- **THEN** no pending task starts after the terminal event and each receives
  exactly one cancelled result
- **AND** running tasks finish cleanup and the overall summary fails.

#### Scenario: Real broker faults remain bounded
- **WHEN** connected tasks exceed output, timeout, emit malformed protocol or
  leave descendants
- **THEN** public v5 returns bounded failure and cleanup completes as its
  contract requires
- **AND** scheduler neither manufactures pass nor leaves an owned survivor.

### Requirement: Scheduler v1 MUST remain dormant and authority-free
Scheduler v1 MUST NOT own Git selection, semantic inventory, release profiles,
runner/CI activation, receipts, review/publish or authority. No production
entrypoint MUST import or invoke it before exact later affected-profile
implementation.

Delivery MUST retain focused connected proof, production LOC at most 499,
exact authorization provenance and no history/full/live evidence. It receives
one fresh Sol/high review and one same-card repair opportunity.

#### Scenario: Dormancy scan rejects early activation
- **WHEN** focused proof scans tracked production entrypoints, scripts and CI
- **THEN** scheduler and scheduler-use of broker appear only in its dormant
  module and focused tests
- **AND** any baseline, CI, receipt or review/publish activation fails delivery.

### Requirement: Published affected authorization MUST bind exact activation scope
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v1` как одну
clean tracked `4.done` docs-only card после published
`decide-accelerated-release-loop-integration-boundary` commit
`0de81cf7e578335c728466b81c1c60b6d447dab7` и published
`implement-bounded-release-semantic-scheduler-v1` commit
`1414fd744eab565258d590a18fe687e39461b9af`, до создания
`implement-bounded-affected-release-profile-v1`.

Authorization MUST зависеть от decision и scheduler implementation, блокировать
только exact affected implementation и содержать ровно один object только с
этими six fields в этом порядке и с exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Future implementation MUST зависеть от всех трех published sources и
использовать только:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

Она MUST начинаться от exact authorization-publishing HEAD, добавлять не более
499 production LOC, импортировать published scheduler v1 только в release
runner и не переопределять broker/scheduler supervision, cleanup либо result
contracts. Terminal unpublished prototypes, cards, verdicts, manifests, logs и
evidence MUST NOT удовлетворять implementation или review.

#### Scenario: Exact authorization leaves successor absent
- **WHEN** maintainers deliver эту authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start и
  LOC boundaries остаются machine-checkable
- **AND** successor card/code, executable activation и expensive evidence
  остаются absent.

### Requirement: Affected authorization MUST freeze selection and authority
Future affected profile v1 MUST владеть canonical semantic inventory, exact
physical resolution, bounded NUL Git selector и sole runner activation
published scheduler v1. Selector MUST aggregate committed, staged, unstaged и
untracked paths, сохраняя old+new operands rename/copy.

Zero arguments MUST оставаться compatibility alias requested `full-release`, а
explicit `--profile full-release` MUST быть identical. Requested `affected`
MUST требовать ровно один `--base`; invalid, missing, repeated или unknown CLI
combinations MUST fail before admission или semantic launch.

Invalid/non-ancestor base, malformed framing, unknown status, invalid path,
unknown/ambiguous ownership, selector/authority self-change, Git
nonzero/stderr/timeout или declared path/count/byte bound breach MUST выбирать
exact full inventory с bounded deterministic fallback reason.

Requested `affected` MUST всегда возвращать `authoritative:false`, включая
успешный full fallback. Только admitted requested `full-release`, выполнивший и
прошедший exact full inventory, MAY вернуть `authoritative:true`. Review,
publish, receipt и certification gates MUST отвергать affected output как full
evidence.

#### Scenario: Known input selects required semantics once
- **WHEN** affected получает valid docs-only или owned-Python Git state
- **THEN** invariant safety floor и каждый exact functional owner выбираются в
  deterministic inventory order
- **AND** scheduler выполняет только resolved plan, каждый task ровно один раз.

#### Scenario: Uncertainty falls back without authority
- **WHEN** input unknown, ambiguous, self-referential, malformed или over-bound
- **THEN** affected выбирает exact full inventory и bounded fallback reason
- **AND** requested affected остается non-authoritative.

### Requirement: Affected authorization MUST preserve canonical full runner
Canonical CI MUST содержать ровно один active exact explicit full-release
runner и MUST NOT отдельно запускать affected, scheduler, broker или individual
semantic commands. Parsed YAML/Python-AST ownership proof MUST отвергать
inactive, duplicate, chained, wrapped, indirect, reordered или additional
execution surfaces.

Authorization MUST оставаться docs-only: только card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` spec и archive metadata.
Production/test/runtime LOC MUST быть 0. Successor, dependencies, schemas, code,
CI, baseline, receipts и review/publish activation MUST оставаться absent.

Она MUST NOT запускать или принимать reachable-history, full release baseline,
affected execution, live matrix либо terminal prototype evidence. Требуется один
fresh Sol/high review с одной доступной same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review или publish authorization
- **THEN** меняются только exact lineage и bounded future contracts
- **AND** ни один semantic task, selector, history, full baseline, affected или
  live matrix не запускается и не принимается.

### Requirement: Exact report/proof rescue MUST replace terminal unpublished affected paths
ChangeRail MUST publish
`rescue-affected-release-profile-exact-report-proof-boundary` as one docs-only
decision from exact published `authorize-bounded-affected-release-profile-v1`
commit `cd5393a643b7b0e8f9ea83574945b837aa4089e8`.

The unpublished `implement-bounded-affected-release-profile-v1` and unpublished
`rescue-affected-release-profile-closed-validation-boundary` paths MUST be
terminal, non-conforming and forensic-only. Their payloads, cards, manifests,
verdicts, logs and evidence MUST NOT satisfy any dependency, authorization,
implementation, review or publication gate. Published cards and archives MUST
remain unchanged.

The only conforming order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v2`, clean
`implement-bounded-affected-release-profile-v2`, then
`certify-accelerated-release-loop-v1`. The v2 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-report-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v1`. It MUST block only
`implement-bounded-affected-release-profile-v2`.

The v2 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

Its `Depends On` relation MUST contain exactly those four published predecessors
plus `authorize-bounded-affected-release-profile-v2`; it MUST block only
`certify-accelerated-release-loop-v1`; it MUST start from the
authorization-publishing HEAD, add at most 499 production LOC and reconstruct
from published sources without copying or cherry-picking terminal work.

#### Scenario: Rescue leaves one published-source successor path
- **WHEN** maintainers publish this decision
- **THEN** both unpublished predecessor paths are exhausted and exact v2 lineage is exclusive
- **AND** authorization, implementation and certification successors remain absent.

### Requirement: Affected v2 MUST preserve admission and non-authority boundaries
Future v2 MUST preserve exact 35-ID registry/digest, complete 35→30 physical
resolution, bounded aggregate NUL Git selector, rename/copy old+new operands,
sole scheduler v1 activation and full-only authority without changing published
broker/scheduler supervision or cleanup.

Both requested profiles MUST complete one aggregate bounded effective-PATH
admission before Git selection and before any semantic scheduler call. Admission
MUST verify Python `>=3.11`, exact requirement pins and installed origins, Ruff
`0.6.9` from the selected environment, Git/repository identity, Node/npm/npx,
pinned OpenSpec `1.3.1` offline and every registry target. Any admission fault
MUST return one bounded aggregate failure with `semantic_started: 0` and MUST
launch no semantic task.

Requested affected MUST remain `authoritative:false` for subset success and
full fallback. Only admitted requested full-release with exact complete pass MAY
be authoritative. V2 MUST create and accept no receipt, capture, marker or
cache. Review, publish and certification gates MUST reject affected/focused
output and every forged or replayed protocol artifact as full evidence.

#### Scenario: Admission or protocol uncertainty cannot authorize
- **WHEN** admission fails, affected falls back, or receipt/capture/marker/cache material appears
- **THEN** semantic launch is zero on admission failure and authority remains false
- **AND** no protocol artifact can upgrade affected or focused output.

### Requirement: Affected v2 MUST validate exact scheduler summaries and rows
At the runner trust boundary, a scheduler summary MUST have exactly fields
`version`, `status`, `jobs`, `results`; version MUST equal
`changerail.release-semantic-scheduler.v1`; jobs MUST equal requested `1` or
`4`; results MUST contain every planned physical ID exactly once in registry
order. Summary status MUST be exactly `pass` if all rows have status `pass` and
MUST be exactly `fail` otherwise.

Every row MUST have exactly `id`, `status`, `reason`, `returncode`,
`output_bytes`, `cleanup_complete`, `messages`. Return code MUST be null or an
exact integer and MUST NOT be boolean; output and messages MUST be exact
non-negative integers, not booleans, within `0..8193` and `0..3`; cleanup MUST
be boolean; reason MUST be bounded ASCII. Each row MUST satisfy exactly one:

- pass MUST be status `pass`, reason `completed`, return code `0`, output
  `0..8192`, cleanup `true`, messages `3`;
- `child_failed` MUST be status `fail`, nonzero integer return code, output
  `0..8192`, cleanup `true`, messages `3`;
- `execution_timeout` MUST be status `fail`, integer return code, output
  `0..8192`, cleanup `true`, messages `3`;
- `output_limit` MUST be status `fail`, integer return code, output `8193`,
  cleanup `true`, messages `3`;
- `cleanup_incomplete` MUST be status `fail`, null or integer return code,
  output `0..8193`, cleanup `false`, messages `3`;
- `internal_error` MUST be status `fail`, null or integer return code, output
  `0..8192`, boolean cleanup, messages `3`;
- `protocol_error`, `broker_lost`, `outer_timeout` or `outer_cleanup_error` MUST
  be status `fail`, null or integer return code, output `0`, cleanup `false`,
  messages `0..2`;
- `supervisor_result_error`, `supervisor_error` or `executor_error` MUST be
  status `fail`, null return code, output `0`, cleanup `false`, messages `0`;
- `cancelled` MUST be status `fail`, null return code, output `0`, cleanup
  `true`, messages `0`.

Missing/extra fields, unknown reasons, invalid cross-fields, wrong summary
status, missing/duplicate/unknown/reordered/cross-ID rows and canonical JSON over
64 KiB MUST fail terminal and MUST NOT authorize full release.

#### Scenario: Every non-all-pass summary is exact fail
- **WHEN** any terminal, outer or synthetic row occurs or any row/schema invariant fails
- **THEN** summary status is exactly `fail` and release authority is false
- **AND** a failure row can never claim status `pass` or another status.

### Requirement: Affected v2 MUST validate the exact canonical CI schema
Canonical CI MUST parse YAML without YAML 1.1 key coercion. Its top-level field
set MUST be exactly `{name, on, permissions, jobs}` with name `ChangeRail CI`,
trigger map keys exactly `push`, `pull_request`, `workflow_dispatch` and each
trigger value exactly null, permissions exactly `{contents: read}`, and only
job `verify`.

The verify-job field set MUST be exactly `{name, runs-on, steps}` with name
`Verify ChangeRail release gates` and `runs-on: ubuntu-latest`. It MUST contain
exactly these ordered steps and no others:

1. fields `{name, uses, with}`, name `Check out repository`,
   `uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5`,
   `with: {fetch-depth: "0"}`;
2. fields `{name, uses, with}`, name `Set up Node.js for OpenSpec wrapper`,
   `uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`,
   `with: {node-version: "20"}`;
3. fields `{name, run}`, name `Prepare offline release dependencies`, and exact
   run scalar:

```text
python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install --disable-pip-version-check -r requirements-dev.txt
echo "$PWD/.runtime/changerail/ci-venv/bin" >> "$GITHUB_PATH"
./bin/openspec --version >/dev/null
```

4. fields `{name, run}`, name `Run canonical full release`, and exact run
   `python3 scripts/run-release-baseline.py --profile full-release`.

Any other top-level/job/step field, job, trigger/value, permission, action,
`with` key/value, run, order or step; workflow/job/step `env`; strategy/matrix;
condition; continue-on-error; timeout; shell; working-directory; wrapper;
chain; indirect runner; affected, scheduler, broker or individual semantic
command MUST fail the parsed ownership oracle.

#### Scenario: CI schema mutation cannot preserve authority
- **WHEN** any top-level, job, trigger, permission, action, with-map, run, field, order or gating value changes
- **THEN** the parsed CI oracle fails even if the canonical runner text remains
- **AND** no alternate execution surface can satisfy canonical full release.

### Requirement: Affected v2 MUST retain exhaustive connected counterfactual proof
Disposable focused scheduler fixtures MUST enumerate every valid row tuple and
mutate each status/reason/return-code/output/cleanup/message cross-field,
top-level field/version/jobs/status, summary size, result count, identity,
order, missing/extra/duplicate/unknown/cross-ID row. Protocol fixtures MUST add,
forge and replay receipt, capture, marker and cache artifacts and prove none can
change authority.

CI fixtures MUST mutate every exact top-level and verify-job field set/name,
each trigger key/value, permission, action SHA, `with` map, step name/field/order,
run scalar, workflow/job/step env, extra job/uses/run, one/multiple matrix,
condition, continue-on-error, timeout, shell/working-directory and direct,
chained, wrapped or indirect execution surface.

The preserved selector/admission/authority floor MUST cover Git A/M/D/R/C
old+new operands, staged/unstaged/untracked aggregation, base/framing/status/
path/count/per-path/aggregate/stderr/nonzero/timeout/self/unknown fallbacks,
zero semantic launch for every admission fault, zero-argument/full parity,
exact full authority and affected subset/full-fallback non-authority. Every
mutation MUST assert it changed the fixture and MUST fail if its corresponding
guard is weakened.

#### Scenario: No-op or disconnected fixture cannot count
- **WHEN** a fixture misses a row/protocol/CI/selector/admission/authority branch or mutates the wrong surface
- **THEN** the required proof remains incomplete
- **AND** no no-op mutation or tautological assertion is accepted.

### Requirement: Exact report/proof rescue MUST remain docs-only
This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
code, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
benchmark, live matrix, certification or unpublished prototype evidence. One
fresh Sol/high review and one same-card docs repair are available.

#### Scenario: Decision cannot claim executable closure
- **WHEN** this decision is delivered or reviewed
- **THEN** only lineage and exact future trust boundaries change
- **AND** executable closure remains absent until separately published v2 work.

### Requirement: Affected v2 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v2` as one
docs-only authorization from exact published
`rescue-affected-release-profile-exact-report-proof-boundary` commit
`64ba9ab5c3af79c3babc4800969a68eae20ec5bb`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-report-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v1`. It MUST block only
`implement-bounded-affected-release-profile-v2`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

It MUST start from the authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the four published predecessors above plus this published
authorization and block only `certify-accelerated-release-loop-v1`. Its card,
change and executable payload MUST remain absent until this authorization is
committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** the implementation successor remains absent until publication.

### Requirement: Affected v2 authorization MUST preserve the exact trust boundary
The future implementation MUST preserve without weakening the published
decision's exact 35-ID registry/digest, complete 35→30 physical resolution,
bounded aggregate NUL Git selector, rename/copy old+new operands, complete
aggregate effective-PATH admission before selection and semantics, sole
scheduler v1 activation and full-only authority.

It MUST validate scheduler summary status exactly `pass` iff all rows pass and
exactly `fail` otherwise; every terminal, outer and synthetic row MUST have
status `fail` and its exact published reason/cross-field tuple. It MUST create
and accept no receipt, capture, marker or cache. Affected/focused output and
forged/replayed protocol artifacts MUST NOT satisfy review, publish or
certification authority.

It MUST preserve the literal canonical-CI top-level/job/trigger/permission/
action/with/run/field/order schema and the exhaustive connected mutation floor
for scheduler rows/summaries, protocol artifacts, CI surfaces, Git selector,
admission zero-launch and full-only authority. Terminal unpublished v1 or prior
rescue code, cards, manifests, verdicts, logs and evidence MUST NOT be copied,
cherry-picked or accepted.

#### Scenario: Authorization cannot narrow published proof
- **WHEN** the future implementation plans or verifies its trust boundary
- **THEN** every exact report, protocol, CI, selector, admission and authority invariant remains mandatory
- **AND** no terminal unpublished payload or evidence can satisfy it.

### Requirement: Affected v2 authorization MUST remain docs-only
This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
dependencies, schemas, code, CI, baseline, receipt or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
benchmark, live matrix, certification or terminal prototype evidence. It
requires one fresh Sol/high review and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
