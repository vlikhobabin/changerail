## 1. Metrics Output

- [x] 1.1 Derive displayed `total_tokens` from input plus output tokens when explicit totals are absent.
- [x] 1.2 Render cached input, uncached input, output and reasoning token breakdowns in text and CSV output.
- [x] 1.3 Render per-run slow-command summary and review-cycle timeline from structured status/history data.

## 2. Regression Coverage

- [x] 2.1 Extend `scripts/smoke-delivery-metrics.py` fixtures for derived token totals and token breakdowns.
- [x] 2.2 Extend metrics smoke coverage for slow-command summary, review-cycle count and unknown optional timing fields.

## 3. Specs And Verification

- [x] 3.1 Sync delta specs into `openspec/specs/changerail-delivery-observability/spec.md` and `openspec/specs/changerail-contracts/spec.md`.
- [x] 3.2 Run `python3 scripts/smoke-delivery-metrics.py`.
- [x] 3.3 Run `./bin/openspec validate report-delivery-performance-metrics --strict`.
- [x] 3.4 Run `git diff --check`.
