## Why

Текущий history mode выполняет `ls-tree` для каждого reachable commit и
`git show <commit>:<path>` для каждого повторяющегося path. На release history
это превращает обязательный fail-closed public-safety gate в практически
неограниченную по числу Git-процессов операцию: focused real-checkout scan и
public-safe synthetic fixtures не укладываются в 30 секунд.

## What Changes

- Зафиксировать точную семантику release ref и полное покрытие всех уникальных
  public blobs, достижимых из него, с сохранением commit/path attribution.
- Выбрать bounded batching/caching design, Git framing и fail-closed lifecycle
  для будущей реализации, не изменяя production scanner в этой change.
- Определить public-safe benchmark matrix, runtime ceilings и regression floor.
- Назвать один exact implementation successor и проверить, нужна ли ему
  отдельная authorization card по ChangeRail complexity boundary.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-release-ci`: обязательный reachable-history public-safety gate
  получает измеримый bounded-runtime и fail-closed implementation contract.

## Impact

Эта change изменяет только tracked OpenSpec decision/spec artifacts и board
metadata. Она не изменяет `scripts/public-surface-scan.py`, release baseline,
CI workflow или smoke tests. Consumer-project behavior и wire protocols не
затрагиваются. Реализация будет отдельной successor-карточкой.
