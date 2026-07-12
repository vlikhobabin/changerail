## Why

The board guide now documents the current ChangeRail card lifecycle and
two-agent practice, but root board docs and project templates still carry older
or weaker guidance. New consumers should not be bootstrapped with process
instructions that contradict the current lifecycle.

## What Changes

- Update root board docs to describe the currently available full lifecycle
  surface instead of the earlier minimal surface.
- Update project board templates so generated consumers receive the same
  lifecycle semantics and a canonical guide pointer.
- Keep examples generic and avoid private consumer names or local inventory.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-templates`: generated consumer board docs must carry or
  link to the current workflow model.
- `changerail-agent-methodology`: board documentation must align with the
  review-gated lifecycle and two-agent guide.

## Impact

- Affected files: root board docs, project templates and related docs.
- No runtime state or machine-local inventory is committed.
