## Why

ChangeRail launches a fresh LLM reviewer before one deterministic gate has
reconciled the delivery manifest, board state and locally available strict
checks. Consequently manifest-only corrections and planning/live evidence
reviews can consume the implementation rescue budget, while repeated fixes may
grow into a larger authority protocol than the original feature.

## What Changes

- Extend the existing review helper with a deterministic preflight that validates
  and safely normalizes manifest metadata/operation mismatches, reconciles scope
  and runs available strict OpenSpec, diff and public checks.
- Add a schema-valid preflight result carrying the risk route, reasoning effort,
  machine checks and a typed complexity stop.
- Define deterministic, ordinary and critical review tiers and separate phase
  counters.
- Require one payload review, allow only one declared milestone clean-HEAD audit,
  and permit hash-bound verification reuse only until live/final publication.
- Replace the broad five-rescue default with two scoped implementation rescues
  and an early investigation/simplification guard.
- Update lifecycle skills, shared methodology, templates and consumer guidance.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: add deterministic review-preflight results and optional
  phase counters to review history.
- `changerail-agent-methodology`: define risk-tier routing, one-review/milestone
  rules, evidence reuse and the rescue complexity guard.
- `changerail-skill-surface`: require preflight before independent LLM review and
  keep deterministic failures outside implementation review budget.
- `changerail-project-templates`: expose review risk and complexity declarations
  on new board cards.
- `changerail-project-verification`: require reachability for the new public
  preflight-result schema.
- `changerail-release-ci`: include the focused preflight smoke in the release
  verification inventory.

## Impact

- Public Python helper behavior and one new JSON schema.
- Canonical review/deliver/do/publish skill wording.
- Shared methodology, contract docs, workflow guide and consumer runbook.
- Root and generated consumer card templates.
- Consumer verification and release baseline schema/smoke inventory.
- No model launcher, live system, credential or external service changes.
