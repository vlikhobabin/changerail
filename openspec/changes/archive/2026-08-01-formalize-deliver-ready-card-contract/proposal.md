## Why

Операторы уже передают принятые карточки в `$chrl-deliver`, но текущая
терминология смешивает готовность карточки с готовностью OpenSpec artifacts.
Нужен проверяемый contract `deliver-ready`, который объясняет, когда карточку
можно передать в one-command delivery без добавления новой board lane.

## What Changes

- Определить `deliver-ready` как свойство принятой story в `2.todo`: scope
  принят, владелец известен, acceptance observable, ordered change plan записан,
  а gates и следующий handoff понятны.
- Зафиксировать, что OpenSpec artifacts не являются precondition для запуска
  `$chrl-deliver <card>`; artifacts остаются результатом internal `ff` phase.
- Переформулировать lifecycle guidance так, чтобы `$chrl-deliver <card>` был
  normal operator handoff, а `ff/do/review/pub` оставались internal phases или
  explicit repair/debug/manual-resume commands.
- Обновить board docs и project templates так, чтобы generated consumers могли
  подготовить deliver-ready card без premature OpenSpec changes и без шестой
  board column.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-agent-methodology`: shared methodology and board docs must define
  the deliver-ready card contract and normal one-command handoff.
- `changerail-skill-surface`: lifecycle skill guidance must allow
  `$changerail-deliver <card>` to start from an accepted ordered card before
  OpenSpec artifacts exist.
- `changerail-project-templates`: consumer board templates must prepare
  deliver-ready cards without requiring premature OpenSpec change directories.

## Impact

- Affected files: shared methodology, board docs, project templates and
  ChangeRail lifecycle skill wording.
- No runtime state, secrets, private workspace names or consumer-specific
  project data are committed.
