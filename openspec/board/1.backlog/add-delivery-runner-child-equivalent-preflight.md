# Add delivery runner child-equivalent preflight

## Status
1.backlog

## Owner
ChangeRail maintainers

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Successor bound by the investigation
  `openspec/board/4.done/investigate-delivery-runner-child-environment-preflight-parity.md`.

## Summary
Implement child-equivalent publish-target preflight for delivery-plan
admission and dispatch so predictable child Git/SSH environment failures are
detected before aggregate work begins, before workspace locks are created and
before delivery children are launched.

The implementation must preserve existing fail-closed publish, auth,
clean-tree, upstream and explicit `--no-push` behavior. It should reuse
existing delivery-run and delivery-plan status fields and stay within the
investigation's no-new-protocol boundary.

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

If delivery needs more than 300 added production-counted LOC or new required
runner/status wire fields, stop and create a separate published authorization
source bound to the investigation and this exact successor.

## Depends On
- `openspec/board/4.done/investigate-delivery-runner-child-environment-preflight-parity.md`

## Acceptance
- Supervisor pass plus child-equivalent fail blocks before aggregate queue
  launch and before a workspace lock or delivery child is created.
- Supervisor and child-equivalent pass admit the queue without weakening the
  existing clean-tree, authority, auth, upstream or remote checks.
- Dispatch-time revalidation catches environment drift before a later card.
- SSH configuration and permission diagnostics are sanitized, classified as
  non-retryable and never expose credentials, identity paths or remote
  userinfo.
- Retryable DNS/timeout failures remain bounded and record attempt counts.
- Child terminal markers survive into single-card and aggregate structured
  status without the `unpublished_card` fallback.
- `resume-plan` continues the same aggregate run after fresh preflight while
  delivered cards remain skipped and pending dependencies remain ordered.
- Explicit `--no-push` retains its existing local-only semantics; remote
  failure must not silently select it.
- POSIX child-environment parity coverage does not regress supported Windows
  runner behavior or custom launcher behavior.
- The payload adds no more than 300 production-counted LOC and does not add new
  required runner/status wire fields without a separate published
  authorization.

## Change Set
- none yet

## Verify
- not started

## Archive
not started

## Related
- `openspec/board/4.done/investigate-delivery-runner-child-environment-preflight-parity.md`
- `bin/changerail-delivery-runner`
- `bin/codex`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `docs/consumer-adoption-runbook.md`
- `openspec/specs/changerail-delivery-runner/spec.md`

## Result
not started

## Next
- After the investigation card is published in `4.done`, triage this successor
  into `2.todo` only if the no-protocol, <=300 production-LOC boundary still
  holds.

## Log
- 2026-08-21T09:30:27Z backlog successor created by
  `investigate-delivery-runner-child-environment-preflight-parity`; production
  implementation intentionally deferred.
