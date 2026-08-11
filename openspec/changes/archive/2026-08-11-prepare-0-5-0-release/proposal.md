## Why

ChangeRail has accumulated a new public maintenance and consumer bootstrap
surface after `v0.4.0`, and the local release baseline is green. The repository
still reports `0.4.0`, leaves migration notes under `Unreleased` and lacks
versioned release notes for operators.

## What Changes

- Bump root `VERSION` to `0.5.0`.
- Move release notes into `CHANGELOG.md` section `0.5.0 - 2026-08-11`.
- Update compatibility notes, migration guide, release discipline and security
  policy for the new release.
- Add a release-prep board card and archived OpenSpec artifacts for review and
  publish scope.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: current prepared version and migration
  notes now describe `0.5.0`.

## Impact

Release metadata changes only. Runtime behavior was delivered by prior
reviewed cards after `v0.4.0`.
