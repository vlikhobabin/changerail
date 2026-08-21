# Отчитываться о recovery-aware delivery episodes

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- Sanitized retrospective long-running supervised delivery с blocked attempts,
  manual recovery, independent review rescues и final publish.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Перед реализацией episode/attempt schemas требуется exact published
investigation authorization.

## Problem
ChangeRail независимо записывает каждый runner process, preflight и review
artifact. Поэтому у blocked/resumed карточки нет canonical delivery episode,
связывающего initial attempt, recovery attempts, operator intervention, review
cycles и publish result.

Текущий metrics report также считает preflight records delivered runs,
связывает final review history карточки с unrelated earlier preflights и не
учитывает manual recovery runs. Terminal performance сохраняет только последние
50 command summaries и 100 timeline events, поэтому long delivery нельзя
восстановить из structured records без raw agent logs и inference phases по
artifact timestamps.

## Goal
Предоставить privacy-safe recovery-aware delivery episode и trustworthy
retrospective metrics без сохранения prompts, command bodies или tool payloads.

## Acceptance
- Каждый card execution имеет stable `episode_id`; attempts preflight, delivery,
  recovery, review, rescue и publish имеют unique `attempt_id` и explicit
  parent/previous-attempt linkage.
- Каждый attempt записывает start/end time, terminal state, blocker class, phase
  transitions, active/wait/operator-wait durations, token usage, command/tool
  counts и bounded semantic outcome classes.
- Recovery через supported workflow создает тот же schema-versioned status и
  sanitized timing fields, что и original child.
- Review history append-only по cycle; current canonical verdict может
  заменяться, но prior cycle result, finding ids и timestamps остаются доступны
  episode report.
- `changerail-delivery-metrics` исключает preflight-only records из delivery
  success/first-pass-review rates, roll up attempts по episode и не связывает
  later review с unrelated preflight.
- Long runs сохраняют aggregate timing всех commands/MCP calls при truncated
  bounded samples; record сообщает sampling limits.
- Operator intervention для credential/license/external-state wait
  представляется value-free structured event и не сохраняет entered value или
  screen contents.
- Tests покрывают one-pass delivery, blocked/resumed delivery, multiple review
  rescues, abandoned recovery, preflight-only plans, truncated detail и
  secret-bearing synthetic tool output.

## Non-Goals
- Сохранение raw prompts, shell commands, MCP arguments/results или screenshots
  в committable state.
- Замена live progress heartbeat или retained-payload authorization model.
- Вывод business acceptance из process telemetry.

## Related
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `schemas/changerail-delivery-run.schema.json`
- `expose-structured-live-delivery-progress.md`
- `resume-retained-payload-after-external-blocker.md`
- `openspec/changes/record-recovery-aware-delivery-episodes/`
- `openspec/changes/report-recovery-aware-delivery-metrics/`

## Change Set
- `record-recovery-aware-delivery-episodes`
- `report-recovery-aware-delivery-metrics`

## Verify
- Contract/schema smokes для attempt/episode records.
- Metrics fixtures, доказывающие preflight exclusion и recovery rollup.
- End-to-end fake runner с blocker, resume, no-go rescue, go и publish.

## Result
Проработка завершена; два apply-ready changes созданы, реализация не начата.

## Next
- После завершения progress/external-resume dependencies и published
  investigation authorization выполнить
  `$chrl-deliver openspec/board/2.todo/report-recovery-aware-delivery-episodes.md`.

## Change 1: `record-recovery-aware-delivery-episodes`

### Why
Run status, plan status, review history и manifest связываются по card id или
timestamps и не образуют достоверную recovery lineage.

### Goal
Добавить explicit episode/attempt ids во все owner artifacts, derived ignored
episode index и complete aggregate telemetry с bounded samples.

### Acceptance
- New execution создает episode, supported resume наследует его и связывает
  unique typed attempts.
- Review/rescue/publish links не выводятся по card id или timestamp.
- Totals включают все events после truncation, а waits остаются value-free.
- Legacy runs изолируются с `unknown`, без ложных later review links.

### Depends On
- `expose-structured-live-delivery-progress`
- `resume-retained-payload-after-external-blocker`
- exact published investigation authorization for this card's episode/attempt
  wire contracts

### Related
- `openspec/changes/record-recovery-aware-delivery-episodes/`

## Change 2: `report-recovery-aware-delivery-metrics`

### Why
Текущий report считает preflight-only records delivery runs и присоединяет
review history несвязанным попыткам той же карточки.

### Goal
Перевести text/JSON/CSV metrics на one-row-per-episode rollup с explicit
denominators, recovery cost, complete totals и honest unknowns.

### Acceptance
- Preflight-only records не входят в delivery/review-rate denominators.
- Review/publish присоединяются только через episode/attempt lineage.
- Blocked/resumed/rescued episode имеет один final rollup без double count.
- Long-run totals не уменьшаются при truncation detail samples.

### Depends On
- `record-recovery-aware-delivery-episodes`

### Related
- `openspec/changes/report-recovery-aware-delivery-metrics/`

## Log
- 2026-08-20T17:30:00Z карточка создана из sanitized field-validation evidence.
- 2026-08-21T07:43:31Z исследование разделило owner-artifact lineage/episode
  materialization и metrics rollup; оба OpenSpec changes достигли apply-ready.
