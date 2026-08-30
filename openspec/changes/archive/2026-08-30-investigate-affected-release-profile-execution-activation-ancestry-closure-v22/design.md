## Context

Published authorization v21 at
`f04b99d99555585703538eb9722be4c8e64cf6a6` is the last safe boundary.
Terminal unpublished implementation v21 received a fresh `NO-GO` with five
blockers: admitted origin/environment state did not constrain the broker
process boundary, the activation catalog contained no row-level worklist
result, the dynamic oracle did not prove exact static topology, runtime
ancestry stopped before aliased ancestors, and the attempt entered a prohibited
real fallback diagnostic without retained process evidence.

Only those class summaries and validated `5/11`, `5/0/0` counters cross the
forensic boundary. The terminal implementation is not an implementation or
proof source. Published scheduler v1, broker v5, the v18 proof inventory and
the accumulated release-CI spec are the only executable/contract sources.

## Goals / Non-Goals

**Goals:**

- bind each admitted environment and executable/operand identity to the exact
  descriptor-bound exec that starts semantic work;
- keep legacy scheduler/broker entrypoints and result schemas compatible while
  authorizing one additive, closed admitted-execution transport;
- compute row-level context reachability from the public affected call and
  compare it with a separately authored fully annotated catalog;
- map every raw cross-process production event and prove exact normalized
  static/catalog/dynamic activation topology;
- reject every symlink, alias, mount or outside-anchor runtime ancestry before
  process or semantic work;
- force a new disposable focused episode with genuine original RED and no
  workspace fallback, history, live or certification execution.

**Non-Goals:**

- no terminal v21 payload, evidence or runtime state reuse;
- no weakening or replacement of immutable v18 command identity;
- no authority for scheduler, broker, admission, proof or affected artifacts;
- no receipt/cache/publication behavior;
- no history, real full/affected benchmark, live matrix or certification run;
- no authorization or implementation card in this investigation.

## Decisions

### 1. Additive admitted transport reaches an atomic descriptor-bound exec

Origin validation cannot constrain execution while scheduler workers pass raw
tokens to legacy `supervise` and broker `Popen` inherits ambient environment.
V22 therefore authorizes one additive
`changerail.release-admitted-execution.v1` transport. Legacy `run_plan` and
`supervise`, their accepted inputs, defaults, output tuples and authority-free
semantics remain compatible.

The additive scheduler entrypoint accepts the existing ordered physical plan
plus an ordered one-to-one physical-owner admission table. A direct-owner row
contains one member. A composite row contains one outer group-executor record
and the exact ordered member record for every immutable inner argv. Every
closed record binds owner/member ID, exact logical argv, a normalized physical
launch plan, executable/component identities, any script/module operand
identities, exact closed environment and canonical record digest. The row
digest commits to the ordered outer/member digests. Missing, extra, reordered,
cross-owner or partially bound members fail before a worker starts.

After validation, the scheduler worker opens every executable and operand with
no-follow descriptor operations and verifies its pinned identity. It writes
the closed nested table to a bounded Linux `memfd`, applies all write/grow/
shrink/seal seals and retains the verified executable/operand FDs. Direct work
passes its FDs to the additive broker. Composite work passes the sealed table,
outer-executor FD and every ordered member FD through the outer admitted exec;
the group executor receives only owner ID, registry/admission digests and the
numeric sealed-bundle FD. It verifies seals, digests, FD identities and the
production registry mapping before any inner call. It never reconstructs an
inner target, component chain or environment from ambient state.

The admitted broker does not use path-based `Popen`. It reuses the published
capture/cleanup/result semantics around a bounded fork/pipe process adapter,
then the target child invokes FD-capable `os.execve(fd, argv, env)` (the
platform `fexecve`/`execveat(AT_EMPTY_PATH)` primitive) on the already-verified executable FD
with the exact closed environment. A close-on-exec status pipe makes the parent
emit `started` only after successful exec; any validation or exec error is a
bounded pre-start failure. Renaming or replacing the path after open cannot
change the executed object.

Logical inventory argv remains exact. When its first token is a script or
launcher, independent normalization MUST NOT ask the kernel to re-resolve a
shebang or `/usr/bin/env`: the physical plan pins a native interpreter FD plus
each script/module operand FD and substitutes only `/proc/self/fd/<passed-fd>`
operand references. Both logical argv and the deterministic physical argv/FD
mapping are closed and independently compared. Native commands have no operand
rewrite. Thus every executable dependency is descriptor-bound without turning
proof inventory into runtime input.

A direct owner executes its one member through this primitive. A composite
owner remains one scheduler task/result: the admitted group executor applies
the exact inherited member record and FDs to the additive broker once per
immutable logical argv in order. The first non-passing inner tuple prevents all
later commands. All inherited FDs are bounded, enumerated, close-on-exec except
where the exact next exec needs them, and closed after their one owner/member.

The independent oracle derives every direct/outer/inner logical and physical
row separately from the immutable inventory, pinned CI and fixture filesystem.
It observes the `os.exec` audit/syscall inputs, FD `fstat` identities, sealed
bundle and post-exec `/proc/<pid>/exe` identity rather than a production marker.
It also proves legacy `Popen` is not reached by admitted work. A changed target,
environment, member, bundle, fake-first PATH selection or raw-token legacy call
therefore fails before an unadmitted target can start.

Alternative rejected: clear `os.environ` around legacy `run_plan`. This is
process-global, races concurrent work and still does not bind executable
identity at Popen. Alternative rejected: a wrapper executable. The outer
wrapper itself would start under ambient broker state and could hide the
semantic target. Alternative rejected: change the legacy result schema. No new
result field is needed for execution binding. Alternative rejected: reopen and
check immediately before `Popen(executable=<path>)`; that remains a path
check/use race and cannot meet the pre-start guarantee.

### 2. Full annotations come from a real context-sensitive worklist

The static observer enumerates every import, binding, function, predicate,
call and raw sink in runner/profile/group-executor/admitted-transport sources
and exact-digest legacy scheduler/broker sources. Canonical row identity is a
tuple of source path/digest, qualified owner, AST field/index path, node kind
and span. A finite worklist starts only at public
`run_profile("affected", base=<known-docs-base>, jobs=1,
environment=<production-shaped>)` and carries normalized bound arguments,
receiver/callee sets and predicate facts through an allowlisted transfer table.

Every row receives an explicit predecessor, transfer, reachability and reason.
Reachable bindings must resolve to one finite non-empty set, and each reachable
row must have a complete predecessor chain to the seed. Unreachable rows need
an evaluated false predicate or an exact unsupported-by-seed reason; generic
sentinels such as `cataloged`, `pending`, `unknown` and empty annotations are
invalid.

A separately authored immutable `ACTIVATION_CATALOG` lists every row and every
field. The catalog is not generated by production or by the observer. Full
observed rows, worklist annotations and catalog compare bidirectionally on each
field. This makes a digest or count insufficient and exposes every missing,
extra, rebound or latent row.

### 3. Raw events are complete; topology equality uses canonical activation keys

Exact raw occurrence counts inside selector/poll/deadline loops vary with
scheduling and are not a stable reachability property. V22 does not discard
them: the collector retains every bounded raw production occurrence, and every
one must map uniquely to a catalog row. It then normalizes only repeated
iterations with the identical canonical activation key:

`(process role, row ID, normalized context, predicate facts, callee/receiver)`.

The static reachable projection, catalog reachable projection and normalized
dynamic key multiset compare exactly and bidirectionally. A repeat with a
different role, row, context, predicate or target is a different key and
cannot be collapsed. Each timing-loop row also has a finite raw-count bound;
overflow fails. Thus timing jitter cannot make proof flaky, while a new
callsite, alternate wrapper, hidden sink or conflicting duplicate remains an
extra topology key.

Before any production import, a disposable child installs a test-only
`sitecustomize`, nonce-bound Unix datagram collector, import guard,
opcode/profile/audit hooks and at-fork registration. Registration precedes
events in the public interpreter, scheduler spawn children and group-executor
exec. The collector validates closed schemas, source digests, roles, per-process
sequence and complete pid/ppid/spawn/fork/exec topology. Test bootstrap fields
may be present in the admitted proof environment but production does not read
them; they never count as a row, pass or authority.

Alternative rejected: compare function-entry counts or a hand-selected edge
list. Both can pass with a missing public callsite. Alternative rejected: exact
poll-loop counts. They measure timing, not activation identity.

### 4. Runtime roots are proven from an exact anchor by directory FDs

Phase A admits an exact real runtime anchor and only one lexically direct child
candidate. It rejects relative spellings, `.`/`..`, alternate normalization and
any lexical/real mismatch. Starting from an opened anchor FD, it walks the
candidate with `openat`-equivalent directory-FD operations using
`O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`, compares `fstat` with the expected
`(device,inode,type,mount)` prefix and rejects repeated identities or any mount
transition below the anchor.

The final root must be a real empty directory. Unknown and dangling entries,
symlinked ancestors, bind/alias transitions, non-direct descendants and
outside-anchor identities all fail with `semantic_started:0`. The same FD chain
is checked again immediately before scheduler reservation, closing a stale
lexical proof.

Alternative rejected: `Path.resolve()` plus parent equality. A symlinked or
aliased ancestor can resolve inside or outside after the lexical parent check.

### 5. A clean episode is part of the proof, not a repair detail

The v22 implementation starts from its future published authorization HEAD and
creates a new direct fingerprint-first missing-module/symbol RED before any
production, CI or main-spec mutation. All executable proof runs occur in
disposable real-Git fixtures with an exact harmless command allowlist and
retained process/event evidence. Test discovery and workspace diagnostics are
static and cannot call public affected or exact-full fallback.

The harness aborts on any command outside the allowlist before broker launch.
History, real full/affected execution or benchmark, live matrix and
certification remain forbidden. The prior non-conforming episode cannot be
reclassified or reused.

## Risks / Trade-offs

- **[Risk] Additive transport changes published scheduler/broker source.** The
  future authorization names this exact bounded exception; legacy entrypoints
  and result schemas receive compatibility/mutation tests and no authority.
- **[Risk] Machine identities are runtime-specific.** They remain ephemeral
  admission rows and evidence, never tracked inventory or protocol authority.
- **[Risk] A large activation catalog is expensive to review.** Row identity,
  forbidden sentinel checks, bidirectional field equality and source digests
  make the review mechanical; the fixture stays test-only and immutable.
- **[Risk] Event normalization could hide behavior.** Only identical activation
  keys collapse; every raw occurrence must map, conflicting repeats remain
  distinct and per-row raw bounds fail closed.
- **[Risk] Component paths can change after Phase A.** Worker revalidation
  opens exact objects, and admitted execution uses those same FDs; later path
  replacement cannot redirect exec. Sealed nested rows bind every composite
  member before the outer executor starts.
- **[Risk] The 499 LOC ceiling remains tight.** Additive APIs reuse published
  validation, scheduling, capture and cleanup primitives; preflight measures
  the complete production addition.

## Migration Plan

1. Publish this docs-only investigation from authorization v21 HEAD.
2. Publish one docs-only v22 authorization with the exact transport, proof,
   ancestry, chronology, lineage and 500 authorization ceiling.
3. Start one clean v22 implementation from authorization-publishing HEAD and
   retain the new original RED before executable mutation.
4. Implement the additive transport, profile, guards and focused proof within
   499 added production LOC; synchronize and archive before fresh review.
5. Publish only on fresh GO. Certification remains the only owner of history,
   full baseline and three requested affected scenarios.

Rollback before publication removes only the unpublished successor. The
published v18 inventory and legacy scheduler/broker entrypoints remain valid.

## Open Questions

- none; any admission, row, topology, ancestry or execution episode outside the
  closed contracts fails before authority or publication.
