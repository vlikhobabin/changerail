## Context

Scheduler v1 and broker v5 are published and compatible but dormant. The
published v18 proof inventory is the sole immutable description of 35 semantic
IDs, 30 physical owners and 48 typed operands. Authorization v22 requires a
clean implementation that binds selected work through actual descriptor-bound
exec and proves the complete public activation path.

## Goals / Non-Goals

**Goals:**

- preserve the exact published inventory and implement deterministic strict
  four-stream selection with exact-full fallback;
- activate the scheduler only through a public profile runner;
- bind one admission row to every physical plan owner and every inner member;
- execute verified native executable/operand objects by FD with closed env;
- prove complete syntax/worklist/catalog/dynamic topology and runtime ancestry;
- keep affected and protocol surfaces non-authoritative.

**Non-Goals:**

- no certification evidence or timing decision;
- no history, real workspace full/affected run or live matrix;
- no v22 inventory copy and no terminal v21 payload/evidence reuse;
- no new receipt, review, publish or certification authority.

## Decisions

### 1. Registry and selector are closed production data

The profile module owns canonical semantic rows and physical owners matching
the published v18 artifact. It validates both canonical digests at import.
Affected selection consumes bounded NUL-delimited committed, staged, unstaged
and untracked records, preserves both rename/copy operands and maps only exact
allowlisted ownership. Any uncertainty selects the canonical full plan with a
bounded reason; requested affected remains non-authoritative.

### 2. Admission is an additive scheduler/broker path

Legacy `run_plan` and `supervise` are unchanged. `run_admitted_plan` validates
one closed ordered admission row per physical task, opens every executable and
operand no-follow, verifies component identities, seals the canonical nested
table in a bounded memfd and calls `supervise_admitted`. Direct rows carry one
member. Composite rows carry an outer executor and ordered inner members while
remaining one scheduler result.

The admitted broker forks a bounded capture child and performs atomic
`os.execve(executable_fd, physical_argv, closed_env)`. A CLOEXEC status pipe
distinguishes exec success from pre-start error. Script/launcher plans use a
pinned native interpreter FD and inherited `/proc/self/fd/<n>` operands; no
target is rediscovered through PATH or reopened after validation.

### 3. Runtime ancestry fails before observation or semantics

The runner accepts only an absolute lexical direct child of an admitted real
anchor. It opens the anchor and target with directory-FD `O_NOFOLLOW` walks,
compares device/inode/type/mount identity, rejects repetitions, aliases,
neighbors and non-empty roots, then repeats the check immediately before
scheduler reservation. Admission failure returns closed non-authoritative
diagnostics with `semantic_started:0` and performs no Git/process/write work.

### 4. Proof truth is independent and complete

The focused proof parses the published inventory and exact pinned four-step CI,
constructs its own disposable real-Git/tool filesystem and derives expected
logical/physical rows without production descriptors. It observes exec audit,
FD identity, memfd bytes/seals and post-exec target and exercises the complete
pre-start negative matrix plus post-open rename stability.

A separately authored immutable `ACTIVATION_CATALOG` annotates every import,
binding, function, predicate, call and raw sink in the exact source set. The
observer builds an independent finite public-seeded context worklist. A clean
pre-import `sitecustomize` child records nonce-bound registration and raw
events across public/spawn/group/exec roles. Full rows and normalized
static/catalog/dynamic reachable projections compare bidirectionally.

### 5. CI and authority stay singular

Canonical CI parses as the exact pinned checkout/setup-node/install/full-runner
four-step object. It contains one explicit full-release invocation and no
affected, scheduler, broker or semantic bypass. Only successful requested
full-release over exact full inventory can be authoritative; affected,
admission, scheduler and proof outputs are always non-authoritative.

## Risks / Trade-offs

- Descriptor execution is Linux-specific; admission fails closed elsewhere.
- Complete row catalog is intentionally sensitive to source changes; any drift
  requires explicit proof/catalog review.
- Fail-closed selection can run the full inventory for uncertain input, trading
  speed for completeness without gaining authority.

## Migration Plan

1. Retain the genuine fingerprint-first missing-module RED.
2. Add profile/admission code and focused disposable proofs.
3. Apply the exact four-step CI activation and synchronize this delta.
4. Archive, run deterministic preflight, obtain fresh independent review and
   publish scoped commits. Certification remains a later card.

## Open Questions

- none.
