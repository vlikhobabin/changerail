## Context

ChangeRail already exposes canonical lifecycle names:

- Codex skills under `skills/changerail-*` and repo-local symlinks under
  `.codex/skills/changerail-*`;
- Claude wrappers under `claude/commands/changerail/`;
- generated consumer wiring through `templates/project/`, `bin/bootstrap-project`
  and `bin/verify-project`;
- smoke coverage for wiring discovery and generated consumers.

The new `chrl` namespace is only invocation ergonomics. It must not create new
runtime namespaces, schema ids, manifest paths or lifecycle contracts.

## Goals / Non-Goals

**Goals:**

- Provide official short aliases for the six ChangeRail lifecycle commands:
  explore, ff, do, review, pub and deliver.
- Keep canonical `changerail-*` skill and `/changerail:*` command contracts as
  the source of truth.
- Install both canonical and short aliases in repo-local dogfooding wiring and
  generated consumer projects.
- Make verification and smoke checks fail when required short aliases are
  missing.
- Update durable public docs so users can choose `chrl-*` for daily use and
  `changerail-*` for reference clarity.

**Non-Goals:**

- Do not remove, rename or deprecate `changerail-*`.
- Do not introduce `chrl` schema ids, runtime directories, manifest keys or
  OpenSpec namespaces.
- Do not restore old `opsx-*` aliases.
- Do not change lifecycle behavior inside canonical contracts.

## Decisions

1. **Alias skills are thin source files.**
   Each `skills/chrl-*/SKILL.md` uses frontmatter `name: chrl-*` and delegates
   to the corresponding canonical `changerail-*` contract. This keeps Codex
   skill discovery explicit while avoiding duplicated lifecycle instructions.
   Alternative considered: symlink `skills/chrl-*` directly to canonical
   directories. That would make frontmatter names mismatched or require
   canonical files to carry multiple names, so explicit thin files are clearer.

2. **Claude aliases are thin wrapper commands.**
   `claude/commands/chrl/<command>.md` should load or invoke the matching
   canonical `/changerail:<command>` behavior instead of copying full command
   content. This mirrors the skill approach and keeps canonical wrappers as the
   long-form reference surface.

3. **Generated wiring uses symlinks for both alias families.**
   Repo-local `.codex/skills/chrl-*` and generated consumer `.codex/skills/chrl-*`
   point to tracked ChangeRail source directories. Generated Claude command
   wiring adds `.claude/commands/chrl` beside `.claude/commands/changerail`.
   This follows the existing source-of-truth pattern and keeps consumer
   repositories small.

4. **Verification owns fail-closed alias checks.**
   `bin/verify-project` should validate canonical and short alias symlinks
   explicitly. Smoke tests should cover generated consumers and wiring discovery
   so missing aliases are caught before publication.

5. **Docs recommend shorthand without changing canonical terms.**
   Public docs may show `chrl-*` as the daily shorthand, but specs, schemas,
   runtime paths and long-form reference examples keep `changerail` naming.

## Risks / Trade-offs

- Duplicate wrapper files can drift from canonical contracts -> keep wrappers
  intentionally tiny and delegate by name/path.
- Extra symlinks increase verification surface -> centralize expected command
  lists in bootstrap/verify helpers where practical.
- Users could infer `chrl` is a new product namespace -> docs and specs must
  state that it is invocation ergonomics only.

## Migration Plan

1. Add tracked alias source directories and command wrappers.
2. Add repo-local symlinks for Codex dogfooding.
3. Update templates and bootstrap generation for consumer projects.
4. Update verification and smoke checks.
5. Update docs and shared methodology.
6. Validate OpenSpec, whitespace, config parsing and affected smoke scripts.

Rollback is removing the alias files and symlinks while leaving canonical
`changerail-*` behavior untouched.
