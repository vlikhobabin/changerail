## Why

OPSX lifecycle skills rely on reusable OpenSpec action skills, but those skills
are not yet part of the public OPSX source surface. Consumer projects also need
a stable `bin/openspec` route that pins the CLI version used by OPSX guidance.

## What Changes

- Add the OpenSpec lifecycle skills under `skills/openspec-*`.
- Add `bin/openspec`, pinned to a documented OpenSpec CLI version with an
  environment override for controlled upgrades.
- Add compatibility and sync-policy notes for the imported OpenSpec skills.
- Extend wiring docs and status text so consumers know these files are part of
  the source-of-truth surface.

## Capabilities

### New Capabilities
- `opsx-openspec-lifecycle`: public source surface for OpenSpec lifecycle
  skills and CLI wrapper.

### Modified Capabilities
- `opsx-wiring-discovery`: documented wiring includes `openspec-*` skills and
  `bin/openspec`.

## Impact

- Affected files: `skills/openspec-*/SKILL.md`, `bin/openspec`,
  `docs/openspec-lifecycle.md`, `docs/wiring-discovery.md`, `README.md`,
  `CLAUDE.md`, `openspec/specs/**`.
- Consumer projects can link a consistent OpenSpec action surface from OPSX.
- No OpenSpec CLI implementation is vendored; the wrapper executes the pinned
  npm package.
