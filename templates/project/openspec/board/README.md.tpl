# {{PROJECT_NAME}} Board

Файловая доска проекта живет в `openspec/board/`.

## Layout

- `1.backlog/` - идеи и проблемы до triage.
- `2.todo/` - deliver-ready задачи с принятым scope, owner, observable
  acceptance и ordered change plan.
- `3.inprogress/` - apply-ready stories в работе.
- `4.done/` - завершенные задачи с результатом и verification.
- `5.canceled/` - закрытые без реализации или вынесенные за scope.

## Rules

- Одна задача = один markdown-файл.
- В `2.todo/` и `3.inprogress/` карточка содержит sections
  `## Change 1:`, `## Change 2:` и так далее.
- `deliver-ready` - свойство карточки в `2.todo`, а не новая колонка. OpenSpec
  artifacts могут отсутствовать до `$chrl-deliver`; internal `ff` phase создаст
  или дополнит их перед `do`.
- Если readiness diagnostic используется, он должен назвать missing scope,
  owner, acceptance, ordered plan, dependency или handoff criteria.
- `Related` содержит project-local paths или generic public examples.
- `Review` объявляет `deterministic|ordinary|critical` risk и complexity flags;
  legacy card без секции считается `ordinary`.
- Domain-specific production source kinds can be declared in project-owned
  `.changerail/source-classification.yaml`; generated templates do not create
  application-specific production roots by default.
- Domain-specific verification coverage can be declared through
  `verification.coverage_map` and a tracked project-owned map; generated
  templates keep that reference `null` by default.
- Runtime evidence may be referenced, but raw runtime state stays ignored.

## Gates

- `1.backlog -> 2.todo`: scope истории принят к проработке.
- `2.todo -> 3.inprogress`: ordered change plan и OpenSpec artifacts готовы.
- `3.inprogress -> 4.done`: fresh machine receipt или independent `go` verdict
  получен, scoped publish завершен, и карточка финализирована post-publish metadata.
- `* -> 5.canceled`: принято явное решение не продолжать.

## Agent Workflow

ChangeRail workflow:

```text
explore -> ff -> do -> review -> pub
```

`deliver` выполняет supervised full flow для одной карточки или bounded queue,
но обрабатывает карточки по одной. Для принятой deliver-ready карточки normal
operator handoff - `$chrl-deliver <card>` или canonical
`$changerail-deliver <card>`; `ff/do/review/pub` остаются internal phases и
explicit repair/debug/manual-resume commands. `do` реализует, проверяет,
синхронизирует specs и архивирует changes, оставляя review-gated карточку в
`3.inprogress`. До model launch выполняется deterministic preflight; ordinary
и critical review должен быть fresh context, который не планировал и не
реализовывал payload. `pub` принимает fresh machine-only receipt для
deterministic payload либо fresh valid `go` verdict.

Практический guide по доскам и двум агентам находится в ChangeRail docs из
{{CHANGERAIL_ROOT_LABEL}}; reusable agent contract встроен в project `AGENTS.md`
из `{{CHANGERAIL_SHARED_SOURCE}}`.
