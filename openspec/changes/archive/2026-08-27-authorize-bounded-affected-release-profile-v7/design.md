## Context

Published investigation commit
`932b3c5643b009e5a2f372c4c6b4ca803cac1d87` terminates the unpublished
affected v6 attempt and fixes one exact successor boundary: installed
distribution origins come only from the effective interpreter's resolved
`purelib` and `platlib` paths. This change is the separate authorization gate
before any v7 card, focused test or production work may exist.

## Goals / Non-Goals

**Goals:**

- Bind one exact v7 implementation successor and bounded LOC allowance.
- Preserve exact dependency and sole-block relations.
- Carry retained pre-production RED and reviewer reconstruction requirements.
- Bind exact package-root derivation and connected production-default origin
  proof while preserving every repaired v6 guard and authority invariant.

**Non-Goals:**

- Creating or implementing the v7 successor.
- Reading or importing terminal unpublished v6 implementation artifacts.
- Running history, real full/affected, benchmark, live or certification checks.

## Decisions

### Exact authorization lineage

The authorization starts from exact published investigation HEAD and contains
one object:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-installed-origin-boundary-v7.md","investigation_id":"rescue-affected-release-profile-installed-origin-boundary-v7","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v7.md","successor_id":"implement-bounded-affected-release-profile-v7","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on the v7 investigation, integration decision, scheduler v1
implementation and v6 authorization, and blocks only v7 implementation. The
implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v7.md","authorization_id":"authorize-bounded-affected-release-profile-v7"}
```

It starts from authorization-publishing HEAD, depends on those four
predecessors plus this authorization, blocks only certification and adds at
most 499 production LOC.

Alternative: authorize implementation directly from the investigation. This
is rejected because it collapses the separately reviewed bounded-LOC and
protocol-allowance gate.

### Auditable test-first ordering

Before its first production, CI or main-spec mutation, v7 may create only its
card, same-slug OpenSpec and focused-test artifacts. It directly captures one
command that prints the workspace fingerprint first and then runs the real
focused test while preserving its non-zero exit.

The retained entry must be failed and include a reachable saved tree,
fingerprint and concrete missing module or symbol. The fresh reviewer
reconstructs that tree against the authorization HEAD and rejects any forbidden
pre-RED mutation. A later reproduction cannot replace chronology evidence.

Alternative: accept a current-tree reproduction. This is rejected because it
cannot prove what existed before production mutation.

### Exact installed-origin admission

The effective interpreter supplies only exact `purelib` and `platlib` values.
Both are resolved fail closed, checked as real package directories and
deduplicated only when equal. Every pinned runtime/dev distribution origin must
equal one admitted root. Non-package sysconfig roots, child/prefix matches and
arbitrary existing paths never qualify.

Ruff additionally binds exact version `0.6.9`, installed origin and selected
interpreter executable origin; OpenSpec remains exact offline `1.3.1`.
Aggregate admission completes before selection, scheduling or filesystem
mutation.

Alternative: admit every `sysconfig.get_paths()` value or any common prefix.
This is rejected because `stdlib`, `scripts`, `data` and `include` are not
installed-package roots.

### Production-default connected proof and preserved floor

Focused proof must exercise production-default package-root derivation, first
with an exact `purelib`/`platlib` neighbor and then independent otherwise-valid
non-package and wrong-origin cases. Mutants remove or weaken actual production
derivation, equality or executable-binding guards; an injected allowlist cannot
satisfy this criterion.

The same proof retains connected resolved-base, runtime-output, per-path,
deduplicated count, four-stream and aggregate byte guards plus the exact 35→30
profile, typed scheduler, full-only authority, four-step CI and protocol-
artifact non-authority.

Alternative: accept source assertions or aggregate success/failure. This is
rejected because disconnected proof can pass while production defaults remain
over-admitting.

## Risks / Trade-offs

- [Authorization is mistaken for implementation closure] → Successor card,
  tests and executable paths remain absent until this card is published.
- [Platform aliases make `purelib` and `platlib` equal] → Exact equality is
  deduplicated; missing, wrong-type, symlink or uncertain paths fail closed.
- [Tests exercise only injected roots] → Require the production-default happy
  neighbor and actual-guard mutants.
- [Published green v6 floors regress during clean reconstruction] → Name every
  preserved admission, selector, scheduler, CI and authority boundary.
- [Ignored RED evidence is lost] → Lost chronology requires another clean
  lineage; later reproduction is insufficient.

## Migration Plan

1. Publish this docs-only authorization from exact investigation HEAD.
2. Create the sole v7 implementation from authorization-publishing HEAD.
3. Retain and audit valid RED before production mutation.
4. Implement and review exact-origin and preserved-floor contracts.
5. Run certification only after v7 implementation publishes.

Rollback is omission of this unpublished authorization; published history is
not rewritten.

## Open Questions

None.
