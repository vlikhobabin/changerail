# Формализовать review rescue budget в runtime state

## Status
1.backlog

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
- none yet

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
not started

## Next
- После `020-03` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z lower-priority counter work выделено из E1 epic.
