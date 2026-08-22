## Context

Published investigation
`investigate-phase-routed-delivery-authorization-boundary` выбрала exact
replacement `implement-phase-routed-delivery-authorization-boundary`, его
authorization-time path в `3.inprogress`, ceiling 500 и protocol allowance для
новой aggregate/child authority boundary. Generic deterministic preflight уже
принимает только clean tracked `4.done` authorization source с exact reciprocal
relations; investigation decision сама этим source не является.

Successor уже содержит existing reciprocal contract: authorization source
depends on investigation, investigation blocks exact successor, а successor
depends on investigation и содержит inline reference на будущий published
authorization. Поэтому planning не должен менять blocked successor или
production surfaces: source of truth этой карточки — один authorization object
на target board card и delta requirement для `changerail-contracts`.

## Goals / Non-Goals

**Goals:**

- Опубликовать один exact six-field authorization object для выбранной цепочки.
- Ограничить exception ceiling 500 и только принятой aggregate/child authority,
  resume и status boundary.
- Сохранить fail-closed rejection любого несовпадения relation, id, path,
  ceiling или protocol flag.
- Подготовить deterministic evidence без production delta.

**Non-Goals:**

- Реализовывать или чинить phase-routed delivery payload.
- Разрешать третий repair исходной карточки, alternate aggregate runtime root,
  reusable waiver или ослабление global review policy.
- Изменять runner, schemas, CLI, credentials, provider authority или runtime
  state.

## Decisions

1. **Authorization source остается отдельной карточкой.** Clean tracked
   `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`
   будет единственным source, который объявляет exact investigation/successor
   ids и paths, ceiling и protocol flag. Считать investigation card неявным
   authorization отвергнуто: это обходит generic published-source gate.
2. **Object сохраняет generic six-field shape.** Он содержит только
   `investigation_card`, `investigation_id`, `successor_card`, `successor_id`,
   `production_loc_ceiling` и `allow_new_authority_or_wire_protocol`. Новые
   phase-specific wire fields не добавляются; scope allowance задается
   normative requirement и investigation decision.
3. **Canonical successor path привязан к authorization-time lane.** Source
   использует
   `openspec/board/3.inprogress/implement-phase-routed-delivery-authorization-boundary.md`.
   Текущий `2.todo` path является queue location, но не может заменить exact
   path, который preflight проверит при delivery successor.
4. **Используется существующий reciprocal contract.** Authorization source
   зависит от investigation, investigation блокирует exact successor, а
   successor зависит от investigation и ссылается на будущий canonical `4.done`
   source. Investigation не обязана блокировать authorization source; planning
   сохраняет эту metadata без unrelated edits.
5. **Verification использует существующий generic preflight oracle.** Focused
   non-production smoke должен принять fixture с exact phase-routed ids/paths и
   отклонить варианты с измененным id/path, investigation relation, ceiling или
   protocol flag в пределах existing reciprocal contract. Новые production
   hooks и raw runtime evidence не нужны.

## Risks / Trade-offs

- **[Risk] Lane/path drift инвалидирует authorization.** Это намеренный
  fail-closed binding; successor должен находиться в exact `3.inprogress` path
  при consumption.
- **[Risk] Protocol allowance может быть прочитано слишком широко.** Delta spec
  связывает его только с опубликованной investigation boundary и запрещает
  reusable waiver, alternate runtime root и global policy weakening.
- **[Risk] Delivery не может доказать clean `HEAD` source до publish.** Focused
  smoke проверяет contract fixture во время delivery, а реальный source
  становится consumable только после scoped publish в `4.done`.

## Migration Plan

1. Во время delivery сохранить exact object и reciprocal metadata без
   production changes.
2. Синхронизировать `changerail-contracts`, архивировать change и пройти strict,
   focused preflight, public-surface и whitespace verification.
3. После fresh review опубликовать authorization card в `4.done`.
4. Оставить successor заблокированным до publication; затем его отдельный flow
   переместит карточку в `3.inprogress` и повторно проверит exact chain.
