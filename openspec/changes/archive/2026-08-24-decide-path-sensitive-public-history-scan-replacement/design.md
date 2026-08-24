## Context

Published decision `investigate-deterministic-release-baseline-acceleration` at
`ccccb62562e1646b595119edd3326763860f14a7` remains the last safe source. It
requires fresh reachable-input enumeration, exact `(blob, path)` identities,
batch object I/O, fail-safe ignored cache, legacy parity, frozen cold/warm
acceptance and unchanged mandatory baseline coverage.

The first implementation successor is unpublished and exhausted. Independent
review cycle 1 found four blockers. After its only same-card rescue, cycle 2
closed cache totality and duration coverage but retained two blockers:

- non-empty `ls-tree -z` output without a terminal NUL, and output containing
  an empty record, both became successful empty history;
- the exact repaired payload produced a warm/legacy median ratio of `5.0094%`,
  above the immutable `<=5%` threshold, while CV was already `<=15%` and thus
  did not permit a favorable rerun.

The exhausted diff fingerprint
`sha256:2904deabe2cc8c6ce6d1dfa2410cf2e1f513c5673409f700898286b53e47d116`
identifies forensic input only. This decision does not copy its source, tests,
artifacts, runtime records or evidence. It records only the published contract
and the two independently reviewed blocker outcomes.

## Goals / Non-Goals

**Goals:**

- Resolve the repeated fail-closed framing class with a total byte grammar.
- Choose one implementation design with enough structural margin for the
  frozen warm `<=5%` gate.
- Keep the complete unpublished capability in one clean `<=300` production-LOC
  successor rooted at the last safe source.
- Freeze benchmark and review policy so implementation cannot move the oracle,
  workload, timer or threshold.
- Preserve full verification and make smoke parallelization wait for a
  published replacement.

**Non-Goals:**

- Repairing, copying, archiving, accepting or publishing the exhausted payload.
- Changing `history-fixture-v1`, its parent oracle, workload, sample order,
  timed boundaries, rounding rule or thresholds.
- Running a benchmark, reachable-history scan or full release baseline during
  this decision.
- Changing production scripts, tests, schemas, runtime, CLI, baseline
  inventory, consumer contracts or any authority.
- Creating the implementation successor or downstream smoke card in this
  change.

## Decisions

### 1. The exhausted payload is terminal forensic input

`accelerate-path-sensitive-public-history-scan` remains `NO-GO` with rescue
budget `1/1` consumed. No file or evidence entry from that worktree is an input
to implementation. The only source baseline for production code is exact
commit `ccccb62562e1646b595119edd3326763860f14a7`; the exact scanner blob there is
`74b218d8d92274d73ffaea129404749a330e8320` and the exact baseline-runner blob is
`01e8fac656f359077f65a26b508a74ada389ce89`.

This decision payload has `Repeated defect class: no` because it changes zero
production lines. It nevertheless classifies the source problem as a repeated
unresolved fail-closed framing invariant. The implementation successor may keep
that review flag `no` only by using the structural raw-tree simplification below
and satisfying every framing negative. Reintroducing a production `ls-tree`
enumerator, weakening the grammar or using another hypothesis is a new
investigation-required scope.

### 2. `ls-tree -r -z` has one exact fail-closed grammar

The repeated defect is specified independently of implementation language. For
`git ls-tree -r -z --full-tree <commit>`, let `NUL = b"\x00"`, `SP = b" "` and
`TAB = b"\x09"`:

```text
stream = b"" | record (NUL record)* NUL
record = mode SP type SP oid TAB path
mode   = "100644" | "100755" | "120000" | "160000"
type   = "blob" for 100644/100755/120000 | "commit" for 160000
oid    = lowercase hexadecimal with exact object-format width
path   = non-empty strict UTF-8 repository-relative bytes
```

Object format is read fail-closed before parsing: `sha1` means exactly 40 OID
characters and `sha256` means exactly 64; any other format, uppercase digit,
non-hex byte or width mismatch is invalid. Header contains exactly two single
spaces and exactly one separator TAB. Type and mode MUST match the table.

Only `b""` is a valid empty tree. Every non-empty stream MUST end in exactly one
terminal NUL. The decoder removes that one byte and then requires every split
record to be non-empty, so `b"\x00"`, a missing terminal NUL, consecutive NULs
and an additional terminal NUL are invalid. It parses all records before root,
skip-directory or selected-type filtering; malformed unselected records cannot
be hidden by a filter.

Decoded path bytes MUST round-trip through strict UTF-8 and MUST NOT contain a
NUL, ASCII control/DEL character, backslash, leading slash, drive prefix, empty
component, `.` component or `..` component. Duplicate exact paths in one stream
are invalid. Command failure, malformed framing, invalid header/OID/type,
undecodable or unsafe path produces one redacted hard history failure before
any cache lookup, cache reuse, successful history result or partial finding is
emitted.

This grammar remains the compatibility and fault-matrix oracle. The chosen
production replacement does not consume `ls-tree` output, eliminating the
repeated parser from its success path rather than trying a second local patch.

### 3. The only implementation hypothesis is persistent raw-tree batch traversal

`deliver-path-sensitive-public-history-scan-replacement` will freshly obtain
the ordered commit set with `git rev-list --all` and object format on every
invocation. One persistent `git cat-file --batch` reader will then read commit,
tree and authentic cache-miss blob objects. There is no `ls-tree` process per
commit and no process-per-blob `git show`.

Raw tree bodies use Git's native repeated framing:

```text
raw_tree = b"" | raw_entry+
raw_entry = raw_mode SP raw_name NUL raw_oid_bytes
```

`raw_mode` is exactly `40000`, `100644`, `100755`, `120000` or `160000`;
`raw_name` is exactly one non-empty Git tree path component: bytes that
round-trip through strict UTF-8 unchanged and contain none of NUL, slash,
ASCII control/DEL or backslash, and are neither `.` nor `..`. It is validated
as one component before prefixing, with no splitting, normalization or
repository-relative-path interpretation. `raw_oid_bytes` is exactly 20 bytes
for SHA-1 or 32 bytes for SHA-256. Tree mode maps only to a `tree` object,
regular/executable/symlink modes only to `blob`, and gitlink mode only to
`commit`. Batch response headers, declared sizes, terminal LF, object OID and
type are checked before a body is used. Short/long bodies, missing separators,
an empty, undecodable or unsafe `raw_name` (including a slash-bearing name),
duplicate names, type mismatch, missing objects or unexpected trailing bytes
are hard failures before traversal materialization, cache lookup, cache reuse,
output, partial findings or successful history result.

Each unique tree body is decoded once into immutable child entries. Traversal
still retains `(tree_oid, path_prefix)` when the same tree is reachable below
different prefixes, and materializes the ordered per-commit occurrence table
before any success. All selected blob OIDs are authentically type-checked.
Unique `(blob_oid, exact_path)` identities retain the published policy digest,
cache envelope, redaction, bound and invalidation contract; cache hits never
replace fresh commit/tree traversal.

The single performance hypothesis is that removing all per-commit `ls-tree`
process launches and de-duplicating repeated tree-object decoding gives a
stable warm margin below `5%` of the exact legacy oracle. No cache-layout,
concurrency, fixture or threshold change is a second hypothesis. Failure of
this hypothesis ends the successor rather than opening a same-card repair.

### 4. `history-fixture-v1` and its benchmark policy are immutable

The successor inherits `history-fixture-v1` exactly: fixture fingerprint
`sha256:4575cd8b42082d57c25cf474427579c3559aa8a5b3989413a91c40a876c5cf28`,
48 commits, 1152 selected occurrences, 96 unique `(blob,path)` identities and
72 unique blobs. It retains unchanged, rename, same-blob/two-path,
binary/invalid UTF-8, secret/redaction, new/deleted ref and corruption cases.
Any byte, ref, path, count, generation order or fingerprint drift is a failure,
not `history-fixture-v2` inside this successor.

Legacy behavior is materialized only from
`ccccb62562e1646b595119edd3326763860f14a7:scripts/public-surface-scan.py`, blob
`74b218d8d92274d73ffaea129404749a330e8320`. Candidate and legacy receive the
same fixture snapshot, roots, environment controls and normalized output
comparison. No result from the exhausted implementation is an oracle.

One sample's monotonic timer starts immediately before spawning the scanner
process and stops only after process exit and complete stdout/stderr collection.
Fixture construction, checkout, empty-cache preparation, host metadata capture
and post-run RSS analysis stay outside the timed interval. Within each complete
trial the immutable order is legacy uncached, candidate with an empty cache,
then its immediate candidate warm rerun without Git, policy or cache mutation.
Each trial uses a fresh temp root.

The harness performs exactly two discarded complete warmup trials followed by
five measured complete trials. Medians and population CV are computed from
unrounded monotonic seconds. Display may use six decimals, but verdict ratios
use the unrounded medians: cold/legacy MUST be `<=0.20` and warm/legacy MUST be
`<=0.05`. If every mode has CV `<=0.15`, no rerun is allowed. Otherwise the
entire measured set is discarded and exactly one complete five-trial set is
run; it wholly replaces the first and cannot be selected by outcome. A second
CV failure is `NOT-VERIFIABLE`, not a pass.

Every measured Git child remains covered by exact per-process VmHWM and 100 ms
parent/descendant RSS sampling. Child VmHWM MUST be `<=256 MiB`; aggregate RSS
MUST be `<=128 MiB + 256 MiB * active job ceiling`. Missing process samples,
fixture/parity mismatch, a numeric bound breach or either performance ratio
exits non-zero. Exact-payload raw output and summary are retained in the
successor's ignored card-owned evidence index before review; a prose-only prior
pass claim is insufficient.

### 5. One exact clean successor owns the whole unpublished capability

After this decision is independently reviewed and published, maintainers may
create only `deliver-path-sensitive-public-history-scan-replacement`. Its
worktree starts clean from the published decision lineage, while all production
LOC accounting and semantic parent comparisons use exact
`ccccb62562e1646b595119edd3326763860f14a7`.

The successor owns fresh reachability, raw commit/tree/blob batch parsing,
path-sensitive occurrence materialization, cache totality/invalidation,
legacy/fault/benchmark fixtures and per-step baseline duration. Added production
LOC across `scripts/public-surface-scan.py` and
`scripts/run-release-baseline.py`, classified relative to `ccccb625`, MUST be
`<=300`. It introduces no new production file, public schema/CLI, authority,
receipt, step skip, baseline inventory change or smoke parallelization.

The implementation review policy has same-card repair/rescue budget `0`: initial
cycle `1`, `same_card_rescue_attempt: 0`, limit `0`, used `0`, remaining `0`.
Any `NO-GO`, failed immutable threshold or unverified mandatory criterion is
terminal for that card: no semantic edit, rerun selection or re-review is
allowed in the same card. A new published investigation/replacement is
required.

### 6. Verification is an indivisible floor

The successor records focused RED against the exact safe parent before GREEN.
Connected framing negatives cover valid `b""`; valid multi-record output;
missing, single-only, interior and extra NULs; malformed spaces/TABs; mode/type
mismatch; wrong-width, uppercase and non-hex OIDs; invalid UTF-8; absolute,
traversal, control, backslash and duplicate paths. Raw batch/tree negatives
cover header/type/size/LF errors, short OIDs/bodies, duplicates, missing objects
and cleanup after failure. A connected successor fixture injects a
slash-bearing `raw_name` and proves a hard failure before traversal output,
cache lookup, cache reuse, partial findings or successful history result.
Parity, cache corruption/permissions/bounds,
policy/content/path/ref invalidation and SHA-1/SHA-256 remain mandatory.

After focused GREEN, the exact floor is:

- focused history and baseline-duration RED/GREEN plus the immutable benchmark;
- scanner self-test, current scan and authentic cold/warm reachable-history
  scans;
- Python compile and repository Ruff checks for every changed/new Python file;
- strict target-change and all-change OpenSpec validation;
- JSON/TOML parse, source-classification, public-surface and whitespace checks,
  including untracked files;
- delivery manifest scope/fingerprint, production-LOC classification and
  deterministic review preflight;
- exactly one final full `scripts/run-release-baseline.py` after every earlier
  check and exact-payload benchmark is GREEN;
- a fresh independent ordinary-risk review of that unchanged fingerprint.

The full history scan, benchmark and full baseline are successor evidence only.
They are explicitly forbidden as GREEN claims and are not run by this
decision-only change.

### 7. Smoke parallelization remains downstream

`parallelize-isolated-release-smoke-cases` depends on a published
`deliver-path-sensitive-public-history-scan-replacement` with the full
verification floor and fresh `GO`. It cannot depend on the exhausted card,
consume its evidence, or begin from this decision alone. Its final baseline
evidence continues to include the published replacement history step.

## Risks / Trade-offs

- [Risk] Raw tree parsing introduces another framing surface. -> The grammar is
  smaller than recursive `ls-tree` orchestration, fully byte-bounded and covered
  by connected mode/type/OID/body fault probes before cache access.
- [Risk] A 300 LOC ceiling may be too small for safe raw traversal plus cache. ->
  The successor owns one implementation attempt and must simplify helpers; an
  over-ceiling payload stops instead of requesting a local exception.
- [Risk] Freezing a noisy benchmark can produce `NOT-VERIFIABLE`. -> Timer,
  ordering, CV replacement rule and unrounded ratios are fixed in advance; no
  favorable rerun is possible.
- [Risk] Tree de-duplication can lose path-sensitive identity. -> Bodies are
  decoded once, but traversal and cache identity retain exact path prefixes and
  ordered commit occurrences.
- [Trade-off] Rejecting unusual control/backslash paths may reject a valid Git
  repository. -> Public history safety is fail-closed; an unsupported path
  returns non-zero rather than silently excluding content.

## Migration Plan

1. Deliver, independently review and publish this documentation-only decision.
2. Create the exact clean replacement card from the published decision lineage;
   do not copy the exhausted payload or its evidence.
3. Implement the one raw-tree hypothesis within `<=300` production LOC and run
   the complete immutable verification floor once the focused suite is GREEN.
4. On first `NO-GO` or hypothesis failure, stop with zero same-card repair and
   require a new investigation.
5. Only after the replacement publishes may downstream smoke parallelization
   proceed. Rollback is the exact safe behavior at `ccccb625`; no exhausted
   implementation is a rollback source.

## Open Questions

- none
