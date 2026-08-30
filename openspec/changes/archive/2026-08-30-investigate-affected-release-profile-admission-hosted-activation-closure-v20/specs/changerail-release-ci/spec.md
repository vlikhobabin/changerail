## ADDED Requirements

### Requirement: Affected v20 investigation MUST isolate terminal v19 and close all three remaining proof gaps
ChangeRail MUST publish one clean docs-only
`investigate-affected-release-profile-admission-hosted-activation-closure-v20`
decision from exact published authorization v19 commit
`e3dbdd494f7a8d3dbd10e3b70b9b034d3079b416` after terminal unpublished v19
initial fresh acceptance `6/10`, one same-card repair, terminal fresh acceptance
`7/10`, three blockers and exhausted repair budget `1/1/0`. Only those validated
counters and the admission-order, hosted-ancestor/CI-oracle and
activation-worklist finding summaries MAY cross. Terminal v19 implementation
card, OpenSpec, source, tests, CI/main-spec mutation, manifest, verdicts, logs
and raw evidence MUST remain forensic-only and MUST NOT be read, copied,
cherry-picked, reproduced or accepted. Production, test and runtime LOC MUST
remain zero.

#### Scenario: Exhausted v19 forces a clean design source
- **WHEN** maintainers continue the affected-profile lineage after terminal v19
- **THEN** local, upstream and remote investigation plus remote authorization references resolve to the exact published SHA
- **AND** only the validated chronology and three finding-class summaries enter tracked v20 artifacts.

### Requirement: Affected v20 aggregate admission MUST precede every process and semantic event
Future v20 MUST implement one explicit two-phase admission state machine. Its
process-free Phase A MUST validate the real repository root, immutable
registry/typed operands, origins, requirement/package metadata, runtime root
and every selected task root as one aggregate before any subprocess, Git,
scheduler, write-intent or mutation event. Missing, occupied, dangling,
symlinked, aliased, non-directory or outside-root runtime/task roots and any
other Phase-A uncertainty MUST reject the whole aggregate.

Only one successful Phase-A barrier MAY enable bounded Phase-B version and
usability probes for already admitted executable identities. Phase B MUST
complete before Git collection or scheduler activation. No helper, lazy
property, descriptor extraction or error diagnostic MAY execute a process while
Phase A is incomplete.

An independent clean child MUST install audit, profile, process and write
observers before production import and maintain an external ordered event
ledger plus before/after filesystem snapshots. A separately authored stage
catalog MUST assign every admission field and neighbor to Phase A or B. For
every Phase-A failure, including an occupied selected task root, observed
process count before rejection and all later Git/scheduler/write/mutation
counts MUST be zero; output MUST remain bounded, non-authoritative and
`semantic_started:0`. Production-owned ledgers MUST NOT satisfy this proof.

#### Scenario: Runtime-root rejection cannot follow a Git probe
- **WHEN** a connected public affected case presents one invalid runtime or selected task root
- **THEN** the external observer records rejection before every process event, including executable version probes and Git
- **AND** no later semantic or mutation event occurs and affected output remains non-authoritative.

#### Scenario: Successful Phase A does not authorize publication
- **WHEN** all process-free identity and root checks reach the aggregate barrier
- **THEN** only bounded Phase-B probes may start and any Phase-B uncertainty still fails before Git/scheduler activation
- **AND** neither phase, its ledger nor its protocol artifacts create publication authority.

### Requirement: Affected v20 hosted oracle MUST reject ancestor ambiguity and derive targets from CI
Future v20 proof MUST independently parse the exact pinned source-safe
four-step CI and require its checkout/setup-node action pins, canonical hosted
runner, exact `node-version: "20"`, absence of alternate environment/execution
fields and sole explicit full-release invocation. The parsed CI row MUST yield
the admitted major and layout; the oracle MUST NOT hardcode a patch version or
import production descriptors, markers, expected sets or results.

For each separate `node`, `npm` and `npx` clean child, the oracle MUST combine
that CI row with an externally created real absolute `RUNNER_TOOL_CACHE`,
supplied architecture and observed filesystem. It MUST require exactly one
strict `node/<20.x.y>/<arch>/bin` candidate and use non-following component
identity checks from the declared cache root through every directory ancestor.
A symlink, alias, traversal, duplicate/wrong version, wrong architecture or
containment uncertainty in any directory component MUST fail in Phase A.

`node` MUST be the canonical regular executable. Any npm/npx launcher chain
MUST be relative, finite, cycle-free and wholly contained in the same real
version subtree through non-symlinked directory ancestors, and MUST end at the
CI/layout-derived canonical CLI target. Absolute, broken, traversing, escaping,
ambiguous or alternate launchers MUST fail. The oracle MUST derive the expected
final executable target and argv from parsed CI plus observed filesystem and
compare them with external process observation.

Each valid token case MUST place an exact-version successful fake first in
`PATH` and prove that production selected the oracle target while the fake was
not invoked. Missing/relative/outside roots, zero/multiple targets,
wrong/duplicate token, fake-first selection or hosted-to-system fallback MUST
return bounded non-authoritative `semantic_started:0` failure with zero process
and later Git/scheduler/write/mutation events.

#### Scenario: Symlinked ancestor cannot become a hosted root
- **WHEN** any component from `RUNNER_TOOL_CACHE` through version, architecture or `bin` is a symlink even though its resolved target is inside the fixture
- **THEN** Phase A rejects before target usability and before every process event
- **AND** resolving to the canonical bytes does not substitute component identity.

#### Scenario: Pinned CI and filesystem jointly determine each token target
- **WHEN** the valid `node`, `npm` and `npx` clean children run with one strict matching patch and architecture
- **THEN** each expected target/argv is derived from the parsed CI row and observed contained layout and equals the externally observed process target/argv
- **AND** a hardcoded patch, live PATH, `_SYSTEM_ORIGINS` or production branch marker cannot satisfy any case.

### Requirement: Affected v20 activation proof MUST derive rows and projections from one context-sensitive worklist
Future v20 MUST independently parse exact affected runner/profile and
exact-digest scheduler/broker sources and materialize the complete multiset of
imports, bindings, functions, predicates, calls and raw sinks. One finite
context-sensitive worklist seeded only by the exact public affected entrypoint,
production tasks/jobs arguments and `supervisor=None` MUST assign every row its
reachability, exact reason, predecessor row and allowlisted transfer-rule ID.

Worklist state MUST include canonical row identity, qualified callable,
normalized bound arguments and predicate facts. Bindings, receivers, returns
and predicate refinements MUST resolve to finite exact sets. Unknown, empty or
ambiguous reachable binding, unsupported call form, runtime rebind, dynamic
lookup, unlisted wrapper or unresolved transfer MUST fail closed.

The static reachable call/sink projection MUST be computed only from exact
rows marked reachable by that same worklist. A separate literal edge list,
hardcoded owner exclusions or projection that is not a deterministic function
of the full row multiset MUST NOT satisfy proof. Owner closure MUST require
every reachable function owner to have a reachable entry row and predecessor
chain to the seed, every reachable call/sink row to enter the projection and no
unreachable row to enter it.

The separately authored immutable `ACTIVATION_CATALOG` and full observed row
multiset MUST compare bidirectionally over source/digest, item/kind,
owner/canonical AST path, normalized context/predicates, exact finite
callee/receiver set, predecessor, transfer rule, reachability/reason and sink
class. Counts, uniqueness, a catalog hash, self-derived rows, extra/missing
owner or disconnected rows MUST fail.

#### Scenario: A second edge catalog cannot hide disconnected rows
- **WHEN** a literal edge worklist or dynamic expectation matches while one observed reachable owner or call/sink row lacks a worklist predecessor chain
- **THEN** owner closure or row-derived projection equality fails before behavioral evidence is admitted
- **AND** row counts, catalog hashes and selected-edge equality cannot replace the missing connection.

### Requirement: Affected v20 dynamic activation MUST equal the exact row-derived reachable projection
Future v20 MUST run a separate clean child with profile/audit/process hooks
installed before public runner import and invoke exact public affected
activation with the admitted production argument row. It MUST map every
qualified call, scheduler argument and raw sink to one canonical observed row
ID using source identity and callsite without replacing production functions,
constants, calls or results.

After an explicit immutable interpreter/harness exclusion set, the complete
dynamic call/sink multiset MUST equal the static reachable projection computed
from exact worklist rows. Every reachable owner and call/sink row MUST have its
predecessor chain and dynamic witness. The path MUST enter affected
runner/profile, scheduler default with `supervisor=None` and published broker
sinks. The injected non-None supervisor path MUST remain in syntax, observed
rows and catalog with an exact false-predicate-backed unreachable reason;
absence from trace MUST NOT establish that reason.

#### Scenario: Static and dynamic equality share canonical row identities
- **WHEN** the public affected clean child completes its source-safe activation witness
- **THEN** dynamic observations map bidirectionally to the exact row-derived reachable call/sink projection through scheduler default and broker sinks
- **AND** an extra/missing owner, row, predecessor, transfer, wrapper, sink or latent transition fails closed.

### Requirement: Affected v20 investigation MUST preserve the floor and freeze one clean successor order
Future v20 MUST preserve unchanged published authorization v18 proof inventory
as the sole immutable command/typed-operand anchor with exact section counts
`35/30/48`, semantic SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
canonical full SHA-256
`6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35-to-30 ownership and exact `36 - 4 - (3 - 1) = 30` migration. It MUST
also preserve independently authored Unicode 16.0.0 `23/235`, strict pure and
honest real-Git committed/staged/unstaged/untracked selection including rename/
copy old and new operands, deterministic full fallback, typed scheduler,
connected resolved-base/collector/fallback mutants, full-only publication
authority, protocol-artifact non-authority, closed ownership, source-safe exact
four-step CI and genuine original-RED chronology.

The only conforming future order MUST be this published investigation,
docs-only `authorize-bounded-affected-release-profile-v20`, clean
`implement-bounded-affected-release-profile-v20`, then
`certify-accelerated-release-loop-v1`. Future authorization MUST contain
exactly:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-admission-hosted-activation-closure-v20.md","investigation_id":"investigate-affected-release-profile-admission-hosted-activation-closure-v20","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v20.md","successor_id":"implement-bounded-affected-release-profile-v20","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Future authorization MUST depend exactly on this investigation, the
accelerated release-loop integration decision, release semantic scheduler v1
implementation and authorization v19 and block only implementation v20. Future
implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v20.md","authorization_id":"authorize-bounded-affected-release-profile-v20"}`,
depend on those four predecessors plus authorization v20, block only
certification, start from authorization-publishing HEAD, retain a new direct
fingerprint-first non-zero missing-module/symbol RED before production/CI/main-
spec mutation and add at most `499` production LOC.

This investigation MUST change only its card, same-slug OpenSpec artifacts,
synchronized release-CI spec and archive metadata. Authorization,
implementation and certification successors MUST remain absent. Reachable
history, real full/affected execution or benchmark, live matrix and
certification checks MUST NOT run. One fresh ordinary `gpt-5.6-sol/high` review
MUST gate publication.

#### Scenario: Investigation leaves one dormant bounded v20 path
- **WHEN** maintainers audit paths, dependencies, successor absence, LOC and verification
- **THEN** executable LOC is zero and only exact authorization v20 can follow this published decision
- **AND** affected output remains non-authoritative while certification stays blocked.
