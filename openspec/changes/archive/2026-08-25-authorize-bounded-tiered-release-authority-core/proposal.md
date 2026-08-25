## Why

Published split rescue fixes the disjoint Scope A/Scope B boundary, but the
future release-authority-core implementation cannot consume a decision card as
its generic authorization source. Scope A therefore needs one clean tracked
authorization card before its successor can be created.

## What Changes

- Publish exactly one recognized inline `Investigation authorization` object
  with the six generic fields, exact rescue/successor identities and canonical
  paths.
- Fix authorization ceiling `500`, protocol allowance `true` and the separate
  implementation limit `<=499` production LOC against
  `25f756ebf2aa90c58e01eab3703b291dbdde257f`.
- Preserve exact reciprocal lineage and require the future successor to use
  only the exact two-field inline authorization reference.
- Limit authorization to Scope A release authority core; Scope B Windows
  scheduling/deduplication and all later scanner, verify-project and smoke
  implementations remain excluded.
- Keep the payload board/OpenSpec/spec documentation only: production, test
  and runtime additions are `0` LOC and successor card/code remain absent.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: publish the exact bounded authorization source for
  the single future Scope A release-authority-core successor.

## Impact

Planning changes only the authorization board card and
`openspec/changes/authorize-bounded-tiered-release-authority-core/`. Delivery
will synchronize its delta into `openspec/specs/changerail-release-ci/spec.md`.
Production code, tests, workflows, schemas, helpers, CLI, runtime state and the
future successor do not change in this card.
