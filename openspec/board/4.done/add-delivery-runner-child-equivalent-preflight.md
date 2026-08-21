# Add delivery runner child-equivalent preflight

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `add-delivery-runner-child-equivalent-preflight`

## Verify
- `python3 scripts/smoke-delivery-runner.py`
- `bin/openspec validate --all --strict`
- `git diff --check`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/run-release-baseline.py`

## Archive
`openspec/changes/archive/2026-08-21-add-delivery-runner-child-equivalent-preflight/`

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
Runner now records `terminal_reason: publish_target_preflight_failed` for
single-card publish-target preflight failures, preserves the child status
receipt in aggregate plan status, blocks aggregate admission before locks or
child launch, and revalidates child-equivalent preflight immediately before
dispatching later unresolved cards.

Focused delivery-runner smoke, strict OpenSpec validation, whitespace checks,
public-surface scan and the complete 36-step release baseline pass.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `add-delivery-runner-child-equivalent-preflight`

### Why
Supervisor-side publish-target preflight can pass while the delivery child
would later fail under its effective Git/SSH environment. The runner needs a
child-equivalent gate before aggregate work and before each dispatched child.

### Goal
Add child-equivalent publish-target preflight to delivery-plan admission and
per-card dispatch without adding required runner/status wire fields.

### Scope
- delivery-plan admission before aggregate queue launch;
- delivery-plan dispatch-time revalidation before launching a later child card;
- single-card structured status preservation for child preflight terminal
  markers;
- sanitized diagnostics for SSH/config/permission failures and bounded retry
  behavior for retryable network failures;
- no change to explicit `--no-push` local-only semantics.

### Acceptance
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

### Depends On
- `openspec/board/4.done/investigate-delivery-runner-child-environment-preflight-parity.md`

### Related
- `openspec/changes/archive/2026-08-21-add-delivery-runner-child-equivalent-preflight/`

## Log
- 2026-08-21T09:30:27Z backlog successor created by
  `investigate-delivery-runner-child-environment-preflight-parity`; production
  implementation intentionally deferred.
- 2026-08-21T12:00:00Z triaged into `2.todo`; published investigation is in
  `4.done`, no-new-protocol and <=300 production-LOC boundary still holds.
- 2026-08-21T12:05:00Z OpenSpec artifacts created and validated; card moved
  to `3.inprogress` for implementation.
- 2026-08-21T12:37:10Z implemented child-equivalent admission/dispatch
  preflight, synced specs/docs, archived the change and passed focused runner
  smoke plus the complete release baseline.
- 2026-08-21T12:58:40Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
