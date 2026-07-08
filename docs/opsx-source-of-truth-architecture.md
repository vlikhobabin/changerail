# OPSX как единый source of truth разработки

Статус: проектное решение, целевая архитектура.

Дата: 2026-07-08.

## 1. Контекст

OPSX выделяется в самостоятельную открытую технологию для организации
разработки с AI-агентами. Цель - дать проектам единый workflow:
OpenSpec-артефакты, board-процесс, skills/commands для агентов,
fresh-context review gate и проверяемую публикацию изменений.

До выделения в отдельный репозиторий такие workflow-элементы часто появляются
внутри конкретного рабочего проекта. Это удобно на старте, но плохо
масштабируется:

- новые проекты вынуждены зависеть от структуры первого проекта;
- skills и команды расходятся копиями;
- документация дублируется и drift-ит;
- bootstrap нового проекта остается ручным;
- сложно объяснить технологию людям и агентам как самостоятельный продукт.

Целевое решение: вынести OPSX в отдельный workspace `/opt/opsx` и сделать его
единственным source of truth для технологии разработки.

## 2. Решение

Создать отдельный публичный репозиторий:

```text
/opt/opsx
```

`/opt/opsx` становится владельцем:

- методологии OPSX/OpenSpec;
- agent skills для Codex CLI;
- slash-команд и skills для Claude Code;
- bootstrap-инструментов для создания нового проекта;
- verification/drift-инструментов для проверки подключенных проектов;
- документации по pipeline, board-конвенциям, review-gate и publish-flow;
- шаблонов проектных файлов, которые генерируются или копируются при
  подключении нового проекта.

Все проекты-потребители подключаются к `/opt/opsx`, но остаются
самостоятельными git-репозиториями.

## 3. Цели

- Убрать зависимость новых проектов от структуры любого конкретного проекта.
- Иметь один универсальный source of truth OPSX для всех проектов на машине или
  в workspace.
- Обновлять skills, команды и методологию один раз, в OPSX.
- Подключать новый проект через bootstrap, а не через ручное копирование
  большого набора файлов.
- Минимизировать drift между проектами.
- Сделать OPSX самостоятельным открытым продуктом, который можно развивать,
  версионировать и распространять отдельно.

## 4. Нецели

- Не переносить в OPSX бизнес-код, customer-specific tooling или
  domain-specific реализацию из проектов-потребителей.
- Не делать весь проект symlink-копией шаблона.
- Не хранить machine-local auth, sessions, traces, runtime state или секреты в
  OPSX.
- Не превращать OPSX в монорепозиторий всех проектов.
- Не ломать существующие проекты одномоментной миграцией: переход должен быть
  поэтапным и проверяемым.

## 5. Целевая модель

```text
                    source of truth
                  +----------------+
                  |   /opt/opsx    |
                  +--------+-------+
                           |
          symlinks + generated project files
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
/opt/example-a       /opt/example-b       /opt/example-project
 consumer repo        consumer repo        consumer repo
```

`/opt/opsx` не копируется целиком в новый проект. Новый проект создается
bootstrap-процессом:

1. Создается пустой проектный репозиторий.
2. В проект кладутся только проектно-специфичные файлы.
3. Общие OPSX skills и команды подключаются symlink-ами на `/opt/opsx`.
4. Конфиги `.mcp.json` и `.codex/config.toml` генерируются под конкретный путь
   проекта.
5. `verify-project` проверяет, что проект действительно подключен к актуальному
   source of truth.

## 6. Планируемая структура OPSX

Начальная структура может быть минимальной:

```text
/opt/opsx/
└── docs/
    └── opsx-source-of-truth-architecture.md
```

Целевая структура:

```text
/opt/opsx/
├── README.md
├── LICENSE
├── AGENTS.shared.md
├── docs/
│   ├── new-project-runbook.md
│   ├── opsx-pipeline.md
│   ├── opsx-source-of-truth-architecture.md
│   ├── project-adoption.md
│   └── migration-guide.md
├── skills/
│   ├── opsx-deliver/
│   ├── opsx-ff/
│   ├── opsx-do/
│   ├── opsx-review/
│   ├── opsx-pub/
│   ├── opsx-explore/
│   ├── openspec-apply-change/
│   ├── openspec-verify-change/
│   └── ...
├── claude/
│   └── commands/
│       └── opsx/
│           ├── deliver.md
│           ├── ff.md
│           ├── do.md
│           ├── review.md
│           ├── pub.md
│           └── explore.md
├── schemas/
│   ├── opsx-review-verdict.schema.json
│   ├── opsx-delivery-manifest.schema.json
│   └── opsx-evidence-index.schema.json
├── bin/
│   ├── bootstrap-project
│   ├── verify-project
│   ├── openspec
│   └── opsx-review-verdict
├── templates/
│   └── project/
│       ├── AGENTS.md.tpl
│       ├── CLAUDE.md.tpl
│       ├── gitignore.tpl
│       ├── mcp.json.tpl
│       ├── codex-config.toml.tpl
│       └── openspec/
└── scripts/
    ├── smoke-drift.py
    └── install-git-hooks
```

## 7. Что является общим, а что проектным

Общее, source of truth в OPSX:

- `opsx-*` skills;
- `openspec-*` lifecycle skills, если они используются как часть OPSX;
- Claude slash-команды `/opsx:*`;
- общая методология OPSX;
- board-конвенции;
- review-gate контракт;
- wire-контракты технологии со schemas и reference-доками:
  review verdict, delivery manifest, evidence index — вместе с
  validate/fingerprint helper-ами, которые их проверяют;
- bootstrap и verify tooling;
- drift-проверки;
- документация pipeline.

Проектное, остается в каждом проекте:

- `AGENTS.md` с ролью проекта, boundaries и safety policy;
- `CLAUDE.md`, если нужен проектный Claude-layer;
- `openspec/config.yaml`;
- `openspec/board/**`;
- `openspec/changes/**`;
- `.mcp.json` с project-local filesystem scope;
- `.codex/config.toml` с trust-секцией и project-local MCP scope;
- `.gitignore`;
- исходный код, тесты, runtime-политики и domain-specific docs.

### Контрактный namespace

Публичные wire-контракты OPSX живут в собственном namespace `opsx.*`
(`opsx.review-verdict.v1`, `opsx.delivery-manifest.v1`,
`opsx.evidence-index.v1`). Контрактные id из legacy-источника **не
переименовываются** — это замороженные wire-строки уже развернутых
потребителей; вместо этого на переходный период validate-helpers принимают
оба семейства id, новые проекты получают только `opsx.*`, а legacy-семейство
объявляется deprecated в migration notes. Namespace фиксируется в Фазе 1,
до появления второго потребителя: чем раньше, тем дешевле переход.

### Path-neutrality skills

Тексты skills в OPSX не содержат machine-specific абсолютных fallback-путей
и упоминаний конкретных workspace-specific источников: helper-инструменты резолвятся
относительно корня OPSX (родителя каталога `skills/`), проектные пути
приходят из контекста запуска. Абсолютный `/opt/opsx` допустим только как
документированный contract path. Это условие генерализации при переносе
каждого skill в Фазе 1, и его проверяет CI публичного репозитория.

## 8. Symlink-модель потребителя

Каждый проект подключает общие части так:

```text
.claude/commands/opsx       -> /opt/opsx/claude/commands/opsx
.claude/skills              -> /opt/opsx/skills
.codex/skills/opsx-*        -> /opt/opsx/skills/opsx-*
.codex/skills/openspec-*    -> /opt/opsx/skills/openspec-*
bin/openspec                -> /opt/opsx/bin/openspec
```

При необходимости можно добавить:

```text
bin/opsx-review-verdict     -> /opt/opsx/bin/opsx-review-verdict
```

Проектные `AGENTS.md`, `.mcp.json` и `.codex/config.toml` не должны быть
symlink-ами целиком, потому что они содержат путь проекта и локальные правила.
Они должны генерироваться из templates или поддерживаться проектом вручную с
проверкой через `verify-project`.

### Слоеная модель для доменных надстроек

У workspace с доменным слоем (набор domain-specific skills поверх generic
OPSX) есть два варианта подключения:

1. **Прямой потребитель.** Проект линкует generic-части напрямую из
   `/opt/opsx`, а domain-skills — отдельными symlink-ами из доменного
   репозитория. `.claude/skills` в этом случае обязан быть реальным
   каталогом с per-skill symlink-ами: единый dir-symlink не может смотреть
   в два источника.
2. **Агрегатор.** Доменный репозиторий сам становится потребителем OPSX: в
   его каталоге skills generic `opsx-*`/`openspec-*` превращаются в
   symlink-и на `/opt/opsx`, а domain-skills остаются реальными каталогами.
   Существующие потребители доменного слоя продолжают смотреть на агрегатор
   и получают OPSX транзитивно — миграция большого workspace сводится к
   одному изменению в агрегаторе вместо правки каждого его потребителя.
   Цепочки symlink-ов (потребитель -> агрегатор -> OPSX) должны быть
   покрыты discovery-smoke обоих агентов до переключения.

Для миграции существующего workspace с уже развернутой сетью потребителей
агрегатор — предпочтительный первый шаг; прямое подключение — целевая форма
для новых standalone-проектов.

## 9. Методология и AGENTS.md

Проблема: агентские инструкции должны быть в контексте каждого проекта, но
полный `AGENTS.md` всегда содержит проектную специфику.

Целевая модель:

- `/opt/opsx/AGENTS.shared.md` содержит общий OPSX-блок:
  pipeline `ff -> do -> review -> pub`, review-gate, правила карточек,
  OpenSpec lifecycle, commit/push policy, evidence policy.
- проектный `AGENTS.md` содержит локальные правила проекта и явный блок
  "OPSX Methodology", ссылающийся на `/opt/opsx/AGENTS.shared.md`.
- `bootstrap-project` может вставлять shared-блок в `AGENTS.md` как
  generated section с version/hash-маркером.
- `verify-project` проверяет drift generated section против
  `/opt/opsx/AGENTS.shared.md`.

Практическое правило:

- для максимальной надежности агентского контекста использовать generated
  вставку shared-блока;
- для минимального дублирования использовать ссылку на shared-файл;
- окончательный вариант выбрать после smoke-проверки Codex и Claude на чтение
  внешнего shared-файла.

## 10. Bootstrap нового проекта

Целевая команда:

```bash
/opt/opsx/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

Bootstrap должен:

1. Проверить, что target-путь безопасен и не содержит рабочий проект.
2. Создать базовые каталоги:
   - `.claude/commands`;
   - `.codex/skills`;
   - `bin`;
   - `openspec/changes`;
   - `openspec/specs`;
   - `openspec/board/{1.backlog,2.todo,3.inprogress,4.done,5.canceled}`.
3. Создать symlink-и на OPSX.
4. Сгенерировать `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
   `.codex/config.toml`, `openspec/config.yaml`, `openspec/board/README.md`.
5. Для domain-specific templates добавить расширенные verification rules.
6. Запустить `verify-project`.
7. Напечатать следующие шаги: `git init`, первый commit, подключение remote.

Шаблоны project-local файлов находятся в `templates/project/`. Bootstrap
рендерит `*.tpl` файлы с placeholders для project path, project name,
project kind и OPSX root, копирует OpenSpec skeleton и создает symlink-и на
OPSX-owned surfaces.

Текущая реализация `bin/bootstrap-project` поддерживает `--dry-run`,
`--backup-existing`, `--skip-verify` для диагностики и по умолчанию запускает
`bin/verify-project` после генерации.

## 11. Verification и drift

`/opt/opsx/bin/verify-project <path>` должен проверять:

- symlink-и `.claude/commands/opsx`, `.claude/skills`, `.codex/skills/*`;
- что symlink-и резолвятся в OPSX source of truth (напрямую или транзитивно
  через задокументированный агрегатор);
- наличие и валидность `openspec/config.yaml`;
- успешный `bin/openspec validate --all`;
- что filesystem scope в `.mcp.json` покрывает корень проекта;
- что filesystem scope и trust-section в `.codex/config.toml` покрывают корень
  проекта;
- что helper-ы контрактов (review verdict validate/fingerprint) и schemas
  достижимы из проекта;
- версию OpenSpec CLI, зафиксированную в `bin/openspec`, против compatibility
  notes;
- что `.runtime/`, `.artifacts/`, `.ai/`, Codex runtime и Claude local settings
  игнорируются git;
- отсутствие committed runtime/auth/session файлов;
- drift generated sections в `AGENTS.md` и board docs, если выбран режим
  generated вставок.

Каждая проверка — красно-зеленая (exit-код), не «напечатать и посмотреть»:
verify-project — это gate, а не отчет.

Текущая реализация `bin/verify-project` выполняет gate локально: печатает
`PASS`/`FAIL` для каждой проверки, поддерживает `--opsx-root` и
`--aggregator-root`, запускает project-local `bin/openspec validate --all
--strict` и возвращает non-zero exit при любом failed check.

Текущая реализация `/opt/opsx/scripts/smoke-drift.py` проходит по configured
workspace roots или explicit projects из operator-provided config/CLI input,
пишет JSON report `opsx.drift-gate.v1` в ignored runtime space и показывает:

- какие проекты подключены к OPSX;
- какие проекты используют legacy source of truth;
- где symlink-и сломаны;
- какие проекты не участвуют в OPSX и явно исключены.

## 12. Дорожная карта реализации OPSX

Статус актуализирован: 2026-07-08.

Текущая точка: Фазы 1-3 собраны в рабочем дереве. Архитектурное решение,
dogfooding через OpenSpec, shared methodology, generic lifecycle skills,
OpenSpec lifecycle skills, contract schemas, review-verdict helper,
discovery-smoke, bootstrap, verify-project и drift-gate уже есть. Массовая
миграция потребителей еще не завершена.

Операционная оценка готовности к целевому состоянию "выбранные проекты
workspace используют единый pipeline через `/opt/opsx`": около 35%. Эта оценка
не является release-метрикой; точную картину по конкретной машине должен
показывать operator-provided drift report, а публичная документация фиксирует
только generic-классы потребителей.

### Фаза 0. Зафиксировать решение - done

- [x] Создать `/opt/opsx/docs`.
- [x] Добавить архитектурный документ.
- [x] Создать публичный GitHub-репозиторий.
- [x] Добавить `.gitignore`, `README.md` и `LICENSE`.

Результат: есть место и зафиксированное архитектурное решение.

### Фаза 1. Собрать минимальный source of truth - done

Готово:

- [x] Добавить `AGENTS.shared.md`.
- [x] Добавить минимальные generic skills `opsx-explore` и `opsx-ff`.
- [x] Добавить Claude wrappers `/opsx:explore` и `/opsx:ff`.
- [x] Добавить repo-local wiring для dogfooding Codex и Claude.
- [x] Добавить discovery-smoke для repo-local и consumer-example wiring.
- [x] Добавить generic lifecycle skills `opsx-do`, `opsx-review`,
  `opsx-pub` и `opsx-deliver`.
- [x] Добавить `openspec-*` lifecycle skills.
- [x] Добавить wrapper `bin/openspec`.
- [x] Добавить helper review-verdict.
- [x] Добавить `schemas/` с контрактами review-verdict, delivery-manifest,
  evidence-index в namespace `opsx.*`.
- [x] Генерализовать каждый переносимый skill: убрать machine-specific
  fallback-пути и упоминания workspace-specific источников (см. Path-neutrality),
  перевести контрактные id на `opsx.*`, зафиксировать язык публичной
  документации.
- [x] Проверить лицензию и происхождение переносимых upstream `openspec-*`
  skills; зафиксировать политику синка с развитием OpenSpec CLI.

Результат фазы: OPSX может быть источником symlink-ов для новых проектов и
миграции существующих consumers.

### Фаза 2. Bootstrap и templates - done

- [x] Создать `templates/project`.
- [x] Описать placeholders для project path, project name, project kind.
- [x] Реализовать `bin/bootstrap-project`.
- [x] Реализовать `bin/verify-project`.
- [x] Добавить smoke-проект в `.runtime` для проверки bootstrap.

Результат: новый проект можно создать одной командой.

### Фаза 3. Drift gate - done

Готово:

- [x] Добавить discovery-smoke для минимальной поверхности
  `opsx-explore`/`opsx-ff`.
- [x] Реализовать `scripts/smoke-drift.py`.
- [x] Добавить список include/exclude проектов через operator-provided config
  или CLI flags; machine-local inventory остается в ignored `internal/`.
- [x] Проверить configured workspace roots shallow scan.
- [x] Добавить machine-readable output для CI с schema
  `opsx.drift-gate.v1`.
- [x] Показывать consumer-классы: OPSX source, legacy source, broken wiring,
  disconnected и explicitly excluded.

Результат: можно видеть, какие проекты соответствуют OPSX source of truth.

### Фаза 4. Миграция существующих потребителей - not started

- [ ] Найти проекты, где workflow уже частично настроен локально.
- [ ] Переключить их skills/commands на OPSX. Для workspace с развернутой
  сетью потребителей предпочтительно использовать агрегатор (см. раздел 8):
  одно изменение в доменном источнике вместо правки каждого потребителя.
- [ ] Перевести drift-gate legacy-источника: его канонические проверки должны
  либо указывать на OPSX, либо проверять агрегатор-симлинки на OPSX.
- [ ] Решить владение OpenSpec-спеками и тестами generic skills: перенести в
  OPSX или зафиксировать переходное двойное владение с явным сроком.
- [ ] Обновить локальные docs, чтобы они ссылались на OPSX как внешний workflow
  layer; пометить legacy bootstrap-runbook как superseded ссылкой на
  `bootstrap-project`.
- [ ] Убрать старые локальные копии, если они больше не нужны.

Результат: существующие проекты становятся consumers OPSX.

### Фаза 5. Подключение новых проектов - not started

- [ ] Проинвентаризировать workspace roots.
- [ ] Выбрать проекты для подключения к OPSX.
- [ ] Для каждого проекта запустить adoption flow.
- [ ] Для проектов, которые не должны использовать OPSX, добавить явный exclude.

Результат: все нужные проекты используют один OPSX toolchain.

### Фаза 6. Версионирование и релизная дисциплина - implemented

- [x] Ввести semver.
- [x] Описать changelog.
- [x] Добавить compatibility notes для Codex CLI, Claude Code и OpenSpec CLI.
- [x] Добавить migration notes между версиями.
- [x] Настроить CI для templates, bootstrap, verify и drift.

Результат: OPSX становится самостоятельной поддерживаемой технологией.

### Индекс шагов реализации и карточки доски

Оставшиеся работы разложены в упорядоченную последовательность story-level
шагов. Каждый шаг соответствует одноименной карточке в `openspec/board/` и
проходит обычные board gates (`1.backlog -> 2.todo -> 3.inprogress -> 4.done`).
Порядок отражает зависимости: контракты и helper-ы нужны `verify-project`,
`verify-project` нужен `bootstrap-project`, drift gate переиспользует
verify-проверки, миграция и adoption идут после зеленого drift gate.

| # | Шаг / карточка | Фаза | Scope (кратко) | Depends on |
| --- | --- | --- | --- | --- |
| 1 | `01-finish-minimal-source-of-truth` | 1 | lifecycle skills `do/review/pub/deliver`, `openspec-*` skills, `bin/openspec`, schemas `opsx.*`, review-verdict helper, генерализация | — |
| 2 | `02-bootstrap-and-templates` | 2 | `templates/project`, `bin/bootstrap-project`, `bin/verify-project`, smoke-проект | 1 |
| 3 | `03-drift-gate` | 3 | `scripts/smoke-drift.py`, include/exclude, machine-readable output, consumer-классы | 2 |
| 4 | `04-migrate-existing-consumers` | 4 | переключить первый aggregator/legacy consumers на OPSX, перевести legacy drift-gate | 2, 3 |
| 5 | `05-adopt-new-projects` | 5 | adoption flow для новых проектов, explicit exclude | 2, 4 |
| 6 | `06-release-discipline` | 6 | semver, changelog, compatibility/migration notes, CI | 2, 3 |

Триаж каждой карточки и декомпозиция в apply-ready OpenSpec changes выполняются
через `opsx-ff`. Machine-local inventory для шагов 4–5 (реальные пути, список
проектов, порядок миграции) остается в `internal/`, а не в карточках.

## 13. Дорожная карта миграции существующих проектов

### 13.1. Инвентаризация

Для каждого проекта определить:

- является ли он git-репозиторием;
- есть ли `AGENTS.md`;
- есть ли OpenSpec;
- есть ли `.claude` или `.codex`;
- используется ли текущий OPSX-like workflow;
- есть ли project-specific MCP;
- можно ли безопасно менять agent wiring.

### 13.2. Классы миграции

| Класс | Описание | Действие |
| --- | --- | --- |
| A | Проект уже использует OPSX-like workflow | заменить локальные links/copies на OPSX source of truth |
| B | Проект без OPSX | подключить через adoption flow |
| C | Проект с собственной агентской обвязкой | вручную совместить project rules и OPSX templates |
| D | Проект, который не должен использовать OPSX | добавить в exclude drift-gate |

### 13.3. Миграция одного проекта

1. Проверить git status.
2. Прочитать локальный `AGENTS.md` или аналогичные инструкции.
3. Сохранить текущие `.claude`, `.codex`, `openspec` настройки как diff.
4. Запустить adoption-команду или выполнить ручной adoption checklist.
5. Переключить symlink-и на OPSX.
6. Обновить `AGENTS.md` и `CLAUDE.md`.
7. Проверить `.mcp.json` и `.codex/config.toml`.
8. Запустить `verify-project`.
9. Запустить smoke OPSX на небольшой docs-card.
10. Закоммитить migration diff в проектном репозитории.

## 14. Риски и решения

| Риск | Решение |
| --- | --- |
| Старые проекты продолжают ссылаться на legacy source | drift-gate должен явно показывать legacy consumers |
| В проектных `AGENTS.md` появится drift методологии | generated section с hash или обязательная ссылка на `/opt/opsx/AGENTS.shared.md` |
| Claude или Codex изменят поведение symlink discovery | discovery smoke после обновления CLI, fallback на generated copies |
| Абсолютные symlink-и ломаются при переносе сервера | `/opt/opsx` является рекомендуемым contract path; для переносимости добавить bootstrap с `--opsx-root` |
| OPSX станет слишком domain-specific | держать generic core отдельно от domain extensions |
| Bootstrap перезапишет живые проектные файлы | dry-run, backup, refuse-on-existing по умолчанию |
| В git попадет runtime/auth state | `.gitignore` templates и `verify-project` проверяют runtime paths |
| `git pull` в `/opt/opsx` мгновенно меняет поведение всех подключенных проектов (symlink = always-latest, pin невозможен) | update-ритуал: pull -> drift/discovery smoke до возврата к работе; возможность держать checkout на теге; changelog с breaking-маркерами |
| Копии upstream `openspec-*` skills разойдутся с развитием OpenSpec CLI или нарушат его лицензию | зафиксировать источник и лицензию, политику синка, pin версии CLI в `bin/openspec` + compatibility notes |
| `internal/` не под git: потеря машины теряет migration-контекст | приватный бэкап `internal/` или дублирование инвентаря в приватном репозитории |

## 15. Открытые решения

- Делать ли `AGENTS.shared.md` внешней ссылкой или generated вставкой.
  Рекомендация: **generated вставка с hash-маркером** как default. Codex не
  следует import-ам и читает только файлы репозитория; Claude умеет
  `@`-import абсолютного пути, но один механизм, работающий для обоих
  агентов одинаково, надежнее двух разных. Внешняя ссылка остается для
  людей; drift generated-вставки ловит `verify-project`.
- Нужен ли отдельный каталог `extensions/` для domain-specific skills.
  Рекомендация: **да** — либо `extensions/`, либо доменный
  репозиторий-агрегатор (раздел 8); generic core остается чистым в обоих
  вариантах.
- Использовать ли абсолютные symlink-и на `/opt/opsx` или генерировать
  относительные там, где это возможно. Рекомендация: абсолютный
  `/opt/opsx` как contract path (+ `--opsx-root` в bootstrap); относительные
  линки — только внутри одного дерева workspace.
- Должен ли OPSX сам быть OPSX-проектом с собственной доской и OpenSpec.
  Рекомендация: **да, dogfooding** — развитие OPSX через собственный
  `ff -> do -> review -> pub` и есть главный тест продукта; гигиена
  публичности карточек обеспечивается правилами репозитория и `internal/`
  для локального контекста.
- Какой уровень обратной совместимости нужен для первых публичных релизов.

## 16. Рекомендуемая ближайшая последовательность

1. Инициализировать git в `/opt/opsx`.
2. Подключить публичный remote.
3. Закоммитить `.gitignore`, `README.md`, `LICENSE` и этот документ.
4. Создать `AGENTS.shared.md`.
5. Перенести минимальный набор skills и Claude commands в generic-форме.
6. Реализовать `bootstrap-project` и `verify-project`.
7. Создать тестовый проект через bootstrap.
8. После smoke-проверки начинать миграцию существующих consumers.
