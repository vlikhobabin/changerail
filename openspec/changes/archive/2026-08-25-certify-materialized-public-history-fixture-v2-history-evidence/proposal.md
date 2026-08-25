## Why

The repaired `history-fixture-v2` payload has no verifiable reachable-history
result: its only source-card capture timed out after 300 seconds with empty
output. Repeating that capture in the same exhausted lineage would permit
outcome-dependent evidence selection, while leaving it unresolved prevents the
fixture from receiving its final source review.

## What Changes

- Define one predeclared, terminal certification capture for the exact repaired
  source fingerprint, fixture fingerprint, detached authority and seven
  immutable authority paths.
- Preserve the original timeout as failed, non-reusable evidence and prohibit
  retry, diagnostic promotion, benchmark rules and source mutation.
- Define the complete-output, exit-status and zero-findings PASS oracle and the
  one-way PASS handoff to a fresh source-card review-only continuation.
- Require the certification policy and documentation payload to be finalized
  and precommitted before capture, followed by one final `critical` Sol/`xhigh`
  review and publish; do not claim the policy is reviewed or published before
  the capture it governs.
- Keep the change documentation/evidence-policy only, with zero added
  production, test or runtime LOC.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `changerail-release-ci`: add the one-shot reachable-history certification
  evidence policy for the exact repaired materialized fixture payload.

## Impact

Affected tracked scope is limited to the certification board card, this
change's OpenSpec artifacts and the `changerail-release-ci` evidence-policy
specification. Delivery may write ignored certification evidence and manifest
state. It does not modify the source fixture worktree, scanner, schemas,
production code, tests, runtime tooling or consumer projects, and it does not
run a benchmark or full release baseline.
