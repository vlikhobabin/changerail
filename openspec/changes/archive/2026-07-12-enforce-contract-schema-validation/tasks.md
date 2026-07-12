## 1. Schema Validation

- [x] 1.1 Добавить shared Draft 2020-12 schema loading/validation helpers в manifest и verdict validation paths.
- [x] 1.2 Валидировать delivery manifests по `schemas/changerail-delivery-manifest.schema.json` до manifest semantic checks.
- [x] 1.3 Валидировать review verdicts по `schemas/changerail-review-verdict.schema.json` до verdict semantic и freshness checks.
- [x] 1.4 Сохранить helper diagnostics structured и sanitized для validation и input errors.

## 2. Regression Coverage

- [x] 2.1 Добавить manifest negative fixtures для `additionalProperties`, invalid date-time, wrong nested types и missing conditional operation fields.
- [x] 2.2 Добавить verdict negative fixtures для `additionalProperties`, invalid date-time, wrong nested types и malformed `go` verdict publish freshness validation.
- [x] 2.3 Проверить, что tests используют тот же helper validation code path, что и CLI.

## 3. Docs And Verification

- [x] 3.1 Обновить contract docs и review verdict reference с schema-backed fail-closed validation behavior.
- [x] 3.2 Run `python3 scripts/smoke-delivery-manifest-derive.py`.
- [x] 3.3 Run `python3 scripts/smoke-review-verdict-validation.py`.
- [x] 3.4 Run `openspec validate enforce-contract-schema-validation --strict`.
- [x] 3.5 Run `git diff --check`.
