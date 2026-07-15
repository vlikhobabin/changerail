## Context

Once a queue plan is valid, ChangeRail needs supervised execution across
independent workspaces while each card still goes through the existing
single-card runner. The queue runner is responsible for dependency order,
workspace serialization, fail-fast behavior, resume and aggregate reporting.

## Goals / Non-Goals

**Goals:**

- Add `run-plan` and `resume-plan` live orchestration.
- Keep one child `changerail.delivery-run.v1` record per card.
- Enforce per-workspace serialization and bounded cross-workspace parallelism.
- Implement workspace locks and safe resume checks.
- Extend metrics/docs for queue status and child records.

**Non-Goals:**

- No force-push, destructive git cleanup or automatic stale-lock removal.
- No replacement of `$changerail-deliver` or `run <card>` for single-card work.
- No mandatory YAML parser or external scheduler service.

## Decisions

- Launch child deliveries through the existing single-card runner. This keeps
  review/publish semantics and status compatibility centralized.
- Treat `max_parallel` as a global cap and hard-code workspace parallelism to
  one for live cards. The plan may declare per-workspace parallelism, but values
  above one fail validation for now.
- Use lock files under ignored queue runtime state. Locks prevent two queue
  children in one repository and give diagnostics for stale locks without
  deleting them automatically.
- Make resume fingerprint-aware. Resume compares the current plan fingerprint
  and repository/card state with aggregate status before deciding what can be
  skipped or retried.
- Accept success according to push mode. Push-enabled success requires published
  card location, clean repository and `HEAD == upstream`; `--no-push` success
  requires committed clean tree with the expected ahead-of-upstream state.

## Risks / Trade-offs

- Running children in parallel can still create operator load -> `max_parallel`
  defaults conservatively and can be lowered to one.
- Upstream comparison may fail in offline environments -> the status records the
  blocked check rather than guessing success.
- Stale locks can interrupt legitimate recovery -> the runner reports evidence
  and requires explicit operator action instead of unsafe automatic deletion.

## Migration Plan

Existing delivery-run records remain valid. Queue users add aggregate queue
status under ignored runtime state. Metrics can read queue status when present
and fall back to existing run/history inputs otherwise.

## Open Questions

- Future versions may add explicit lock cleanup commands once safe stale-lock
  criteria are proven through tests.
