## Why

Existing consumers can have justified optional browser MCP tooling, but
`verify-project` currently cannot verify two known exact browser MCP pins because
the lock file lacks their integrity metadata and the parser misses standard
`npx --package` forms.

## What Changes

- Add locked npm metadata for the approved optional browser MCP packages
  `@playwright/mcp@0.0.68` and `chrome-devtools-mcp@0.20.3`.
- Teach `bin/verify-project` to recognize exact MCP package pins passed as a
  direct `npx` package argument, `--package=<package>@<version>` or
  `--package <package>@<version>`.
- Extend focused smoke coverage for successful optional browser package forms
  and fail-closed cases.
- Document the approved optional package list and trusted update procedure
  without adding browser MCP packages to default ChangeRail templates or root
  config.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: verifier recognizes locked exact package
  pins in direct and `--package` npx forms and still fails closed on unpinned,
  unlocked or integrity-mismatched MCP packages.
- `changerail-release-discipline`: compatibility and release guidance describe
  approved optional MCP package pins and the trusted update procedure.

## Impact

- `mcp-npm-lock.json`
- `bin/verify-project`
- `scripts/smoke-verify-project.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/specs/changerail-release-discipline/spec.md`
