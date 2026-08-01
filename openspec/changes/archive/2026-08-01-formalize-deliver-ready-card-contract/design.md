## Context

Стандартная доска уже различает `2.todo` и `3.inprogress`: первая колонка
означает accepted story с ordered plan, вторая - apply-ready или уже
доставляемую story. При этом practical docs часто начинают с ручной цепочки
`ff -> do -> review -> pub`, из-за чего оператор может решить, что OpenSpec
artifacts нужно создать до запуска one-command delivery.

## Goals / Non-Goals

**Goals:**

- Дать одно проверяемое определение `deliver-ready` для accepted story.
- Сделать `$chrl-deliver <card>` normal operator handoff для такой карточки.
- Сохранить `ff/do/review/pub` как internal phases и явные repair/debug/resume
  surfaces.
- Обновить templates так, чтобы consumer project мог подготовить карточку без
  premature `openspec/changes/<slug>/` directories.

**Non-Goals:**

- Не добавлять шестую board column или второй независимый status field.
- Не автоматизировать product triage без operator authority.
- Не менять review, scope, archive или publish safety gates.
- Не добавлять новый runtime schema для readiness в рамках этой карточки.

## Decisions

- `deliver-ready` живет как predicate в methodology, board docs и templates.
  Его source of truth - наличие принятой story в `2.todo` с owner, observable
  acceptance, ordered change plan, понятными dependencies/gates и handoff.
- OpenSpec artifacts не входят в predicate. Если artifacts отсутствуют,
  `$changerail-deliver` начинает с `ff`, создает или дополняет artifacts, затем
  продолжает `do -> review -> pub`.
- `3.inprogress` остается apply-ready/review/publish lane. Карточка попадает
  туда после artifact readiness, а не на момент triage.
- Docs представляют `$chrl-deliver` как everyday operator path, сохраняя
  `$changerail-deliver` как canonical command. Phase commands описываются как
  internal phases and explicit repair/debug/manual-resume commands.
- Readiness diagnostics, если они появляются в runner или verifier, остаются
  advisory before acceptance и должны объяснять missing criteria. Эта карточка
  не требует нового blocking runtime gate.

## Risks / Trade-offs

- Термин `deliver-ready` может быть воспринят как новый status. Mitigation:
  явно связать его с `2.todo` и запретить новую lane/status.
- Упрощение handoff может скрыть полезность phase commands. Mitigation:
  оставить phase commands documented как repair/debug/manual-resume surface.
- Templates могут устареть относительно root board docs. Mitigation: обновить
  root docs и generated templates в одном reviewed payload и проверить
  bootstrap smoke.
