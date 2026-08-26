## Context

`decide-bounded-unpublished-terminal-micro-fix-boundary` is the published
investigation decision for exactly one S3 reconstruction. It deliberately does
not create an authorization source or successor. The release-CI contract must
now expose the exact publishable source while retaining the decision's narrow
eligibility and proof boundary.

## Goals / Non-Goals

**Goals:**

- Publish exactly one six-field authorization object bound to the decision and
  only `deliver-psutil-backed-release-child-supervisor-v3`.
- Preserve reciprocal blocks/dependencies, the exact two-field future reference
  and the successor's `<=499` production-LOC limit from the HEAD that publishes
  this authorization.
- Preserve fail-closed eligibility, clean reconstruction, terminal-evidence
  non-reuse, fresh connected R1-R7 proof, R7 EOF semantics, one attempt,
  `0/0/0` budget and dormant downstream boundary.
- Keep the authorization docs-only with production, test and runtime LOC `0`.

**Non-Goals:**

- Do not create, implement, review, publish or otherwise activate the S3
  successor.
- Do not reuse terminal verdicts, history, logs, receipts, manifests or
  evidence from the frozen candidate.
- Do not change production paths, dependencies, schemas, ownership, release
  baseline, CI, review/publish gate, receipt schema or production entrypoint.
- Do not run or accept history, full release baseline, live execution, review,
  commit or push evidence.

## Decisions

### 1. One exact object is the sole new authority source

The authorization card contains exactly one object, with precisely these six
fields and values:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends on the published decision and blocks only its exact successor. The
future successor depends on both sources and contains only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The `500` source ceiling does not enlarge implementation scope: the future
successor remains at most 499 added production LOC relative to the exact HEAD
that publishes this authorization.

### 2. Reconstruction is clean and re-proves the entire connected contract

The sole successor is admitted only for an unpublished candidate with valid
exact published authorization, independently closed prior findings and exactly
one new isolated latest blocker. It begins from the authorization-publishing
HEAD and remains in unchanged authorized paths, scope, dependencies, schema and
ownership.

Executable code and tests can be mechanically reconstructed from the frozen
failed candidate only as source material. No verdict, history, log, receipt,
manifest or evidence transfers. Every connected R1-R7 proof runs again from
the clean authorization base.

### 3. EOF is not completion and the future remains dormant

R7 treats pipe EOF as stream state only. A live leader after EOF remains
incomplete; completion requires a terminal leader observation or
`execution_timeout`, followed by cleanup under the existing bounded contract.

The successor receives one implementation attempt and one fresh Sol/high
review, with repair/retry/rescue exactly `0/0/0`. It has no credential,
mutation, live-admission or final authority. S3 and all downstream refresh
work remain dormant until the successor is published.

## Connected Proof Matrix

| Contract | Fresh focused proof | Fail-closed result |
| --- | --- | --- |
| Lineage | Parse the exact ordered six-field object, decision dependency, successor-only block and future two-field reference. | Any identity, field, ordering or relation mismatch blocks S3. |
| Eligibility and base | Assert unpublished candidate, exact valid authorization, independently closed prior findings, one isolated latest blocker, clean authorization HEAD, unchanged scope and `<=499` LOC. | Any stale, widened or multi-blocker candidate is rejected. |
| Reconstruction and R1-R7 | Assert source-material-only reconstruction and fresh proof for every connected R1-R7 obligation. | Reused terminal material or missing fresh proof blocks delivery. |
| R7 | Cover EOF with live leader, terminal leader observation, execution timeout and cleanup order. | EOF alone cannot report completion or successful cleanup. |
| Dormancy | Assert no authority or release wiring activation and blocked downstream refresh until publication. | Premature activation or refresh blocks delivery. |

## Risks / Trade-offs

- **[Risk] An authorization object is broadened through extra fields or another
  successor.** -> The contract requires one exact six-field object and an exact
  successor-only block.
- **[Risk] Frozen terminal material is mistaken for evidence.** -> The contract
  permits mechanical source reconstruction only and requires a fresh R1-R7
  connected proof set.
- **[Risk] EOF masks a still-live leader.** -> Completion has only the terminal
  leader or execution-timeout paths before cleanup.

## Migration Plan

1. Validate and archive this same-slug docs-only authorization while leaving its
   card in `3.inprogress` for a fresh ordinary/high review.
2. Publish it. Its exact publishing HEAD becomes the S3 implementation LOC
   comparison base.
3. Only then may a separate exact successor card be created and delivered;
   downstream refresh remains blocked until that successor is published.

## Open Questions

None. The published decision fixes the successor identity and bounded contract.
