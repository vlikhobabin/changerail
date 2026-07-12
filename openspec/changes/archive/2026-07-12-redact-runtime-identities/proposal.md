## Why

Runtime handoff records currently can persist raw remote URLs and connectivity
diagnostics. Those fields may contain URL userinfo, passwords, bearer-like query
values or private operator identity, and they are consumed by review/publish
workflow tooling.

## What Changes

- Sanitize delivery manifest repository identity before writing runtime JSON.
- Sanitize delivery runner connectivity diagnostics for both pass and fail
  preflight outcomes.
- Add focused smoke coverage for HTTPS remotes with user/password, token-like
  query parameters, SCP-style SSH remotes and connectivity pass/fail messages.
- Document redaction guarantees and residual risk from raw child logs.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: delivery manifest repository identity must be
  credential-redacted.
- `changerail-delivery-runner`: connectivity preflight diagnostics must store
  sanitized endpoint metadata rather than raw URLs or exception strings.

## Impact

- `scripts/changerail_delivery_manifest.py`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-manifest.py`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `skills/changerail-do/references/changerail-delivery-manifest.md`
