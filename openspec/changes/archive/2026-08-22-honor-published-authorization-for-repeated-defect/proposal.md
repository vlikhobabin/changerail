## Why

Deterministic review preflight validates an exact published investigation
authorization and uses it for LOC and protocol decisions, but still stops every
successor that truthfully declares `Repeated defect class: yes`. This makes a
published bounded decision unusable for the third complexity signal and blocks
otherwise authorized consumer delivery.

## What Changes

- Treat a valid exact published authorization as the bounded exception for the
  repeated-defect complexity signal of its bound successor.
- Preserve `investigation-required` when repeated defect is declared without a
  valid authorization.
- Add focused positive and negative regression coverage without changing the
  authorization object or preflight result schema.
- Clarify the deterministic preflight contract and shared methodology.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: exact published authorization governs the
  repeated-defect complexity decision as well as the existing LOC/protocol
  decisions.
- `changerail-agent-methodology`: the bounded investigation exception applies
  consistently to all three complexity signals.

## Impact

`scripts/changerail_review_preflight.py`, its focused smoke, synced OpenSpec
contracts and archived change artifacts. No new wire fields, authority surface,
launcher behavior or consumer-specific code is introduced. Public examples
remain generic.
