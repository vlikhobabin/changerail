## Why

Terminal unpublished implementation v20 exposed a contract incompatibility
between the immutable three-command physical group and scheduler v1's singular
command task schema, plus a disconnected activation proof that bypassed the
public affected entrypoint. A new published decision is required before any
executable successor can safely resolve those gaps.

## What Changes

- Define a two-layer composite execution boundary: one scheduler result per
  physical owner with each immutable group argv executed in order through a
  nested published-broker call.
- Define closed scheduler-envelope validation that cannot manufacture pass or
  full-release authority from malformed result rows.
- Define a public-entry, callsite-qualified static/dynamic activation oracle
  using one source-derived worklist and disposable focused execution.
- Freeze exact empty-runtime-root, canonical hosted launcher and sole-CI
  execution guards for the future v21 successor.
- Preserve the immutable v18 inventory and all accumulated selection,
  non-authority and certification boundaries.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-release-ci`: add the v21 investigation decision for composite
  execution identity, scheduler summary admission, activation projection and
  remaining v20 guard closure.

## Impact

This change is docs-only. It affects one board card, same-slug OpenSpec
artifacts and the accumulated release-CI specification. It adds no production,
test or runtime behavior, does not import terminal v20 payload/evidence and
does not run history, full, affected, live or certification evidence.
