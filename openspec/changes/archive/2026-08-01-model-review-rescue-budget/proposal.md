## Why

Delivery now distinguishes initial review, post-review same-card rescue attempts
and later re-review cycles in policy, but structured runtime records and metrics
do not expose the rescue budget counters directly. Operators currently have to
infer used and remaining attempts from prose or raw cycle count.

## What Changes

- Add an optional review rescue budget object to review-cycle history records.
- Add matching best-effort review rescue budget fields to delivery-run
  performance records.
- Update delivery metrics to report first-pass GO and rescue budget counters
  from structured fields, rendering legacy records as `unknown`.
- Clarify lifecycle docs and skills so the first review is cycle `1` but not a
  consumed rescue attempt.
- Preserve the existing fail-closed policy when the same-card rescue budget is
  exhausted.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: review-cycle history and delivery-run contracts expose
  optional same-card rescue budget counters.
- `changerail-delivery-observability`: metrics output reads and reports
  structured rescue budget counters with legacy compatibility.
- `changerail-agent-methodology`: lifecycle wording defines initial review,
  rescue attempt and re-review cycle consistently.

## Impact

- `schemas/changerail-review-cycle-history.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `bin/changerail-delivery-metrics`
- smoke fixtures for schema validation and metrics output
- lifecycle docs and skill/reference wording for delivery review rescue policy
