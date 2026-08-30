## ADDED Requirements

### Requirement: Affected v22 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v22` as one
docs-only authorization from exact published
`investigate-affected-release-profile-execution-activation-ancestry-closure-v22`
commit `6fd94a4bf964dc9551fae607f9504fd22e3b3e26`. Before authorization
mutation, the local/upstream/remote authorization branch and remote
investigation branch MUST resolve to that exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-execution-activation-ancestry-closure-v22.md","investigation_id":"investigate-affected-release-profile-execution-activation-ancestry-closure-v22","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v22.md","successor_id":"implement-bounded-affected-release-profile-v22","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v22, the accelerated
release-loop integration decision, release semantic scheduler v1
implementation and authorization v21. It MUST block only
`implement-bounded-affected-release-profile-v22`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v22.md","authorization_id":"authorize-bounded-affected-release-profile-v22"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v22
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, sole block, base and LOC ceiling
- **THEN** only the exact clean implementation v22 successor is eligible
- **AND** any object, path, ID, dependency, block, ceiling or base substitution fails closed.

### Requirement: Affected v22 authorization MUST preserve the immutable v18 proof anchor
Future v22 MUST use unchanged published
`openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
as its sole external command/typed-operand anchor. It MUST preserve exact
section counts `35/30/48`, semantic SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
canonical full SHA-256
`6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35→30 ownership and exact `36 - 4 - (3 - 1) = 30` migration.

V22 MUST NOT copy, regenerate, supersede or modify that inventory. Future
production registry/extraction and independently implemented proof parser MUST
compare bidirectionally with the already-published rows/digests. The inventory
MUST remain proof-only with no runtime, wire, receipt or publication authority.

#### Scenario: V22 cannot move the published command anchor
- **WHEN** a future command, operand, origin, target, owner, map, count or digest differs from authorization v18 inventory
- **THEN** v22 proof fails even if production metadata and parser drift together
- **AND** neither execution success nor a copied v22 inventory can replace the immutable anchor.

### Requirement: Affected v22 authorization MUST bind every admitted row to descriptor-bound exec
Future v22 MUST add exactly one bounded additive
`changerail.release-admitted-execution.v1` transport while preserving legacy
scheduler v1 `run_plan`, broker v5 `supervise`, their accepted behavior,
defaults, result schemas and authority-free status. The additive scheduler
entrypoint MUST accept the existing ordered physical plan plus one exact
ordered one-to-one closed physical-owner admission table. A direct row MUST
contain exactly one member; a sequential-group row MUST contain one outer
executor plus every exact ordered immutable inner member.

Every direct, outer and inner record MUST bind owner/member ID, exact logical
argv, deterministic physical argv/FD map, resolved native executable, complete
executable/operand component identities, exact closed environment and
canonical record digest. The physical-row digest MUST commit to every ordered
record digest. Missing, extra, duplicate, reordered, cross-owner, malformed,
partially bound or stale records and every plan/argv/digest mismatch MUST fail
before worker start.

The worker MUST open every executable and operand with no-follow descriptor
operations, compare identities and store the complete bounded nested table in a
fully sealed Linux `memfd`. Direct work MUST pass verified FDs to the additive
broker. Composite work MUST inherit the sealed table and all ordered outer/
member FDs; the group executor MUST validate seals, identities, production
registry mapping and digests without ambient reconstruction.

The admitted broker MUST NOT use path-based `subprocess.Popen`. Its bounded
fork/pipe adapter MUST call FD-capable `os.execve(fd, argv, env)` backed by
`fexecve` or `execveat(AT_EMPTY_PATH)` on the same verified native executable
FD with the exact closed environment. A close-on-exec status pipe MUST report
successful exec before `started`; validation or exec error MUST fail before
target start. For scripts/launchers the physical plan MUST execute a pinned
native interpreter FD and pass pinned script/module operands only as inherited
`/proc/self/fd/<n>` references, without kernel shebang, `/usr/bin/env`, live
PATH or path reopening.

The composite owner MUST remain one scheduler task/result. Its admitted typed
executor MUST invoke the additive broker once per immutable logical argv in
order, and first failure, timeout, cleanup fault, malformed tuple, FD/digest or
identity mismatch MUST start zero later argv. Proof inventory MUST NOT be
runtime input and all admission/scheduler/broker/affected artifacts MUST remain
`authoritative:false`.

#### Scenario: Ambient process success cannot satisfy admitted execution
- **WHEN** a case changes one direct/outer/inner record or environment, swaps a target before open, renames it after open or places a successful fake first in PATH
- **THEN** execution uses the exact admitted physical row, FD object and environment or fails before an unadmitted target starts
- **AND** sealed-bundle drift, ambient reconstruction, legacy Popen/raw-token execution and a passing protocol tuple cannot satisfy admission.

### Requirement: Affected v22 authorization MUST require an independent actual-execution oracle
The future focused oracle MUST derive every direct, outer and inner logical and
physical row independently from the immutable v18 inventory, exact pinned
source-safe CI and externally constructed fixture filesystem. It MUST observe
actual `os.exec` audit/syscall inputs, executable/operand FD `fstat`
identities, sealed-bundle bytes/seals and post-exec `/proc/<pid>/exe` identity.
It MUST NOT use production descriptors, `_SYSTEM_ORIGINS`, live PATH,
usability-only results or production branch markers as expected truth.

The oracle MUST compare expected and observed logical argv, physical argv/FD
map, environment, component ancestry, records, row/bundle digests and exact
target bidirectionally. It MUST prove admitted work reaches zero legacy Popen
or raw-token execution calls. Missing/extra/cross-owner/reordered member,
changed environment or bundle, fake-first selection, pre-open swap, unsafe
launcher and every malformed neighbor MUST fail before target start. Renaming
or replacing a path after the verified FD is opened MUST not redirect the
executed object.

#### Scenario: Production cannot attest its own executable identity
- **WHEN** production admission and expected rows drift together or a marker claims the intended target ran
- **THEN** independent FD, exec-input, sealed-bundle and post-exec identity comparison still fails
- **AND** only the immutable inventory, pinned CI and external filesystem derive expected execution.

### Requirement: Affected v22 authorization MUST require a complete public-entry activation worklist
Future v22 MUST independently parse exact affected runner/profile/group-
executor/admitted-transport sources and exact-digest legacy scheduler/broker
sources into the complete multiset of imports, bindings, functions, predicates,
calls and raw sinks. One finite context-sensitive worklist MUST start only at
public `run_profile("affected", base=<known-docs-base>, jobs=1,
environment=<production-shaped>)` and carry normalized bound arguments,
predicate facts and exact finite callee/receiver sets through an allowlisted
transfer table.

Every row MUST contain source path/digest, qualified owner, canonical AST
field/index path and span, kind, normalized context/predicates,
callee/receiver set, predecessor, transfer rule, reachability, exact reason and
sink class. Every reachable row MUST have a complete predecessor chain to the
public seed. Every unreachable row MUST have an evaluated false-predicate or
exact seed-incompatibility reason. Empty or sentinel annotations including
`cataloged`, `pending` and `unknown` MUST fail.

A separately authored immutable `ACTIVATION_CATALOG` MUST contain the full
annotated row multiset and MUST NOT be generated by production or the observer.
Observed syntax rows, worklist results and catalog MUST compare
bidirectionally on every field. Counts, hashes, self-derived rows,
unknown/ambiguous bindings, extra/missing rows, runtime rebind, alternate
wrapper/sink, unresolved transfer or latent transition MUST fail closed.

#### Scenario: Placeholder annotations cannot prove activation
- **WHEN** one row retains a sentinel reason, loses its predecessor, changes a binding or becomes reachable under the public seed
- **THEN** exact full-row equality or predecessor closure fails before dynamic evidence is accepted
- **AND** catalog size, uniqueness and digest cannot replace the missing annotation.

### Requirement: Affected v22 authorization MUST require exact normalized dynamic topology
Before production import, a disposable clean child MUST install test-only
`sitecustomize`, a fresh nonce-bound bounded Unix datagram collector, import
guard, opcode/profile/audit hooks and at-fork registration. Registration MUST
precede production events in the public interpreter, scheduler spawn children
and group-executor exec. Closed records MUST identify nonce, pid/ppid, bounded
role, monotonic per-process sequence, source/caller/span and context inputs
rather than observer-authored row IDs. Complete process topology, source
digests, roles, sequencing, bounds and deadlines MUST be reconciled.

Every bounded raw production occurrence MUST be retained and map uniquely to
one catalog row. Only repeated occurrences with identical canonical key
`(process role, row ID, normalized context, predicate facts,
callee/receiver)` MAY normalize to one activation key; every raw row MUST have
a finite count bound and a conflicting duplicate MUST remain distinct. The
exact normalized dynamic topology, static worklist reachable projection and
catalog reachable projection MUST compare bidirectionally.

The path MUST connect public affected to admitted scheduler transport, actual
descriptor-bound broker exec and, for the composite owner, the sealed group
executor plus ordered inner descriptor-bound broker calls. Missing/late/
duplicate/bad-nonce registration, event-before-registration, sequence gap or
replay, unknown role, disconnected parentage, digest mismatch, malformed or
oversized datagram, loss, overflow, timeout, unmapped raw event, missing/extra
key or alternate sink MUST fail. Test bootstrap/transport MUST NOT count as
production reachability, pass, authority or proof of an unreachable row.

#### Scenario: Timing-loop normalization cannot hide a new topology edge
- **WHEN** one exact poll callsite repeats a different bounded number of times
- **THEN** every raw occurrence maps to its exact row/key and all three normalized projections remain equal
- **AND** a different role, row, context, predicate, callee or unmapped occurrence creates an extra failing key.

### Requirement: Affected v22 authorization MUST prove anchored runtime ancestry and preserve closed guards
Phase A MUST accept only an exact lexical direct child of one admitted real
runtime anchor. It MUST reject relative, empty, dot, dot-dot and alternate
normalized spellings and require lexical/real equality. Starting from an open
anchor FD, it MUST walk every candidate component using directory-FD operations
with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`, compare expected and observed
`(device,inode,type,mount)` identities, reject repeated identities and reject
any symlink, alias, mount or outside-anchor transition.

The target MUST be a real empty directory. Unknown or dangling entries,
non-directory targets and any known/unknown neighbor MUST fail. The exact FD
chain and emptiness MUST be rechecked immediately before scheduler reservation.
Every failure MUST be bounded and non-authoritative with
`semantic_started:0` and externally observed zero later process, Git,
scheduler, write or mutation events.

Future v22 MUST preserve independently derived hosted `node`, `npm` and `npx`
targets from the exact pinned four-step CI and canonical setup-node/toolcache
layout, including exact npm/npx launcher targets, usable fake-first rejection
and zero hosted-to-system fallback. It MUST preserve exact dependency block and
the sole explicit `full-release` invocation across every CI execution-bearing
field; duplicate, wrapped, chained, indirect, inactive or reordered semantics
MUST fail.

#### Scenario: Aliased ancestry or alternate hosted/CI target fails before semantics
- **WHEN** any runtime ancestor is symlinked/aliased/repeated/outside-anchor or a hosted/CI target differs from the independently parsed exact source
- **THEN** admission or CI structure fails before scheduler reservation or target start
- **AND** usability, resolved path, hidden command or passing protocol output cannot satisfy the guard.

### Requirement: Affected v22 authorization MUST preserve a clean episode and remain dormant
Before production, CI or main-spec mutation, future implementation MUST contain
only its card, same-slug OpenSpec and focused-test artifacts and retain a direct
fingerprint-first `bin/changerail-evidence capture` failure with genuine
non-zero exit, reachable reconstructable saved tree and concrete missing
production module or symbol. Later reproduction, zero-exit wrapper, workspace
fallback diagnostics and terminal v21 evidence MUST NOT satisfy chronology.

All later executable proof MUST run only in disposable real-Git fixtures with
an exact harmless command allowlist and retained process/event evidence.
Workspace diagnostics MUST NOT invoke public affected or exact-full fallback.
Future v22 MUST preserve Unicode 16.0.0 `23/235`, strict committed/staged/
unstaged/untracked selection including rename/copy old and new operands,
deterministic exact-full fallback, typed scheduler, connected guard mutants,
full-only publication authority, affected/protocol non-authority, closed
ownership and exact source-safe four-step CI.

This authorization MUST change only its card, same-slug OpenSpec artifacts,
synchronized release-CI spec and archive metadata. It MUST add production/test/
runtime LOC `0`, create no implementation or certification artifact and MUST
NOT run or accept reachable history, real full/affected execution or benchmark,
live matrix or certification evidence. One fresh ordinary
`gpt-5.6-sol/high` review MUST gate publication.

#### Scenario: Authorization cannot execute or certify affected work
- **WHEN** maintainers audit changed paths, successor absence, LOC, chronology and verification
- **THEN** only exact lineage and future proof constraints change with zero executable LOC
- **AND** affected/proof artifacts remain non-authoritative while implementation and certification stay absent.
