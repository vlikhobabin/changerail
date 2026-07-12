# ChangeRail Board

Файловая доска проекта для развития ChangeRail через собственный workflow.

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
- `3.inprogress -> 4.done`: independent review вернул fresh `go`, publish
  опубликовал scoped payload, и карточка финализирована post-publish metadata.
- `* -> 5.canceled`: принято явное решение не продолжать.

## Card Rules

- Одна задача = один markdown-файл.
- Имя файла должно быть sortable и уникальным.
- Новые карточки используют kebab-case slug, при необходимости с числовым
  префиксом.
- В `2.todo/` и `3.inprogress/` карточка должна содержать ordered sections
  `## Change 1:`, `## Change 2:` и так далее.
- В `Related` указываются только публичные пути внутри ChangeRail или generic
  example-пути.

## Agent Workflow

1. Создать или уточнить карточку в `1.backlog/`.
2. После triage перенести карточку в `2.todo/` и описать ordered change plan.
3. Когда artifacts готовы, перенести карточку в `3.inprogress/`.
4. Реализовать changes через ChangeRail/OpenSpec flow, записать результат, проверки
   и archive paths, оставив review-gated карточку в `3.inprogress/`.
5. Провести independent review; на `no-go` исправлять только scoped blocker и
   запрашивать свежий review.
6. После fresh `go` выполнить publish и перенести карточку в `4.done/` только
   как deterministic post-publish finalization.

Минимальный собственный ChangeRail surface уже начинается с `changerail-explore` и
`changerail-ff`. Пока delivery/review/publish skills не перенесены, реализация,
archive и publish выполняются прямыми правками с baseline verification из
`AGENTS.md` либо через явно доступный project-local workflow.
