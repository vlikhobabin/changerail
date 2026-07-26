## Why

Queue-plan operators can misread ChangeRail runner docs as requiring every
consumer repository to track its own `bin/codex`. The supported launcher chain
and effective workspace binding should be explicit before first unattended
queue setup.

## What Changes

- Clarify that the plan runner launches the ChangeRail single-card runner and
  each child runner launches Codex.
- Document how `CODEX_WORKDIR` and effective `CODEX_HOME` bind the child run to
  the consumer workspace.
- Document that repo-local `bin/codex` in a consumer project is optional, not a
  universal tracked-file requirement.
- Keep examples generic and public-safe.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: runner documentation and docs-backed behavior
  for queue launcher semantics.

## Impact

- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `docs/board-and-two-agent-feature-flow.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
