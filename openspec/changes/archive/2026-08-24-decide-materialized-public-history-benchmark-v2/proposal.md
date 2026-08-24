## Why

Опубликованный `history-fixture-v1` фиксирует только fingerprint и
cardinalities; ни один tracked source не позволяет независимо материализовать
его exact preimage. Поэтому остановленный clean replacement не может доказать
будущий benchmark GREEN, а новый fixture authority должен быть опубликован до
появления следующего scanner candidate.

## What Changes

- Объявить `history-fixture-v1` только историческим и выбрать новый
  `history-fixture-v2` с явным tracked recipe и deterministic Git materializer.
- Потребовать byte-identical canonical realization transcripts и fixture
  fingerprints от двух materializations в разных fresh roots.
- Закрепить recipe schema, recipe, materializer, realization transcript,
  benchmark harness и self-tests через detached authority record без
  self-reference.
- Сохранить independent legacy oracle на exact published commit
  `ccccb62562e1646b595119edd3326763860f14a7`, а также scale, semantic cases,
  timing thresholds, CV rule и RSS limits из v1.
- Зафиксировать publish order и exact authorization chain для materialization
  fixture, bounded authorization и scanner implementation.
- Оставить change decision-only: ноль production/test/runtime LOC и никаких
  history scan, benchmark, full release baseline, successor card, archive,
  review, commit или push.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: заменить зависимость от нематериализуемого v1 на
  publish-before-candidate fixture authority v2 и exact successor/preflight
  lineage.

## Impact

- Сейчас затронуты только investigation card и один OpenSpec decision change.
- Будущий scope ограничен tracked fixture authority data и verification tools,
  существующими public-history scanner/baseline runner, release-CI contract и
  focused tests.
- Текущий change не меняет production/test/runtime LOC, CLI, schema или
  consumer behavior. Будущая fixture schema является internal verification
  data, а не consumer wire protocol или publish authority.
