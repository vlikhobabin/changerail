## Context

Серия `060` добавляет maintenance harness поверх существующего ChangeRail
workflow. Первый delivery unit должен дать schema-backed source of truth для
repository knowledge без навязывания consumer-у layout вроде `docs/` и без
scheduled mutation.

Текущие public wire contracts живут в `schemas/`, валидируются shared helper-ом
`scripts/changerail_contract_schema.py` и описаны в `docs/changerail-contracts.md`.
Новый catalog/policy contract должен следовать тому же pattern: tracked JSON
Schema, focused smoke fixtures, fail-closed diagnostics и public-safe examples.

## Goals / Non-Goals

**Goals:**
- Опубликовать schema ids `changerail.repository-knowledge.v1` и
  `changerail.maintenance-policy.v1`.
- Задать default tracked paths `.changerail/knowledge.yaml` и
  `.changerail/maintenance.yaml`, оставив consumer overrides для CLI phase.
- Описать catalog record fields, enum values, null/empty semantics и safe path
  validation.
- Добавить shared loader, который сначала читает YAML через PyYAML, затем
  валидирует Draft 2020-12 schemas и semantic path checks.
- Добавить public-safe fixtures и минимальный dogfood catalog без runtime state.

**Non-Goals:**
- Не добавлять deterministic scan, finding lifecycle, scheduler adapters или
  agent triage.
- Не запускать arbitrary generator commands из policy.
- Не менять delivery runner, review gate или existing consumers без opt-in
  `.changerail/maintenance.yaml`.

## Decisions

- **Two schemas, one loader module.** Catalog и policy имеют разные schema ids,
  потому что catalog описывает knowledge records, а policy описывает operational
  defaults. Shared loader уменьшает duplication и дает общий diagnostics
  contract.
- **YAML parse before schema validation.** PyYAML является runtime dependency,
  поэтому helper читает user-facing YAML, а JSON Schema остается public
  canonical contract.
- **Repository-relative path normalization in semantic validation.** JSON
  Schema проверяет shape, а Python loader отклоняет absolute paths, traversal и
  root escape после нормализации относительно repository root.
- **No implicit consumer impact.** Отсутствующая `.changerail/maintenance.yaml`
  означает no-op для будущих maintenance checks; catalog validation запускается
  только explicit helper-ом или будущим opt-in gate.
- **Fixtures under `fixtures/repository-knowledge/`.** Fixtures остаются tracked,
  public-safe и используются smoke test-ом без обращения к runtime evidence.

## Risks / Trade-offs

- **Schema becomes too prescriptive** -> contract фиксирует fields и enum values,
  но не требует directory layout или конкретную документационную taxonomy сверх
  supported `type` values.
- **Path checks diverge across commands** -> normalization lives in one shared
  module and future CLI/index code reuses it.
- **Dogfood catalog goes stale before deterministic scan exists** -> first
  change only validates shape and paths; index freshness belongs to the second
  change.
