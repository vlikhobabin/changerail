## Context

Queue execution is only safe if every workspace, card and dependency can be
resolved before the first live child process starts. The runner already has
single-card `preflight`; plan preflight must compose that readiness check with
queue-specific validation and board re-resolution.

## Goals / Non-Goals

**Goals:**

- Add explicit `plan`, `preflight-plan` and `status-plan` commands.
- Provide a dry-run view of resolved cards, dependencies, waves and child
  runner commands.
- Fail closed on inconsistent plan/card/workspace state before live delivery.
- Write aggregate status for preflight and status inspection.

**Non-Goals:**

- This change does not launch live child delivery runs.
- This change does not implement resume or locking.
- This change does not change `run <card>` semantics.

## Decisions

- Keep command names explicit and plan-oriented. This makes queue support
  discoverable while avoiding ambiguity with the existing single-card commands.
- Resolve card identity from stable id/filename and current board lanes. This
  allows cards to move through the board without stale paths silently launching
  the wrong file.
- Perform semantic validation after schema validation. JSON Schema handles
  shape; Python validation handles DAG cycles, wave ordering and filesystem
  state.
- Write preflight aggregate status even on failure. Supervisors need a
  structured terminal outcome instead of prose-only diagnostics.

## Risks / Trade-offs

- Full preflight can be slower across many repositories -> it runs before live
  delivery by design so the queue fails before side effects.
- Card resolution by filename rejects duplicates -> this is conservative and
  forces the operator to fix ambiguous board state.
- Preflight status may become stale quickly -> live run and resume must
  re-resolve and re-validate before launching unfinished cards.

## Migration Plan

Existing users keep `preflight <card>` for a single card. Queue users create a
plan JSON and run `plan` or `preflight-plan` before `run-plan`.

## Open Questions

- None for the initial JSON-only preflight surface.
