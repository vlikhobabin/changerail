## Why

`030-03` needs evidence-backed trade-offs for native Windows architecture
choices. This change captures the two-host probe output as sanitized tracked
comparison data while keeping raw host evidence ignored.

## What Changes

- Run `scripts/windows-runtime-wiring-probe.py` on both ignored inventory hosts.
- Publish a sanitized comparison table covering direct symlink, junction, file
  link, generated copy, wrapper invocation, Git traversal, drift and upgrade
  behavior.
- Record repeatability after full cleanup and preserve only generic host ids in
  tracked output.
- Update the board card with concrete verification commands and outcomes.

## Capabilities

### New Capabilities
- `changerail-windows-runtime-wiring-results`: evidence contract for sanitized
  two-host runtime/wiring/Git comparison results.

### Modified Capabilities
- none

## Impact

- Updates `docs/compatibility.md` with a public-safe `030-02` comparison table.
- References ignored runtime report paths from the card and compatibility notes.
- Does not choose or implement the final Windows architecture.
