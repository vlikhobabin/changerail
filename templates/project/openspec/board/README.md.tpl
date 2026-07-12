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

## Gates

- `1.backlog -> 2.todo`: scope истории принят к проработке.
- `2.todo -> 3.inprogress`: ordered change plan и OpenSpec artifacts готовы.
- `3.inprogress -> 4.done`: fresh independent `go` verdict получен, scoped
  publish завершен, и карточка финализирована post-publish metadata.
- `* -> 5.canceled`: принято явное решение не продолжать.

## Agent Workflow

ChangeRail workflow:

```text
explore -> ff -> do -> review -> pub
```

`deliver` выполняет supervised full flow для одной карточки или bounded queue,
но обрабатывает карточки по одной. `do` реализует, проверяет, синхронизирует
specs и архивирует changes, оставляя review-gated карточку в `3.inprogress`.
`review` должен быть fresh context, который не планировал и не реализовывал
payload. `pub` публикует только после fresh valid `go` verdict.

Практический guide по доскам и двум агентам находится в
`{{CHANGERAIL_ROOT}}/docs/board-and-two-agent-feature-flow.md`; reusable agent
contract встроен в project `AGENTS.md` из `{{CHANGERAIL_ROOT}}/AGENTS.shared.md`.
