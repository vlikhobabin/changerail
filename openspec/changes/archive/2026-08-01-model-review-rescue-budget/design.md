## Context

`changerail-deliver` already has a bounded autonomous rescue policy after an
independent `no-go`: default five same-card rescue attempts, each followed by a
fresh review. The current runtime model has `review_cycle` and review-cycle
history, but it does not separately store the rescue-attempt budget. That makes
cycle `1` easy to misread as "one attempt used" and forces metrics consumers to
infer budget state from surrounding prose or local conventions.

## Goals / Non-Goals

**Goals:**

- Make review rescue budget counters explicit in structured runtime contracts.
- Preserve legacy `changerail.review-cycle-history.v1` records by making new
  fields optional.
- Keep one canonical owner for budget counters when history is available.
- Expose metrics columns and text fields for limit, used, remaining and
  exhausted state.
- Clarify that the first review is not a rescue attempt.

**Non-Goals:**

- Change the default budget of five same-card rescue attempts.
- Automate blocker fixes outside the card scope.
- Add a new durable tracked ledger for runtime review cycles.

## Decisions

1. Canonical runtime owner is review-cycle history.

   Add optional `rescue_budget` to
   `.runtime/changerail/reviews/<card-id>.history.json`. The object stores
   `limit`, `used`, `remaining` and `exhausted`. New per-cycle optional
   `same_card_rescue_attempt` records the number of same-card rescue attempts
   consumed before that review. Cycle `1` should record `0` when the writer knows
   the value.

   Alternative considered: derive budget from `len(cycles) - 1`. That breaks for
   skipped, external, abandoned or linked-card recovery paths and does not expose
   the configured limit.

2. Delivery-run status may carry a best-effort summary copy.

   Add the same optional `rescue_budget` shape under `performance.review` in
   `changerail.delivery-run.v1`. Metrics will prefer history when both sources
   exist, using the delivery-run copy only as fallback. This avoids divergent
   owner semantics while still allowing a single run record to summarize budget
   state.

3. Legacy means `unknown`, not inferred.

   If neither history nor run performance has `rescue_budget`, metrics must show
   budget fields as `unknown`. This is more conservative than guessing from
   cycle count and keeps old runtime records readable.

4. Metrics output is extended in both text and CSV modes.

   Per-run output gains stable fields:
   `rescue_budget_limit`, `rescue_budget_used`,
   `rescue_budget_remaining` and `rescue_budget_exhausted`. Existing
   `first_pass_go` stays derived from structured cycle results.

## Risks / Trade-offs

- Schema-only optional fields can be omitted by older writers. Mitigation:
  metrics reports `unknown` and smoke tests cover legacy records.
- Two locations can contain summary budget data. Mitigation: metrics prefer the
  canonical review history source whenever available.
- The first implementation does not update every possible writer to produce the
  new fields. Mitigation: contracts and metrics accept absence while new smoke
  fixtures prove the intended shape.

## Migration Plan

1. Extend schemas with optional fields.
2. Extend metrics parsing and output.
3. Update smoke fixtures for schema and metrics behavior, including legacy
   absence.
4. Update lifecycle docs and skill/reference wording.
5. Validate OpenSpec, schemas, metrics smoke, drift checks and release baseline.

## Open Questions

- none
