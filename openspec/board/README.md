# OPSX Board

Файловая доска проекта для развития OPSX через собственный workflow.

Доска живет в `openspec/board/`, потому что карточки являются story-level
входом, а `openspec/changes/` содержит apply-ready OpenSpec changes для этих
историй.

## Layout

- `1.backlog/` - идеи, проблемы и предложения до triage.
- `2.todo/` - принятые задачи, которые нужно разложить на ordered changes.
- `3.inprogress/` - задачи с apply-ready change-set, взятые в работу.
- `4.done/` - завершенные задачи с зафиксированным результатом.
- `5.canceled/` - закрытые без реализации или вынесенные за текущий scope.

## Gates

- `1.backlog -> 2.todo`: scope истории принят к проработке.
- `2.todo -> 3.inprogress`: ordered change plan и OpenSpec artifacts готовы.
- `3.inprogress -> 4.done`: planned changes реализованы, проверены и
  зафиксированы в карточке.
- `* -> 5.canceled`: принято явное решение не продолжать.

## Card Rules

- Одна задача = один markdown-файл.
- Имя файла должно быть sortable и уникальным.
- Новые карточки используют kebab-case slug, при необходимости с числовым
  префиксом.
- В `2.todo/` и `3.inprogress/` карточка должна содержать ordered sections
  `## Change 1:`, `## Change 2:` и так далее.
- В `Related` указываются только публичные пути внутри OPSX или generic
  example-пути.

## Agent Workflow

1. Создать или уточнить карточку в `1.backlog/`.
2. После triage перенести карточку в `2.todo/` и описать ordered change plan.
3. Когда artifacts готовы, перенести карточку в `3.inprogress/`.
4. Реализовать changes через OPSX/OpenSpec flow.
5. Записать результат, проверки и archive paths.
6. После independent review и publish перенести карточку в `4.done/`.

Минимальный собственный OPSX surface уже начинается с `opsx-explore` и
`opsx-ff`. Пока delivery/review/publish skills не перенесены, реализация,
archive и publish выполняются прямыми правками с baseline verification из
`AGENTS.md` либо через явно доступный project-local workflow.
