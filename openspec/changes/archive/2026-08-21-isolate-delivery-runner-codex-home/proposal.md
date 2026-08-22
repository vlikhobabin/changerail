## Why

Delivery runner currently defaults `CODEX_HOME` to the tracked project
`.codex/` directory. Codex may persist an absolute trust entry there during
startup, creating a machine-specific payload mutation after clean preflight and
forcing an otherwise valid delivery to stop at review.

## What Changes

- Separate tracked project configuration from the runner-owned mutable Codex
  user/runtime home for default unattended runs.
- Prepare an ignored private runtime home with an exact workspace trust binding
  and a reference to an existing ignored project auth marker without copying
  credential contents.
- Keep authority, auth and stale-symlink preflight fail-closed across the two
  configuration layers and preserve explicit operator `CODEX_HOME` behavior.
- Add regression smoke coverage that simulates Codex trust persistence and
  proves the tracked project config remains byte-identical and git-clean.
- Update public operator documentation for the new default and remediation
  boundary.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: Default Codex home isolation, preparation and
  preflight behavior for non-interactive delivery children.

## Impact

- Affected command: `bin/changerail-delivery-runner`.
- Affected verification: `scripts/smoke-delivery-runner.py` and release
  baseline coverage.
- Affected public documentation: delivery contracts, workflow explanation and
  consumer adoption guidance.
- Consumer projects retain tracked `.codex/config.toml` as project policy;
  default mutable state moves under ignored `.runtime/changerail/`.
- No wire schema, external dependency or domain-specific extension changes.
