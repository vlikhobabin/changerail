## Why

The published brokered supervision decision requires one separate six-field
authorization before an implementation card can exist. This docs-only change
creates that source without creating or activating the future implementation.

## What Changes

- Publish the exact decision-to-v4 authorization object and reciprocal lineage.
- Bind future v4 to a clean authorization HEAD, `<=499` production LOC, no new
  external dependency, the complete broker ownership/protocol proof and one
  bounded repair/re-review allowance.
- Preserve v3 exhaustion and keep v4 plus downstream work dormant.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the published brokered v4 authorization source.

## Impact

Only docs/OpenSpec authorization artifacts change. No successor, executable,
test, dependency, CI, baseline, runtime authority or live behavior is added.
