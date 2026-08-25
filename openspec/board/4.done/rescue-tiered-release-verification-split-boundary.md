# Спасти tiered release verification через split boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R6-I

## Source
- Published tiered decision `investigate-tiered-release-verification-loop-boundary`,
  commit `7e30b08`.
- Published broad authorization `authorize-bounded-tiered-release-verification-loop`,
  commit `ba5636e`.
- Recovery for unpublished `implement-tiered-release-verification-loop` after
  two independent pre-capture audits found the combined `<=499` scope unsafe.
  Its worktree, code, diff, evidence and incomplete runs remain forensic-only.

## Summary
Разделить broad verification implementation на два independently authorized
bounded scopes: A владеет release authority core, B владеет Windows process
scheduler и duplicate removal. Clean scanner-v2 публикуется между A и B;
verify-project и оба release-smoke набора продолжаются только после B. Не
ослаблять coverage и не переносить failed prototype implementation.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: fresh `gpt-5.6-terra`/`high`
- Independent review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair: at most one fresh `gpt-5.6-terra`/`high`
- Re-review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair/rescue budget limit/used/remaining: `1/0/1`, exhausted
  `false`

## Depends On
- `investigate-tiered-release-verification-loop-boundary`
- `authorize-bounded-tiered-release-verification-loop`

## Blocks
- `authorize-bounded-tiered-release-authority-core`
- `implement-tiered-release-authority-core`
- `authorize-bounded-windows-release-matrix-scheduler`
- `implement-bounded-windows-release-matrix-scheduler`
- `authorize-bounded-parallel-verify-project-cases`
- `parallelize-isolated-verify-project-cases`
- `authorize-clean-git-compatible-structural-history-scan-v2`
- `deliver-clean-git-compatible-structural-history-scan-v2`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- Current broad implementation remains unpublished/forensic-only; no code,
  tests, diff, evidence, receipt or runtime state is reused.
- Scope A `implement-tiered-release-authority-core` exclusively owns bounded
  aggregate toolchain admission, exact 35-ID registry/digest, affected/full
  selection and authority, atomic marker/lock/fsync, generic capture ID,
  pre/post fingerprint, JSONL/manifest receipt equality, schema/preflight/pub
  gate, canonical CI full runner and parsed YAML/Python-AST oracles.
- Scope B `implement-bounded-windows-release-matrix-scheduler` exclusively owns
  six case schemas/registry, jobs/isolation/order, central process-group registry,
  cancel/finally/TERM/KILL/reap, malformed/crash/timeout/oversize/env faults,
  six-ID owner transition and exact four-process dedupe.
- A authorization uses exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-authority-core.md","successor_id":"implement-tiered-release-authority-core","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- B authorization uses exactly
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md","investigation_id":"rescue-tiered-release-verification-split-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-windows-release-matrix-scheduler.md","successor_id":"implement-bounded-windows-release-matrix-scheduler","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- Each implementation is `<=499` production LOC against its exact published
  authorization HEAD recorded as its comparison base; neither protocol
  allowance grants credential, mutation or live authority.
- B depends on published A and clean scanner-v2 HEAD; it extends A's parsed CI
  ownership oracle but cannot duplicate receipt, selector, registry authority
  or CI parser.
- Required remote-reachable order is A authorization/implementation, separate
  clean scanner-v2 authorization/implementation, B authorization/implementation,
  separate verify-project authorization/implementation, then the separate
  review-preflight and delivery-runner smoke successor.
- Each executable successor requires fresh Sol/xhigh pre-capture audit, exactly
  one atomic terminal full baseline, repair/retry budget `0/0/0`, and fresh
  formal Sol/xhigh review.
- Scanner-v2 remains tied to Git-header rescue investigation; verify-project and
  release-smoke successors remain separately authorized/scoped.
- Docs-only decision, production/test/runtime LOC 0; no history/full baseline.

## Change Set
- `rescue-tiered-release-verification-split-boundary`

## Verify
- Strict target/capability/all and exact scenario/lineage ownership.
- JSON/TOML/current scan/classification/diff/whitespace/manifest/preflight.
- No history scan, benchmark or full baseline.

## Result
DO complete: one docs-only rescue change synced and archived. Exact split
ownership, A/B authorization objects, ordering and forensic-only broad path
passed current-only deterministic verification. Production/test/runtime LOC: 0.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-tiered-release-verification-split-boundary`

### Why
The combined authority/scheduler scope reached the LOC ceiling while connected
fault oracles still exposed fail-open behavior.

### Goal
Publish exact separate ownership boundaries for safe smaller implementations.

### Scope
- Decision/card and release-CI contract only.
- Two future authorization/implementation lineages.
- Production/test/runtime LOC: 0.

### Acceptance
- A/B ownership is exact and disjoint, with two exact six-field objects,
  independent `<=499` limits and immutable ordering through scanner-v2,
  verify-project and both release smokes.
- Each future executable lineage receives a fresh Sol/`xhigh` pre-capture audit
  and exactly one atomic full-release capture without repair or retry.
- Broad unpublished implementation payload remains forensic-only and absent.

### Depends On
- `investigate-tiered-release-verification-loop-boundary`
- `authorize-bounded-tiered-release-verification-loop`

### Related
- `openspec/changes/archive/2026-08-25-rescue-tiered-release-verification-split-boundary/`

## Log
- 2026-08-25T08:30:00Z split rescue created after two pre-capture NO-GO audits;
  broad unpublished implementation remains forensic-only.
- 2026-08-25T08:45:00Z FF prepared exactly one apply-ready same-slug docs-only
  rescue change with disjoint A/B ownership, two exact future authorizations,
  immutable successor order and one-shot audit/capture policy. No successor,
  implementation, main-spec sync, history scan, baseline, archive, review,
  commit or push was created.
- 2026-08-25T09:00:00Z DO synced exactly four modified release-CI requirements,
  archived the one same-slug change, and completed current-only strict/OpenSpec,
  JSON/TOML, public-surface, whitespace, manifest and preflight handoff checks.
  No executable successor, history scan, benchmark, full baseline, review,
  commit or push was run.
- 2026-08-25T09:10:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
