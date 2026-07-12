# ChangeRail

ChangeRail - открытая технология организации разработки с AI-агентами:
OpenSpec-артефакты, доска задач, проверяемый delivery pipeline и общий
toolchain для Codex CLI и Claude Code.

Минимальный public source of truth, bootstrap/verification, drift gate,
migration/adoption и release discipline уже реализованы. Текущий фокус -
укрепить delivery pipeline для повторяемой эксплуатации и подготовить stable
release на основе практического feedback.

## Зачем нужен ChangeRail

ChangeRail решает практическую проблему AI-assisted разработки: агент должен не
просто писать код, а работать в воспроизводимом процессе.

ChangeRail задает:

- единый workflow от идеи до публикации;
- OpenSpec-артефакты для требований, дизайна, задач и проверок;
- board-процесс для карточек и изменений;
- независимый review gate перед публикацией;
- единый набор agent skills и команд для разных проектов;
- bootstrap нового проекта без ручного копирования десятков файлов;
- drift-проверки, чтобы проекты не расходились с source of truth.

## Базовый pipeline

Целевая форма ChangeRail pipeline:

```text
explore -> ff -> do -> review -> pub
```

Команды:

- `explore` - исследовать идею, проблему или архитектурный выбор без
  реализации.
- `ff` - превратить карточку в apply-ready OpenSpec changes.
- `do` - реализовать changes, проверить их, синхронизировать specs и
  подготовить результат.
- `review` - выполнить независимый fresh-context аудит перед публикацией.
- `pub` - проверить verdict и docs в reviewed payload, сделать scoped commit и
  опубликовать результат.
- `deliver` - выполнить полный supervised flow для одной карточки или пачки
  карточек.

Для ежедневной работы рекомендуются короткие aliases: Codex skills
`$chrl-*` и Claude slash-команды `/chrl:*`. Canonical/reference форма остается
длинной: `$changerail-*` и `/changerail:*`.

## Source of truth

ChangeRail проектируется как отдельный системный source of truth:

```text
/opt/changerail
```

Проекты-потребители не копируют ChangeRail целиком. Они подключают общие skills,
команды и helpers через symlink-и или generated wiring, а проектные файлы
получают через bootstrap.

Упрощенная модель:

```text
                 +-----------+
                 | /opt/changerail |
                 +-----+-----+
                       |
          symlinks + generated config
                       |
      +----------------+----------------+
      |                |                |
      v                v                v
/opt/example-a   /opt/example-b   /opt/example-project
```

## Как это работает

Работа идёт через доску карточек в проекте (`openspec/board/`):
`1.backlog -> 2.todo -> 3.inprogress -> 4.done -> 5.canceled`. Одна карточка =
один markdown-файл; принятая карточка дробится на **2–5 небольших apply-ready
changes**, каждый со своими OpenSpec-артефактами в `openspec/changes/<slug>/`.

Карточка проходит пайплайн `explore -> ff -> do -> review -> pub`. Роли
разведены по сессиям: **оркестратор** ведёт карточку по стадиям, **воркер**
реализует changes, а **review — обязательно отдельный свежий контекст** (не та
сессия, что писала код). Review выдаёт машинно-проверяемый **go/no-go verdict**,
который возвращается оркестратору: `go` -> `pub`, `no-go` -> fix-директива
воркеру и новый цикл. Publish работает fail-closed — без свежего `go`-вердикта
публикации нет.

Подробный разбор с диаграммой — в [Как это работает](docs/how-it-works.md).

## Текущий статус

На данный момент репозиторий содержит:

- публичную архитектурную запись;
- базовый `README.md`;
- `AGENTS.shared.md` с начальной общей методологией ChangeRail для AI-агентов;
- минимальную OpenSpec-доску для dogfooding развития самого ChangeRail;
- generic ChangeRail lifecycle skills: `changerail-explore`, `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub`, `changerail-deliver` и short aliases
  `chrl-explore`, `chrl-ff`, `chrl-do`, `chrl-review`, `chrl-pub`,
  `chrl-deliver`;
- OpenSpec lifecycle skills `openspec-*` для proposal/spec/tasks, apply,
  verify, sync и archive;
- Claude wrappers `/changerail:explore`, `/changerail:ff`, `/changerail:do`, `/changerail:review`,
  `/changerail:pub`, `/changerail:deliver` и daily aliases
  `/chrl:explore`, `/chrl:ff`, `/chrl:do`, `/chrl:review`, `/chrl:pub`,
  `/chrl:deliver`;
- `bin/openspec` с pin версии OpenSpec CLI;
- schemas `changerail.review-verdict.v1`, `changerail.delivery-manifest.v1`,
  `changerail.evidence-index.v1` и helper `bin/changerail-review-verdict`;
- `templates/project/` для generated project files и OpenSpec skeleton;
- `bin/verify-project` как red/green gate для consumer wiring/config;
- `bin/bootstrap-project` для создания generic consumer project;
- `scripts/smoke-drift.py` как workspace-level drift gate с JSON report;
- `VERSION`, `CHANGELOG.md`, compatibility notes и migration guide для
  release discipline;
- `.github/workflows/changerail-ci.yml` и `scripts/smoke-release-ci.py` для
  release CI gate;
- публично-безопасный `.gitignore`;
- лицензию MIT.

Следующие направления:

- однозначный lifecycle delivery/review/pub и полный publish scope;
- generic runner operations, структурированный runtime status и метрики;
- первый stable release после проверки operational hardening на consumer
  projects.

## Структура репозитория

```text
changerail/
├── README.md
├── LICENSE
├── AGENTS.shared.md
├── docs/
├── skills/
├── claude/
│   └── commands/
│       └── changerail/
├── schemas/
├── bin/
├── templates/
│   └── project/
└── scripts/
```

## Быстрый старт

Установите ChangeRail source of truth:

```bash
git clone https://github.com/vlikhobabin/changerail.git /opt/changerail
cd /opt/changerail
```

Создайте generic consumer project:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

После генерации bootstrap запускает тот же verifier.
По умолчанию bootstrap рендерит portable tracked config: project scope в
`.mcp.json` и `.codex/config.toml` хранится как `.` вместо machine-local
absolute path. Если оператору нужен локальный absolute-path config, используйте
`--config-mode local`; bootstrap напечатает warning перед предложенным
`git add`.

Повторная проверка:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

Для подключения существующего проекта используйте отдельный
[runbook adoption](docs/consumer-adoption-runbook.md). Не запускайте
`bootstrap-project` поверх непустого проекта без отдельного решения.

Проверка drift по workspace inventory:

```bash
python3 /opt/changerail/scripts/smoke-drift.py \
  --config /opt/changerail/internal/changerail-drift.json
```

Файл inventory держите в ignored `internal/` или генерируйте в CI. Он может
содержать `workspace_roots`, `projects`, `exclude` и `legacy_roots`; публичные
документы ChangeRail используют только generic examples.

## Для пользователей

Если вы хотите применять ChangeRail в своем проекте, ориентируйтесь на следующие
принципы:

- проект остается самостоятельным git-репозиторием;
- OpenSpec, board, исходный код и проектные правила живут в проекте;
- общая методология, skills и команды живут в ChangeRail;
- runtime-состояние агентов не коммитится;
- публикация изменений должна быть scoped и проверяемой;
- review gate выполняется отдельным контекстом, а не той же сессией, которая
  делала реализацию.

## Для AI-агентов

Если вы работаете внутри этого репозитория как AI-агент:

- считайте этот репозиторий публичным по умолчанию;
- не добавляйте сведения о локальных рабочих проектах, customer data, токенах,
  ключах, runtime traces или machine-local путях;
- используйте generic-примеры вроде `/opt/changerail` и `/opt/example-project`;
- не коммитьте `.runtime/`, `.artifacts/`, `.ai/`, `.codex/`, локальные
  `.env` или agent session state;
- в документации отделяйте универсальную ChangeRail-методологию от
  domain-specific extensions;
- при изменении будущих templates проверяйте, что generated config не содержит
  локальных абсолютных путей кроме явно документированных placeholders.

## Документация

Основные документы:

- [Как это работает](docs/how-it-works.md)
- [Гайд по доскам и двум агентам при разработке фичи](docs/board-and-two-agent-feature-flow.md)
- [Runbook подключения существующего проекта](docs/consumer-adoption-runbook.md)
- [ChangeRail как единый source of truth разработки](docs/changerail-source-of-truth-architecture.md)
- [OpenSpec lifecycle source](docs/openspec-lifecycle.md)
- [ChangeRail contracts](docs/changerail-contracts.md)
- [Release discipline](docs/release-discipline.md)
- [Compatibility notes](docs/compatibility.md)
- [Migration guide](docs/migration-guide.md)
- [Security policy](SECURITY.md)

## Безопасность публичного репозитория

В репозиторий не должны попадать:

- секреты, токены, ключи, `.env`;
- runtime-состояние Codex, Claude или других агентских инструментов;
- трассы, дампы, логи, базы данных, отчеты с чувствительными данными;
- реальные customer/workspace данные;
- упоминания локальных рабочих репозиториев, если они не являются частью
  публичной документации ChangeRail.

`.gitignore` настроен консервативно, но он не заменяет review перед commit.

## Лицензия

ChangeRail распространяется по лицензии MIT. См. [LICENSE](LICENSE).

## Roadmap

Текущая точка: bootstrap-фазы 1-6 завершены. Репозиторий содержит generic
lifecycle и OpenSpec skills, contracts/helpers, bootstrap/templates,
verification и drift gates, release CI и документацию. Подтвержденные
consumer-проекты мигрированы или подключены через adoption flow; проекты вне
ChangeRail явно исключены из workspace drift inventory.

Ближайшие шаги:

1. Укрепить delivery lifecycle, verification floor и publish scope по активной
   board card `harden-delivery-operations`.
2. Добавить public-safe runner operations, structured status и delivery
   observability без зависимости от machine-local runtime.
3. Подготовить первый stable release после operational feedback и проверки
   compatibility на consumer projects.
