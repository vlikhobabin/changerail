# Общая методология OPSX для агентов

Этот файл задает переиспользуемый workflow OPSX для AI-агентов и
сопровождающих. Проектно-специфичные правила остаются в `AGENTS.md` каждого
потребителя.

## Область

OPSX предоставляет общий процесс и toolchain для AI-assisted разработки:

- OpenSpec-артефакты для proposal, requirements, design и tasks;
- файловые board-карточки для story-level планирования;
- переиспользуемые agent skills и command wrappers;
- независимые review gates перед публикацией;
- verification, evidence и drift-проверки;
- bootstrap-шаблоны для проектов-потребителей.

Проекты-потребители остаются отдельными git-репозиториями. Они владеют своим
исходным кодом, проектными правилами, локальной OpenSpec-доской, MCP scope,
runtime policy, secrets policy и domain-specific verification.

## Pipeline

Стандартный delivery pipeline OPSX:

```text
explore -> ff -> do -> review -> pub
```

- `explore`: исследовать идею, bug, архитектурный вопрос или требование до
  реализации.
- `ff`: превратить board card или story в ordered, apply-ready OpenSpec changes.
- `do`: реализовать каждый planned change, проверить его, синхронизировать specs
  и подготовить результат.
- `review`: выполнить независимый fresh-context аудит перед публикацией.
- `pub`: обновить docs, создать scoped commit и опубликовать результат.
- `deliver`: выполнить supervised full flow для одной карточки или ordered batch.

Не объединяйте `review` с `do`. Review gate нужен потому, что контекст, который
планировал и реализовывал изменение, недостаточно независим для финального
quality gate.

## Жизненный цикл доски

Проектная доска живет в `openspec/board/`:

- `1.backlog/`: неразобранные идеи и проблемы.
- `2.todo/`: принятые stories, которым нужен или уже задан change plan.
- `3.inprogress/`: apply-ready stories в работе.
- `4.done/`: завершенные stories с записанным результатом и verification.
- `5.canceled/`: work closed без реализации или вынесенный за scope.

Одна карточка = один markdown-файл. Карточка в `2.todo/` или `3.inprogress/`
должна содержать ordered sections:

```md
## Change 1: `change-slug`
## Change 2: `another-change-slug`
```

Каждая секция ссылается на свой каталог
`openspec/changes/<change-slug>/` и фиксирует, зачем нужен change, чего он
должен достичь, зависимости и verification expectations.

## Жизненный цикл OpenSpec

Каждый implementation-sized change живет в `openspec/changes/<change>/`.
Для default schema `spec-driven` используются:

- `proposal.md`: зачем нужен change и какие capabilities он затрагивает;
- `specs/**/spec.md`: normative requirements и scenarios;
- `design.md`: когда нужно явно зафиксировать implementation choices,
  trade-offs или migration concerns;
- `tasks.md`: trackable implementation и verification checkboxes.

Requirements используют `MUST` или `SHALL` и observable scenarios. Не
записывайте implementation details как requirements, если это не externally
observable behavior и не contract, который нужно сохранять в будущем.

## Explore

Используйте explore mode, когда problem, scope или architecture неясны. Explore
mode может читать code, docs, OpenSpec artifacts и локальные project
instructions, но не реализует product/runtime changes.

Хороший explore output фиксирует:

- что теперь понятно;
- viable options;
- risks и unknowns;
- recommended next artifact или command.

## Fast-Forward Planning

Fast-forward planning превращает board card в apply-ready changes. Хороший
результат `ff`:

- сохраняет one story = one card;
- делит implementation на небольшие ordered changes;
- создает нужные OpenSpec artifacts для каждого change;
- записывает dependencies и verification expectations;
- держит domain-specific work вне generic OPSX core, если он явно не входит в
  scope.

## Delivery

Во время `do` работайте с одним change за раз. Перед coding прочитайте
релевантный project context: `openspec/config.yaml`, `AGENTS.md`, board rules,
target card и change artifacts.

Implementation не завершена, пока verification не запущена и результат не
записан. Для docs/config-only changes обычный baseline:

```bash
openspec validate --all --strict
git diff --check
```

Если change добавляет новые untracked files, whitespace check должен покрывать
их явно: через staging/intent-to-add перед `git diff --check` или отдельный scan
по `git ls-files --others --exclude-standard`.

Project-specific tests или smoke checks также должны выполняться, если их
требуют local instructions, tasks или affected code.

## Review Gate

Review gate независим от implementation session. Он аудитит:

- diff versus card и OpenSpec scope;
- покрытие requirements и acceptance criteria;
- verification evidence и retained outputs;
- public-safety и repository-boundary risks;
- missing tests или residual risk.

Reviewer производит go/no-go verdict и не исправляет молча работу, которую
ревьюит. Publish должен fail closed, если verdict отсутствует, stale или
negative.

## Publish

Publishing scoped к завершенной карточке. Перед commit или push:

- проверьте `git status` и final diff;
- исключите runtime state, traces, logs, credentials и local reports;
- подтвердите, что OpenSpec validation и required project checks зеленые;
- обновите user-facing docs, если behavior или workflow изменился;
- commit only files, которые относятся к named card.

Commit и push выполняются только по явной просьбе operator или invoked publish
workflow.

## Evidence

Verification claims требуют evidence. Подходящие evidence: command output, test
reports, retained smoke artifacts, review verdicts и explicit manual checks,
записанные с достаточными деталями для воспроизведения вывода.

Ignored runtime evidence может упоминаться в cards или manifests, но не должно
попадать в commit. Не храните secrets, credentials, customer data, full source
payloads или large logs в tracked evidence.

## Public Safety

OPSX core публичен по умолчанию. Shared methodology и templates не должны
содержать:

- private workspace или customer names;
- secrets, tokens, keys или `.env` content;
- local traces, dumps, screenshots, databases или runtime reports;
- machine-local state вне documented generic examples;
- domain-specific extension rules, выданные за generic OPSX behavior.

Используйте generic examples: `/opt/opsx`, `/opt/example-project`,
`/opt/example-a`, `/opt/example-b`.

## Generated Sections And Drift

Consumer projects могут встраивать эту shared methodology в локальный
`AGENTS.md` как generated section. Generated section должен содержать marker,
который позволит будущему `verify-project` сравнить его с OPSX source of truth.

Внешняя ссылка на `/opt/opsx/AGENTS.shared.md` полезна для людей, но embedded
generated content является default target для надежного agent context.

## Extension Boundary

OPSX generic core должен оставаться отдельно от domain-specific extensions.
Domain extension может добавить extra skills, commands, verification matrices
или runtime policies, но не должен делать generic OPSX зависимым от этого
domain.

Если consumer project использует и OPSX core, и extension, его project
`AGENTS.md` должен явно фиксировать ordering и ownership boundaries.
