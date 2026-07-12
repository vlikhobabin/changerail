## Why

The user-facing command namespace is where the OpenSpec/OPSX collision is most
visible: users currently need to distinguish OpenSpec from `/opsx:*` and
`$opsx-*`. ChangeRail needs its own command and skill namespace.

## What Changes

- **BREAKING**: Rename generic lifecycle Codex skills from `opsx-*` to
  `changerail-*`.
- **BREAKING**: Rename Claude command wrappers from `/opsx:*` to
  `/changerail:*`.
- Rename repo-local and consumer skill/command discovery wiring for the new
  namespace.
- Update skill bodies, command wrappers and handoff prompts so new defaults do
  not install or recommend `/opsx:*` aliases.
- Keep `openspec-*` lifecycle skills unchanged because they belong to the
  OpenSpec artifact layer.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-skill-surface`: rename the generic lifecycle skill and command surface
  to `changerail-*` and `/changerail:*`.
- `changerail-wiring-discovery`: update repo-local and consumer discovery checks for
  ChangeRail skills and Claude commands.
- `changerail-agent-methodology`: update delivery handoffs and workflow examples to
  use the ChangeRail command namespace.

## Impact

- `skills/opsx-*` directories and `SKILL.md` frontmatter.
- `claude/commands/opsx/` wrappers.
- `.codex/skills/` and `.claude/commands/` repo-local symlinks.
- README, wiring docs, compatibility notes and runbooks.
- Smoke tests that assert command/skill discovery.
