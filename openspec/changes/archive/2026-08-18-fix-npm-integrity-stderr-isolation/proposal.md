## Why

`verify-project` treated npm warnings written to stderr as part of the JSON
integrity response. A successful registry lookup could therefore fail with a
false integrity mismatch.

## What Changes

- Capture npm stdout and stderr separately.
- Parse successful integrity responses only from stdout.
- Preserve both streams in diagnostics when npm exits non-zero.
- Add a regression smoke and normative verification scenario.

## Capabilities

### Modified Capabilities
- `changerail-project-verification`
