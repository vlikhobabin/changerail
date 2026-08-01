# Планы для package runner

Здесь живут tracked delivery plans, когда серия карточек готова к запуску через
package runner.

## Правила

- План является public-safe input contract, а не runtime status.
- Runtime statuses, locks, child logs и reviewer verdicts остаются только в
  ignored `.runtime/changerail/`.
- План содержит только executable story cards; coordination-only epic cards
  `*-00-*` не включаются.
- Card refs должны быть filename-only или repository-relative public paths, без
  private workspace names, absolute paths, credentials или hostnames.
- Для одной ChangeRail repo-local серии используйте workspace alias
  `changerail=.` и `max_parallel: 1`.
- Если следующая серия имеет refresh gate, ее plan создается только после exit
  audit предыдущей серии.

## Текущие планы

- `010-core-release-contracts.json` - карточки `010-02`..`010-05` после bootstrap
  delivery карточки `010-01`.
