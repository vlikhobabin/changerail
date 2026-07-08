# OPSX

OPSX - открытая технология организации разработки с AI-агентами:
OpenSpec-артефакты, доска задач, проверяемый delivery pipeline и общий
toolchain для Codex CLI и Claude Code.

Проект находится на ранней стадии выделения в самостоятельный открытый
репозиторий. Текущий фокус - закрепить минимальный source of truth, затем
добавить bootstrap нового проекта, verify-project и drift gate для
проектов-потребителей.

## Зачем нужен OPSX

OPSX решает практическую проблему AI-assisted разработки: агент должен не
просто писать код, а работать в воспроизводимом процессе.

OPSX задает:

- единый workflow от идеи до публикации;
- OpenSpec-артефакты для требований, дизайна, задач и проверок;
- board-процесс для карточек и изменений;
- независимый review gate перед публикацией;
- единый набор agent skills и команд для разных проектов;
- bootstrap нового проекта без ручного копирования десятков файлов;
- drift-проверки, чтобы проекты не расходились с source of truth.

## Базовый pipeline

Целевая форма OPSX pipeline:

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
- `pub` - проверить verdict, обновить документацию, сделать scoped commit и
  опубликовать результат.
- `deliver` - выполнить полный supervised flow для одной карточки или пачки
  карточек.

Для Codex целевой интерфейс - skills вида `$opsx-*`.
Для Claude Code целевой интерфейс - slash-команды вида `/opsx:*`.

## Source of truth

OPSX проектируется как отдельный системный source of truth:

```text
/opt/opsx
```

Проекты-потребители не копируют OPSX целиком. Они подключают общие skills,
команды и helpers через symlink-и или generated wiring, а проектные файлы
получают через bootstrap.

Упрощенная модель:

```text
                 +-----------+
                 | /opt/opsx |
                 +-----+-----+
                       |
          symlinks + generated config
                       |
      +----------------+----------------+
      |                |                |
      v                v                v
/opt/example-a   /opt/example-b   /opt/example-project
```

## Текущий статус

На данный момент репозиторий содержит:

- публичную архитектурную запись;
- базовый `README.md`;
- `AGENTS.shared.md` с начальной общей методологией OPSX для AI-агентов;
- минимальную OpenSpec-доску для dogfooding развития самого OPSX;
- generic OPSX lifecycle skills: `opsx-explore`, `opsx-ff`, `opsx-do`,
  `opsx-review`, `opsx-pub`, `opsx-deliver`;
- OpenSpec lifecycle skills `openspec-*` для proposal/spec/tasks, apply,
  verify, sync и archive;
- Claude wrappers `/opsx:explore`, `/opsx:ff`, `/opsx:do`, `/opsx:review`,
  `/opsx:pub`, `/opsx:deliver`;
- `bin/openspec` с pin версии OpenSpec CLI;
- schemas `opsx.review-verdict.v1`, `opsx.delivery-manifest.v1`,
  `opsx.evidence-index.v1` и helper `bin/opsx-review-verdict`;
- `templates/project/` для generated project files и OpenSpec skeleton;
- `bin/verify-project` как red/green gate для consumer wiring/config;
- `bin/bootstrap-project` для создания generic consumer project;
- `scripts/smoke-drift.py` как workspace-level drift gate с JSON report;
- публично-безопасный `.gitignore`;
- лицензию MIT.

Планируемые следующие части:

- миграция и adoption flow для существующих/новых consumer projects;
- release discipline: semver, changelog, compatibility notes и CI.

## Планируемая структура

```text
opsx/
├── README.md
├── LICENSE
├── AGENTS.shared.md
├── docs/
├── skills/
├── claude/
│   └── commands/
│       └── opsx/
├── schemas/
├── bin/
├── templates/
│   └── project/
└── scripts/
```

## Быстрый старт

Установите OPSX source of truth:

```bash
git clone https://github.com/vlikhobabin/opsx.git /opt/opsx
cd /opt/opsx
```

Создайте generic consumer project:

```bash
/opt/opsx/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

После генерации bootstrap запускает тот же verifier.

Повторная проверка:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

Проверка drift по workspace inventory:

```bash
python3 /opt/opsx/scripts/smoke-drift.py \
  --config /opt/opsx/internal/opsx-drift.json
```

Файл inventory держите в ignored `internal/` или генерируйте в CI. Он может
содержать `workspace_roots`, `projects`, `exclude` и `legacy_roots`; публичные
документы OPSX используют только generic examples.

## Для пользователей

Если вы хотите применять OPSX в своем проекте, ориентируйтесь на следующие
принципы:

- проект остается самостоятельным git-репозиторием;
- OpenSpec, board, исходный код и проектные правила живут в проекте;
- общая методология, skills и команды живут в OPSX;
- runtime-состояние агентов не коммитится;
- публикация изменений должна быть scoped и проверяемой;
- review gate выполняется отдельным контекстом, а не той же сессией, которая
  делала реализацию.

## Для AI-агентов

Если вы работаете внутри этого репозитория как AI-агент:

- считайте этот репозиторий публичным по умолчанию;
- не добавляйте сведения о локальных рабочих проектах, customer data, токенах,
  ключах, runtime traces или machine-local путях;
- используйте generic-примеры вроде `/opt/opsx` и `/opt/example-project`;
- не коммитьте `.runtime/`, `.artifacts/`, `.ai/`, `.codex/`, локальные
  `.env` или agent session state;
- в документации отделяйте универсальную OPSX-методологию от
  domain-specific extensions;
- при изменении будущих templates проверяйте, что generated config не содержит
  локальных абсолютных путей кроме явно документированных placeholders.

## Документация

Основной документ текущего этапа:

- [OPSX как единый source of truth разработки](docs/opsx-source-of-truth-architecture.md)
- [OpenSpec lifecycle source](docs/openspec-lifecycle.md)
- [OPSX contracts](docs/opsx-contracts.md)

## Безопасность публичного репозитория

В репозиторий не должны попадать:

- секреты, токены, ключи, `.env`;
- runtime-состояние Codex, Claude или других агентских инструментов;
- трассы, дампы, логи, базы данных, отчеты с чувствительными данными;
- реальные customer/workspace данные;
- упоминания локальных рабочих репозиториев, если они не являются частью
  публичной документации OPSX.

`.gitignore` настроен консервативно, но он не заменяет review перед commit.

## Лицензия

OPSX распространяется по лицензии MIT. См. [LICENSE](LICENSE).

## Roadmap

Текущая точка: Фазы 1-3 реализованы в рабочем дереве: generic lifecycle
skills, OpenSpec lifecycle skills, wrapper `bin/openspec`, schemas,
review-verdict helper, project templates, `bin/verify-project`,
`bin/bootstrap-project` и `scripts/smoke-drift.py` присутствуют. Миграция
потребителей еще впереди.

Ближайшие шаги:

1. Переключить существующие legacy consumers на `/opt/opsx`.
2. Подключить новые проекты через adoption/bootstrap flow.
3. Подготовить первый стабильный release: semver, changelog, compatibility
   notes и CI.
