## Context

Published split rescue `rescue-tiered-release-verification-split-boundary` at
`25f756e` replaced an unpublished broad implementation with two disjoint future
lineages. Scope A owns release authority core, while Scope B owns Windows
process scheduling and deduplication. The rescue is a decision source, not the
generic clean tracked `4.done` authorization source required by deterministic
preflight.

This change publishes only the Scope A authorization source. The rescue already
blocks both this authorization and the exact future successor
`implement-tiered-release-authority-core`. That successor remains absent until
this source is independently reviewed, published and remote-reachable.

## Goals / Non-Goals

**Goals:**

- Publish exactly one parser-recognized six-field object binding the exact
  published rescue to the exact future Scope A successor.
- Preserve exact reciprocal rescue/authorization/future-successor relations
  and the exact two-field source reference required from that successor.
- Bound the successor to Scope A alone and preserve `<=499` production LOC
  against exact comparison base
  `25f756ebf2aa90c58e01eab3703b291dbdde257f`.
- Keep planning and delivery docs-only with zero production, test and runtime
  additions.

**Non-Goals:**

- Do not create the future successor card, implementation, tests or runtime
  state.
- Do not implement or authorize Scope B Windows scheduling/deduplication,
  verify-project internals, history scanning or review/delivery smoke internals.
- Do not change generic authorization parsing/schema behavior or grant
  credential, mutation or live authority.
- Do not run a history scan, benchmark or full release baseline.

## Decisions

### 1. The board card is the sole authorization source

The source card retains one parser-owned `Investigation authorization` field
with exactly this six-field JSON object:

```json
{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

No second object, external authorization file or parser/schema change is
introduced. This uses the existing generic authorization contract.

### 2. Reciprocal lineage is fixed before successor creation

The published rescue blocks this authorization and the exact future successor.
This authorization depends on the rescue and blocks the same successor. A later
separate flow may create the successor only after publication; it must depend
on both the rescue and this authorization and its `Published investigation
authorization` field must contain only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-authority-core.md","authorization_id":"authorize-bounded-tiered-release-authority-core"}
```

A changed id, path, relation or extra reference field fails closed.

### 3. The true protocol allowance is exclusive to Scope A

`allow_new_authority_or_wire_protocol: true` authorizes only aggregate
toolchain admission; the exact 35-ID registry and digest; affected/full
selection and authority; atomic marker, lock and fsync; generic capture
identity and fingerprint equality; receipt, manifest, schema, preflight and
publish gates; canonical CI full-runner invocation; and the parsed YAML and
Python-AST ownership oracles for those surfaces.

It does not grant credential, mutation or live authority. Scope B case schemas,
jobs, isolation/order, process-group lifecycle, deduplication and owner
transition remain outside this source, as do verify-project, scanner and smoke
internals.

### 4. Authorization ceiling does not raise the implementation limit

`production_loc_ceiling: 500` is the generic authorization gate ceiling. The
future successor independently remains limited to `<=499` added production LOC
against exact published split-rescue base
`25f756ebf2aa90c58e01eab3703b291dbdde257f`; a 500th line fails closed.

### 5. Verification remains cheap and current-only

Delivery validates strict OpenSpec targets, exact JSON and reciprocal links,
JSON/TOML, current-only public surface, classification, whitespace, manifest
scope and normalized preflight. It does not run history, benchmarks or the full
baseline because this payload adds no executable surface.

## Risks / Trade-offs

- **[Risk] Future identity or path drift invalidates the source.** Exact paths,
  ids and relations intentionally fail closed; a different successor requires
  a new tracked lineage.
- **[Risk] Protocol allowance is treated as a broad waiver.** The exclusive
  Scope A list and explicit Scope B/later-successor exclusions constrain it.
- **[Risk] Ceiling `500` is read as a 500-line budget.** The independent
  `<=499` acceptance and exact comparison base are normative in every artifact.

## Migration Plan

1. Delivery preserves the exact source object, synchronizes the release-CI
   delta and archives this sole docs-only change.
2. Fresh ordinary review verifies exact binding, disjoint ownership and zero
   executable LOC; publish moves the authorization source to `4.done`.
3. Only after remote-reachable publication may a separate flow create the
   future successor with the exact two-field reference.

Before publication rollback removes only unpublished documentation. After
publication any binding or scope change requires a new tracked authorization
lineage.

## Open Questions

None. Identities, paths, ownership, ceiling, allowance, comparison base and
successor order are fixed by the published split rescue.
