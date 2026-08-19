# Учитывать production-исходники 1С в review complexity guard

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

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

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

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
- `define-review-preflight-source-classification`
- `count-review-preflight-bsl-production-loc`
- `measure-review-preflight-designer-xml`

## Verify
- `./bin/openspec validate "define-review-preflight-source-classification" --strict`
- `./bin/openspec validate "count-review-preflight-bsl-production-loc" --strict`
- `./bin/openspec validate "measure-review-preflight-designer-xml" --strict`
- `./bin/openspec validate --all --strict`
- `git diff --check`
- `python3 scripts/public-surface-scan.py`

## Archive
- not started

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `schemas/changerail-review-preflight-result.schema.json`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/changes/define-review-preflight-source-classification/`
- `openspec/changes/count-review-preflight-bsl-production-loc/`
- `openspec/changes/measure-review-preflight-designer-xml/`

## Result
not started

## Next
- `$changerail-do openspec/board/2.todo/count-1c-production-source-in-review-complexity.md`

## Change 1: `define-review-preflight-source-classification`

### Why
Review preflight needs project-declared production source classification before
domain-specific formats can be counted without hard-coding consumer application
names in generic ChangeRail core.

### Goal
Add a deterministic optional source-classification contract and preflight
breakdown output that lets consumers declare production roots/source kinds while
preserving legacy generic classification when absent.

### Scope
- Add schema-backed loading for `.changerail/source-classification.yaml` or the
  implemented equivalent.
- Validate repository-relative roots and fail closed on unsafe or malformed
  classification.
- Extend review preflight result detail by source kind.
- Document the optional consumer-owned classification in contracts/templates.

### Acceptance
- Missing classification keeps existing generic production suffix behavior.
- Valid classification makes declared source kinds eligible for production
  complexity under safe repository-relative roots.
- Unsafe or schema-invalid classification blocks preflight before LLM review.
- Preflight result exposes bounded source-kind breakdown without raw source
  content.

### Depends On
- none

### Related
- `openspec/changes/define-review-preflight-source-classification/`

## Change 2: `count-review-preflight-bsl-production-loc`

### Why
Production `.bsl` additions can currently bypass investigation because the
complexity guard reports zero production LOC for BSL source.

### Goal
Count added BSL lines under declared production roots while keeping BSL tests,
fixtures, examples and other non-production paths excluded.

### Scope
- Use source classification from Change 1 for `.bsl` production proof.
- Count `.bsl` with the same line-based complexity strategy as common source
  files.
- Add synthetic RED/GREEN smoke coverage for production and non-production BSL.
- Preserve existing language suffix, Go test and executable-helper behavior.

### Acceptance
- More than 300 added production `.bsl` lines returns
  `investigation-required` unless valid bounded authorization applies.
- `.bsl` under existing non-production roots does not contribute to
  `added_production_loc`.
- Source-kind breakdown explains the BSL contribution.
- Existing Python, Go, JavaScript and executable helper classification remains
  unchanged.

### Depends On
- `define-review-preflight-source-classification`

### Related
- `openspec/changes/count-review-preflight-bsl-production-loc/`

## Change 3: `measure-review-preflight-designer-xml`

### Why
Designer XML can be production metadata, but suffix-only XML counting creates
false positives and raw line count can overstate hierarchical Designer export
complexity.

### Goal
Count only classified production Designer XML using a fail-closed structural
complexity measure and report mixed BSL/XML guard detail.

### Scope
- Use source classification from Change 1 for Designer XML production proof.
- Add an `xml-structure` or equivalent effective complexity strategy for
  declared Designer XML.
- Keep generic XML schemas, templates, fixtures, docs, examples and OpenSpec
  XML out of production complexity by default.
- Preserve default and published-authorization ceilings using effective
  complexity, with fallback/block behavior when measurement is unsafe.
- Add synthetic XML and mixed BSL/XML smoke coverage.

### Acceptance
- Declared production Designer XML contributes effective complexity and source
  kind detail.
- Generic or unclassified `.xml` does not count as production by suffix alone.
- Verbose structural XML can be evaluated by effective complexity rather than
  raw line count when the helper can prove the measure safely.
- Malformed or unmeasurable classified XML falls back to raw added lines or
  blocks; it never reports zero silently.
- Mixed BSL/XML payloads report separate source-kind breakdown entries and an
  aggregate guard value.

### Depends On
- `define-review-preflight-source-classification`
- `count-review-preflight-bsl-production-loc`

### Related
- `openspec/changes/measure-review-preflight-designer-xml/`

## Log
- 2026-08-18T11:08:00Z карточка создана по результату field validation:
  complexity guard не классифицирует production source 1С и занижает payload
  до нуля.
- 2026-08-19T06:38:57Z `$chrl-ff` разложил story на три ordered OpenSpec
  changes, создал apply-ready artifacts и перенес карточку в `2.todo`.
