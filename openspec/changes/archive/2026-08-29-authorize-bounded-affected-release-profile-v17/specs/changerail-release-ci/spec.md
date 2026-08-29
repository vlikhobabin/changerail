## ADDED Requirements

### Requirement: Affected v17 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v17` as one
docs-only authorization from exact published
`investigate-affected-release-profile-semantic-proof-closure-v17` commit
`7a627b97d8acf226ce32d1da2ab6811795cca8f1`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-semantic-proof-closure-v17.md","investigation_id":"investigate-affected-release-profile-semantic-proof-closure-v17","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v17.md","successor_id":"implement-bounded-affected-release-profile-v17","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v17, the accelerated
release-loop integration decision, semantic scheduler v1 implementation and
affected v16 authorization. It MUST block only implementation v17.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v17.md","authorization_id":"authorize-bounded-affected-release-profile-v17"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization, and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v17
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v17 successor is eligible
- **AND** any object/path/id/dependency/block/ceiling substitution fails closed.

### Requirement: Affected v17 authorization MUST preserve honest selector proof boundaries
Future v17 MUST expose a public pure bounded NUL framing/ownership boundary for
valid A/M/D and complete `R/C 000..100` grammar, consuming both owner-distinct
old/new operands and producing exact registry-ordered results. Independent pure
cases MUST cover R000/C000, interior and 100 plus every bounded framing, score,
operand, UTF-8, path and byte fault.

The public real-Git collector MUST use an explicit admitted repository root and
disposable repositories to observe all four streams, owner-distinct A/M/D and
honestly emitted non-zero R/C interior and 100 records. It MUST preserve actual
A/D outcomes for zero-similarity pairs and MUST NOT fabricate R000/C000 through
monkeypatches, wrappers, replacement output or coercion.

#### Scenario: Grammar completeness and Git honesty are both required
- **WHEN** focused proof covers R000/C000 only through pure input or claims a fabricated real-Git zero score
- **THEN** the first is accepted only for grammar/ownership and the second is rejected as Git evidence
- **AND** both boundaries must independently satisfy their exact observable contract.

### Requirement: Affected v17 authorization MUST preserve guard-relative scheduler mutants
Future v17 MUST independently author a normative case inventory, executable
case catalog, requirement guard catalog and semantic mutant catalog. Normative
and executable case IDs MUST compare equal bidirectionally. Requirement guard
IDs, case-referenced guard IDs and mutant guard IDs MUST compare equal
bidirectionally, while case IDs MUST NOT be required to equal mutant IDs.

Every case MUST execute independently from an exact passing neighbor and
reference one guard. Multiple data cases MAY reference one guard. Every guard
MUST have at least one mapped neighbor and exactly one unique mutation that
replaces one existing canonical AST operator or operand at an exact node path
with canonical before/after digests.

Inserted/generated early returns or raises, payload predicates, new control
flow, marker-only/no-op/reused edits and earlier-fault masking MUST fail closed.

#### Scenario: Guard semantics cannot be inflated by per-case bypasses
- **WHEN** multiple cases reach one guard or a generated payload-specific bypass claims a unique digest per case
- **THEN** the honest cases share one canonical guard mutant and the bypasses are rejected
- **AND** completeness remains case-exhaustive and guard-exhaustive without equating their cardinalities.

### Requirement: Affected v17 authorization MUST preserve original RED and remain dormant
Before any production, CI or main-spec mutation, future v17 MUST contain only
its implementation card, same-slug OpenSpec and focused-test artifacts. The
test MUST address a genuinely missing production module or symbol and run
directly through `bin/changerail-evidence capture`; its command MUST first print
the current ChangeRail fingerprint and then exit genuinely non-zero without
masking.

The retained failed entry MUST bind non-zero exit, `tree_sha`,
`diff_fingerprint` and the specific missing-module/symbol raw error. The saved
tree MUST exist before executable mutation and reconstruct relative to
authorization HEAD with no production, CI or main-spec mutation. Later
reproduction MUST NOT satisfy chronology.

Future v17 MUST preserve the exact 35-to-30 typed registry, independent operand
extraction, aggregate repository/origin/package/runtime/task-root admission
before Git, independent ledgers, Unicode 16.0.0 `23/235`, closed
runner/profile/scheduler/broker ownership, full-only authority,
protocol-artifact non-authority, connected resolved-base guards and exact
source-safe four-step CI.

This authorization MUST add zero production, test and runtime LOC and change
only its card, same-slug OpenSpec, synchronized release-CI spec and archive
metadata. Implementation v17, focused tests, production, CI and certification
MUST remain absent. Reachable history, real full/affected execution or
benchmark, live matrix and certification checks MUST NOT run. One fresh
ordinary `gpt-5.6-sol/high` review MUST gate publication.

#### Scenario: Authorization remains docs-only and non-authoritative
- **WHEN** maintainers audit changed paths, successor absence and retained verification
- **THEN** executable LOC is zero and implementation v17 surfaces remain absent
- **AND** affected/protocol artifacts create no publication authority and prohibited checks were not accepted.
