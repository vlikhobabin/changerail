## Why

The unpublished v4 implementation passed its direct runtime probes, but its
final independent review proved that two decisive tests were disconnected from
the production paths they claimed to protect. The exhausted v4 lineage cannot
be repaired, rescued or used as a source of code or evidence. A new decision is
required before a clean successor can be authorized.

## What Changes

- Close the v4 implementation path without rewriting its published decision or
  authorization history.
- Define exact v5 authorization and implementation lineage with a clean-start
  and `<=499` production LOC boundary.
- Require mutation-sensitive connected proof through public `supervise` for
  outer cleanup and pidfd signaling.
- Keep the decision docs-only and all executable/downstream surfaces dormant.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the exclusive v5 lineage and connected-proof
  boundary for brokered child supervision.

## Impact

Only this card, its OpenSpec artifacts, synchronized release-CI specification
and archive metadata change. Production code, tests, dependencies, CI, release
baseline and runtime behavior remain unchanged.
