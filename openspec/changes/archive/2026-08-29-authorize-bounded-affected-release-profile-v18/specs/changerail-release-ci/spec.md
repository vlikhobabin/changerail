## ADDED Requirements

### Requirement: Affected v18 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v18` as one
docs-only authorization from exact published
`investigate-affected-release-profile-proof-oracle-closure-v18` commit
`fe2f50398e535c3d265ef7664b2b1a2102505e38`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-proof-oracle-closure-v18.md","investigation_id":"investigate-affected-release-profile-proof-oracle-closure-v18","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v18.md","successor_id":"implement-bounded-affected-release-profile-v18","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v18, the accelerated
release-loop integration decision, release semantic scheduler v1 implementation
and affected v17 authorization. It MUST block only
`implement-bounded-affected-release-profile-v18`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v18.md","authorization_id":"authorize-bounded-affected-release-profile-v18"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v18
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v18 successor is eligible
- **AND** any object, path, ID, dependency, block, ceiling or base substitution fails closed.

### Requirement: Affected v18 authorization MUST publish an independent complete proof inventory
Authorization MUST publish
`openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
before implementation exists. The artifact MUST contain canonical fixed-order
compact-JSONL sections for exactly 35 ordered semantic `logical_id/owner` rows,
30 ordered physical task rows and every non-task admission target.

Every physical row MUST contain task ID, command kind, every exact literal
token or the one closed ROOT-derived canonical token defined below, immutable
authorization-HEAD origin, every typed operand kind/value/location/grammar and
a non-empty ordered owned-logical-ID set. The ownership map MUST be total and
bidirectional. `windows.local-matrix` MUST own exactly the six published
Windows leaves with no aggregator PASS; every other logical ID MUST have
exactly one physical owner.

The only non-literal argv identity is
`drift.generated-fixture commands[2].argv[3]`. Authorization HEAD MUST contain
exact AST `str(DRIFT_PROJECT)`, assign `DRIFT_PROJECT` from exact
`ROOT / ".runtime" / "changerail" / "ci-drift" / "example-project"`, and
derive `ROOT` as `Path(__file__).resolve().parents[1]` equal to the real Git top
level. Independent parsing MUST prove the resolved operand equals that exact
root child before canonical serialization as
`.runtime/changerail/ci-drift/example-project`. The physical-row grammar MUST
bind that derivation and enter the full digest. Any other absolute-to-relative,
separator, case, symlink, traversal or environment normalization MUST fail
closed.

Canonical bytes MUST append, for each fixed section, an eight-lowercase-hex
UTF-8 length-framed section tag, decimal row count and every exact canonical
JSONL row. Lowercase SHA-256 MUST cover all section tags, row counts, fixed keys
and values/tokens. The semantic-ID-only newline digest MUST independently equal
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`.

Authorization verification MUST independently parse every direct and embedded
authorization-HEAD command and compare it with the physical rows, typed
operands, non-task targets, ownership and recomputed digest. It MUST parse 36
legacy `Step(...)` calls, remove only four published matrix-owned standalone
duplicates, group only the three drift operations and prove
`36 - 4 - (3 - 1) = 30` without dropping a semantic leaf. The 36-step count,
35-ID digest or a usability probe MUST NOT substitute exact command identity;
the single declared ROOT-derived canonicalization MUST compare both exact
source expression/value semantics and its canonical token.

Future production registry, production extraction and independently
implemented proof parser MUST each compare bidirectionally with this already
published anchor. Shared parsing, inference, ambiguous embedded decoding and
coordinated command/descriptor drift MUST fail closed. The proof artifact MUST
have no runtime, wire, receipt or publication authority.

#### Scenario: Coordinated command metadata cannot move the published anchor
- **WHEN** a future command and its production descriptor drift together, an embedded operand is skipped or ownership changes
- **THEN** at least one production/extraction/proof comparison or recomputed full digest differs from the published authorization inventory
- **AND** neither successful execution nor the separate 35-ID digest can certify the candidate.

#### Scenario: Legacy grouping preserves every semantic owner
- **WHEN** maintainers run the static authorization-HEAD migration oracle
- **THEN** 36 legacy calls become exactly 30 physical rows only through four published duplicate removals and one three-operation drift group
- **AND** all 35 ordered semantic IDs still map to exactly one physical owner.

### Requirement: Affected v18 authorization MUST preserve closed proof and remain dormant
Future v18 MUST preserve four independently authored scheduler catalogs,
closed one-existing-node whole-tree mutations with post-target divergence,
complete immutable scheduler/broker syntax inventory separated from exact
`supervisor=None` activation reachability, connected public mutants for every
resolved-base/four-stream/fallback guard, independent direct/embedded operand
parsing and clean-child external side-effect observation.

Before production, CI or main-spec mutation, future implementation MUST contain
only its card, same-slug OpenSpec and focused-test artifacts and retain a direct
fingerprint-first `bin/changerail-evidence capture` failure with non-zero exit,
reachable saved tree and concrete missing production module or symbol. Later
reproduction, zero-exit wrappers and terminal-v17 evidence MUST NOT satisfy
chronology.

Future v18 MUST also preserve exact 35-to-30 semantics, independently authored
Unicode 16.0.0 `23/235`, aggregate repository/origin/package/runtime/task-root
admission before Git, strict public pure and honest real-Git four-stream
selection, typed scheduler and bounded failures, full-only publication
authority, protocol-artifact non-authority, closed runner/profile/scheduler/
broker ownership and exact source-safe four-step CI.

This authorization MUST change only its card, same-slug OpenSpec/proof
artifacts, synchronized `changerail-release-ci` specification and archive
metadata. It MUST add production/test/runtime LOC `0`, create no implementation
or certification artifact and MUST NOT run or accept reachable history, real
full/affected execution, benchmark, live matrix or certification evidence. One
fresh ordinary `gpt-5.6-sol/high` review MUST gate publication.

#### Scenario: Authorization cannot execute or certify affected work
- **WHEN** maintainers audit changed paths, successor absence, LOC and verification
- **THEN** only exact lineage and future proof constraints change with zero executable LOC
- **AND** affected/proof artifacts remain non-authoritative while implementation and certification stay absent.
