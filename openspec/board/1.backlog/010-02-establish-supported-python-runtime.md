# Зафиксировать поддерживаемый Python runtime ChangeRail

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`010-core-release-contracts`

## Series Index
`02`

## Source
- Повторяемый consumer failure на host Python без `tomllib` и runtime
  dependencies.

## Summary
Определить единый поддерживаемый Python runtime для ChangeRail helpers,
добавить bootstrap/selection contract и выдавать раннюю actionable diagnostic
вместо import или shebang failure.

## Acceptance
- Compatibility docs объявляют минимальную Python version и runtime modules.
- Один bootstrap/selection mechanism используется `verify-project`, manifest,
  verdict, runner и metrics helpers.
- Поддерживается явный interpreter override без редактирования tracked shebangs.
- Bootstrap пишет environment только в ignored runtime path.
- Старый или неполный host runtime завершается с точной remediation diagnostic.
- Smoke покрывает supported runtime, old-version simulation, missing dependency
  и invalid override.

## Scope
- Runtime bootstrap/launcher contract.
- Python helper entrypoints и compatibility/migration docs.
- Release smoke для interpreter selection.

## Non-Goals
- Native Windows command shims: это серия `040`.
- Packaging ChangeRail как отдельного wheel/installer без отдельного решения.

## Depends On
- `010-01-repair-skill-frontmatter-validation`

## Implementation Notes
- Предпочесть один tracked launcher/selection path вместо локального изменения
  нескольких shebangs.
- Не использовать `requirements-dev.txt` как неявный runtime API без явного
  разделения runtime и release-only dependencies.

## Change Set
- none yet

## Verify
- Focused runtime/bootstrap smoke.
- `python3 scripts/run-release-baseline.py` из поддерживаемого environment.
- Public-surface scan и `git diff --check`.

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `docs/compatibility.md`
- `bin/verify-project`
- `bin/changerail-delivery-runner`

## Result
not started

## Next
- После `010-01` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z generic runtime requirement извлечен из consumer feedback.
