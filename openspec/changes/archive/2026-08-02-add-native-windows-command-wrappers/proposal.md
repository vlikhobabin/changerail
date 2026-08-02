## Why

Native Windows cannot reliably launch ChangeRail's extensionless POSIX helper
wrappers as process entrypoints. The architecture decision selected tracked
`.cmd` wrappers as the native Windows runtime default, so the supported helper
surfaces need concrete Windows entrypoints before later wiring work can depend
on them.

## What Changes

- Add tracked `.cmd` wrappers for the supported ChangeRail helper commands under
  `bin/`.
- Route Python-backed helpers through the shared `changerail-python` runtime
  selector so missing Python, unsupported Python and missing runtime dependency
  failures keep the existing actionable diagnostics.
- Preserve existing POSIX wrapper behavior and keep PowerShell as an explicit
  diagnostic or fallback path rather than the default native Windows entrypoint.
- Document native wrapper invocation semantics where durable operator-facing
  docs need to mention the new supported surface.

## Capabilities

### New Capabilities
- `changerail-windows-runtime-entrypoints`: concrete supported native Windows
  helper entrypoints, argument forwarding, working-directory/environment
  preservation and runtime-selector diagnostics.

### Modified Capabilities
- none

## Impact

- `bin/*.cmd` tracked helper wrappers.
- Shared Python helper launch contract through `bin/changerail-python`.
- Compatibility documentation for supported native Windows command entrypoints.
- OpenSpec specs for the new runtime entrypoint capability.
