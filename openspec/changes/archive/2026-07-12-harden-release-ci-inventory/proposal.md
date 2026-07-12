## Why

Release CI уже проверяет базовый ChangeRail workflow, но часть tracked
исполняемой поверхности выпала из gate: новые runner/metrics/fingerprint smoke
и contract schema coverage не запускаются автоматически, а lint gap позволил
оставить unused imports. Перед публичным release gate должен закрывать весь
актуальный набор helper-ов, schemas и smoke checks без ручного устаревающего
списка.

## What Changes

- Расширить release CI так, чтобы Python syntax gate автоматически покрывал
  tracked executable helpers и smoke scripts under `bin/` и `scripts/`.
- Добавить согласованный lint gate и устранить текущие lint failures.
- Запускать focused smoke checks для delivery runner, delivery metrics,
  review fingerprint, review verdict validation, manifest derivation, bootstrap,
  verify, wiring, archive diagnostics, release contract и drift fixture.
- Проверять все public contract schemas через parse, Draft 2020-12 meta-schema
  validation и positive/negative fixture paths, чтобы helper/schema drift
  приводил к red CI.
- Сделать `scripts/smoke-release-ci.py` inventory-driven: проверять полный
  обязательный command inventory workflow, а не только отдельные строки.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-release-ci`: release CI должен автоматически покрывать tracked
  Python helpers/smokes, lint, полный smoke inventory и schema validation.
- `changerail-contracts`: release-facing checks должны валидировать весь
  публичный schema set как canonical Draft 2020-12 contracts.

## Impact

- `.github/workflows/changerail-ci.yml`
- `scripts/smoke-release-ci.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `scripts/smoke-review-fingerprint.py`
- `scripts/smoke-drift.py`
- `scripts/changerail_contract_schema.py`
- `schemas/*.schema.json`
- release verification documentation that names mandatory CI checks
