## Context

Published investigation v18 is the latest safe affected-profile reference at
`fe2f50398e535c3d265ef7664b2b1a2102505e38`. It closed three repeated proof
classes without reading terminal implementation v17: self-derived scheduler
catalogs, incomplete execution/connectivity oracles and command metadata that
could drift with production.

The investigation requires authorization v18 to publish a full command and
typed-operand anchor before implementation. The existing 35-ID digest covers
only ordered semantic identities; it cannot prove literal command bytes. The
current baseline contains 36 legacy `Step(...)` calls, while the future
profile has 30 physical tasks after four matrix-owned duplicate processes are
removed and the three drift operations become one sequential group. These
cardinalities must remain distinct.

## Goals / Non-Goals

**Goals:**

- bind exactly one clean implementation v18 successor and a `500` ceiling;
- publish independently reviewable 35 semantic, 30 physical and non-task
  inventories before implementation;
- make command tokens, embedded operands, ownership and migration externally
  reproducible through deterministic length-framed digests;
- carry the published graph, mutation, connected-guard, external-observation,
  original-RED and accumulated release floor into the successor;
- keep this authorization docs-only and non-authoritative.

**Non-Goals:**

- no implementation card, focused test, production, CI or certification;
- no import of terminal v17 payload, tests, specs, evidence or verdicts;
- no reachable-history scan, full/affected execution, benchmark, live matrix
  or certification check;
- no runtime registry, parser, scheduler or publication-authority change.

## Decisions

### 1. One exact six-field authorization and one successor order

The card and delta specification carry the investigation's exact six-field
object. Authorization depends exactly on investigation v18, the integration
decision, scheduler v1 and authorization v17, and blocks only implementation
v18. The implementation uses only the exact two-field authorization reference,
starts at the authorization-publishing HEAD, adds at most 499 production LOC,
depends on those four predecessors plus this authorization and blocks only
certification.

Any path, ID, dependency, block, object field, ceiling or base substitution
fails closed. The proof inventory is separate from the six-field object and
does not broaden its authority.

### 2. `proof-inventory.md` is the independent normative anchor

`proof-inventory.md` is a same-slug OpenSpec artifact, not executable input,
receipt, wire message or publication authority. It contains three canonical
compact-JSONL sections in fixed order:

1. `semantic_rows`: 35 ordered `logical_id/owner` rows;
2. `physical_rows`: 30 ordered task rows with exact command representation,
   origin, typed operands and non-empty owned logical IDs;
3. `non_task_targets`: exact repository, pin, executable, origin, runtime-root
   and per-task-root descriptors required before Git or mutation.

Every JSONL object uses the key order printed in the artifact and no optional
fields. Canonical bytes are constructed independently of Markdown formatting:
for each section, append `frame(section_tag)`, `frame(decimal_row_count)` and
`frame(exact_utf8_jsonl_row)` for every row. `frame(x)` is eight lowercase hex
digits for the UTF-8 byte length, one ASCII colon and the bytes of `x`.
SHA-256 of the concatenation is lowercase hexadecimal. This covers section
tags, row counts, fixed keys and every value/token without including the digest
field in its own preimage.

The semantic section also recomputes the published newline-only 35-ID digest
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`.
Authorization verification parses the artifact independently, rejects
non-canonical JSONL and compares both digests.

### 3. Physical identity preserves semantics without false cardinality

Twenty-nine physical tasks own one semantic ID each. The single
`windows.local-matrix` task owns exactly the six published Windows leaves and
has no aggregator semantic PASS. Thus 35 IDs map totally to 30 owners.

The static legacy migration oracle parses authorization-HEAD
`scripts/run-release-baseline.py` and observes 36 `Step(...)` calls. It removes
only the four published standalone matrix duplicates (`entrypoints`, wiring
Git safety, bootstrap and verify-project) and groups only reset/bootstrap/smoke
as `drift.generated-fixture`: `36 - 4 - (3 - 1) = 30`. It then compares every
remaining exact command or approved group with the physical section and every
semantic leaf with exactly one owner. Neither the legacy count nor the 35-ID
digest can substitute this comparison.

One checkout-dependent source operand has an explicit closed canonical form.
For the grouped drift assertion, the parser requires exact authorization-HEAD
AST `str(DRIFT_PROJECT)`, the exact `ROOT / ".runtime" / "changerail" /
"ci-drift" / "example-project"` assignment and `ROOT` equal to the real Git
top level derived from `Path(__file__).resolve().parents[1]`. Only after proving
the resolved argv is that exact root child does it serialize the public-safe
repository-relative token `.runtime/changerail/ci-drift/example-project` with
the dedicated grammar recorded in the physical row. No other command or path
normalization is allowed. This binds the dynamic value without storing a
machine-specific checkout path, and both the grammar and canonical token enter
the full digest.

Production implementation later authors its runtime registry independently.
Production extraction and a separate proof parser must each match the already
published artifact bidirectionally. Coordinated changes to commands and
descriptors therefore differ from the authorization anchor.

### 4. Non-task targets are explicit and pre-semantic

The inventory freezes the repository root, requirements files, effective
Python and exact package pins, `purelib`/`platlib`, Ruff/Git/Node/npm/npx,
offline repository OpenSpec, the non-conflicting environment constraint, one
dedicated runtime root and one exact direct-child task root per physical task.
Dynamic installed paths are described by exact derivation grammar rather than
machine-local values.

Future admission compares these targets before Git, plan construction,
scheduler calls or mutation. Clean-child audit/profile hooks and external
filesystem snapshots, never production-owned empty ledgers, prove fake-first
faults have zero later effects.

### 5. Published v18 proof closure remains mandatory

Future focused proof retains four independently authored scheduler catalogs,
one-node whole-tree mutations with post-target divergence, complete immutable
scheduler/broker syntax inventory separated from exact-argument
`supervisor=None` activation, connected public mutants for every base,
collector and fallback guard, independent command parsing and externally
observed side effects. A new fingerprint-first retained missing-module/symbol
RED must exist before any executable or main-spec mutation.

The exact 35-to-30/Unicode `23/235`, aggregate admission, strict four-stream
selector, typed scheduler, full-only authority, protocol-artifact
non-authority and four-step source-safe CI floor remains unchanged.

## Risks / Trade-offs

- **[Risk] Manual inventory contains a typo.** Independent parser, source AST
  comparison, cardinality/ownership checks and both digests block publication.
- **[Risk] Legacy 36-step source is mistaken for future truth.** The migration
  oracle admits only the published four removals and one three-to-one group;
  the proof artifact, not legacy source, is normative for implementation.
- **[Risk] Dynamic package roots become machine-specific.** Exact derivation
  descriptors freeze `purelib`/`platlib` semantics without recording local
  absolute paths.
- **[Risk] Proof artifact is treated as authority.** Card/spec explicitly deny
  runtime, receipt, protocol and publication authority; only full release can
  authorize publication.

## Migration Plan

1. Publish this docs-only authorization and inventory from exact investigation
   v18 HEAD after strict/current-only verification and fresh Sol/high review.
2. Create implementation v18 only from the exact published authorization HEAD.
3. Capture one genuine original RED before executable/main-spec mutation.
4. Implement independently against the published inventory and proof closure,
   then publish only after fresh implementation review.
5. Leave certification as the sole later critical history/full-release gate.

Rollback before publication removes only this unpublished docs-only change.
After publication, changing any row, token, operand, target, map or digest
requires a new tracked decision/authorization lineage.

## Open Questions

- none.
