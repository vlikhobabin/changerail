# Формализовать deliver-ready contract карточки

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`020-one-command-delivery-experience`

## Series Index
`01`

## Source
- Consumer operator feedback от 2026-08-01.

## Summary
Определить `deliver-ready` как проверяемое свойство принятой story, а не новую
board lane: карточка scoped, owned, имеет observable acceptance, ordered change
plan и известные gates, но OpenSpec artifacts еще могут отсутствовать.

## Acceptance
- `deliver-ready` определен в shared methodology, board docs и templates.
- Для стандартной доски состояние соответствует принятой карточке в `2.todo`
  с ordered plan; новая шестая колонка не добавляется.
- OpenSpec artifacts не являются precondition для запуска `$chrl-deliver`.
- `$chrl-deliver <card>` представлен как normal operator handoff.
- `ff/do/review/pub` описаны как internal phases или явные
  repair/debug/manual-resume commands.
- Templates позволяют подготовить deliver-ready card без premature changes.

## Scope
- Shared agent methodology, board docs/templates и deliver/ff wording.
- Readiness diagnostics в runner только если они остаются advisory до явного
  принятия карточки.

## Non-Goals
- Автоматическое product triage без operator authority.
- Создание OpenSpec artifacts при заполнении карточки.

## Depends On
- Серия `010-core-release-contracts` завершена.

## Implementation Notes
- Избегать второго независимого status field, который может расходиться с
  board path.
- Readiness predicate должен объяснять missing criteria, а не только отдавать
  boolean.

## Change Set
- `formalize-deliver-ready-card-contract` (planned)

## Change 1: `formalize-deliver-ready-card-contract`

### Why
Accepted board cards can currently be handed to phase commands or
`$chrl-deliver` with ambiguous readiness language, so operators still infer
whether OpenSpec artifacts are required before delivery.

### Goal
Define `deliver-ready` as the accepted-card contract for normal one-command
handoff while keeping `ff/do/review/pub` as internal phases or explicit repair
surfaces.

### Scope
- Shared methodology, board docs, templates and skill wording.
- Advisory readiness diagnostics if they stay non-blocking before card
  acceptance.

### Acceptance
- `deliver-ready` определен в shared methodology, board docs и templates.
- Для стандартной доски состояние соответствует принятой карточке в `2.todo`
  с ordered plan; новая шестая колонка не добавляется.
- OpenSpec artifacts не являются precondition для запуска `$chrl-deliver`.
- `$chrl-deliver <card>` представлен как normal operator handoff.
- `ff/do/review/pub` описаны как internal phases или явные
  repair/debug/manual-resume commands.
- Templates позволяют подготовить deliver-ready card без premature changes.

### Depends On
- `010-core-release-contracts`

### Related
- `openspec/changes/formalize-deliver-ready-card-contract/`

## Verify
- Docs/template consistency smoke.
- Bootstrap project smoke.
- Skill discovery smoke, release baseline и `git diff --check`.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `AGENTS.shared.md`
- `docs/board-and-two-agent-feature-flow.md`
- `templates/project/openspec/board/README.md.tpl`

## Result
deliver-ready after series `010` exit audit

## Next
- `$chrl-deliver openspec/board/2.todo/020-01-formalize-deliver-ready-card-contract.md`

## Log
- 2026-08-01T15:07:29Z исходная карточка уточнена без введения новой board lane.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
