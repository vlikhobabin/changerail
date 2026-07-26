## Why

The delivery-plan UX changes span CLI output, generated plan files and durable
operator docs. Focused smoke coverage and examples are needed so release
baseline catches regressions before operators hit first-run queue setup.

## What Changes

- Extend delivery-runner smoke coverage for compact child failure reporting.
- Add smoke coverage for generated plan validation through `plan` and
  `preflight-plan`.
- Add lightweight docs expectation checks for launcher semantics and optional
  repo-local launcher wording.
- Run public-surface checks for the tracked payload.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: smoke and docs coverage for queue-plan operator
  UX.

## Impact

- `scripts/smoke-delivery-runner.py`
- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `docs/board-and-two-agent-feature-flow.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `scripts/public-surface-scan.py` verification output only; no schema change
  expected.
