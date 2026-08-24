## ADDED Requirements

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

## MODIFIED Requirements

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
