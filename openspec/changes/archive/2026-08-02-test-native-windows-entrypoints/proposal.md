## Why

The native Windows entrypoint wrappers must be regression-tested before
bootstrap, wiring or release gates rely on them. The tests need deterministic
coverage for Windows quoting, path and process semantics while preserving the
existing Linux/POSIX helper baseline.

## What Changes

- Add deterministic tests for `.cmd` wrapper argv forwarding, exit-code
  propagation, cwd and environment preservation.
- Cover paths with spaces and non-ASCII characters through local fixtures that
  can run from the Linux release baseline without requiring a live Windows host.
- Add negative coverage that documents unsupported native Windows assumptions:
  direct extensionless POSIX launch and implicit Bash.
- Keep live two-host Windows smoke as explicit evidence or blocker/caveat,
  rather than claiming support from deterministic fixtures alone.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-windows-runtime-entrypoints`: verification requirements for the
  native Windows entrypoint capability.
- `changerail-release-ci`: release baseline and CI workflow include the focused
  Windows entrypoint smoke.

## Impact

- Focused smoke or test scripts for Windows entrypoint wrapper semantics.
- Release baseline coverage for the deterministic fixture suite.
- Verification evidence requirements in the runtime entrypoint spec.
