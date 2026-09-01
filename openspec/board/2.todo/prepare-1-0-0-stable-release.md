# Подготовить и опубликовать ChangeRail 1.0.0

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
not-started

## Series
- none

## Series Index
- none

## Source
- Решение оператора от 2026-08-31 выпустить первый stable release после
  стабилизации clean core scope и устранения подтвержденных release blockers.

## Summary
Определить минимальный публичный distribution contract и выпустить reviewed
ChangeRail `1.0.0` из clean generic core: version/changelog, compatibility и
migration notes, trusted checks, полный baseline, final independent review,
release commit/tag и public distribution metadata.

## Review
- Risk tier: `critical`
- Milestone audit: `yes`
- New authority or wire protocol: `no`
- Credential or mutation authority: `yes`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `yes`
- Published investigation authorization: `none`

## Depends On
- `stabilize-first-stable-release-scope`

## Acceptance
- Release base содержит опубликованный результат
  `stabilize-first-stable-release-scope`, не содержит phase-routed/retention
  deferred payloads и имеет пустую unrelated working tree.
- Выбран и документирован минимальный packaged source distribution contract с
  однозначными version, license, source revision, compatibility и checksum
  metadata; формат не выдает machine-local state.
- `VERSION` равен `1.0.0`; `CHANGELOG.md` содержит датированный `1.0.0` и новый
  пустой `Unreleased`; compatibility и migration guide описывают переход
  `0.5.0 -> 1.0.0`, required actions и rollback.
- Core и extended release suites последовательно проходят в изолированном
  clone exact release candidate; release CI smoke, current/history public scan
  и применимые trusted-network dependency checks проходят на frozen payload.
- Native Windows claim подтвержден live evidence либо release docs содержат
  явный reviewed caveat без private host data.
- Fresh independent final-certification review возвращает `GO` для exact
  payload; после него создаются scoped release commit, annotated tag `v1.0.0`
  и public distribution metadata, а remote refs подтверждаются read-only.

## Change Set
- `define-first-stable-distribution-contract`
- `prepare-changerail-1-0-0-release`

## Verify
- `python3 scripts/run-release-baseline.py`
- `python3 scripts/run-release-baseline.py --suite extended`
- `python3 scripts/smoke-release-ci.py`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/public-surface-scan.py --history`
- trusted `npm view` integrity checks from `docs/release-discipline.md`
- `git diff --check`

## Archive
- pending

## Related
- `docs/release-discipline.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `CHANGELOG.md`
- `VERSION`

## Result
pending

## Next
- wait until `stabilize-first-stable-release-scope` is published, then run
  `$changerail-deliver openspec/board/2.todo/prepare-1-0-0-stable-release.md`

## Change 1: `define-first-stable-distribution-contract`

### Why
Stable decision снял прежний gate на tags/package metadata, но репозиторий еще
не определяет воспроизводимый публичный distribution bundle.

### Goal
Определить минимальный source distribution contract и проверяемые metadata для
`1.0.0` без превращения ChangeRail в неподходящий language-specific package.

### Scope
- Выбрать generic source bundle/tag/checksum metadata и release verification.
- Обновить release discipline и необходимые public metadata/templates.
- Не менять runtime behavior или dependency pins без отдельного blocker.

### Acceptance
- Distribution можно построить из exact reviewed commit, проверить по checksum
  и связать с `v1.0.0`, license, compatibility и migration docs.

### Depends On
- `stabilize-first-stable-release-scope`

### Related
- `openspec/changes/define-first-stable-distribution-contract/`

## Change 2: `prepare-changerail-1-0-0-release`

### Why
После определения distribution contract требуется единый final-certification
payload, который связывает release metadata, verification и publication.

### Goal
Подготовить, проверить, независимо отревьюить и опубликовать ChangeRail
`1.0.0`.

### Scope
- Обновить version/changelog/compatibility/migration и distribution metadata.
- Выполнить полный release/trusted verification floor.
- После fresh `GO` создать scoped commit, annotated tag и public publication.

### Acceptance
- Все card-level acceptance выполнены на одном frozen release fingerprint.

### Depends On
- `define-first-stable-distribution-contract`

### Related
- `openspec/changes/prepare-changerail-1-0-0-release/`

## Log
- 2026-08-31T00:00:00Z создано как отдельный final-certification handoff;
  publication начинается только после завершения scope-normalization card.
