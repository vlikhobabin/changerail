## Why

Неопубликованный Scope A объединил пассивное admission/registry поведение с
активацией terminal release authority и не смог доказать обе границы в одном
bounded payload до единственного дорогого capture. Нужна новая decision-only
lineage, которая оставляет failed Scope A forensic-only и разрешает независимо
проверить dormant A1 до создания authoritative A2.

## What Changes

- Фиксируется точное и непересекающееся владение A1 passive admission/registry
  library и A2 terminal authority activation.
- Фиксируются два будущих six-field authorization objects с отдельными
  ceiling `500`: protocol `false` для A1 и `true` только для A2.
- Для A1 вводится обязательная structural dormancy и negative-wiring oracle;
  история, full baseline и authority receipt для A1 запрещены как нерелевантные.
- Для A2 фиксируются atomic one-shot capture, exact terminal receipt equality и
  нулевой repair/retry/rescue budget.
- Сохраняется неизменный порядок scanner-v2, Windows scheduler, verify-project и
  двух release-smoke наборов после опубликованных A1 и A2.
- Неопубликованный Scope A и его code/tests/diff/evidence/runtime state остаются
  forensic-only и не становятся допустимым источником реализации.

## Capabilities

### New Capabilities

- Нет.

### Modified Capabilities

- `changerail-release-ci`: заменить broad Scope A future path точной
  двухступенчатой A1/A2 authority boundary без ослабления full-release gate.

## Impact

Изменяются только decision/card и OpenSpec contract для release CI. В этой
карточке нет executable code, тестовой реализации, runtime state, consumer
изменений или activation authority; production/test/runtime additions равны
нулю.
