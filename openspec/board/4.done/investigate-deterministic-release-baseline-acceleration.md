# Исследовать детерминированное ускорение release baseline

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 01

## Source
- Operator request от 2026-08-24: остановить текущую authorization lineage на
  безопасном handoff и радикально ускорить три самых дорогих этапа полного
  release baseline до продолжения phase-routed delivery.

## Summary
Принять публичное decision о безопасном ускорении `public-surface-scan
--history`, `smoke-review-preflight` и `smoke-delivery-runner`. Полный baseline
должен по-прежнему запускать все обязательные проверки; ускорение достигается
content-addressed reuse, устранением process-per-file/process-per-case работы и
параллельным выполнением действительно изолированных групп с детерминированной
агрегацией.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- none

## Blocks
- implementation cards selected by this investigation

## Acceptance
- Измерены cold/warm wall costs обоих smoke и cold wall плюс identical
  cold/warm work count history scan без повторного полного baseline; отдельный
  второй 627.163-second history run исключён bounded constraint.
- Выбран алгоритм history scan, который сканирует каждый релевантный Git blob
  ограниченное число раз, сохраняет path-sensitive policy semantics и
  fail-closed инвалидирует cache при изменении scanner policy или Git inputs.
- Выбрана безопасная схема параллельных групп для review-preflight и delivery
  runner smoke с отдельными temp roots, bounded worker count, timeout и
  детерминированным порядком diagnostics.
- Решение не разрешает пропуск обязательного baseline: каждая команда остаётся
  вызванной, а reuse допустим только внутри шага по проверяемому content key.
- Зафиксированы parity, negative, corruption, invalidation, frozen completeness
  oracle и reproducible timing/RSS acceptance, а implementation разделена на
  bounded independently reviewable cards.
- Decision-only delivery не меняет production scripts/tests/schemas/runtime и
  получает fresh independent review до публикации.

## Change Set
- `decide-deterministic-release-baseline-acceleration`
- `openspec/changes/decide-deterministic-release-baseline-acceleration/`

## Verify
- `bin/openspec validate decide-deterministic-release-baseline-acceleration --strict`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- JSON/TOML parse, `git diff --check` и scoped status/diff.
- Bounded inventory without `--history`: 92 reachable commits, 102706 selected
  occurrences, 1652 unique blobs and 1959 unique `(blob,path)` identities.
- Static inventory confirms exactly 36 release baseline steps; the decision did
  not run the full baseline or a second history scan.

## Archive
- `openspec/changes/archive/2026-08-24-decide-deterministic-release-baseline-acceleration/`
- Delta requirements synced to `openspec/specs/changerail-release-ci/spec.md`.

## Related
- `scripts/public-surface-scan.py`
- `scripts/smoke-review-preflight.py`
- `scripts/smoke-delivery-runner.py`
- `scripts/run-release-baseline.py`
- `openspec/changes/decide-deterministic-release-baseline-acceleration/`

## Result
Archived decision фиксирует fresh reachability, conservative exact `(blob,path)`
identity, policy digest, batch object I/O, fail-closed cache validation,
process-isolated smoke registry, frozen legacy completeness oracle, bounded
jobs/timeouts/RSS и deterministic aggregation. Retained evidence index хранит
exact commands, outputs и durations; production implementation, successor cards
и baseline receipts не созданы. После repair нужен fresh independent review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-deterministic-release-baseline-acceleration`

### Why
Полный release baseline остаётся обязательным, но повторная работа трёх
доминирующих этапов делает каждую review/publish итерацию чрезмерно долгой.

### Goal
Опубликовать измеренное, fail-closed и implementation-ready решение, которое
радикально уменьшит wall-clock time без ослабления проверок.

### Acceptance
- Decision точно задаёт keys, invalidation, isolation, parallel aggregation,
  compatibility и rollout для каждого из трёх этапов.
- Decision задаёт два ordered successor scopes без создания их cards:
  `accelerate-path-sensitive-public-history-scan`, затем
  `parallelize-isolated-release-smoke-cases`.

### Depends On
- none

### Related
- `openspec/changes/decide-deterministic-release-baseline-acceleration/`

## Log
- 2026-08-24T00:00:00Z card created after bounded authorization handoff.
- 2026-08-24T17:40:41Z FF established the bounded current history inventory
  (102706 selected occurrences versus 1959 unique `(blob,path)` identities)
  without a full baseline. Preliminary unretained smoke samples from this phase
  are superseded by the retained repair captures recorded below.
- 2026-08-24T17:40:41Z one decision change made apply-ready; two ordered future
  successor scopes recorded without creating successor cards or implementation
  payload.
- 2026-08-24T17:40:41Z Preliminary warm-host smoke samples were not retained as
  evidence and are superseded by the retained repair captures recorded below;
  a second history run was excluded by the bounded investigation.
- 2026-08-24T17:49:35Z DO confirmed the published timing evidence and bounded
  inventory without a full baseline or repeated history scan; strict change/all
  validation, current public scan, JSON/TOML parsing and whitespace checks pass.
- 2026-08-24T17:49:35Z synced exactly the three acceleration requirements,
  archived the decision change and retained this card in `3.inprogress` for a
  fresh independent review.
- 2026-08-24T18:12:58Z repair retained and validated
  `.runtime/changerail/evidence/investigate-deterministic-release-baseline-acceleration/index.json`:
  canonical prior index extraction confirms history 627.163 s
  (14:39:56--14:50:23) and full baseline 1810.799 s (15:17:36--15:47:47);
  metadata inventory, three-sample object-I/O microbenchmark and fresh cold/warm
  standalone smoke captures are separately recorded. No history scan or full
  baseline was rerun.
- 2026-08-24T18:12:58Z repair corrected the conservative current-path fixture,
  added the frozen parent-blob completeness oracle and made fixture/environment,
  sampling/variance and numeric RSS acceptance explicit in archive delta and
  synced main requirement. Same-card repair budget is `1/1`; cycle-1 review
  verdict/history remain unchanged.
- 2026-08-24T18:54:12Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
