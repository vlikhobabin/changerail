## Why

The delivery runner writes raw child JSONL streams, but those events do not have
runner-observed timestamps and cannot be used after the fact to compute command
durations or slow-command summaries. The runner should capture enough timing
metadata during execution to explain long delivery runs from `status.json`.

## What Changes

- Record a machine-readable event timeline or equivalent status summary while
  streaming child JSONL output.
- Capture runner-observed timestamps for child events and start/end/duration
  data for command executions when the child stream exposes command lifecycle
  events.
- Aggregate command counts, slowest commands, agent message counts, file-change
  counts, review-cycle timing and publish latency into the delivery status
  performance summary when those signals are available.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: runner behavior includes performance summary
  capture for non-interactive delivery runs.
- `changerail-delivery-observability`: observability data is produced from
  structured runtime evidence rather than free-text scraping.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- runtime status under `.runtime/changerail/delivery-runs/`
