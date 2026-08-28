## Context

Published investigation v11 is the clean decision source for the next affected
implementation. It fixes the contract before executable work: runtime output
must be one exact dedicated target, every selected task root needs read-only
pre-reservation proof, and scheduler proof completeness must come from an
independent requirement map plus immutable reason schema.

The investigation was published at exact commit
`c1df80ff4591c6c2619856b91cc4e1bcdc50cec6`. Terminal implementation v10 and
all of its tracked or runtime payload remain forensic-only. A separate
authorization is required before implementation v11 may exist.

## Goals / Non-Goals

**Goals:**

- publish the exact six-field authorization for one clean v11 successor;
- bind authorization and implementation to exact dependency and block sets;
- retain auditable pre-production RED before executable mutation;
- carry the accumulated release floor plus exact dedicated runtime-root,
  task-root pre-reservation and independent scheduler-matrix boundaries;
- keep this stage docs-only with production/test/runtime LOC `0`.

**Non-Goals:**

- create implementation v11, focused tests, production code, CI or runtime
  authority;
- read, repair, reproduce or import terminal v10 payload or raw evidence;
- weaken full-only publication authority or make affected artifacts authoritative;
- run history, real full/affected, benchmark, live-matrix or certification
  evidence.

## Decisions

### Exact investigation object is the sole authorization source

The card and delta spec carry the published investigation's exact six-field
object: investigation card/id, future implementation card/id, ceiling `500`
and protocol allowance `true`. No wrapper, alternate successor or additional
field is allowed. This metadata authorizes one bounded clean successor; it does
not grant publication authority to affected mode.

### Authorization and implementation sets remain distinct

This authorization depends exactly on investigation v11, the integration
decision, scheduler v1 and authorization v10, and blocks only implementation
v11. Future implementation adds this authorization to that exact set and
blocks only certification. Its direct investigation dependency must equal the
six-field `investigation_id`; transitive reachability is insufficient.

The future implementation uses only the exact two-field authorization
reference and starts from authorization-publishing HEAD. The authorization
ceiling is `500`, while the implementation card is constrained to at most
`499` added production LOC.

### Authorization preserves, but cannot fabricate, RED chronology

Before production, CI or main-spec mutation, future v11 may contain only its
card, same-slug artifacts and focused tests. `bin/changerail-evidence capture`
must invoke a command that prints the workspace fingerprint first and then
directly executes a genuinely failing focused test with non-zero exit.

The retained entry and reachable tree must let a fresh reviewer reconstruct
the pre-production state against authorization HEAD. A late reproduction,
zero-success wrapper or prose claim cannot replace retained raw chronology.

### Dedicated runtime-root and task-root admission precede mutation

Future v11 must match the exact frozen runtime-output descriptor and reject
empty, dot/repository-root, NUL, surrogate/non-encodable, overlong,
absolute/multi-component/alternate, escaping, symlinked, wrong-type/access or
non-dedicated values before Git, scheduler or filesystem mutation. A missing
leaf is admitted only as the exact direct child of its real contained writable
and searchable parent.

Every selected task root is independently checked read-only for exact bounded
unique direct-child token, containment and absence of leaf/symlink/conflict
before `run_plan`. Aggregate failure launches zero semantics. A later race or
atomic reservation failure stays scheduler-owned, bounded and
non-authoritative and removes only roots created by that attempt.

### Scheduler completeness comes from independent normative sources

Future focused proof has an independently authored requirement-to-row map and
a separate immutable reason schema covering every `completed`, terminal,
outer, synthetic and `cancelled` tuple. It enumerates top-level
version/jobs/status/size and result identity/order/count plus valid nullable,
boolean and numeric boundary neighbors and one-field invalid type, bound and
cross-field cases.

The executable catalog must equal the required-row set in both directions and
bind each row to a unique non-noop production-source/AST mutant observed
through public `profile.main` or `run_smoke` after preceding guards pass.
Catalog-local counts, replacement production functions, reused/disconnected
mutants and earlier-fault masking cannot establish completeness.

### Authorization stays dormant until remote publication

Only the card, same-slug OpenSpec artifacts, synchronized release-CI spec and
archive metadata may change. Implementation v11 and certification remain
absent through review and publish. The clean successor may be created only
from the remote-reachable authorization-publishing commit.

## Risks / Trade-offs

- [The accumulated contract is large] → keep exact object, dependency,
  runtime-root, task-root and scheduler-matrix boundaries separately observable.
- [Protocol allowance can be mistaken for affected publication authority] →
  restate full-release as the sole authority and all affected artifacts as
  non-authoritative.
- [A future test can claim RED without chronology] → require captured non-zero
  output plus reachable-tree reconstruction against authorization HEAD.
- [A catalog can self-certify an omission] → require bidirectional equality
  against independent normative sources and public-boundary counterfactuals.
- [Successor creation can race publication] → verify absence through publish
  and require successor base to equal the published remote tip.

## Migration Plan

1. Publish this docs-only authorization from exact investigation v11 HEAD.
2. Prove its remote branch reaches the exact final commit.
3. Create clean implementation v11 only from that commit and obtain retained
   pre-production RED before executable mutation.
4. Review and publish implementation v11, then open the one final critical
   certification stage.

Rollback before successor creation is simply to leave implementation absent.
After publication, superseding this authorization requires another tracked
decision; terminal v10 is never a rollback source.

## Open Questions

- none; investigation v11 fixes the object, successor, boundary and ordering.
