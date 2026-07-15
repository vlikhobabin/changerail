## Why

After a queue plan passes preflight, ChangeRail needs a generic supervised
runner that can execute dependency-ordered child deliveries, stop on unsafe
terminal states and resume without re-publishing already successful cards.

## What Changes

- Add live `run-plan` and `resume-plan` orchestration over the existing
  single-card delivery runner.
- Schedule cards deterministically by wave and dependency while keeping each
  workspace serial and allowing bounded parallelism across independent
  workspaces.
- Add workspace locks, fail-fast terminal outcome handling, plan fingerprint
  checks and push/no-push success validation.
- Preserve each child card's separate `changerail.delivery-run.v1` record and
  write aggregate queue status under ignored runtime state.
- Extend metrics and public docs for queue lifecycle, locks, resume,
  terminal outcomes and generic multi-workspace examples.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: add live queue execution, resume, scheduling,
  locking and success criteria.
- `changerail-delivery-observability`: read queue status plus child run records
  for aggregate metrics.
- `changerail-agent-methodology`: document orchestrator behavior for bounded
  queue execution through the tracked runner.

## Impact

- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `openspec/specs/changerail-agent-methodology/spec.md`
- `docs/how-it-works.md`
- `docs/consumer-adoption-runbook.md`
- `docs/changerail-contracts.md`
- `docs/compatibility.md`
