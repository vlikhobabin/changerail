## Why

The unpublished affected v4 implementation exhausted review repair because its
real pre-production RED output was not retained at execution time. Continuing
that lineage or accepting a later reproduction would make test-first chronology
non-auditable.

## What Changes

- Exhaust the unpublished v4 implementation without importing its payload or evidence.
- Declare one exclusive docs-only authorization and clean v5 implementation path.
- Require retained failing evidence, including pre-production workspace identity,
  before the first production mutation.
- Require independent reconstruction of that saved tree against the published
  authorization HEAD.
- Preserve the published affected profile and connected-proof floor.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the affected v5 clean-lineage and auditable
  pre-production RED evidence boundary.

## Impact

- Methodology: terminal unpublished work is replaced through explicit lineage.
- Verification: v5 test-first chronology becomes machine-auditable.
- Public surface: docs/OpenSpec only; no code, dependency, schema or runtime state.
- Consumer projects: no impact.
