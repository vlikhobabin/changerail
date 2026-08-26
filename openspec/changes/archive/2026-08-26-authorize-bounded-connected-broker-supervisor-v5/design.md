## Context

The published decision `a94bd4e2907a1c216e7456cf1a9da643d283b796`
defines exact v5 as the sole future broker-supervisor path and requires two
mutation-sensitive public-entrypoint proofs. This authorization is the required
docs-only gate between that decision and any executable successor.

## Goals / Non-Goals

**Goals:**

- Freeze one exact six-field authorization and exact two-field successor ref.
- Bind v5 to the authorization-publishing HEAD and at most 499 production LOC.
- Preserve R8/R9 public-`supervise`, mutation integrity, retained evidence and
  `0/0/0` review budget.
- Keep successor absent and all executable surfaces dormant.

**Non-Goals:**

- Do not create or implement v5.
- Do not reuse v4 code, tests, cards or runtime evidence.
- Do not add dependencies, schemas, CI, baseline, receipts or activation.
- Do not run history, full release baseline or live matrix evidence.

## Decisions

### 1. One exact authorization object

This authorization alone contains:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The future successor uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

### 2. Authorization binds proof, not only size

V5 must start from the HEAD that publishes this card, add at most 499 production
LOC and add no dependency. Its canonical R8/R9 scenarios invoke public
`supervise`; disposable mutations remove outer cleanup wiring and replace
pidfd signaling with PID-only signaling, and each identical scenario must turn
red. Missing, ambiguous, no-op or pre-signal-only proof blocks publication.

### 3. One attempt, one review

V5 receives one implementation attempt and one fresh Sol/high review with
repair/retry/rescue budget `0/0/0`. It may use published requirements and
generic findings but cannot copy terminal v4 code or runtime evidence.

## Verification

- Exact object/reference/lineage and source commit.
- Successor absence and docs-only scope with zero executable LOC.
- Strict target/all OpenSpec, exact archive/main sync, JSON/TOML,
  classification, current public scan, whitespace and manifest scope.

## Risks / Trade-offs

The zero-repair budget is intentionally strict. A failed v5 proof cannot start
another local staircase under this authorization.

## Migration Plan

1. Validate, archive, independently review and publish this authorization.
2. Only after publication create exact v5 from this authorization HEAD.

## Open Questions

None.
