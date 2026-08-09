## Why

Maintainers need stable quality evidence across maintenance reports, triage
state and proposal decisions before adding broader automation. Existing delivery
metrics are intentionally scoped to delivery runs, so maintenance quality needs a
separate rollup contract.

## What Changes

- Add `changerail.maintenance-quality-rollup.v1` JSON output for maintenance
  quality metrics.
- Add `changerail.maintenance-proposal-decision.v1` ignored runtime input
  records for accepted and rejected fix proposal decisions.
- Add `bin/changerail-maintenance quality` with human-readable, JSON and stable
  CSV output.
- Report catalog coverage, open/resolved/accepted/waived findings,
  stale/generated findings, duplicate-card prevention, instruction bytes,
  time-to-triage and accepted/rejected proposals.
- Render missing optional metrics as `unknown`, not zero.
- Keep `bin/changerail-delivery-metrics` columns and behavior unchanged.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-repository-knowledge`: repository maintenance exposes structured
  quality rollup metrics over lifecycle reports, state, triage and proposal
  decision evidence.

## Impact

- Affected public surfaces: `bin/changerail-maintenance`,
  `bin/changerail-maintenance.cmd`, `scripts/changerail_maintenance.py`, new
  maintenance schemas, fixtures, repository-knowledge specs and smoke tests.
- Proposal-decision records remain ignored runtime evidence and do not authorize
  or apply fixes.
