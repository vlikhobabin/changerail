## Context

Published decision
`rescue-private-release-loop-acceleration-publication-boundary` defines
isolation owner I, but the future implementation needs a clean published
authorization source that deterministic preflight can consume. The source card
is the tracked authority; its same-slug OpenSpec change and release-CI delta
make that contract reviewable and canonical.

## Goals / Non-Goals

**Goals:**

- Publish exactly one parser-recognized six-field authorization object for the
  exact decision and one future I successor.
- Preserve reciprocal investigation, authorization and future-successor
  relations plus the successor's exact two-field source reference.
- Keep the authorization payload docs-only and bound the future implementation
  to `<=499` executable LOC against its exact published authorization HEAD.

**Non-Goals:**

- Do not create the future successor card, code, tests or runtime state.
- Do not implement I's executor, change generic authorization parsing or alter
  schemas, helpers, workflows, CLI surfaces or release behavior.
- Do not add authority or wire protocol in this payload, or authorize
  credential, mutation, live or terminal authority.
- Do not run a history scan, full release baseline or live execution.

## Decisions

### 1. The `4.done` board card is the sole authorization source

The source card contains exactly one `Investigation authorization` object:

```json
{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-isolated-release-case-executor-v2.md","successor_id":"implement-bounded-isolated-release-case-executor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The established generic object remains unchanged: no second object or
authorization protocol/schema is introduced. Keeping the source on the card
makes the deterministic preflight source of truth visible and public.

### 2. Reciprocal lineage is fixed before successor creation

The published decision already blocks authorization and successor. This card
depends on that decision and blocks the exact future successor. A later flow
may create the successor only after this card is published in `4.done`; it must
depend on the decision and use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-isolated-release-case-executor-v2.md","authorization_id":"authorize-bounded-isolated-release-case-executor-v2"}
```

Exact path/id matching and no extra reference fields fail closed instead of
allowing an authorization to migrate to another implementation.

### 3. `true` belongs to the future I scope, not this payload

The authorization's protocol/authority allowance is required by the published
decision for the future I implementation. This authorization card itself adds
no authority or wire protocol and has zero executable LOC. The future I scope
is only isolated case schemas, jobs/order, hard output/timeout bounds, process
containment, cleanup and parsed-CI ownership proof. It excludes registry
selection, history parsing, receipts and terminal authority.

The ceiling `500` is an authorization gate, not permission for a 500th
executable line. Future acceptance is independently `<=499` executable LOC
relative to the exact published authorization HEAD that its own creation flow
records.

### 4. Verification is current-only and docs-only

Delivery runs strict OpenSpec, exact JSON/lineage checks, JSON/TOML parsing,
current public-surface scan, classification, whitespace, manifest scope and
normalized preflight. No reachable-history scan, full baseline, live run,
successor execution, review, commit or push is part of this change.

## Risks / Trade-offs

- **[Risk] Future path or identity drift invalidates the source.** Exact
  reciprocal ids, paths and two-field reference fail closed.
- **[Risk] Ceiling `500` appears to authorize 500 executable lines.** Card,
  delta and tasks retain the separate `<=499` future limit.
- **[Risk] Boolean `true` looks like a broad waiver.** It is constrained to the
  decision-defined future I scope; this docs-only payload adds none.

## Migration Plan

1. Keep only the source card and same-slug artifacts in planning.
2. Sync the release-CI delta, archive the verified docs-only change and leave
   the card in `3.inprogress` for independent ordinary review.
3. After scoped publication moves the card to `4.done`, a separate flow may
   create the future successor with its exact two-field reference.

Before publication, rollback removes only unpublished documentation. Any
published binding change requires a new authorization lineage.

## Open Questions

None. The decision fixes identities, ownership, ceiling and allowance.
