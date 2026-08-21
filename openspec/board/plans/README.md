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
- `020-one-command-delivery-experience.json` - карточки `020-01`..`020-05`
  после exit audit серии `010`.
- `030-native-windows-discovery.json` - карточки `030-01`..`030-03` после exit
  audit серии `020` и ignored Windows lab readiness.
- `040-native-windows-implementation.json` - карточки `040-01`..`040-05` после
  exit audit серии `030` и полного refresh native Windows implementation cards.
- `050-field-validation-authorizations.json` - шесть exact bounded authorization
  sources после опубликованного field-validation investigation; prerequisite
  target invariant и основной implementation batch запускаются только после
  успешного завершения этого плана.
- `060-field-validation-implementation.json` - пять исходных field-validation
  карточек после опубликованных authorization sources и завершенного
  execution-target prerequisite; выполняются последовательно в одном workspace.
