## ADDED Requirements

### Requirement: Affected v20 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v20` as one
docs-only authorization from exact published
`investigate-affected-release-profile-admission-hosted-activation-closure-v20`
commit `eba34c3ef965a8c4f6ffa68261408101049399c5`. Before authorization
mutation, the local/upstream/remote authorization branch and remote
investigation branch MUST resolve to that exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-admission-hosted-activation-closure-v20.md","investigation_id":"investigate-affected-release-profile-admission-hosted-activation-closure-v20","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v20.md","successor_id":"implement-bounded-affected-release-profile-v20","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v20, the accelerated
release-loop integration decision, release semantic scheduler v1
implementation and authorization v19. It MUST block only
`implement-bounded-affected-release-profile-v20`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v20.md","authorization_id":"authorize-bounded-affected-release-profile-v20"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v20
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, sole block, base and LOC ceiling
- **THEN** only the exact clean implementation v20 successor is eligible
- **AND** any object, path, ID, dependency, block, ceiling or base substitution fails closed.

### Requirement: Affected v20 authorization MUST preserve the immutable v18 proof anchor
Future v20 MUST use unchanged published
`openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
as its sole external command/typed-operand anchor. It MUST preserve exact
section counts `35/30/48`, semantic SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
canonical full SHA-256
`6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35→30 ownership and exact `36 - 4 - (3 - 1) = 30` migration.

V20 MUST NOT copy, regenerate, supersede or modify that inventory. Future
production registry/extraction and independently implemented proof parser MUST
compare bidirectionally with the already-published rows/digests. The inventory
MUST remain proof-only with no runtime, wire, receipt or publication authority.

#### Scenario: V20 cannot move the published command anchor
- **WHEN** a future command, operand, origin, target, owner, map, count or digest differs from authorization v18 inventory
- **THEN** v20 proof fails even if production metadata and parser drift together
- **AND** neither execution success nor a copied v20 inventory can replace the immutable anchor.

### Requirement: Affected v20 authorization MUST require aggregate admission before every process event
Future v20 MUST implement one process-free Phase A that aggregate-validates the
real repository root, immutable registry/typed operands, origins,
requirement/package metadata, runtime root and every selected task root before
any subprocess, Git, scheduler, write-intent or mutation event. Missing,
occupied, dangling, symlinked, aliased, non-directory or outside-root identity
and any other Phase-A uncertainty MUST reject the whole aggregate.

Only one successful Phase-A barrier MAY enable bounded Phase-B version and
usability probes for already admitted executable identities. Phase B MUST
complete before Git collection or scheduler activation. No helper, lazy
property, descriptor extraction or diagnostic MAY execute a process while
Phase A is incomplete.

An independent clean child MUST install audit/profile/process/write observers
before production import and use a separately authored stage catalog. Every
Phase-A failure, including an occupied selected task root, MUST externally show
zero process events before rejection and zero later Git/scheduler/write/
mutation events or snapshot deltas. Output MUST be bounded,
non-authoritative and `semantic_started:0`; production-owned ledgers MUST NOT
satisfy ordering proof.

#### Scenario: Aggregate root rejection precedes executable probes
- **WHEN** one repository, runtime or selected task-root invariant fails in a connected public affected case
- **THEN** rejection occurs before every process event, including version probes and Git
- **AND** no later semantic/mutation event occurs and affected output remains non-authoritative.

### Requirement: Affected v20 authorization MUST require component-safe CI-derived hosted targets
Future v20 focused proof MUST run separate clean-child cases for `node`, `npm`
and `npx`. An independent oracle MUST parse the exact pinned source-safe
four-step CI, require canonical hosted runner and exact `node-version: "20"`,
and derive the admitted major/layout without hardcoded patch, production
descriptors, branch markers, expected sets or results.

For each externally constructed real absolute `RUNNER_TOOL_CACHE`, supplied
architecture and observed filesystem, the oracle MUST require exactly one
strict `node/<20.x.y>/<arch>/bin` candidate. It MUST check every directory
component from the cache through `node`, version, architecture and `bin`
without following symlinks. Relative/outside/aliased roots, a symlinked
ancestor, wrong/duplicate version, architecture/token or uncertain containment
MUST fail in Phase A.

`node` MUST be the canonical regular executable. Any npm/npx launcher chain
MUST be relative, finite, cycle-free, wholly contained in the same real version
subtree through non-symlinked directory ancestors and terminate at the
CI/layout-derived canonical CLI target. Absolute, broken, traversing, escaping,
ambiguous or alternate launchers MUST fail. Expected final target/argv MUST be
derived from parsed CI plus observed filesystem and equal external process
observation.

Each valid case MUST place an exact-version successful fake first in PATH and
prove the canonical target ran while the fake remained unused. Zero/multiple
target, fake-first selection or hosted-to-system fallback MUST return bounded
non-authoritative `semantic_started:0` failure with zero process and later
Git/scheduler/write/mutation events.

#### Scenario: Every hosted component and target is independently admitted
- **WHEN** the valid `node`, `npm` and `npx` clean children run from one strict matching setup-node layout
- **THEN** every directory ancestor is non-symlink identity-safe and each CI/filesystem-derived target/argv equals external observation
- **AND** a hardcoded patch, live PATH, `_SYSTEM_ORIGINS`, resolved symlinked ancestor or production marker cannot satisfy a case.

### Requirement: Affected v20 authorization MUST require one row-derived activation projection
Future v20 MUST independently parse exact affected runner/profile and
exact-digest scheduler/broker sources and materialize the complete multiset of
imports, bindings, functions, predicates, calls and raw sinks. One finite
context-sensitive worklist seeded only by the exact public affected entrypoint,
production tasks/jobs arguments and `supervisor=None` MUST assign every row
source/digest, item/kind, owner/canonical AST path, normalized context/
predicates, exact finite callee/receiver set, predecessor, allowlisted transfer
rule, reachability/reason and sink class.

The static reachable call/sink projection MUST be computed only from exact
rows marked reachable by that same worklist. A separate literal edge list,
hardcoded owner exclusions or projection disconnected from the full row set
MUST NOT satisfy proof. Owner closure MUST require every reachable function
owner and call/sink row to have a complete predecessor chain to the seed.

The separately authored immutable `ACTIVATION_CATALOG` and full observed row
multiset MUST compare bidirectionally on every field. Counts, uniqueness,
catalog hashes, self-derived rows, extra/missing owner, unknown/empty/ambiguous
binding, unlisted wrapper/sink, unresolved transfer or latent transition MUST
fail closed.

#### Scenario: Complete rows and worklist cannot diverge
- **WHEN** a candidate row or reachable owner lacks a worklist predecessor/transfer chain or the static projection is maintained separately
- **THEN** owner closure or bidirectional row/projection equality fails before behavioral evidence is admitted
- **AND** selected-edge equality, row counts or hashes cannot substitute the missing connection.

### Requirement: Affected v20 authorization MUST require exact-row dynamic activation equality
Future v20 MUST run a separate clean child with profile/audit/process hooks
installed before public runner import and invoke exact public affected
activation with the admitted production argument row. It MUST map every
qualified call, scheduler argument and raw sink to one canonical observed row
ID using source identity and callsite without replacing production functions,
constants, calls or results.

After an explicit immutable interpreter/harness exclusion set, the complete
dynamic call/sink multiset MUST equal the static reachable projection computed
from exact worklist rows. Every reachable owner and call/sink row MUST have a
predecessor chain and dynamic witness. The path MUST enter affected
runner/profile, scheduler default with `supervisor=None` and published broker
sinks. The injected non-None supervisor path MUST remain observed/cataloged
with an exact false-predicate-backed unreachable reason; trace absence MUST NOT
establish that reason.

#### Scenario: Dynamic evidence uses the same canonical row identities
- **WHEN** future focused proof activates the exact public affected path
- **THEN** dynamic calls/sinks compare bidirectionally with the row-derived reachable projection through scheduler default and broker
- **AND** an extra/missing owner, row, predecessor, transfer, wrapper, sink or latent transition fails closed.

### Requirement: Affected v20 authorization MUST preserve original RED and remain dormant
Before production, CI or main-spec mutation, future implementation MUST contain
only its card, same-slug OpenSpec and focused-test artifacts and retain a direct
fingerprint-first `bin/changerail-evidence capture` failure with genuine
non-zero exit, reachable saved tree and concrete missing production module or
symbol. Later reproduction, zero-exit wrapper and terminal-v19 evidence MUST
NOT satisfy chronology.

Future v20 MUST preserve independently authored Unicode 16.0.0 `23/235`,
strict pure and honest real-Git committed/staged/unstaged/untracked selection
including rename/copy old and new operands, deterministic exact full fallback,
typed scheduler and bounded failures, connected resolved-base/collector/
fallback mutants, full-only publication authority, protocol-artifact
non-authority, closed runner/profile/scheduler/broker ownership and exact
source-safe four-step CI. Affected and protocol outputs MUST remain
`authoritative:false`.

This authorization MUST change only its card, same-slug OpenSpec artifacts,
synchronized release-CI spec and archive metadata. It MUST add production/test/
runtime LOC `0`, create no implementation or certification artifact and MUST
NOT run or accept reachable history, real full/affected execution, benchmark,
live matrix or certification evidence. One fresh ordinary
`gpt-5.6-sol/high` review MUST gate publication.

#### Scenario: Authorization cannot execute or certify affected work
- **WHEN** maintainers audit changed paths, successor absence, LOC and verification
- **THEN** only exact lineage and future proof constraints change with zero executable LOC
- **AND** affected/proof artifacts remain non-authoritative while implementation and certification stay absent.
