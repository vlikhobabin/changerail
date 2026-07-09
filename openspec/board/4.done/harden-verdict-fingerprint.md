# Захардить freshness-fingerprint под untracked-контент

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

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
- `harden-verdict-fingerprint`

## Verify
- RED: `python3 scripts/smoke-review-fingerprint.py` failed before helper
  changes with `AssertionError: untracked non-ignored content change did not
  alter fingerprint`.
- passed: `openspec validate harden-verdict-fingerprint --strict`
- passed: `python3 scripts/smoke-review-fingerprint.py`
- passed: `python3 -m py_compile scripts/opsx_review_verdict.py scripts/smoke-review-fingerprint.py`
- passed: `python3 scripts/opsx_review_verdict.py fingerprint --workspace .`
  emitted `sha256:00f5acad9386d841aae4dab4bb0af40e208dccd227121ed2998abd823a89cfd2`
  during implementation.
- passed: `openspec validate opsx-contracts --strict`
- passed: `openspec validate --all --strict` after archive (11 passed, 0 failed).
- passed: `python3 -m json.tool .mcp.json`
- passed: `python3 -m json.tool
  .runtime/opsx/delivery-manifests/harden-verdict-fingerprint.json`
- passed: delivery manifest validation against
  `schemas/opsx-delivery-manifest.schema.json`
- passed: `python3 scripts/opsx_review_verdict.py validate
  .runtime/opsx/reviews/harden-verdict-fingerprint.json --check-fresh
  --workspace . --json` returned `result: go` and `fresh: true` against HEAD
  `3e68e61031a3eccbb0b890adb256648dac7c903d` with fingerprint
  `sha256:589bab4bd452a125805fd85c0474fd4ceb233bef3e3b2edecfd8e7e3a3bfa314`.
- passed: TOML parse for `.codex/config.toml`
- passed: `git diff --check`
- passed: targeted public-surface scan; matches were existing generic
  public-safety wording and Python `secrets` module imports, with no unexpected
  private names, credentials or local paths found.

## Archive
- `openspec/changes/archive/2026-07-09-harden-verdict-fingerprint/`

## Related
- `openspec/changes/archive/2026-07-09-harden-verdict-fingerprint/`
- `scripts/opsx_review_verdict.py`
- `scripts/smoke-review-fingerprint.py`
- `skills/opsx-review/references/opsx-review-verdict.md`
- `docs/opsx-contracts.md`
- `openspec/specs/opsx-contracts/spec.md`
- `schemas/opsx-review-verdict.schema.json`

## Result
Implemented and archived `harden-verdict-fingerprint`. External review cycle 1
returned a fresh `go` verdict; publish proceeds with ignored runtime artifacts
excluded.

## Next
- Continue with `openspec/board/1.backlog/04-migrate-existing-consumers.md`.

## Change 1: `harden-verdict-fingerprint`

### Why
Review verdict freshness must include newly delivered untracked file content, or
publish can accept a verdict for a different working tree than the one being
published.

### Goal
Strengthen `opsx_review_verdict.py fingerprint` so untracked non-ignored file
content affects freshness while ignored runtime files remain excluded.

### Scope
- Update `scripts/opsx_review_verdict.py`.
- Add focused smoke coverage under `scripts/`.
- Update review verdict and contracts documentation.
- Update the `opsx-contracts` OpenSpec requirement.

### Acceptance
- Untracked non-ignored file content changes alter the fingerprint.
- Ignored runtime file changes do not alter the fingerprint.
- `validate`, `--check-fresh`, exit codes and `sha256:<64 hex>` format stay
  compatible.
- Smoke, OpenSpec validation and public-surface checks pass.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-09-harden-verdict-fingerprint/`

## Log
- 2026-07-09T03:48:42Z card created from card-01 review follow-up (fingerprint
  untracked-content blind spot).
- 2026-07-09T03:52:22Z `$opsx-ff` decomposed story into
  `harden-verdict-fingerprint`, completed artifacts and moved card to
  `3.inprogress`.
- 2026-07-09T03:57:09Z `$opsx-do` implemented fingerprint hardening, smoke
  coverage and docs/spec updates; synced specs and archived
  `harden-verdict-fingerprint`.
- 2026-07-09T03:57:09Z safety stop: awaiting external review per supervisor
  instruction; no self-review, reviewer launch, publish, commit or push was
  performed.
- 2026-07-09T04:02:08Z external review cycle 1 returned `go`; verdict
  validated fresh against HEAD `3e68e61031a3eccbb0b890adb256648dac7c903d`
  with fingerprint
  `sha256:589bab4bd452a125805fd85c0474fd4ceb233bef3e3b2edecfd8e7e3a3bfa314`.
- 2026-07-09T04:04:50Z card moved to `4.done` for scoped publish; runtime
  review verdict and delivery manifest remain excluded from commit.
