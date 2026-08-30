## ADDED Requirements

### Requirement: Affected v21 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v21` as one
docs-only authorization from exact published
`investigate-affected-release-profile-composite-command-dynamic-closure-v21`
commit `09e0555d8c189dff0b77823a2286ce0f7a36a067`. Before authorization
mutation, the local/upstream/remote authorization branch and remote
investigation branch MUST resolve to that exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, IDs, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-composite-command-dynamic-closure-v21.md","investigation_id":"investigate-affected-release-profile-composite-command-dynamic-closure-v21","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v21.md","successor_id":"implement-bounded-affected-release-profile-v21","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v21, the accelerated
release-loop integration decision, release semantic scheduler v1
implementation and authorization v20. It MUST block only
`implement-bounded-affected-release-profile-v21`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v21.md","authorization_id":"authorize-bounded-affected-release-profile-v21"}`,
start from authorization-publishing HEAD, add no more than `499` production
LOC, depend exactly on those four predecessors plus this authorization and
block only `certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v21
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, sole block, base and LOC ceiling
- **THEN** only the exact clean implementation v21 successor is eligible
- **AND** any object, path, ID, dependency, block, ceiling or base substitution fails closed.

### Requirement: Affected v21 authorization MUST preserve the immutable v18 proof anchor
Future v21 MUST use unchanged published
`openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
as its sole external command/typed-operand anchor. It MUST preserve exact
section counts `35/30/48`, semantic SHA-256
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
canonical full SHA-256
`6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
total 35→30 ownership and exact `36 - 4 - (3 - 1) = 30` migration.

V21 MUST NOT copy, regenerate, supersede or modify that inventory. Future
production registry/extraction and independently implemented proof parser MUST
compare bidirectionally with the already-published rows/digests. The inventory
MUST remain proof-only with no runtime, wire, receipt or publication authority.

#### Scenario: V21 cannot move the published command anchor
- **WHEN** a future command, operand, origin, target, owner, map, count or digest differs from authorization v18 inventory
- **THEN** v21 proof fails even if production metadata and parser drift together
- **AND** neither execution success nor a copied v21 inventory can replace the immutable anchor.

### Requirement: Affected v21 authorization MUST preserve one composite result and close scheduler admission
Direct tasks MUST present their exact immutable argv to scheduler v1. The
immutable three-command physical owner MUST remain one scheduler task/result
whose separately typed repository group-executor command contains only owner ID
and expected production registry digest. The executor MUST import production
registry, validate exact digest, owner, kind and complete ordered group and
invoke published broker v5 once per immutable argv in order with bounded
timeouts.

Every nested result MUST be an exact closed passing broker tuple. First failure,
timeout, cleanup fault, malformed result or identity mismatch MUST stop later
argv and fail the outer physical result. Direct subprocess/shell execution, raw
proof-inventory input, wrapper argv substitution, skip, duplicate or reorder
MUST fail closed. An independent oracle MUST separately parse immutable
inventory and production registry, observe the outer scheduler/broker row and
all three ordered inner broker argv and prove one physical result plus zero
later argv after each injected failure index.

Profile pass MUST additionally require exact published scheduler version,
requested jobs, closed top-level fields/status, exact ordered selected owners
and one complete internally consistent passing result per owner. Missing,
empty, duplicate, unknown, reordered, extra, cross-owner, malformed or failing
rows and wrong version/jobs/status/registry digest MUST fail locally without
full authority. Scheduler/protocol artifacts and affected output MUST remain
`authoritative:false`.

#### Scenario: Composite and scheduler forgeries fail closed
- **WHEN** a focused case changes one immutable argv, nested ordering, physical cardinality, top-level summary or result-row identity
- **THEN** execution or local admission fails before pass and no later argv starts after the first nested failure
- **AND** neither the outer result nor any protocol artifact can manufacture publication authority.

### Requirement: Affected v21 authorization MUST require one public-entry activation worklist
Future v21 MUST independently parse exact affected runner/profile/group-
executor and exact-digest scheduler/broker sources and materialize the complete
multiset of imports, bindings, functions, predicates, calls and raw sinks. One
finite context-sensitive worklist MUST start only at public
`run_profile("affected", base=<known-docs-base>, jobs=1,
environment=<production-shaped>)`; internal `main(..., supervisor=None)` MUST be
reachable only through that public path.

The worklist MUST assign every row source/digest, owner, canonical AST
path/span, normalized context/predicates, exact finite callee/receiver set,
predecessor, allowlisted transfer, reachability/reason and sink class. Static
reachable call/sink projection MUST be only the exact filter of those rows.
Every reachable owner/row MUST have a complete predecessor chain to the seed.

The separately authored immutable activation catalog and full observed row
multiset MUST compare bidirectionally on every field. Counts, uniqueness,
catalog hashes, self-derived rows, unknown/empty/ambiguous binding,
extra/missing owner, alternate wrapper/sink, unresolved transfer or latent
transition MUST fail closed.

#### Scenario: Internal reachability cannot replace public exact rows
- **WHEN** seed, binding, predicate, callsite, wrapper, sink, predecessor, transfer or row identity is removed, added or redirected
- **THEN** full catalog, owner closure or exact row-derived projection equality fails
- **AND** counts, hashes, sink classes or selected edges cannot replace the missing public connection.

### Requirement: Affected v21 authorization MUST require bounded cross-process dynamic equality
Before the exact public clean child starts, the independent harness MUST bind a
test-only bounded Unix datagram collector and materialize `sitecustomize.py`
with a fresh 128-bit nonce, hard deadline, exact source-digest/role catalog and
finite datagram/event/byte bounds. Inherited `PYTHONPATH` MUST install one
registration, production-import guard, opcode/profile/audit hooks and at-fork
child registration before production import in the public interpreter, every
scheduler `spawn` interpreter and the execed group executor.

Closed registration/event datagrams MUST contain nonce, pid/ppid, bounded role,
monotonic per-process sequence and caller code/span inputs rather than
observer-authored row IDs. The collector MUST reconcile every registered
interpreter/fork child with observed spawn/exec/fork topology before comparing
rows. Event-before-registration, missing, late, duplicate or bad-nonce
registration, sequence gap/replay, unknown production-importing role,
disconnected parentage, unexpected interpreter, digest mismatch, malformed or
oversized datagram, overflow, timeout or collector loss MUST fail.

The complete dynamic occurrence multiset MUST equal the static row-derived
reachable call/sink projection bidirectionally through public affected,
scheduler default, outer broker, group executor and inner brokers. Unknown,
ambiguous, zero/multiple, missing or extra mappings MUST fail. Non-None
supervisor rows MUST remain cataloged with exact false-predicate unreachable
reasons; trace absence MUST NOT prove them. Connected mutants MUST remove or
delay bootstrap for public/spawn/exec interpreters and inject duplicate,
bad-nonce and disconnected registration. Test-only bootstrap/transport MUST
NOT count as production reachability, a row, pass, authority or unreachable
proof.

#### Scenario: Every production-importing interpreter is observed first
- **WHEN** the exact public affected path crosses scheduler spawn, group-executor exec and nested broker sinks
- **THEN** complete registered topology and exact dynamic callsite occurrences equal the row-derived static projection
- **AND** any missing, late, duplicate, disconnected or ambiguous observation fails proof.

### Requirement: Affected v21 authorization MUST close runtime hosted and CI guard neighbors
Phase A MUST accept an existing runtime root only when it is a real directory
with zero entries. Any known or unknown child, dangling entry, symlink, alias,
non-directory or outside-root neighbor MUST fail before every process and later
Git/scheduler/write/mutation event with `semantic_started:0` and
`authoritative:false`.

Hosted npm/npx launcher text MUST equal exact relative
`../lib/node_modules/npm/bin/{npm|npx}-cli.js` and resolve through real
non-symlinked ancestors to the canonical target. Obfuscated traversal,
alternate spelling and every published hosted negative neighbor MUST fail
before process without fake-first or system fallback.

Canonical CI MUST parse as the exact pinned four-step YAML object. The
dependency block MUST equal its exact three commands and the final scalar MUST
be the only exact full-release invocation in every scalar/block or
execution-bearing field. Duplicate, wrapped, chained, indirect, inactive,
reordered or alternate semantics MUST fail.

#### Scenario: Closed guard neighbors reject before semantic launch
- **WHEN** a focused connected case adds any runtime entry, alternate hosted launcher spelling or second full-release occurrence
- **THEN** runtime/hosted cases record zero process and later events while CI structure fails deterministically
- **AND** no usability result, resolved target or hidden command can satisfy the guard.

### Requirement: Affected v21 authorization MUST preserve original RED and remain dormant
Before production, CI or main-spec mutation, future implementation MUST contain
only its card, same-slug OpenSpec and focused-test artifacts and retain a direct
fingerprint-first `bin/changerail-evidence capture` failure with genuine
non-zero exit, reachable reconstructable saved tree and concrete missing
production module or symbol. Later reproduction, zero-exit wrapper and terminal
evidence MUST NOT satisfy chronology.

Future v21 MUST preserve independently authored Unicode 16.0.0 `23/235`,
strict committed/staged/unstaged/untracked selection including rename/copy old
and new operands, deterministic exact-full fallback, typed scheduler and
bounded failures, connected guard mutants, full-only publication authority,
protocol-artifact non-authority, closed runner/profile/group-executor/
scheduler/broker ownership and exact source-safe four-step CI. Affected and
protocol outputs MUST remain `authoritative:false`.

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
