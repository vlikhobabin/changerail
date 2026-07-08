# Перенести минимальные generic OPSX skills

## Status
3.inprogress

## Owner
Codex

## OpenSpec Stage
implemented

## Source
- OPSX roadmap phase 1.
- `docs/opsx-source-of-truth-architecture.md`
- `AGENTS.shared.md`
- Existing local OPSX skill drafts used only as source material.

## Summary
Добавить первый публичный generic OPSX skill surface: `opsx-explore` и
`opsx-ff`, а также соответствующие Claude command wrappers. Перенос должен быть
path-neutral и не должен включать domain-specific trace, manifest или provider
политику.

## Acceptance
- `skills/opsx-explore/SKILL.md` существует и не содержит machine-local paths.
- `skills/opsx-ff/SKILL.md` существует и описывает generic planning-only flow.
- `claude/commands/opsx/explore.md` и `claude/commands/opsx/ff.md` существуют.
- Public docs отражают текущий минимальный skill/command surface.
- OpenSpec validation и public-surface scans проходят.

## Change Set
- `add-minimal-opsx-skills`

## Verify
- passed: `openspec validate --all --strict --json`
- passed: `python3 -m json.tool .mcp.json`
- passed: `.codex/config.toml` parsed with Python `tomllib`
- passed: `git diff --check`
- passed: whitespace scan over changed and untracked text files
- passed: `git status --short --ignored`
- passed: public-surface scan for private paths and workspace names
- passed: targeted review regression checks for Claude skill lookup, conditional
  delivery handoff and board README wording

## Archive
- not started

## Related
- `openspec/changes/add-minimal-opsx-skills/`
- `skills/opsx-explore/SKILL.md`
- `skills/opsx-ff/SKILL.md`
- `claude/commands/opsx/explore.md`
- `claude/commands/opsx/ff.md`

## Result
Implemented minimal generic skill and Claude command source files for
`opsx-explore` and `opsx-ff`.

## Next
- Review the generic skill surface before archive/commit.

## Change 1: `add-minimal-opsx-skills`

### Why
OPSX needs a minimal reusable skill surface before bootstrap templates and
consumer symlinks can point at `/opt/opsx` as source of truth.

### Goal
Add path-neutral generic source files for `opsx-explore`, `opsx-ff` and their
Claude command wrappers.

### Scope
- Add only explore and fast-forward planning skills.
- Add only `/opsx:explore` and `/opsx:ff` Claude wrappers.
- Do not add `opsx-do`, `opsx-review`, `opsx-pub` or `opsx-deliver`.
- Do not add repo-local `.claude` or `.codex` symlink wiring in this change.

### Acceptance
- Skill text has no private workspace paths or domain-specific provider policy.
- `opsx-ff` remains planning-only and does not introduce implementation,
  archive or publish behavior.
- Commands load generic skills through skill discovery instead of assuming a
  root `skills/` path in consumer projects.

### Depends On
- `opsx-agent-methodology` main spec.

### Related
- `openspec/changes/add-minimal-opsx-skills/`

## Log
- 2026-07-08T09:40:00Z card created and minimal generic skill surface implemented.
- 2026-07-08T09:50:00Z verification completed for generic skill surface.
- 2026-07-08T10:00:00Z fixed review findings: Claude skill lookup path, conditional delivery handoff and stale board README language.
