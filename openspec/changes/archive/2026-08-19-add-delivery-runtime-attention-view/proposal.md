## Why

Single-card delivery runs already write schema-backed runtime status, manifests,
review verdicts and retained evidence, but operators do not have one compact
read-only entrypoint that answers what a current or blocked card needs next.
This became visible during package-runner delivery where aggregate
`status-plan` helped, while single-card attention still required process-tree
inspection and ad hoc path lookup.

## What Changes

- Add a read-only single-card status/attention command to
  `bin/changerail-delivery-runner`.
- Validate the selected `changerail.delivery-run.v1` record before displaying
  it and fail closed for missing, corrupt or unsupported inputs.
- Resolve explicit status path, explicit `run_id`, and latest-run selection
  within the effective workspace.
- Print compact human-readable attention output for card, phase, result,
  `updated_at`, `terminal_reason`, related manifest, review verdict and
  retained evidence paths when each path is unambiguous.
- Surface existing manifest `runtime_pause_reasons[].summary` and
  `runtime_pause_reasons[].next_action` without deriving advice from raw logs
  or free-text agent sessions.
- Keep JSON mode machine-readable by returning either the schema-valid source
  status record or a minimal view whose separate schema need is justified in
  design before implementation.
- Preserve existing `status-plan` behavior for aggregate queue status.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: add read-only single-card runtime attention
  inspection over existing delivery-run, manifest, verdict and evidence
  contracts.

## Impact

- Affects `bin/changerail-delivery-runner`, its CLI help and argument parsing.
- Affects `scripts/smoke-delivery-runner.py` focused smoke fixtures.
- Affects public docs that describe runner status/attention workflows:
  `docs/changerail-contracts.md` and `docs/how-it-works.md`.
- Does not introduce a new scheduler, daemon, mutable runtime writer, worker
  lifecycle, browser UI or schema id by default.
