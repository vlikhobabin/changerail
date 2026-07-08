## Why

Once templates and verifier exist, operators need a single command that creates
a consumer project consistently and immediately proves the result with the
verification gate.

## What Changes

- Add executable `bin/bootstrap-project`.
- Render `templates/project/*.tpl`, copy OpenSpec skeleton and create required
  OPSX symlink-и.
- Refuse existing non-empty targets by default.
- Support `--dry-run` and explicit backup mode.
- Add `.runtime` smoke coverage for bootstrap end-to-end.

## Capabilities

### New Capabilities
- `opsx-project-bootstrap`: command-line bootstrap flow for new OPSX consumer
  projects.

### Modified Capabilities
- none

## Impact

- Affected files: `bin/bootstrap-project`, `scripts/smoke-bootstrap-project.py`,
  `README.md`, `docs/opsx-source-of-truth-architecture.md`,
  `openspec/specs/**`.
- Smoke projects and reports remain under ignored `.runtime/`.
- Bootstrap writes only to the requested target path and never commits files.
