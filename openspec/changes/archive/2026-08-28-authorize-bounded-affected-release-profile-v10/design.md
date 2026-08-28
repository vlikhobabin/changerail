## Context

Published rescue v10 is the clean investigation/design source for the next
affected implementation. It fixes the contract before executable work:
repository-local runtime output must reject symlinked ancestors, execution
ownership must inventory every import and `ast.Call`, and guard proof must be
complete, connected and observed through a public boundary.

The rescue was published at exact commit
`0318483db897ade4908013e3d270bda60b0e1f3a`. Terminal implementation v9 and
all of its tracked or runtime payload remain forensic-only. A separate
authorization is required before implementation v10 may exist.

## Goals / Non-Goals

**Goals:**

- publish the exact six-field authorization for one clean v10 successor;
- bind authorization and implementation to exact dependency and block sets;
- retain auditable pre-production RED before executable mutation;
- carry the accumulated 35→30, admission, selector, scheduler, authority and
  CI floor plus the three new rescue boundaries;
- keep this stage docs-only with production/test/runtime LOC `0`.

**Non-Goals:**

- create implementation v10, focused tests, production code, CI or runtime
  authority;
- read, repair, reproduce or import terminal v9 payload or raw evidence;
- weaken full-only publication authority or make affected artifacts authoritative;
- run history, real full/affected, benchmark, live-matrix or certification
  evidence.

## Decisions

### Exact rescue object is the sole authorization source

The card and delta spec carry the published rescue's exact six-field object:
the rescue card/id, future implementation card/id, ceiling `500` and protocol
allowance `true`. No wrapper, alternate successor or additional field is
allowed. This is authorization metadata for the bounded successor, not a grant
of publication authority to affected mode.

### Authorization and implementation sets remain distinct

This authorization depends exactly on rescue v10, the integration decision,
scheduler v1 and authorization v9, and blocks only implementation v10. Future
implementation adds this authorization to that exact set and blocks only
certification. Its direct rescue dependency must equal the six-field
`investigation_id`; transitive reachability through this card is insufficient.

The future implementation uses only the exact two-field authorization reference
and starts from authorization-publishing HEAD. The authorization ceiling is
`500`, while the implementation card is constrained to at most `499` added
production LOC.

### Authorization preserves, but cannot fabricate, RED chronology

Before production, CI or main-spec mutation, future v10 may contain only its
card, same-slug artifacts and focused tests. `bin/changerail-evidence capture`
must invoke a command that prints the workspace fingerprint first and then
directly executes a genuinely failing focused test with non-zero exit.

The saved entry and reachable tree must let a fresh reviewer reconstruct the
pre-production state against authorization HEAD. A late reproduction,
zero-success wrapper or prose claim cannot replace retained raw chronology.

### Rescue boundaries are additive to the accumulated release floor

Future v10 retains exact 35-ID digest and 35→30 typed ownership, aggregate
admission, effective distribution origins, bounded four-stream selection,
typed scheduler-v1, full-only authority, exact four-step CI and protocol
artifact non-authority.

It additionally validates every runtime leaf and existing ancestor against the
real repository root before mutation; freezes every import and `ast.Call`
shape in runner/profile/scheduler source; and executes every normative guard
catalog row as a canonical/single-mutant pair through `profile.main` or
`run_smoke`. Dynamic execution, function replacement, private-helper-only
observation and earlier-fault masking fail closed.

### Authorization stays dormant until remote publication

Only the card, same-slug OpenSpec artifacts, synchronized release-CI spec and
archive metadata may change. Implementation v10 and certification remain
absent through review and publish. The clean successor may be created only from
the remote-reachable authorization-publishing commit.

## Risks / Trade-offs

- [The accumulated contract is large] → keep exact dependency, authorization,
  containment, ownership and proof boundaries separately observable.
- [Protocol allowance can be mistaken for affected publication authority] →
  restate full-release as the sole authority and all affected artifacts as
  non-authoritative.
- [A future test can claim RED without chronology] → require captured non-zero
  output plus reachable-tree reconstruction against authorization HEAD.
- [Successor creation can race publication] → verify absence through publish
  and require the successor base to equal the published remote tip.

## Migration Plan

1. Publish this docs-only authorization from exact rescue v10 HEAD.
2. Prove its remote branch reaches the exact final commit.
3. Create clean implementation v10 only from that commit and obtain retained
   pre-production RED before executable mutation.
4. Review and publish implementation v10, then open the one final critical
   certification stage.

Rollback before successor creation is simply to leave implementation absent.
After publication, superseding this authorization requires another tracked
decision; terminal v9 is never a rollback source.

## Open Questions

- none; rescue v10 fixes the object, successor, boundary and ordering.
