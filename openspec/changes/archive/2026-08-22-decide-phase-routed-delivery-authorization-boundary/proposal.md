## Why

Независимый cycle-3 review остановил неопубликованный
phase-routed delivery payload: его aggregate/child dirty-worktree
authorization противоречит schema-valid plan forms и не имеет
обязательного published investigation authorization. Два same-card
repair исчерпаны, поэтому нужно decision-only решение и точный
replacement boundary до любой следующей реализации.

## What Changes

- Зафиксировать единый fail-closed contract: `max_repair_cycles`
  обязателен для opt-in phase routing; его отсутствие отклоняет plan до
  aggregate и child launch.
- Выбрать canonical card identity как пару workspace identity и
  canonical card path; declared plan card id сохраняется как wire
  identity и может отличаться от filename stem.
- Определить resume как новый aggregate run, который до dirty child
  preflight пишет schema-valid canonical parent status, привязанный к
  новому child и previous-run lineage.
- Разрешить только exact same-phase `BLOCKED -> retry` переход с
  новой attempt identity и неизменным payload; не возобновлять terminal
  `DELIVERED`, review `GO` и exhausted-budget `NO-GO`.
- Отклонять noncanonical aggregate `--runtime-root` для phase-routed
  mode на admission до child launch; monolithic plan behavior не меняется.
- Разделить authority и provenance поля parent status, не обещая
  криптографическую защиту от полностью согласованной same-user
  фальсификации.
- Привязать exact replacement
  `implement-phase-routed-delivery-authorization-boundary` и отдельную
  authorization-card `authorize-bounded-phase-routed-delivery-payload` к
  ceiling 500 без ослабления regression floor.
- Не изменять production runner, schemas, smoke implementation, CLI и
  runtime behavior в этом change.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: tracked investigation decision задает
  exact aggregate/child authorization contract, replacement boundary и
  обязательную production regression matrix.

## Impact

- Affected tracked files: target board card и
  `openspec/changes/decide-phase-routed-delivery-authorization-boundary/`.
- Expected payload is board/OpenSpec documentation only. Production runner,
  schemas, tests, CLI и runtime behavior остаются неизменными.
- Consumer impact is deferred: phase-routed mode не может быть
  опубликован или допущен к pilot wave до publication этого
  investigation, exact authorization source, implementation и fresh
  independent `GO` successor-карточки.
