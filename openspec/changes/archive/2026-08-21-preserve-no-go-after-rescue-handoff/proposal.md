## Why

After a final independent `no-go`, delivery must create a tracked rescue or
replacement handoff. That safe post-review mutation intentionally makes the
negative verdict fingerprint stale, but the runner currently misclassifies the
valid safety stop as `BLOCKED/review_verdict_invalid`.

## What Changes

- Validate an unpublished verdict structurally before terminal classification.
- Treat schema-valid `no-go` as a conservative `NO-GO` signal without requiring
  current-tree freshness.
- Continue requiring exact freshness before interpreting `go` as an
  unpublished positive verdict.
- Add deterministic smoke coverage for a tracked rescue card created after the
  final negative review.

## Capabilities

### Modified Capabilities
- `changerail-delivery-runner`: preserve the negative terminal outcome across
  mandatory rescue-handoff mutation while keeping positive paths fail-closed.

## Impact

The generic delivery runner, its smoke fixture, public contracts documentation
and consumer projects using final review-budget handoffs are affected. No
schema, authority or wire protocol changes.
