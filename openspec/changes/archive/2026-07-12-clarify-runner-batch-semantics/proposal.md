## Why

The guide describes bounded batch delivery, while the tracked
`bin/changerail-delivery-runner` is currently a single-card launcher that
delegates to `$changerail-deliver`. The docs, skill contract and runner spec
must describe the same boundary.

## What Changes

- Clarify that `$changerail-deliver` owns card directory/queue handling.
- Clarify that `bin/changerail-delivery-runner` is a single-card
  non-interactive launcher unless explicit queue support is added later.
- Align docs/specs/CLI help so supervisors know which status records exist.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: runner accepted inputs and status records are
  documented as single-card.
- `changerail-agent-methodology`: batch guidance distinguishes deliver skill
  queue handling from runner single-card status.

## Impact

- Affected files: runner docs/specs, guide wording, CLI help and possibly
  smoke coverage.
- No change to runtime schema is expected unless implementation adds queue
  support.
