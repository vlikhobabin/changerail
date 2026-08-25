## Context

Published decision `7e30b08` defined one `<=499` implementation containing
both tiered release authority and bounded Windows scheduling. Published
authorization `ba5636e` correctly authorized that exact broad successor, but
did not prove that the combined payload fits its bounded implementation and
verification envelope. Two independent pre-capture audits later found the
combined unpublished implementation unsafe at that limit. Its worktree, code,
tests, diff, evidence, receipts and incomplete runs remain forensic-only.

This decision does not rewrite those published documents or retroactively mark
the failed implementation accepted. It supersedes only the executable route:
future work uses two clean authorizations and two clean implementations with an
independent scanner-v2 publication between them.

## Goals / Non-Goals

**Goals:**

- Give release authority core and Windows scheduling exact, disjoint owners.
- Bind each implementation through its own six-field authorization with a
  `500` ceiling, protocol allowance `true` and independent `<=499` limit.
- Preserve all 35 frozen semantic IDs, their digest and full-release authority
  while separating process-topology work from receipt/selector authority.
- Make A, scanner-v2, B, verify-project and release-smoke ordering explicit.
- Require one atomic terminal full baseline without retry for each executable
  successor after a fresh pre-capture audit.

**Non-Goals:**

- Reuse or repair the broad unpublished implementation.
- Change the Git-compatible structural scanner in A or B.
- Parallelize `verify-project`, review-preflight or delivery-runner smoke here.
- Disable or weaken any full-release semantic ID, public/history scan, Windows
  local case, review or publish gate.
- Make `affected` evidence authoritative, introduce a whole-suite cache, or
  enable live Windows access.
- Create successor cards/artifacts/code, sync the main spec, archive, review,
  commit, push, history scan, benchmark or full baseline during FF.

## Decisions

### 1. Scope A exclusively owns release authority core

Future authorization card
`authorize-bounded-tiered-release-authority-core` contains exactly this
six-field source object:

```json
{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its successor cites only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-tiered-release-authority-core.md","authorization_id":"authorize-bounded-tiered-release-authority-core"}
```

A owns only:

- aggregate startup toolchain admission before semantic children;
- the exact ordered 35-ID registry and digest
  `7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`;
- exact-one declared semantic ownership, affected/full selection, fallback and
  the rule that only `full-release` is review/pub/CI authority;
- atomic marker/lock/write/fsync behavior, generic capture identity and
  pre/post payload fingerprint equality;
- JSONL/manifest terminal receipt equality, schema validation and fail-closed
  preflight/publish admission;
- the canonical CI invocation of the full runner and parsed YAML/Python-AST
  ownership oracles for those authority contracts.

A preserves the existing Windows process topology. It may declare which
existing owner supplies each frozen Windows semantic result, but redundant
compatibility process invocations remain non-authoritative and are not removed
or rescheduled by A. A MUST NOT implement Windows jobs, case schemas,
process-group lifecycle, six-ID owner transition or four-process removal.

The authorization ceiling is `500`; the executable acceptance is `<=499`
production LOC against the exact published authorization HEAD recorded when
the successor is created. Protocol allowance `true` is limited to the
decision-defined profile/receipt/release authority. It excludes credential,
mutation and live authority.

### 2. Clean scanner-v2 is published between A and B

After A is reviewed, published and remote-reachable, maintainers publish the
already separate clean Git-compatible structural history scanner-v2 lineage.
Its own investigation, authorization, ceiling, protocol allowance, parser and
one-shot verification policy remain authoritative. Neither A nor B may absorb
scanner implementation or use its old forensic payload.

This ordering gives scanner-v2 an exact published tiered authority base before
B changes Windows topology. B is created only from the remote-reachable
scanner-v2 HEAD.

### 3. Scope B exclusively owns Windows scheduler and deduplication

Future authorization card
`authorize-bounded-windows-release-matrix-scheduler` contains exactly this
six-field source object:

```json
{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-windows-release-matrix-scheduler.md","successor_id":"implement-bounded-windows-release-matrix-scheduler","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its successor cites only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-windows-release-matrix-scheduler.md","authorization_id":"authorize-bounded-windows-release-matrix-scheduler"}
```

B owns only:

- the exact six-case schema and ordered Windows case registry;
- bounded `--jobs`, isolated roots/environment/output, registry-order
  aggregation and jobs-1/default parity;
- one central process-group registry and cancel/finally/TERM/KILL/reap behavior;
- malformed result, crash, timeout, oversized output and environment/root
  collision fault handling;
- transition of the six frozen Windows semantic IDs to the matrix owner;
- removal of exactly four now-redundant standalone processes: entrypoints,
  wiring Git safety, bootstrap and verify-project;
- the narrow extension of A's parsed CI ownership oracle needed to prove the
  six-ID transition and absence of those four process invocations.

B MUST NOT redefine the 35-ID registry/digest, selector, capture identity,
receipt schema, release authority, marker/lock protocol or general CI parser.
It consumes those contracts from published A and scanner-v2. Its authorization
ceiling is `500`; executable acceptance is `<=499` production LOC against the
exact published B-authorization HEAD, which descends from the exact published
scanner-v2 HEAD. Protocol allowance `true` is limited to process scheduling,
ownership transition and cleanup; it adds no credential, mutation or live
authority.

### 4. Remaining optimizations stay separate and ordered

Only after B is reviewed, published and remote-reachable may maintainers
continue with the separately authorized
`parallelize-isolated-verify-project-cases` lineage and the separate
`parallelize-isolated-release-smoke-cases` lineage covering review-preflight
and delivery-runner registries. They may consume A/B orchestration but cannot
reopen A/B ownership or merge their own completeness oracles into B.

The normative order is:

```text
A authorization -> A implementation -> clean scanner-v2 authorization/implementation
-> B authorization -> B implementation -> verify-project authorization/implementation
-> review-preflight and delivery-runner release-smoke implementation
```

Each arrow requires the previous revision to be published and
remote-reachable. A later card cannot use a dirty worktree or an unpublished
commit as its comparison base.

### 5. Executable capture is audited, atomic and non-repeatable

Before any executable successor starts its terminal capture, a fresh
Sol/`xhigh` pre-capture audit verifies exact lineage, LOC comparison base,
authority allowance, ownership boundary, focused fault coverage and absence of
forensic payload reuse. Focused deterministic checks must already be GREEN.

The unchanged audited payload then receives exactly one predeclared atomic
`full-release` capture. Atomicity requires one run/capture identity, admitted
toolchain, exact registry digest, equal pre/post payload fingerprints and one
complete terminal receipt/manifest. A failed, timed-out, malformed, stale or
changed-payload capture is terminal for that lineage. Capture retry, result
selection and same-card executable repair are all forbidden; executable
repair/retry/rescue budget is `0/0/0`. A fresh formal Sol/`xhigh` review may
start only after that sole capture is GREEN.

This docs-only rescue itself retains one bounded same-card repair because it
does not execute or certify the changed runtime authority.

### 6. The broad path remains forensic and non-authoritative

Published `ba5636e` remains immutable historical evidence that the original
decision had an authorization. After this rescue is published, no new card may
create or cite `implement-tiered-release-verification-loop` as an executable
successor. The old combined worktree and all derived code, tests, patches,
diffs, receipts, reports, evidence and runtime state remain forensic-only.

Clean A/B implementations may reproduce behavior only from published
decisions/specifications and newly written focused tests. File identity,
textual similarity, cherry-pick, patch application or evidence carry-forward
from the broad payload fails the pre-capture audit.

## Risks / Trade-offs

- **[Risk] A accidentally absorbs scheduler work.** Exact forbidden ownership
  and focused scope/LOC audit stop A before terminal capture.
- **[Risk] Temporary redundant Windows processes are mistaken for semantic
  owners.** A distinguishes declared receipt ownership from retained
  compatibility invocations; B alone removes them and changes the matrix
  owner.
- **[Risk] Two protocol allowances become generic waivers.** Each six-field
  object binds one successor and the design enumerates the only allowed
  authority; mismatch fails closed.
- **[Risk] A later optimization starts from an unpublished base.** Every stage
  requires exact remote reachability before the next authorization is created.
- **[Risk] One-shot full capture fails for environmental reasons.** The lineage
  stops and a clean rescue/replacement must diagnose the cause; observing a
  failure cannot authorize a retry.

## Migration Plan

1. Publish this docs-only rescue after strict/current-only verification and
   fresh critical review.
2. Publish A authorization, then implement A cleanly and run its one-shot gate.
3. Publish the separate clean scanner-v2 authorization/implementation lineage.
4. Publish B authorization, then implement B cleanly and run its one-shot gate.
5. Continue separately with verify-project and release-smoke successors.

Before publication, rollback removes only this unpublished docs-only change.
After publication, changing an ID, path, object, ceiling, allowance, order or
ownership requires a new tracked decision/authorization lineage.

## Open Questions

None. Scope identities, exact objects, ordering, ownership and capture policy
are fixed by this rescue.
