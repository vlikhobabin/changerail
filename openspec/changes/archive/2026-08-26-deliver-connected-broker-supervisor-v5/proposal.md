## Why

The published v5 authorization permits one clean implementation attempt. The
implementation must provide bounded broker-owned supervision and make the two
previously disconnected production connections observable through public
`supervise` with effective counterfactual source mutations.

## What Changes

- Add one dormant Linux broker/controller production module.
- Add one focused test suite covering canonical broker behavior and effective
  R8/R9 source mutations through public `supervise`.
- Retain bounded evidence and synchronize the v5 delivery requirement.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: materialize the authorized dormant v5 supervisor
  and connected-proof contract.

## Impact

Adds one production Python module and one focused test. It does not add a
dependency or activate release baseline, CI, receipts, review/publish or
downstream workflows.
