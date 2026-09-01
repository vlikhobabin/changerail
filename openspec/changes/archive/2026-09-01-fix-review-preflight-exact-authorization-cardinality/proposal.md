## Why

Deterministic review preflight сейчас берет первое authorization field и считает
reciprocal relation выполненной при наличии хотя бы одной matching reference.
Из-за этого clean source с duplicate `Investigation authorization` и лишней
dependency получает `valid` и допускается к semantic review вопреки published
fail-closed release decision.

## What Changes

- Ввести generic exact-cardinality boundary для двухполевого successor
  reference и шестиполевого authorization source без special-case card id.
- Требовать unique decoded JSON keys, exact key sets и существующие строгие
  types до filesystem/relation semantics.
- Сделать relation sections однозначными: один section, одна exact source
  dependency, ровно одно expected successor/investigation relation occurrence;
  сохранить unrelated successor dependencies и другие targets shared
  investigation.
- Возвращать invalid bounded chain как `investigation-required` до semantic
  review и добавить connected adversarial regression matrix.
- Уточнить generic contract и public docs, явно разрешив конфликт с прежней
  multi-candidate идеей в пользу exact-one published source field. JSON вне
  exact field по-прежнему не является authorization candidate.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: deterministic preflight принимает bounded
  authorization только при exact field/JSON/relation cardinality и сохраняет
  совместимость легитимных unrelated board relations.

## Impact

Затрагиваются `scripts/changerail_review_preflight.py`, focused
`scripts/smoke-review-preflight.py`, delta capability `changerail-contracts` и
`docs/changerail-contracts.md`. Production delta остается существенно меньше
300 LOC. Не меняются result schema, authority/wire protocol, provider,
credential, workflow, mutation surface, конкретные authorization/successor/
release cards, release objects, assets или `.github/workflows/*`.
