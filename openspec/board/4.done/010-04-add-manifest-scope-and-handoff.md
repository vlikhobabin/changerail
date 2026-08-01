# Добавить manifest scope reconciliation и handoff summary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`010-core-release-contracts`

## Series Index
`04`

## Source
- Consumer publish потребовал ручного rename-aware сравнения manifest и staged
  diff; review/verification/card final state не сохранились в handoff ledger.

## Summary
Добавить machine-readable `scope-check` для delivery manifest и расширить
ignored handoff summary данными review, verification и окончательного состояния
карточки.

## Acceptance
- `scope-check` сравнивает manifest с working tree и отдельно со staged diff.
- Проверка NUL-safe и корректно обрабатывает add/modify/delete/rename.
- Результат явно перечисляет missing, extra и mismatched paths.
- Ignored runtime paths не считаются committable scope.
- Manifest хранит concise review и verification summaries и final card state.
- Schema и negative smoke отклоняют ложный green при extra staged path.

## Scope
- Delivery manifest schema/helper и documentation.
- Review/publish handoff integration.
- Rename и staged-scope fixtures.

## Non-Goals
- Хранение raw command logs в manifest.
- Generic command evidence capture: карточка `020-02`.

## Depends On
- `010-03-fix-publish-finalization-ledger`

## Implementation Notes
- Строить сравнение из structured Git status/index data, а не из
  `--name-only` text parsing.
- Summary должна оставаться малой; raw evidence остается ignored и ссылочной.

## Change Set
- `add-manifest-scope-and-handoff` (archived)

## Change 1: `add-manifest-scope-and-handoff`

### Why
Review/publish handoff сейчас требует ручного rename-aware сравнения manifest и
staged diff, а итоговые review/verification/card summaries не закреплены в
машиночитаемом ignored ledger.

### Goal
Добавить manifest scope reconciliation и concise handoff summary, которые
проверяют tracked payload без включения raw runtime logs в commit scope.

### Scope
- Delivery manifest schema/helper и documentation.
- Review/publish handoff integration.
- Rename и staged-scope fixtures.

### Acceptance
- `scope-check` сравнивает manifest с working tree и отдельно со staged diff.
- Проверка NUL-safe и корректно обрабатывает add/modify/delete/rename.
- Результат явно перечисляет missing, extra и mismatched paths.
- Ignored runtime paths не считаются committable scope.
- Manifest хранит concise review и verification summaries и final card state.
- Schema и negative smoke отклоняют ложный green при extra staged path.

### Depends On
- `fix-publish-finalization-ledger`

### Related
- `openspec/changes/archive/2026-08-01-add-manifest-scope-and-handoff/`

## Verify
- Fast-forward validation passed:
  `./bin/openspec validate add-manifest-scope-and-handoff --strict`,
  `./bin/openspec validate --all --strict`, `git diff --check` and explicit
  untracked whitespace scan (`UNTRACKED_WHITESPACE_OK 6 files`) passed.
- Delivery verification floor: scope-check smoke для add/modify/delete/rename
  и non-UTF-8 path, negative staged extra/missing cases, contract schema smoke,
  release baseline и `git diff --check`.
- Delivery verification passed:
  `python3 scripts/smoke-delivery-manifest.py` passed;
  `python3 scripts/smoke-delivery-manifest-derive.py` passed and covers
  working-tree/staged `scope-check`, add/modify/delete/rename, spaces, quotes,
  Unicode, literal ` -> ` and Linux non-UTF-8 path round trip, plus negative
  staged extra/missing/mismatched cases;
  `python3 scripts/smoke-contract-schemas.py` passed with `7` schemas.
- `./bin/openspec validate add-manifest-scope-and-handoff --strict`,
  `./bin/openspec validate changerail-contracts --strict`,
  `./bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py` passed before archive; public scan
  reported `603` files and `0` findings.
- `python3 scripts/run-release-baseline.py` passed: `26/26` steps, including
  OpenSpec validation, schema smoke, Python syntax inventory, ruff,
  current/history public-surface scans, delivery manifest smokes, runner/metrics
  smokes, generated drift fixture and whitespace check.
- Manifest validation and working-tree scope reconciliation passed:
  `bin/changerail-python scripts/changerail_delivery_manifest.py validate
  .runtime/changerail/delivery-manifests/010-04-add-manifest-scope-and-handoff.json
  --json` and `bin/changerail-python scripts/changerail_delivery_manifest.py
  scope-check .runtime/changerail/delivery-manifests/010-04-add-manifest-scope-and-handoff.json
  --target working-tree --json`.
- Post-archive `./bin/openspec validate --all --strict` passed: `14` specs;
  post-archive `git diff --check` passed.
- Test adequacy: positive and negative scope-check smokes execute the helper
  against real temporary Git repositories and would fail if extra staged paths,
  missing staged paths, operation mismatches, rename source/target handling,
  ignored runtime exclusions or path byte preservation regressed. Separate RED
  output was not retained.

## Archive
- `openspec/changes/archive/2026-08-01-add-manifest-scope-and-handoff/`

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `scripts/changerail_delivery_manifest.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `docs/changerail-contracts.md`
- `openspec/changes/archive/2026-08-01-add-manifest-scope-and-handoff/`

## Result
Implemented manifest scope reconciliation and concise handoff summaries.
Delivery manifest schema/helper now support `scope-check` for working-tree and
staged scopes, operation-aware missing/extra/mismatched diagnostics,
schema-backed verification/review/final-card summaries and helper-assisted
handoff updates. Docs, lifecycle skills, smoke fixtures and synced
`changerail-contracts` requirements were updated; the OpenSpec change is
archived and awaiting independent review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z карточка выделена из E1 delivery feedback.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
- 2026-08-01T19:37:49Z `changerail-ff` создал apply-ready artifacts для
  `add-manifest-scope-and-handoff` и перевел карточку в `3.inprogress`.
- 2026-08-01T19:38:43Z `changerail-ff` validation passed for active change,
  all OpenSpec specs, tracked diff whitespace and untracked artifact whitespace.
- 2026-08-01T19:55:56Z `changerail-do` реализовал manifest scope/handoff
  contract, выполнил focused smokes, public-surface scan и release baseline,
  синхронизировал specs и archived change
  `2026-08-01-add-manifest-scope-and-handoff`; карточка оставлена в
  `3.inprogress` для independent review.
- 2026-08-01T20:20:03Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
