## Why

Static TOML/wiring checks не подтверждают effective Codex runtime, а generated
`AGENTS.md` уже занимает около 26 KiB без deterministic instruction-budget
gate. Consumer должен видеть эти риски до silent truncation или ошибочного
runtime-ready claim.

## What Changes

- Добавить opt-in Codex runtime diagnostic отдельно от static verifier result.
- Классифицировать effective config/trust/MCP/instruction evidence и
  unsupported/unavailable probes.
- Хранить raw runtime output только в ignored state и публиковать redacted
  summary без local paths или credential data.
- Явно рендерить tracked `project_doc_max_bytes` budget.
- Предупреждать при 85% budget и fail closed при превышении.
- Добавить deterministic boundary, redaction и false-runtime-proof fixtures.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-project-bootstrap`: generated Codex config и guidance получают
  explicit instruction budget и runtime-diagnostic handoff.
- `changerail-project-templates`: templates различают static и runtime evidence
  и задают tracked budget.
- `changerail-project-verification`: verifier измеряет instruction input и
  запускает runtime probes только по explicit opt-in.

## Impact

Затрагиваются templates, `bin/verify-project`, возможно отдельный runtime helper,
bootstrap/verify smoke и compatibility/adoption docs. Default verification не
получает network dependency и не читает credential contents.
