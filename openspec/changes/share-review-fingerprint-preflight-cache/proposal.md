## Why

Delivery computes the same exact payload fingerprint before review, while
validating a verdict and again before publish. After the tree builder is exact
and path-scoped, repeated gates should share one canonical implementation and
may reuse a validated unchanged-workspace result without weakening freshness.

## What Changes

- Make review preflight, independent review verdict validation and publish
  freshness checks call the same canonical fingerprint implementation.
- Add a bounded, ignored runtime cache for unchanged workspace fingerprint
  results, keyed by machine-checkable workspace state rather than prose.
- Ensure cache hits are validated against current HEAD and changed path metadata
  before reusing `tree_sha` or `diff_fingerprint`.
- Document when cache reuse is allowed and when the helper must recompute.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: review freshness consumers share the canonical
  fingerprint implementation and may reuse validated unchanged-workspace cache
  entries without weakening exact payload freshness.

## Impact

- Affected files: `scripts/changerail_review_verdict.py`,
  `scripts/changerail_review_preflight.py`, `bin/changerail-review-verdict`,
  publish/review skill references or docs if needed, smoke tests and OpenSpec
  contract artifacts.
- Cache files remain in ignored `.runtime/changerail/` state and are not part
  of the public tracked surface.
- Freshness validation continues to fail closed on missing, stale or malformed
  cache entries.
