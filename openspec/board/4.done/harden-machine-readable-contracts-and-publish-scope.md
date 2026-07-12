# Укрепить machine-readable contracts и scoped publish

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Комплексное ревью кода, документации и public-safety controls ChangeRail от
  2026-07-12.
- `docs/changerail-contracts.md`
- `skills/changerail-pub/SKILL.md`
- `openspec/board/4.done/harden-delivery-operations.md`

## Summary
Сделать delivery manifest, review verdict и delivery run contracts надежной
машинной границей, соответствующей опубликованным JSON Schema и fail-closed
publish semantics. Исправить формирование staging proposal для всех допустимых
git paths и ограничить terminal outcome parsing только авторитетными
структурированными событиями.

Ревью воспроизвело три класса дефектов: quoted path с пробелом попадает в
manifest вместе с кавычками, untracked directory сворачивается до широкого пути
вместо точных файлов, а оба Python validators принимают документы, которые
нарушают собственные JSON Schema. Дополнительно runner трактует произвольную
строку `error` или `failed` в любом JSON field как terminal `BLOCKED`, даже если
позже присутствует authoritative `DELIVERED` event.

## Findings
- `git_status_entries()` разбирает human-readable `git status --porcelain`
  через `splitlines()` и строковый `" -> "`, не используя NUL-safe format.
- Untracked directories могут попасть в `committable_paths` как общий каталог и
  расширить proposed staging scope на unrelated files.
- `validate_manifest()` проверяет только часть required shape и принимает
  неверные типы для `workspace`, `card`, `changes`, runtime paths и timestamps.
- `_validate_verdict()` не проверяет date-time formats, nested unknown fields и
  часть optional field types, несмотря на `additionalProperties: false` в
  schema.
- Runner рекурсивно интерпретирует все строковые значения JSONL; outcome зависит
  от глобального приоритета найденных слов, а не от typed terminal event и его
  позиции в lifecycle.
- `verify-project` перечисляет не все публичные ChangeRail schemas и поэтому не
  обнаружит отсутствие delivery-run или review-cycle-history schema.

## Acceptance
- Manifest derivation использует NUL-safe git status format и сохраняет точные
  repository-relative byte-safe paths для add/modify/delete/rename, включая
  spaces, quotes, Unicode, valid non-UTF-8 Linux path bytes и имена,
  содержащие literal ` -> `.
- Untracked paths перечисляются на уровне файлов либо консервативно отклоняются;
  staging proposal не содержит directory-wide path, если это может включить
  unrelated work.
- Focused regression tests доказывают правильный staging plan для нескольких
  untracked файлов в одном каталоге, tracked path с пробелом, rename, delete,
  Unicode path и mixed pre-existing dirty state.
- Delivery manifest и review verdict helpers валидируют canonical Draft 2020-12
  schemas с проверкой `format`, `additionalProperties`, conditional required
  fields и всеми nested types, после чего применяют отдельные semantic
  invariants ChangeRail.
- Один и тот же schema validation implementation используется CLI helpers и
  focused tests либо drift между ними проверяется отрицательными fixtures.
- Invalid manifest/verdict всегда завершается non-zero с sanitized structured
  diagnostic; malformed `go` verdict не проходит publish freshness gate.
- Runner признает `DELIVERED`, `NO-GO` и `BLOCKED` только из документированных
  event types/fields. Промежуточные tool errors, prose и arbitrary JSON strings
  не меняют terminal result.
- Tests покрывают conflicting и ordered events, successful exit после
  non-terminal error, non-zero exit без outcome, authoritative no-go и
  awaiting-review.
- `verify-project` и release checks охватывают все пять contract schemas:
  review verdict, review history, delivery manifest, delivery run и evidence
  index.
- Docs, schemas, helpers, smoke fixtures и lifecycle skills описывают одинаковые
  guarantees и fail-closed поведение.

## Change Set
- `harden-delivery-manifest-scope`
- `enforce-contract-schema-validation`
- `harden-delivery-runner-outcomes`

## Verify
- `python3 scripts/smoke-delivery-manifest-derive.py` - passed; проверяет
  manifest `derive`, `validate` и `staging-plan` на временном git repo с tracked
  spaces, quotes, Unicode, literal ` -> `, rename, delete, несколькими
  untracked files в одном directory, mixed dirty state и schema negative
  fixtures. Проверка падает, если manifest parsing расширяет scope, сохраняет
  shell quotes, теряет rename/delete paths или принимает malformed manifests.
- `python3 scripts/smoke-review-verdict-validation.py` - passed; проверяет
  review verdict `fingerprint` и `validate` с valid/fresh verdicts,
  independence failures, schema negative fixtures и malformed `go` verdicts.
  Проверка падает, если malformed verdicts проходят publish freshness gate.
- `python3 scripts/smoke-delivery-runner.py` - passed; проверяет fake Codex
  JSONL output, status records и terminal outcomes для non-terminal error
  strings, ordered terminal conflicts, non-zero exit fallback, authoritative
  no-go и awaiting-review.
- `python3 scripts/smoke-verify-project.py` - passed; проверяет generated
  consumer wiring и подтверждает, что все пять public contract schemas
  проверяются.
- `python3 -m py_compile scripts/changerail_contract_schema.py scripts/changerail_delivery_manifest.py scripts/changerail_review_verdict.py scripts/smoke-delivery-manifest-derive.py scripts/smoke-review-verdict-validation.py scripts/smoke-delivery-runner.py scripts/smoke-verify-project.py bin/changerail-delivery-runner bin/verify-project` - passed.
- `openspec validate harden-delivery-manifest-scope --strict` - passed before archive.
- `openspec validate enforce-contract-schema-validation --strict` - passed before archive.
- `openspec validate harden-delivery-runner-outcomes --strict` - passed before archive.
- `openspec validate changerail-contracts --strict` - passed.
- `openspec validate changerail-delivery-runner --strict` - passed.
- `openspec validate changerail-project-verification --strict` - passed.
- `openspec validate --all --strict` - passed after all archives; 13 specs passed, 0 failed.
- `git diff --check` - passed.
- Cycle-1 review fix для R1 language policy:
  public docs, synced OpenSpec specs, archived OpenSpec artifacts и card prose
  переведены на русский с сохранением technical identifiers и commands.
- Post-fix checks:
  `openspec validate --all --strict` - passed;
  `python3 scripts/smoke-delivery-manifest-derive.py` - passed;
  `python3 scripts/smoke-review-verdict-validation.py` - passed;
  `python3 scripts/smoke-delivery-runner.py` - passed;
  `python3 scripts/smoke-verify-project.py` - passed;
  `python3 scripts/public-surface-scan.py` - passed;
  `python3 -m py_compile ...` for changed Python/helper files - passed;
  `git diff --check` - passed.
- Cycle-2 review fix для R1 byte-safe path handling:
  `scripts/changerail_delivery_manifest.py` теперь пишет manifest и JSON CLI
  payloads с ASCII escaping, поэтому `surrogateescape` path strings для valid
  non-UTF-8 Linux filenames не ломают UTF-8 writer; `staging-plan` non-JSON
  output пишет paths через `os.fsencode`.
- Post-fix checks:
  `python3 scripts/smoke-delivery-manifest-derive.py` - passed; fixture создает
  untracked path `docs/bad-\xff.txt` и проверяет exact byte round-trip через
  `os.fsencode`;
  `python3 -m py_compile scripts/changerail_delivery_manifest.py scripts/smoke-delivery-manifest-derive.py` - passed.

## Archive
- `openspec/changes/archive/2026-07-12-harden-delivery-manifest-scope/`
- `openspec/changes/archive/2026-07-12-enforce-contract-schema-validation/`
- `openspec/changes/archive/2026-07-12-harden-delivery-runner-outcomes/`

## Related
- `docs/changerail-contracts.md`
- `bin/changerail-delivery-runner`
- `bin/verify-project`
- `scripts/changerail_delivery_manifest.py`
- `scripts/changerail_review_verdict.py`
- `scripts/smoke-delivery-manifest-derive.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-review-verdict-validation.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-review-verdict.schema.json`
- `schemas/changerail-review-cycle-history.schema.json`
- `skills/changerail-pub/SKILL.md`
- `openspec/board/1.backlog/close-release-gate-and-docs-drift.md`
- `openspec/changes/archive/2026-07-12-harden-delivery-manifest-scope/`
- `openspec/changes/archive/2026-07-12-enforce-contract-schema-validation/`
- `openspec/changes/archive/2026-07-12-harden-delivery-runner-outcomes/`

## Result
planned changes реализованы; helper и runner regressions покрыты focused
smokes; specs synced; все три OpenSpec changes archived; карточка готова к
independent review

Reviewed payload включен в publish commit; точный commit hash фиксируется git
history и ignored manifest publish metadata после push. Push status: `pending`;
branch/remote: `main`/`origin`.

## Next
- done

## Change 1: `harden-delivery-manifest-scope`

### Why
Delivery manifest derivation является publish staging proposal boundary, но
текущий parser может неверно прочитать valid git paths и расширить untracked
directory scope.

### Goal
Выводить точные card-owned manifest operations из NUL-safe git status data и
fail closed, когда untracked directory нельзя представить как точные files.

### Scope
- `scripts/changerail_delivery_manifest.py`
- `scripts/smoke-delivery-manifest-derive.py`
- delivery manifest docs/specs

### Acceptance
- Manifest derivation сохраняет точные repository-relative paths для add,
  modify, delete и rename operations, включая spaces, quotes, Unicode и literal
  ` -> ` в filenames.
- Untracked directories разворачиваются до точных untracked files или
  консервативно отклоняются; staging plans не содержат directory-wide paths,
  которые могут включить unrelated work.
- Focused smoke coverage проверяет tracked path со space, rename, delete,
  Unicode path, literal arrow text и mixed pre-existing dirty state.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-harden-delivery-manifest-scope/`

## Change 2: `enforce-contract-schema-validation`

### Why
Helpers объявляют JSON Schemas canonical contracts, но сейчас принимают
documents, которые нарушают schema-required types, formats и nested shape.

### Goal
Сделать так, чтобы manifest и verdict helper validation использовали tracked
Draft 2020-12 schemas до применения ChangeRail semantic invariants.

### Scope
- `scripts/changerail_delivery_manifest.py`
- `scripts/changerail_review_verdict.py`
- manifest/verdict smoke tests
- contract docs/specs

### Acceptance
- Delivery manifest и review verdict helpers enforce canonical schemas,
  включая `format`, `additionalProperties`, conditionals и nested types.
- CLI helpers и tests используют один validation implementation или включают
  negative fixtures, которые ловят drift.
- Invalid manifest/verdict files завершаются non-zero с sanitized structured
  diagnostics, а malformed `go` verdicts не проходят publish freshness gate.

### Depends On
- `harden-delivery-manifest-scope`

### Related
- `openspec/changes/archive/2026-07-12-enforce-contract-schema-validation/`

## Change 3: `harden-delivery-runner-outcomes`

### Why
Delivery runner сейчас трактует arbitrary JSON string values как terminal
outcomes, поэтому ordinary tool errors могут override later authoritative
lifecycle events.

### Goal
Ограничить terminal outcome parsing документированными structured events и
fields, а также гарантировать, что project/release checks покрывают каждую
public contract schema.

### Scope
- `bin/changerail-delivery-runner`
- `bin/verify-project`
- runner и verify-project smoke tests
- contract и release docs/specs

### Acceptance
- Runner распознает `DELIVERED`, `NO-GO` и `BLOCKED` только из documented event
  types или terminal fields плюс process exit behavior.
- Tests покрывают conflicting and ordered events, successful exit после
  non-terminal error, non-zero exit без outcome, authoritative no-go и
  awaiting-review.
- `verify-project` и release checks покрывают review verdict, review history,
  delivery manifest, delivery run и evidence index schemas.

### Depends On
- `enforce-contract-schema-validation`

### Related
- `openspec/changes/archive/2026-07-12-harden-delivery-runner-outcomes/`

## Log
- 2026-07-12T15:05:13Z card created from reproducible review findings in scoped
  staging, manifest/verdict validation and delivery terminal outcome parsing.
- 2026-07-12T15:38:48Z `$changerail-ff` decomposed story into three ordered
  changes: manifest scope derivation, schema-backed validation and runner
  outcome/schema coverage hardening.
- 2026-07-12T15:52:17Z `$changerail-do` реализовал все три changes,
  синхронизировал specs, архивировал OpenSpec changes и оставил карточку в
  `3.inprogress` для independent review.
- 2026-07-12T16:09:50Z independent review cycle 1 вернул `no-go` по R1:
  новая public docs/OpenSpec prose нарушала language policy; `$changerail-do`
  исправил blocker переводом public docs, synced specs, archived artifacts и
  card prose на русский.
- 2026-07-12T16:20:00Z independent review cycle 2 вернул `no-go` по R1:
  manifest derivation падал на valid non-UTF-8 path bytes; `$changerail-do`
  исправил JSON serialization и добавил regression fixture для
  `docs/bad-\xff.txt`.
- 2026-07-12T16:33:24Z publish финализировал карточку в `4.done`; точный
  commit hash фиксируется git history и ignored manifest publish metadata после
  push; push status `pending`.
