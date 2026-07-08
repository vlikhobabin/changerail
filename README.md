# OPSX

OPSX - открытая технология организации разработки с AI-агентами:
OpenSpec-артефакты, доска задач, проверяемый delivery pipeline и общий
toolchain для Codex CLI и Claude Code.

Проект находится на ранней стадии выделения в самостоятельный открытый
репозиторий. Текущий фокус - аккуратно зафиксировать архитектуру, правила
публичного репозитория, будущий bootstrap нового проекта и план миграции
проектов-потребителей на единый OPSX source of truth.

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
/opt/app-a       /opt/app-b       /opt/service-c
```

## Текущий статус

На данный момент репозиторий содержит:

- публичную архитектурную запись;
- базовый `README.md`;
- `AGENTS.shared.md` с начальной общей методологией OPSX для AI-агентов;
- минимальную OpenSpec-доску для dogfooding развития самого OPSX;
- публично-безопасный `.gitignore`;
- лицензию MIT.

Планируемые следующие части:

- `skills/` с OPSX и OpenSpec lifecycle skills;
- `claude/commands/opsx/` с slash-командами;
- `bin/bootstrap-project`;
- `bin/verify-project`;
- `templates/project/`;
- drift/smoke-проверки.

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

Пока bootstrap еще не реализован, рекомендуемый способ установки для
экспериментов:

```bash
git clone https://github.com/vlikhobabin/opsx.git /opt/opsx
cd /opt/opsx
```

После появления bootstrap целевая команда будет выглядеть примерно так:

```bash
/opt/opsx/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

Затем:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

Интерфейс bootstrap пока проектируется и может измениться.

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

Ближайшие шаги:

1. Зафиксировать публичную архитектуру и правила репозитория.
2. Добавить `AGENTS.shared.md` и начать dogfooding через OpenSpec-доску.
3. Перенести минимальный набор OPSX skills и команд в generic-форме.
4. Реализовать `bootstrap-project`.
5. Реализовать `verify-project`.
6. Добавить smoke/drift-проверки.
7. Подготовить первый стабильный release.
