## Context

The published `rescue-private-release-loop-acceleration-publication-boundary`
decision already declares the exact H authorization object. This change makes
that declaration consumable by deterministic preflight through one separate,
clean, tracked authorization card. The future H successor does not exist yet.

## Goals / Non-Goals

**Goals:**

- Publish exactly one parser-recognized six-field object on the authorization
  card, without auxiliary authorization data or parser behavior.
- Preserve exact decision -> authorization -> future-successor relations and
  the exact future two-field authorization reference.
- Keep the H budget independent: ceiling `350` permits the exception gate,
  while implementation remains `<=349` production LOC against its future
  published authorization HEAD.
- Limit H ownership to structural history traversal, Git-compatible parsing,
  memoization, non-mutation and focused/CI history ownership proof.

**Non-Goals:**

- Create the future successor card or any production/test/runtime code.
- Change schemas, parsers, helpers, workflows, CLI behavior, authority or wire
  protocol.
- Run history, full-release, live, successor, review, commit or push work.

## Decisions

### 1. Board card is the sole authorization source

The board card uses exactly one `Investigation authorization` inline object
with the six fields prescribed by the published decision. A separate JSON
file, additional fields or new validation behavior would widen the payload and
is excluded.

### 2. The successor is bound but not created

The source card depends on the published decision and blocks only
`deliver-clean-structural-history-scan-v3`. The decision already blocks this
authorization and future successor. The delta requirement defines that the
later card must depend on the decision and contain only the exact two-field
inline authorization reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-clean-structural-history-scan-v3.md","authorization_id":"authorize-clean-structural-history-scan-v3"}
```

This preserves reciprocal lineage without manufacturing a successor before
publication.

### 3. Scope remains H-only and docs-only

The authorization records only the H boundary already chosen by the decision.
The low-level Git traversal, parsing, memoization, mutation guard and focused
proof remain future implementation scope. The tracked payload contains only a
board card, its OpenSpec artifacts and the synchronized release-CI contract.

## Risks / Trade-offs

- **[Risk] Bound id/path drift makes the exception ambiguous.** -> Exact
  canonical paths, ids and two-field future reference fail closed.
- **[Risk] Ceiling `350` is mistaken for implementation budget.** -> Every
  artifact repeats the independent `<=349` limit against the future published
  authorization HEAD.
- **[Risk] Authorization is consumed before publication.** -> The successor
  stays absent until this source is published in `4.done`.

## Migration Plan

1. Create the docs-only authorization artifacts, then move the card to
   `3.inprogress` when they are apply-ready.
2. Sync the release-CI delta and archive the completed authorization change.
3. Hand the source to independent ordinary/high review; only scoped publication
   can make the later successor reference valid.

Rollback before publication removes only this unpublished docs payload. A
published binding must be superseded by a new tracked decision rather than
altered in place.

## Open Questions

None. The published decision fixes the object, ownership, ceiling and protocol
allowance.
