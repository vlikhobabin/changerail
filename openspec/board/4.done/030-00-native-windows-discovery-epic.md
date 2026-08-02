# Серия 030: Исследование native Windows support

## Status
4.done

## Owner
ChangeRail core + operator

## OpenSpec Stage
epic

## Series
`030-native-windows-discovery`

## Series Index
`00`

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- Три независимых native Windows failure class: symlink privilege, Git
  junction traversal и Win32 execution extensionless wrapper.
- Operator decision: native Windows support обязателен.

## Summary
До реализации получить воспроизводимые данные с двух operator-managed native
Windows hosts, определить support matrix и выбрать одну проверяемую wiring,
runtime и Git tracking architecture.

## Series Goal
Завершить серию утвержденным Windows architecture decision и executable test
plan. Реализация серии `040` не должна опираться на предположения о junction,
symlink, shell, Git или Python behavior.

## Entry Gate
- Серия `010-core-release-contracts` завершена.
- Серия `020-one-command-delivery-experience` завершена.
- Runtime/bootstrap и verification profile contracts повторно прочитаны.
- Доступ к двум Windows hosts проверен оператором; hostnames, usernames,
  credentials и private paths записаны только в ignored operator inventory.

## Research Principles
- Проверять native Windows, а не подменять его WSL-only результатами.
- На каждом host фиксировать Windows edition/build, filesystem, Git, Python,
  shell, Developer Mode/elevation и Codex/OpenSpec prerequisites.
- Все tracked evidence делать generic и sanitized; raw SSH/session logs
  оставлять ignored.
- Исследовать least-privilege path как default и elevated mode отдельно.
- Не модифицировать реальные consumer repositories для destructive probes;
  использовать disposable test workspaces.

## Candidate Strategies To Compare
- Native symlinks при доступном Developer Mode.
- Directory junctions плюс generated/untracked wiring policy.
- Generated copies с explicit pin/drift verification.
- Small `.cmd`/PowerShell/Python shims для file entrypoints.
- Git Bash invocation как compatibility layer, но не как неявная зависимость.

## Series Cards
1. `030-01-establish-windows-lab-and-support-matrix.md`
2. `030-02-reproduce-windows-runtime-wiring-and-git-behavior.md`
3. `030-03-freeze-native-windows-architecture.md`

## Exit Gate
- Все три исходных failure classes воспроизведены или опровергнуты на двух hosts.
- Выбран default и fallback wiring/runtime model.
- Security, Git tracking, drift и upgrade trade-offs записаны.
- Серия `040` полностью переоценена: cards могут быть объединены, разделены,
  переупорядочены или отменены до перехода первой из них в `2.todo`.

## Related
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `docs/compatibility.md`
- `bin/bootstrap-project`
- `bin/verify-project`

## Result
done; series `030` delivered by tracked runner plan

## Next
- Использовать frozen native Windows architecture как entry gate для серии
  `040-native-windows-implementation`.

## Log
- 2026-08-01T15:07:29Z native Windows support выделен в research-first series.
- 2026-08-02T00:58:19Z exit audit после `020` прошел, но local SSH config и
  ignored inventory не содержат готового mapping для двух Windows hosts; серию
  нельзя запускать non-interactive runner-ом до operator inventory.
- 2026-08-02T05:48:42Z readiness обновлен после operator SSH handoff: ignored
  inventory заполнен двумя generic Windows host ids, SSH/Git/Python prerequisite
  подтвержден на обоих hosts, private connection data остается ignored.
- 2026-08-02T08:16:40Z tracked runner plan `030-native-windows-discovery`
  завершил `030-01`..`030-03` с результатом `DELIVERED`; workspace clean,
  `HEAD == origin/main`.
- 2026-08-02T08:24:42Z exit audit после серии `030` прошел: OpenSpec 20/20,
  public-surface current/history scans clean, release baseline 27/27.
