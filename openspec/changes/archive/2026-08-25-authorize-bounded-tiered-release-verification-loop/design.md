## Context

Published investigation `investigate-tiered-release-verification-loop-boundary`
at `7e30b08` defines one first executable successor:
`implement-tiered-release-verification-loop`. It fixes the affected/full-release
authority boundary, frozen semantic ownership, fail-fast toolchain admission and
bounded Windows matrix behavior, but it is a decision rather than a generic
authorization source accepted by deterministic preflight.

This change publishes only that missing authorization source. The investigation
already blocks both the authorization and future successor. The successor is
intentionally absent until this source is independently reviewed, published in
`4.done` and remote-reachable.

## Goals / Non-Goals

**Goals:**

- Publish exactly one parser-recognized six-field authorization object binding
  the exact published investigation to the exact future successor.
- Preserve reciprocal investigation/authorization/future-successor relations
  and the exact two-field source reference required from the future successor.
- Separate authorization ceiling `500` from the implementation acceptance of
  `<=499` executable LOC against exact baseline `45a2de9`.
- Keep planning and delivery docs-only with zero production, test and runtime
  additions.

**Non-Goals:**

- Do not create the future successor card, code, tests or runtime state.
- Do not implement affected/full-release orchestration, toolchain admission,
  semantic registry ownership or Windows concurrency.
- Do not change the generic authorization parser, schema or protocol.
- Do not run history scan, benchmark or full release baseline.

## Decisions

### 1. The board card is the sole authorization source

The source card retains exactly one parser-owned `Investigation authorization`
field with this exact JSON object:

```json
{"investigation_card":"openspec/board/4.done/investigate-tiered-release-verification-loop-boundary.md","investigation_id":"investigate-tiered-release-verification-loop-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-verification-loop.md","successor_id":"implement-tiered-release-verification-loop","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

No second object, external authorization document or parser/schema change is
introduced. This uses the existing generic authorization contract.

### 2. Reciprocal lineage is fixed before successor creation

The published investigation blocks the authorization and the future successor.
The authorization depends on that investigation and blocks that successor. A
later separate flow may create the successor only after publication; its
`Published investigation authorization` field must contain only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-verification-loop.md","authorization_id":"authorize-bounded-tiered-release-verification-loop"}
```

The future successor also depends on the exact investigation. A changed id,
path, relation or extra reference field fails closed.

### 3. Protocol allowance is narrow and does not raise the LOC budget

`allow_new_authority_or_wire_protocol: true` authorizes only the decision-defined
affected non-authority/full-release authority boundary. It does not authorize
credential, mutation or live authority and is not reusable by another
successor. `production_loc_ceiling: 500` is the authorization gate ceiling;
normative implementation acceptance remains independently `<=499` executable
LOC relative to
`45a2de98924c61bb9e944767013ea09918bba4b0`.

### 4. Verification remains cheap and current-only

Delivery validates strict OpenSpec targets, exact JSON and reciprocal links,
JSON/TOML, current-only public surface, classification, whitespace, manifest
scope and preflight. It does not run history scan, benchmark or full baseline;
those would add cost without exercising this zero-executable-LOC payload.

## Risks / Trade-offs

- **[Risk] Future path or identity drift invalidates authorization.** Exact
  paths and ids are intentionally fail-closed; a different successor needs a
  new tracked lineage.
- **[Risk] Ceiling `500` is read as permission for 500 executable lines.** The
  card, delta spec and design independently retain the `<=499` implementation
  limit against the exact baseline.
- **[Risk] Boolean `true` is treated as a broad waiver.** The permission is
  limited to the authority boundary already defined by the investigation and
  explicitly excludes credential, mutation and live authority.

## Migration Plan

1. Delivery preserves the exact source object, synchronizes the release-CI
   delta and archives this sole change without executable additions.
2. Fresh ordinary review verifies exact binding, relations and zero-LOC scope;
   publish moves the authorization source to `4.done`.
3. Only after remote-reachable publication may a separate flow create the
   future successor with the exact two-field reference.

Before publication rollback removes only unpublished documentation. After
publication any binding change requires a new tracked authorization lineage.

## Open Questions

None. Identities, paths, ceiling, protocol allowance, baseline and successor
scope are fixed by the published investigation.
