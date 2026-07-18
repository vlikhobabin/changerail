# Как это работает

Этот документ описывает модель работы ChangeRail — чтобы понять, как устроен процесс,
ещё до подключения ChangeRail к своему проекту. Полные agent-инструкции — в
[`AGENTS.shared.md`](../AGENTS.shared.md); здесь человеко-читаемый обзор.

## Два слоя: source of truth и проект-потребитель

ChangeRail живёт отдельно (contract path `/opt/changerail`) и хранит переиспользуемое:
методологию, agent-skills, команды и helper-ы. Проект-потребитель остаётся
самостоятельным git-репозиторием: он подключает общие части symlink-ами, а свои
файлы — код, доску, OpenSpec-артефакты, проектные правила — держит у себя.
Обновление `/opt/changerail` сразу доступно всем потребителям: один источник вместо
копий в каждом проекте.

## Доска и жизненный цикл карточки

Работа организована доской в `openspec/board/` проекта. Пять папок — это стадии:

| Папка | Что внутри |
| --- | --- |
| `1.backlog/` | неразобранные идеи и проблемы |
| `2.todo/` | принятые истории с планом изменений |
| `3.inprogress/` | истории в активной работе |
| `4.done/` | завершённые истории с результатом и verification |
| `5.canceled/` | закрытые без реализации или вынесенные за scope |

Одна карточка = один markdown-файл по
[шаблону](../templates/project/openspec/board/card-template.md): поля `Status`,
`Summary`, `Acceptance` (observable outcomes), `Verify`, `Result`, `Log` и др.
Карточка перемещается между папками по мере продвижения работы.

Для review-gated delivery важно различать завершенный change payload и
завершенную story. `changerail-do` реализует, проверяет, синхронизирует specs и
архивирует card-owned changes, но оставляет карточку в `3.inprogress`.
Independent review проверяет именно этот полный payload. `changerail-pub` после
свежего `go` публикует payload без содержательных edits и только затем
финализирует карточку в `4.done` детерминированной board metadata.

## Карточка = 2–5 apply-ready changes

Принятая карточка (`2.todo`/`3.inprogress`) несёт упорядоченные секции:

```md
## Change 1: `change-slug`
## Change 2: `another-change-slug`
```

Крупная история дробится на небольшие implementation-sized changes — **обычно
2–5 на карточку**. Так каждый change обозрим, независимо проверяем и имеет
чёткие границы. Каждый change живёт в `openspec/changes/<change-slug>/` со
своими OpenSpec-артефактами (`proposal.md`, `specs/**/spec.md`, при
необходимости `design.md`, `tasks.md`).

## Пайплайн: explore → ff → do → review → pub

| Стадия | Что делает |
| --- | --- |
| `explore` | исследовать идею/проблему/архитектуру до реализации (ничего не меняет) |
| `ff` | превратить карточку в упорядоченные apply-ready changes (планирует, не кодит) |
| `do` | реализовать каждый change по одному, проверить, синхронизировать specs |
| `review` | независимый аудит свежим контекстом → go/no-go verdict |
| `pub` | проверить verdict/docs, scoped commit, публикация |
| `deliver` | supervised full-flow для одной карточки или упорядоченной очереди |

Для ежедневной работы это skills `$chrl-*` в Codex и команды `/chrl:*` в Claude
Code. Длинные `$changerail-*` и `/changerail:*` остаются canonical/reference
names для contracts, docs и troubleshooting.

Durable docs/source edits должны быть частью reviewed payload до `go`. Если
после `go` требуется содержательное изменение, verdict считается stale и
нужен повторный review. Post-publish допускает только документированную
финализацию карточки, например commit/push metadata и move в `4.done`.

## Verification floor и evidence

ChangeRail не навязывает каждому проекту одинаковую toolchain-matrix. Обязательный
floor объявляется локальными правилами и artifacts: `AGENTS.md`,
`openspec/config.yaml`, `tasks.md`, `design.md` и затронутым toolchain.
Delivery выполняет эти команды или останавливается с blocker. Если formatter,
strict typing или отдельная environment matrix не объявлены, generic workflow
не делает их обязательными автоматически.

Evidence записывается как command + observed outcome. Raw logs остаются в
ignored runtime state, а карточка, tasks или manifest содержат воспроизводимое
резюме и путь к evidence, если он нужен. Для измененных тестов delivery
фиксирует, почему тест наблюдает нужное поведение и способен упасть при
регрессе; для docs/config-only changes можно явно указать, что RED evidence
неприменима.

Для card-level handoff manifest можно строить helper-ом:

```bash
python3 scripts/changerail_delivery_manifest.py derive \
  openspec/board/3.inprogress/example.md --write --json
```

`staging-plan` по manifest дает reviewable список путей для scoped publish, но
publish все равно повторно сверяет scope с `git status`.

Перед публичным commit используйте единый scanner вместо ad hoc regex:

```bash
python3 scripts/public-surface-scan.py
```

Default mode scans the tracked public surface including `openspec/changes/archive`,
so archived OpenSpec artifacts are checked together with docs, skills, scripts,
templates and board/spec files.

## Non-interactive runner и status

Для длительных supervised запусков ChangeRail предоставляет tracked helper
`bin/changerail-delivery-runner`. Это single-card launcher: он запускает
`$changerail-deliver <card>` через repo-scoped `bin/codex`, закрывает stdin
child-процесса и пишет
`.runtime/changerail/delivery-runs/<run-id>/status.json` с contract
`changerail.delivery-run.v1`. Supervisor наблюдает этот status record, а не `pgrep`
или свободный текст лога.

Для dependency-ordered очередей через несколько независимых workspaces runner
поддерживает отдельный JSON plan contract и plan-oriented команды:

```bash
bin/changerail-delivery-runner plan delivery-plan.json --consumer-root /opt/example-workspace --json
bin/changerail-delivery-runner preflight-plan delivery-plan.json --consumer-root /opt/example-workspace --json
bin/changerail-delivery-runner run-plan delivery-plan.json --consumer-root /opt/example-workspace
bin/changerail-delivery-runner resume-plan delivery-plan.json --consumer-root /opt/example-workspace \
  --status-path /opt/example-workspace/.runtime/changerail/delivery-plans/<run-id>/status.json
bin/changerail-delivery-runner status-plan \
  /opt/example-workspace/.runtime/changerail/delivery-plans/<run-id>/status.json --json
```

Plan-файл использует `changerail.delivery-plan.v1`: workspace aliases,
consumer-root-relative paths, card ids, dependencies, waves и concurrency
limits. `plan`/`preflight-plan` полностью проверяют workspaces, git/card state,
dependencies, waves и single-card runner readiness до первого live child.
Aggregate status пишется под
`.runtime/changerail/delivery-plans/<run-id>/status.json` с
`changerail.delivery-plan-status.v1`; каждый live card по-прежнему запускает
single-card `run` и сохраняет отдельный `changerail.delivery-run.v1` record.

Workspace lock-и под ignored runtime state исключают два live child run в одном
repository. Stale lock не удаляется автоматически: runner пишет structured
diagnostic и ждет явного operator action. Queue fail-fast останавливает новые
downstream cards на `NO-GO`, `BLOCKED`, stale/invalid verdict, push rejection,
unexpected dirty scope или inconsistent card state. В push-enabled mode card
success требует card в `4.done`, clean repository и `HEAD == upstream`; при
`--no-push` требуется clean committed tree и recorded ahead/upstream state.

Для workspace-агрегаторов с несколькими независимыми дочерними git-репозиториями
default-модель - запускать runner в каждом дочернем репозитории через
`--workspace <child-repo>`. Такие child-repo deliveries могут идти параллельно,
потому что у них разные git scopes, доски и runtime status. Внутри одного
репозитория карточки остаются последовательными, а root-level integration
обновления выполняются отдельным сериализованным gate.

Per-run model и reasoning effort передаются штатными Codex CLI overrides и не
меняют repository defaults:

```bash
bin/changerail-delivery-runner run openspec/board/3.inprogress/example.md \
  --model gpt-5 --reasoning-effort medium
```

Если `--workspace` не указан, runner берет git-root текущего invocation cwd,
а вне git - сам cwd. `--workspace` задает реальный child cwd и
`CODEX_WORKDIR`; если `CODEX_HOME` не задан оператором, runner использует
`<workspace>/.codex`, а не path ChangeRail source of truth. Если `--runtime-root` не
указан, status и logs пишутся под
`<workspace>/.runtime/changerail/delivery-runs/`. Перед background-run используйте
preflight: он проверяет launcher, эффективный `CODEX_HOME`, `config.toml`,
auth state без чтения секретов, stale symlink-и внутри `CODEX_HOME`,
executable permissions, наличие Codex binary и, если указан URL, делает
реальную connectivity-проверку proxy/endpoint. Диагностика читается из status
JSON; runtime logs остаются ignored state. Если status показывает
`CODEX auth: fail`, обновите auth в проектном `CODEX_HOME` или задайте
поддерживаемую auth env переменную; если `CODEX_HOME symlinks: fail`,
пересоздайте устаревшие symlink-и до запуска.

## Fix budget до review

`changerail-do --max-fix-cycles` (default `2`) ограничивает pre-review
implement/verify attempts. Это другой budget, чем
`changerail-deliver --max-review-cycles` (default `5`), который считает
same-card rescue/re-review после independent `NO-GO`.

Если fix budget исчерпан, worker не просит ручное увеличение counter как
default path и не выдает stop за review verdict. Он возвращает
`terminal_outcome: BLOCKED` вместе с
`terminal_reason: fix_budget_exhausted`, remaining findings, attempted fixes и
verification target. Оркестратор классифицирует продолжение:

- bounded same-card micro-fix — только тот же capability, acceptance scope,
  authority и одна конкретная verification target;
- linked rescue/replacement card — новый deliverable, расширение acceptance
  scope или отдельный independently reviewable risk; карточка получает lineage
  и ставится перед blocked downstream work;
- `BLOCKED`/`NOT-VERIFIABLE` — external authority, credentials,
  infrastructure или condition, которую implementation не может устранить.

Неуспешный bounded micro-fix не открывает бесконечный loop: lifecycle
останавливается или материализует отдельный scope карточкой.

## No-go rescue loop и метрики

Типовой operational flow:

```text
over-claim -> no-go -> scoped rescue -> re-review -> go -> pub
```

Если review находит over-claim, missing evidence или out-of-scope файл,
reviewer пишет `no-go` с blocker finding. Implementing session исправляет
только scoped blocker, обновляет evidence и снова передает карточку на свежий
review. Дефолтный autonomous `deliver` допускает пять bounded same-card
rescue-подходов после первого `no-go`; каждый из них требует fresh independent
re-review. Когда re-review возвращает `go`, publish может продолжать.
Предыдущий `no-go` сохраняется в review-cycle history, а latest canonical
verdict остается совместимым с publish freshness gate.

Если same-card budget исчерпан и review снова возвращает `no-go`, агент не
публикует dirty payload и не self-authorizes следующий same-card rescue.
Автономный путь - создать linked rescue/replacement карточку, перенести в нее
source card, latest safe published reference, prior findings, rescue attempts,
evidence summaries, текущую гипотезу и required verification floor, затем
поставить эту карточку перед blocked downstream work. Если две linked
replacement/rescue карточки подряд возвращают тот же blocker class или
unresolved invariant, следующая карточка должна быть investigation/design.
External blockers и цели, которые больше нельзя воспроизвести или проверить,
фиксируются как `BLOCKED`, `SUPERSEDED` или `NOT-VERIFIABLE` с concrete
evidence.

`bin/changerail-delivery-metrics` читает `.runtime/changerail/delivery-runs/*/status.json`
и `.runtime/changerail/reviews/*.history.json`, чтобы показать first-pass go rate,
findings по severity, acceptance outcomes, wall-time и доступный token usage.
CSV mode предназначен для внешней аналитики; отсутствующие optional поля
отображаются как `unknown`.

## Supervised-модель: оркестратор, воркер и независимый review

Ключевой принцип: **контекст, который планировал и реализовывал изменение,
недостаточно независим для финального quality gate.** Поэтому ChangeRail разводит роли
по сессиям.

```text
                  ┌──────── no-go: fix-директива ────────┐
                  ▼                                       │
  card ─▶ ff ─▶ do ─────────▶ review ──── go ──▶ pub
                 │                │
             (воркер)     (свежий, независимый
          реализует         контекст) → go/no-go
          changes,          verdict
          пишет evidence
```

- **Оркестратор** — supervised-сессия, которая ведёт карточку по пайплайну и
  принимает решения на стыках стадий.
- **Воркер** — реализует запланированные changes (`do`) и фиксирует evidence.
  На мелких задачах оркестратор и воркер могут быть одной сессией; на крупных
  оркестратор делегирует реализацию отдельной сессии.
- **Review** — **обязательно отдельный, свежий контекст**, а не та сессия, что
  реализовывала. Она аудитит diff против карточки и OpenSpec-scope, покрытие
  acceptance, evidence и public-safety-риски, и выдаёт машинно-проверяемый
  **go/no-go verdict** (контракт `changerail.review-verdict.v1`) с
  `reviewer.independence` attestation.
- **Возврат к оркестратору**: verdict возвращается оркестратору. `go` →
  оркестратор запускает `pub`. `no-go` → оркестратор передаёт воркеру
  fix-директиву, и цикл `do → review` повторяется в пределах same-card budget.
  После исчерпания budget оркестратор переводит работу в linked replacement
  или investigation card.

Publish работает **fail-closed**: без валидного свежего `go`-вердикта публикация
не происходит.

После успешного payload commit `changerail-pub` может использовать helper для
детерминированной board finalization: move `3.inprogress -> 4.done`, обновление
`Result`/`Log`/`Next` и card-only amend. Такие edits являются metadata, а не
содержательным изменением reviewed payload.

## Что делает пользователь

1. Подключить проект: `bin/bootstrap-project` (или adopt существующего
   потребителя).
2. Проверить сцепку: `bin/verify-project` — red/green gate.
3. Завести карточку на доске и вести её через `$chrl-*` / `/chrl:*`; для
   reference/debugging использовать canonical `$changerail-*` / `/changerail:*`.
4. Публиковать только scoped и только после `go`-вердикта.

## Дальше

- [Общая методология ChangeRail для агентов](../AGENTS.shared.md)
- [Гайд по доскам и двум агентам при разработке фичи](board-and-two-agent-feature-flow.md)
- [ChangeRail contracts](changerail-contracts.md) — схемы verdict/manifest/evidence
- [Архитектура: единый source of truth](changerail-source-of-truth-architecture.md)
