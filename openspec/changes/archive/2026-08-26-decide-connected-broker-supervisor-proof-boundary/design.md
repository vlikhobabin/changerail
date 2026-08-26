## Context

The terminal v4 candidate closed its initial process, protocol and identity
defects and passed targeted behavior probes. Its committed proof still allowed
two counterfactual regressions: deleting the public `supervise` cleanup wiring
and replacing pidfd signaling with `os.kill` both left the suite green. Because
the v4 repair/re-review budget is exhausted, a new clean lineage is required.

## Goals / Non-Goals

**Goals:**

- Make the two previously disconnected production connections directly
  observable through the public entrypoint.
- Require executable counterfactual source mutations that turn the proof red.
- Preserve the bounded broker ownership, protocol, cleanup and dormancy
  contracts already published.
- Authorize one clean v5 attempt with one fresh Sol/high review.

**Non-Goals:**

- Do not patch, cherry-pick, import or publish the terminal v4 payload.
- Do not reuse its card, verdict, history, manifest, logs or retained evidence.
- Do not activate release baseline, CI, receipt, review/publish or downstream
  work.
- Do not run history, full release baseline or live matrix evidence.

## Decisions

### 1. V4 is closed and v5 is exclusive

Publication of this decision exhausts the future
`deliver-brokered-release-child-supervisor-v4` path. Its published sources
remain immutable history but do not authorize more v4 implementation work.
Exact `deliver-connected-broker-supervisor-v5` becomes the sole conforming
future broker-supervisor implementation.

The decision blocks
`authorize-bounded-connected-broker-supervisor-v5` and
`deliver-connected-broker-supervisor-v5`. The future authorization alone uses:

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The successor depends on both published sources and uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

### 2. R8 is proved through public supervise

The outer timeout and fatal broker-loss scenarios invoke only public
`supervise`. They must cause the target process group to be stopped through
that entrypoint and prove no survivor. A disposable source copy removes the
specific outer `_stop_group(proc)` exception/timeout wiring; the same connected
scenario must then fail. Direct `_stop_group` calls cannot satisfy this proof.

### 3. R9 reaches and distinguishes the signal backend

The identity scenario must first pass identity validation and then observe the
actual signaling operation. The connected scenario invokes public `supervise`,
proves `pidfd_send_signal` is used and proves no PID-only `os.kill(pid, sig)`
fallback can signal the target. A disposable source mutation replaces the
pidfd operation with PID-only signaling; the same scenario must fail. A test
that rejects before signaling is insufficient.

### 4. Counterfactual evidence is bounded and fresh

Both disposable mutations must assert that the intended production source was
actually changed and that the mutation fails for the intended reason. The
canonical candidate must pass the same scenarios. Commands and bounded outputs
are retained in a fresh ignored evidence index bound to the v5 payload.

V5 starts from the future authorization-publishing HEAD, reconstructs code and
tests from published requirements and generic findings only, adds no dependency
and adds at most 499 production LOC. It gets one implementation attempt and one
fresh Sol/high review with `0/0/0` repair/retry/rescue budget.

## Connected Proof Matrix

| Contract | Canonical proof | Required counterfactual |
| --- | --- | --- |
| R8 outer cleanup | Public `supervise` observes fatal broker loss and outer timeout, returns bounded failure and leaves no same-group target survivor. | Remove the exact public-path `_stop_group(proc)` wiring; identical scenario must fail with a detected survivor or missing cleanup observation. |
| R9 pidfd signaling | Public `supervise` reaches post-identity signaling, records pidfd use and leaves no target survivor without PID-only signaling. | Replace `pidfd_send_signal` with `os.kill(pid, sig)` in a disposable source copy; identical scenario must fail on the forbidden backend observation. |
| Mutation integrity | Each mutation changes exactly its intended source construct and executes the same public scenario. | Missing, ambiguous or no-op mutation is a test failure. |
| Dormancy | Repository-wide production entrypoint scan finds no v5 activation outside focused tests. | Any baseline, CI, receipt or review/publish wiring blocks delivery. |

## Risks / Trade-offs

- Source mutation tests are more complex than direct helper tests, but they
  prove the exact connection that prior tests missed.
- The `0/0/0` budget may terminate v5 on a small defect; this is intentional to
  stop another patch staircase.
- Linux pidfd and `/proc` behavior remains platform-specific; v5 does not claim
  native Windows supervision.

## Migration Plan

1. Validate, review and publish this docs-only decision.
2. Create, review and publish the exact docs-only v5 authorization.
3. Reconstruct one clean v5 implementation from that authorization HEAD.
4. Retain canonical and counterfactual evidence, obtain one fresh Sol/high
   review and publish only on GO.

## Open Questions

None. Any expansion beyond the two connected-proof defects and the already
published broker contract requires a separate decision.
