## Why

Remote-push preflight failures can be transient, but current single-card and
queue runner status preserves only a generic sanitized failure detail. After a
later successful manual proof, the operator cannot safely resume without
reconstructing which failure happened and whether it was retryable.

## What Changes

- Add fail-closed remote publish-target diagnostics for SSH config, DNS, auth,
  missing remote branch, timeout and unknown remote failures.
- Record bounded, sanitized preflight evidence in
  `changerail.delivery-run.v1` status without adding duplicate top-level
  aliases such as `id`, `status` or `started_at`.
- Allow limited retry/backoff only for transient remote preflight classes.
- Add explicit single-card resume semantics that accepts prior status, repeats
  a full fresh preflight and continues only after the publish target is proven.
- Propagate compact remote preflight diagnostics through queue preflight/status
  and keep auth/branch uncertainty fail-closed.
- Document the operator diagnostics and resume contract.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: remote publish-target preflight
  classification, retry/backoff, single-card resume and queue propagation.
- `changerail-contracts`: structured delivery-run preflight evidence fields
  and delivery runner contract documentation.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `docs/compatibility.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
