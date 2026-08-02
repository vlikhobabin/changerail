## Why

Generated Windows wiring needs safe refresh and rollback before it can be a
durable default. Symlink and junction modes are useful compatibility paths, but
`030-03` explicitly rejected both as defaults because they require proof,
operator opt-in and Git-safety controls.

## What Changes

- Add refresh/upgrade semantics that update only generated-owned artifacts and
  never silently overwrite project-owned files.
- Add partial-failure rollback that removes only artifacts created by the
  current run.
- Require explicit operator opt-in and positive privilege or Developer Mode
  proof before enabling Windows symlink fallback.
- Require explicit operator opt-in, link-aware cleanup and Git-safety
  preconditions before enabling Windows junction fallback.
- Report stale generated copies, project-owned divergence and fallback reasons
  through verify/drift output.
- Preserve existing POSIX symlink behavior outside native Windows.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: refresh/upgrade, rollback and fallback
  operator controls for Windows wiring.
- `changerail-project-verification`: generated ownership, stale copy,
  project-owned divergence and fallback proof verification.
- `changerail-windows-native-architecture`: fail-closed symlink/junction
  fallback semantics, cleanup and Git-safety preconditions.
- `changerail-wiring-discovery`: drift/refresh discovery expectations for
  generated Windows wiring.

## Impact

- `bin/bootstrap-project`, `bin/verify-project` and any shared wiring
  classification helpers introduced by implementation.
- Smoke fixtures for stale generated copies, project-owned divergence, symlink
  fallback, junction fallback and partial cleanup.
- Operator-facing wiring, compatibility and migration documentation.
- Public-surface scan expectations because generated manifests may mention
  source paths and digests.
