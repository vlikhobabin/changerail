## Why

After long delivery runs, operators need the metrics helper to explain token
usage, slow commands and review-cycle timing without custom Python scripts
against raw runtime logs. Existing output omits derived total tokens when the
runner observes only input and output tokens, and it does not expose the new
performance summary.

## What Changes

- Teach `bin/changerail-delivery-metrics` to derive `total_tokens` from
  `input_tokens + output_tokens` when an explicit total is absent.
- Display cached input, uncached input, output and reasoning token breakdowns
  when status records provide them, with unavailable values shown as `unknown`.
- Add text and CSV output for slow-command summaries and review-cycle timing.
- Extend smoke coverage for metrics output, runner timing capture and contract
  schema validation.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-observability`: metrics output includes performance,
  usage breakdown and review-cycle timeline reporting.
- `changerail-contracts`: delivery-run fixtures validate optional performance
  and usage breakdown fields.

## Impact

- `bin/changerail-delivery-metrics`
- `scripts/smoke-delivery-metrics.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-contract-schemas.py`
- `docs/changerail-contracts.md`
