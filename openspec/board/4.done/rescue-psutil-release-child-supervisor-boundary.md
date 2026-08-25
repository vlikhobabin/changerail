# Спасти psutil-backed release child supervisor boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S2

## Source
- Exact published S v1 authorization
  `authorize-bounded-release-child-supervisor-v1`, commit
  `94fe74681d88ec234ef90e55c6359d54fb71abae`.
- Exact published investigation
  `rescue-release-process-supervisor-boundary`, commit
  `ea7eb235b95356ecd86afc98a0db8b48ea6243e9`.
- The unpublished S v1 implementation exhausted cycle 2 and an unpublished S2
  authorization attempt failed its prerequisite. Both are forensic input only:
  this card retains no code, diff, evidence or local identifier from either.

## Summary
Зафиксировать отдельную docs-only decision для будущего psutil-backed S2 child
supervisor: новый published authorization source может появиться только после
этого решения, а его единственный successor должен быть bounded,
platform-neutral и структурно dormant до последующего refresh после публикации
S2.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: docs-only deterministic
- Independent review: cycle 1 fresh `gpt-5.6-sol`/`high` `NO-GO`, sole R1;
  cycle 2 fresh `gpt-5.6-sol`/`high` pending
- Same-card repair/rescue budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `rescue-release-process-supervisor-boundary` (published
  `ea7eb235b95356ecd86afc98a0db8b48ea6243e9`)
- `authorize-bounded-release-child-supervisor-v1` (published
  `94fe74681d88ec234ef90e55c6359d54fb71abae`)

## Blocks
- `authorize-psutil-backed-release-child-supervisor-v2`
- `implement-psutil-backed-release-child-supervisor-v2`
- downstream H4/I3/W1/R3/A3 authorization and implementation work until S2 is
  published and a later refresh re-establishes their dependencies.

## Authorization
- Future S2 authorization object, to be created only in the later exact
  authorization card:
  `{"investigation_card":"openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md","investigation_id":"rescue-psutil-release-child-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-psutil-backed-release-child-supervisor-v2.md","successor_id":"implement-psutil-backed-release-child-supervisor-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- The future authorization MUST depend on this published decision and block
  only `implement-psutil-backed-release-child-supervisor-v2`; the future
  implementation MUST depend on both this decision and that authorization and
  use only the authorization's exact two-field published-source reference.

## Acceptance
- The decision blocks future `authorize-psutil-backed-release-child-supervisor-v2`
  and `implement-psutil-backed-release-child-supervisor-v2`, preserves the
  exact six-field future object, and requires reciprocal decision,
  authorization and implementation dependencies.
- Future S2 pins `psutil==7.1.0` consistently in runtime, development,
  bootstrap and admission surfaces. It uses a bounded stdlib
  `selectors`/`prctl` adapter and MUST NOT assume a writable cgroup.
- Future S2 accepts distinct positive `execution_timeout` and
  `cleanup_timeout`; its total wall-clock budget is at most
  `execution_timeout + cleanup_timeout + 1.0s`, where the fixed `1.0s` covers
  report/setup overhead only. Cleanup failure is terminal.
- Every psutil error fails closed. Process identity is `(pid, create_time)`;
  recursive child discovery requires two consecutive empty
  `children(recursive=True)` identity sets before cleanup succeeds; the second
  consecutive empty scan is the success threshold, not a failure cap. The
  exact process/identity/cleanup item caps `128` unique identities, `128`
  descendants per scan and `32` cleanup scans are inclusive allowed maxima;
  exactly `128`/`128`/`32` remain allowed and only a value greater than its cap
  is terminal. A premature success after
  fewer than two consecutive empty scans is rejected.
- S2 remains structurally dormant with no release baseline or CI activation.
  H4/I3/W1/R3/A3 remain blocked until S2 is published and a later refresh
  explicitly re-establishes their downstream authorization and dependencies.
- The old S v1 authorization is a one-successor source and cannot authorize
  v2; the failed unpublished S2 authorization attempt is not reusable.
- The connected proof matrix covers dependency/object lineage, pins/admission,
  bounded POSIX/psutil cleanup, timeout arithmetic, negative cgroup and
  dormant-wiring assertions without live, history, full-baseline, review,
  commit or push evidence.
- This decision creates no future authorization or successor card, adds
  production/test/runtime LOC `0`, and tracks only generic forensic summaries.

## Change Set
- `rescue-psutil-release-child-supervisor-boundary`

## Verify
- GREEN: strict target, `changerail-release-ci` and all OpenSpec validation;
  exact object/reciprocal relation/absence/ownership oracle; `.mcp.json` JSON
  and `.codex/config.toml` TOML parsing.
- GREEN: current-only public-surface scan, source classification, tracked and
  explicit-untracked whitespace, manifest validation/scope and normalized
  ordinary/high preflight after archival handoff.
- This sole repair ran no history scan, full release baseline, live execution,
  new review, commit or push.

## Archive
- `openspec/changes/archive/2026-08-25-rescue-psutil-release-child-supervisor-boundary/`

## Related
- `openspec/board/4.done/rescue-release-process-supervisor-boundary.md`
- `openspec/board/4.done/authorize-bounded-release-child-supervisor-v1.md`
- `openspec/changes/archive/2026-08-25-rescue-psutil-release-child-supervisor-boundary/`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO завершен: одна docs-only decision change синхронизирована в
`changerail-release-ci` и архивирована. Exact S2 lineage, psutil-backed
boundary, connected proof matrix, dormant downstream refresh gate и generic
forensic-only provenance сохранены. Production/test/runtime LOC: `0`. Future
authorization and successor cards/code remain absent. Cycle-1 fresh ordinary/
high review returned one R1 `NO-GO` on inclusive-cap/stable-empty semantics;
the sole docs repair is complete and cycle-2 fresh independent review is
pending.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-psutil-release-child-supervisor-boundary`

### Why
S v1 authorization cannot authorize a replacement after its unpublished
implementation exhausted cycle 2, and the unpublished attempted S2
authorization did not satisfy its prerequisite.

### Goal
Publish one docs-only decision that defines the exact future S2 authorization,
bounded psutil supervision contract, connected proof matrix and dormant
downstream refresh gate without creating any successor authority payload.

### Scope
- This card, same-slug proposal/design/release-CI delta/tasks, synchronized
  main spec and archive metadata only; production/test/runtime LOC `0`.

### Acceptance
- Exact object, blocks and reciprocal future dependencies are retained; old v1
  and failed unpublished authorization paths cannot authorize S2.
- Future S2 pin, selector/prctl, no-cgroup, timeout, fail-closed identity,
  inclusive-cap and second-empty-success-threshold contracts are complete.
- H4/I3/W1/R3/A3 remain dormant and blocked pending S2 publication plus later
  refresh; no future authorization or successor card/code exists.

### Depends On
- `rescue-release-process-supervisor-boundary`
- `authorize-bounded-release-child-supervisor-v1`

### Related
- `openspec/changes/archive/2026-08-25-rescue-psutil-release-child-supervisor-boundary/`

## Log
- 2026-08-25 card created from the exact published S v1 authorization base;
  unpublished failed paths are generic forensic input only.
- 2026-08-25 FF created one same-slug docs-only decision change with proposal,
  design, full release-CI delta and tasks; future authorization and successor
  cards remain absent.
- 2026-08-25 DO synchronized the exact `changerail-release-ci` requirements,
  archived only this same-slug docs-only change and completed strict/current
  verification. No history/full/live execution, review, commit or push
  occurred.
- 2026-08-25 cycle-1 fresh ordinary/high review returned one R1 `NO-GO`:
  clarify that 128/128/32 are inclusive maxima and that the second consecutive
  empty scan is the success threshold. The sole repair is complete; budget is
  `1/1/0` exhausted and cycle-2 review remains pending.
- 2026-08-25T22:25:24Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
