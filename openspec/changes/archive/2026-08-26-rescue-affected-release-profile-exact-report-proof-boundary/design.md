# Design: exact report/proof boundary для affected profile v2

## Clean Lineage
The decision depends only on published integration decision, scheduler v1 and
affected v1 authorization. Unpublished implementation/rescue trees, cards,
manifests, verdicts, logs and evidence are forensic-only and cannot satisfy any
gate. The future authorization repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on this decision plus the three published predecessors and
blocks only v2 implementation. The implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

It depends on those four predecessors plus published v2 authorization, blocks
only certification, starts from authorization-publishing HEAD and adds at most
499 production LOC.

## Closed Scheduler Schema
Top-level fields are exactly `version`, `status`, `jobs`, `results`; version is
`changerail.release-semantic-scheduler.v1`; jobs is requested `1` or `4`;
results contain every physical plan ID exactly once in registry order. Summary
status is exactly `pass` iff all rows pass and exactly `fail` otherwise.

Rows have exactly `id`, `status`, `reason`, `returncode`, `output_bytes`,
`cleanup_complete`, `messages`. Pass is exactly
`pass/completed/0/0..8192/true/3`. Every terminal, outer and synthetic tuple has
status exactly `fail`. Terminal reasons are `child_failed`, `output_limit`,
`execution_timeout`, `cleanup_incomplete`, `internal_error`; outer reasons are
`protocol_error`, `broker_lost`, `outer_timeout`, `outer_cleanup_error`;
synthetic reasons are `supervisor_result_error`, `supervisor_error`, `cancelled`,
`executor_error`. Exact reason-specific return-code/output/cleanup/message
domains match published scheduler v1. Common integers exclude booleans; reason
is bounded ASCII; summary canonical JSON is at most 64 KiB.

## Admission And Authority
Both requested profiles complete aggregate bounded effective-PATH admission
before Git selection and every semantic scheduler call. Any admission fault
returns one bounded aggregate failure with `semantic_started: 0`. Requested
affected is always non-authoritative, including full fallback. Only admitted
requested full-release with exact full pass may authorize. V2 creates or accepts
no receipt, capture, marker or cache, and no affected/focused output satisfies
review, publish or certification.

## Exact CI Schema
YAML is parsed without YAML 1.1 key coercion. Top-level fields, workflow name,
triggers, permissions, sole verify job, job fields/name/runner, ordered step
field sets, literal pinned action SHA, exact `with` maps and two run scalars are
all closed. Extra fields/jobs/steps/actions/runs, env, matrix, condition,
continue-on-error, shell/working-directory, wrappers/chains/indirection and
affected/scheduler/broker/individual semantic commands fail.

## Connected Proof
Disposable fixtures enumerate every valid scheduler tuple and mutate all
top-level, row, identity/order/cardinality/status/bound cross-fields. Protocol
fixtures prove receipt/capture/marker/cache absence and rejection. CI fixtures
mutate exact top-level/job/trigger/permission/action/with/run/field/order/gating
surfaces. Selector/admission/authority fixtures preserve all A/M/D/R/C,
staged/unstaged/untracked, bound/framing/Git/self/unknown fallback, zero-launch
admission and full-only authority behavior. Every mutation is non-noop and
counterfactual. No reachable history, real full, benchmark, live or certification
evidence is allowed before the final successor.
