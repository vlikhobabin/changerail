## Context

Published `rescue-release-process-supervisor-boundary` establishes S as the
first foundation, and published
`authorize-bounded-release-child-supervisor-v1` authorizes exactly
`implement-bounded-release-child-supervisor-v1`. That source is deliberately a
one-successor object. The unpublished S v1 implementation exhausted cycle 2,
and an unpublished attempted S2 authorization failed its prerequisite. Neither
unpublished episode is a reusable authority or source of tracked implementation
detail.

This decision is the new investigation source for a later psutil-backed S2.
It changes no executable surface and creates neither a future authorization
card nor a successor card.

## Goals / Non-Goals

**Goals:**

- Publish one exact future six-field object for only
  `implement-psutil-backed-release-child-supervisor-v2`.
- Require a later authorization card to depend on this decision and block only
  that successor; require the successor to depend on both decision and
  authorization, with only the authorization's exact two-field reference.
- Bound future S2 around pinned psutil process identity and cleanup mechanics,
  deterministic time accounting and a connected static proof matrix.
- Keep release baseline and CI activation dormant, and hold downstream
  H4/I3/W1/R3/A3 until S2 is published and a later refresh restores their
  dependencies.

**Non-Goals:**

- Do not reuse the S v1 authorization or the failed unpublished S2
  authorization attempt.
- Do not create, implement, test, pin or activate S2 now.
- Do not add a cgroup requirement, parser, scheduler policy, Windows Job
  behavior, registry/profile selection, receipt ownership, credential,
  mutation, live-admission or final-certification authority.
- Do not run or cite history scans, full release baseline, live execution,
  review, commit or push as evidence.

## Decisions

### 1. New decision, not mutation of the one-successor source

The only future S2 authorization object is:

```json
{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The later `authorize-psutil-backed-release-child-supervisor-v2` card depends
on this published decision and blocks only the exact successor. The future
successor depends on both cards and uses exactly:

```json
{"authorization_card":"openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md","authorization_id":"authorize-psutil-backed-release-child-supervisor-v2"}
```

This prevents the old v1 source from silently authorizing a new successor and
prevents the failed authorization attempt from becoming a second source.

### 2. Portable containment does not rely on writable cgroups

Future S2 pins `psutil==7.1.0` in its runtime, development, bootstrap and
admission dependency surfaces. It uses a bounded stdlib `selectors`/`prctl`
adapter for POSIX launch, output and process containment; it MUST NOT require,
write or infer authority from a cgroup. `psutil` supplies observation and
identity, while the adapter owns bounded lifecycle control.

### 3. Cleanup is a separate, terminally accountable phase

Future S2 receives separate positive `execution_timeout` and
`cleanup_timeout`. End-to-end elapsed time is bounded by exactly
`execution_timeout + cleanup_timeout + 1.0s`; the fixed `1.0s` is exclusively
setup/report overhead and cannot be consumed by execution or cleanup. A cleanup
failure, psutil exception, timeout expiry, identity mismatch or cap exhaustion
is terminal and fail-closed.

The cleanup proof uses `(pid, create_time)` identities. Its `128` unique
identities, `128` descendants per `children(recursive=True)` scan and `32`
cleanup scans are inclusive allowed maxima: exactly each maximum remains
permitted, while only a value greater than that cap is terminal. It requires
exactly two consecutive scans with empty identity sets before success; the
second empty scan is the success threshold, rather than a failure cap. The
negative proof rejects a claimed success after zero or one empty scan. This
stable-empty rule prevents a transient empty traversal from being mistaken for
completed recursive cleanup.

### 4. Dormancy protects later release ownership

S2 has no baseline or CI activation point. Until exact S2 publication, later
refresh and re-authorization, H4/I3/W1/R3/A3 remain blocked; no prior
publication or evidence carries their authorization across this new boundary.
Only the later refresh may declare the refreshed downstream dependency graph.

### 5. Connected proof remains static and scoped

The future connected proof matrix joins each decision to an observable static
gate: exact lineage/object and card relations; four-surface pin/admission;
selector/prctl and no-cgroup negative scope; timeout arithmetic; psutil
fail-closed identity, cap and stable-empty cleanup; and dormant wiring plus
downstream refresh blocking. This current docs-only decision validates only
the matrix contract and its own source relations, not a live supervisor.

## Connected Proof Matrix

| Contract | Connected focused proof | Fail-closed result |
| --- | --- | --- |
| Lineage | Parse the exact six-field decision object, future two-field reference and reciprocal card dependencies. | Any id, path, field-count or relation mismatch blocks S2. |
| Pin and admission | Inspect runtime, development, bootstrap and admission declarations for one identical `psutil==7.1.0` pin. | Missing, divergent or indirect pin blocks admission. |
| Portable adapter | Inspect bounded `selectors`/`prctl` ownership and assert no cgroup write or writable-cgroup requirement. | Adapter scope expansion or cgroup dependence blocks S2. |
| Time budget | Use controlled clocks to assert distinct positive timeouts and total elapsed time no greater than `execution_timeout + cleanup_timeout + 1.0s`. | Overrun, merged timeout or cleanup extension is terminal. |
| Recursive cleanup | Exercise psutil-error, PID-reuse, `>128` identity, `>128` descendant, `>32` scan and repeated-empty fixtures using `(pid, create_time)`; exact 128/128/32 remain allowed and the second empty scan is success. | Error, identity mismatch, strict cap excess or premature success before the second empty scan is terminal/rejected. |
| Dormancy and refresh | Statically assert absent baseline/CI wiring and blocked H4/I3/W1/R3/A3 relations until published S2 plus later refresh. | Premature wiring or stale downstream relation blocks delivery. |

## Risks / Trade-offs

- **[Risk] A single-successor source is reused for S2.** -> Exact source and
  successor identifiers, paths and field count are checked fail-closed.
- **[Risk] A process is reused between discovery and termination.** ->
  `(pid, create_time)` identity mismatches terminate cleanup.
- **[Risk] Cleanup extends execution indefinitely.** -> Separate timeouts,
  fixed `1.0s` overhead and finite scan/identity caps bound the whole path.
- **[Risk] A writable cgroup becomes an ambient platform dependency.** -> The
  contract explicitly uses the bounded selector/prctl adapter and rejects that
  assumption.
- **[Risk] Downstream CI work resumes from stale S v1 lineage.** -> S2
  publication and an explicit later refresh are both required.

## Migration Plan

1. Complete this same-slug docs-only decision, sync the release-CI delta and
   archive it while leaving its card in `3.inprogress` for independent review.
2. Publish the reviewed decision; only then may a separate flow create the
   future S2 authorization card with the exact six-field object.
3. Publish that authorization before creating the exact S2 successor; publish
   S2 and perform a later separate downstream refresh before H4/I3/W1/R3/A3
   work resumes.

Before publication, rollback removes only this unpublished docs payload. After
publication, changes to object identity, caps, proof matrix or downstream
relations require a new tracked decision rather than mutation.

## Open Questions

None. The decision intentionally fixes exact caps and a `1.0s` overhead rather
than delegating those boundaries to the future implementation.
