## Why

Final review первого stable release установил, что обещанный post-commit
resume недостижим: новая publish/deliver invocation безусловно применяет
pre-commit current-worktree freshness и dirty scope gates к уже чистому payload
commit. Same-card rescue budget исчерпан `2/2`, а cumulative successor payload
с measured baseline `299` production-counted LOC требует отдельного
investigation до bounded authorization.

## What Changes

- Публикуется decision-only граница для exact successor
  `enable-post-commit-release-resume-entry`: ранний state-specific routing,
  read-only committed manifest proof и существующая exact release state
  machine без новой schema, provider или mutation authority.
- Выбирается минимальный affected surface и forecast `359..399` cumulative
  production-counted LOC: не более 100 новых counted строк поверх baseline
  299, hard ceiling 400 и stop при 401+.
- Фиксируется отдельный будущий authorization source
  `authorize-bounded-post-commit-release-resume-entry-payload`, который должен
  связать опубликованное investigation с exact successor и только после
  собственной review/publish разрешить ceiling 400 с protocol allowance
  `false`.
- Future authorization-card и exact successor должны обе объявить exact
  investigation id `investigate-post-commit-release-resume-entry-boundary` в
  `Depends On`; canonical deterministic preflight проверяет обе dependency
  edges вместе с six-field object и two-field successor reference.
- Фиксируется focused и final-certification verification floor для одного
  exact successor tree.
- Investigation остается docs/OpenSpec-only: successor implementation,
  authorization-card, workflow, tag, release и publication mutation не
  создаются.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: добавить нормативное investigation-решение
  для exact post-commit resume successor, его bounded authorization handoff,
  cumulative LOC ceiling и verification floor.

## Impact

В этом change изменяются только investigation card и OpenSpec artifacts. Во
время последующей apply phase его delta requirement будет синхронизирован в
`openspec/specs/changerail-release-discipline/spec.md`, затем change будет
архивирован. Будущий exact successor затронет существующие manifest helper,
pub/deliver skill contracts, focused smoke, specs и release docs, но не
получает authorization из этого decision change.
