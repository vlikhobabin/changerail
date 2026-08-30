## Context

Published authorization v19 at
`e3dbdd494f7a8d3dbd10e3b70b9b034d3079b416` remains the latest safe boundary.
Terminal unpublished implementation v19 ended initial fresh review at `6/10`,
used its sole same-card repair, then ended terminal fresh review at `7/10` with
repair budget `1/1/0`. Only three validated blocker summaries cross the
forensic boundary:

1. runtime/task-root validation followed six version probes, including Git;
2. hosted cache accepted a symlinked ancestor and its proof oracle did not
   derive the executable target from independently parsed CI;
3. the complete activation row set and the finite edge worklist were separate,
   leaving reachable owners outside the compared projection.

The terminal v19 card, OpenSpec, source, tests, CI/main-spec mutation, manifest,
verdicts, logs and raw evidence are not design inputs. V20 remains docs-only and
uses only published v18/v19 investigations and authorizations, immutable v18
proof inventory, integration decision, scheduler v1 and accumulated release-CI
specification.

## Goals / Non-Goals

**Goals:**

- define one explicit aggregate admission barrier before every subprocess, Git,
  scheduler, write-intent or mutation event;
- validate runtime and selected task roots together with repository, registry,
  operand, origin and package identity before the barrier;
- derive hosted `node`, `npm` and `npx` expected targets from independently
  parsed pinned CI plus externally observed canonical filesystem layout;
- reject symlinked directory ancestors while allowing only a bounded,
  contained npm/npx final launcher chain required by canonical Node layout;
- derive complete row reachability and static call/sink projection from the
  same context-sensitive activation worklist;
- compare the full observed rows with an independent catalog and map dynamic
  witnesses to the exact reachable row IDs;
- preserve the accumulated floor and freeze one clean v20 lineage.

**Non-Goals:**

- no production, focused-test, CI workflow, runtime, scheduler or broker edit;
- no terminal v19 payload/evidence access or reproduction;
- no live GitHub runner, live matrix, affected execution, full baseline,
  benchmark, history scan or certification check;
- no new receipt, cache, protocol, marker or affected publication authority;
- no v20 copy or regeneration of the published v18 proof inventory.

## Decisions

### 1. Aggregate admission is a two-phase fail-closed state machine

Future v20 admits work through two ordered phases. Phase A is process-free. It
parses and validates the immutable registry and typed operands, resolves the
exact real repository root, checks committed/staged/unstaged/untracked input
grammar, validates requirements/package metadata without executing tools,
classifies declared origins, and validates the runtime root plus every selected
task root. All filesystem checks use bounded explicit paths and `lstat`-style
component identity; missing, occupied, dangling, symlinked, non-directory,
outside-root or aliased roots reject the aggregate.

Only one successful Phase-A result may cross the admission barrier. Phase B may
then issue bounded version/usability probes for already admitted executable
identities. A Phase-B failure still returns a bounded non-authoritative report
and cannot enter Git collection, scheduler or mutation. There is no helper that
probes eagerly while building Phase-A data, and no Git-specific exception.

Future proof installs audit/profile/process/write observers before production
import and records monotonically ordered external events. For every Phase-A
negative neighbor, including an occupied selected task root, the exact result
must have `semantic_started:0`, zero process events before rejection and zero
later Git/scheduler/write/snapshot events. A separately authored stage catalog
maps each admitted field to Phase A or B; production ordering/ledgers cannot
certify themselves.

Alternative rejected: probe executables first and defer only Git collection.
The required boundary is before every process event, not merely before the
first repository query.

### 2. Hosted targets come from CI plus component-safe filesystem observation

The hosted oracle parses the exact canonical four-step workflow as data. It
requires the pinned checkout/setup-node actions, exact `node-version: "20"`,
canonical runner/platform, absence of alternate environment/execution fields
and the sole explicit full-release step. CI yields the allowed major and
layout; it does not hardcode a patch version in the proof.

The clean child creates one real absolute disposable `RUNNER_TOOL_CACHE` and
supplies architecture before production import. The independent oracle walks
`node/<20.x.y>/<arch>/bin` without following directory symlinks, requires one
strict SemVer `20.x.y` and one architecture, and uses `lstat` on every component
from the declared cache through `node`, version, architecture and `bin`.
Relative roots, a symlink at any directory ancestor, hard links/aliases that
break unique identity, traversal or containment uncertainty reject before any
usability probe.

`node` must be the canonical regular executable. `npm` and `npx` may use only
the canonical bounded final launcher form needed by the observed setup-node
layout: each hop is relative, cycle-free, count-bounded and resolves inside the
same real version subtree through non-symlinked directory ancestors to the
expected npm CLI target. The proof derives the exact final target and argv from
the parsed CI row and observed filesystem, independently from production
descriptors, markers, results and `_SYSTEM_ORIGINS`.

Separate clean-child cases for `node`, `npm` and `npx` place an exact-version
successful fake for that token first in `PATH`. External process observation
must match the oracle's canonical target/argv and show the fake unused.
Negative neighbors cover every root component, duplicate/wrong version,
architecture/token, broken/absolute/traversing/escaping/cyclic launcher,
zero/multiple target, fake-first selection and hosted-to-system fallback. Every
failure occurs in Phase A with zero process and later semantic events.

Alternative rejected: hardcode `20.19.1` in the fixture or accept the first
matching directory. Both disconnect proof from the pinned CI contract.

### 3. One context-sensitive worklist owns row reachability and projection

Future proof independently parses exact affected runner/profile and
exact-digest scheduler/broker sources. It first materializes the complete
syntax multiset of imports, bindings, functions, predicates, calls and raw
sinks. It then runs one finite context-sensitive worklist seeded only by the
exact public affected entrypoint, exact production task/jobs arguments and
`supervisor=None`.

Worklist state is `(canonical row ID, qualified callable, normalized bound
arguments, predicate facts)`. Every transfer records its predecessor row and
an allowlisted transfer-rule ID. Import aliases, assignments, parameters,
receivers, returns and predicate refinements propagate only finite exact sets;
unknown, empty or ambiguous reachable binding, runtime rebind, dynamic lookup
or unsupported call form fails closed.

The worklist writes reachability, exact reason, predecessor and transfer rule
back to each observed row. The static reachable call/sink projection is defined
only as a deterministic projection of rows marked reachable by that same
worklist. There is no separately maintained literal edge list and no hardcoded
owner exclusion. Owner closure requires every reachable function owner to have
a reachable entry row and at least one predecessor chain to the seed; every
reachable call/sink row must appear in projection, and no projected row may be
unreachable.

The immutable `ACTIVATION_CATALOG` is separately authored and cannot be
generated or completed from observer/worklist output. Canonical multiset
equality is bidirectional over source/digest, kind/item/owner/AST path,
normalized context and predicates, finite callee/receiver set, predecessor,
transfer rule, reachability/reason and sink class. Counts, hashes or uniqueness
are only preliminary structure checks.

Alternative rejected: keep a complete row catalog and validate dynamics against
a smaller hand-authored edge catalog. That is the disconnected proof shape this
investigation eliminates.

### 4. Dynamic evidence maps to the exact reachable rows

A separate clean child installs profile/audit/process hooks before public
runner import and invokes the exact public affected entrypoint with the admitted
production argument row. The harness maps qualified calls, scheduler arguments
and broker raw sinks to canonical observed row IDs using source identity and
callsite, without replacing production functions, constants, calls or results.

After an explicit immutable interpreter/harness exclusion set, the dynamic
multiset must equal the static reachable call/sink projection derived from the
worklist rows. The path must include affected runner/profile, scheduler default
with `supervisor=None` and published broker sinks. Every reachable owner and
call/sink row needs a predecessor chain and dynamic witness. The injected
non-None supervisor branch remains present in syntax, observed rows and
catalog, but the worklist marks it unreachable from an exact false predicate;
trace absence alone does not provide that reason.

An extra/missing row, owner, predecessor, transfer, callsite or sink; an
alternate wrapper; a latent-to-reachable transition; or dynamic evidence that
cannot map uniquely to one row fails before affected evidence admission.

### 5. V20 preserves the published floor and one successor lineage

Future authorization must contain exactly:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-admission-hosted-activation-closure-v20.md","investigation_id":"investigate-affected-release-profile-admission-hosted-activation-closure-v20","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v20.md","successor_id":"implement-bounded-affected-release-profile-v20","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

It depends exactly on this investigation, the integration decision, scheduler
v1 and authorization v19 and blocks only implementation v20. Future
implementation uses only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v20.md","authorization_id":"authorize-bounded-affected-release-profile-v20"}`,
depends on those four predecessors plus authorization v20, blocks only
certification, begins at authorization-publishing HEAD, retains a new genuine
fingerprint-first missing-module/symbol RED and adds at most 499 production
LOC.

The published v18 proof inventory remains the sole immutable command/operand
anchor with counts `35/30/48`, semantic/full digests, total ownership and exact
static migration. Unicode `23/235`, strict four-stream selection, typed
scheduler, connected guard mutants, full-only authority, protocol-artifact
non-authority and exact source-safe four-step CI remain additive gates.

## Risks / Trade-offs

- **[Risk] Phase A accidentally performs a process probe through a helper.**
  Pre-import audit/process hooks and a stage catalog reject any event before the
  barrier, including indirect helpers.
- **[Risk] Canonical npm/npx uses a symlink.** Directory ancestors remain
  symlink-free; only an explicitly bounded contained final launcher chain is
  allowed and independently resolved.
- **[Risk] CI `node-version: "20"` lacks a patch.** The oracle derives major
  from CI and requires exactly one strict matching filesystem version rather
  than inventing a patch.
- **[Risk] The worklist becomes self-certifying.** The full row catalog is
  separately authored and every worklist output field compares
  bidirectionally; dynamic hooks independently witness reachable rows.
- **[Risk] Proof scope exceeds the 499-line production ceiling.** Proof code is
  test-only; authorization preflight rejects an over-ceiling production diff.

## Migration Plan

1. Publish this docs-only investigation after strict/current-only verification
   and one fresh ordinary/high review.
2. Publish a separate docs-only authorization v20 from the investigation HEAD.
3. Create implementation v20 only from authorization HEAD and retain a new
   original RED before any production/CI/main-spec mutation.
4. Implement the Phase-A barrier, component-safe hosted oracle proof and unified
   activation worklist/projection, then obtain fresh ordinary/high review.
5. Only after remotely published implementation create final critical
   certification; its single history/full/scenario budgets remain unchanged.

Rollback before publication removes only this unpublished docs-only payload.
After publication, a changed admission stage, hosted grammar, activation row
schema, lineage or ceiling requires a new tracked decision.

## Open Questions

- none; an unknown stage, filesystem identity, launcher shape, binding,
  transfer, owner or trace mapping fails closed and requires a new decision.
