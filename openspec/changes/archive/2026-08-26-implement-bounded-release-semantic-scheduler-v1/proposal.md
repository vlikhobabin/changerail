## Why

Published scheduler authorization permits one dormant bounded executor before
affected-profile activation. The repository needs this independently reviewed
primitive to prove parallel execution, cancellation and deterministic results
without coupling them to Git selection or release authority.

## What Changes

- Add one dormant semantic scheduler module using connected broker v5.
- Add connected focused proof for prelaunch validation, root allocation,
  jobs parity, exact-once ordering, cancellation and broker fault propagation.
- Keep all runner, CI, selector, receipt and authority surfaces unchanged.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: realize the authorized dormant scheduler-v1
  execution and proof contract.

## Impact

Adds one production scheduler module and one focused test within the exact
authorization ceiling. No dependency, schema, runner, CI or runtime activation
changes.
