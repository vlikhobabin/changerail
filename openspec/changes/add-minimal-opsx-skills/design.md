## Context

OPSX phase 1 requires a minimal source-of-truth skill surface before templates,
bootstrap scripts and consumer symlinks can be implemented. Existing local skill
drafts are useful source material, but they include domain-specific trace,
manifest and provider-policy sections that do not belong in generic OPSX core.

## Goals / Non-Goals

**Goals:**
- Add path-neutral `opsx-explore` and `opsx-ff` skills under `skills/`.
- Add matching Claude command wrappers under `claude/commands/opsx/`.
- Preserve generic OPSX boundaries and public-safety requirements.
- Document that repo-local symlink wiring is not part of this change.

**Non-Goals:**
- Do not migrate `opsx-do`, `opsx-review`, `opsx-pub` or `opsx-deliver`.
- Do not migrate upstream `openspec-*` skills.
- Do not add trace, manifest, provider or domain-specific runtime policy.
- Do not create `.claude` or `.codex` symlinks in this change.

## Decisions

- `opsx-explore` is a compact alias for OpenSpec exploration. It may inspect
  context and suggest next artifacts, but it does not implement code.
- `opsx-ff` is a card-level planning skill. It decomposes stories and creates
  apply-ready OpenSpec artifacts, but it does not run implementation, archive or
  publish steps.
- Claude wrappers live in `claude/commands/opsx/` as source files for future
  consumer wiring. Repo-local discovery symlinks are deferred to a separate
  change so they can be tested explicitly.
- Skill/command runtime contracts stay in English because frontmatter and
  trigger text are consumed directly by agent runtimes.

## Risks / Trade-offs

- Too much of the local draft could leak into generic core -> keep only generic
  planning/explore behavior and scan for private paths.
- Without repo-local symlinks, the commands are source files rather than active
  local slash commands -> defer wiring until discovery-smoke can validate it.
- `opsx-ff` without `opsx-do` gives only planning flow -> this is intentional,
  because delivery/review/publish need separate cleanup and contracts.

## Migration Plan

1. Add minimal source files.
2. Update docs to show explore/ff as current and the rest as planned.
3. Run OpenSpec validation, config parsing, whitespace and private-path scans.
4. Leave active change unarchived until review/commit policy is applied.

## Open Questions

- Exact `.claude` and `.codex` dogfooding symlink layout should be decided in a
  follow-up change with discovery-smoke evidence.
