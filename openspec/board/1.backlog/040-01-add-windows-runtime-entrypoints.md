# Добавить native Windows runtime entrypoints

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`01`

## Planning State
refreshed after `030-03`; pending deliver-ready decomposition

## Source
- `030-03-freeze-native-windows-architecture`
- `010-02-establish-supported-python-runtime`

## Summary
Реализовать tracked `.cmd` entrypoints и runtime invocation semantics для
OpenSpec and ChangeRail helper commands on native Windows, preserving existing
POSIX entrypoints.

## Acceptance
- `bin/*.cmd` wrappers exist for supported Windows helper surfaces: OpenSpec,
  `changerail-python`, `verify-project`, `changerail-review-verdict`,
  `changerail-evidence`, delivery runner and metrics.
- `.cmd` wrappers preserve argv, exit code, cwd and environment.
- Paths with spaces and non-ASCII are covered by deterministic tests.
- OpenSpec Windows launch uses the same pinned OpenSpec version contract and
  does not call extensionless POSIX wrapper or implicit Bash.
- Python-backed helpers use the shared Python runtime selector and emit
  actionable diagnostics for missing Python, unsupported Python or missing
  runtime dependency.
- PowerShell remains diagnostic/explicit fallback, not the primary default.
- Existing POSIX entrypoints keep compatibility.

## Depends On
- `030-03-freeze-native-windows-architecture`
- `010-02-establish-supported-python-runtime`

## Change Set
- none yet; run `$changerail-ff` after `030-03` publish

## Verify
- Deterministic Windows entrypoint fixtures for argv, cwd, env, exit code,
  spaces and non-ASCII paths.
- Negative fixtures for direct extensionless launch and implicit Bash
  assumptions.
- Live smoke on both Windows hosts or explicit blocker/caveat.
- Existing Linux/POSIX helper regression checks and release baseline.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `bin/openspec`
- `bin/changerail-python`
- `bin/verify-project`
- `bin/changerail-review-verdict`
- `bin/changerail-evidence`

## Result
refreshed; implementation not started

## Next
- После publish `030-03`: `$changerail-ff openspec/board/1.backlog/040-01-add-windows-runtime-entrypoints.md`

## Log
- 2026-08-01T15:07:29Z provisional card создана из Win32 wrapper report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: `.cmd` wrappers selected as
  native Windows runtime default.
