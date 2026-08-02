# Зафиксировать native Windows architecture и test plan

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`030-native-windows-discovery`

## Series Index
`03`

## Source
- Результаты двух-host исследования `030-02`.

## Summary
Выбрать default/fallback native Windows runtime и wiring architecture,
зафиксировать tracked/untracked ownership, upgrade/drift model и обязательную
test matrix, затем полностью перепланировать серию `040`.

## Acceptance
- Architecture decision выбирает один default path и bounded fallbacks.
- Явно определены prerequisites: shell, Python, Git, Developer Mode/elevation.
- Определено, какие wiring artifacts tracked, generated ignored или copied.
- Описаны bootstrap, verify, drift, upgrade и cleanup semantics.
- Threat model покрывает junction traversal, accidental staging, credentials,
  command quoting и untrusted repository content.
- Test matrix включает оба Windows hosts и deterministic local fixtures.
- Все cards серии `040` обновлены против решения до delivery.

## Scope
- Architecture/design docs, compatibility contract и implementation backlog.
- Изменение состава/порядка серии `040`.

## Non-Goals
- Реализация выбранной architecture.
- Обещание unsupported Windows editions без evidence.

## Depends On
- `030-02-reproduce-windows-runtime-wiring-and-git-behavior`

## Implementation Notes
- Не сохранять несколько равноправных default strategies.
- Если host results расходятся, support matrix должна объяснять branching rule,
  а не скрывать несовместимость.

## Change Set
- `freeze-native-windows-architecture`
- `refresh-native-windows-implementation-series`

## Verify
- Architecture review против `030-01`/`030-02` tracked evidence -> passed;
  `docs/compatibility.md` cites retained sanitized evidence and records caveats
  for elevated-only symlink results.
- Cross-link и board series consistency checks -> passed; `040-01`..`040-05`
  remain in `1.backlog` and keep dependency order entrypoints -> wiring ->
  verifier/Git safety -> smoke -> end-to-end proof.
- `./bin/openspec validate freeze-native-windows-architecture --strict` ->
  passed.
- `./bin/openspec validate refresh-native-windows-implementation-series --strict` ->
  passed.
- `./bin/openspec validate changerail-windows-native-architecture --strict` ->
  passed after spec sync.
- `./bin/openspec validate changerail-windows-implementation-series --strict` ->
  passed after spec sync.
- `./bin/openspec validate --all --strict` -> passed after archive, 20 items.
- `git diff --check` -> passed.
- `python3 scripts/public-surface-scan.py` -> passed, 685 files scanned,
  0 findings.
- `python3 scripts/public-surface-scan.py --history` -> passed, 685 files
  scanned, 0 findings.
- `python3 scripts/run-release-baseline.py` -> passed, 27 steps.
- Review cycle 1 returned `no-go` on `R1`: fresh reviewer saw
  `python3 scripts/run-release-baseline.py` fail at step 20
  `delivery runner one-command smoke` with `timeout git ls-remote attempts
  mismatch: 1 != 2`. Same-card rescue did not change tracked runtime/test
  code; focused `python3 scripts/smoke-delivery-runner.py` passed three
  consecutive reruns, then `python3 scripts/run-release-baseline.py` passed
  27 steps including step 20.
- `bin/changerail-python scripts/changerail_delivery_manifest.py scope-check .runtime/changerail/delivery-manifests/030-03-freeze-native-windows-architecture.json --target working-tree --json` ->
  passed with no missing, extra or mismatched paths.

## Archive
- `freeze-native-windows-architecture` ->
  `openspec/changes/archive/2026-08-02-freeze-native-windows-architecture/`.
- `refresh-native-windows-implementation-series` ->
  `openspec/changes/archive/2026-08-02-refresh-native-windows-implementation-series/`.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/changes/archive/2026-08-02-freeze-native-windows-architecture/`
- `openspec/changes/archive/2026-08-02-refresh-native-windows-implementation-series/`
- `openspec/specs/changerail-windows-native-architecture/spec.md`
- `openspec/specs/changerail-windows-implementation-series/spec.md`
- `docs/compatibility.md`
- `docs/wiring-discovery.md`

## Result
Architecture frozen: native Windows default is tracked `.cmd` entrypoints plus
generated project-local wiring with verifier/drift ownership. Symlink and
junction modes are explicit bounded fallbacks, not defaults. Series `040` has
been refreshed against this decision and remains in `1.backlog`; implementation
is intentionally out of scope for this card.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `freeze-native-windows-architecture`

### Why
Нужно превратить two-host evidence из `030-01` и `030-02` в один
evidence-backed native Windows default path с явно ограниченными fallback-ами.

### Goal
Зафиксировать runtime entrypoints, Windows wiring default, generated/tracked
ownership, drift/upgrade/cleanup semantics, threat model и mandatory test
matrix для реализации серии `040`.

### Scope
- `docs/compatibility.md`
- `docs/wiring-discovery.md`
- `openspec/specs/changerail-windows-native-architecture/spec.md`
- OpenSpec artifacts for `freeze-native-windows-architecture`

### Acceptance
- `.cmd` выбран как native Windows command default; extensionless wrappers and
  implicit Bash rejected as defaults.
- Generated project-local wiring выбран как least-privilege Windows default;
  symlink/junction fallbacks explicitly bounded.
- Prerequisites, ownership, drift/upgrade/cleanup, threat model and test matrix
  documented with sanitized evidence.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-02-freeze-native-windows-architecture/`

## Change 2: `refresh-native-windows-implementation-series`

### Why
Серия `040` была provisional до финального решения `030-03`; implementation
cards должны стартовать из выбранной architecture, а не из старых hypotheses.

### Goal
Обновить `040` epic и cards `040-01`..`040-05` против selected default,
fallback policy, ownership semantics and verification matrix.

### Scope
- `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
- `openspec/board/1.backlog/040-01-add-windows-runtime-entrypoints.md`
- `openspec/board/1.backlog/040-02-add-windows-wiring-backend.md`
- `openspec/board/1.backlog/040-03-add-windows-verification-and-git-safety.md`
- `openspec/board/1.backlog/040-04-add-windows-automated-smoke.md`
- `openspec/board/1.backlog/040-05-prove-native-windows-end-to-end.md`
- OpenSpec artifacts for `refresh-native-windows-implementation-series`

### Acceptance
- `040` epic no longer says provisional and links to the `030-03` decision.
- Each executable `040` card has refreshed scope, acceptance, dependencies,
  verification floor and next handoff.
- No `040` card is moved out of `1.backlog` by this refresh.

### Depends On
- `freeze-native-windows-architecture`

### Related
- `openspec/changes/archive/2026-08-02-refresh-native-windows-implementation-series/`

## Log
- 2026-08-01T15:07:29Z карточка создана как research exit gate.
- 2026-08-02T05:48:42Z переведена в `2.todo` как завершающая карточка серии
  `030`; ее publish должен обновить планирование серии `040`.
- 2026-08-02T07:25:17Z `$changerail-deliver` начал fast-forward planning:
  добавлены ordered changes `freeze-native-windows-architecture` и
  `refresh-native-windows-implementation-series`.
- 2026-08-02T07:25:17Z fast-forward завершен: OpenSpec artifacts для обоих
  changes созданы и прошли validation; карточка переведена в `3.inprogress`.
- 2026-08-02T07:27:00Z delivery обновил compatibility/wiring docs, synced
  specs и series `040` backlog против selected Windows architecture.
- 2026-08-02T07:34:32Z delivery archived `freeze-native-windows-architecture`
  and `refresh-native-windows-implementation-series`; карточка оставлена в
  `3.inprogress` до fresh independent review.
- 2026-08-02T07:41:35Z full release baseline passed 27 steps including
  public-surface current/history scans and ignored-status check.
- 2026-08-02T07:49:27Z independent review cycle 1 returned `no-go` for
  reviewer-observed release baseline failure in delivery runner smoke.
- 2026-08-02T08:00:27Z same-card rescue reran focused delivery runner smoke
  three consecutive times and reran full release baseline; all passed. Fresh
  re-review required before publish.
- 2026-08-02T08:14:45Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
