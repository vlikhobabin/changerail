## Context

Published authorization v20 at
`e04dc38582490339d55876acc512623a0547a2ec` remains the last safe executable
boundary. The unpublished v20 successor received a fresh `NO-GO` with six
blockers. Five are closed guards, but two expose architectural gaps: scheduler
v1 accepts one argv per task while the immutable v18 inventory contains one
physical owner with three sequential argv, and the required dynamic activation
projection must start at public `run_profile` and equal exact callsite rows.

The published v18 proof inventory remains the only immutable external anchor.
Published scheduler v1 and broker v5 cannot be changed by the future profile.
The next implementation must remain within 499 production LOC and certification
must stay dormant.

## Goals / Non-Goals

**Goals:**

- preserve 35 semantic IDs, 30 physical owners and one scheduler result per
  owner while supervising every immutable sequential-group command;
- distinguish scheduler transport identity from immutable payload argv without
  allowing proof inventory to become runtime input;
- validate the complete scheduler summary before pass or authority;
- derive static and dynamic activation projections from the same public affected
  callsite identities;
- close the runtime-root, hosted-launcher and CI duplicate guards;
- publish a docs-only v21 lineage before executable authorization.

**Non-Goals:**

- no scheduler/broker source or wire-schema modification;
- no v20 payload/evidence reuse;
- no inventory copy, regeneration or runtime parsing;
- no receipt, cache, publication authority or affected authority;
- no history, real full/affected benchmark, live matrix or certification run.

## Decisions

### 1. Composite owners use an outer transport and inner exact broker calls

A direct task keeps its immutable argv as the scheduler command. A sequential
group uses one separately typed repository group-executor command as its
scheduler transport, so scheduler v1 still emits exactly one result for the
physical owner. The transport carries only owner ID and expected production
registry digest; it carries no raw argv and cannot read the proof inventory.

The executor imports the production registry, checks the digest and exact
`sequential-group` kind, and then calls published broker v5 once per original
argv in immutable order. It accepts only the exact closed passing broker tuple.
On the first failure or malformed result it exits non-zero and never starts a
later argv. The scheduler's outer broker bounds the executor itself, while each
inner broker bounds the actual immutable command and descendants.

This preserves one physical scheduler result and makes every original command
identity externally observable at a published broker boundary. A synthesized
`python -c` loop or direct `subprocess.run` is rejected because neither exposes
the immutable argv to the broker.

Alternative rejected: split the group into three scheduler tasks. That changes
30 physical owners/results to 32 and breaks exact ownership. Alternative
rejected: teach scheduler v1 a commands array. That mutates a published
dependency outside profile authority.

### 2. Summary admission duplicates the published envelope oracle locally

Profile authority cannot trust a scheduler protocol object merely because it
has `status: pass`. The profile validates exact top-level fields, version,
requested jobs, result-list type/cardinality/order and each exact published
result field/cross-field passing tuple against the selected physical plan.
Only that local closed validation contributes to requested full-release pass.

This does not redefine scheduler semantics: it is a consumer-side admission
oracle over the published schema. Unknown, duplicate, reordered or malformed
rows fail locally even if a substituted callable returns them.

### 3. One exact-context worklist owns both projections

The observer parses runner, profile, group executor and exact-digest
scheduler/broker sources. It assigns canonical row IDs using source digest,
function owner, AST path and source span. A finite abstract interpreter starts
only from `run_profile("affected", base=<known-docs-base>, jobs=1,
environment=<production-shaped>)` and carries concrete profile/base/jobs/
environment/supervisor facts through calls and predicates. The internal profile
`main` becomes reachable only from this path; the injected non-None supervisor
branch stays cataloged with a predicate-backed unreachable reason.

The dynamic child starts hooks before import and runs that exact public call in
a disposable real-Git repository. Only harmless exact selected commands are
materialized. Python 3.11 instruction positions plus caller code identity map
Python/C calls to AST spans; audit/profile hooks map raw process and POSIX sinks
the same way. Ambiguous or unmapped events fail. Static and dynamic call/sink
multisets compare bidirectionally by canonical row ID and occurrence, rather
than comparing only function entries or sink classes.

Before starting the public child, the harness creates a test-only
`sitecustomize.py` and binds an `AF_UNIX/SOCK_DGRAM` collector under its
disposable root. It passes a fresh 128-bit nonce, socket path, hard deadline,
maximum datagram/event/byte bounds and exact expected source-digest catalog via
the fixture environment. Inherited `PYTHONPATH` causes every Python interpreter
on the exact path to load the bootstrap before production imports: the public
child, multiprocessing manager/resource helpers and `spawn` workers, and the
group executor launched by the outer broker. The executor transport uses the
already admitted Python without `-S`, so it cannot bypass `sitecustomize`.

Bootstrap sends exactly one closed registration datagram before installing an
import guard plus opcode/profile/audit hooks. Registration carries nonce,
pid/ppid, bounded argv-derived role and per-process sequence zero. Subsequent
datagrams carry monotonic sequence and canonical caller code/span inputs, never
self-authored row IDs. `os.register_at_fork` emits a linked child registration
before an inherited fork child can emit a production event. The collector
matches registrations to observed spawn/exec/fork topology and independently
maps bounded event fields to source-derived rows after all children exit.

The proof fails on event-before-registration, missing/late/duplicate
registration, bad nonce, sequence gap/replay, unknown role that imports a
production source, disconnected pid/ppid edge, unexpected interpreter,
source-digest mismatch, malformed/oversized datagram, event/byte overflow,
deadline or collector loss. Focused mutants remove or delay bootstrap separately
for the public child, one scheduler spawn and the executor exec, and inject
duplicate/bad-nonce/disconnected registration. Test-only bootstrap variables,
registrations and transport are never read by production and cannot count as a
dynamic row, pass, authority or evidence of unreachable production behavior.

Alternative rejected: seed internal `main` or maintain a second edge list.
Either can pass while the public path or a callsite is disconnected.

### 4. Remaining guards use exact closed forms

An existing runtime root must be a real directory with zero directory entries;
checking only known task names is insufficient. Hosted npm/npx symlinks must
equal the one canonical relative string derived from the setup-node layout,
not merely resolve to the canonical target. The CI oracle parses the YAML
object and requires the dependency block to equal three exact commands and the
final scalar to equal one exact full runner; every other command-bearing scalar
or block is forbidden.

## Risks / Trade-offs

- **[Risk] Nested supervision complicates cleanup.** The outer broker owns the
  executor process group and each inner broker must return exact cleanup state;
  focused failure-at-index cases prove no later start and no survivor.
- **[Risk] Transport identity could become a second inventory.** It contains
  only owner ID and digest; exact payload argv remain solely in the production
  registry and immutable proof anchor.
- **[Risk] Bytecode positions vary across Python versions.** The proof pins the
  repository's admitted Python `>=3.11` position API and fails closed when an
  event has no unique AST span.
- **[Risk] Spawn/exec loses interpreter-local hooks.** Inherited test-only
  `sitecustomize` registers every interpreter before production import, while
  the bounded nonce-bound collector rejects incomplete process topology.
- **[Risk] Disposable dynamic execution could drift toward real release work.**
  The fixture admits only a known docs path and harmless exact fixture commands;
  it never invokes history/full/live/certification surfaces.
- **[Risk] Added executor consumes the LOC ceiling.** The future authorization
  retains 500 and implementation retains 499; preflight measures the complete
  production addition before review.

## Migration Plan

1. Publish this docs-only investigation from authorization v20 HEAD.
2. Publish one docs-only v21 authorization with the exact nested boundary,
   proof architecture, lineage and LOC ceiling.
3. Start a clean v21 implementation from authorization-publishing HEAD and
   retain a new genuine original RED before executable mutation.
4. Implement guards, executor, summary admission and public-entry projection;
   synchronize and archive before one fresh ordinary/high review.
5. Publish only on fresh GO. Certification remains the next separate card and
   owns the only history/full/scenario evidence sequence.

Rollback before publication removes only the unpublished successor. Published
scheduler/broker and the v18 proof inventory never change.

## Open Questions

- none; unknown composite identity, broker tuple, scheduler row, callsite,
  runtime entry, launcher spelling or CI execution field fails closed.
