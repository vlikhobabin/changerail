# ChangeRail Board

Файловая доска проекта для развития ChangeRail через собственный workflow.

Доска живет в `openspec/board/`, потому что карточки являются story-level
входом, а `openspec/changes/` содержит apply-ready OpenSpec changes для этих
историй.

## Layout

- `1.backlog/` - идеи, проблемы и предложения до triage.
- `2.todo/` - deliver-ready задачи: scope принят, owner известен, acceptance
  observable, ordered change plan записан.
- `3.inprogress/` - задачи с apply-ready change-set, взятые в работу.
- `4.done/` - завершенные задачи с зафиксированным результатом.
- `5.canceled/` - закрытые без реализации или вынесенные за текущий scope.
- `plans/` - tracked public-safe delivery plans для package runner; runtime
  statuses и locks остаются в ignored `.runtime/changerail/`.

## Gates

- `1.backlog -> 2.todo`: scope истории принят к проработке.
- `2.todo -> 3.inprogress`: ordered change plan и OpenSpec artifacts готовы.
- `3.inprogress -> 4.done`: risk-appropriate payload review дал fresh machine
  receipt или independent `go`, publish опубликовал scoped payload, и карточка
  финализирована post-publish metadata.
- `* -> 5.canceled`: принято явное решение не продолжать.

## Card Rules

- Одна задача = один markdown-файл.
- Имя файла должно быть sortable и уникальным.
- Новые карточки используют kebab-case slug, при необходимости с числовым
  префиксом.
- Для ordered series используется имя `<series>-<index>-<slug>.md`, например
  `010-03-fix-publish-finalization-ledger.md`.
- `Series` содержит stable series id, а `Series Index` - двухзначный порядок
  внутри серии. Индекс `00` зарезервирован для головной epic-карточки.
- Epic-карточка остается coordination-only в `1.backlog`, перечисляет общие
  constraints, состав, entry/exit/refresh gates и не является целью
  `$chrl-deliver`.
- Исполняемые story-карточки серии переходят по обычным board gates и
  выполняются по `Series Index`, если epic явно не разрешает иной порядок.
- Если следующая серия зависит от фактического результата предыдущей, ее epic
  и stories остаются provisional до обязательного refresh gate.
- Tracked plan серии создается только после readiness/refresh gate и содержит
  только executable story cards; coordination-only epic cards не включаются.
- В `2.todo/` и `3.inprogress/` карточка должна содержать ordered sections
  `## Change 1:`, `## Change 2:` и так далее.
- `deliver-ready` не является новой колонкой: это свойство карточки в
  `2.todo`. OpenSpec artifacts могут отсутствовать до запуска
  `$chrl-deliver`; internal `ff` phase создаст или дополнит их перед `do`.
- Если карточка еще не deliver-ready, diagnostic должен назвать missing scope,
  owner, acceptance, ordered plan, dependency или handoff criteria.
- В `Related` указываются только публичные пути внутри ChangeRail или generic
  example-пути.
- `Review` объявляет `deterministic|ordinary|critical` risk и complexity flags;
  legacy card без секции считается `ordinary`.

## Agent Workflow

1. Создать или уточнить карточку в `1.backlog/`.
2. После triage перенести карточку в `2.todo/`, назначить owner, описать
   observable acceptance, ordered change plan, dependencies и handoff через
   `$chrl-deliver <card>`.
3. Когда artifacts готовы, перенести карточку в `3.inprogress/`.
4. Реализовать changes через ChangeRail/OpenSpec flow, записать результат, проверки
   и archive paths, оставив review-gated карточку в `3.inprogress/`.
5. До model launch выполнить deterministic preflight. Для process-only payload
   принять `machine-reviewed`; для ordinary/critical провести один independent
   review и на `no-go` исправлять только scoped blocker.
6. После fresh machine receipt или `go` выполнить publish и перенести карточку в `4.done/` только
   как deterministic post-publish finalization.

Для series сначала прочитайте epic `00`, проверьте entry/refresh gate и только
затем запускайте следующую story. Coordination-only epic не входит в bounded
delivery queue.

Актуальный ChangeRail surface включает `changerail-explore`, `changerail-ff`,
`changerail-do`, `changerail-review`, `changerail-pub`, `changerail-deliver` и
короткие `$chrl-*` / `/chrl:*` aliases. Роли оркестратора, delivery worker и
fresh reviewer закреплены в `AGENTS.shared.md`; практический workflow описан в
`docs/board-and-two-agent-feature-flow.md`.
