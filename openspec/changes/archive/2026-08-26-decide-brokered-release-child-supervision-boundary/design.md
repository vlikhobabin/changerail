## Context

Three unpublished supervisor implementations progressively closed ordinary
process-group, descendant, output and EOF defects. The remaining v3 boundary is
architectural: a caller that becomes subreaper and scans all of its children
cannot distinguish a target orphan from a new descendant of an unrelated
pre-existing child. An identity acquisition fault immediately after target
launch also occurs before the caller has a complete ownership set.

The new design moves ownership into a dedicated broker subprocess. The broker
has no pre-existing application children, enables subreaper mode before target
launch and owns the target tree by construction. The caller remains a protocol
controller and never scans or claims caller-global children.

## Goals / Non-Goals

**Goals:**

- Make process ownership structural instead of inferred from a caller-global
  before/after snapshot.
- Specify a bounded protocol whose EOF, malformed state or sequence drift
  cannot become success.
- Retain bounded execution, cleanup, output, identity and report limits.
- Permit one clean v4 implementation plus at most one bounded repair/re-review.

**Non-Goals:**

- Do not resume, patch, cherry-pick or publish the terminal v3 payload.
- Do not reuse its verdict, history, logs, receipts, manifests or evidence.
- Do not add a writable-cgroup requirement, privilege escalation or a new
  external dependency beyond the published psutil pin.
- Do not activate baseline, CI, review/publish, receipt or downstream work.
- Do not run history, full baseline or live matrix evidence for this decision.

## Decisions

### 1. The broker is the ownership boundary

The parent launches one broker in a new session/process group. Before accepting
a target command, the broker enables its platform child-supervision role and
emits a bounded ready message. Only then may it launch the target.

On Linux the broker, not the application caller, is the child subreaper. Its
initial application-child set is empty and its only launched workload is the
target, so adopted target descendants remain in a broker-owned domain. The
caller never enables subreaper mode, compares caller-global child snapshots or
claims unrelated caller children.

### 2. The protocol cannot manufacture completion

Messages use one closed version and monotonic sequence numbers. Each message
has a bounded byte size and the complete stream has bounded message and byte
counts. The valid order is `ready`, `started`, zero or more bounded observations,
and exactly one terminal report after cleanup.

EOF, timeout, malformed UTF-8/JSON, unknown or duplicate field/message,
sequence drift, multiple terminal reports, broker exception or missing cleanup
proof is terminal failure. Pipe EOF is stream state only and never completion.

### 3. Cleanup stays inside the broker ownership domain

Every recoverable post-launch exception enters a total broker `finally` path.
The broker tracks exact `(pid, create_time)` identities, performs bounded
recursive discovery and TERM/KILL/reap, and requires two consecutive empty
scans before its single terminal report.

The parent does not terminate a responsive broker before its cleanup deadline.
It retains an outer process-group containment path for a missing/unresponsive
broker and reports terminal failure, never success, when the broker cannot
produce the cleanup proof. The future implementation must state its fatal
broker-death guarantee precisely and may not claim that process groups contain
detached sessions.

### 4. One clean lineage replaces the patch staircase

Publication of this decision exhausts the earlier
`deliver-psutil-backed-release-child-supervisor-v3` path. Its published
decision and authorization remain immutable historical sources, but no longer
authorize creation, continuation, repair, rescue, reuse or publication of v3.
Any earlier active requirement that permitted the future v3 successor is
superseded by this decision. Exact v4 is the sole conforming future supervisor
implementation path.

The decision blocks only
`authorize-bounded-brokered-release-child-supervisor-v4` and
`deliver-brokered-release-child-supervisor-v4`. The future authorization alone
contains:

```json
{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The successor depends on the decision and authorization and uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}
```

It starts from the authorization-publishing HEAD and adds at most 499
production LOC. It receives one implementation attempt and one fresh Sol/high
review. A first NO-GO may authorize exactly one bounded same-card repair and
one final Sol/high re-review; no third review or rescue is allowed.

## Connected Proof Matrix

| Contract | Focused proof | Fail-closed result |
| --- | --- | --- |
| Ownership | Run a pre-existing caller bystander that forks after broker readiness alongside target setsid/double-fork cases. | Bystander identities survive and never enter broker cleanup; every target identity is gone. |
| Launch boundary | Inject readiness, target spawn and immediate identity-acquisition faults. | No pre-ready target; every post-launch recoverable fault enters broker cleanup. |
| Protocol | Mutate UTF-8, JSON, version, fields, sequence, duplication, truncation, EOF and terminal count at exact N/N+1 bounds. | Any mutation is terminal and cannot emit success. |
| Execution | Exercise live-leader EOF, normal exit, signal, crash, timeout and bounded stdout/stderr. | EOF alone is incomplete; terminal report follows process completion and cleanup. |
| Cleanup | Exercise setsid, inherited pipe, TERM-ignore, fork-during-TERM, identity reuse/error and stable-empty boundaries. | No successful report with a live/zombie owned identity or incomplete proof. |
| Controller | Inject broker exception, missing report and cleanup deadline exhaustion. | Outer containment runs and result remains terminal failure without overstating detached-session coverage. |
| Dormancy | Parse all production entrypoints and CI ownership before publication. | Any activation outside focused tests blocks delivery. |
| Exclusive lineage | Parse active requirements and reject any future v3 implementation or any supervisor successor other than exact v4. | Published historical v3 sources remain immutable but cannot authorize executable work. |

## Risks / Trade-offs

- **Broker fatal death cannot be described as ordinary successful cleanup.**
  The contract requires terminal failure and an explicit outer-containment
  guarantee; detached-session coverage must be proved rather than inferred.
- **IPC adds a wire surface.** The exact authorization sets
  `allow_new_authority_or_wire_protocol=true`, while message grammar and bounds
  remain closed and testable.
- **One repair may extend the cycle.** It replaces repeated rescue lineages with
  one bounded correction and one final review, then stops.

## Migration Plan

1. Validate, archive, independently review and publish this docs-only decision.
2. Create, review and publish the exact docs-only v4 authorization without a
   successor.
3. Create one clean v4 implementation from that authorization HEAD, run focused
   broker tests and one fresh Sol/high review.
4. If cycle one is NO-GO, permit only one bounded in-scope repair and one final
   Sol/high re-review. Publish only a fresh GO.

## Open Questions

The future implementation must choose and prove the exact fatal broker-death
containment boundary. It may not silently equate a process group with a detached
process tree.
