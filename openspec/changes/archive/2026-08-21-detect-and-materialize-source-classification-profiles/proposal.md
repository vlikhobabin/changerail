## Why

После определения profile schema проекту нужен безопасный operator workflow:
сначала неизменяющее обнаружение кандидатов, затем явный preview и только после
подтверждения materialization tracked classification. Detection не должно
само менять риск текущего payload.

## What Changes

- Добавить machine-readable `detect` для profile candidates с bounded signals,
  confidence, ambiguities и recommended action.
- По умолчанию определять технологии относительно tracked `HEAD`; разрешить
  explicit snapshot input для интеграции без чтения сети.
- Добавить `materialize --profile` с preview/diff до записи, idempotent no-op и
  отказом перезаписывать отличающийся project file.
- Поддержать explicit local profile path, прошедший ту же schema/checksum
  validation, без загрузки кода или remote data.
- Доказать, что detected-but-unaccepted candidate не влияет на preflight risk,
  а materialized classification влияет через существующий contract.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: command contracts для detection/materialization
  создают schema-valid source classification только после явного выбора.
- `changerail-project-verification`: project verification проверяет созданный
  classification file и provenance report.

## Impact

- новый source-classification profile helper/CLI и wrapper
- `scripts/changerail_review_preflight.py`
- synthetic mixed-stack detection/materialization smokes
- зависит от `define-source-classification-profile-contract`
