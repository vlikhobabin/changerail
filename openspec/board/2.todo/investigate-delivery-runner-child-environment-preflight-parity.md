# Исследование parity preflight среды дочернего delivery runner

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
deliver-ready / artifacts created or reconciled by internal ff

## Series
- none

## Series Index
- none

## Source
- Sanitized field observation from a supervised consumer package run: the
  aggregate publish-target preflight passed, while the first child delivery
  worker failed the equivalent Git remote probe inside its Codex execution
  surface before planning or implementation began.
- The child changed no tracked files, the workspace lock was released, and the
  aggregate queue stopped fail-closed with all dependent cards still pending.

## Summary
Investigate why the delivery-plan supervisor and the child Codex execution
surface can produce different publish-target results for the same repository,
branch and remote. Define a child-equivalent, freshness-bound preflight that
detects environment, sandbox and SSH-policy incompatibility before a package
run is admitted.

The investigation must preserve safety stops. Its goal is to move predictable
environment failures ahead of queue launch, retain precise structured reasons
and keep the same aggregate run resumable after an external condition is
repaired.

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

This card is decision-only. A successor that changes runner/status wire
semantics must declare that boundary separately and use the repository's
investigation-authorization route when required by complexity preflight.

## Acceptance
- Reproduce the supervisor/child parity gap with public-safe deterministic
  evidence that does not require a real credential, private remote or
  machine-local runtime record.
- Inventory the execution boundaries that can affect the result: runner
  process, launcher environment, Codex configuration, permission profile,
  sandboxed command execution, Git configuration and SSH configuration
  resolution.
- Select one canonical child-equivalent preflight design and define how its
  receipt is bound to workspace, branch, remote class, execution profile and a
  bounded freshness interval.
- Define dispatch-time revalidation so environment drift during a long serial
  queue is caught before the next child begins.
- Define a structured terminal contract that preserves an exact reason such as
  `publish_target_preflight_failed`, a sanitized failure class such as
  `ssh_config`, and retryability instead of falling back to
  `unpublished_card`.
- Separate retryable DNS, timeout and transient transport failures from
  non-retryable authentication, SSH policy and configuration failures; do not
  introduce an unbounded retry loop.
- Decide whether a consumer-scoped SSH override can be supported explicitly
  without becoming a generic default, bypassing host policy or modifying
  package-managed system SSH files.
- Bind one exact implementation successor id/path, its production LOC ceiling,
  protocol-boundary declaration and the verification floor listed below.

## Required Successor Verification Floor
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

## Non-Goals
- Implementing runner, launcher, schema, skill or test changes in this card.
- Suppressing legitimate review, authority, dirty-tree, publish or external
  safety stops.
- Mutating package-managed system SSH files or prescribing one host-specific
  permission workaround as generic ChangeRail behavior.
- Making `ssh -F /dev/null`, a particular remote provider or a credential
  mechanism the cross-project default.
- Reading, copying or committing authentication material, local runtime logs or
  consumer-specific paths.

## Change Set
- `investigate-delivery-runner-child-environment-preflight-parity`

## Verify
- RED/GREEN product evidence: N/A for this decision-only investigation; the
  investigation must instead retain a deterministic reproducer and prove that
  it distinguishes supervisor-only success from child-equivalent success.
- `./bin/openspec validate
  investigate-delivery-runner-child-environment-preflight-parity --strict`
- `./bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check` plus an explicit whitespace scan for untracked files.
- Fresh independent ordinary/high review before scoped publish.

## Archive
not started

## Related
- `bin/changerail-delivery-runner`
- `bin/codex`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `docs/consumer-adoption-runbook.md`

## Result
not started

## Next
- Run `$chrl-deliver
  openspec/board/2.todo/investigate-delivery-runner-child-environment-preflight-parity.md`.

## Change 1: `investigate-delivery-runner-child-environment-preflight-parity`

### Why
The aggregate runner currently proves publish-target readiness in the
supervisor process, but the delivery worker repeats that gate inside a Codex
execution surface whose environment and SSH configuration resolution may
differ. A green package preflight can therefore be followed immediately by a
predictable child safety stop.

### Goal
Publish a public-safe architecture decision for child-equivalent preflight,
freshness, dispatch-time revalidation, failure taxonomy and resumability, then
bind one bounded implementation successor.

### Scope
- Produce a deterministic environment-parity reproducer.
- Map supervisor, launcher and sandbox execution boundaries.
- Compare viable preflight placement and receipt-binding designs.
- Specify structured failure classification and bounded retry behavior.
- Select and bind the exact implementation successor and verification floor.
- Do not modify production runner behavior in this investigation.

### Acceptance
- The decision explains the observed parity gap without relying on private
  consumer evidence.
- The selected design detects the gap before aggregate work begins and catches
  later environment drift before dispatch.
- Structured status retains the real sanitized blocker and retryability.
- The successor contract preserves fail-closed publish and resume behavior.

### Depends On
- none

### Related
- `openspec/changes/investigate-delivery-runner-child-environment-preflight-parity/`

## Log
- 2026-08-21T07:06:02Z created from a sanitized supervised package-runner
  preflight-parity finding; implementation and tests intentionally deferred to
  a separate ChangeRail successor.
