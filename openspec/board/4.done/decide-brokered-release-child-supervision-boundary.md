# Определить границу brokered release child supervision

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S4D

## Source
- Published terminal micro-fix decision
  `decide-bounded-unpublished-terminal-micro-fix-boundary`, commit
  `faacde9f86868b61da38eb9194080bc4bfdc9339`.
- Published v3 authorization
  `authorize-bounded-psutil-supervisor-micro-fix-v3`, commit
  `0d7869b6eb86b63b0f85955db87db7f1eefd116e`.
- The unpublished terminal v3 candidate is generic forensic input only. It
  supplies no code, authority, evidence, verdict, history, log, receipt or
  manifest to this decision.

## Summary
Зафиксировать отдельную архитектурную границу для broker subprocess, который
становится subreaper до запуска target и владеет только своим деревом
процессов. Это устраняет неоднозначность caller-global child discovery и
разрешает одну будущую чистую authorization/implementation lineage.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Implementation: docs-only deterministic
- Independent review: one fresh `gpt-5.6-sol`/`high` pending
- Same-card repair budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `decide-bounded-unpublished-terminal-micro-fix-boundary`
- `authorize-bounded-psutil-supervisor-micro-fix-v3`

## Blocks
- `authorize-bounded-brokered-release-child-supervisor-v4`
- `deliver-brokered-release-child-supervisor-v4`
- downstream release-loop activation remains blocked until exact v4
  publication and a later tracked refresh.

## Authorization
- Future authorization object, to be created only by the later exact
  authorization card:
  `{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- The future implementation MUST use only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}`.

## Acceptance
- Publication of this decision exhausts the earlier v3 successor path. The
  published v3 decision and authorization remain immutable historical sources
  but MUST NOT authorize creation, continuation, repair, rescue, reuse or
  publication of `deliver-psutil-backed-release-child-supervisor-v3`; exact v4
  becomes the sole conforming future implementation path.
- This decision blocks exactly the future authorization and v4 implementation;
  neither future card or executable payload exists in this delivery.
- The broker enables its child-subreaper role before target launch, starts the
  target only after readiness, and owns only processes descended from that
  broker. The caller never enables subreaper mode, scans caller-global children
  or claims a pre-existing bystander and its later descendants.
- The parent-broker protocol is bounded, versioned and fail-closed. Pipe EOF,
  malformed/truncated/duplicate messages, sequence drift, broker exception,
  target identity error, timeout or incomplete cleanup cannot report success.
- A post-launch recoverable broker fault MUST enter broker-owned cleanup before
  terminal reporting. The parent MUST keep an outer process-group containment
  path and MUST NOT publish success without a terminal broker cleanup report.
- The connected proof includes: pre-existing bystander plus later descendant,
  immediate post-launch identity fault, live-leader pipe EOF, setsid/double-fork,
  TERM-ignore/fork-during-cleanup, bounded output and protocol faults, broker
  exception, timeout arithmetic, stable cleanup and no-live/no-zombie results.
- Future v4 starts clean from its published authorization HEAD, adds at most
  499 production LOC, adds no external dependency beyond the already published
  psutil pin, and remains dormant outside focused tests until publication.
- Future v4 receives one implementation attempt, one fresh Sol/high review and
  at most one bounded same-card repair followed by one final Sol/high re-review;
  no third review, rescue or evidence reuse is permitted.
- This docs-only decision adds production/test/runtime LOC `0`, runs no history
  scan, full release baseline or live matrix, and creates no future card/code.

## Change Set
- `decide-brokered-release-child-supervision-boundary`

## Verify
- GREEN: strict target and all OpenSpec validation; exact object, reciprocal
  lineage, broker ownership, protocol/failure, proof-matrix, budget,
  future-card absence and executable-dormancy oracles.
- GREEN: JSON/TOML parsing, current-only public scan `1433/0`, source
  classification, tracked/untracked whitespace and diff check.
- GREEN: ignored manifest validation/scope and normalized ordinary/high
  preflight `ready-for-llm-review`; production/test/runtime LOC `0`.

## Archive
- `openspec/changes/archive/2026-08-26-decide-brokered-release-child-supervision-boundary/`

## Related
- `openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md`
- `openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: the same-slug decision is synchronized and archived, exact
scope and ordinary/high preflight are green, and no future authorization,
successor, code or evidence exists. The payload awaits one fresh review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-brokered-release-child-supervision-boundary`

### Why
Caller-global subreaper and psutil discovery cannot distinguish a target orphan
from a descendant created later by an unrelated pre-existing caller child.

### Goal
Publish a decision for one broker-owned process tree and one clean bounded v4
authorization/implementation lineage.

### Scope
- This card, same-slug OpenSpec artifacts, synchronized
  `changerail-release-ci` specification and archive metadata only.

### Acceptance
- Exact future authorization and successor identities, ownership boundary,
  bounded protocol, failure semantics, proof matrix and repair budget are
  represented without creating executable or successor artifacts.

### Depends On
- `decide-bounded-unpublished-terminal-micro-fix-boundary`
- `authorize-bounded-psutil-supervisor-micro-fix-v3`

### Related
- `openspec/changes/decide-brokered-release-child-supervision-boundary/`

## Log
- 2026-08-26 FF created one clean docs-only decision from published sources;
  terminal v3 material remains forensic-only and no successor was created.
- 2026-08-26 DO validated the exact broker ownership/protocol boundary and
  current public surface without running history, full baseline or live work.
- 2026-08-26 DO synchronized and archived the same-slug change; ignored
  manifest scope and normalized ordinary/high preflight passed. No review,
  commit or push was run.
- 2026-08-26 cycle-1 Sol/high review returned NO-GO R1: the active spec still
  permitted v3 alongside v4. The sole bounded repair explicitly exhausted v3
  and made the exact v4 lineage exclusive; repair budget is now `1/1/0`.
- 2026-08-26T06:44:21Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
