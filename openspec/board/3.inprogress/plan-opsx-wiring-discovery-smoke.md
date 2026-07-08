# Спланировать OPSX wiring/discovery smoke

## Status
3.inprogress

## Owner
Codex

## OpenSpec Stage
apply-ready

## Source
- OPSX roadmap phase 1.
- `docs/opsx-source-of-truth-architecture.md`
- `openspec/specs/opsx-skill-surface/spec.md`
- Review notes from `add-minimal-opsx-skills`.

## Summary
Спланировать проверяемый wiring/discovery smoke для подключения OPSX skills и
Claude command wrappers в consumer projects и в самом `/opt/opsx` без
machine-local symlink leaks.

## Acceptance
- Создан apply-ready OpenSpec change `plan-opsx-wiring-discovery-smoke`.
- Change фиксирует expected wiring для consumer projects и repo-local
  dogfooding.
- Change требует smoke evidence для Claude command discovery и Codex skill
  discovery.
- Change не создает symlink-и и не меняет runtime/local settings.

## Change Set
- `plan-opsx-wiring-discovery-smoke`

## Verify
- passed: `openspec validate --all --strict --json`
- passed: JSON/TOML checks
- passed: `git diff --check`
- passed: whitespace scan over changed and untracked text files
- passed: public-surface scan for private paths and workspace names

## Archive
- not started

## Related
- `openspec/changes/plan-opsx-wiring-discovery-smoke/`
- `docs/opsx-source-of-truth-architecture.md`
- `openspec/specs/opsx-skill-surface/spec.md`

## Result
Apply-ready planning artifacts created. Repo-local wiring shape, consumer
smoke evidence format, implementation docs/scripts and scan expectations are
specified in `design.md`.

## Next
- Review artifacts.
- Implement wiring smoke docs/scripts in a follow-up delivery pass.

## Change 1: `plan-opsx-wiring-discovery-smoke`

### Why
OPSX now ships source files for `opsx-explore` and `opsx-ff`, but discovery
wiring is not yet specified or verified. Consumer projects must be able to link
OPSX skills and command wrappers without creating root-path assumptions or
committing machine-local symlinks.

### Goal
Define the discovery-smoke contract and implementation plan for consumer wiring
and repo-local dogfooding.

### Scope
- Specify expected consumer wiring for `.claude/skills`,
  `.claude/commands/opsx` and `.codex/skills/opsx-*`.
- Specify repo-local `/opt/opsx` dogfooding wiring constraints.
- Define smoke evidence requirements.
- Do not create symlinks or scripts in this planning change.

### Acceptance
- Artifacts are ready for implementation.
- Public examples remain generic.
- Machine-local paths are not introduced beyond documented generic examples.
- Evidence format and pass/fail criteria are explicit.

### Depends On
- `opsx-skill-surface` main spec.

### Related
- `openspec/changes/plan-opsx-wiring-discovery-smoke/`

## Log
- 2026-07-08T10:20:00Z card created for wiring/discovery smoke planning.
- 2026-07-08T10:30:00Z planning decisions and smoke evidence contract completed.
