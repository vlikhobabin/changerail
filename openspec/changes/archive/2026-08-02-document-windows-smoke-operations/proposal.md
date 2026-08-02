## Why

Automated Windows smoke is only useful if maintainers can run it repeatably,
interpret host caveats and retain public-safe evidence. Operators also need a
documented path from local two-host execution to future Windows CI without
embedding private SSH inventory in the public repository.

## What Changes

- Document the local two-host Windows smoke workflow using generic host ids and
  ignored operator inventory.
- Document report retention, sanitizer expectations, explicit blocker/caveat
  handling and repeat-after-cleanup expectations.
- Document how the platform-neutral smoke matrix remains part of Linux release
  baseline while live Windows execution stays opt-in until CI capacity exists.
- Document the future Windows CI integration path without committing private
  hostnames, credentials, SSH commands or machine-local roots.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-windows-smoke-matrix`: add operator documentation, evidence
  interpretation and future CI integration requirements for the smoke matrix.

## Impact

- Updates durable docs such as `docs/compatibility.md` and/or
  `docs/wiring-discovery.md`.
- Updates the Windows smoke matrix spec and card evidence.
- Does not add private inventory, credentials or raw runtime reports to tracked
  files.
