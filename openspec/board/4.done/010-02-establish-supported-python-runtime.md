# Зафиксировать поддерживаемый Python runtime ChangeRail

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `establish-supported-python-runtime` (archived)

## Change 1: `establish-supported-python-runtime`

### Why
ChangeRail helpers сейчас полагаются на host Python и implicit modules; на
consumer hosts это приводит к late import/shebang failures без actionable
diagnostic.

### Goal
Определить единый поддерживаемый Python runtime и ранний bootstrap/selection
contract для всех ChangeRail Python helpers.

### Scope
- Runtime bootstrap/launcher contract.
- Python helper entrypoints и compatibility/migration docs.
- Focused smoke для interpreter selection и diagnostic failure modes.

### Acceptance
- Compatibility docs объявляют минимальную Python version и runtime modules.
- Один bootstrap/selection mechanism используется `verify-project`, manifest,
  verdict, runner и metrics helpers.
- Поддерживается явный interpreter override без редактирования tracked shebangs.
- Bootstrap пишет environment только в ignored runtime path.
- Старый или неполный host runtime завершается с точной remediation diagnostic.
- Smoke покрывает supported runtime, old-version simulation, missing dependency
  и invalid override.

### Depends On
- `repair-skill-frontmatter-validation`

### Related
- `openspec/changes/establish-supported-python-runtime/`

## Verify
- RED: `python3 scripts/smoke-python-runtime.py` failed before implementation
  with missing `bin/changerail-python`, proving the focused smoke covered the
  selector absence.
- `python3 scripts/smoke-python-runtime.py` passed after R1 fix: `7/7`
  checks, including invalid `CHANGERAIL_PYTHON` for `bin/bootstrap-project`.
- `CHANGERAIL_PYTHON=/opt/example-project/missing-python bin/bootstrap-project
  --help` exits `2` with the selector invalid override diagnostic.
- `python3 scripts/compile-python-inventory.py` passed and compiled
  polyglot Python helper entrypoints.
- `ruff check bin scripts` passed.
- `python3 scripts/smoke-release-ci.py` passed: `40/40` checks.
- `python3 scripts/smoke-verify-project.py` passed: `17/17` checks.
- `python3 scripts/smoke-bootstrap-project.py` passed: `8/8` checks.
- `python3 scripts/smoke-delivery-runner.py` passed.
- `python3 scripts/smoke-delivery-metrics.py` passed.
- `python3 scripts/smoke-wiring-discovery.py` passed: `172/172` checks.
- `python3 scripts/smoke-contract-schemas.py` passed: `7` schemas.
- `python3 scripts/smoke-drift.py --project <generated fixture>` passed:
  `1/1` checks.
- `python3 scripts/run-release-baseline.py` passed after R1 fix: `26/26`
  steps, including current/history public-surface scans and generated drift
  fixture bootstrap through the selector.
- `python3 scripts/public-surface-scan.py` passed after R1 fix:
  `591` files scanned, `0` findings.
- `./bin/openspec validate --all --strict` passed after R1 fix.
- `git diff --check` passed after R1 fix.

## Archive
- `openspec/changes/archive/2026-08-01-establish-supported-python-runtime/`

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `openspec/changes/establish-supported-python-runtime/`
- `openspec/changes/archive/2026-08-01-establish-supported-python-runtime/`
- `docs/compatibility.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `bin/changerail-python`
- `bin/changerail-delivery-runner`

## Result
Implemented shared Python runtime selector, explicit runtime dependency file,
selector-backed helper entrypoints, docs/migration updates and focused runtime
smoke. Synced specs and archived the OpenSpec change. Post-review R1 rescue
routed `bin/bootstrap-project` through the same selector and re-ran the release
baseline; awaiting fresh independent review.

Published reviewed payload as `a47ca3407ad77aee2c8cbb0b6c1074bc4e0ca447`; push status `pending` on `main`/`origin`.

## Next
- done

## Log
- 2026-08-01T15:07:29Z generic runtime requirement извлечен из consumer feedback.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
- 2026-08-01T16:30:36Z `changerail-ff` создал apply-ready artifacts для
  `establish-supported-python-runtime` и перевел карточку в `3.inprogress`.
- 2026-08-01T16:51:17Z `changerail-do` реализовал selector/runtime contract,
  выполнил focused smokes и release baseline, синхронизировал specs и
  archived change `2026-08-01-establish-supported-python-runtime`; карточка
  оставлена в `3.inprogress` для independent review.
- 2026-08-01T17:19:09Z post-review R1 rescue routed `bin/bootstrap-project`
  through shared `bin/changerail-python` selector and extended runtime smoke
  coverage for invalid bootstrap override; requires fresh review cycle 2.
- 2026-08-01T17:54:15Z publish finalized card into `4.done` with commit `a47ca3407ad77aee2c8cbb0b6c1074bc4e0ca447` and push status `pending`.
