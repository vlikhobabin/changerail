## Why

The published accelerated-loop integration decision requires a separate
docs-only authorization before any scheduler successor exists. This preserves
reviewable authority and prevents scheduler implementation from being mixed
with its investigation boundary.

## What Changes

- Publish the exact scheduler six-field authorization object and future
  two-field implementation reference.
- Freeze the clean-start, `<=499` production LOC, v5-only supervision,
  plan/jobs/output/result and dormancy boundaries.
- Keep successor code, activation and expensive evidence absent.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the exact bounded scheduler-v1 authorization
  contract required by the published integration decision.

## Impact

Only this card, same-slug OpenSpec artifacts, synchronized release-CI spec and
archive metadata change. Production code, tests, dependencies, schemas, CI,
baseline and runtime behavior remain unchanged.
