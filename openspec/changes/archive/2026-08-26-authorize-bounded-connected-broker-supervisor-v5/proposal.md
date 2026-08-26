## Why

The connected-proof decision is published and closes v4, but executable v5
work must not begin until a separate bounded authorization freezes its exact
successor, LOC, protocol and review boundary.

## What Changes

- Publish one exact six-field authorization for
  `deliver-connected-broker-supervisor-v5`.
- Preserve the public-`supervise` R8/R9 mutation-sensitive proof and clean-start
  constraints from the decision.
- Keep successor code and all executable/runtime surfaces absent.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the exact docs-only v5 authorization contract.

## Impact

Only the authorization card, same-slug artifacts, synchronized release-CI spec
and archive metadata change. Production, tests, dependencies, CI, baseline,
runtime behavior and future successor remain unchanged.
