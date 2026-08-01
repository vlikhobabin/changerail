# Формализовать review rescue budget в runtime state

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`020-one-command-delivery-experience`

## Series Index
`04`

## Source
- Реальный delivery run дошел до нескольких review cycles; human wording и
  metrics не показывали одинаково used/remaining attempts.

## Summary
Развести initial review, review cycle и same-card rescue attempt в schemas,
status, history, metrics и docs, не меняя bounded fail-closed policy.

## Acceptance
- Docs однозначно определяют initial review, rescue attempt и re-review cycle.
- Runtime state хранит limit, used и remaining same-card rescue attempts.
- Первый review не считается использованной rescue attempt.
- Metrics показывают first-pass GO и rescue budget без вычислений из prose.
- Legacy history без новых optional fields остается читаемой как `unknown`.
- Exhausted budget ведет к linked rescue/investigation policy, а не publish.

## Scope
- Deliver/review wording, run/history schemas и metrics.
- Migration compatibility для существующих runtime records.

## Non-Goals
- Увеличение default rescue limit.
- Автоматическое исправление blocker findings вне card scope.

## Depends On
- `020-03-add-remote-preflight-diagnostics-and-resume`

## Implementation Notes
- Вычислять counters из canonical cycle history или атомарно обновлять их в
  одном owner path; не хранить несколько расходящихся источников истины.

## Change Set
- `model-review-rescue-budget` (planned)

## Change 1: `model-review-rescue-budget`

### Why
Actual delivery runs now use review cycles and same-card rescues, but runtime
state and metrics do not expose used/remaining rescue attempts consistently.

### Goal
Model initial review, re-review cycle and same-card rescue attempt in one
canonical runtime/history/metrics contract without weakening fail-closed policy.

### Scope
- Deliver/review wording, run/history schemas and metrics.
- Migration compatibility for existing runtime records.

### Acceptance
- Docs однозначно определяют initial review, rescue attempt и re-review cycle.
- Runtime state хранит limit, used и remaining same-card rescue attempts.
- Первый review не считается использованной rescue attempt.
- Metrics показывают first-pass GO и rescue budget без вычислений из prose.
- Legacy history без новых optional fields остается читаемой как `unknown`.
- Exhausted budget ведет к linked rescue/investigation policy, а не publish.

### Depends On
- `add-remote-preflight-diagnostics-and-resume`

### Related
- `openspec/changes/model-review-rescue-budget/`

## Verify
- Review cycle history schema/metrics smoke.
- Exhaustion и legacy-record fixtures.
- Skill/docs drift checks и release baseline.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `schemas/changerail-review-cycle-history.schema.json`
- `bin/changerail-delivery-metrics`
- `skills/changerail-deliver/SKILL.md`

## Result
deliver-ready after series `010` exit audit

## Next
- `$chrl-deliver openspec/board/2.todo/020-04-model-review-rescue-budget.md`

## Log
- 2026-08-01T15:07:29Z lower-priority counter work выделено из E1 epic.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
