# Реализовать OPSX wiring/discovery smoke

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- OPSX roadmap phase 1.
- `docs/opsx-source-of-truth-architecture.md`
- `openspec/specs/opsx-skill-surface/spec.md`
- Review notes from `add-minimal-opsx-skills`.

## Summary
Реализовать проверяемый wiring/discovery smoke для подключения OPSX skills и
Claude command wrappers в consumer projects и в самом `/opt/opsx` без
machine-local symlink leaks.

## Acceptance
- Создан и реализован OpenSpec change
  `plan-opsx-wiring-discovery-smoke`.
- Change фиксирует expected wiring для consumer projects и repo-local
  dogfooding.
- Добавлены `docs/wiring-discovery.md` и
  `scripts/smoke-wiring-discovery.py`.
- Добавлены public-safe repo-local relative symlink-и для Claude/Codex
  discovery.
- Smoke генерирует ignored JSON report для repo-local и consumer-example
  checks.
- Change не создает local settings, secrets, machine-local links или tracked
  runtime state.

## Change Set
- `plan-opsx-wiring-discovery-smoke`

## Verify
- passed: `python3 scripts/smoke-wiring-discovery.py` -> 20/20 checks,
  report `.runtime/opsx/wiring-smoke/20260708T132042Z-1a0a8e2d/report.json`
- passed: `python3 scripts/smoke-wiring-discovery.py --mode repo-local --surface claude`
- passed: `python3 scripts/smoke-wiring-discovery.py --mode consumer-example --surface codex`
- passed: `openspec archive plan-opsx-wiring-discovery-smoke -y`
- passed: `openspec validate --all --strict`
- passed: JSON/TOML checks
- passed: `git diff --check`
- passed: whitespace scan over changed and untracked text files
- passed: public-surface scan for private paths and workspace names

## Archive
- `openspec/changes/archive/2026-07-08-plan-opsx-wiring-discovery-smoke/`

## Related
- `openspec/changes/archive/2026-07-08-plan-opsx-wiring-discovery-smoke/`
- `openspec/specs/opsx-wiring-discovery/spec.md`
- `docs/wiring-discovery.md`
- `scripts/smoke-wiring-discovery.py`
- `docs/opsx-source-of-truth-architecture.md`
- `openspec/specs/opsx-skill-surface/spec.md`

## Result
Wiring/discovery smoke implemented. Repo-local relative symlink-и expose the
minimal OPSX surface to Claude and Codex. Consumer-example wiring is created
under ignored runtime space, and aggregate JSON evidence records repo-local and
consumer-example checks for both surfaces.

## Next
- Commit and push scoped publish diff.

## Change 1: `plan-opsx-wiring-discovery-smoke`

### Why
OPSX now ships source files for `opsx-explore` and `opsx-ff`, but discovery
wiring is not yet specified or verified. Consumer projects must be able to link
OPSX skills and command wrappers without creating root-path assumptions or
committing machine-local symlinks.

### Goal
Define and implement the discovery-smoke contract for consumer wiring and
repo-local dogfooding.

### Scope
- Specify expected consumer wiring for `.claude/skills`,
  `.claude/commands/opsx` and `.codex/skills/opsx-*`.
- Specify repo-local `/opt/opsx` dogfooding wiring constraints.
- Define aggregate smoke evidence requirements.
- Add wiring docs and smoke script.
- Add relative repo-local symlink-и for the minimal Claude/Codex surface.

### Acceptance
- Artifacts are implemented and verified.
- Public examples remain generic.
- Machine-local paths are not introduced beyond documented generic examples.
- Evidence format and pass/fail criteria are explicit.

### Depends On
- `opsx-skill-surface` main spec.

### Related
- `openspec/changes/archive/2026-07-08-plan-opsx-wiring-discovery-smoke/`

## Log
- 2026-07-08T10:20:00Z card created for wiring/discovery smoke planning.
- 2026-07-08T10:30:00Z planning decisions and smoke evidence contract completed.
- 2026-07-08T13:20:42Z wiring smoke implemented and aggregate report generated.
- 2026-07-08T12:40:00Z review findings resolved: lifecycle scope and aggregate
  report contract aligned.
- 2026-07-08T12:45:00Z standalone publish requested by operator; runtime
  review verdict file is absent, review findings were provided in chat and
  fixed before publish.
- 2026-07-08T12:46:00Z OpenSpec change archived and main
  `opsx-wiring-discovery` spec created.
