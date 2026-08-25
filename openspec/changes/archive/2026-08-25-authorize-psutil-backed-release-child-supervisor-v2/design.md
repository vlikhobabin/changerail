## Context

The published S2 decision is the only investigation source for a replacement
after S v1's one-successor authorization became inapplicable. It fixes the
future psutil supervision contract but explicitly requires a later
authorization before the exact S2 implementation exists. This change creates
that documentation authority source without changing executable behavior.

## Goals / Non-Goals

**Goals:**

- Publish exactly one six-field authorization object bound to the S2 decision
  and its exact future implementation.
- Preserve decision blocks, authorization dependency/block and future two-field
  reference, with `<=499` added production LOC against the authorization HEAD.
- Carry forward the exact future psutil pin, portable cleanup, deadline,
  identity, cap, stable-empty, dormancy and downstream-refresh contract.
- Keep the authorization docs-only with production, test and runtime LOC `0`.

**Non-Goals:**

- Do not create or implement `implement-psutil-backed-release-child-supervisor-v2`.
- Do not change runtime/development/bootstrap/admission dependency manifests,
  source, tests, release baseline, CI, review/publish gates, receipt schema or
  production entrypoint.
- Do not authorize H4/I3/W1/R3/A3 work or replace their required later refresh.
- Do not run or accept history, full baseline, live execution, review, commit
  or push as evidence.

## Decisions

### 1. The authorization card is the only S2 implementation authority source

The `3.inprogress` authorization card contains exactly this inline object:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The card depends on the decision and blocks only the exact future
implementation. The future implementation depends on both sources and contains
only:

```json
{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}
```

The `500` authorization ceiling is not implementation allowance: the future
implementation remains at most 499 added production LOC relative to the exact
HEAD that publishes this authorization.

### 2. Future S2 has a narrow portable psutil cleanup boundary

Future S2 pins `psutil==7.1.0` identically in runtime, development, bootstrap
and admission dependency surfaces. It uses a bounded stdlib
`selectors`/`prctl` adapter and cannot require, write or infer authority from a
writable cgroup. It accepts distinct positive `execution_timeout` and
`cleanup_timeout`, with total elapsed time at most
`execution_timeout + cleanup_timeout + 1.0s`; the fixed overhead is setup and
reporting only. Cleanup failure is terminal.

Every psutil error fails closed. Process identity is `(pid, create_time)`.
Exactly 128 unique identities, 128 descendants per
`children(recursive=True)` scan and 32 cleanup scans remain allowed; only
strict `>128`, `>128` and `>32` excesses are terminal. Cleanup success requires
the second of exactly two consecutive empty identity scans. Zero or one empty
scan rejects a premature success.

### 3. Dormancy preserves later release ownership

Before exact S2 publication, baseline, CI, review/publish gates, receipt schema
and production entrypoint neither import, invoke nor activate it. H4/I3/W1/R3/A3
authorization and implementation remain blocked until exact S2 publication and
a later tracked refresh establishes a new downstream graph.

## Connected Proof Matrix

| Contract | Focused static proof | Fail-closed result |
| --- | --- | --- |
| Lineage | Parse exact six-field authorization object, decision relation, future two-field reference and reciprocal dependencies. | Any id, path, field-count or relation mismatch blocks S2. |
| Pin and adapter | Inspect four future dependency surfaces for `psutil==7.1.0`, bounded `selectors`/`prctl` scope and writable-cgroup absence. | Missing/divergent pin or cgroup dependence blocks S2. |
| Deadlines and cleanup | Assert distinct positive timeouts, exact total arithmetic, fail-closed psutil error, `(pid, create_time)`, inclusive caps and second-empty success. | Timeout, error, identity mismatch, strict cap excess or premature success is terminal. |
| Dormancy | Assert absent release wiring and blocked H4/I3/W1/R3/A3 relations until publication plus later refresh. | Premature activation or stale downstream relation blocks delivery. |

## Risks / Trade-offs

- **[Risk] The S v1 source or failed unpublished material is reused.** -> Exact
  S2 investigation, authorization and successor identities are checked
  fail-closed.
- **[Risk] Future cleanup gains ambient cgroup authority or unbounded time.** ->
  The source fixes no-cgroup, separate deadlines, fixed overhead and finite
  identity/scan caps.
- **[Risk] Downstream release work resumes from stale lineage.** -> The source
  retains dormancy and later-refresh blocking without creating downstream work.

## Migration Plan

1. Validate and archive this same-slug docs-only authorization while keeping
   the card in `3.inprogress` for independent review.
2. Publish it. Its exact publishing HEAD becomes the future implementation's
   production-LOC comparison base.
3. Only later create the exact S2 implementation, then publish S2 and perform
   a separate downstream refresh before H4/I3/W1/R3/A3 work resumes.

## Open Questions

None. The published decision fixes the future scope, caps and dormant
downstream boundary.
