# Подготовить и опубликовать ChangeRail 1.0.0

## Status
5.canceled

## Owner
ChangeRail maintainers

## OpenSpec Stage
superseded

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

Ранние qualification fingerprints до independent review superseded и не
являются final-certification evidence. Authoritative exact tree, source-archive
SHA-256, retained evidence path и outcomes для следующего frozen candidate
записываются после rescue в ignored delivery manifest/preflight, чтобы tracked
card не содержала self-referential tree fingerprint. Требуемый floor остается:
CPU affinity `0,1`, строго последовательные core `23/23` и extended `12/12`,
release-CI `27/27`, current/history public scans, strict OpenSpec/config/
whitespace, live trusted npm SRI `4/4`, action tags и byte-identical source
assets. Pinned dev requirements не менялись. Native Windows live evidence для
exact candidate не заявляется; Linux-focused caveat находится в public release
docs.

## Archive
- `openspec/changes/archive/2026-09-01-define-first-stable-distribution-contract/`
- `openspec/changes/archive/2026-09-01-prepare-changerail-1-0-0-release/`

## Related
- `docs/release-discipline.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `CHANGELOG.md`
- `VERSION`

## Result
Исходный release rescue route superseded опубликованной linked replacement
`openspec/board/4.done/enable-post-commit-release-resume-entry.md`. Replacement
сохранила подготовленный payload и завершила публикацию ChangeRail `v1.0.0`;
predecessor больше не является live delivery handoff.

## Next
- done

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
- 2026-09-01T00:00:00Z dependency подтверждена на exact published merge PR #6
  `aabfb2d8d7ba98e727766f2cb0299a607389b6d9`; два ordered change получили
  apply-ready proposal/spec/design/tasks и прошли strict OpenSpec validation.
- 2026-09-01T07:05:00Z distribution change synced/archived; release
  qualification after one bounded lint fix passed sequential core/extended,
  public/trusted and reproducible-asset gates on a two-CPU isolated candidate.
  Tag/GitHub Release не создавались; handoff остается critical xhigh review.
- 2026-09-01T07:10:00Z release-discipline delta synced, второй change archived
  at `openspec/changes/archive/2026-09-01-prepare-changerail-1-0-0-release/`;
  card остается `3.inprogress` до fresh review и scoped publish.
- 2026-09-01T08:00:00Z independent review cycle 1 вернул `NO-GO`: bounded
  rescue 1 добавляет dirty-tracked distribution oracle, согласует metadata
  sidecar wording и authoritative fail-closed release continuation; прежние
  candidate fingerprints superseded, tag/Release по-прежнему отсутствуют.
- 2026-09-01T08:20:00Z independent review cycle 2 подтвердил устранение ранних
  findings и вернул `NO-GO` по post-commit freshness и partial-resume identity;
  bounded rescue 2 фиксирует tree-equality handoff и exact annotation/title/
  notes/assets rules. Tag/GitHub Release не создавались.
- 2026-09-01T19:42:39Z закрыто как superseded опубликованной linked replacement
  `enable-post-commit-release-resume-entry`; replacement сохранила payload и
  завершила `v1.0.0`, новый release handoff не создается.
