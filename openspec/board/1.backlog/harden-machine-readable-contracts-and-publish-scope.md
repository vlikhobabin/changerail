# Укрепить machine-readable contracts и scoped publish

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

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
  spaces, quotes, Unicode и имена, содержащие literal ` -> `.
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
- none yet

## Verify
- not started

## Archive
- not started

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

## Result
not started

## Next
- Triage contract compatibility and split the story into parser, schema
  validation and runner outcome changes.

## Log
- 2026-07-12T15:05:13Z card created from reproducible review findings in scoped
  staging, manifest/verdict validation and delivery terminal outcome parsing.
