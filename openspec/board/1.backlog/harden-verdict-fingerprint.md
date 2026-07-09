# Захардить freshness-fingerprint под untracked-контент

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Follow-up из независимого ревью карточки 01 (cycle 2, finding R1 minor),
  опубликовано в commit `2e49c57`.
- `scripts/opsx_review_verdict.py`
- `skills/opsx-review/references/opsx-review-verdict.md`
- `docs/opsx-contracts.md`

## Summary
`opsx_review_verdict.py fingerprint` хеширует только `git status --porcelain` и
`git diff HEAD`. Контент untracked (но не ignored) файлов в fingerprint не
входит — виден лишь как имя через `git status`. Поэтому verdict остаётся
`fresh`, даже если содержимое untracked-файлов изменилось после ревью. Для
карточек, чей deliverable — новые (untracked) файлы, это ослабляет freshness-
гарантию гейта. Захардить: включить контент untracked non-ignored файлов в
fingerprint, сохранив свойство «ignored пути (в т.ч. сам verdict под
`.runtime/`) не влияют на fingerprint».

## Acceptance
- `fingerprint` включает детерминированный хеш путей И содержимого untracked
  non-ignored файлов (перечисление через `git ls-files --others
  --exclude-standard`), в дополнение к `git status --porcelain` и `git diff
  HEAD`.
- Изменение содержимого untracked non-ignored файла меняет fingerprint.
- Добавление/изменение ignored файла (например, под `.runtime/`, включая сам
  verdict-файл) НЕ меняет fingerprint — запись verdict не инвалидирует его.
- Формат вывода остаётся `sha256:<64 hex>`; CLI-контракт `validate`,
  `--check-fresh` и exit-коды не меняются.
- Детерминизм: одинаковое дерево → одинаковый fingerprint (стабильная сортировка
  файлов; корректная обработка бинарных/крупных/удалённых файлов).
- Добавлен smoke/тест под `scripts/`, демонстрирующий оба свойства
  (чувствительность к untracked-контенту, нечувствительность к ignored).
- Обновлены `skills/opsx-review/references/opsx-review-verdict.md` и
  `docs/opsx-contracts.md`: секция про freshness больше не утверждает, что
  untracked-контент невидим; guidance «ревьюер всё равно читает файлы»
  сохраняется как defense-in-depth.
- OpenSpec validation и public-surface scans проходят.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `scripts/opsx_review_verdict.py`
- `skills/opsx-review/references/opsx-review-verdict.md`
- `docs/opsx-contracts.md`
- `schemas/opsx-review-verdict.schema.json`

## Result
not started

## Next
- triage: через `opsx-ff` разложить на 1 change (helper + smoke + docs).

## Change Plan Notes
Когда карточка переходит в `2.todo`, замените эту секцию реальными ordered
sections (`## Change 1: ...`).

## Log
- 2026-07-09T03:48:42Z card created from card-01 review follow-up (fingerprint
  untracked-content blind spot).
