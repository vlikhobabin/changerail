## Why

Review preflight normalizes authorization relations only through lowercase card
id regexes. Consumer boards that mandate sortable UTC filenames therefore
cannot cite otherwise valid published investigation chains because the exact
ids contain uppercase `T` and `Z`.

## What Changes

- Admit one explicit sortable UTC timestamp-prefix alternative at the existing
  exact card-reference matcher.
- Preserve fail-closed rejection for arbitrary mixed-case ids, malformed
  timestamps, unrelated stems and noncanonical board paths.
- Add matcher and full authorization-chain smoke coverage.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-contracts`: exact published-investigation references also accept
  repository-mandated sortable UTC timestamp card ids.

## Impact

The change is limited to `scripts/changerail_review_preflight.py`, its focused
smoke, and the existing contracts spec. It changes no verdict schema, authority
payload, filesystem access or consumer board naming policy.
