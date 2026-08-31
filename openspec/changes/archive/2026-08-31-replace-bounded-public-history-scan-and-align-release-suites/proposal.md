## Why

Исходная delivery-попытка исчерпала budget независимого review: её технические
acceptance checks прошли, но итоговый `NO-GO` выявил противоречие между
фактическим split release suites и нормативным требованием, которое всё ещё
относило one-command delivery regression к default core. Нужен clean linked
replacement от опубликованного safe base, который заново собирает scanner,
release suites, CI и оба нормативных контракта в один согласованный publish
unit.

## What Changes

- Реализовать bounded `HEAD` unique-blob history scanner с одним raw-history
  stream, одним persistent batch-object reader и focused public-safe fixture,
  проверяющим framing, lifecycle, attribution и runtime bounds.
- Сделать default release suite Linux-focused, вынести тяжёлые regressions в
  отдельную scheduled/manual `extended` suite и закрепить точные непересекающиеся
  inventories с full-history CI checkout.
- Оставить one-command delivery regression только в `extended`; его точный
  нормативный запуск —
  `python3 scripts/run-release-baseline.py --suite extended`.
- Синхронизировать public release/compatibility guidance и delta requirements
  `changerail-release-ci` и `changerail-release-discipline`, чтобы документация,
  runner и CI имели одного владельца для каждой проверки.
- Ограничить весь coherent implementation payload 300 added production LOC;
  не добавлять authority, release-ref CLI, dependency или wire/report schema.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-release-ci`: bounded history implementation, exact disjoint
  `core`/`extended` inventories, Linux-focused default CI, full checkout и
  отдельный scheduled/manual extended route становятся единым fail-closed
  release contract.
- `changerail-release-discipline`: public release guidance и нормативное
  ownership one-command delivery regression закрепляют его только за exact
  `extended` invocation и описывают текущую Linux-focused support boundary.

## Impact

Изменятся public scanner и focused fixture, source classification, local
release runner, default/extended GitHub Actions workflows, CI contract smoke,
release/compatibility docs и два OpenSpec contracts. Consumer repositories,
Windows runtime implementation и существующая
`changerail.public-surface-scan.v1` schema не изменяются. Старый unpublished
payload не переносится: implementation и все последующие evidence/manifest/
review должны быть свежими относительно safe published base.
