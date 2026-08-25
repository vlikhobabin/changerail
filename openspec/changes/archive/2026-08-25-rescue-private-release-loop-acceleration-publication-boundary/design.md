## Context

Published decision `e51dbaea99d2e6ffd537f5afda4692ff81077cb7`
split release authority into passive A1 and activating A2. Published
authorization `b027d30441ad366931aa5c89203a4286efbfa4b1` then bound A1, but no
compliant A1 implementation or A2 authorization was published.

A later private multi-worktree experiment integrated structural history,
isolated execution, a 37-ID registry, affected selection and canonical full
authority. It produced useful measurements, including a small affected subset
and a complete admitted full run, but it changed ownership in the wrong
publication order. Its commits and local evidence therefore cannot be promoted
or treated as public review evidence.

The repository permits an authorization ceiling of at most `500` production
LOC. The private experiment spans several independent owners and cannot be
made reviewable or policy-compliant as one aggregate implementation.

## Goals / Non-Goals

**Goals:**

- Create a clean publication lineage from the exact published `b027d304` base.
- Preserve only behavior-level lessons from the private experiment.
- Split implementation into independently reviewable scopes below local LOC
  ceilings.
- Permit parallel work only for history and isolation foundations with no
  shared production ownership.
- Make both full and affected execution bounded before semantic child launch.
- Make full authority payload-bound, atomic, machine-checkable and canonical in
  CI; keep affected permanently non-authoritative.
- Use per-step measurements to drive later optimization without turning timing
  into correctness authority.
- Reserve the single Sol/`xhigh` review for final unchanged certification.
- Route bounded H, I, R and A successors as `ordinary` with fresh Sol/`high`:
  their authorization may allow protocol/authority code but excludes
  credential/mutation authority, live admission and final certification.

**Non-Goals:**

- Cherry-pick, merge or publish the private integration branch.
- Reuse its runtime logs, receipts, diffs or commits as publication evidence.
- Run history, full-release or live Windows during this decision.
- Optimize `verify-project`, review-preflight or delivery-runner internals in
  this decision.
- Remove the authoritative full-release gate or allow affected evidence to
  authorize review, publish or CI.

## Decisions

### 1. One new decision supersedes the old downstream order

After this decision is published, its exact successors replace the old
A1 -> A2 -> scanner -> Windows ordering for new acceleration work. Historical
done cards, archived changes and the old normative text remain immutable
history; the main active requirement is modified rather than retroactively
editing those sources.

The private branch is a forensic prototype only. Implementers may use the
observable requirements and failure classes recorded here, but MUST start from
the exact published predecessor and MUST NOT cherry-pick private commits or
cite private runtime evidence as a gate.

### 2. Wave F has two parallel, disjoint foundations

History owner H changes only structural history scanner behavior and its
focused/CI ownership tests. Its authorization object is:

`{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/deliver-clean-structural-history-scan-v3.md","successor_id":"deliver-clean-structural-history-scan-v3","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}`

H remains `<=349` production LOC against its published authorization HEAD. It
uses two bounded Git children, strict Git-compatible commit/tree framing,
object memoization, no repository mutation and connected malformed/timeout/
output/depth/path/child-count faults.

Isolation owner I changes only the reusable case executor, exact child/report
schemas, process containment and its focused/parsed-CI tests. Its object is:

`{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-isolated-release-case-executor-v2.md","successor_id":"implement-bounded-isolated-release-case-executor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

I remains `<=499` production LOC. It owns jobs bounds, deterministic ordering,
hard output limits, timeout, crash/malformed handling, TERM/KILL/reap, isolated
HOME/TMP roots, Linux subreaper preservation and Windows Job Object
containment. It does not own registry selection, history parsing, receipts or
terminal authority.

H and I may be planned, implemented and reviewed concurrently in separate clean
worktrees because their tracked production paths and authority are disjoint.
Each is published independently before Wave R.

### 3. Wave R owns registry reconciliation and affected selection

After both H and I are remote-reachable, R publishes one exact semantic
registry and maps every semantic ID onto the canonical physical baseline. Its
authorization object is:

`{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-public-release-registry-profile-v2.md","successor_id":"implement-public-release-registry-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

R remains `<=499` production LOC. It owns the external registry anchor, exact
owner/command/group resolution, bounded A/M/D/R/C/untracked selector, closed
path mapping, fail-closed full fallback and affected report schema. It does not
create receipts, review/publish authority or canonical CI activation.

Requested `affected` remains `authoritative:false` even when uncertainty
selects every full semantic ID. Unknown paths, selector self-change, malformed
Git output, non-ancestor base, bounds failure or registry drift can only expand
selection; they cannot omit a required semantic check.

### 4. Wave A owns bounded execution and payload-bound authority

After R is remote-reachable, A activates both profiles through one canonical
runner. Its authorization object is:

`{"investigation_card":"openspec/board/4.done/rescue-private-release-loop-acceleration-publication-boundary.md","investigation_id":"rescue-private-release-loop-acceleration-publication-boundary","successor_card":"openspec/board/3.inprogress/implement-payload-bound-release-authority-v2.md","successor_id":"implement-payload-bound-release-authority-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

A remains `<=499` production LOC. Before any semantic child it performs the
same bounded offline toolchain/registry admission for full and affected. Each
semantic step has an explicit timeout, aggregate stdout/stderr bound, dedicated
process group or Job Object, TERM/KILL/reap cleanup and deterministic result.
Failure is fail-fast while already-started groups are still terminalized.

The report includes requested/effective profile, admitted state, registry and
payload fingerprints, selected semantic IDs, resolved physical steps, per-step
monotonic duration, bounded diagnostic metadata, semantic started/completed and
terminal authority. Timing is observational only: clock faults or timing values
cannot change selection, pass/fail, ordering, retry or authority.

Full authority additionally requires an `O_EXCL` reservation, held lock,
bounded append-only attempt events, temp-file fsync, atomic no-replace terminal
publication, directory fsync and exact receipt/marker/manifest/payload equality.
Review, publish and CI reject absent, partial, stale, affected, replayed,
mismatched or nonterminal receipts. CI has one explicit canonical
`--profile full-release` entrypoint and a job-level timeout.

### 5. Performance and Windows certification follow authority

After A is published, a separate profiling card records per-step time and
resource evidence from the canonical full runner, selects the dominant
bottlenecks and authorizes bounded changes to those owners. It does not use a
timing threshold as correctness authority and does not revive the failed
parallel smoke experiments.

Native Windows certification then exercises the published Job Object path on a
real Windows runner, including timeout, output overflow, crash, descendant
cleanup and deterministic report parity. Static Linux source proof is not
sufficient for this gate.

Final certification runs only after all focused/static/receipt/Windows gates
are green on an unchanged payload. It receives the one Sol/`xhigh` audit and
one predeclared history plus full-release capture with no retry after terminal
failure.

## Risks / Trade-offs

- **More cards before public code.** Four bounded owners add planning overhead,
  but each stays under the enforced `500`-LOC limit and can be reviewed without
  granting unrelated authority.
- **Clean implementation repeats engineering work.** Reimplementation is the
  cost of restoring valid publication ancestry; copying the aggregate branch
  would preserve the policy violation.
- **Parallel foundations can drift.** R accepts only exact remote-reachable H
  and I heads and re-proves complete registry-to-baseline resolution.
- **Per-step bounds can terminate historically slow checks.** Timeouts are
  declared per owner from retained observations with conservative headroom;
  timeout is a correctness failure, never an automatic retry.
- **Windows cannot be fully proven on Linux.** Publication records static
  review separately and withholds final certification until a native run.

## Migration Plan

1. Publish this docs-only decision from `b027d304`.
2. Create and publish H and I authorization cards; implement them concurrently
   in separate clean worktrees; independently review and publish both.
3. Create, implement, review and publish R from the exact merged published H/I
   predecessors.
4. Create, implement, review and publish A from R, including atomic receipts,
   manifest/review/pub gate and canonical CI.
5. Profile the authoritative full runner and optimize only measured dominant
   owners through separate bounded cards.
6. Run native Windows certification, then one final Sol/`xhigh` audit and one
   unchanged terminal history/full capture.

Rollback is omission of unpublished successors. A published authorization does
not grant another successor or permit reuse of private payload/evidence.

## Open Questions

None. Ownership, order, protocol flags, ceilings and proof boundaries are fixed
by this decision; concrete per-step timeout values are measured and declared in
Wave A artifacts before implementation.
