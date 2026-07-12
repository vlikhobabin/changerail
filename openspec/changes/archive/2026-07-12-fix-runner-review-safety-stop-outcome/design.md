## Context

`bin/changerail-delivery-runner` supervises one card by launching
`$changerail-deliver <card>` through Codex JSONL mode and writing
`.runtime/changerail/delivery-runs/<run-id>/status.json`. Today it derives the
terminal outcome from the last authoritative JSONL event, or falls back to
`exit_code == 0 -> DELIVERED`.

Observed failure: `$changerail-deliver` can hit a review-gated safety stop after
fresh repeated `no-go`, write that stop in assistant text, and still exit `0`.
The runner then records `DELIVERED` even though the card is still not published.

## Goals / Non-Goals

**Goals:**

- Keep documented structured JSONL terminal events as the primary source of
  truth.
- Make fallback classification fail closed when the card is still review-gated
  and canonical verdict evidence blocks publish.
- Preserve existing behavior for non-terminal tool errors and successful
  deliveries with no blocking evidence.
- Cover the regression in `scripts/smoke-delivery-runner.py`.

**Non-Goals:**

- Parse arbitrary assistant prose or raw log text for outcome words.
- Implement multi-card queue semantics in the single-card runner.
- Change review verdict schemas or delivery-run schema shape.

## Decisions

1. **JSONL terminal event remains authoritative.**
   If stdout contains a documented terminal event or explicit terminal outcome
   field, the runner uses the last such event in stdout order. This preserves the
   existing contract and avoids a stale runtime file overriding an explicit
   terminal event.

2. **Fallback inspects structured workspace evidence only.**
   When no authoritative JSONL event exists, the runner resolves the current
   board location for the card filename and inspects
   `.runtime/changerail/reviews/<card-id>.json`. If the card is not in
   `4.done` and the verdict validates fresh as `result: no-go`, fallback outcome
   is `NO-GO`. If the verdict exists but fails validation or freshness while the
   card remains review-gated, fallback outcome is `BLOCKED`.

3. **No verdict evidence keeps the existing exit-code fallback.**
   A successful child exit with no authoritative terminal event and no
   review-blocking evidence still records `DELIVERED`; a non-zero child exit
   still records `BLOCKED`.

4. **The deliver contract documents the structured event expectation.**
   `$changerail-deliver` should emit a machine-readable terminal event on safety
   stops, but the runner still defends against older or incomplete child output
   by checking canonical review evidence.

## Risks / Trade-offs

- **Stale verdict after a real publish could look blocking** -> board location
  check treats a card already under `4.done` as delivered fallback-safe unless an
  authoritative event says otherwise.
- **Helper invocation adds post-run work** -> validation is local, cheap and
  only happens when no JSONL terminal event exists.
- **A workspace without review helper cannot classify verdict freshness** ->
  current repository provides the helper; if it is unavailable, fallback records
  `BLOCKED` only when a verdict file exists and cannot be validated.

## Migration Plan

No data migration is required. Existing runtime statuses remain historical
records. New runner invocations get corrected terminal outcome fallback
behavior.

## Open Questions

- none
