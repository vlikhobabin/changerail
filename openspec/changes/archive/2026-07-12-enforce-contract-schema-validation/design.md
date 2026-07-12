## Context

Репозиторий уже публикует Draft 2020-12 schemas в `schemas/` для delivery
manifest и review verdict contracts. Python helpers вручную дублировали subset
этих rules, поэтому пропускали schema behavior: `format`,
`additionalProperties`, conditionals и nested field types. `jsonschema`
доступен в local runtime, где запускаются helper smoke tests.

## Goals / Non-Goals

**Goals:**
- Каждый helper валидирует документ по tracked canonical schema до применения
  helper-specific semantic invariants.
- Использовать `jsonschema.Draft202012Validator` с `FormatChecker`.
- Выдавать sanitized structured diagnostics на validation failures.
- Оставить semantic checks читаемыми и отделенными от schema mechanics.

**Non-Goals:**
- Не менять schema ids или file names.
- Не валидировать ignored runtime state вне указанного document.
- Не заменять ChangeRail semantic checks только schema validation.

## Decisions

- Загружать schemas по repository-relative path от helper script location. Это
  сохраняет source-of-truth в public repo и работает для tracked wrappers.
- Преобразовывать jsonschema errors в короткие path-qualified messages. CLI
  helpers уже выводят structured JSON diagnostics; detail не должен включать
  raw document payloads.
- Оставить verdict-specific checks для result/findings consistency и freshness
  в `_validate_verdict_semantics`. Manifest operation invariants держать в
  schema conditionals или небольшом semantic layer, если schema expressiveness
  недостаточно.
- Добавить negative smoke fixtures вместо опоры только на happy-path helper
  calls.

## Risks / Trade-offs

- [Risk] Missing `jsonschema` dependency сделает validation недоступной.
  Mitigation: helpers fail closed со structured input/validation diagnostic,
  вместо принятия documents.
- [Risk] Schema validation может менять формулировки между versions.
  Mitigation: smoke tests проверяют стабильные field/path fragments, а не весь
  raw error string.
- [Risk] Publishing code может зависеть от legacy malformed runtime files.
  Mitigation: fail closed намеренно применяется к runtime contracts; operators
  могут regenerated manifests или verdicts из текущего workspace.
