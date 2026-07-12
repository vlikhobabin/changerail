## Context

OPSX is currently both the product name and a namespace embedded in paths,
commands, docs, schemas and examples. Users also encounter OpenSpec artifacts
and OpenSpec-related `opsx` terminology, which makes installation guidance
ambiguous. The product needs a distinct public identity while preserving a
clear migration trail.

## Goals / Non-Goals

**Goals:**
- Make ChangeRail the canonical public product name.
- Make `/opt/changerail` the documented source-of-truth path.
- Keep OpenSpec positioned as the artifact/spec workflow dependency.
- Preserve only explicit migration/history mentions of OPSX.
- Keep tracked docs public-safe and generic.

**Non-Goals:**
- Do not rename OpenSpec itself or `openspec-*` lifecycle skills.
- Do not migrate consumer repositories in this change.
- Do not leave `/opt/opsx` as the normal documented path.

## Decisions

1. **Use ChangeRail as the product name and `changerail` as the technical
   token.**
   This creates a clean separation from OpenSpec. The lowercase token is used
   for repository names, paths, schema filenames and command namespaces.

2. **Treat the rename as a breaking release.**
   Source-of-truth path changes and command namespace changes affect every
   consumer. Release notes and migration docs must mark this explicitly instead
   of presenting it as a cosmetic edit.

3. **Keep history readable but active docs canonical.**
   Archived OpenSpec artifacts and old cards may retain OPSX as historical
   record. Active docs, templates, specs, scripts and examples should use
   ChangeRail, except migration notes that explain the old name.

## Risks / Trade-offs

- **Risk:** Broad text replacement can rewrite historical archives or generic
  OpenSpec-owned terms incorrectly. -> **Mitigation:** Scope implementation to
  active public surface first and validate remaining `OPSX`/`opsx` matches as
  allowed history or migration mentions.
- **Risk:** Users may follow old GitHub URLs. -> **Mitigation:** Document the
  GitHub rename and rely on GitHub redirects only as compatibility, not as the
  canonical docs target.
- **Risk:** Real consumer names leak into public docs. -> **Mitigation:** Keep
  operator consumer inventory in ignored `internal/` and run a public-surface
  scan before commit.

## Migration Plan

1. Update tracked public identity docs and specs to ChangeRail.
2. Add migration notes that OPSX was the previous name.
3. Rename the GitHub repository after the code/docs rename is committed.
4. Update local `origin` to `git@github.com:vlikhobabin/changerail.git`.
5. Continue with command, contract and consumer wiring changes before migrating
   real consumers.

## Open Questions

- None for product naming; ChangeRail is selected.
