## Context

OPSX already documents `ff -> do -> review -> pub`, but the durable docs,
skills and manifest contract leave two operational gaps: a card can be treated
as done before review/publish, and a board-card move can under-claim publish
scope because only final paths are recorded. The card requires keeping archived
OpenSpec changes in the reviewed payload while deferring board finalization.

## Goals / Non-Goals

**Goals:**
- Make `3.inprogress` the post-`do`, pre-publish state for review-gated cards.
- Make `4.done` a deterministic post-publish finalization state.
- Preserve archive-before-review as the freshness invariant.
- Extend delivery manifests with structured file operations for add, modify,
  delete and rename without breaking existing v1 manifests.
- Update skills/docs so agents use the same lifecycle language.

**Non-Goals:**
- Do not change the base phase order.
- Do not require publish to make content edits after a `go` verdict.
- Do not commit runtime verdicts, manifests or evidence.

## Decisions

- Keep the schema id `opsx.delivery-manifest.v1` and add optional operation
  fields to `committable_paths`.
  - Rationale: existing consumers can keep reading `path`, `kind` and `phase`.
  - Alternative considered: introduce v2 immediately. That adds migration cost
    without a breaking need.
- Represent deletes and renames with operation metadata.
  - Rationale: publish can stage both sides of a board-card move using one
    manifest entry or paired entries.
  - Alternative considered: infer deletes from `git status`. Inference remains
    useful, but the manifest should claim the intended operation.
- Leave the card in `3.inprogress` after `opsx-do`.
  - Rationale: archived changes are complete, but the story is not published.
  - Alternative considered: move to `4.done` after archive. That weakens the
    review/publish gate.

## Risks / Trade-offs

- Existing manifest producers may omit `operation` -> publish must treat a
  missing operation as legacy/unknown and re-check `git status`.
- Deterministic card metadata after publish can change the reviewed fingerprint
  -> publish must limit post-`go` edits to documented card finalization and
  fail closed for content edits.
