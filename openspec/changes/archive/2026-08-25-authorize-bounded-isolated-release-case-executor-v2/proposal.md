## Why

Published clean lineage defines isolation owner I, but its future implementation
cannot consume the decision itself as a deterministic authorization source. A
separate clean tracked authorization must be published first.

## What Changes

- Publish exactly one six-field authorization object that binds the published
  decision to the single future I successor.
- Define reciprocal lineage, a future exact two-field reference, ceiling `500`
  and independent `<=499` executable LOC acceptance against the future
  published authorization HEAD.
- Keep authorization planning and delivery docs-only with zero executable,
  production, test and runtime LOC.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-release-ci`: publish the bounded authorization contract for the
  future isolated release case executor v2.

## Impact

Planning changes only this board card and its same-slug OpenSpec artifacts.
Delivery syncs the release-CI delta and archives the change. Production code,
tests, schemas, helpers, workflows, CLI, runtime state and the future successor
remain unchanged.
