# Добавить Windows verification, drift и Git safety

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`03`

## Planning State
refreshed after `030-03`; pending deliver-ready decomposition

## Source
- `030-03-freeze-native-windows-architecture`
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

## Summary
Teach `verify-project`, drift checks and Git safety gates to enforce the
Windows generated-copy ownership model and fail closed for unsafe link fallback
or staging behavior.

## Acceptance
- `verify-project` validates Windows generated wiring manifest/policy and
  distinguishes valid generated content, stale copies, missing generated files,
  project-owned divergence and ordinary directories.
- Drift gate detects ChangeRail source updates and reports required refresh for
  generated Windows wiring.
- Git safety checks prove generated, symlink and junction paths do not stage
  ChangeRail source, ignored runtime state, credentials or out-of-scope files.
- Git safety uses porcelain status, `git add --dry-run` and index inspection.
- Symlink and junction fallback verification fails closed when required
  privilege, Developer Mode, cleanup or Git evidence is missing.
- Ignore rules stay minimal and do not hide project-owned source.
- Rename/update/uninstall and partial cleanup scenarios have negative tests.
- Diagnostics do not print credentials, private hostnames or private Windows
  paths.

## Depends On
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

## Change Set
- none yet; run `$changerail-ff` after `040-02`

## Verify
- Windows verifier fixtures for generated valid/stale/missing/diverged wiring.
- Git index/status/dry-run fixtures for generated, symlink and junction paths.
- Drift smoke on both Windows hosts or explicit blocker/caveat.
- Linux verification regressions and public-surface scan.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/1.backlog/040-02-add-windows-wiring-backend.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `bin/verify-project`
- `scripts/smoke-drift.py`

## Result
refreshed; implementation not started

## Next
- После publish `040-02`: `$changerail-ff openspec/board/1.backlog/040-03-add-windows-verification-and-git-safety.md`

## Log
- 2026-08-01T15:07:29Z provisional card создана из Git junction report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: verifier/drift/Git safety
  must enforce generated ownership and explicit link fallback gates.
