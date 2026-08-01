# Native Windows bug reports заменены research-first серией

## Status
5.canceled

## Owner
ChangeRail core + operator

## OpenSpec Stage
superseded

## Source
- Bug reports о symlink privilege, Git junction traversal и Win32 wrapper
  execution.

## Summary
Три исходные карточки описывали наблюдаемые симптомы одной platform-level
проблемы. Исправлять их независимо нельзя: выбор wiring strategy определяет
bootstrap, Git ownership, verification, drift и entrypoint design.

## Cancellation Reason
- Native Windows support подтвержден как обязательный product scope.
- Симптомные карточки заменены отдельной discovery series и provisional
  implementation series.
- Implementation backlog должен быть переписан после evidence с двух Windows
  hosts, поэтому исходные acceptance criteria не считаются готовым design.

## Superseded By
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`

## Preserved Failure Classes
- Non-elevated directory-link creation.
- Git staging traversal through directory junctions.
- Direct Win32 execution of extensionless POSIX wrapper.

## Result
закрыто как superseded; failure classes сохранены в сериях `030` и `040`

## Next
- Начать native Windows work с controlled lab card `030-01`.

## Log
- 2026-08-01T15:07:29Z три Windows reports объединены и заменены research-first plan.
