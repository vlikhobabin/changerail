## Context

Published decision `decide-accelerated-release-loop-integration-boundary`
splits release acceleration into scheduler, affected activation and final
certification. Scheduler v1 must be authorized and published separately before
its implementation card is created.

## Goals / Non-Goals

**Goals:**

- Bind exact scheduler v1 to its published decision and future successor.
- Preserve v5-only supervision, bounded execution and structural dormancy.
- Make successor absence and zero executable LOC machine-checkable.

**Non-Goals:**

- Do not create or implement scheduler v1.
- Do not activate runner, CI, profiles, receipts or publish authority.
- Do not run history, full release baseline or live matrix evidence.

## Decisions

### 1. Authorization is exact and singular

This authorization alone contains exactly one six-field object:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Future implementation depends on both published sources and uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

It starts from the authorization-publishing HEAD and adds at most 499
production LOC.

### 2. Scheduler owns execution but no release authority

The future scheduler accepts one fully prevalidated immutable plan of 1..64
unique task IDs, commands, timeouts and isolated roots. It validates the whole
plan before launch, accepts jobs 1..4, dispatches every task exactly once
through published connected broker v5, cancels outstanding tasks after a
terminal failure and aggregates exactly one result per task in registry order.

Every child retains v5's 8192-byte combined-output cap. Scheduler summary is at
most 64 KiB and contains no raw child output. Invalid, duplicate, missing,
unknown, incomplete or over-bound input/result state fails closed.

Scheduler owns no Git selector, semantic inventory, release profile,
runner/CI/receipt or review/publish authority. Only later exact affected-profile
implementation may activate it.

### 3. This delivery is docs-only

The successor card and code remain absent. This authorization changes only its
card, same-slug artifacts, synchronized main spec and archive metadata, with
production/test/runtime LOC 0. It runs no history, full baseline or live
matrix.

## Risks / Trade-offs

- **Authorization duplicates decision limits** -> exact repetition makes drift
  machine-detectable and binds the successor without widening scope.
- **Implementation remains unavailable after this card** -> this is required
  separation; the successor starts only from the published authorization HEAD.

## Migration Plan

1. Validate, independently review and publish this authorization.
2. Only then create exact `implement-bounded-release-semantic-scheduler-v1`.

## Open Questions

None. Selector, activation, certification and any widened protocol belong to
their separately authorized cards.
