# Учитывать production-исходники 1С в review complexity guard

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Field validation в generic consumer-проекте 1С, 2026-08-18.
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`

## Summary
Текущий review preflight считает added production LOC только для ограниченного
набора суффиксов из `PRODUCTION_SUFFIXES`. Исходники модулей 1С `.bsl` и
иерархическая XML-выгрузка Конфигуратора не попадают в эту классификацию,
поэтому крупный production payload 1С может получить
`added_production_loc = 0` и обойти обязательное investigation.

Расширить complexity guard так, чтобы он fail-closed оценивал production-код и
метаданные 1С, но не считал тесты, fixtures, schemas, templates и произвольный
XML. Решение не должно сводиться к безусловному добавлению `.xml`: одна
структурная выгрузка управляемой формы может превышать текущий максимальный
authorization ceiling в 500 строк и сделать обычную доставку 1С практически
непроходимой. Нужна стабильная, объяснимая метрика или project-declared source
classification, совместимая с существующим investigation flow.

## Acceptance
- Exploration воспроизводит false-negative на synthetic consumer: более 300
  добавленных строк `.bsl` в production source сейчас дают
  `added_production_loc = 0` и не требуют investigation.
- Design определяет, как consumer объявляет production roots или source kinds
  для BSL и иерархической Designer XML-выгрузки без встраивания прикладных
  имен конфигураций в generic ChangeRail core.
- Добавленные production-модули `.bsl` в заявленном source root вносят вклад в
  complexity measure; `.bsl` в `test`, `tests`, `fixtures`, `examples` и
  других существующих non-production roots не учитываются.
- Designer XML учитывается только при доказанной production-классификации;
  generic XML schemas, templates, fixtures и документы не становятся
  production payload по одному суффиксу.
- Для BSL, Designer XML и смешанного payload результат содержит наблюдаемую
  детализацию по source kind и объясняет итоговое значение guard.
- Payload 1С выше default limit не может получить false-green без
  investigation; bounded authorization сохраняет exact successor binding и
  не превращается в неограниченный bypass.
- Design отдельно решает, как обрабатывать структурный XML, который штатно
  превышает текущий ceiling 500: meaningful line measure, отдельный bounded
  threshold или decomposition rule должны быть обоснованы и fail-closed.
- Существующая классификация Python, Go, JavaScript и executable helpers, а
  также их test/non-production исключения не меняют поведение.
- Focused smoke использует только синтетически созданные временные `.bsl` и XML
  fixtures; реальные конфигурации, выгрузки и клиентские данные в публичный
  репозиторий не добавляются.

## Non-Goals
- Встраивание правил конкретной конфигурации 1С в ChangeRail core.
- Парсинг BSL, Designer XML или проверка корректности метаданных.
- Замена независимого semantic review статическим подсчетом строк.
- Неограниченное повышение `production_loc_ceiling` для всех consumer-проектов.
- Хранение реальных 1С-выгрузок как regression fixtures.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `schemas/changerail-review-preflight-result.schema.json`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-contracts/spec.md`

## Result
not started

## Next
- explore source classification и bounded complexity metric для 1С

## Change Plan Notes
До перевода в `2.todo` проверить минимум два варианта: project-declared
production roots/source kinds и отдельную структурную метрику Designer XML.
Выбранный contract должен закрывать false-negative `.bsl`, не создавая
false-positive для произвольного XML и не делая типовую XML-выгрузку
автоматически недоставляемой.

## Log
- 2026-08-18T11:08:00Z карточка создана по результату field validation:
  complexity guard не классифицирует production source 1С и занижает payload
  до нуля.
