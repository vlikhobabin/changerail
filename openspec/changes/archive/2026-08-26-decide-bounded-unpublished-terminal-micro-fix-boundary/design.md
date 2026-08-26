## Context

Published psutil S2 lineage supplied one authorization for an exact prior
successor. Its unpublished candidate exhausted the allowed delivery cycle.
The candidate's first review cycle closed R1-R6 through one repair; the second
cycle exposed one new isolated R7 blocker, where pipe EOF was treated as
completion while the leader was still live. That payload was not published and
has no public authority.

This decision creates no executable payload. It permits only a later, clean
authorization followed by one v3 micro-fix, and prevents that successor from
reusing terminal verdicts, histories, logs, receipts or manifests.

## Goals / Non-Goals

**Goals:**

- Preserve the exact future authorization and v3 successor identities and
  reciprocal decision/authorization/successor relations.
- Bound the successor to the existing authorized production paths, one
  implementation attempt, `<=499` added production LOC against its own
  authorization HEAD, one fresh Sol/high review and no repair/retry/rescue.
- Permit mechanical reconstruction of executable code and tests from the
  frozen candidate only as source material, while requiring a fresh connected
  R1-R7 proof set.
- Fix the semantic R7 boundary: pipe EOF is stream state; observed leader
  terminal state or execution timeout establishes completion, then cleanup.

**Non-Goals:**

- Do not resume, publish, authorize or treat the terminal candidate as a
  source of authority, proof or receipt.
- Do not widen production paths, scope, dependencies, schema or ownership.
- Do not grant credentials, mutation, live admission or final authority.
- Do not create a future authorization or successor card, code, dependency
  change, CI/baseline activation, review, commit or push.
- Do not run or accept history, full baseline or live execution evidence.

## Decisions

### 1. A new authorization is required before the sole v3 successor exists

The decision card blocks both future cards. Only the future
`authorize-bounded-psutil-supervisor-micro-fix-v3` card may contain the exact
six-field object:

```json
{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

That authorization depends on this decision and blocks only the exact
successor. The v3 card depends on both sources and carries only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}
```

The ceiling authorizes investigation-scale change, not the successor's LOC:
the v3 implementation remains at most 499 added production LOC versus the
HEAD that publishes its own authorization.

### 2. Reconstructed source material is not reusable terminal evidence

The future v3 candidate starts from the clean HEAD that publishes its new
authorization. It may mechanically reconstruct executable code and tests from
the frozen failed candidate only as source material. It cannot reuse any
verdict, review history, log, receipt, manifest or terminal evidence, and must
rerun every connected R1-R7 proof.

Admission is fail-closed: the candidate must be unpublished, its exact
published authorization must be valid, all prior findings must be independently
closed, and the latest cycle must contain exactly one new isolated blocker.
It cannot expand authorized production paths, scope, dependencies, schema or
ownership, and obtains no credential, mutation, live or final authority.

### 3. R7 separates pipe state from process completion

Pipe EOF is only a stream-state observation. It cannot declare the supervised
execution complete while the leader remains live. Completion requires an
observed terminal leader state or exhaustion of `execution_timeout`; only then
does cleanup run. The v3 proof must cover the live-leader EOF negative case,
leader terminal observation, timeout path and required cleanup order as part
of its new R1-R7 connected proof.

### 4. Dormancy and one-shot review preserve downstream boundaries

S3 remains dormant and downstream refresh remains blocked until S3 is
published. The v3 successor gets one implementation attempt and one fresh
Sol/high review; repair/retry/rescue is exactly `0/0/0`. Any nonconforming
candidate requires a new decision rather than a continuation.

## Connected Proof Matrix

| Contract | Fresh focused proof | Fail-closed result |
| --- | --- | --- |
| Lineage | Parse exact six-field and two-field objects plus reciprocal blocks/dependencies. | Any identity, field count or relation mismatch blocks v3. |
| Admission | Assert unpublished candidate, valid exact authorization, independently closed prior findings, one new isolated latest blocker, unchanged paths/scope and LOC limit. | Any stale, widened or multi-blocker continuation is rejected. |
| R1-R7 | Rerun every connected proof from a clean authorization HEAD without importing terminal proof artifacts. | Missing fresh proof or reused verdict/history/log/receipt/manifest blocks delivery. |
| R7 completion | Exercise EOF with live leader, observed terminal leader and timeout-before-cleanup paths. | EOF alone cannot complete execution; absent terminal/timeout observation blocks cleanup success. |
| Dormancy | Assert absent S3 activation and blocked downstream refresh before publication. | Premature activation or refresh blocks delivery. |

## Risks / Trade-offs

- **[Risk] Terminal candidate material silently becomes authority.** -> The
  successor may use only mechanically reconstructed source material and must
  recreate every proof from a clean authorization HEAD.
- **[Risk] EOF masks a live leader.** -> Completion is explicitly tied to a
  terminal leader observation or execution timeout, before cleanup.
- **[Risk] A narrow repair expands into a new release surface.** -> Exact
  production paths, scope, dependency, schema and ownership boundaries remain
  fail-closed, with no authority expansion.

## Migration Plan

1. Validate and archive this docs-only decision, then hand it to one fresh
   ordinary/high review without creating future cards.
2. Publish only after that fresh review. A later authorization starts from the
   published decision and establishes its own clean comparison HEAD.
3. Only after the future authorization is published may a v3 successor be
   created, reconstructed as allowed, fully reproved and reviewed once.

## Open Questions

None. The decision deliberately rejects continuation outside this exact
one-successor boundary.
