## Why

Previous native Windows cards added focused deterministic probes for `.cmd`
entrypoints, generated wiring, verification, drift and Git safety. The next
step is a repeatable matrix runner that composes those checks and can also
record live two-host smoke results without committing private host details.

## What Changes

- Add a Windows smoke matrix runner that executes platform-neutral local
  contract fixtures from Linux or Windows workspaces.
- Add an optional live-host mode that reads ignored Windows lab inventory,
  targets `windows-host-a` and `windows-host-b`, writes sanitized structured
  reports under ignored runtime state and records explicit blockers or caveats
  when a host cannot be exercised.
- Cover generated-copy default behavior plus bounded symlink and junction
  fallback positive and negative conditions.
- Cover disposable workspace setup, idempotent cleanup, path quoting, non-ASCII
  paths, Git status/add/index evidence and stale/generated ownership behavior.
- Add release-baseline and CI inventory checks for the platform-neutral smoke
  contract.

## Capabilities

### New Capabilities
- `changerail-windows-smoke-matrix`: native Windows smoke matrix runner,
  fixture coverage, live-host evidence contract and sanitized runtime reports.

### Modified Capabilities
- `changerail-release-ci`: include the platform-neutral Windows smoke matrix
  contract in local release baseline and tracked CI inventory.

## Impact

- Adds a new focused smoke script under `scripts/`.
- Updates `scripts/run-release-baseline.py`, `scripts/smoke-release-ci.py` and
  the tracked CI workflow command inventory.
- Updates Windows-related specs and the card-owned delivery evidence.
