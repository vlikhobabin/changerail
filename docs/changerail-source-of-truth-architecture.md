# ChangeRail как единый source of truth разработки

Статус: проектное решение, целевая архитектура.

Дата: 2026-07-08.

## 1. Контекст

ChangeRail выделяется в самостоятельную открытую технологию для организации
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

Целевое решение: вынести ChangeRail в отдельный workspace `/opt/changerail` и сделать его
единственным source of truth для технологии разработки.

## 2. Решение

Создать отдельный публичный репозиторий:

```text
/opt/changerail
```

`/opt/changerail` становится владельцем:

- методологии ChangeRail/OpenSpec;
- agent skills для Codex CLI;
- slash-команд и skills для Claude Code;
- bootstrap-инструментов для создания нового проекта;
- verification/drift-инструментов для проверки подключенных проектов;
- документации по pipeline, board-конвенциям, review-gate и publish-flow;
- шаблонов проектных файлов, которые генерируются или копируются при
  подключении нового проекта.

Все проекты-потребители подключаются к `/opt/changerail`, но остаются
самостоятельными git-репозиториями.

## 3. Цели

- Убрать зависимость новых проектов от структуры любого конкретного проекта.
- Иметь один универсальный source of truth ChangeRail для всех проектов на машине или
  в workspace.
- Обновлять skills, команды и методологию один раз, в ChangeRail.
- Подключать новый проект через bootstrap, а не через ручное копирование
  большого набора файлов.
- Минимизировать drift между проектами.
- Сделать ChangeRail самостоятельным открытым продуктом, который можно развивать,
  версионировать и распространять отдельно.

## 4. Нецели

- Не переносить в ChangeRail бизнес-код, customer-specific tooling или
  domain-specific реализацию из проектов-потребителей.
- Не делать весь проект symlink-копией шаблона.
- Не хранить machine-local auth, sessions, traces, runtime state или секреты в
  ChangeRail.
- Не превращать ChangeRail в монорепозиторий всех проектов.
- Не ломать существующие проекты одномоментной миграцией: переход должен быть
  поэтапным и проверяемым.

## 5. Целевая модель

```text
                    source of truth
                  +----------------+
                  |   /opt/changerail    |
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

`/opt/changerail` не копируется целиком в новый проект. Новый проект создается
bootstrap-процессом:

1. Создается пустой проектный репозиторий.
2. В проект кладутся только проектно-специфичные файлы.
3. Общие ChangeRail skills и команды подключаются symlink-ами на `/opt/changerail`.
4. Конфиги `.mcp.json` и `.codex/config.toml` генерируются под конкретный путь
   проекта.
5. `verify-project` проверяет, что проект действительно подключен к актуальному
   source of truth.

## 6. Планируемая структура ChangeRail

Начальная структура может быть минимальной:

```text
/opt/changerail/
└── docs/
    └── changerail-source-of-truth-architecture.md
```

Целевая структура:

```text
/opt/changerail/
├── README.md
├── LICENSE
├── AGENTS.shared.md
├── docs/
│   ├── new-project-runbook.md
│   ├── changerail-pipeline.md
│   ├── changerail-source-of-truth-architecture.md
│   ├── project-adoption.md
│   └── migration-guide.md
├── skills/
│   ├── changerail-deliver/
│   ├── changerail-ff/
│   ├── changerail-do/
│   ├── changerail-review/
│   ├── changerail-pub/
│   ├── changerail-explore/
│   ├── openspec-apply-change/
│   ├── openspec-verify-change/
│   └── ...
├── claude/
│   └── commands/
│       └── changerail/
│           ├── deliver.md
│           ├── ff.md
│           ├── do.md
│           ├── review.md
│           ├── pub.md
│           └── explore.md
├── schemas/
│   ├── changerail-review-verdict.schema.json
│   ├── changerail-delivery-manifest.schema.json
│   └── changerail-evidence-index.schema.json
├── bin/
│   ├── bootstrap-project
│   ├── verify-project
│   ├── openspec
│   └── changerail-review-verdict
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

Общее, source of truth в ChangeRail:

- `changerail-*` skills;
- `openspec-*` lifecycle skills, если они используются как часть ChangeRail;
- Claude slash-команды `/changerail:*`;
- общая методология ChangeRail;
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

Публичные wire-контракты ChangeRail живут в собственном namespace `changerail.*`
(`changerail.review-verdict.v1`, `changerail.delivery-manifest.v1`,
`changerail.evidence-index.v1`). Старые `opsx.*.v1` payloads считаются
pre-rename legacy artifacts: новые helpers и schemas не делают их canonical
post-rename контрактом. Новые проекты получают только `changerail.*`, а
migration notes описывают breaking namespace change и required consumer
rewiring.

### Path-neutrality skills

Тексты skills в ChangeRail не содержат machine-specific абсолютных fallback-путей
и упоминаний конкретных workspace-specific источников: helper-инструменты резолвятся
относительно корня ChangeRail (родителя каталога `skills/`), проектные пути
приходят из контекста запуска. Абсолютный `/opt/changerail` допустим только как
документированный contract path. Это условие генерализации при переносе
каждого skill в Фазе 1, и его проверяет CI публичного репозитория.

## 8. Symlink-модель потребителя

Каждый проект подключает общие части так:

```text
.claude/commands/changerail       -> /opt/changerail/claude/commands/changerail
.claude/skills              -> /opt/changerail/skills
.codex/skills/changerail-*        -> /opt/changerail/skills/changerail-*
.codex/skills/openspec-*    -> /opt/changerail/skills/openspec-*
bin/openspec                -> /opt/changerail/bin/openspec
```

При необходимости можно добавить:

```text
bin/changerail-review-verdict     -> /opt/changerail/bin/changerail-review-verdict
```

Проектные `AGENTS.md`, `.mcp.json` и `.codex/config.toml` не должны быть
symlink-ами целиком, потому что они содержат путь проекта и локальные правила.
Они должны генерироваться из templates или поддерживаться проектом вручную с
проверкой через `verify-project`.

### Слоеная модель для доменных надстроек

У workspace с доменным слоем (набор domain-specific skills поверх generic
ChangeRail) есть два варианта подключения:

1. **Прямой потребитель.** Проект линкует generic-части напрямую из
   `/opt/changerail`, а domain-skills — отдельными symlink-ами из доменного
   репозитория. `.claude/skills` в этом случае обязан быть реальным
   каталогом с per-skill symlink-ами: единый dir-symlink не может смотреть
   в два источника.
2. **Агрегатор.** Доменный репозиторий сам становится потребителем ChangeRail: в
   его каталоге skills generic `changerail-*`/`openspec-*` превращаются в
   symlink-и на `/opt/changerail`, а domain-skills остаются реальными каталогами.
   Существующие потребители доменного слоя продолжают смотреть на агрегатор
   и получают ChangeRail транзитивно — миграция большого workspace сводится к
   одному изменению в агрегаторе вместо правки каждого его потребителя.
   Цепочки symlink-ов (потребитель -> агрегатор -> ChangeRail) должны быть
   покрыты discovery-smoke обоих агентов до переключения.

Для миграции существующего workspace с уже развернутой сетью потребителей
агрегатор экономит правки, но у него есть важный нюанс порядка: flip
агрегатора транзитивно переключает **всех** его потребителей одновременно.
Если часть из них в активной работе, безопаснее сначала перевести отдельные
проекты как прямые потребители ChangeRail (вариант 1), а flip агрегатора отложить —
тогда к моменту flip у агрегатора остаются только доменные потребители.

Что именно делать с агрегатором при flip (проверено на практике):

- **generic `openspec-*`** (lifecycle-скиллы OpenSpec CLI) — де-дуплить:
  реальные копии заменять symlink-ами на ChangeRail. Они идентичны у всех и должны
  иметь один источник.
- **специализированные `changerail-*`** — если доменный слой встроил в них свои
  хуки (доменные `agents/`, trace-ссылки, verification-матрицы), оставлять
  их **реальными каталогами в агрегаторе**: это легитимный доменный форк,
  которым пользуются доменные потребители. Их генерализация в overlay поверх
  generic-базы из ChangeRail — отдельная целевая задача, не часть механического flip.
- **доменные скиллы** (`1c-*`, router-ы и т.п.) — всегда остаются в агрегаторе.
- **drift-gate агрегатора**: проверить, входят ли `openspec-*` в его
  source-набор. Если нет — он терпит внешние symlink-и на ChangeRail без правок;
  если да — научить его «generic резолвятся в ChangeRail» до flip.

Прямое подключение (вариант 1) — целевая форма для новых standalone-проектов.

## 9. Методология и AGENTS.md

Проблема: агентские инструкции должны быть в контексте каждого проекта, но
полный `AGENTS.md` всегда содержит проектную специфику.

Целевая модель:

- `/opt/changerail/AGENTS.shared.md` содержит общий ChangeRail-блок:
  pipeline `ff -> do -> review -> pub`, review-gate, правила карточек,
  OpenSpec lifecycle, commit/push policy, evidence policy.
- проектный `AGENTS.md` содержит локальные правила проекта и явный блок
  "ChangeRail Methodology", ссылающийся на `/opt/changerail/AGENTS.shared.md`.
- `bootstrap-project` может вставлять shared-блок в `AGENTS.md` как
  generated section с version/hash-маркером.
- `verify-project` проверяет drift generated section против
  `/opt/changerail/AGENTS.shared.md`.

Практическое правило:

- для максимальной надежности агентского контекста использовать generated
  вставку shared-блока;
- для минимального дублирования использовать ссылку на shared-файл;
- окончательный вариант выбрать после smoke-проверки Codex и Claude на чтение
  внешнего shared-файла.

## 10. Bootstrap нового проекта

Целевая команда:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
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
3. Создать symlink-и на ChangeRail.
4. Сгенерировать `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
   `.codex/config.toml`, `openspec/config.yaml`, `openspec/board/README.md`.
5. Для domain-specific templates добавить расширенные verification rules.
6. Запустить `verify-project`.
7. Напечатать следующие шаги: `git init`, первый commit, подключение remote.

Шаблоны project-local файлов находятся в `templates/project/`. Bootstrap
рендерит `*.tpl` файлы с placeholders для project path, project name,
project kind и ChangeRail root, копирует OpenSpec skeleton и создает symlink-и на
ChangeRail-owned surfaces.

Текущая реализация `bin/bootstrap-project` поддерживает `--dry-run`,
`--backup-existing`, `--skip-verify` для диагностики и по умолчанию запускает
`bin/verify-project` после генерации.

## 11. Verification и drift

`/opt/changerail/bin/verify-project <path>` должен проверять:

- symlink-и `.claude/commands/changerail`, `.claude/skills`, `.codex/skills/*`;
- что symlink-и резолвятся в ChangeRail source of truth (напрямую или транзитивно
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
`PASS`/`FAIL` для каждой проверки, поддерживает `--changerail-root` и
`--aggregator-root`, запускает project-local `bin/openspec validate --all
--strict` и возвращает non-zero exit при любом failed check.

Текущая реализация `/opt/changerail/scripts/smoke-drift.py` проходит по configured
workspace roots или explicit projects из operator-provided config/CLI input,
пишет JSON report `changerail.drift-gate.v1` в ignored runtime space и показывает:

- какие проекты подключены к ChangeRail;
- какие проекты используют legacy source of truth;
- где symlink-и сломаны;
- какие проекты не участвуют в ChangeRail и явно исключены.

## 12. Дорожная карта реализации ChangeRail

Статус актуализирован: 2026-07-08.

Текущая точка: Фазы 1-3 собраны в рабочем дереве. Архитектурное решение,
dogfooding через OpenSpec, shared methodology, generic lifecycle skills,
OpenSpec lifecycle skills, contract schemas, review-verdict helper,
discovery-smoke, bootstrap, verify-project и drift-gate уже есть. Массовая
миграция потребителей еще не завершена.

Операционная оценка готовности к целевому состоянию "выбранные проекты
workspace используют единый pipeline через `/opt/changerail`": около 35%. Эта оценка
не является release-метрикой; точную картину по конкретной машине должен
показывать operator-provided drift report, а публичная документация фиксирует
только generic-классы потребителей.

### Фаза 0. Зафиксировать решение - done

- [x] Создать `/opt/changerail/docs`.
- [x] Добавить архитектурный документ.
- [x] Создать публичный GitHub-репозиторий.
- [x] Добавить `.gitignore`, `README.md` и `LICENSE`.

Результат: есть место и зафиксированное архитектурное решение.

### Фаза 1. Собрать минимальный source of truth - done

Готово:

- [x] Добавить `AGENTS.shared.md`.
- [x] Добавить минимальные generic skills `changerail-explore` и `changerail-ff`.
- [x] Добавить Claude wrappers `/changerail:explore` и `/changerail:ff`.
- [x] Добавить repo-local wiring для dogfooding Codex и Claude.
- [x] Добавить discovery-smoke для repo-local и consumer-example wiring.
- [x] Добавить generic lifecycle skills `changerail-do`, `changerail-review`,
  `changerail-pub` и `changerail-deliver`.
- [x] Добавить `openspec-*` lifecycle skills.
- [x] Добавить wrapper `bin/openspec`.
- [x] Добавить helper review-verdict.
- [x] Добавить `schemas/` с контрактами review-verdict, delivery-manifest,
  evidence-index в namespace `changerail.*`.
- [x] Генерализовать каждый переносимый skill: убрать machine-specific
  fallback-пути и упоминания workspace-specific источников (см. Path-neutrality),
  перевести контрактные id на `changerail.*`, зафиксировать язык публичной
  документации.
- [x] Проверить лицензию и происхождение переносимых upstream `openspec-*`
  skills; зафиксировать политику синка с развитием OpenSpec CLI.

Результат фазы: ChangeRail может быть источником symlink-ов для новых проектов и
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
  `changerail-explore`/`changerail-ff`.
- [x] Реализовать `scripts/smoke-drift.py`.
- [x] Добавить список include/exclude проектов через operator-provided config
  или CLI flags; machine-local inventory остается в ignored `internal/`.
- [x] Проверить configured workspace roots shallow scan.
- [x] Добавить machine-readable output для CI с schema
  `changerail.drift-gate.v1`.
- [x] Показывать consumer-классы: ChangeRail source, legacy source, broken wiring,
  disconnected и explicitly excluded.

Результат: можно видеть, какие проекты соответствуют ChangeRail source of truth.

### Фаза 4. Миграция существующих потребителей - done

- [x] Найти проекты, где workflow уже частично настроен локально.
- [x] Переключить их skills/commands на ChangeRail. Практика уточнила порядок:
  точечный перевод по одному проекту (каждый как прямой потребитель ChangeRail)
  предпочтительнее одномоментного aggregator-flip, когда потребители в
  активной работе — flip транзитивно меняет их все сразу (см. раздел 8 и
  карточку `04`).
- [x] Перевести drift-gate legacy-источника. Для доменного агрегатора это
  свелось к де-дупу generic `openspec-*` в ChangeRail при сохранении
  специализированных `changerail-*` локально; его собственный drift-gate внешние
  symlink-и на ChangeRail терпит без изменений (generic skills вне его source-набора).
- [x] Решить владение OpenSpec-спеками и тестами generic skills.
- [x] Обновить локальные docs потребителей, чтобы они ссылались на ChangeRail как
  внешний workflow layer.
- [x] Убрать старые локальные копии, если они больше не нужны.

Результат: существующие проекты стали consumers ChangeRail; доменный агрегатор берёт
generic-часть из ChangeRail, оставляя доменный слой у себя. Практический playbook и
краевые случаи — в разделе 13.3.

### Фаза 5. Подключение новых проектов - not started

- [ ] Проинвентаризировать workspace roots.
- [ ] Выбрать проекты для подключения к ChangeRail.
- [ ] Для каждого проекта запустить adoption flow.
- [ ] Для проектов, которые не должны использовать ChangeRail, добавить явный exclude.

Результат: все нужные проекты используют один ChangeRail toolchain.

### Фаза 6. Версионирование и релизная дисциплина - implemented

- [x] Ввести semver.
- [x] Описать changelog.
- [x] Добавить compatibility notes для Codex CLI, Claude Code и OpenSpec CLI.
- [x] Добавить migration notes между версиями.
- [x] Настроить CI для templates, bootstrap, verify и drift.

Результат: ChangeRail становится самостоятельной поддерживаемой технологией.

### Индекс шагов реализации и карточки доски

Оставшиеся работы разложены в упорядоченную последовательность story-level
шагов. Каждый шаг соответствует одноименной карточке в `openspec/board/` и
проходит обычные board gates (`1.backlog -> 2.todo -> 3.inprogress -> 4.done`).
Порядок отражает зависимости: контракты и helper-ы нужны `verify-project`,
`verify-project` нужен `bootstrap-project`, drift gate переиспользует
verify-проверки, миграция и adoption идут после зеленого drift gate.

| # | Шаг / карточка | Фаза | Scope (кратко) | Depends on |
| --- | --- | --- | --- | --- |
| 1 | `01-finish-minimal-source-of-truth` | 1 | lifecycle skills `do/review/pub/deliver`, `openspec-*` skills, `bin/openspec`, schemas `changerail.*`, review-verdict helper, генерализация | — |
| 2 | `02-bootstrap-and-templates` | 2 | `templates/project`, `bin/bootstrap-project`, `bin/verify-project`, smoke-проект | 1 |
| 3 | `03-drift-gate` | 3 | `scripts/smoke-drift.py`, include/exclude, machine-readable output, consumer-классы | 2 |
| 4 | `04-migrate-existing-consumers` | 4 | переключить первый aggregator/legacy consumers на ChangeRail, перевести legacy drift-gate | 2, 3 |
| 5 | `05-adopt-new-projects` | 5 | adoption flow для новых проектов, explicit exclude | 2, 4 |
| 6 | `06-release-discipline` | 6 | semver, changelog, compatibility/migration notes, CI | 2, 3 |

Триаж каждой карточки и декомпозиция в apply-ready OpenSpec changes выполняются
через `changerail-ff`. Machine-local inventory для шагов 4–5 (реальные пути, список
проектов, порядок миграции) остается в `internal/`, а не в карточках.

## 13. Дорожная карта миграции существующих проектов

### 13.1. Инвентаризация

Для каждого проекта определить:

- является ли он git-репозиторием;
- есть ли `AGENTS.md`;
- есть ли OpenSpec;
- есть ли `.claude` или `.codex`;
- используется ли текущий ChangeRail-like workflow;
- есть ли project-specific MCP;
- можно ли безопасно менять agent wiring.

### 13.2. Классы миграции

| Класс | Описание | Действие |
| --- | --- | --- |
| A | Проект уже использует ChangeRail-like workflow | заменить локальные links/copies на ChangeRail source of truth |
| B | Проект без ChangeRail | подключить через adoption flow |
| C | Проект с собственной агентской обвязкой | вручную совместить project rules и ChangeRail templates |
| D | Проект, который не должен использовать ChangeRail | добавить в exclude drift-gate |

### 13.3. Миграция одного проекта

Точечный, обратимо-проверяемый порядок. Каждый шаг — по одному проекту, и
только после приостановки активной работы в нём.

**1. Пауза и чистое дерево.** Проверить `git status`. Если есть WIP —
закоммитить/убрать его отдельно **до** миграции: она трогает `AGENTS.md`,
`.gitignore`, `.codex/config.toml`, и смешивать её с чужой правкой не нужно.

**2. Снять текущее состояние.** Прочитать локальный `AGENTS.md`; зафиксировать,
куда сейчас резолвятся `.claude`/`.codex`-symlink-и (часто в legacy-источник
или битые). Прогнать `verify-project` для базовой картины (сколько из проверок
проходит и что именно не так).

**3. Переключить wiring на ChangeRail** (абсолютный `/opt/changerail` как contract path).
Целевое состояние — это ровно то, что проверяет `verify-project`:

```text
.claude/skills            -> /opt/changerail/skills
.claude/commands/changerail     -> /opt/changerail/claude/commands/changerail
.codex/skills/<skill>     -> /opt/changerail/skills/<skill>   для каждого skill c SKILL.md
bin/openspec              -> /opt/changerail/bin/openspec
bin/changerail-review-verdict   -> /opt/changerail/bin/changerail-review-verdict
```

Реальные копии (`openspec-*` как каталоги) заменяются symlink-ами. Лишние
symlink-и в чужой источник, не входящие в набор ChangeRail-скиллов, удаляются
(generic-only, см. ниже).

**4. Конфиги проекта** (не symlink-и; проверяются, но не заменяются целиком):

- `.codex/config.toml` — должна быть trusted-запись `[projects."<project-path>"]`
  и filesystem MCP scope, покрывающий корень проекта;
- `.mcp.json` — filesystem scope, покрывающий корень проекта;
- `.gitignore` — должен содержать буквально: `.runtime/ .artifacts/ .ai/
  .codex/tmp/ .codex/auth.json .codex/sessions/ .claude/settings.local.json`.

**5. Обновить `AGENTS.md`/`CLAUDE.md`** проекта: блок про ChangeRail должен
ссылаться на `/opt/changerail` (и на `/opt/changerail/AGENTS.shared.md`), а не на прежний
источник. `verify-project` это не проверяет, но иначе инструкции агента лгут.

**6. Проверить и закоммитить.** `verify-project` должен быть зелёным; migration
diff коммитится **в репозитории проекта**, не в `/opt/changerail`.

**Generic-only.** По умолчанию потребитель получает только generic ChangeRail-скиллы:
`.claude/skills -> /opt/changerail/skills` одним symlink-ом. Если проект реально
использует доменные скиллы, нужен вариант «двух источников» (раздел 8, вариант
1): `.claude/skills` — реальный каталог с per-skill symlink-ами (generic ->
ChangeRail, домен -> доменный репозиторий). Заметьте: `verify-project` требует, чтобы
`.claude/skills` был **одиночным** symlink-ом на `/opt/changerail/skills`, поэтому на
Claude-стороне доменные скиллы при generic-only исчезают в любом случае.

**Краевые случаи (проверено на практике):**

- **Workspace из нескольких репозиториев.** Один «проект» может оказаться
  набором независимых git-репо (корень + под-проекты). Мигрировать и коммитить
  каждый отдельно; часть под-проектов может держать `.codex` в `.gitignore` —
  тогда их wiring машинно-локальный и коммитить нечего.
- **Проект под root / systemd-деплой.** Если `.git` и tracked-файлы принадлежат
  `root` (сервис запускался под root), git выдаёт «dubious ownership». Нормализовать
  владельца (`chown` на пользователя) после проверки, что живые процессы это
  переживут; убрать repo-local git-identity override (напр. `user.email=root@local`)
  и переатрибутировать коммит на реального автора.
- **filesystem MCP scope = весь workspace.** Если проект скоупит MCP на широкий
  каталог (`/opt`), `verify-project` потребует точный корень проекта. Сузить до
  корня, либо, если проекту нужен кросс-проектный доступ, добавить корень рядом
  с широким scope.
- **Смена версии lifecycle-скиллов.** `openspec-*` — upstream-скиллы OpenSpec
  CLI. Обновление выполняется `openspec update` (сохраняет весь набор и
  перегенерирует его под новую версию); `openspec init` генерирует только
  текущий default-набор. Версия CLI пиннится в `bin/openspec` (см.
  `docs/openspec-lifecycle.md`).

## 14. Риски и решения

| Риск | Решение |
| --- | --- |
| Старые проекты продолжают ссылаться на legacy source | drift-gate должен явно показывать legacy consumers |
| В проектных `AGENTS.md` появится drift методологии | generated section с hash или обязательная ссылка на `/opt/changerail/AGENTS.shared.md` |
| Claude или Codex изменят поведение symlink discovery | discovery smoke после обновления CLI, fallback на generated copies |
| Абсолютные symlink-и ломаются при переносе сервера | `/opt/changerail` является рекомендуемым contract path; для переносимости добавить bootstrap с `--changerail-root` |
| ChangeRail станет слишком domain-specific | держать generic core отдельно от domain extensions |
| Bootstrap перезапишет живые проектные файлы | dry-run, backup, refuse-on-existing по умолчанию |
| В git попадет runtime/auth state | `.gitignore` templates и `verify-project` проверяют runtime paths |
| `git pull` в `/opt/changerail` мгновенно меняет поведение всех подключенных проектов (symlink = always-latest, pin невозможен) | update-ритуал: pull -> drift/discovery smoke до возврата к работе; возможность держать checkout на теге; changelog с breaking-маркерами |
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
- Использовать ли абсолютные symlink-и на `/opt/changerail` или генерировать
  относительные там, где это возможно. Рекомендация: абсолютный
  `/opt/changerail` как contract path (+ `--changerail-root` в bootstrap); относительные
  линки — только внутри одного дерева workspace.
- Должен ли ChangeRail сам быть ChangeRail-проектом с собственной доской и OpenSpec.
  Рекомендация: **да, dogfooding** — развитие ChangeRail через собственный
  `ff -> do -> review -> pub` и есть главный тест продукта; гигиена
  публичности карточек обеспечивается правилами репозитория и `internal/`
  для локального контекста.
- Какой уровень обратной совместимости нужен для первых публичных релизов.

## 16. Рекомендуемая ближайшая последовательность

1. Инициализировать git в `/opt/changerail`.
2. Подключить публичный remote.
3. Закоммитить `.gitignore`, `README.md`, `LICENSE` и этот документ.
4. Создать `AGENTS.shared.md`.
5. Перенести минимальный набор skills и Claude commands в generic-форме.
6. Реализовать `bootstrap-project` и `verify-project`.
7. Создать тестовый проект через bootstrap.
8. После smoke-проверки начинать миграцию существующих consumers.
