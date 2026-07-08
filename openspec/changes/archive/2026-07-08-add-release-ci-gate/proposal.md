## Why

Release discipline is not enforceable if maintainers only run checks manually.
OPSX needs a public CI gate that exercises templates, bootstrap, verify, drift
and wiring smoke before release-facing changes are merged.

## What Changes

- Add a GitHub Actions workflow for OPSX CI.
- Run OpenSpec validation, docs/config parsing and Python syntax checks.
- Run wiring, verify-project and bootstrap smoke tests.
- Run drift gate against a generated public-safe runtime fixture.
- Add a local smoke script that validates the CI workflow contract.

## Capabilities

### New Capabilities
- `opsx-release-ci`: release-facing CI gate for OPSX templates, bootstrap,
  verify, drift and wiring smoke.

### Modified Capabilities
- none

## Impact

- New CI workflow under `.github/workflows/`.
- New smoke validator under `scripts/`.
- Public docs and card verification can reference one local command that checks
  the CI contract without requiring GitHub Actions to run locally.
