## 1. Runtime Contracts

- [x] 1.1 Extend `schemas/changerail-review-cycle-history.schema.json` with optional `rescue_budget` and per-cycle `same_card_rescue_attempt`.
- [x] 1.2 Extend `schemas/changerail-delivery-run.schema.json` with optional `performance.review.rescue_budget`.
- [x] 1.3 Update schema smoke fixtures to cover known budget values and legacy absence.

## 2. Metrics

- [x] 2.1 Update `bin/changerail-delivery-metrics` to read budget counters from review history first and delivery-run performance as fallback.
- [x] 2.2 Add text, JSON and CSV output fields for rescue budget limit, used, remaining and exhausted.
- [x] 2.3 Update delivery metrics smoke coverage for known budget values, fallback behavior and legacy `unknown` output.

## 3. Methodology And Docs

- [x] 3.1 Clarify in lifecycle docs that initial review is `review_cycle: 1` and consumes zero same-card rescue attempts.
- [x] 3.2 Update review/deliver skill wording and review verdict reference so agents record and interpret rescue budget counters consistently.
- [x] 3.3 Update public contract docs for the new review-cycle history fields and metrics output.

## 4. Verification

- [x] 4.1 Run `openspec validate model-review-rescue-budget --strict`.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.3 Run `python3 scripts/smoke-delivery-metrics.py`.
- [x] 4.4 Run `python3 scripts/smoke-wiring-discovery.py`.
- [x] 4.5 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.6 Run `python3 scripts/run-release-baseline.py`.
