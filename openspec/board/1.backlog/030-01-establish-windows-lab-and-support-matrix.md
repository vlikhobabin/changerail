# Подготовить Windows lab и support matrix

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`030-native-windows-discovery`

## Series Index
`01`

## Source
- Доступны два operator-managed native Windows laptop для SSH исследований.

## Summary
Определить безопасный remote research protocol, собрать sanitized capability
matrix двух hosts и подготовить disposable workspaces для воспроизводимых
Windows probes.

## Acceptance
- Для каждого host зафиксированы sanitized OS/filesystem/Git/Python/shell и
  privilege capabilities.
- Проверены SSH access, non-interactive command execution и безопасная передача
  test fixtures без записи credentials в repository.
- Созданы disposable test roots вне реальных consumer repositories.
- Определены cleanup, timeout и evidence retention rules.
- Tracked report использует generic `windows-host-a`/`windows-host-b`; mapping и
  raw connection data остаются ignored.
- Lab protocol запрещает elevation без отдельного operator action.

## Scope
- Research harness/protocol и compatibility matrix.
- Ignored operator inventory schema/notes при необходимости.

## Non-Goals
- Изменение ChangeRail runtime или bootstrap behavior.
- Постоянная CI infrastructure registration.

## Depends On
- Серия `010-core-release-contracts` завершена.

## Implementation Notes
- Команды должны быть idempotent и ограничены disposable workspace.
- Retained public evidence содержит command class и outcome, но не host identity.

## Change Set
- none yet

## Verify
- Dry-run/local validation research harness.
- Non-destructive probe на обоих hosts.
- Public-surface scan sanitized tracked outputs.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `docs/compatibility.md`

## Result
not started

## Next
- После подготовки lab выполнить `030-02` на обоих hosts.

## Log
- 2026-08-01T15:07:29Z карточка создана для controlled Windows research.
