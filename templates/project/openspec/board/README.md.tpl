# {{PROJECT_NAME}} Board

Файловая доска проекта живет в `openspec/board/`.

## Layout

- `1.backlog/` - идеи и проблемы до triage.
- `2.todo/` - принятые задачи с ordered change plan.
- `3.inprogress/` - apply-ready stories в работе.
- `4.done/` - завершенные задачи с результатом и verification.
- `5.canceled/` - закрытые без реализации или вынесенные за scope.

## Rules

- Одна задача = один markdown-файл.
- В `2.todo/` и `3.inprogress/` карточка содержит sections
  `## Change 1:`, `## Change 2:` и так далее.
- `Related` содержит project-local paths или generic public examples.
- Runtime evidence may be referenced, but raw runtime state stays ignored.
