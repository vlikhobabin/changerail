# Добавить Windows verification, drift и Git safety

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`03`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

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
- `openspec/changes/enforce-windows-wiring-verification/` (planned)
- `openspec/changes/add-windows-git-safety-gates/` (planned)

## Verify
- Windows verifier fixtures for generated valid/stale/missing/diverged wiring.
- Git index/status/dry-run fixtures for generated, symlink and junction paths.
- Drift smoke on both Windows hosts or explicit blocker/caveat.
- Linux verification regressions and public-surface scan.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/2.todo/040-02-add-windows-wiring-backend.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/verify-project`
- `scripts/smoke-drift.py`

## Change 1: `enforce-windows-wiring-verification`

### Why
`verify-project` and drift checks need to distinguish generated Windows wiring
from stale, missing or project-owned content.

### Goal
Validate the generated wiring ownership model in project verification and drift
diagnostics.

### Acceptance
- Verifier covers valid, stale, missing and diverged generated artifacts.
- Drift gate reports required refresh after ChangeRail source updates.
- Diagnostics remain sanitized and actionable.

### Depends On
- `040-02-add-windows-wiring-backend`
- `010-05-add-verification-profiles-and-severity`

### Related
- `openspec/changes/enforce-windows-wiring-verification/`

## Change 2: `add-windows-git-safety-gates`

### Why
Generated, symlink and junction paths can accidentally expose ChangeRail source,
runtime state or credentials unless Git behavior is verified fail-closed.

### Goal
Add Git status, dry-run add and index checks for Windows wiring modes and
cleanup/rename scenarios.

### Acceptance
- Git safety covers generated, symlink and junction paths.
- Unsafe fallback evidence fails closed.
- Ignore rules remain minimal and do not hide project-owned source.

### Depends On
- `enforce-windows-wiring-verification`

### Related
- `openspec/changes/add-windows-git-safety-gates/`

## Result
ready for `$chrl-deliver`

## Next
- Выполнять после `040-02` в tracked runner plan
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из Git junction report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: verifier/drift/Git safety
  must enforce generated ownership and explicit link fallback gates.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
