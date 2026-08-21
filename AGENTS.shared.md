# Общая методология ChangeRail для агентов

Этот файл задает компактный переиспользуемый contract ChangeRail. Проектные
правила, source code, verification matrix, MCP scope, secrets policy и runtime
policy принадлежат consumer-проекту и остаются в его локальном `AGENTS.md`.

Подробные phase algorithms и CLI options принадлежат соответствующим
`changerail-*` skills. Human workflow живет в `docs/`, wire/schema details — в
`docs/changerail-contracts.md` и `schemas/`. Этот файл фиксирует только
инварианты, которые должны быть доступны агенту во всех фазах.

## Область и ownership

ChangeRail предоставляет общий AI-assisted delivery workflow:

- OpenSpec artifacts для proposal, requirements, design и tasks;
- файловую board-модель для story-level planning;
- lifecycle skills и command wrappers;
- независимый review gate перед публикацией;
- verification, evidence, bootstrap и drift tooling.

Consumer-проекты остаются самостоятельными git-репозиториями. Generic
ChangeRail core не должен зависеть от domain-specific extensions, private
workspaces или consumer source trees.

## Pipeline и routing

Стандартный pipeline:

```text
explore -> ff -> do -> review -> pub
```

- `explore` исследует problem/scope/architecture без реализации.
- `ff` превращает story в ordered apply-ready OpenSpec changes.
- `do` реализует changes по одному, проверяет, sync-ит specs и архивирует их.
- `review` выполняет независимый fresh-context аудит и пишет go/no-go verdict.
- `pub` проверяет fresh verdict, делает scoped commit/push и финализирует card.
- `deliver` оркестрирует полный flow для одной карточки или bounded queue.

Обычный operator handoff — `$chrl-deliver <card>` или canonical
`$changerail-deliver <card>`. Phase-команды остаются repair/debug/manual-resume
surface. Когда доступен соответствующий lifecycle skill, он является
authoritative source для пошагового алгоритма и safety stops.
После standalone `ff` apply-ready handoff — `$changerail-do <card-path>`.

`$changerail-deliver <board-column>` упорядочивает queue по одной карточке, а
`bin/changerail-delivery-runner run <card>` является single-card structured-
status launcher. Для dependency plan доступны `plan`, `preflight-plan`,
`run-plan`, `resume-plan` и `status-plan`: plan runner вызывает single-card
runner для каждой live card, fail-fast останавливается на safety stop и
возобновляется через aggregate status. Records, logs и locks остаются в ignored
runtime state; supervisor читает structured status/manifest/verdict, а не
`pgrep`. Per-run model/effort overrides не меняют repository defaults.

## Роли и очереди

- Оркестратор выбирает следующую карточку, следит за safety stops и решает,
  нужен ли fix, re-review, publish или новый scope.
- Delivery worker реализует один card-owned change или одну карточку и готовит
  verification evidence/manifest.
- Reviewer работает в fresh context, который не планировал и не реализовывал
  reviewed payload.

Оркестратор и worker могут быть одной сессией только для небольшой single-card
работы; для delegated, multi-card или multi-repository delivery worker отделен
от supervising orchestrator. Reviewer с implementation context совмещать
нельзя. Если независимость нельзя правдиво подтвердить, pipeline
останавливается до внешнего review.

Внутри одного repository карточки выполняются последовательно и queue
останавливается на первом safety stop. Несколько независимых child repositories
могут выполняться параллельно только с разными `--workspace`, git scope,
runtime state и последующим отдельным root-level integration gate. Stale locks
не удаляются автоматически без явного operator action.

## Board contract

Board живет в `openspec/board/`:

- `1.backlog/` — идеи и проблемы до triage;
- `2.todo/` — принятые deliver-ready stories;
- `3.inprogress/` — apply-ready stories в implementation/review/publish;
- `4.done/` — опубликованные stories с результатом и verification;
- `5.canceled/` — work, закрытая без реализации или вынесенная за scope.

Одна карточка — один markdown-файл. Deliver-ready является свойством карточки
в `2.todo`, а не отдельным status: scope принят, owner указан, acceptance
observable, ordered `## Change N:` plan записан, dependencies указаны явно или
как `none`, а `Next` ведет к `$chrl-deliver <card>` либо canonical command.
OpenSpec artifacts не являются precondition: internal `ff` может создать их до
`do`. Diagnostic для неготовой карточки должен перечислить missing criteria.

Каждая `## Change N:` секция ссылается на отдельный implementation-sized
`openspec/changes/<slug>/` и фиксирует goal, dependencies и verification.
Review-gated `do` оставляет story в `3.inprogress`; переход в `4.done` является
только детерминированной post-publish финализацией.

## OpenSpec contract

Default `spec-driven` change содержит:

- `proposal.md` — зачем нужен change и какие capabilities затронуты;
- `specs/**/spec.md` — normative requirements и observable scenarios;
- `design.md` — implementation choices, trade-offs или migration concerns;
- `tasks.md` — trackable implementation и verification work.

Requirements используют `MUST`/`SHALL`. Implementation details становятся
requirements только когда это externally observable или durable contract.
Story и changes должны оставаться достаточно малыми для bounded implementation
и независимого review.

## Delivery, verification и evidence

Перед coding прочитайте `openspec/config.yaml`, local `AGENTS.md`, board rules,
target card, change artifacts и затронутый toolchain. Работайте с одним change
за раз. Discovery начинается со scoped paths/counts/excerpts; broad или
truncated output не считается доказательством отсутствия проблемы.

Обязательный verification floor собирается из local rules, config, tasks,
design и affected toolchain. Generic core не навязывает formatter, typing или
environment matrix, если они не объявлены проектом или измененным surface.

Для docs/config-only changes минимальный baseline обычно включает:

```bash
openspec validate --all --strict
git diff --check
```

Новые untracked files должны попадать в whitespace/public checks через
intent-to-add либо отдельный scan. Project-specific tests обязательны, когда их
требуют artifacts или affected code.

Каждая verification claim называет command и observed outcome. Для измененных
тестов delivery объясняет, какое поведение они наблюдают и почему тест падает
при заявленном regression; для docs-only work RED evidence можно явно признать
неприменимой. Raw output остается ignored, а tracked files ссылаются только на
concise evidence id/path. Предпочтительный ChangeRail-owned contract —
`bin/changerail-evidence` и `changerail.evidence-index.v1`.

Card-owned changes архивируются и specs синхронизируются до review. Любое
содержательное изменение code/docs/specs/schemas/scripts/tests после свежего
`go` делает verdict stale и требует re-review.

## Budgets, preflight и complexity

`changerail-do --max-fix-cycles` ограничивает pre-review implement/verify
attempts. `changerail-deliver --max-review-cycles` отдельно ограничивает
same-card rescue после independent `NO-GO`; counters не расходуют друг друга.
Defaults — два fix cycles и два semantic same-card rescue attempts.

`fix_budget_exhausted` является non-delivered `BLOCKED` handoff. Оркестратор
выбирает одну ветвь: bounded micro-fix в том же capability/scope/authority,
linked rescue/replacement card для отдельного deliverable либо external
`BLOCKED`/`NOT-VERIFIABLE` с evidence и resume condition. Ручное увеличение
budget не является default path.

До LLM review запускается deterministic preflight из lifecycle skill. Process
failure не расходует semantic review budget. Risk routing: `deterministic` —
machine-only, `ordinary` — `high`, credential/mutation/live/final boundary —
`critical`/`xhigh`.

Payload более 300 added production LOC, новая authority/wire protocol или
повторяющийся defect class требуют investigation/simplification. Bounded
exception возможен только через clean tracked `4.done` authorization source,
который связывает exact investigation/successor, ceiling `301..500` и protocol
allowance. Missing, stale, mismatched или over-ceiling authorization всегда
останавливает semantic review.

## Review gate

Reviewer независимо проверяет:

- diff против card/OpenSpec scope;
- requirements и acceptance coverage;
- обязательный verification floor и retained evidence;
- способность измененных tests наблюдать заявленное поведение;
- public-safety, repository boundary и residual risk.

Reviewer не исправляет reviewed payload и пишет machine-checkable verdict.
Unbacked mandatory claims, weakened tests и failed acceptance становятся
findings. Publish fail-closed при absent, stale или negative verdict.

Initial review — `review_cycle: 1`, `same_card_rescue_attempt: 0`. После
`no-go` implementing context исправляет только scoped blocker, обновляет
evidence и передает payload новому fresh reviewer. History сохраняет цепочку
cycles и structured rescue budget в ignored runtime state.

После исчерпания same-card budget dirty payload не публикуется. Создается
linked rescue/replacement card с source, latest safe reference, findings,
attempts, evidence summary и verification target. Повтор одного blocker class
в двух последовательных replacement cards требует investigation/design.
External credentials, network, licenses, stand access и невоспроизводимые цели
фиксируются как `BLOCKED`, `SUPERSEDED` или `NOT-VERIFIABLE`.

## Publish

Перед commit/push publish проверяет final diff/status, fresh positive verdict,
required checks, reviewed user-facing docs и manifest scope. Runtime state,
credentials, traces, local reports и unrelated dirty files исключаются.

Commit и push разрешены только явной просьбой operator или invoked publish
workflow. Если нужны содержательные edits, publish останавливается до staging и
возвращает payload в delivery/review loop.

После успешной публикации card перемещается в `4.done` только через
документированную deterministic metadata finalization. Exact commits,
remote/branch/status/timestamps остаются в ignored delivery manifest ledger, а
не в tracked card prose.

## Public safety

ChangeRail core и consumer templates считаются публичными по умолчанию. Нельзя
коммитить private workspace/customer names, secrets, tokens, keys, `.env`,
traces, dumps, screenshots, databases, runtime reports или machine-local state.
Используйте generic examples: `/opt/changerail`, `/opt/example-project`,
`/opt/example-a`, `/opt/example-b`.

Public-surface verification должна проверять current files, archives и перед
release reachable history. Token-like findings обязаны редактировать secret
values в output.

## Generated sections и extension boundary

Consumer `AGENTS.md` хранит project-specific rules перед generated ChangeRail
section. Marker позволяет tooling и reviewers отличать локальный contract от
shared source. Generated section обновляется из `AGENTS.shared.md`, а не
редактируется вручную; после ChangeRail upgrade consumers должны проверить
drift и instruction budget.

Внешняя ссылка на shared source полезна для людей, но компактный embedded
contract остается default для надежного agent context. Domain extensions могут
добавлять skills, checks и policies, но не делают generic core зависимым от
domain. Consumer явно фиксирует ordering и ownership boundaries между core и
extensions.
