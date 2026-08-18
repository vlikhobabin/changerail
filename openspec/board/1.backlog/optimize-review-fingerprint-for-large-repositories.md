# Оптимизировать review fingerprint для больших репозиториев

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Field-validation supervised delivery от 2026-08-18 на generic consumer с
  более чем 75 000 tracked files.
- `scripts/changerail_review_verdict.py`
- `scripts/changerail_review_preflight.py`
- `bin/changerail-review-verdict`

## Summary
Review fingerprint строит временный index через `git read-tree`, затем выполняет
`git add -A` для всего repository. На большом generated-source consumer даже
docs-only payload приводил к preflight/fingerprint длительностью около двух
минут. Delivery повторяет fingerprint перед review, при проверке verdict и
перед publish, поэтому неизменный payload многократно оплачивает полный обход
repository.

Нужно сохранить точную freshness-семантику и reviewed tree SHA, но сделать
стоимость пропорциональной измененному scope либо безопасно переиспользовать
результат для неизменного workspace fingerprint.

## Acceptance
- Design локализует стоимость `git add -A`, hashing untracked files, OpenSpec
  validation и остальных частей preflight отдельными измерениями.
- Новый алгоритм не выполняет full-index refresh для docs-only изменения в
  большом tracked tree, если exact reviewed tree можно построить из HEAD и
  machine-readable changed path set.
- Reviewed `tree_sha` и `diff_fingerprint` совпадают с текущим reference
  алгоритмом для add, modify, delete, rename, symlink, Unicode, spaces, literal
  arrow и valid non-UTF-8 Linux paths.
- Untracked regular files продолжают участвовать содержимым; ignored runtime
  files не попадают в fingerprint.
- Повторный preflight неизменного payload либо использует валидированный cache,
  либо имеет документированную bounded стоимость без ослабления freshness.
- Synthetic large-repository benchmark фиксирует до/после для docs-only и
  source payload; threshold выбирается из измеренного baseline и не зависит от
  конкретного consumer repository.
- `validate --check-fresh`, independent reviewer и publish gate используют один
  канонический fingerprint implementation.
- Focused smoke и existing review/preflight suite проходят.

## Non-Goals
- Ослабление exact-payload review gate.
- Исключение tracked generated source из reviewed tree.
- Хранение private consumer paths или raw field-validation logs в repository.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `scripts/changerail_review_verdict.py`
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-verdict.py`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`

## Result
not started

## Next
- triage

## Log
- 2026-08-18T17:39:30Z создана по результатам supervised delivery: repeated
  exact-payload fingerprint был корректен, но full-tree index refresh занял
  основную часть review gate latency.
