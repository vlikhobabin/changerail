## Why

Queue delivery must fail closed before the first live child run if the plan,
workspace state or card resolution is inconsistent. Operators also need a dry
run that shows exactly which single-card runner commands would execute.

## What Changes

- Add explicit plan-oriented runner commands for listing, dry-running,
  preflighting and reading queue status.
- Validate the declarative plan against the tracked schema and semantic queue
  invariants before any delivery child can launch.
- Resolve cards by stable filename/card id across board lanes and reject
  missing, duplicate, ambiguous or canceled cards.
- Validate dependency DAGs, wave barriers and concurrency settings.
- Write structured aggregate status for preflight and status inspection without
  scraping raw logs.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: add plan/list, dry-run, preflight-plan and
  status-plan behavior for queue plans.

## Impact

- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `docs/how-it-works.md`
- `docs/consumer-adoption-runbook.md`
- `docs/changerail-contracts.md`
