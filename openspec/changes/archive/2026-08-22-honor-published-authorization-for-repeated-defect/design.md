## Context

`_published_investigation_authorization` already fails closed unless a clean
tracked `4.done` authorization source binds one exact published investigation
and one exact successor. Its decision object owns the LOC ceiling and protocol
allowance. The complexity guard currently consumes that valid state for LOC and
protocol, then unconditionally adds a repeated-defect reason.

## Goals / Non-Goals

**Goals:**

- make the repeated-defect branch consume the same exact validated
  authorization state;
- retain all missing, invalid, stale, mismatched, over-ceiling and disallowed
  protocol stops;
- prove both the authorized and unauthorized repeated routes with focused
  smoke tests.

**Non-Goals:**

- change the six-field authorization source or two-field successor reference;
- infer authorization from prose or introduce a CLI waiver;
- let one authorization apply to a different successor;
- weaken semantic review after deterministic admission.

## Decisions

### 1. Reuse the existing all-or-nothing authorization state

The repeated branch checks `not authorized`, where `authorized` is true only
after the exact source, investigation, successor and reciprocal relations have
all passed. No additional field or ambiguous policy layer is introduced.

### 2. Keep LOC and protocol decisions independent

A valid authorization does not bypass its own ceiling and does not permit a
protocol when its boolean allowance is false. The change removes only the
unconditional repeated reason for an otherwise valid exact successor.

### 3. Test through the public preflight command

The focused smoke creates the same tracked published graph used by existing
authorization tests. A positive card declares repeated defect with valid
authority and must reach `ready-for-llm-review`; an otherwise equivalent card
without authority must retain `investigation-required` and the repeated reason.
The test would fail on the current unconditional branch.

## Risks / Trade-offs

- A stale or mismatched source could appear to authorize a repeat -> existing
  clean-HEAD and exact graph validation remains the only route to `authorized`.
- A valid authorization could be mistaken for a global waiver -> the contract
  reiterates exact successor binding and independent ceiling/protocol checks.

## Migration Plan

1. Add RED regression cases to the focused preflight smoke.
2. Gate the repeated reason on absence of valid exact authorization.
3. Run focused and full release verification, sync specs and archive.

## Open Questions

- none
