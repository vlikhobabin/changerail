# Добавить consumer profiles и severity в verify-project

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`010-core-release-contracts`

## Series Index
`05`

## Source
- Codex-first consumer намеренно не использовал часть legacy surfaces и имел
  известный project-wide OpenSpec debt.

## Summary
Сделать `verify-project` profile-aware и severity-aware, сохранив fail-closed
default: project policy может объявить surface required/optional/forbidden и
отдельно классифицировать baseline diagnostics, но не скрывать blocking failure.

## Acceptance
- Project profile объявляет Codex, Claude и legacy MCP surfaces как required,
  optional или forbidden.
- Checks имеют stable status/severity contract и machine-readable summary.
- Только non-blocking findings могут давать `pass-with-diagnostics`.
- Targeted card-owned OpenSpec validation остается обязательной.
- Project-wide baseline debt допускается как diagnostic только при явной
  tracked policy с видимым residual risk.
- Default profile сохраняет текущий строгий all-surfaces behavior.
- Positive/negative smokes покрывают Codex-only, all-surfaces, forbidden
  artifact и попытку ослабить mandatory check.

## Scope
- `bin/verify-project`, JSON output contract и project config/template docs.
- Verification specs и deterministic fixtures.

## Non-Goals
- Автоматическое исправление legacy OpenSpec debt.
- Native Windows path/link semantics: серии `030` и `040`.

## Depends On
- `010-02-establish-supported-python-runtime`
- `010-04-add-manifest-scope-and-handoff`

## Implementation Notes
- Разделить `status` и `severity`; `skip` не должен маскировать required check.
- Forbidden surface должен падать, если artifact присутствует.
- Не смешивать delivery auth advisory с structural verification outcome.

## Change Set
- none yet

## Verify
- Focused `verify-project` profile/severity smoke matrix.
- Generated project bootstrap/verify smoke.
- Release baseline и public-surface scans.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `bin/verify-project`
- `openspec/specs/changerail-project-verification/spec.md`
- `templates/project/openspec/config.yaml.tpl`

## Result
not started

## Next
- После `010-04` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z requirements нормализованы из consumer feedback.
