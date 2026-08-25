## Context

Published split decision `25f756e` separated the broad verification loop into
Scope A release authority core and Scope B Windows scheduling. Published Scope
A authorization `0fba407` still covered both passive parsing/admission and
terminal activation. Its unpublished implementation did not pass the required
pre-capture audit, so that complete implementation lineage remains
forensic-only.

The rescue must narrow future work without treating the failed payload as an
accepted prototype. It therefore defines two new authorization and
implementation lineages from published decision sources only.

## Goals / Non-Goals

**Goals:**

- Give A1 exact, testable passive ownership and prove it cannot affect an
  authoritative execution path.
- Give A2 the only activation and terminal receipt authority.
- Bind both successors to independent `500` authorization ceilings and exact
  reciprocal paths.
- Spend the expensive one-shot full-release capture only after A2 has wired the
  final authority path.
- Preserve the downstream scanner, Windows, verify-project and smoke order.

**Non-Goals:**

- Implement, copy, repair, review or publish any executable successor.
- Reuse code, tests, evidence, receipts, diffs or runtime state from the failed
  Scope A worktree.
- Change the 35-ID inventory, its semantic coverage or the existing Windows,
  scanner, verify-project and release-smoke ownership.
- Run reachable-history or full-release verification during this docs-only
  decision.

## Decisions

### 1. A1 is a dormant library, not a release entrypoint

A1 owns the literal registry, bounded admission and affected selector as pure
passive behavior. Until the separately published exact A2 activation,
production entrypoints, baseline, CI, receipt schemas and review/publish gates
cannot import, invoke or activate A1. After A2 is published, only that exact A2
may import, invoke or activate published A1; a static negative-wiring oracle
must fail on every pre-A2 activation and every post-A2 activation outside exact
A2.

This makes real offline admission plus focused, static and current-only
connected fault proof the exclusive deterministic A1 publication gate. A1 MUST
NOT execute, require or accept a reachable-history scan, full release baseline,
authority receipt or terminal capture. Those authority checks are not admissible
A1 publication evidence: a full baseline would execute the old authoritative
path and would neither observe A1 nor prove its dormancy.

### 2. A1 cannot receive protocol allowance

The A1 authorization object uses ceiling `500` and
`allow_new_authority_or_wire_protocol:false`. Its implementation remains
`<=499` production LOC against the exact published authorization HEAD. Any
receipt, activation or authority behavior is an ownership violation rather
than an allowed extension.

### 3. A2 is the sole atomic activation boundary

A2 imports published A1 and owns only reservation/lock/fsync, bounded JSONL,
atomic terminal marker and strict receipt equality, signals, gates and canonical
CI wiring. Its authorization uses ceiling `500` and protocol allowance `true`
because it creates the terminal authority contract. The allowance does not
cover credentials, mutation, live access or redefinition of A1.

### 4. The expensive proof is one-shot and payload-bound

After focused GREEN, a fresh Sol/`xhigh` pre-capture audit precedes exactly one
atomic capture named
`implement-terminal-release-authority-activation-cycle-1`. The captured
fingerprint must equal the reviewed payload. Capture/repair/retry-rescue budget
is `0/0/0`; any failure ends that implementation lineage instead of inviting a
second expensive run on changed code.

### 5. Publication order is a correctness property

The order is A1 authorization/implementation, A2 authorization/implementation,
scanner-v2 authorization/implementation, Windows scheduler authorization/
implementation, verify-project authorization/implementation, then the one
separate release-smoke successor. Each authorization is created only after its
predecessors are remote-reachable. This prevents a later optimization from
silently becoming authority for an earlier boundary.

## Risks / Trade-offs

- **Risk: dormant A1 can drift before A2 imports it.** -> A2 binds the exact
  published A1 predecessor and reuses its public contract rather than copying
  implementation.
- **Risk: omitting A1 full baseline hides integration defects.** -> Structural
  negative wiring proves integration is absent; A2 owns the only integration
  and its single atomic full capture.
- **Risk: two lineages add planning overhead.** -> Each implementation has one
  owner, one LOC bound and relevant proof, avoiding repeated full captures on a
  combined payload.
- **Risk: protocol allowance expands beyond receipts.** -> A2's exact ownership
  list and negative boundaries reject credential, mutation, live and A1
  redefinition claims.

## Migration Plan

1. Publish this docs-only rescue from sources `25f756e` and `0fba407`.
2. Publish the exact A1 authorization, then implement and independently review
   dormant A1 using focused/current proof only.
3. Publish the exact A2 authorization, then implement A2 and perform its single
   audited atomic full-release capture.
4. Continue scanner-v2, Windows scheduler, verify-project and release-smoke
   lineages only in the declared order.

Rollback is omission of unpublished successors. Published decision and
authorization sources remain immutable history; the failed Scope A worktree
remains forensic-only.

## Open Questions

Нет. Authorization objects, ownership, proof boundary and publication order are
fully specified by this decision.
