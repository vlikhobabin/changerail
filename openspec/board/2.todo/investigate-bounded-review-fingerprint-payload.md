# Investigate bounded review fingerprint payload

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- `openspec/board/5.canceled/optimize-review-fingerprint-for-large-repositories.md`
- Deterministic review preflight from the retained first implementation.
- Public-safe diff summary retained from the stopped first implementation.

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
- Do not publish the retained unreviewed implementation or treat its local
  checkpoint as review evidence.

## Non-Goals
- Bypassing deterministic preflight or independent semantic review.
- Raising the global production LOC ceiling.
- Removing edge-path parity or cache invalidation tests to reduce line count.
- Changing fingerprint authority or wire protocol.

## Change Set
- `decide-bounded-review-fingerprint-payload`

## Verify
- `./bin/openspec validate "decide-bounded-review-fingerprint-payload" --strict`
- `./bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/decide-bounded-review-fingerprint-payload/`
- `openspec/changes/measure-review-fingerprint-costs/`
- `openspec/changes/optimize-review-fingerprint-tree-build/`
- `openspec/changes/share-review-fingerprint-preflight-cache/`
- `openspec/board/1.backlog/authorize-bounded-review-fingerprint-payload.md`
- `openspec/board/1.backlog/deliver-bounded-review-fingerprint-optimization.md`

## Result
planned

## Next
- `$chrl-do openspec/board/2.todo/investigate-bounded-review-fingerprint-payload.md`

## Change 1: `decide-bounded-review-fingerprint-payload`

### Why
The retained first implementation correctly stopped before independent review:
deterministic preflight measured 527 added production LOC, above the ordinary
300 limit and above what can proceed without a published investigation.

### Goal
Publish a public-safe investigation decision that preserves the accepted
review-fingerprint optimization scope, identifies a bounded simplification and
authorizes only the exact successor at no more than 500 added production LOC.

### Scope
- Reproduce the retained preflight breakdown from public-safe commit evidence:
  489 added lines in `scripts/changerail_review_verdict.py`, 36 in
  `scripts/changerail_review_preflight.py` and 2 in
  `scripts/run-release-baseline.py`, for 527 production-counted lines.
- Record removable over-expansion: duplicate timing helper classes, extra
  dataclass layers for path/cache state and repeated synthetic repository setup
  across benchmark/cache smoke scripts.
- Preserve exact reviewed-tree parity, untracked content hashing, ignored
  runtime exclusion, cache invalidation, diagnostics and focused benchmark
  coverage.
- Bind the replacement boundary to
  `openspec/board/1.backlog/deliver-bounded-review-fingerprint-optimization.md`
  and its existing three OpenSpec implementation changes.
- Keep the local checkpoint as read-only investigation evidence only.

### Acceptance
- The investigation card records why the retained payload measured 527 added
  production LOC and names the production-counted files.
- The decision identifies concrete simplification work that does not weaken
  exact fingerprint freshness or focused smoke coverage.
- The successor boundary is no larger than 500 added production LOC and does not
  raise the global limit or permit a new authority/wire protocol.
- Verification floor and exact successor card are stated for the follow-up
  authorization and delivery cards.
- The retained local checkpoint is not published or treated as review evidence.

### Depends On
- none

### Related
- `openspec/changes/decide-bounded-review-fingerprint-payload/`

## Log
- 2026-08-19T07:17:52Z created after deterministic preflight stopped the
  retained 527-production-LOC implementation before independent review.
- 2026-08-19T07:42:49Z `$chrl-ff` created
  `decide-bounded-review-fingerprint-payload`, recorded the bounded
  investigation decision plan and moved the card to `2.todo`.
