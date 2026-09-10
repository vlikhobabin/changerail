# Recovery после технического отказа model session

## Status
2.todo

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

## Result
accepted native OpenSpec plan; structural admission only

## Next
- native-accept после проверки плана
