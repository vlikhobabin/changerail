## Context

The current lifecycle surface is exposed as `opsx-*` Codex skills and
`/opsx:*` Claude commands. This directly conflicts with the user's mental model
when ChangeRail is explained as a workflow built on OpenSpec. The command
surface must be renamed without changing OpenSpec lifecycle skills.

## Goals / Non-Goals

**Goals:**
- Rename generic lifecycle skills to `changerail-*`.
- Rename Claude command wrappers to `/changerail:*`.
- Update repo-local and consumer discovery wiring.
- Remove old `/opsx:*` defaults from templates and runbooks.

**Non-Goals:**
- Do not rename `openspec-*` skills or `bin/openspec`.
- Do not preserve `/opsx:*` aliases as default generated surface.
- Do not implement consumer migration in this change.

## Decisions

1. **No default aliases for old commands.**
   Aliases would preserve the confusion this rename is meant to remove. Any
   temporary compatibility should be operator-local and undocumented as the
   normal path.

2. **Keep lifecycle verbs stable.**
   Only the namespace changes: `explore`, `ff`, `do`, `review`, `pub` and
   `deliver` remain the command verbs.

3. **Rename directories instead of wrapping old names.**
   Skill discovery and Claude command discovery should resolve to the new
   canonical files, so smoke tests can catch stale wiring.

## Risks / Trade-offs

- **Risk:** Active agent sessions keep old skill discovery in memory. ->
  **Mitigation:** Consumer migration requires session restart after rewiring.
- **Risk:** Third-party docs still mention `/opsx:*`. -> **Mitigation:** Add a
  migration note and make generated docs use `/changerail:*`.

## Migration Plan

1. Rename skill directories and frontmatter.
2. Rename Claude command directory and wrapper references.
3. Update repo-local symlinks and discovery smoke.
4. Update docs/templates/handoff prompts.
5. Validate that no generated consumer defaults install `/opsx:*`.
