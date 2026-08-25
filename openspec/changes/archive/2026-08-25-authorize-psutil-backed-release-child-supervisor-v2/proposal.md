## Why

Published `rescue-psutil-release-child-supervisor-boundary` defines the future
psutil-backed S2 contract, but it is an investigation decision rather than the
separately publishable authorization source required before the exact S2
implementation card can exist.

## What Changes

- Add one docs-only, six-field `Investigation authorization` source bound to
  the published S2 decision and only
  `implement-psutil-backed-release-child-supervisor-v2`.
- Preserve the decision/authorization/future-implementation reciprocal
  relations, exact future two-field reference and `<=499` production-LOC
  limit against the authorization-publishing HEAD.
- Synchronize the already accepted future S2 contract: four-surface
  `psutil==7.1.0` pin, bounded `selectors`/`prctl` adapter, no writable
  cgroup, separate deadlines, fail-closed identity and inclusive cleanup caps,
  stable-empty success, dormancy and downstream refresh blocking.
- Keep this authorization docs-only: successor card/code and all downstream
  authority work remain absent.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `changerail-release-ci`: add the publishable S2 authorization source and
  its exact bounded future implementation contract.

## Impact

Only the authorization board card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` specification and archive metadata change. Production
code, dependency manifests, tests, bootstrap, admission, baseline, CI,
runtime state, future successor card, review, commit and push remain unchanged.
