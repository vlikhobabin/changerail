## Context

Latest safe published authority is affected v5 authorization commit
`3588c1d3de0ddc9d8ef50e81992620fc107e4e90`. Its clean implementation successor
ended after two independent reviews and one same-card repair. Cycle 1 closed at
`10/12`; cycle 2 closed at `9/12`. The remaining findings are narrow in code
shape but repeat an older proof-completeness class: runtime-output validation
can happen after filesystem creation, and named selector limits lack connected
counterfactuals.

ChangeRail policy therefore requires an investigation/design boundary before
another implementation rescue. This change owns only the public decision,
future lineage and observable proof contract. The terminal implementation
worktree and runtime evidence are forensic-only inputs; the decision uses only
their concise reviewed finding summary, never their files or implementation.

## Goals / Non-Goals

**Goals:**

- make v6 the sole future affected implementation lineage after a separately
  published authorization;
- place runtime-output validation before `mkdir`, `mkdtemp`, selection or
  semantic execution;
- define exact absent/existing-directory and wrong-type/symlink/root/access
  states for a repository-local runtime output;
- require connected, non-noop counterfactuals for every selector path/count/
  per-stream/aggregate byte bound;
- preserve all already published affected v5 trust boundaries and retained RED
  chronology.

**Non-Goals:**

- creating authorization v6, implementation v6 or certification;
- importing or repairing terminal v5 code/tests/evidence;
- changing scheduler, broker, CI, schemas or runtime authority;
- running history, real full/affected execution, benchmark or live checks.

## Decisions

### 1. Escalate repeated proof failure into a docs-only investigation/design

The next artifact is a clean published decision rather than another same-card
or implementation rescue. It carries only source lineage, review counts,
finding classes, current hypothesis and a finite verification floor. This
satisfies the repeated-defect escalation while keeping terminal payload bytes
outside future authority.

Alternative considered: patch v5 a second time. Rejected because its declared
repair budget is exhausted and cycle-2 verdict is terminal.

### 2. Admit runtime output before creating any runtime path

Future v6 must evaluate the runtime-output descriptor inside aggregate
admission before `main()` or a helper creates `.runtime/changerail`, a run root
or scheduler state. The descriptor accepts an absent leaf only when its nearest
existing repository-local parent is a real writable/searchable directory. An
existing leaf is accepted only when it is a real non-symlink writable/searchable
directory. File, symlink, other type, escape, access uncertainty or failing
parent returns a bounded report with `semantic_started: 0`.

Alternative considered: catch `mkdir` exceptions in `main()`. Rejected because
it would bound the symptom while leaving target admission after a filesystem
mutation and disconnected from the closed descriptor inventory.

### 3. Split selector limits into named production-path oracles

The focused matrix names and reaches four distinct classes:

- per-path `MAX_PATH` in both name-status and untracked parsing;
- aggregate/deduplicated `MAX_PATHS` across all four streams;
- per-stream `MAX_GIT_BYTES` for committed, staged, unstaged and untracked;
- aggregate `MAX_GIT_BYTES` after otherwise valid bounded streams.

Each fixture first proves its valid neighbor, then injects only its named fault.
Each counterfactual changes the exact production condition and asserts that the
named fixture detects removal or weakening. Source-text presence checks,
earlier-branch failures and copied-result mutations do not count.

Alternative considered: one oversized generic selector fixture. Rejected
because it cannot prove which guard fired or whether per-stream and aggregate
limits are independently connected.

### 4. Preserve an exact two-stage v6 lineage

This decision publishes the exact six-field investigation object for future
`authorize-bounded-affected-release-profile-v6`. Only after that authorization
is published and remote-reachable may a clean v6 card use its exact two-field
reference. V6 remains `<=499` production LOC and blocks only certification.

## Risks / Trade-offs

- **Risk: another broad implementation repeats hidden proof gaps.** → The
  decision freezes a finite named matrix and requires a guard-specific mutant
  for every bound before authorization.
- **Risk: checking only the leaf misses unsafe parents.** → The contract checks
  containment, nearest existing parent type/access and leaf type/symlink state.
- **Risk: filesystem checks race with later creation.** → V6 must fail closed on
  uncertainty and keep publication authority exclusively in full release; the
  decision does not claim a portable atomic reservation protocol.
- **Trade-off: another docs-only stage delays certification.** → It prevents an
  exhausted payload from becoming authority and limits v6 to a reviewable,
  predeclared repair surface.

## Migration Plan

1. Publish this docs-only investigation/design from exact `3588c1d3...`.
2. Create and publish the separate exact v6 authorization.
3. Create v6 in a new worktree from the authorization-publishing HEAD, retaining
   a real pre-production RED tree before any production/CI/main-spec mutation.
4. Run focused/static/current checks and one fresh Sol/high implementation
   review; publish only on `GO`.
5. Resume certification only after v6 is published and remote-reachable.

Rollback is omission: until each stage is published, no successor exists and
the last safe published v5 authorization remains unchanged.

## Open Questions

- none; runtime-output states, selector limit classes, lineage and prohibited
  execution surface are closed by this decision.
