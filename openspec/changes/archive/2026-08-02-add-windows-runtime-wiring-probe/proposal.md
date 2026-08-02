## Why

`030-02` must reproduce native Windows runtime, wiring and Git behavior before
ChangeRail chooses a Windows architecture. The probe needs a reusable,
public-safe harness so both operator-managed hosts can be tested without
touching real consumer repositories or exposing private host data.

## What Changes

- Add a native Windows runtime/wiring probe harness that reuses the ignored
  Windows lab inventory and disposable roots from `030-01`.
- Check direct directory symlinks, direct file symlinks, junctions, generated
  copies, extensionless and extension-specific wrapper invocation, explicit
  shell invocation, Git status/index traversal and cleanup repeatability.
- Retain raw SSH output under ignored `.runtime/changerail/` paths and emit only
  sanitized JSON summaries with generic host ids.
- Provide a local sample dry-run mode that validates report shape without
  contacting real Windows hosts.

## Capabilities

### New Capabilities
- `changerail-windows-runtime-wiring-probe`: public-safe harness contract for
  native Windows runtime, wiring and Git behavior probes.

### Modified Capabilities
- none

## Impact

- Adds `scripts/windows-runtime-wiring-probe.py`.
- Adds OpenSpec requirements for reusable Windows wiring/runtime probe behavior.
- Does not change ChangeRail bootstrap, runtime wrappers or consumer templates.
