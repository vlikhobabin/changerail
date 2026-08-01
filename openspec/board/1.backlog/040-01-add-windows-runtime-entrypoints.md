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
provisional до `030-03`

## Summary
Реализовать выбранные Windows command shims и interpreter selection для
OpenSpec, verifier, manifest, verdict, runner и metrics helpers.

## Provisional Acceptance
- Extensionless POSIX wrapper не запускается напрямую через Win32 CreateProcess.
- Supported Windows shim корректно передает argv, exit code, cwd и environment.
- Paths со spaces и non-ASCII покрыты automated tests.
- Все helpers используют runtime contract серии `010`.
- Missing shell/interpreter/dependency дает actionable diagnostic.
- Existing POSIX entrypoints сохраняют compatibility.

## Depends On
- `030-03-freeze-native-windows-architecture`
- `010-02-establish-supported-python-runtime`

## Change Set
- none yet; перепланировать после `030-03`

## Verify
- Windows entrypoint fixture tests.
- Live smoke на обоих Windows hosts.
- Linux release baseline.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `bin/openspec`
- `bin/verify-project`

## Result
not started

## Next
- Mandatory refresh после `030-03`, затем `$changerail-ff`.

## Log
- 2026-08-01T15:07:29Z provisional card создана из Win32 wrapper report.
