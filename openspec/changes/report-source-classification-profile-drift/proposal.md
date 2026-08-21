## Why

Даже после materialization repository может получить вероятные исходники,
которые не покрыты принятой classification, либо profile и project overrides
могут разойтись. Проверка должна объяснять drift, не включая автоматически
новые правила и не меняя risk calculation текущего review.

## What Changes

- Добавить value-free `check` report с profile provenance, effective rules,
  covered/excluded roots и bounded uncovered-source diagnostics.
- Различать advisory low-confidence candidate и blocking divergence с явно
  подтвержденным profile или несовместимым measurement rule.
- Зафиксировать deterministic precedence profile → project overrides и
  fail-closed конфликт merge.
- Интегрировать check в project verification и review-preflight diagnostics,
  сохранив расчет риска только по tracked classification.
- Обновить templates/docs для потока `detect -> review -> materialize -> check`
  и безопасной явной migration существующего файла.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: schema-backed drift/provenance report объясняет
  effective source classification без source contents.
- `changerail-project-verification`: verifier различает advisory detection и
  blocking confirmed-profile drift.
- `changerail-project-templates`: bootstrap guidance описывает явный profile
  lifecycle и запрет скрытого включения detected stack.

## Impact

- source-classification profile helper/CLI
- `bin/verify-project` и `scripts/changerail_review_preflight.py`
- template docs, contract inventory and synthetic drift smokes
- зависит от `detect-and-materialize-source-classification-profiles`
