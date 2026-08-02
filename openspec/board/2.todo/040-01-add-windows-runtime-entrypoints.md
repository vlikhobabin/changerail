# Добавить native Windows runtime entrypoints

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`040-native-windows-implementation`

## Series Index
`01`

## Planning State
deliver-ready after `030` exit audit; OpenSpec artifacts deferred to internal
`ff` during `$chrl-deliver`

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
- `openspec/changes/add-native-windows-command-wrappers/` (planned)
- `openspec/changes/test-native-windows-entrypoints/` (planned)

## Verify
- Deterministic Windows entrypoint fixtures for argv, cwd, env, exit code,
  spaces and non-ASCII paths.
- Negative fixtures for direct extensionless launch and implicit Bash
  assumptions.
- Live smoke on both Windows hosts or explicit blocker/caveat.
- Existing Linux/POSIX helper regression checks and release baseline.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/4.done/030-03-freeze-native-windows-architecture.md`
- `bin/openspec`
- `bin/changerail-python`
- `bin/verify-project`
- `bin/changerail-review-verdict`
- `bin/changerail-evidence`

## Change 1: `add-native-windows-command-wrappers`

### Why
Native Windows cannot execute extensionless POSIX wrappers as process
entrypoints, so supported helper surfaces need tracked Windows-native command
wrappers.

### Goal
Add `.cmd` wrappers for the supported helper commands while preserving existing
POSIX behavior and the shared Python runtime contract.

### Acceptance
- Supported helper commands have tracked `.cmd` wrappers.
- Wrappers preserve argv, cwd, environment and exit code.
- Missing or unsupported Python diagnostics remain actionable.

### Depends On
- none

### Related
- `openspec/changes/add-native-windows-command-wrappers/`

## Change 2: `test-native-windows-entrypoints`

### Why
The command wrappers must be regression-tested for Windows path, quoting and
process-launch behavior before wiring or bootstrap code depends on them.

### Goal
Add deterministic tests for Windows command invocation semantics and Linux/POSIX
regression coverage for existing wrappers.

### Acceptance
- Tests cover argv, cwd, env, exit code, spaces and non-ASCII paths.
- Negative coverage documents extensionless launch and implicit Bash
  assumptions.
- Linux release baseline remains green.

### Depends On
- `add-native-windows-command-wrappers`

### Related
- `openspec/changes/test-native-windows-entrypoints/`

## Result
ready for `$chrl-deliver`

## Next
- Запустить первой карточкой tracked runner plan
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из Win32 wrapper report.
- 2026-08-02T07:27:00Z refreshed against `030-03`: `.cmd` wrappers selected as
  native Windows runtime default.
- 2026-08-02T08:24:42Z переведена в `2.todo` после exit audit `030`; planned
  changes записаны, artifacts будут созданы internal `ff` phase.
