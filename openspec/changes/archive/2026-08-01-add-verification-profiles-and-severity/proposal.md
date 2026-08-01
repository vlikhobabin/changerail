## Why

`bin/verify-project` сейчас проверяет все ChangeRail surfaces как обязательные и
отдельно выводит advisory, поэтому Codex-only consumers, forbidden legacy
artifacts и известный project-wide OpenSpec debt требуют ручной интерпретации.
Перед release gate verifier должен иметь явный profile/severity contract, не
ослабляющий fail-closed default.

## What Changes

- Добавить project verification profile, где Codex, Claude и legacy MCP
  surfaces объявляются как `required`, `optional` или `forbidden`.
- Разделить machine-readable `status` и `severity` для проверок и advisory-like
  diagnostics.
- Ввести итоговый `pass-with-diagnostics` только для non-blocking findings,
  сохранив `fail` для blocking failures и mandatory targeted checks.
- Разрешить project-wide baseline debt только через tracked policy с видимым
  residual risk и без отключения card-owned OpenSpec validation.
- Обновить generated consumer config/template docs и smoke matrix для
  Codex-only, all-surfaces, forbidden artifact и mandatory-check weakening
  сценариев.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: profile-aware и severity-aware verifier
  contract, summary semantics и baseline-debt policy.
- `changerail-project-bootstrap`: generated consumer templates expose the
  default strict verification profile and documented override surface.
- `changerail-project-templates`: template content documents the project
  verification profile policy without private or machine-local state.

## Impact

- `bin/verify-project` JSON/text output contract and exit semantics.
- `scripts/smoke-verify-project.py` fixture matrix.
- `templates/project/openspec/config.yaml.tpl` and related generated guidance.
- `openspec/specs/changerail-project-verification/spec.md`,
  `openspec/specs/changerail-project-bootstrap/spec.md` and
  `openspec/specs/changerail-project-templates/spec.md`.
