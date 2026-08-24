## Why

Unpublished successor `accelerate-path-sensitive-public-history-scan` exhausted
its only same-card rescue and still accepted malformed `ls-tree -z` framing as
successful empty history while its exact repaired payload missed the frozen
warm threshold. A new implementation attempt therefore requires a published
decision that preserves both blockers, selects one clean replacement and does
not reuse or retrospectively accept the exhausted payload.

## What Changes

- Classify strict history-enumeration framing as a repeated unresolved
  fail-closed invariant and define its exact byte grammar, including
  `raw_name` as exactly one non-empty strict-UTF-8 slash-free Git tree component
  with no NUL, control/DEL, backslash, `.` or `..`, and path safety rules.
- Select one implementation hypothesis: replace process-per-commit `ls-tree`
  enumeration with fresh raw Git tree traversal through a persistent batch
  object reader, while retaining path-sensitive identities and authentic object
  validation.
- Freeze the existing `history-fixture-v1`, legacy oracle, timed boundaries,
  workload, sample/retry policy, unrounded ratios and cold/warm thresholds.
- Bind only `deliver-path-sensitive-public-history-scan-replacement` to a clean
  implementation based on published commit
  `ccccb62562e1646b595119edd3326763860f14a7`, with total added production code
  `<=300` LOC relative to that commit and same-card repair budget `0`.
- Preserve the full history verification floor and make downstream
  `parallelize-isolated-release-smoke-cases` wait for the published replacement.
- Keep this decision payload documentation-only: production additions are
  exactly `0` LOC and no benchmark, history scan or release baseline result is
  claimed.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: strengthen the path-sensitive history contract with
  exact fail-closed framing, immutable benchmark acceptance and clean successor
  lineage after an exhausted implementation.

## Impact

This change affects only the board card, OpenSpec artifacts and the
`changerail-release-ci` relationship contract. It does not modify production
scripts, tests, schemas, runtime, CLI, baseline inventory, consumer projects or
authority. The exhausted implementation and its ignored evidence remain
forensic-only and are neither copied nor published.
