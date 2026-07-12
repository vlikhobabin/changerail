## Why

The lifecycle already requires an independent review gate, but the
orchestrator, delivery worker and reviewer roles are documented mostly in
guides. Reusable methodology and lifecycle skills need one consistent role
contract so agents know which boundaries are binding.

## What Changes

- Add an explicit reusable role model to shared methodology.
- Update lifecycle skills and Claude wrappers where needed so role boundaries
  are visible at the point of use.
- Clarify when orchestrator and worker may be the same context, and when review
  must be separate.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-agent-methodology`: shared methodology must define the
  orchestrator, delivery worker and reviewer roles.
- `changerail-skill-surface`: lifecycle skill contracts must preserve and
  expose those role boundaries.

## Impact

- Affected files: `AGENTS.shared.md`, lifecycle skills, Claude wrappers and
  user-facing docs that summarize the model.
- No runtime state is committed.
