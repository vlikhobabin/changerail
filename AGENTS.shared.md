# Общая методология ChangeRail для агентов

Этот файл задает переиспользуемый workflow ChangeRail для AI-агентов и
сопровождающих. Проектно-специфичные правила остаются в `AGENTS.md` каждого
потребителя.

## Область

ChangeRail предоставляет общий процесс и toolchain для AI-assisted разработки:

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

Стандартный delivery pipeline ChangeRail:

```text
explore -> ff -> do -> review -> pub
```

- `explore`: исследовать идею, bug, архитектурный вопрос или требование до
  реализации.
- `ff`: превратить board card или story в ordered, apply-ready OpenSpec changes.
- `do`: реализовать каждый planned change, проверить его, синхронизировать specs
  и подготовить результат.
- `review`: выполнить независимый fresh-context аудит перед публикацией.
- `pub`: проверить fresh verdict, подтвердить docs в reviewed payload, создать
  scoped commit и опубликовать результат.
- `deliver`: выполнить supervised full flow для одной карточки или ordered batch.

Для ежедневного ручного invocation можно использовать короткие aliases
`$chrl-*` в Codex и `/chrl:*` в Claude Code. Canonical/reference names остаются
`$changerail-*` и `/changerail:*`; runtime paths, schema ids и OpenSpec
namespaces продолжают использовать `changerail`.

Для non-interactive supervised запусков ChangeRail может использовать tracked runner,
который пишет machine-readable status/run record в ignored runtime state.
Supervisor должен наблюдать structured status, а не `pgrep` или свободный
текст лога. Per-run model/effort overrides не должны менять repository defaults.

## Supervised Roles

ChangeRail различает операционные роли:

- Оркестратор ведет карточку или bounded queue через стадии, выбирает следующую
  карточку, следит за safety stops, читает verdict и решает, нужен ли fix,
  re-review или publish.
- Delivery worker реализует один card-owned change или одну карточку,
  выполняет verification, синхронизирует specs, архивирует changes и готовит
  evidence/manifest для review.
- Reviewer работает в fresh context, который не планировал и не реализовывал
  reviewed payload, аудитит scope/evidence/acceptance и пишет go/no-go verdict
  в ignored runtime state.

Для небольших single-card работ оркестратор и delivery worker могут быть одной
сессией. Reviewer не может быть совмещен с planning/implementation context. Если
fresh reviewer недоступен или не может правдиво подтвердить независимость,
pipeline останавливается на review gate до внешнего review.

Для очередей и roadmap-серий оркестратор обрабатывает карточки по одной,
останавливается на первом safety stop и периодически актуализирует оставшуюся
очередь с учетом уже опубликованных карточек.

Для workspace, где верхний каталог является агрегатором, а работа живет в
нескольких независимых дочерних git-репозиториях с собственными
`openspec/board/`, default operational unit - дочерний репозиторий. Оркестратор
может запускать delivery нескольких дочерних репозиториев параллельно, если
каждый run использует свой `--workspace`, свой runtime status и свой git scope.
Внутри одного репозитория карточки остаются последовательными. Root-level
integration commits, submodule/gitlink updates или общий manifest публикуются
отдельным сериализованным gate после завершения child-repo payloads.

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

Для review-gated карточек `changerail-do` завершает implementation payload:
реализует changes, выполняет verification, синхронизирует specs и архивирует
card-owned OpenSpec changes. Сама story при этом остается в `3.inprogress`,
пока independent review и publish не пройдут успешно. Переход в `4.done` -
детерминированная post-publish финализация, а не часть `do`.

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
- держит domain-specific work вне generic ChangeRail core, если он явно не входит в
  scope.

## Delivery

Во время `do` работайте с одним change за раз. Перед coding прочитайте
релевантный project context: `openspec/config.yaml`, `AGENTS.md`, board rules,
target card и change artifacts.

Обязательный verification floor собирается из project-declared sources:
`AGENTS.md`, `openspec/config.yaml`, `tasks.md`, `design.md` и затронутого
toolchain. Generic ChangeRail не делает formatter, strict typing или clean/ambient
environment matrix обязательными для всех проектов, если они не объявлены
локальными правилами или не следуют из измененного surface.

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

Архивация card-owned OpenSpec changes происходит до review: reviewer должен
видеть полный delivery payload, включая archive paths и synced specs. Любое
содержательное изменение code/docs/specs/schemas/scripts/tests после свежего
`go` делает verdict stale и требует re-review. Publish может записывать только
документированную детерминированную board metadata после commit/push.

Каждая verification claim должна называть выполненную команду и observed
outcome. Если raw output сохраняется, он остается в ignored runtime evidence, а
карточка или manifest ссылается на путь и краткое резюме. Для измененных тестов
delivery фиксирует, почему тест способен упасть при заявленном регрессе и
наблюдает нужный источник поведения. Для docs-only/config-only changes можно
записать, почему RED evidence неприменима.

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

Reviewer также проверяет, что обязательный project-declared verification floor
имеет concrete command/outcome evidence. Unbacked mandatory claims, weakened
tests и тесты, которые не наблюдают заявленное поведение, должны становиться
findings, а не молчаливым pass.

Review-cycle history сохраняется как ignored runtime evidence отдельно от
latest canonical verdict. Это позволяет видеть цепочку `no-go -> fix ->
re-review -> go` в метриках, не меняя fail-closed publish gate.

## Publish

Publishing scoped к завершенной карточке. Перед commit или push:

- проверьте `git status` и final diff;
- исключите runtime state, traces, logs, credentials и local reports;
- подтвердите, что OpenSpec validation и required project checks зеленые;
- подтвердите, что user-facing docs для измененного behavior или workflow уже
  входят в reviewed payload;
- commit only files, которые относятся к named card.

Commit и push выполняются только по явной просьбе operator или invoked publish
workflow.

Для review-gated flow durable docs и source edits должны входить в reviewed
payload до verdict. Если publish обнаруживает, что нужны содержательные edits,
он останавливается до staging и возвращает карточку в delivery/review loop.
После успешного publish карточка финализируется в `4.done` по board protocol.

## Evidence

Verification claims требуют evidence. Подходящие evidence: command output, test
reports, retained smoke artifacts, review verdicts и explicit manual checks,
записанные с достаточными деталями для воспроизведения вывода.

Ignored runtime evidence может упоминаться в cards или manifests, но не должно
попадать в commit. Не храните secrets, credentials, customer data, full source
payloads или large logs в tracked evidence.

Метрики должны читаться из structured run records и review-cycle evidence, а не
из свободного текста логов. Отсутствующие optional значения, например token
usage, отображаются явно как unknown.

## Public Safety

ChangeRail core публичен по умолчанию. Shared methodology и templates не должны
содержать:

- private workspace или customer names;
- secrets, tokens, keys или `.env` content;
- local traces, dumps, screenshots, databases или runtime reports;
- machine-local state вне documented generic examples;
- domain-specific extension rules, выданные за generic ChangeRail behavior.

Используйте generic examples: `/opt/changerail`, `/opt/example-project`,
`/opt/example-a`, `/opt/example-b`.

Public-surface verification should include the tracked scanner for current
files and, before release, reachable history:

```bash
python3 scripts/public-surface-scan.py
python3 scripts/public-surface-scan.py --history
```

Scanner findings for token-like assignments must redact secret values in logs.

## Generated Sections And Drift

Consumer projects могут встраивать эту shared methodology в локальный
`AGENTS.md` как generated section. Generated section должен содержать marker,
который позволит будущему `verify-project` сравнить его с ChangeRail source of truth.

Внешняя ссылка на `/opt/changerail/AGENTS.shared.md` полезна для людей, но embedded
generated content является default target для надежного agent context.

## Extension Boundary

ChangeRail generic core должен оставаться отдельно от domain-specific extensions.
Domain extension может добавить extra skills, commands, verification matrices
или runtime policies, но не должен делать generic ChangeRail зависимым от этого
domain.

Если consumer project использует и ChangeRail core, и extension, его project
`AGENTS.md` должен явно фиксировать ordering и ownership boundaries.
