# Investigate bounded review fingerprint payload

## Status
1.backlog

## Owner
ChangeRail maintainer

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- `openspec/board/5.canceled/optimize-review-fingerprint-for-large-repositories.md`
- Deterministic review preflight from the retained first implementation.

## Summary
The first implementation of the review fingerprint optimization passed its
focused verification but deterministic review preflight stopped before model
review because it added 527 production Python lines. The ordinary limit is 300
and published investigation authorization is capped at 500.

Investigate the retained generic implementation, identify a concrete bounded
simplification that preserves exact fingerprint freshness and focused smoke
coverage, and publish a decision that makes a replacement payload no larger
than 500 added production LOC.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Blocks
- `deliver-bounded-review-fingerprint-optimization`

## Acceptance
- Reproduce the preflight breakdown from public-safe retained evidence and
  explain why the first payload measured 527 added production LOC.
- Identify concrete duplication or over-expansion that can be removed without
  weakening exact reviewed-tree parity, untracked-content hashing, cache
  invalidation, diagnostics or focused benchmark coverage.
- Define a replacement implementation boundary no larger than 500 added
  production LOC; authorization must not raise the global limit or exceed the
  existing bounded maximum.
- State the verification floor and exact successor card that the decision
  authorizes.
- Do not publish the retained unreviewed implementation or treat its WIP commit
  as review evidence.

## Non-Goals
- Bypassing deterministic preflight or independent semantic review.
- Raising the global production LOC ceiling.
- Removing edge-path parity or cache invalidation tests to reduce line count.
- Changing fingerprint authority or wire protocol.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `openspec/changes/measure-review-fingerprint-costs/`
- `openspec/changes/optimize-review-fingerprint-tree-build/`
- `openspec/changes/share-review-fingerprint-preflight-cache/`
- `openspec/board/1.backlog/authorize-bounded-review-fingerprint-payload.md`
- `openspec/board/1.backlog/deliver-bounded-review-fingerprint-optimization.md`

## Result
not started

## Next
- `$chrl-ff openspec/board/1.backlog/investigate-bounded-review-fingerprint-payload.md`

## Log
- 2026-08-19T07:17:52Z created after deterministic preflight stopped the
  retained 527-production-LOC implementation before independent review.
