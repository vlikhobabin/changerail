## Why

The retained review-fingerprint implementation stopped before independent
review because deterministic preflight measured 527 added production LOC, above
the ordinary 300 limit and above the maximum that can be justified without a
published investigation. ChangeRail needs a public-safe decision that explains
the oversize, preserves exact fingerprint semantics and bounds the replacement
payload to the existing 500 production-LOC ceiling.

## What Changes

- Record the retained public-safe diff summary as read-only investigation evidence,
  not as review evidence or a publishable payload.
- Reproduce the production-LOC breakdown from public-safe evidence:
  `scripts/changerail_review_verdict.py` added 489 lines,
  `scripts/changerail_review_preflight.py` added 36 lines and
  `scripts/run-release-baseline.py` added 2 lines, for 527 production-counted
  added lines.
- Publish a bounded simplification decision for the exact successor
  `deliver-bounded-review-fingerprint-optimization`.
- Preserve the three existing implementation scopes:
  `measure-review-fingerprint-costs`,
  `optimize-review-fingerprint-tree-build` and
  `share-review-fingerprint-preflight-cache`.
- Require the replacement implementation to stay at or below 500 added
  production LOC without raising the global limit, changing fingerprint
  authority or introducing a new wire protocol.
- Point the authorization publication card at the exact investigation result and
  successor card.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: deterministic review preflight accepts a bounded
  published investigation authorization only when it is tied to one exact
  investigation, authorization source and successor card, and the production LOC
  ceiling does not exceed 500.

## Impact

- Affected public files: this board card, its successor authorization/delivery
  cards and `openspec/changes/decide-bounded-review-fingerprint-payload/`.
- No production code is implemented by this change.
- Consumer impact is procedural: review-gated replacement payloads may rely on a
  published bounded authorization only after exact reciprocal links pass.
