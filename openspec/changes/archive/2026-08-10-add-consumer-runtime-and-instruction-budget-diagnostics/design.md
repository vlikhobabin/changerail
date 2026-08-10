## Context

`verify-project` валидирует tracked Codex TOML, trust entry и MCP scope, но этот
PASS является static claim. Effective CLI может загрузить другой `CODEX_HOME`
или managed policy. Одновременно generated `AGENTS.md` имеет размер около
26 KiB, а template не задает и verifier не контролирует instruction budget.

## Goals / Non-Goals

**Goals:**
- явно разделить static и runtime evidence;
- дать opt-in supported Codex diagnostic без credential leakage;
- сделать instruction budget tracked и deterministic;
- дать раннюю actionable remediation.

**Non-Goals:**
- делать Codex runtime/network обязательным для default verifier;
- объявлять один CLI subcommand вечным universal probe;
- коммитить raw doctor/prompt output;
- автоматически увеличивать budget при превышении.

## Decisions

### Static result wording

Default verifier продолжает существующие checks, но summary называет их static
configuration/wiring verification. Он не утверждает effective runtime readiness.

### Opt-in runtime diagnostics

`verify-project --runtime-diagnostics` запускает supported probes из consumer
cwd с declared effective `CODEX_HOME`. Initial adapter использует structured
`codex doctor --json` для loaded config/trust/MCP/auth classes и
`codex debug prompt-input` для discovered instructions, когда команды доступны
в supported Codex version.

Unavailable/unsupported/invalid probe output дает explicit non-success
diagnostic. Raw output записывается только под ignored
`.runtime/changerail/diagnostics/`; public/JSON summary содержит allowlisted
fields и redacted path classes.

### Tracked instruction budget

Generated `.codex/config.toml` явно задает `project_doc_max_bytes = 32768` для
стабильного consumer contract. Verifier измеряет UTF-8 bytes effective generated
`AGENTS.md`: ниже 85% — pass, от 85% до budget — non-blocking warning, выше
budget — blocking failure.

Альтернатива только с hard-coded verifier threshold отклонена: tracked Codex
config и verifier могли бы расходиться.

### Remediation

Diagnostic сообщает measured bytes, budget и безопасные варианты: сократить
project rules, обновить generated shared block, вынести operational detail в
skills/docs или явно изменить tracked budget после review. Автоматического
изменения config нет.

## Risks / Trade-offs

- [Codex probe schema меняется] -> version-aware adapter, schema validation и
  unsupported status вместо best-effort parsing.
- [Raw runtime report содержит local paths] -> ignored storage и allowlisted
  summary; public-surface negative fixture.
- [32 KiB со временем станет неверным implicit default] -> значение explicit в
  tracked consumer config и compatibility matrix, а не inferred from CLI.

## Migration Plan

1. Добавить explicit budget в template и static size checks.
2. Добавить runtime adapter/ignored evidence contract.
3. Добавить boundary/redaction/version fixtures.
4. Обновить compatibility/adoption docs; existing consumers without explicit
   budget получают documented compatibility default until migrated.

## Open Questions

- none
