## Why

Исчерпанное unpublished investigation корректно определило минимальную
Git commit-header grammar, но неверно присвоило сценарий existing auth
requirement новому requirement. Нужен чистый docs-only rescue, который
заново публикует проверенное решение с корректным OpenSpec ownership.

## What Changes

- Зафиксировать exact bounded byte grammar: first exact lowercase-hex `tree`,
  later first-`SP` headers с opaque value и `SP`-prefixed continuations, включая
  exact blank fold `b" "`.
- Сохранить read-only model evidence для exact source ancestry `644e9e1`
  (`95/95`) и pinned all-ref planning snapshot (`98/98`) с exact digests.
- Добавить ровно один Git-header requirement с восемью собственными
  scenarios, не изменяя existing auth requirement с двумя scenarios.
- Связать future clean authorization с этим rescue investigation и
  unchanged replacement, ceiling `301`, protocol allowance `false`.
- Оставить exhausted card, archive, payload и evidence forensic-only. Change
  добавляет `0` production/test/runtime LOC и не запускает history scan или
  full baseline.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: опубликовать Git-compatible commit-header boundary с
  корректным requirement/scenario ownership и clean successor lineage.

## Impact

Change затрагивает только rescue board card, OpenSpec artifacts и
`changerail-release-ci` decision contract. Scripts, tests, fixtures, schemas,
runtime, CI execution и consumer projects не меняются.
