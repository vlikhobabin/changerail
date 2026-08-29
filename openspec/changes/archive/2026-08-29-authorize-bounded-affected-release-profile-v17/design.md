## Context

Investigation v17 is published at exact commit
`7a627b97d8acf226ce32d1da2ab6811795cca8f1` and defines one feasible clean
successor architecture. Authorization is intentionally separate so preflight
can resolve a stable six-field investigation object and the implementation can
start from one remotely published HEAD without importing terminal v16.

## Goals / Non-Goals

**Goals:**

- bind exactly one implementation v17 path, ID and bounded LOC ceiling;
- preserve original-RED chronology before executable mutation;
- carry the split selector and guard-relative scheduler proof verbatim;
- keep authorization docs-only, dormant and independently reviewable.

**Non-Goals:**

- no implementation card, focused test, production, CI or certification;
- no terminal v16 payload/evidence access;
- no history, release/affected execution, benchmark or live matrix;
- no new publication authority.

## Decisions

### Exact tracked source

The card/spec own one literal six-field authorization object from the published
investigation. Future implementation owns only the two-field authorization-card
reference. Alternate wrappers, aliases, paths, IDs or ceilings fail closed.

### One clean successor

Authorization depends exactly on investigation v17, integration decision,
scheduler v1 and authorization v16, and blocks only implementation v17.
Implementation adds authorization v17 as its fifth dependency, blocks only
certification and starts from authorization-publishing HEAD.

### Dormant proof carriage

This change repeats observable future constraints but adds no executable proof.
The future successor must independently create its original RED and implement
the published grammar/emission and case/guard/mutant relations from clean
sources.

## Risks / Trade-offs

- [Docs repeat accumulated constraints] → exact objects and bounded acceptance
  make drift machine-reviewable; main spec remains the normative source.
- [Implementation may still exceed complexity] → preflight enforces the
  published `500` exception and implementation itself remains capped at `499`.
- [Authorization could be mistaken for authority] → production/test/runtime
  LOC is zero and affected/protocol artifacts remain explicitly
  non-authoritative.

## Migration Plan

Publish authorization after fresh ordinary/high GO. Only then create the clean
implementation worktree/branch from its exact published commit. No rollback is
needed for dormant docs-only state.

## Open Questions

Нет; implementation and certification boundaries are fixed by the published
investigation.
