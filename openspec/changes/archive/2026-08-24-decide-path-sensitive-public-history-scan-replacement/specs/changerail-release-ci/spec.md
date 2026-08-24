## ADDED Requirements

### Requirement: Exhausted path-sensitive history acceleration is replaced fail-closed
ChangeRail MUST treat the exhausted
`accelerate-path-sensitive-public-history-scan` payload as forensic-only and
MUST allow only `deliver-path-sensitive-public-history-scan-replacement` to
reimplement the unpublished capability from exact safe commit
`ccccb62562e1646b595119edd3326763860f14a7`. The replacement MUST use fresh
persistent raw-tree batch traversal, MUST add at most 300 production LOC
relative to that commit, and MUST have zero same-card repair or rescue
attempts. Each raw-tree `raw_name` MUST be exactly one non-empty Git tree path
component: strict UTF-8 bytes that round-trip unchanged, contain no NUL, slash,
ASCII control/DEL or backslash, and are neither `.` nor `..`; it MUST be
validated before prefixing, without splitting or normalization.

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

#### Scenario: Clean replacement enumerates reachable objects
- **WHEN** the replacement performs a current cold or warm history scan
- **THEN** it freshly enumerates every reachable commit and traverses strict
  commit/tree/blob framing through one persistent batch object reader without a
  production `ls-tree` process per commit
- **AND** it preserves ordered per-commit findings and exact `(blob,path)` cache
  identity while treating every malformed, missing or mistyped object as a hard
  history failure

#### Scenario: Frozen benchmark evaluates the exact successor
- **WHEN** the successor runs `history-fixture-v1`
- **THEN** fixture fingerprint
  `sha256:4575cd8b42082d57c25cf474427579c3559aa8a5b3989413a91c40a876c5cf28`,
  scale `48/1152/96/72`, legacy blob
  `74b218d8d92274d73ffaea129404749a330e8320`, workload, timed process boundary,
  trial order, two discarded warmups and five measured trials are unchanged
- **AND** unrounded medians satisfy cold/legacy `<=0.20` and warm/legacy
  `<=0.05`, with no rerun when CV is `<=0.15` and at most one whole-set
  replacement when CV is higher

#### Scenario: Initial replacement review is not successful
- **WHEN** the exact successor receives `NO-GO`, misses a frozen performance or
  memory threshold, exceeds 300 added production LOC, or lacks any mandatory
  focused, history, baseline, manifest, preflight or independent-review proof
- **THEN** same-card repair and re-review are forbidden because its rescue limit
  and remaining budget are both zero
- **AND** the exhausted payload remains unpublished and downstream
  `parallelize-isolated-release-smoke-cases` remains blocked pending a new
  published decision and replacement
