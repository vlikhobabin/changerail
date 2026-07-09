## Why

Review verdict freshness currently hashes tracked diffs and status output, but
untracked non-ignored file content is represented only by path. A delivered
card can therefore change a newly added file after review without making the
verdict stale.

## What Changes

- Extend the review-verdict fingerprint helper to hash the deterministic list
  of untracked non-ignored paths and each file's content.
- Preserve ignored-file exclusion so runtime files such as `.runtime/` verdicts
  do not invalidate the verdict they record.
- Add a focused smoke check demonstrating both untracked-content sensitivity
  and ignored-file insensitivity.
- Update review verdict documentation and OPSX contracts guidance.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `opsx-contracts`: review verdict freshness fingerprint includes untracked
  non-ignored file content while preserving ignored runtime exclusions.

## Impact

- Affected files: `scripts/opsx_review_verdict.py`, `scripts/`,
  `skills/opsx-review/references/opsx-review-verdict.md`,
  `docs/opsx-contracts.md`, `openspec/specs/opsx-contracts/spec.md`.
- Public helper CLI output format and exit-code behavior stay unchanged.
- Consumer projects get a stronger publish freshness gate without committing
  runtime verdicts, manifests or evidence.
