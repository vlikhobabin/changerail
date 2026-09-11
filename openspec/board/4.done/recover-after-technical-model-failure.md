# Recovery после технического отказа model session

## Status
4.done

## Lifecycle
openspec-v1

## OpenSpec Stage
artifacts

## Summary
Текущий delivery run остановился на группе 3 из-за `Selected model is at capacity` после завершённых групп 1–2. Нужен отдельный безопасный recovery без переписывания старого run.

## Acceptance
- [C1] Recognized capacity failure до старта следующей группы создаёт один successor.
- [C2] Старый run, evidence, checkpoints, payload и review accounting побайтно сохраняются.
- [C3] Неизвестный/semantic/live/writer-started failure отклоняется fail-closed.
- [C4] Duplicate/race/drift не создают второй successor или новый review allowance.

## Scope
- `scripts/changerail/local_delivery.py`, recovery receipts, model adapter, tests, docs.

## Non-Goals
- Не менять текущую карточку и её продуктовый scope; не разрешать review №3; не менять qa-mcp; не восстанавливать operator-stopped runs.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `recover-after-technical-model-failure`

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Delivery Budget
- primary_invariant: one exact successor after a pre-group technical model failure
- expected_wall_minutes: 120
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 8
- estimated_production_loc: 700

## Verify
- Strict OpenSpec validation, focused pytest, Ruff, diff check, synthetic E2E с сохранением старого run.
```json
{"schema":"changerail.card-evidence.v1","conditions":[{"condition":"C1","seam":"technical recovery","precondition":"capacity failure before next group","action":"prepare and apply","expected":"one successor","method":{"kind":"test","target":"tools/changerail/tests/test_local_changerail_delivery.py"},"stage":"implementation"},{"condition":"C2","seam":"history","precondition":"completed checkpoints","action":"recover","expected":"old bytes unchanged","method":{"kind":"test","target":"tools/changerail/tests/test_openspec_recovery_boundaries.py"},"stage":"implementation"},{"condition":"C3","seam":"fail closed","precondition":"ambiguous failure","action":"recover","expected":"reject","method":{"kind":"test","target":"tools/changerail/tests/test_native_execution_contract.py"},"stage":"implementation"},{"condition":"C4","seam":"idempotency","precondition":"duplicate apply","action":"retry","expected":"same successor","method":{"kind":"test","target":"tools/changerail/tests/test_native_openspec_integration.py"},"stage":"implementation"}],"risks":[{"kinds":["input_safety","mutation","restart","concurrency"],"applies":true,"decision":"append-only receipt and project lock","conditions":["C1","C2","C3","C4"]},{"kinds":["publication","external_effects"],"applies":false,"decision":"recovery does not publish or touch consumer runtime","conditions":[]}]}
```

## Design
- Append-only receipt связывает predecessor, failure class, session, group, fallback model и payload fingerprint; старый run не переписывается.
- Successor создаётся только один раз после подтверждения, что writer следующей группы не стартовал.

## Log
- 2026-09-10 Карточка создана после технического отказа model session; реализация ещё не начата.

- 2026-09-10T17:32:17Z accepted native OpenSpec plan

- 2026-09-10T17:56:14Z started native OpenSpec delivery

- 2026-09-10T18:15:09Z change-2: реализованы атомарный successor из технического receipt и запуск только назначенной группы через зафиксированный fallback model; focused pytest proof записан.

- 2026-09-10T18:37:30Z change-3 (время completion event): добавлены fail-closed регрессии и synthetic successor flow, documented opt-in fallback route; strict OpenSpec validation, focused pytest, Ruff и diff check прошли.

- 2026-09-10T18:40:58Z finalize (время окончания сессии; sync выполнен ранее): delta `native-delivery` семантически перенесена в canonical spec; `native-sync` receipt записан для текущего run.

- 2026-09-10T18:54:43Z post-stop audit: временные метки Log уточнены по сохранённым phase/session receipts; первоначальные будущие значения и последующие приблизительные исправления не использованы как доказательство. Выявлены frozen-identity, lifecycle и no-writer дефекты recovery; исправления выполняются вне остановленного run, новые проверки не записываются от имени его worker.

- 2026-09-11T10:41:15Z self-host finalize: delta `native-delivery` сопоставлена с уже семантически эквивалентным canonical requirement без дублирования; `native-sync` receipt и sync report сохранены в successor run. Актуальные strict validation, 580 focused recovery regressions, Ruff из project venv и diff check записаны как evidence для fingerprint successor.

- 2026-09-11T10:52:36Z finalize: повторно подтверждён semantic no-op delta `native-delivery`; mapping report и обновлённый `native-sync` receipt сохранены в текущем successor run. Product code, canonical spec и task checklist не изменялись.

- 2026-09-11T11:05:13Z finalize: в текущем self-host successor сохранены delta-to-canonical mapping с deliberate semantic no-op и свежий `native-sync` receipt; canonical spec, продуктовый код и чеклист задач не изменялись.

- 2026-09-11T11:25:34Z repair после semantic NO-GO: в закреплённых Verify-файлах добавлены recovery-specific регрессии C1–C4. Они вызывают реальные prepare/apply/reconcile, проверяют successor, неизменность predecessor и review budget, fail-closed boundary, idempotency/lock/fallback/payload drift; task-group worker явно изолирован как test seam. Focused receipts и observed proofs будут обновлены для нового payload перед handoff.

- 2026-09-11T11:35:43Z archive-refresh: после provisional GO штатный OpenSpec archive переместил change в `openspec/changes/archive/2026-09-11-recover-after-technical-model-failure`; product code, canonical spec и archived artifacts не изменялись. Archive изменил fingerprint payload, поэтому reuse не заявляется: C1–C4 focused receipts и observed proofs переисполняются перед новым handoff в mandatory continuation independent review.

## Result
Все три группы завершены и сохранены без replay. Semantic sync остаётся deliberate no-op: canonical requirement уже покрывает delta без дублирования. OpenSpec change штатно архивирован после provisional GO; archive receipt сохраняет exact artifact bytes. Для архивированного payload переисполняются focused C1–C4 receipts и observed proofs перед новым handoff в обязательный independent final review. Final verification и публикация этой карточки ещё не выполнены.

## Next
- continue with the next dependency-ready epic card

## Delivery Receipt

- Independent review: `GO` at `2026-09-11T11:44:08Z`.
- Final repository verification: `passed` at `2026-09-11T12:25:58Z`; 2/2 configured commands succeeded.
- Pytest: `1010 passed in 2477.61s (0:41:17)`.
- Deterministic done transition recorded at `2026-09-11T12:26:11Z` for publish.
