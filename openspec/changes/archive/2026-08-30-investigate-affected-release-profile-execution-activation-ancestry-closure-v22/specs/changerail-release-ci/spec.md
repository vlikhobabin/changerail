## ADDED Requirements

### Requirement: Affected v22 investigation MUST isolate terminal v21 and require a clean episode
The v22 investigation MUST start from exact published authorization v21 HEAD
`f04b99d99555585703538eb9722be4c8e64cf6a6`. Before mutation, local, upstream
and remote investigation branch and remote authorization branch MUST resolve to
that exact commit. It MUST carry only validated terminal v21 review counters
`5/11`, findings `5/0/0`, the unspent same-card repair and five finding-class
summaries: missing execution binding, placeholder worklist annotations,
incomplete static/dynamic topology equality, incomplete runtime ancestry and a
non-conforming prohibited fallback episode.

Terminal v21 card, OpenSpec, source, tests, CI/main-spec mutation, manifest,
verdicts, logs and raw evidence MUST remain forensic-only. The decision MUST
modify only its card, same-slug OpenSpec artifacts, synchronized release-CI
spec and archive metadata with production/test/runtime LOC zero. It MUST NOT
create authorization, implementation or certification artifacts or run
reachable history, real full/affected execution or benchmark, live matrix or
certification checks.

#### Scenario: Terminal execution cannot be repaired in place
- **WHEN** maintainers inspect the v22 base, counters, finding classes, changed paths and successor absence
- **THEN** only published sources and bounded summaries inform the new decision
- **AND** the prior payload/evidence and prohibited episode cannot satisfy any v22 proof or chronology.

### Requirement: Affected v22 MUST bind admission to actual broker execution
Future v22 MUST add exactly one bounded additive
`changerail.release-admitted-execution.v1` transport while preserving legacy
scheduler v1 `run_plan`, broker v5 `supervise`, their accepted behavior, result
schemas and authority-free status. The additive scheduler entrypoint MUST accept
the existing ordered physical plan plus an exact ordered one-to-one closed
physical-owner admission table. A direct row MUST contain exactly one member.
A sequential-group row MUST contain one outer executor plus one exact ordered
member for every immutable inner argv. Every direct, outer and inner record MUST
bind owner/member ID, exact logical argv, deterministic physical argv/FD map,
resolved native executable, complete executable/operand component identities,
exact closed environment and canonical record digest; the physical-row digest
MUST commit to every ordered record digest.

Before worker start the scheduler MUST reject missing, extra, duplicate,
reordered, cross-owner, malformed, partially bound or stale records and every
plan/argv/digest mismatch. The worker MUST open every executable and operand
with no-follow descriptor operations, compare all identities and store the
bounded nested table in a fully sealed Linux `memfd`. Direct execution MUST pass
the verified FDs to the additive broker. Composite outer execution MUST inherit
the sealed table and every ordered outer/member FD; the group executor MUST
verify seals, identities, production registry mapping and all digests without
reconstructing target or environment from ambient state.

The admitted broker MUST NOT use path-based `subprocess.Popen`. Its bounded
fork/pipe adapter MUST call FD-capable `os.execve(fd, argv, env)` backed by
platform `fexecve`/`execveat(AT_EMPTY_PATH)` on the same verified native executable
FD with the exact closed environment. A close-on-exec status pipe MUST report
successful exec before `started`; validation or exec error MUST fail before
target start. Path rename or replacement after open MUST NOT redirect the
executed object. For a logical script/launcher, an independently derived
physical plan MUST execute a pinned native interpreter FD and pass every pinned
script/module operand as an inherited `/proc/self/fd/<n>` reference, without
kernel shebang, `/usr/bin/env`, live PATH or path reopening. Native commands
MUST preserve an empty operand rewrite.

Direct owners MUST preserve exact immutable argv. A sequential-group owner MUST
remain one scheduler task/result; its admitted typed executor MUST validate the
sealed nested table, inherited member FDs and production registry/admission
digests and invoke the admitted broker once per immutable logical argv in order.
First failure, timeout, cleanup fault, malformed tuple, FD/digest mismatch or
identity error MUST start zero later argv. Proof inventory MUST NOT be runtime
input, and admission/scheduler/broker/affected outputs MUST remain
`authoritative:false`.

#### Scenario: Ambient success cannot replace admitted execution
- **WHEN** an oracle supplies a successful fake first in PATH, changes one direct/outer/inner environment or record, swaps a component before open or renames its path after open
- **THEN** actual descriptor-bound exec uses the exact admitted logical/physical row, FD object and environment or fails before an unadmitted target starts
- **AND** sealed-bundle drift, ambient reconstruction, legacy Popen/raw-token execution and a passing protocol tuple cannot satisfy admission.

### Requirement: Affected v22 activation worklist MUST annotate every exact row
Future v22 proof MUST independently parse exact affected runner/profile/group-
executor/admitted-transport sources and exact-digest legacy scheduler/broker
sources into the complete multiset of imports, bindings, functions, predicates,
calls and raw sinks. One finite context-sensitive worklist MUST start only at
public `run_profile("affected", base=<known-docs-base>, jobs=1,
environment=<production-shaped>)` and carry normalized bound arguments,
predicate facts and exact finite callee/receiver sets through an allowlisted
transfer table.

Every row MUST contain source path/digest, qualified owner, canonical AST
field/index path and span, kind, normalized context/predicates, callee/receiver
set, predecessor, transfer rule, reachability, exact reason and sink class.
Every reachable row MUST have a complete predecessor chain to the public seed.
Every unreachable row MUST have an evaluated false-predicate or exact seed-
incompatibility reason. Empty or sentinel annotations including `cataloged`,
`pending` and `unknown` MUST fail.

A separately authored immutable `ACTIVATION_CATALOG` MUST contain the full
annotated row multiset and MUST NOT be generated by production or the observer.
Observed syntax rows, worklist results and catalog MUST compare bidirectionally
on every field. Counts, hashes, self-derived rows, unknown/ambiguous bindings,
extra/missing rows, runtime rebind, alternate wrapper/sink, unresolved transfer
or latent transition MUST fail closed.

#### Scenario: Placeholder catalog cannot prove reachability
- **WHEN** one row retains a sentinel reason, loses its predecessor, changes a binding or becomes reachable under the public seed
- **THEN** exact full-row equality or predecessor closure fails before dynamic evidence is accepted
- **AND** catalog size, uniqueness and digest cannot replace the missing annotation.

### Requirement: Affected v22 dynamic topology MUST equal the exact static projection
Before production import, a disposable clean child MUST install test-only
`sitecustomize`, a fresh nonce-bound bounded Unix datagram collector, import
guard, opcode/profile/audit hooks and at-fork registration. Registration MUST
precede production events in the public interpreter, scheduler spawn children
and group-executor exec. Closed registration/event records MUST identify nonce,
pid/ppid, bounded role, monotonic per-process sequence, source/caller/span and
context inputs rather than observer-authored row IDs. Complete process topology,
source digests, roles, sequencing, bounds and deadlines MUST be reconciled.

Every bounded raw production occurrence MUST be retained and map uniquely to
one catalog row. Only repeated occurrences with the identical canonical key
`(process role, row ID, normalized context, predicate facts,
callee/receiver)` MAY normalize to one activation key; every raw row retains a
finite count bound and a conflicting duplicate MUST remain distinct. The exact
normalized dynamic topology, static worklist reachable projection and catalog
reachable projection MUST compare bidirectionally.

The path MUST connect public affected to admitted scheduler transport, actual
descriptor-bound broker exec and, for the composite owner, sealed group
executor plus ordered inner descriptor-bound broker calls. Missing/late/
duplicate/bad-nonce registration, event-before-
registration, sequence gap/replay, unknown role, disconnected parentage,
digest mismatch, malformed/oversized datagram, loss, overflow, timeout,
unmapped raw event, missing/extra key or alternate sink MUST fail. Test-only
bootstrap/transport MUST NOT count as production reachability, pass, authority
or proof of an unreachable row.

#### Scenario: Timing loops cannot weaken exact topology
- **WHEN** harmless execution repeats one exact poll callsite a different bounded number of times
- **THEN** every raw occurrence maps to the same exact row/key and the three normalized projections remain equal
- **AND** a different role, callsite, context, predicate, callee or unmapped occurrence produces an extra failing key.

### Requirement: Affected v22 runtime admission MUST prove the complete anchored ancestry
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

#### Scenario: Aliased ancestor fails before reservation
- **WHEN** the lexical parent or any earlier component reaches the candidate through a symlink, bind/alias mount, repeated identity or outside-anchor path
- **THEN** component identity admission fails even when `resolve()` names an existing empty directory
- **AND** scheduler reservation and every semantic/later event remain unstarted.

### Requirement: Affected v22 investigation MUST freeze the clean successor order and accumulated floor
Future authorization MUST depend exactly on this investigation, the accelerated
release-loop integration decision, scheduler v1 implementation and
authorization v21 and MUST block only implementation v22. Future implementation
MUST depend exactly on those four predecessors plus authorization v22, block
only certification, start from authorization-publishing HEAD, use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v22.md","authorization_id":"authorize-bounded-affected-release-profile-v22"}`
and add no more than 499 production LOC.

Before production, CI or main-spec mutation, implementation v22 MUST retain a
new direct fingerprint-first non-zero missing-module/symbol RED with a
reconstructable saved tree. All later executable proof MUST use disposable
real-Git fixtures and an exact harmless command allowlist with retained process/
event evidence. Workspace diagnostics MUST NOT invoke public affected or exact-
full fallback. Reachable history, real full/affected execution or benchmark,
live matrix and certification checks MUST remain prohibited.

Future v22 MUST preserve published v18 proof inventory as the sole immutable
external anchor, exact `35/30/48`, semantic digest
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`, full
digest `6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35→30 ownership, `36 - 4 - (3 - 1) = 30`, Unicode 16.0.0 `23/235`,
strict four-stream selector, deterministic full fallback, full-only authority,
affected/protocol non-authority and exact source-safe four-step CI.

#### Scenario: Decision cannot authorize execution or certification
- **WHEN** maintainers audit exact future relations, authorization object, ceiling, original-RED order, changed paths and prohibited commands
- **THEN** only one clean authorization then implementation sequence is eligible
- **AND** executable successors, certification evidence and terminal v21 artifacts remain absent during investigation.
