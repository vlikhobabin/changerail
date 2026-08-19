# Оптимизировать review fingerprint для больших репозиториев

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

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

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

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
- `measure-review-fingerprint-costs`
- `optimize-review-fingerprint-tree-build`
- `share-review-fingerprint-preflight-cache`

## Verify
- `./bin/openspec validate "measure-review-fingerprint-costs" --strict`
- `./bin/openspec validate "optimize-review-fingerprint-tree-build" --strict`
- `./bin/openspec validate "share-review-fingerprint-preflight-cache" --strict`
- `./bin/openspec validate --all --strict`
- `git diff --check`

## Archive
- not started

## Related
- `scripts/changerail_review_verdict.py`
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-verdict.py`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/changes/measure-review-fingerprint-costs/`
- `openspec/changes/optimize-review-fingerprint-tree-build/`
- `openspec/changes/share-review-fingerprint-preflight-cache/`

## Result
not started

## Next
- `$changerail-do openspec/board/2.todo/optimize-review-fingerprint-for-large-repositories.md`

## Change 1: `measure-review-fingerprint-costs`

### Why
Перед оптимизацией нужно отделить стоимость full-index refresh, hashing
untracked files, OpenSpec validation и других deterministic preflight gates,
чтобы subsequent changes сравнивались с публично воспроизводимым baseline.

### Goal
Добавить public-safe измерения и synthetic benchmark, не меняя canonical
freshness output или review gate semantics.

### Scope
- Timing diagnostics для fingerprint/preflight phases.
- Synthetic large-repository benchmark для docs-only и source payload.
- Baseline/threshold rationale в focused smoke evidence.

### Acceptance
- Измерения явно разделяют changed path discovery, reviewed-tree construction,
  untracked content hashing, OpenSpec validation, scoped whitespace check и
  public-surface scan.
- Benchmark использует generic temporary repositories и не tracked private
  consumer data.
- Existing fingerprint/preflight behavior остается совместимым.

### Depends On
- none

### Related
- `openspec/changes/measure-review-fingerprint-costs/`

## Change 2: `optimize-review-fingerprint-tree-build`

### Why
Полный `git add -A` по всему repository корректен, но слишком дорог для малого
payload в большом tracked tree.

### Goal
Построить exact reviewed tree из HEAD и machine-readable changed path set без
full-index refresh на безопасном happy path.

### Scope
- NUL-safe changed path model для add/modify/delete/rename/untracked/symlink.
- Path-scoped temporary-index updates.
- Reference full-tree parity tests для edge path cases.
- Conservative fallback/fail-closed behavior для unsafe states.

### Acceptance
- Для docs-only изменения в synthetic large repository happy path не выполняет
  full-repository `git add -A`.
- `tree_sha` и `diff_fingerprint` совпадают с reference full-tree algorithm для
  add, modify, delete, rename, symlink, Unicode, spaces, literal arrow и valid
  non-UTF-8 Linux paths.
- Untracked regular files still hash by content; ignored runtime files stay out
  of fingerprint.

### Depends On
- `measure-review-fingerprint-costs`

### Related
- `openspec/changes/optimize-review-fingerprint-tree-build/`

## Change 3: `share-review-fingerprint-preflight-cache`

### Why
После path-scoped fingerprint delivery still recomputes the same exact payload
identity multiple times across preflight, verdict validation and publish.

### Goal
Сделать один canonical fingerprint implementation для all review freshness
consumers и разрешить validated ignored runtime cache for unchanged payloads.

### Scope
- Shared fingerprint function for preflight, verdict validation and publish
  gates.
- Ignored `.runtime/changerail/` cache record with fail-closed validation.
- Cache hit/miss diagnostics and stale cache smoke coverage.

### Acceptance
- Preflight, `validate --check-fresh` и publish gate observe identical
  `head_commit`, `tree_sha` and `diff_fingerprint`.
- Repeated unchanged preflight may reuse a cache only after current HEAD and
  changed path metadata prove the exact payload is unchanged.
- Stale, malformed or cross-workspace cache entries recompute or fail closed
  before emitting freshness data.

### Depends On
- `optimize-review-fingerprint-tree-build`

### Related
- `openspec/changes/share-review-fingerprint-preflight-cache/`

## Log
- 2026-08-18T17:39:30Z создана по результатам supervised delivery: repeated
  exact-payload fingerprint был корректен, но full-tree index refresh занял
  основную часть review gate latency.
- 2026-08-19T00:00:00Z `$chrl-ff` decomposed story into ordered OpenSpec changes
  and moved card to `2.todo`.
