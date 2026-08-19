# Investigate runner retained resume payload boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Deterministic review preflight for
  `openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md`.
- `.runtime/changerail/review-preflights/support-runner-resume-after-investigation-required.json`

## Summary
The retained-runner resume implementation is verified and archived, but the
review gate stopped before independent review because the payload adds 562
production-counted lines in `bin/changerail-delivery-runner` and introduces a
new runner/status protocol boundary without published investigation
authorization.

Publish a public-safe investigation decision that determines how to simplify or
split the retained-resume payload below the bounded authorization ceiling while
preserving the safety properties already verified by the smoke suite.

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
- `support-runner-resume-after-investigation-required`

## Acceptance
- Reproduce the deterministic preflight stop from public-safe evidence:
  562 added production-counted LOC in `bin/changerail-delivery-runner`, new
  wire/protocol boundary, and no published authorization.
- Identify the smallest safe simplification or split that brings the exact
  successor implementation under the maximum 500 production-LOC authorization
  ceiling without weakening fail-closed retained-payload checks.
- State whether the successor remains
  `support-runner-resume-after-investigation-required` or must be replaced by a
  linked successor card, and bind the exact successor id/path.
- State the required verification floor for the successor: retained identity
  schema acceptance/rejection, single-card retained resume success, wrong
  card/workspace, stale authorization, relation mismatch, over-ceiling,
  fingerprint drift, queue original resume, queue replacement recovery and
  duplicate recovery rejection.
- Do not publish the retained unreviewed implementation, treat a checkpoint
  commit as review evidence or raise the global complexity limit.

## Non-Goals
- Implementing the retained-resume production changes.
- Publishing an authorization object without a bounded successor decision.
- Raising `MAX_AUTHORIZED_PRODUCTION_LOC_LIMIT`.

## Investigation Decision
The retained runner-resume implementation is investigation input only. It is
not published, is not independent review evidence and does not authorize itself.

The public-safe preflight breakdown is:

- `bin/changerail-delivery-runner`: 562 added production-counted lines.
- Source classification: built-in production source, line-count strategy.
- Complexity reasons: added production LOC exceeds 300, and a new runner/status
  protocol boundary requires published investigation authorization.

The smallest safe boundary is simplification inside the existing successor
card, not a replacement card. The exact successor remains
`support-runner-resume-after-investigation-required`; its current queue path is
`openspec/board/2.todo/support-runner-resume-after-investigation-required.md`,
and its authorization-time target path is
`openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md`.

The successor may use a later published investigation authorization only if its
implementation is simplified to at most 500 added production-counted LOC. That
authorization must be a separate clean tracked `4.done` source, must bind this
published investigation and the exact successor, and must set
`allow_new_authority_or_wire_protocol` to true because the retained-resume
contract changes the runner/status protocol boundary.

The successor should reduce at least 63 production-counted lines without
weakening fail-closed behavior by sharing retained-payload validation between
single-card and queue resume paths, reusing existing manifest/review-preflight
authorization helpers, avoiding duplicate status construction and keeping plan
recovery metadata compact. If the simplified implementation cannot stay at or
below 500 production-counted LOC, this decision does not authorize it and a
replacement investigation or split decision is required.

The successor verification floor remains:

- retained identity schema acceptance and rejection;
- single-card retained resume success;
- wrong card and wrong workspace rejection;
- stale authorization rejection;
- relation mismatch rejection;
- over-ceiling rejection;
- fingerprint drift rejection;
- queue original resume success;
- queue replacement recovery success;
- duplicate recovery rejection.

## Change Set
- `decide-runner-retained-resume-payload-boundary`

## Verify
- GREEN: `./bin/openspec validate "decide-runner-retained-resume-payload-boundary" --strict`
- GREEN: `./bin/openspec validate "changerail-contracts" --strict`
- GREEN: `./bin/openspec validate --all --strict` -> 27/27 passed.
- GREEN: `python3 scripts/public-surface-scan.py` -> 1080 files scanned, 0
  findings.
- GREEN: `git diff --check`
- GREEN: untracked-file trailing-whitespace scan over `git ls-files --others
  --exclude-standard`
- GREEN: `bin/changerail-delivery-manifest scope-check
  .runtime/changerail/delivery-manifests/investigate-runner-retained-resume-payload-boundary.json
  --workspace . --target working-tree --json`

## Archive
- `openspec/changes/archive/2026-08-19-decide-runner-retained-resume-payload-boundary/`

## Related
- `openspec/changes/archive/2026-08-19-decide-runner-retained-resume-payload-boundary/`
- `openspec/board/2.todo/support-runner-resume-after-investigation-required.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-contract-schemas.py`

## Result
published; investigation decision complete

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-runner-retained-resume-payload-boundary`

### Why
The blocked successor cannot pass review preflight as-is: its production
contribution is above both the normal 300 LOC limit and the repo's 500 LOC
bounded authorization ceiling, and the new runner/status protocol requires a
published authorization source.

### Goal
Publish a decision-only investigation artifact that chooses a bounded
simplification or split, names the exact successor, and preserves the
verification floor needed for fail-closed retained-resume recovery.

### Scope
- Summarize the retained preflight stop and source-kind breakdown.
- Identify removable implementation expansion or a split boundary.
- Bind the exact successor id/path for a later authorization source.
- Preserve the verification floor from the blocked card.
- Do not modify production runner behavior in this investigation card.

### Acceptance
- The decision explains why the current retained payload cannot be reviewed or
  authorized as-is.
- The decision names a successor boundary no larger than 500 added
  production-counted LOC.
- The decision states whether the current card can continue after
  simplification or whether a replacement card is required.
- The verification floor remains strong enough to catch wrong card, wrong
  workspace, stale authorization, relation mismatch, over-ceiling, fingerprint
  drift and duplicate queue recovery defects.

### Depends On
- none

### Related
- `openspec/changes/decide-runner-retained-resume-payload-boundary/`

## Log
- 2026-08-19T16:55:00Z created after `$changerail-deliver` stopped
  `support-runner-resume-after-investigation-required` at deterministic review
  preflight with `investigation-required`.
- 2026-08-19T17:11:09Z `$changerail-ff` created
  `decide-runner-retained-resume-payload-boundary`, completed apply-ready
  proposal/design/spec/tasks artifacts and validated the change set.
- 2026-08-19T17:13:35Z `$changerail-do` recorded the bounded investigation
  decision, synced `changerail-contracts`, archived
  `decide-runner-retained-resume-payload-boundary` and prepared review handoff.
- 2026-08-19T17:34:09Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
