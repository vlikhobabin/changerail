## Why

Published connected broker supervisor v5 provides a reviewed child-tree
ownership primitive, but release-loop acceleration still lacks a bounded
integration lineage. Combining scheduler, affected selection, activation and
final measurement in one payload would recreate the broad, hard-to-review
change class that earlier investigations rejected.

## What Changes

- Split future delivery into a dormant bounded semantic scheduler, a later
  affected release profile that alone activates it and a final certification
  card with no production changes.
- Freeze exact future authorization objects, references, ownership boundaries,
  production LOC ceilings and publication order.
- Preserve `full-release` as the only potentially authoritative profile and
  keep affected execution diagnostic-only even when it falls back to all work.
- Confine reachable-history and full-baseline measurement to the final
  certification card and forbid retries.
- Keep this decision docs-only and leave all future cards and executable
  surfaces absent.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the scheduler, affected-profile and final
  certification integration boundary for release-loop acceleration.

## Impact

Only this card, its OpenSpec artifacts, the synchronized release-CI
specification and archive metadata change. Production code, tests,
dependencies, schemas, CI, release baseline and runtime behavior remain
unchanged.
