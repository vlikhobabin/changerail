# Воспроизвести Windows runtime, wiring и Git behavior

## Status
2.todo

## Owner
ChangeRail core + operator

## OpenSpec Stage
story

## Series
`030-native-windows-discovery`

## Series Index
`02`

## Source
- Consolidated native Windows reports от 2026-08-01.

## Summary
На обоих Windows hosts воспроизвести три исходных дефекта и сравнить candidate
strategies для directory/file wiring, wrapper invocation, Git staging, drift и
upgrade behavior.

## Acceptance
- Проверен direct `os.symlink` без elevation и с доступным Developer Mode.
- Проверены junction behavior и `git status`/`git add --dry-run` traversal.
- Проверен direct subprocess launch extensionless `bin/openspec` и варианты
  `.cmd`, PowerShell, Python и explicit bash invocation.
- Проверены file links отдельно от directory links.
- Для generated copy измерены drift detection и source update behavior.
- Каждый probe выполнен на `windows-host-a` и `windows-host-b` либо имеет
  explicit not-applicable reason.
- Создана sanitized comparison table с security, portability, Git и operator
  trade-offs.

## Scope
- Disposable consumer fixture и remote probe runner.
- Evidence, достаточное для architecture decision.

## Non-Goals
- Выбор architecture до получения результатов.
- Изменение реальных consumer worktrees.

## Depends On
- `030-01-establish-windows-lab-and-support-matrix`

## Implementation Notes
- Использовать `git ls-files`, porcelain status и index inspection, а не только
  console display.
- Проверять checkout/clone повторно: generated local wiring и tracked wiring
  имеют разные lifecycle semantics.

## Change Set
- none yet

## Verify
- Structured probe report с двумя host results.
- Repeatability run после полного cleanup.
- Public-surface scan sanitized report/fixtures.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `scripts/smoke-wiring-discovery.py`

## Result
ready for `$chrl-deliver`

## Next
- Выполнять после `030-01`; передать comparison evidence в `030-03`.

## Log
- 2026-08-01T15:07:29Z три исходных Windows reports объединены в один research scope.
- 2026-08-02T05:48:42Z переведена в `2.todo` после readiness pass: оба
  Windows hosts доступны через ignored inventory, story зависит от lab protocol
  и support matrix из `030-01`.
