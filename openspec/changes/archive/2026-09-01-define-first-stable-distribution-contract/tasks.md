## 1. Distribution contract

- [x] 1.1 Добавить deterministic generic source-distribution builder с exact
  Git commit, semver, license, reproducible gzip, SHA-256 и metadata sidecar.
- [x] 1.2 Добавить test-first smoke, который отклоняет invalid input и
  проверяет byte reproducibility, archive layout, version/license,
  source-revision metadata и checksum.

## 2. Durable release surface

- [x] 2.1 Документировать build/verify/publication contract в release
  discipline и согласовать public inventory/status docs без language-specific
  package claim.
- [x] 2.2 Добавить smoke ровно в core release inventory и сохранить extended
  suite отдельной без дублирования.

## 3. Verification

- [x] 3.1 Выполнить focused RED/GREEN source-distribution smoke и
  `python3 scripts/smoke-release-ci.py`.
- [x] 3.2 Выполнить strict OpenSpec validation, current public-surface scan и
  `git diff --check`; записать команды и observed outcomes.
