## Why

OPSX already ships `opsx-explore` and `opsx-ff`, but a consumer project still
cannot complete the standard `ff -> do -> review -> pub` workflow from
`/opt/opsx`. The remaining lifecycle skills must become public, path-neutral
source files before bootstrap and adoption flows can link them.

## What Changes

- Add generic source skills for `opsx-do`, `opsx-review`, `opsx-pub` and
  `opsx-deliver`.
- Add Claude wrappers for `/opsx:do`, `/opsx:review`, `/opsx:pub` and
  `/opsx:deliver`.
- Update the public skill-surface contract and user-facing docs to include the
  full lifecycle surface.
- Keep domain-specific provider, trace and suite fallback policy outside the
  generic OPSX skills.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `opsx-skill-surface`: add the remaining generic lifecycle skills and Claude
  wrappers.

## Impact

- Affected files: `skills/opsx-do/**`, `skills/opsx-review/**`,
  `skills/opsx-pub/**`, `skills/opsx-deliver/**`,
  `claude/commands/opsx/**`, `README.md`, `CLAUDE.md`,
  `docs/opsx-source-of-truth-architecture.md`,
  `openspec/specs/opsx-skill-surface/spec.md`.
- Consumer projects can expose the full OPSX lifecycle through the documented
  skill and command wiring.
- No runtime state, private paths or domain-specific policy is added.
