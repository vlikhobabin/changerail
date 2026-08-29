## ADDED Requirements

### Requirement: Affected v18 investigation MUST isolate terminal v17 and close repeated proof oracles
ChangeRail MUST publish one clean docs-only
`investigate-affected-release-profile-proof-oracle-closure-v18` decision from
exact published authorization v17 commit
`fdff98a2fbf962182b2d5777f9c5cc6e33e6cf17` after terminal unpublished v17
review cycles `4/10` and `5/10`, findings `5 blockers` and `3 blockers`, and
exhausted repair budget `1/1/0`. Only validated counters and three finding-class
summaries MAY cross. Terminal v17 card, OpenSpec, source, tests, CI, main-spec
mutation, manifest, verdict files, logs and raw evidence MUST remain
forensic-only and MUST NOT be read, copied, cherry-picked, reproduced or
accepted.

The three classes requiring design closure are self-derived scheduler
catalog/mutation proof, incomplete dynamic-execution and connected-base guard
proof, and tautological registry/side-effect observation. Production, test and
runtime LOC MUST remain zero.

#### Scenario: Terminal payload cannot become a design source
- **WHEN** maintainers start v18 investigation from authorization v17 HEAD
- **THEN** local, upstream, remote investigation and remote authorization references resolve to the exact published SHA
- **AND** only the validated chronology and three blocker summaries cross into tracked decision artifacts.

### Requirement: Affected v18 scheduler proof MUST use sealed catalogs and a closed mutation language
Future v18 MUST independently author immutable normative-case, executable-case,
requirement-guard and semantic-mutant catalogs. No catalog MAY be generated,
imported or completed from another catalog or production expected registry.
Normative and executable case IDs MUST compare equal bidirectionally.
Requirement guard IDs, case-referenced guard IDs and mutant guard IDs MUST
compare equal bidirectionally. Each executable case MUST reference exactly one
guard; each guard MUST have at least one passing/invalid public neighbor and
exactly one mutant.

Every guard/mutant MUST pin repository-relative source path, qualified function,
canonical AST field/index path, source digest, node kind and canonical
before/after digests. A mutant MUST replace exactly one existing allowlisted AST
operator or operand. Canonical whole-module comparison MUST reject any other
node/field change, added or removed statement/control-flow/call node, generated
source, payload predicate, wrapper, early return/raise, marker-only/no-op or
reused edit.

The mapped public case MUST pass on original source, reach the exact target span
in both original and mutant traces before the first divergence, and then
produce the declared public-outcome difference. Failure or divergence before
the target MUST be rejected as earlier-fault masking.

#### Scenario: Shared guard remains independently and semantically proven
- **WHEN** several executable neighbors reference one requirement guard
- **THEN** case completeness and guard completeness pass without deriving one catalog from another or duplicating the mutant
- **AND** the one pinned source mutation is accepted only when target reachability precedes its public-outcome kill.

#### Scenario: Generated or masked mutant fails closed
- **WHEN** a candidate adds control flow, changes an unpinned node or fails before reaching the mapped target
- **THEN** whole-tree, digest or trace validation rejects it before evidence admission
- **AND** unique labels, strings or after-digests cannot make it authoritative.

### Requirement: Affected v18 execution proof MUST whitelist the complete graph and connect every base guard
Future v18 MUST parse canonical runner, profile, scheduler and broker sources and
construct complete imports, callable bindings, functions, calls and raw
execution sinks. This observed graph MUST compare bidirectionally with a
separately authored partitioned edge/sink catalog.

Affected-owned runner/profile calls MUST be limited to direct local or pinned
builtin names, exact one-level members of pinned module aliases and the exact
published scheduler entrypoint with exact production arguments and
`supervisor=None`. Callable parameters/assignments, lambdas, nested
functions/closures, call-valued or subscript-valued callees, unresolved nested
attributes and raw execution sinks in affected-owned source MUST fail.

Immutable published scheduler/broker modules MUST instead match exact pinned
whole-source digests and an independently authored legacy-edge partition that
enumerates every existing higher-order shape, including the public injected
supervisor path, as a complete syntactic inventory.

A separate context-sensitive activation graph MUST start at the exact
affected-owned entrypoint and argument rows. It MUST resolve every reachable
higher-order node to a finite non-empty exact callee/receiver set and classify
every latent node with an exact predicate/argument-backed unreachable reason.
With `supervisor=None`, only the published default broker path may be reachable;
the scheduler's injected callback path MUST remain cataloged but unreachable.
Syntax inventory, catalog and reachable/unreachable classifications MUST compare
bidirectionally. A non-None affected supervisor, changed argument row or
predecessor digest, new shape, latent-to-reachable transition,
unknown/empty/undeclared-ambiguous reachable binding, runtime rebind or unlisted
edge MUST fail and MUST NOT authorize affected successor to modify
scheduler/broker.

Across both partitions `__import__`, dynamic `getattr`, importlib, `eval`,
`exec`, `compile`, unbound dynamic dispatch, unlisted wrappers and alternate
subprocess/`os.system`/shell-equivalent sites MUST fail closed. Existing broker
raw sinks MUST be exact pinned catalog entries reachable from affected-owned
source only through the published scheduler default and broker entry edges.

One immutable guard inventory MUST enumerate every resolved-base, four-stream
collector and bounded-fallback guard. Every guard ID MUST have a mutant at the
exact canonical production node and at least one connected public case through
an explicit admitted repository root; collector cases MUST use honest
disposable Git. Guard IDs, connected-case references and mutant IDs MUST compare
equal bidirectionally. Private or disconnected helpers MUST NOT satisfy proof.

#### Scenario: Dynamic wrapper cannot escape the closed graph
- **WHEN** affected source uses a higher-order/dynamic call or immutable predecessor source/binding differs from its exact digest and legacy catalog
- **THEN** structural resolution fails before behavioral evidence is admitted
- **AND** existing injected scheduler shapes pass only as predicate-backed unreachable inventory while the exact default path has complete finite bindings.

#### Scenario: Every fallback guard has a real connected counterfactual
- **WHEN** one resolved-base, collector or fallback guard lacks a canonical source mutant or explicit-root public case
- **THEN** guard/case/mutant equality fails closed
- **AND** a disconnected helper mutation or private direct call cannot replace the missing proof.

### Requirement: Affected v18 admission proof MUST independently parse operands and externally observe later events
Future v18 MUST keep one immutable physical-task registry with literal command
representations and separate typed target descriptors containing kind, logical
ID, owner, origin and exact operand location or embedded grammar. Production
extraction and an independently implemented proof parser MUST separately parse
every direct argv token and embedded shell operand and compare exact typed
multisets bidirectionally with an immutable normative inventory published and
independently reviewed in authorization v18 before implementation.

That authorization inventory MUST have separate sections for all 35 ordered
semantic `logical_id/owner` rows, all 30 ordered physical task rows and every
non-task admission target. Each physical row MUST contain task ID, command kind,
every exact token, origin, every operand kind/value/token location or embedded
grammar location and its non-empty ordered owned-logical-ID set. The 35-to-30
map MUST be total and bidirectional; every logical ID has exactly one physical
owner, and the Windows matrix task owns exactly its six published leaves with
no aggregator PASS.

Its lowercase SHA-256 MUST cover deterministic length-framed UTF-8
serialization of section tags, row counts, fixed keys and every value/token.
Authorization review MUST compare the semantic section with the published
35-ID list, the physical/non-task sections with published future 35-to-30
requirements and authorization-HEAD source, and a static migration oracle that
maps every mandatory legacy baseline semantic owner exactly once into the
future inventory. The current 36 legacy `Step(...)` calls MUST NOT be treated
as either 35 semantic rows or 30 physical rows, and no false cardinality
equality MAY satisfy proof. The six-field authorization object remains
unchanged; the inventory is a separate proof-only artifact with no runtime or
publication authority.

Production registry rows, production extraction and the independently
implemented proof parser MUST each compare bidirectionally with the published
30 physical/non-task sections, 35-to-30 map and recomputed full digest. The
proof parser MUST NOT import production
extraction, descriptors or expected multisets. The existing 35-ID newline
digest MUST remain a separate order/ownership check and MUST NOT be accepted as
a command-token anchor. Shared parsing, suffix/shape inference, ambiguous shell
expansion and coordinated command/descriptor drift MUST fail closed.

Admission side-effect evidence MUST come only from a clean child with audit and
profile hooks installed before production import plus external before/after
filesystem snapshots. The external observer MUST classify process and exact Git
argv, pinned scheduler entry calls, write-intent operations and mutation. It
MUST NOT replace production functions, constants, calls or results.
Production-declared ledgers, including literal empty arrays, MUST NOT satisfy
evidence.

Every fake-first repository, origin, package, runtime-root or selected-task-root
fault MUST return a bounded non-authoritative report with `semantic_started:0`
and zero later process, Git, scheduler, write-intent and snapshot-delta events.

#### Scenario: Coordinated command metadata cannot certify itself
- **WHEN** a command and its declared descriptors drift together or embedded operands are not independently decoded
- **THEN** at least one production/proof comparison differs from the separately published authorization inventory or its canonical digest
- **AND** neither the 35-ID digest, legacy 36-Step count nor a successful usability probe can substitute exact 30-task identity admission.

#### Scenario: Production empty arrays are not side-effect evidence
- **WHEN** an admission failure returns empty production-owned ledgers but an external hook observes Git, scheduler or mutation activity
- **THEN** the clean-child proof fails closed
- **AND** only pre-import hooks and external snapshots can establish zero later events.

### Requirement: Affected v18 investigation MUST preserve the floor and freeze one clean successor order
Future v18 MUST preserve the exact 35-to-30 typed registry, independently
authored Unicode 16.0.0 `23/235`, aggregate repository/origin/package/runtime/
task-root admission before Git, strict public pure and honest real-Git
four-stream selection, typed scheduler and bounded summary failures, full-only
publication authority, protocol-artifact non-authority, closed runner/profile/
scheduler/broker ownership, source-safe exact four-step CI and retained
original-RED chronology from the accumulated published contract.

The only conforming future order MUST be this published investigation,
docs-only `authorize-bounded-affected-release-profile-v18`, clean
`implement-bounded-affected-release-profile-v18`, then
`certify-accelerated-release-loop-v1`. Future authorization MUST contain
exactly:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-proof-oracle-closure-v18.md","investigation_id":"investigate-affected-release-profile-proof-oracle-closure-v18","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v18.md","successor_id":"implement-bounded-affected-release-profile-v18","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Future authorization MUST depend exactly on this investigation, the integration
decision, scheduler v1 and authorization v17 and block only implementation v18.
Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v18.md","authorization_id":"authorize-bounded-affected-release-profile-v18"}`,
depend on those four predecessors plus authorization v18, block only
certification, start from authorization-publishing HEAD, retain a new genuine
original RED before executable mutation and add at most `499` production LOC.

This investigation MUST change only its card, same-slug OpenSpec artifacts,
synchronized release-CI spec and archive metadata. Authorization,
implementation and certification successors MUST remain absent. Reachable
history, real full/affected execution or benchmark, live matrix and
certification checks MUST NOT run. One fresh ordinary `gpt-5.6-sol/high` review
MUST gate publication.

#### Scenario: Investigation leaves one dormant bounded path
- **WHEN** maintainers audit paths, dependency graph, successor absence and verification
- **THEN** executable LOC is zero and only authorization v18 can follow the published decision
- **AND** affected output remains non-authoritative while certification stays blocked.
